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
from . import core as _core
from . import exceptions as _exceptions
from . import results as _results


CoderConfiguration: __.typx.TypeAlias = __.cabc.Mapping[ str, __.typx.Any ]


_TEMPLATE_PARTS_MINIMUM = 3

_scribe = __.provide_scribe( __name__ )


class RenderedItem( __.immut.DataclassObject ):
    ''' Single rendered item with location and content. '''

    content: str
    location: __.Path


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
                if isinstance( auxdata, _core.Globals ):
                    await _core.render_and_print_result(
                        exception, auxdata.display, auxdata.exits )
                else:
                    for line in exception.render_as_markdown( ):
                        print( line, file = __.sys.stderr )
                raise SystemExit( 1 ) from None
        return wrapper
    return decorator


class DetectCommand( __.appcore_cli.Command ):
    ''' Detects and displays current Copier configuration for agents. '''

    source: __.typx.Annotated[
        __.Path,
        __.tyro.conf.arg(
            help = "Target directory to search for configuration." ),
    ] = __.dcls.field( default_factory = __.Path.cwd )

    @intercept_errors( )
    async def execute( self, auxdata: __.appcore.state.Globals ) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        ''' Detects agent configuration and displays formatted result. '''
        if not isinstance( auxdata, _core.Globals ):  # pragma: no cover
            raise _exceptions.ContextInvalidity
        _scribe.info( f"Detecting agent configuration in {self.source}" )
        configuration = await self._detect_configuration( self.source )
        _scribe.debug( f"Found configuration: {configuration}" )
        result = _results.ConfigurationDetectionResult(
            target = self.source,
            coders = tuple( configuration[ 'coders' ] ),
            languages = tuple( configuration[ 'languages' ] ),
            project_name = configuration.get( 'project_name' ),
        )
        await _core.render_and_print_result(
            result, auxdata.display, auxdata.exits )

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
        if not configuration.get( 'coders' ):
            raise _exceptions.ConfigurationInvalidity( )
        if not configuration.get( 'languages' ):
            raise _exceptions.ConfigurationInvalidity( )


class ContentGenerator( __.immut.DataclassObject ):
    ''' Generates coder-specific content from data sources. '''

    location: __.Path
    configuration: CoderConfiguration
    jinja_environment: _jinja2.Environment = __.dcls.field( init = False )

    def __post_init__( self ) -> None:
        self.jinja_environment = ( # pyright: ignore[reportAttributeAccessIssue]
            self._provide_jinja_environment( ) )

    def generate(
        self, target: __.Path, simulate: bool = True
    ) -> None:
        ''' Generates content for all configured coders. '''
        for coder in self.configuration[ "coders" ]:
            self._generate_coder_content( coder, target, simulate )

    def render_single_item(
        self, item_type: str, item_name: str, coder: str, target: __.Path
    ) -> RenderedItem:
        ''' Renders a single item (command or agent) for a coder.

            Returns RenderedItem with content and location.
        '''
        body = self._get_content_with_fallback( item_type, item_name, coder )
        metadata = self._load_item_metadata( item_type, item_name, coder )
        template_name = self._select_template_for_coder( item_type, coder )
        template = self.jinja_environment.get_template( template_name )
        variables: dict[ str, __.typx.Any ] = {
            'content': body,
            'coder': metadata[ 'coder' ],
            **metadata[ 'frontmatter' ],
        }
        content = template.render( **variables )
        extension = self._get_output_extension( template_name )
        location = (
            target / ".auxiliary" / "configuration" / coder /
            item_type / f"{item_name}.{extension}" )
        return RenderedItem( content = content, location = location )

    def _generate_coder_content(
        self, coder: str, target: __.Path, simulate: bool
    ) -> None:
        ''' Generates commands and agents for specific coder. '''
        _scribe.info( f"Generating content for {coder}" )
        self._render_item_type( "commands", coder, target, simulate )
        self._render_item_type( "agents", coder, target, simulate )

    def _get_available_templates( self, item_type: str ) -> list[ str ]:
        ''' Gets available templates for item type. '''
        directory = self.location / "templates"
        singular_type = item_type.rstrip( 's' )
        pattern = f"{singular_type}.*.jinja"
        return [ p.name for p in directory.glob( pattern ) ]

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
                _scribe.debug( f"Using {fallback_coder} content for {coder}" )
                return fallback_path.read_text( encoding = 'utf-8' )
        raise _exceptions.ContentAbsence( item_type, item_name, coder )

    def _get_output_extension( self, template_name: str ) -> str:
        ''' Extracts output extension from template name. '''
        parts = template_name.split( '.' )
        if len( parts ) >= _TEMPLATE_PARTS_MINIMUM and parts[ -1 ] == 'jinja':
            return parts[ -2 ]
        raise _exceptions.TemplateExtensionError( template_name )

    def _load_item_metadata(
        self, item_type: str, item_name: str, coder: str
    ) -> dict[ str, __.typx.Any ]:
        ''' Loads TOML metadata and extracts frontmatter and coder config. '''
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
            raise _exceptions.ConfigurationInvalidity( ) from exception
        frontmatter = toml_data.get( 'frontmatter', { } )
        coders = toml_data.get( 'coders', [ ] )
        coder_config = next(
            ( c for c in coders if c.get( 'name' ) == coder ),
            { 'name': coder } )
        return { 'frontmatter': frontmatter, 'coder': coder_config }

    def _provide_jinja_environment( self ) -> _jinja2.Environment:
        ''' Provides Jinja2 environment with templates directory. '''
        directory = self.location / "templates"
        loader = _jinja2.FileSystemLoader( directory )
        return _jinja2.Environment( loader = loader, autoescape = True )

    def _render_item_type(
        self, item_type: str, coder: str, target: __.Path, simulate: bool
    ) -> None:
        ''' Renders all items of a specific type for a coder. '''
        configuration_directory = self.location / "configurations" / item_type
        if not configuration_directory.exists( ):
            _scribe.warning( f"No {item_type} configurations found" )
            return
        for configuration_file in configuration_directory.glob( "*.toml" ):
            self._render_single_item(
                item_type, configuration_file.stem, coder, target, simulate )

    def _render_single_item(
        self, item_type: str, item_name: str, coder: str,
        target: __.Path, simulate: bool
    ) -> None:
        ''' Renders a single item and logs status (legacy method). '''
        result = self.render_single_item( item_type, item_name, coder, target )
        _scribe.debug( f"Generated {result.location}" )
        if simulate:
            _scribe.debug(
                f"Content preview: {len( result.content )} characters" )

    def _select_template_for_coder( self, item_type: str, coder: str ) -> str:
        ''' Selects appropriate template based on coder capabilities. '''
        available = self._get_available_templates( item_type )
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
            raise _exceptions.UnsupportedCoderError( coder )
        raise _exceptions.TemplateAbsence( item_type, coder )


class PopulateCommand( __.appcore_cli.Command ):
    ''' Generates dynamic agent content from data sources. '''

    source: __.typx.Annotated[
        str,
        __.tyro.conf.arg( help = "Data source (local path or git URL)" ),
    ] = '.'
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
        if not isinstance( auxdata, _core.Globals ):  # pragma: no cover
            raise _exceptions.ContextInvalidity
        _scribe.info(
            f"Populating agent content from {self.source} to {self.target}" )
        configuration = await self._detect_configuration( self.target )
        coder_count = len( configuration[ 'coders' ] )
        _scribe.debug( f"Detected configuration with {coder_count} coders" )
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
        await _core.render_and_print_result(
            result, auxdata.display, auxdata.exits )

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
        if not configuration.get( 'coders' ):
            raise _exceptions.ConfigurationInvalidity( )
        if not configuration.get( 'languages' ):
            raise _exceptions.ConfigurationInvalidity( )


class SurveyCommand( __.appcore_cli.Command ):
    ''' Surveys available configuration variants. '''

    @intercept_errors( )
    async def execute( self, auxdata: __.appcore.state.Globals ) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        ''' Lists available configuration variants. '''
        if not isinstance( auxdata, _core.Globals ):  # pragma: no cover
            raise _exceptions.ContextInvalidity
        for variant in survey_variants( auxdata ):
            print( variant )


class ValidateCommand( __.appcore_cli.Command ):
    ''' Validates template generation in temporary directory. '''

    variant: __.typx.Annotated[
        str,
        __.tyro.conf.arg(
            help = "Configuration variant to test.",
            prefix_name = False ),
    ] = 'default'
    preserve: __.typx.Annotated[
        bool,
        __.tyro.conf.arg(
            help = "Keep temporary files for inspection.",
            prefix_name = False ),
    ] = False

    @intercept_errors( )
    async def execute( self, auxdata: __.appcore.state.Globals ) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        ''' Validates template generation and displays result. '''
        if not isinstance( auxdata, _core.Globals ):  # pragma: no cover
            raise _exceptions.ContextInvalidity
        _scribe.info( f"Validating template generation for {self.variant}" )
        try: temporary_directory = __.Path( __.tempfile.mkdtemp(
            prefix = f"agents-validate-{self.variant}-" ) )
        except ( OSError, IOError ) as exception:
            raise _exceptions.DirectoryCreateFailure(
                __.Path( __.tempfile.gettempdir( ) ) ) from exception
        _scribe.debug( f"Created temporary directory: {temporary_directory}" )
        try:
            configuration = self._create_test_configuration( auxdata )
            location = _retrieve_data_location( "defaults" )
            generator = ContentGenerator(
                location = location, configuration = configuration )
            items_attempted, items_generated = populate_directory(
                generator, temporary_directory, simulate = False )
            _scribe.info(
                f"Generated {items_generated}/{items_attempted} items" )
        finally:
            if not self.preserve:
                _scribe.debug(
                    f"Cleaning up temporary directory: {temporary_directory}" )
                with __.ctxl.suppress( OSError, IOError ):
                    __.shutil.rmtree( temporary_directory )
        result = _results.ValidationResult(
            variant = self.variant,
            temporary_directory = temporary_directory,
            items_attempted = items_attempted,
            items_generated = items_generated,
            preserved = self.preserve,
        )
        await _core.render_and_print_result(
            result, auxdata.display, auxdata.exits )

    def _create_test_configuration(
        self, auxdata: _core.Globals
    ) -> CoderConfiguration:
        ''' Creates test configuration for specified variant. '''
        answers_file = _retrieve_variant_answers_file( auxdata, self.variant )
        try: content = answers_file.read_text( encoding = 'utf-8' )
        except ( OSError, IOError ) as exception:
            raise _exceptions.ConfigurationAbsence( ) from exception
        try: configuration: CoderConfiguration = _yaml.safe_load( content )
        except _yaml.YAMLError as exception:
            raise _exceptions.ConfigurationInvalidity( ) from exception
        if not isinstance( configuration, __.cabc.Mapping ):
            raise _exceptions.ConfigurationInvalidity( )
        return __.immut.Dictionary( configuration )


def populate_directory(
    generator: ContentGenerator, target: __.Path, simulate: bool = False
) -> tuple[ int, int ]:
    ''' Generates all content items to target directory.

        Returns tuple of (items_attempted, items_written).
    '''
    items_attempted = 0
    items_written = 0
    for coder in generator.configuration[ 'coders' ]:
        for item_type in ( 'commands', 'agents' ):
            attempted, written = _generate_coder_item_type(
                generator, coder, item_type, target, simulate )
            items_attempted += attempted
            items_written += written
    return ( items_attempted, items_written )


def survey_variants( auxdata: _core.Globals ) -> tuple[ str, ... ]:
    ''' Surveys available configuration variants from data directory. '''
    data_directory = auxdata.provide_data_location( )
    profiles_directory = data_directory / 'agentsmgr' / 'profiles'
    if not profiles_directory.exists( ): return ( )
    return tuple(
        fsent.stem.removeprefix( 'answers-' )
        for fsent in profiles_directory.glob( 'answers-*.yaml' )
        if fsent.is_file( ) )


def update_content(
    content: str, location: __.Path, simulate: bool = False
) -> bool:
    ''' Updates content file, creating directories as needed.

        Returns True if file was written, False if simulated.
    '''
    if simulate: return False
    try: location.parent.mkdir( parents = True, exist_ok = True )
    except ( OSError, IOError ) as exception:
        raise _exceptions.DirectoryCreateFailure(
            location.parent ) from exception
    try: location.write_text( content, encoding = 'utf-8' )
    except ( OSError, IOError ) as exception:
        raise _exceptions.ContentUpdateFailure( location ) from exception
    return True


def _generate_coder_item_type(
    generator: ContentGenerator,
    coder: str,
    item_type: str,
    target: __.Path,
    simulate: bool
) -> tuple[ int, int ]:
    ''' Generates items of specific type for a coder.

        Returns tuple of (items_attempted, items_written).
    '''
    items_attempted = 0
    items_written = 0
    configuration_directory = (
        generator.location / 'configurations' / item_type )
    if not configuration_directory.exists( ):
        return ( items_attempted, items_written )
    for configuration_file in configuration_directory.glob( '*.toml' ):
        items_attempted += 1
        result = generator.render_single_item(
            item_type, configuration_file.stem, coder, target )
        if update_content( result.content, result.location, simulate ):
            items_written += 1
    return ( items_attempted, items_written )


def _retrieve_data_location( source_spec: str ) -> __.Path:
    ''' Retrieves data source location and returns local path. '''
    if not source_spec.startswith( ( 'http', 'git@', 'gh:' ) ):
        return __.Path( source_spec ).resolve( )
    raise _exceptions.UnsupportedSourceError( source_spec )


def _retrieve_variant_answers_file(
    auxdata: _core.Globals, variant: str
) -> __.Path:
    ''' Retrieves path to variant answers file in data directory. '''
    data_directory = auxdata.provide_data_location( )
    answers_file = (
        data_directory / 'agentsmgr' / 'profiles' / f"answers-{variant}.yaml" )
    if not answers_file.exists( ):
        raise _exceptions.ConfigurationAbsence( )
    return answers_file
