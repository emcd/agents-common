# vim: set filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-

#============================================================================#
#                                                                            #
#  Licensed under the Apache License, Version 2.0 (the "License");           #
#  you may not use this file except in compliance with the License.          #
#  You may obtain a copy of the License at                                   #
#                                                                            #
#      http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                            #
#  Unless required by applicable law or agreed to in writing, software       #
#  distributed under the License is distributed on an "AS IS" BASIS,         #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#  See the License for the specific language governing permissions and       #
#  limitations under the License.                                            #
#                                                                            #
#============================================================================#


''' Content generation for coder-specific templates and items.

    This module implements the ContentGenerator class which handles
    template-based content generation from structured data sources,
    including content fallback logic for compatible coders.
'''


import jinja2 as _jinja2

from . import __
from . import base as _base
from . import context as _context


_TEMPLATE_PARTS_MINIMUM = 3

_scribe = __.provide_scribe( __name__ )


class RenderedItem( __.immut.DataclassObject ):
    ''' Single rendered item with location and content. '''

    content: str
    location: __.Path


class ContentGenerator( __.immut.DataclassObject ):
    ''' Generates coder-specific content from data sources.

        Provides template-based content generation with intelligent
        fallback logic for compatible coders (Claude ↔ OpenCode).
        Supports configurable targeting modes (per-user or per-project).
    '''

    location: __.Path
    configuration: _base.CoderConfiguration
    application_configuration: __.cabc.Mapping[ str, __.typx.Any ] = (
        __.dcls.field(
            default_factory = __.immut.Dictionary[ str, __.typx.Any ] ) )
    target_mode: __.TargetingMode = 'per-project'
    jinja_environment: _jinja2.Environment = __.dcls.field( init = False )

    def __post_init__( self ) -> None:
        self.jinja_environment = (  # pyright: ignore[reportAttributeAccessIssue]
            self._produce_jinja_environment( ) )

    def render_single_item(
        self, item_type: str, item_name: str, coder: str, target: __.Path
    ) -> RenderedItem:
        ''' Renders a single item (command or agent) for a coder.

            Combines TOML metadata, content body, and template to produce
            final coder-specific file. Returns RenderedItem with content
            and location.
        '''
        body = self._retrieve_content_with_fallback(
            item_type, item_name, coder )
        metadata = self._load_item_metadata( item_type, item_name, coder )
        template_name = self._select_template_for_coder( item_type, coder )
        template = self.jinja_environment.get_template( template_name )
        normalized = _context.normalize_render_context(
            metadata[ 'context' ], metadata[ 'coder' ] )
        variables: dict[ str, __.typx.Any ] = {
            'content': body,
            **normalized,
        }
        content = template.render( **variables )
        extension = self._parse_template_extension( template_name )
        try: renderer = __.RENDERERS[ coder ]
        except KeyError as exception:
            raise __.CoderAbsence( coder ) from exception
        base_directory = renderer.resolve_base_directory(
            mode = self.target_mode,
            target = target,
            configuration = self.application_configuration,
            environment = __.os.environ,
        )
        dirname = renderer.produce_output_structure( item_type )
        location = base_directory / dirname / f"{item_name}.{extension}"
        return RenderedItem( content = content, location = location )

    def _survey_available_templates( self, item_type: str ) -> list[ str ]:
        ''' Lists available templates for item type.

            Surveys template directory for files matching item type pattern.
        '''
        directory = self.location / "templates"
        singular_type = item_type.rstrip( 's' )
        pattern = f"{singular_type}.*.jinja"
        return [ p.name for p in directory.glob( pattern ) ]

    def _retrieve_content_with_fallback(
        self, item_type: str, item_name: str, coder: str
    ) -> str:
        ''' Retrieves content with Claude↔OpenCode fallback logic.

            Attempts to read content from coder-specific location first,
            then falls back to compatible coder if content is missing.
            Claude and OpenCode share compatible syntax and can use each
            other's content files.
        '''
        primary_path = (
            self.location / "contents" / item_type / coder /
            f"{item_name}.md" )
        if primary_path.exists( ):
            return primary_path.read_text( encoding = 'utf-8' )
        fallback_map = { "claude": "opencode", "opencode": "claude" }
        fallback_coder = fallback_map.get( coder )
        if fallback_coder:
            fallback_path = (
                self.location / "contents" / item_type /
                fallback_coder / f"{item_name}.md" )
            if fallback_path.exists( ):
                _scribe.debug( f"Using {fallback_coder} content for {coder}" )
                return fallback_path.read_text( encoding = 'utf-8' )
        raise __.ContentAbsence( item_type, item_name, coder )

    def _parse_template_extension( self, template_name: str ) -> str:
        ''' Extracts output extension from template filename.

            Template names follow pattern: item.extension.jinja
            This extracts the middle component as output extension.
        '''
        parts = template_name.split( '.' )
        if len( parts ) >= _TEMPLATE_PARTS_MINIMUM and parts[ -1 ] == 'jinja':
            return parts[ -2 ]
        raise __.TemplateExtensionError( template_name )

    def _load_item_metadata(
        self, item_type: str, item_name: str, coder: str
    ) -> dict[ str, __.typx.Any ]:
        ''' Loads TOML metadata and extracts context and coder config.

            Reads item configuration file and separates context fields
            from coder-specific configuration.
        '''
        configuration_file = (
            self.location / 'configurations' / item_type
            / f"{item_name}.toml" )
        if not configuration_file.exists( ):
            raise __.ConfigurationAbsence( configuration_file )
        try: toml_content = configuration_file.read_bytes( )
        except ( OSError, IOError ) as exception:
            raise __.ConfigurationAbsence( ) from exception
        try: toml_data: dict[ str, __.typx.Any ] = __.tomli.loads(
            toml_content.decode( 'utf-8' ) )
        except __.tomli.TOMLDecodeError as exception:
            reason = __.ConfigurationInvalidity.TOML_DECODE_ERROR
            raise __.ConfigurationInvalidity( reason ) from exception
        context = toml_data.get( 'context', { } )
        coders_list: list[ dict[ str, __.typx.Any ] ] = (
            toml_data.get( 'coders', [ ] ) )
        # Normalize coders table array to dict keyed by name
        # TOML [[coders]] tables are optional; minimal config if absent
        coders_dict: dict[ str, dict[ str, __.typx.Any ] ] = { }
        for entry in coders_list:
            if not isinstance( entry, __.cabc.Mapping ): continue
            name_value = entry.get( 'name' )
            if not isinstance( name_value, str ): continue
            coders_dict[ name_value ] = entry
        # Look up coder config from YAML, fallback to minimal config
        coder_config = coders_dict.get( coder, { 'name': coder } )
        return { 'context': context, 'coder': coder_config }

    def _produce_jinja_environment( self ) -> _jinja2.Environment:
        ''' Produces Jinja2 environment configured for templates directory.

            Creates new Jinja2 environment instance with FileSystemLoader
            pointing to data source templates directory.
        '''
        directory = self.location / "templates"
        loader = _jinja2.FileSystemLoader( directory )
        return _jinja2.Environment(
            loader = loader,
            autoescape = False,  # noqa: S701  Markdown output, not HTML
        )


    def _select_template_for_coder( self, item_type: str, coder: str ) -> str:
        ''' Selects appropriate template based on coder capabilities.

            Maps coder to preferred template format. Claude and OpenCode
            use markdown templates, while Gemini uses TOML templates.
        '''
        available = self._survey_available_templates( item_type )
        singular_type = item_type.rstrip( 's' )
        preferences = {
            "claude": [ f"{singular_type}.md.jinja" ],
            "opencode": [ f"{singular_type}.md.jinja" ],
            "gemini": [ f"{singular_type}.toml.jinja" ],
        }
        for preferred in preferences.get( coder, [ ] ):
            if preferred in available:
                return preferred
        if coder not in preferences:
            raise __.CoderAbsence( coder )
        raise __.TemplateAbsence( item_type, coder )
