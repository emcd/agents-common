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
from . import cmdbase as _cmdbase
from . import context as _context
from . import exceptions as _exceptions
from . import renderers as _renderers


CoderFallbackMap: __.typx.TypeAlias = __.immut.Dictionary[ str, str ]
PluralMappings: __.typx.TypeAlias = __.immut.Dictionary[ str, str ]

_TEMPLATE_PARTS_MINIMUM = 3

_PLURAL_TO_SINGULAR_MAP: PluralMappings = __.immut.Dictionary( {
    'commands': 'command',
    'agents': 'agent',
} )


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
    configuration: _cmdbase.CoderConfiguration
    application_configuration: __.cabc.Mapping[ str, __.typx.Any ] = (
        __.dcls.field(
            default_factory = __.immut.Dictionary[ str, __.typx.Any ] ) )
    mode: _renderers.TargetMode = 'per-project'
    jinja_environment: _jinja2.Environment = __.dcls.field( init = False )

    def __post_init__( self ) -> None:
        self.jinja_environment = (  # pyright: ignore[reportAttributeAccessIssue]
            self._produce_jinja_environment( ) )


    def _retrieve_fallback_mappings( self ) -> CoderFallbackMap:
        ''' Retrieves coder fallback mappings from configuration. '''
        content_config = self.application_configuration.get( 'content', { } )
        fallbacks = content_config.get( 'fallbacks', { } )
        return __.immut.Dictionary( fallbacks )

    def render_single_item(
        self, item_type: str, item_name: str, coder: str, target: __.Path
    ) -> RenderedItem:
        ''' Renders a single item (command or agent) for a coder.

            Combines TOML metadata, content body, and template to produce
            final coder-specific file. Returns RenderedItem with content
            and location.
        '''
        try: renderer = _renderers.RENDERERS[ coder ]
        except KeyError as exception:
            raise _exceptions.CoderAbsence( coder ) from exception
        if self.mode == 'default':
            actual_mode = renderer.mode_default
        elif self.mode in ( 'per-user', 'per-project' ):
            actual_mode = self.mode
            renderer.validate_mode( actual_mode )
        else:
            raise _exceptions.TargetModeNoSupport( coder, self.mode )
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
        base_directory = renderer.resolve_base_directory(
            mode = actual_mode,
            target = target,
            configuration = self.application_configuration,
            environment = __.os.environ,
        )
        category = metadata[ 'context' ].get( 'category' )
        if category is None:
            category = __.absent
        dirname = renderer.produce_output_structure( item_type, category )
        location = base_directory / dirname / f"{item_name}.{extension}"
        return RenderedItem( content = content, location = location )

    def _survey_available_templates(
        self, item_type: str, coder: str
    ) -> list[ str ]:
        directory = self.location / "templates"
        # Validate coder exists in registry
        if coder not in _renderers.RENDERERS:
            raise _exceptions.CoderAbsence( coder )
        # Template directories always use plural form (commands, agents)
        source_dir = directory / item_type
        if not source_dir.exists():
            raise _exceptions.TemplateError.for_missing_template(
                coder, item_type
            )
        templates = [
            f"{item_type}/{p.name}"
            for p in source_dir.glob( "*.jinja" )
        ]
        if not templates:
            raise _exceptions.TemplateError.for_missing_template(
                coder, item_type
            )
        return templates

    def resolve_content_paths(
        self, item_type: str, item_name: str, coder: str
    ) -> tuple[ __.Path, __.typx.Optional[ __.Path ] ]:
        ''' Resolves primary and fallback content paths.

            Returns tuple of (primary_path, fallback_path) where fallback_path
            is None if no fallback coder is configured.

            This method is public to allow operations module to pre-check
            content availability without loading files.
        '''
        primary_path = (
            self.location / "contents" / item_type / coder /
            f"{item_name}.md" )
        fallback_path = None
        fallback_mappings = self._retrieve_fallback_mappings( )
        fallback_coder = fallback_mappings.get( coder )
        if fallback_coder:
            fallback_path = (
                self.location / "contents" / item_type /
                fallback_coder / f"{item_name}.md" )
        return ( primary_path, fallback_path )

    def _retrieve_content_with_fallback(
        self, item_type: str, item_name: str, coder: str
    ) -> str:
        ''' Retrieves content with fallback logic for compatible coders.

            Attempts to read content from coder-specific location first,
            then falls back to compatible coder if content is missing.
        '''
        primary_path, fallback_path = self.resolve_content_paths(
            item_type, item_name, coder )
        if primary_path.exists( ):
            return primary_path.read_text( encoding = 'utf-8' )
        if fallback_path and fallback_path.exists( ):
            fallback_coder = self._retrieve_fallback_mappings( ).get( coder )
            _scribe.debug( f"Using {fallback_coder} content for {coder}" )
            return fallback_path.read_text( encoding = 'utf-8' )
        raise _exceptions.ContentAbsence( item_type, item_name, coder )

    def _parse_template_extension( self, template_name: str ) -> str:
        ''' Extracts output extension from template filename.

            Template names follow pattern: item.extension.jinja
            This extracts the middle component as output extension.
        '''
        parts = template_name.split( '.' )
        if len( parts ) >= _TEMPLATE_PARTS_MINIMUM and parts[ -1 ] == 'jinja':
            return parts[ -2 ]
        raise _exceptions.TemplateError.for_extension_parse( template_name )

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
            raise _exceptions.ConfigurationAbsence( configuration_file )
        try: toml_content = configuration_file.read_bytes( )
        except ( OSError, IOError ) as exception:
            raise _exceptions.ConfigurationAbsence( ) from exception
        try: toml_data: dict[ str, __.typx.Any ] = __.tomli.loads(
            toml_content.decode( 'utf-8' ) )
        except __.tomli.TOMLDecodeError as exception:
            raise _exceptions.ConfigurationInvalidity(
                exception
            ) from exception
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
        try: renderer = _renderers.RENDERERS[ coder ]
        except KeyError as exception:
            raise _exceptions.CoderAbsence( coder ) from exception
        flavor = renderer.get_template_flavor( item_type )
        available = self._survey_available_templates( item_type, coder )
        # Template paths always use plural item_type (commands, agents)
        for extension in [ 'md', 'toml' ]:
            organized_path = (
                f"{item_type}/{flavor}.{extension}.jinja" )
            if organized_path in available:
                return organized_path
        raise _exceptions.TemplateError.for_missing_template(
            coder, item_type
        )
