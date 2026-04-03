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


''' Commands for Copier template survey and validation. '''


from . import __


_scribe = __.provide_scribe( __name__ )


class SurveyCommand( __.appcore_cli.Command ):
    ''' Surveys available template configuration variants. '''

    @__.cmdbase.intercept_errors( )
    async def execute( self, auxdata: __.appcore.state.Globals ) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        if not isinstance( auxdata, __.Globals ):  # pragma: no cover
            raise __.ContextInvalidity
        stream = await auxdata.display.provide_stream( auxdata.exits )
        for variant in survey_variants( auxdata ):
            print( variant, file = stream )


class ValidateCommand( __.appcore_cli.Command ):
    ''' Validates Copier template using configuration variant answers. '''

    variant: __.typx.Annotated[
        str,
        __.typx.Doc( ''' Configuration variant to validate. ''' ),
        __.tyro.conf.Positional,
    ]
    preserve: __.typx.Annotated[
        bool,
        __.tyro.conf.arg(
            help = "Keep temporary files for inspection.",
            prefix_name = False ),
    ] = False

    @__.cmdbase.intercept_errors( )
    async def execute( self, auxdata: __.appcore.state.Globals ) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        if not isinstance( auxdata, __.Globals ):  # pragma: no cover
            raise __.ContextInvalidity
        _scribe.info( f"Validating Copier template for {self.variant}" )
        repository_directory = _provide_repository_directory( )
        answers_file = __.cmdbase.retrieve_variant_answers_file(
            auxdata, self.variant )
        try: temporary_directory = __.Path( __.tempfile.mkdtemp(
            prefix = f"agents-template-{self.variant}-" ) )
        except ( OSError, IOError ) as exception:
            raise __.FileOperationFailure(
                __.Path( __.tempfile.gettempdir( ) ),
                "create directory" ) from exception
        _scribe.debug( f"Created temporary directory: {temporary_directory}" )
        try:
            project_directory = temporary_directory / self.variant
            commands = _provide_validation_commands(
                repository_directory, project_directory )
            _copy_template(
                answers_file,
                project_directory,
                repository_directory,
            )
            _validate_variant_project( commands, repository_directory )
            result = __.ValidationResult(
                variant = self.variant,
                temporary_directory = temporary_directory,
                items_attempted = len( commands ) + 1,
                items_generated = len( commands ) + 1,
                preserved = self.preserve,
            )
        finally:
            if not self.preserve:
                _scribe.debug(
                    f"Cleaning up temporary directory: {temporary_directory}" )
                with __.ctxl.suppress( OSError, IOError ):
                    __.shutil.rmtree( temporary_directory )
        await __.render_and_print_result(
            result, auxdata.display, auxdata.exits )


class CommandDispatcher( __.appcore_cli.Command ):
    ''' Dispatches maintainer commands for Copier template workflows. '''

    command: __.typx.Union[
        __.typx.Annotated[
            SurveyCommand,
            __.tyro.conf.subcommand( 'survey', prefix_name = False ),
        ],
        __.typx.Annotated[
            ValidateCommand,
            __.tyro.conf.subcommand( 'validate', prefix_name = False ),
        ],
    ] = __.dcls.field( default_factory = SurveyCommand )

    async def execute( self, auxdata: __.appcore.state.Globals ) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        await self.command( auxdata )


def survey_variants( auxdata: __.Globals ) -> tuple[ str, ... ]:
    ''' Surveys available template configuration variants. '''
    return __.cmdbase.survey_variant_names( auxdata )


def _copy_template(
    answers_file: __.Path,
    project_directory: __.Path,
    repository_directory: __.Path,
) -> None:
    ''' Copies template to temporary project directory using answers file. '''
    command = (
        'copier', 'copy',
        '--data-file', str( answers_file ),
        '--defaults',
        '--overwrite',
        '--vcs-ref', 'HEAD',
        '.', str( project_directory ),
    )
    _run_checked_command( command, repository_directory )


def _provide_repository_directory( ) -> __.Path:
    ''' Provides repository directory for template-copy operations. '''
    repository_directory = __.Path.cwd( )
    if not ( repository_directory / 'copier.yaml' ).is_file( ):
        raise __.ConfigurationAbsence( repository_directory )
    if not ( repository_directory / 'template' ).is_dir( ):
        raise __.ConfigurationAbsence( repository_directory )
    return repository_directory


def _provide_validation_commands(
    repository_directory: __.Path,
    project_directory: __.Path,
) -> tuple[ tuple[ str, ... ], ... ]:
    ''' Provides validation commands for generated template project. '''
    # Keep template validation narrowly focused on Copier rendering.
    # Content generation is validated via `agentsmgr-maintain content`.
    return (
        (
            'hatch', '--env', 'develop', 'run',
            'agentsmgr', 'detect',
            '--source', str( project_directory ),
        ),
    )


def _run_checked_command(
    command: tuple[ str, ... ], cwd: __.Path
) -> None:
    ''' Runs command and converts failures into configuration errors. '''
    try: __.subprocess.run( command, cwd = cwd, check = True )
    except FileNotFoundError as exception:
        raise __.ConfigurationInvalidity( exception ) from exception
    except __.subprocess.CalledProcessError as exception:
        raise __.ConfigurationInvalidity( exception ) from exception


def _validate_variant_project(
    commands: tuple[ tuple[ str, ... ], ... ],
    repository_directory: __.Path,
) -> None:
    ''' Validates generated project with configured command sequence. '''
    for command in commands:
        _scribe.debug( f"Running validation command: {' '.join( command )}" )
        _run_checked_command( command, repository_directory )
