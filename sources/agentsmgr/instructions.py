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


''' Instruction file population from Git sources.

    This module provides functionality for downloading and preprocessing
    documentation instruction files from Git repositories, supporting
    flexible configuration through Copier answers.
'''


from . import __
from . import exceptions as _exceptions
from . import sources as _sources


InstructionSourceConfiguration: __.typx.TypeAlias = (
    __.cabc.Mapping[ str, __.typx.Any ] )
FilePreprocessingConfiguration: __.typx.TypeAlias = (
    __.cabc.Mapping[ str, __.typx.Any ] )


_scribe = __.provide_scribe( __name__ )


def populate_instructions(
    sources_configuration: __.cabc.Sequence[ InstructionSourceConfiguration ],
    target: __.Path,
    tag_prefix: __.Absential[ str ] = __.absent,
    simulate: bool = False,
) -> tuple[ int, int ]:
    ''' Populates instruction files from configured Git sources.

        For each source configuration, resolves the Git source, filters
        files by configured patterns, applies preprocessing (such as
        header stripping), and writes results to the target directory.

        Returns tuple of (files_attempted, files_written) across all
        sources.
    '''
    files_attempted = 0
    files_written = 0
    for source_config in sources_configuration:
        try: source_spec = source_config[ 'source' ]
        except KeyError as exception:
            raise _exceptions.InstructionSourceFieldAbsence( ) from exception
        files_config = source_config.get( 'files', { '*.rst': { } } )
        if not isinstance( files_config, __.cabc.Mapping ):
            raise _exceptions.InstructionFilesConfigurationInvalidity( )
        files_mapping: __.cabc.Mapping[
            str, FilePreprocessingConfiguration ] = (
            __.typx.cast(
                __.cabc.Mapping[ str, FilePreprocessingConfiguration ],
                files_config ) )
        _scribe.info( f"Resolving instruction source: {source_spec}" )
        try:
            source_location = _sources.resolve_source_location(
                source_spec, tag_prefix )
        except Exception as exception:
            _scribe.warning(
                f"Failed to resolve instruction source '{source_spec}': "
                f"{exception}" )
            continue
        attempted, written = _populate_instructions_from_location(
            source_location, target, files_mapping, simulate )
        files_attempted += attempted
        files_written += written
    return ( files_attempted, files_written )


def _populate_instructions_from_location(
    source_location: __.Path,
    target: __.Path,
    files_configuration: __.cabc.Mapping[
        str, FilePreprocessingConfiguration ],
    simulate: bool,
) -> tuple[ int, int ]:
    ''' Populates instructions from resolved source location.

        Filters files by configured patterns, applies preprocessing, and
        writes to target directory. Returns tuple of (attempted, written).
    '''
    files_attempted = 0
    files_written = 0
    if not source_location.exists( ):
        _scribe.warning(
            f"Instruction source location does not exist: {source_location}" )
        return ( files_attempted, files_written )
    for pattern, preprocessing_config in files_configuration.items( ):
        config: FilePreprocessingConfiguration = (
            preprocessing_config
            if isinstance( preprocessing_config, __.cabc.Mapping )
            else { } )
        for file_path in source_location.rglob( pattern ):
            if not file_path.is_file( ): continue
            files_attempted += 1
            was_written = _process_and_write_instruction_file(
                file_path, target, config, simulate )
            if was_written: files_written += 1
    return ( files_attempted, files_written )


def _process_and_write_instruction_file(
    source_file: __.Path,
    target_directory: __.Path,
    preprocessing_configuration: FilePreprocessingConfiguration,
    simulate: bool,
) -> bool:
    ''' Processes and writes instruction file to target directory.

        Reads source file, applies configured preprocessing (such as
        header stripping), and writes to target directory. Returns True
        if file was written, False otherwise.
    '''
    try: content = source_file.read_text( encoding = 'utf-8' )
    except ( OSError, IOError ) as exception:
        _scribe.warning(
            f"Failed to read instruction file '{source_file}': {exception}" )
        return False
    processed_content = _preprocess_content(
        content, preprocessing_configuration )
    target_file = target_directory / source_file.name
    if simulate:
        try: relative_path = target_file.relative_to( __.Path.cwd( ) )
        except ValueError: relative_path = target_file
        _scribe.info( f"Would write instruction file: {relative_path}" )
        return True
    try:
        target_directory.mkdir( parents = True, exist_ok = True )
        target_file.write_text( processed_content, encoding = 'utf-8' )
    except ( OSError, IOError ) as exception:
        _scribe.warning(
            f"Failed to write instruction file '{target_file}': {exception}" )
        return False
    else:
        try: relative_path = target_file.relative_to( __.Path.cwd( ) )
        except ValueError: relative_path = target_file
        _scribe.debug( f"Wrote instruction file: {relative_path}" )
        return True


def _preprocess_content(
    content: str,
    configuration: FilePreprocessingConfiguration,
) -> str:
    ''' Applies configured preprocessing transforms to content.

        Supports header stripping via strip_header_lines configuration.
        Additional preprocessing operations can be added here.
    '''
    if not configuration: return content
    strip_lines = configuration.get( 'strip_header_lines' )
    if strip_lines is None: return content
    if not isinstance( strip_lines, int ):
        _scribe.warning(
            f"Invalid strip_header_lines value (expected int): {strip_lines}" )
        return content
    if strip_lines <= 0: return content
    lines = content.splitlines( keepends = True )
    if len( lines ) <= strip_lines: return ''
    return ''.join( lines[ strip_lines: ] )
