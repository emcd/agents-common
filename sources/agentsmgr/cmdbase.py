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


''' Shared infrastructure for command implementations.

    This module provides common utilities used across multiple command
    implementations, including error handling, configuration management,
    and data location resolution.
'''


import yaml as _yaml

from . import __
from . import core as _core
from . import exceptions as _exceptions
from . import nomina as _nomina
from . import sources as _sources


CoderConfiguration: __.typx.TypeAlias = __.cabc.Mapping[ str, __.typx.Any ]


def intercept_errors( ) -> __.cabc.Callable[
    [ __.cabc.Callable[
        ..., __.cabc.Coroutine[ __.typx.Any, __.typx.Any, None ] ] ],
    __.cabc.Callable[
        ..., __.cabc.Coroutine[ __.typx.Any, __.typx.Any, None ] ]
]:
    ''' Decorator for CLI command handlers to intercept and render errors.

        Provides clean separation between business logic and error handling:

        **Purpose**: Enables command implementations to focus purely on
        business logic while the decorator handles all error presentation
        concerns.

        **Responsibilities**:

        - Intercepts Omnierror exceptions from command execution
        - Renders errors in appropriate format (markdown for CLI)
        - Ensures proper exit code handling (SystemExit with code 1)

        **Pattern**: Commands implement business logic and raise exceptions;
        decorator handles presentation and process termination. This
        separation ensures commands remain testable and focused.

        **Type narrowing note**: The isinstance(auxdata, _core.Globals)
        checks in individual command execute methods serve type narrowing
        purposes and must be retained for proper type checking.
    '''
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


async def retrieve_configuration(
    target: __.Path,
    profile: __.typx.Optional[ __.Path ] = None,
) -> __.cabc.Mapping[ str, __.typx.Any ]:
    ''' Loads and validates configuration from Copier answers file.

        Unified configuration loading used by multiple command
        implementations. Reads from standard Copier answers location
        (or specified profile path) and validates required fields.
    '''
    if profile is not None:
        answers_file = profile
    else:
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
        raise _exceptions.ConfigurationInvalidity( exception ) from exception
    if not isinstance( configuration, __.cabc.Mapping ):
        raise _exceptions.ConfigurationInvalidity( )
    await validate_configuration( configuration )
    return configuration


async def validate_configuration(
    configuration: __.cabc.Mapping[ str, __.typx.Any ]
) -> None:
    ''' Validates required configuration fields are present and non-empty. '''
    if not configuration.get( 'coders' ):
        raise _exceptions.ConfigurationInvalidity( )
    if not configuration.get( 'languages' ):
        raise _exceptions.ConfigurationInvalidity( )


def retrieve_data_location(
    source_spec: str,
    tag_prefix: _nomina.TagPrefixArgument = __.absent,
) -> __.Path:
    ''' Resolves data source specification to local filesystem path.

        Supports local paths, Git repositories, and remote sources through
        pluggable source handlers. Uses registered handlers to resolve
        various URL schemes to local filesystem paths.
    '''
    return _sources.resolve_source_location( source_spec, tag_prefix )


def retrieve_variant_answers_file(
    auxdata: _core.Globals, variant: str
) -> __.Path:
    ''' Retrieves path to variant answers file in test data directory.

        Validates file existence and raises ConfigurationAbsence if not
        found.
    '''
    data_directory = auxdata.provide_data_location( )
    project_root = data_directory.parent
    answers_file = (
        project_root / 'tests' / 'data' / 'profiles'
        / f"answers-{variant}.yaml" )
    if not answers_file.exists( ):
        raise _exceptions.ConfigurationAbsence( )
    return answers_file
