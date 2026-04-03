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


''' Commands for validating generated content in temporary directories. '''


import yaml as _yaml

from . import __


_scribe = __.provide_scribe( __name__ )


class ValidateCommand( __.appcore_cli.Command ):
    ''' Validates content generation in temporary directory. '''

    variant: __.typx.Annotated[
        str,
        __.typx.Doc( ''' Configuration variant to test. ''' ),
        __.tyro.conf.Positional,
    ] = 'default'
    preserve: __.typx.Annotated[
        bool,
        __.tyro.conf.arg(
            help = "Keep temporary files for inspection.",
            prefix_name = False ),
    ] = False

    @__.cmdbase.intercept_errors( )
    async def execute( self, auxdata: __.appcore.state.Globals ) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        ''' Validates content generation and displays result. '''
        if not isinstance( auxdata, __.Globals ):  # pragma: no cover
            raise __.ContextInvalidity
        _scribe.info( f"Validating content generation for {self.variant}" )
        try: temporary_directory = __.Path( __.tempfile.mkdtemp(
            prefix = f"agents-validate-{self.variant}-" ) )
        except ( OSError, IOError ) as exception:
            raise __.FileOperationFailure(
                __.Path( __.tempfile.gettempdir( ) ),
                "create directory" ) from exception
        _scribe.debug( f"Created temporary directory: {temporary_directory}" )
        try:
            configuration = self._produce_test_configuration( auxdata )
            location = __.cmdbase.retrieve_data_location( "defaults" )
            generator = __.generator.ContentGenerator(
                location = location, configuration = configuration )
            items_attempted, items_generated = (
                __.operations.populate_directory(
                    generator, temporary_directory, simulate = False ) )
            _scribe.info(
                f"Generated {items_generated}/{items_attempted} items" )
        finally:
            if not self.preserve:
                _scribe.debug(
                    f"Cleaning up temporary directory: {temporary_directory}" )
                with __.ctxl.suppress( OSError, IOError ):
                    __.shutil.rmtree( temporary_directory )
        result = __.ValidationResult(
            variant = self.variant,
            temporary_directory = temporary_directory,
            items_attempted = items_attempted,
            items_generated = items_generated,
            preserved = self.preserve,
        )
        await __.render_and_print_result(
            result, auxdata.display, auxdata.exits )

    def _produce_test_configuration(
        self, auxdata: __.Globals
    ) -> __.cmdbase.CoderConfiguration:
        ''' Produces test configuration for specified variant.

            Creates configuration by loading variant answers file from
            data directory.
        '''
        answers_file = __.cmdbase.retrieve_variant_answers_file(
            auxdata, self.variant )
        try: content = answers_file.read_text( encoding = 'utf-8' )
        except ( OSError, IOError ) as exception:
            raise __.ConfigurationAbsence( ) from exception
        try:
            configuration: __.cmdbase.CoderConfiguration = (
                _yaml.safe_load( content ) )
        except _yaml.YAMLError as exception:
            raise __.ConfigurationInvalidity( exception ) from exception
        if not isinstance( configuration, __.cabc.Mapping ):
            raise __.ConfigurationInvalidity( )
        return __.immut.Dictionary( configuration )


class SurveyCommand( __.appcore_cli.Command ):
    ''' Surveys available configuration variants for content validation. '''

    @__.cmdbase.intercept_errors( )
    async def execute( self, auxdata: __.appcore.state.Globals ) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        if not isinstance( auxdata, __.Globals ):  # pragma: no cover
            raise __.ContextInvalidity
        stream = await auxdata.display.provide_stream( auxdata.exits )
        for variant in survey_variants( auxdata ):
            print( variant, file = stream )


class CommandDispatcher( __.appcore_cli.Command ):
    ''' Dispatches maintainer commands for generated content validation. '''

    command: __.typx.Union[
        __.typx.Annotated[
            SurveyCommand,
            __.tyro.conf.subcommand( 'survey', prefix_name = False ),
        ],
        __.typx.Annotated[
            ValidateCommand,
            __.tyro.conf.subcommand( 'validate', prefix_name = False ),
        ],
    ] = __.dcls.field( default_factory = ValidateCommand )

    async def execute( self, auxdata: __.appcore.state.Globals ) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        await self.command( auxdata )


def survey_variants( auxdata: __.Globals ) -> tuple[ str, ... ]:
    ''' Surveys available configuration variants. '''
    return __.cmdbase.survey_variant_names( auxdata )
