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


''' Command implementations for agentsmgr CLI. '''


import jinja2 as _jinja2
import yaml as _yaml

from . import __
from . import exceptions as _exceptions
from . import results as _results

CoderConfiguration: __.typx.TypeAlias = __.cabc.Mapping[ str, __.typx.Any ]

_TEMPLATE_PARTS_MINIMUM = 3


def intercept_errors( ) -> __.cabc.Callable[
    [ __.cabc.Callable[
        ..., __.cabc.Coroutine[ __.typx.Any, __.typx.Any, None ] ] ],
    __.cabc.Callable[
        ..., __.cabc.Coroutine[ __.typx.Any, __.typx.Any, None ] ]
]:
    ''' Decorator for CLI handlers to intercept and render exceptions. '''
    def decorator(
        function: __.cabc.Callable[
            ..., __.cabc.Coroutine[ __.typx.Any, __.typx.Any, None ] ]
    ) -> __.cabc.Callable[
        ..., __.cabc.Coroutine[ __.typx.Any, __.typx.Any, None ]
    ]:
        @__.funct.wraps( function )
        async def wrapper(
            self: __.typx.Any,
            auxdata: __.typx.Any,
            *posargs: __.typx.Any,
            **nomargs: __.typx.Any,
        ) -> None:
            try: return await function( self, auxdata, *posargs, **nomargs )
            except _exceptions.Omnierror as exception:
                for line in exception.render_as_markdown( ):
                    print( line, file = __.sys.stderr )
                raise SystemExit( 1 ) from None
        return wrapper
    return decorator


class DetectCommand( __.appcore_cli.Command ):
    ''' Detects and displays current Copier configuration for agents. '''

    target: __.typx.Annotated[
        __.Path,
        __.tyro.conf.arg(
            help = "Target directory to search for configuration." ),
    ] = __.dcls.field( default_factory = __.Path.cwd )

    @intercept_errors( )
    async def execute( self, auxdata: __.appcore.state.Globals ) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        ''' Detects agent configuration and displays formatted result. '''
        configuration = await self._detect_configuration( self.target )
        result = _results.ConfigurationDetectionResult(
            target = self.target,
            coders = tuple( configuration[ 'coders' ] ),
            languages = tuple( configuration[ 'languages' ] ),
            project_name = configuration.get( 'project_name' ),
        )
        for line in result.render_as_markdown( ):
            print( line )

    async def _detect_configuration(
        self, target: __.Path
    ) -> __.cabc.Mapping[ str, __.typx.Any ]:
        ''' Loads configuration from Copier answers file. '''
        answers_file = (
            target / ".auxiliary/configuration/copier-answers--agents.yaml" )
        if not answers_file.exists( ):
            raise _exceptions.ConfigurationAbsence( target )
        try: content = answers_file.read_text( encoding = 'utf-8' )
        except ( OSError, IOError ) as exception:
            raise _exceptions.ConfigurationAbsence( ) from exception
        try:
            configuration: __.cabc.Mapping[ str, __.typx.Any ] = (
                _yaml.safe_load( content ) )
        except _yaml.YAMLError as exception:
            raise _exceptions.ConfigurationInvalidity( ) from exception
        if not isinstance( configuration, __.cabc.Mapping ):
            raise _exceptions.ConfigurationInvalidity( )
        await self._validate_configuration( configuration )
        return configuration

    async def _validate_configuration(
        self, configuration: __.cabc.Mapping[ str, __.typx.Any ]
    ) -> None:
        ''' Validates required configuration fields. '''
        if not configuration.get( "coders" ):
            raise _exceptions.ConfigurationInvalidity( )
        if not configuration.get( "languages" ):
            raise _exceptions.ConfigurationInvalidity( )


def _retrieve_data_location( source_spec: str ) -> __.Path:
    ''' Retrieves data source location and returns local path. '''
    if not source_spec.startswith( ( 'http', 'git@', 'gh:' ) ):
        return __.Path( source_spec ).resolve( )
    raise _exceptions.UnsupportedSourceError( source_spec )


class ContentGenerator( __.immut.DataclassObject ):
    ''' Generates coder-specific content from data sources. '''

    location: __.Path
    configuration: CoderConfiguration
    jinja_environment: _jinja2.Environment = __.dcls.field( init = False )

    def __post_init__( self ) -> None:
        self.jinja_environment = ( # pyright: ignore[reportAttributeAccessIssue]
            self._provide_jinja_environment( ) )

    def _provide_jinja_environment( self ) -> _jinja2.Environment:
        ''' Provides Jinja2 environment with templates directory. '''
        directory = self.location / "templates"
        loader = _jinja2.FileSystemLoader( directory )
        return _jinja2.Environment( loader = loader, autoescape = True )

    def generate(
        self, target: __.Path, simulate: bool = True
    ) -> None:
        ''' Generates content for all configured coders. '''
        try:
            for coder in self.configuration[ "coders" ]:
                self._generate_coder_content( coder, target, simulate )
        except Exception as exception:
            print( f"⚠️  Failed to generate {coder} content: {exception}" )

    def _generate_coder_content(
        self, coder: str, target: __.Path, simulate: bool
    ) -> None:
        ''' Generates commands and agents for specific coder. '''
        print( f"📁 Generating content for {coder}:" )
        self._render_item_type( "commands", coder, target, simulate )
        self._render_item_type( "agents", coder, target, simulate )

    def _render_item_type(
        self, item_type: str, coder: str, target: __.Path, simulate: bool
    ) -> None:
        ''' Renders all items of a specific type for a coder. '''
        configuration_directory = self.location / "configurations" / item_type
        if not configuration_directory.exists( ):
            print( f"   ⚠️  No {item_type} configurations found" )
            return
        for configuration_file in configuration_directory.glob( "*.toml" ):
            self._render_single_item(
                item_type, configuration_file.stem, coder, target, simulate )

    def _render_single_item(
        self, item_type: str, item_name: str, coder: str,
        target: __.Path, simulate: bool
    ) -> None:
        ''' Renders a single item (command or agent) for a coder. '''
        content = self._get_content_with_fallback(
            item_type, item_name, coder )
        template_name = self._select_template_for_coder( item_type, coder )
        template = self.jinja_environment.get_template( template_name )
        variables: dict[ str, __.typx.Any ] = {
            'content': content, 'coder': { 'name': coder } }
        rendered = template.render( **variables )
        extension = self._get_output_extension( template_name )
        output_path = (
            target / ".auxiliary" / "configuration" / coder /
            item_type / f"{item_name}.{extension}" )
        print( f"   ✅ {output_path}" )
        if simulate:
            print( f"      Content preview: {len( rendered )} characters" )

    def _get_content_with_fallback(
        self, item_type: str, item_name: str, coder: str
    ) -> str:
        ''' Gets content with Claude↔OpenCode fallback logic. '''
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
                print( f"   🔄 Using {fallback_coder} content for {coder}" )
                return fallback_path.read_text( encoding = 'utf-8' )
        raise _exceptions.ContentAbsence( item_type, item_name, coder )

    def _select_template_for_coder( self, item_type: str, coder: str ) -> str:
        ''' Selects appropriate template based on coder capabilities. '''
        available = self._get_available_templates( item_type )
        preferences = {
            "claude": [ f"{item_type}.md.jinja" ],
            "opencode": [ f"{item_type}.md.jinja" ],
            "gemini": [ f"{item_type}.toml.jinja" ],
        }
        for preferred in preferences.get( coder, [ ] ):
            if preferred in available:
                return preferred
        if coder not in preferences:
            raise _exceptions.UnsupportedCoderError( coder )
        raise _exceptions.TemplateAbsence( item_type, coder )

    def _get_available_templates( self, item_type: str ) -> list[ str ]:
        ''' Gets available templates for item type. '''
        directory = self.location / "templates"
        pattern = f"{item_type}.*.jinja"
        return [ p.name for p in directory.glob( pattern ) ]

    def _get_output_extension( self, template_name: str ) -> str:
        ''' Extracts output extension from template name. '''
        parts = template_name.split( '.' )
        if len( parts ) >= _TEMPLATE_PARTS_MINIMUM and parts[ -1 ] == 'jinja':
            return parts[ -2 ]
        return 'txt'


class PopulateCommand( __.appcore_cli.Command ):
    ''' Generates dynamic agent content from data sources. '''

    source: __.typx.Annotated[
        str,
        __.tyro.conf.arg( help = "Data source (local path or git URL)" ),
    ] = "."

    target: __.typx.Annotated[
        __.Path,
        __.tyro.conf.arg( help = "Target directory for content generation" ),
    ] = __.dcls.field( default_factory = __.Path.cwd )

    simulate: __.typx.Annotated[
        bool,
        __.tyro.conf.arg( help = "Dry run mode - show generated content" ),
    ] = True

    @intercept_errors( )
    async def execute( self, auxdata: __.appcore.state.Globals ) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        ''' Generates content from data sources and displays result. '''
        configuration = await self._detect_configuration( self.target )
        location = _retrieve_data_location( self.source )
        generator = ContentGenerator(
            location = location, configuration = configuration )
        generator.generate( self.target, self.simulate )
        result = _results.ContentGenerationResult(
            source_location = location,
            target_location = self.target,
            coders = tuple( configuration[ 'coders' ] ),
            simulated = self.simulate,
            items_generated = 0,
        )
        for line in result.render_as_markdown( ):
            print( line )

    async def _detect_configuration(
        self, target: __.Path
    ) -> __.cabc.Mapping[ str, __.typx.Any ]:
        ''' Loads configuration from Copier answers file. '''
        answers_file = (
            target / ".auxiliary/configuration/copier-answers--agents.yaml" )
        if not answers_file.exists( ):
            raise _exceptions.ConfigurationAbsence( target )
        try: content = answers_file.read_text( encoding = 'utf-8' )
        except ( OSError, IOError ) as exception:
            raise _exceptions.ConfigurationAbsence( ) from exception
        try:
            configuration: __.cabc.Mapping[ str, __.typx.Any ] = (
                _yaml.safe_load( content ) )
        except _yaml.YAMLError as exception:
            raise _exceptions.ConfigurationInvalidity( ) from exception
        if not isinstance( configuration, __.cabc.Mapping ):
            raise _exceptions.ConfigurationInvalidity( )
        await self._validate_configuration( configuration )
        return configuration

    async def _validate_configuration(
        self, configuration: __.cabc.Mapping[ str, __.typx.Any ]
    ) -> None:
        ''' Validates required configuration fields. '''
        if not configuration.get( "coders" ):
            raise _exceptions.ConfigurationInvalidity( )
        if not configuration.get( "languages" ):
            raise _exceptions.ConfigurationInvalidity( )
