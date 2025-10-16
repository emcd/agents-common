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


''' Global settings management for coder configurations.

    Provides functionality for populating per-user global settings files,
    including direct file copying and JSON settings merging with user
    preservation semantics.
'''


import json as _json

from . import __
from . import exceptions as _exceptions
from . import renderers as _renderers


def _is_json_dict(
    value: __.typx.Any
) -> __.typx.TypeGuard[ dict[ str, __.typx.Any ] ]:
    ''' Type guard for JSON dictionary values. '''
    return isinstance( value, dict )


def populate_globals(
    data_location: __.Path,
    coders: __.cabc.Sequence[ str ],
    application_configuration: __.cabc.Mapping[ str, __.typx.Any ],
    simulate: bool = False,
) -> tuple[ int, int ]:
    ''' Populates per-user global files for configured coders.

        Surveys defaults/globals directory for coder-specific files and
        populates them to per-user locations. Handles two types of files:
        direct copy for non-settings files and merge for settings files
        (preserving user values).

        Returns tuple of (files_attempted, files_updated) counts.
    '''
    globals_directory = data_location / 'globals'
    if not globals_directory.exists( ):
        return ( 0, 0 )
    files_attempted = 0
    files_updated = 0
    for coder in coders:
        coder_globals = globals_directory / coder
        if not coder_globals.exists( ):
            continue
        try: renderer = _renderers.RENDERERS[ coder ]
        except KeyError as exception:
            raise _exceptions.CoderAbsence( coder ) from exception
        per_user_directory = renderer.resolve_base_directory(
            mode = 'per-user',
            target = __.Path.cwd( ),
            configuration = application_configuration,
            environment = __.os.environ,
        )
        for global_file in coder_globals.iterdir( ):
            if not global_file.is_file( ):
                continue
            files_attempted += 1
            target_file = per_user_directory / global_file.name
            if _is_settings_file( global_file, coder ):
                updated = _merge_settings_file(
                    global_file, target_file, simulate )
            else:
                updated = _copy_file_directly(
                    global_file, target_file, simulate )
            if updated:
                files_updated += 1
    return ( files_attempted, files_updated )


def _is_settings_file( file: __.Path, coder: str ) -> bool:
    ''' Determines whether file is a settings file requiring merge logic.

        Settings files have coder-specific names and contain JSON
        configuration that should be merged rather than replaced. Non-settings
        files are directly copied, replacing any existing version.
    '''
    settings_names: dict[ str, tuple[ str, ... ] ] = {
        'claude': ( 'settings.json', ),
        'opencode': ( 'opencode.json', 'opencode.jsonc' ),
        'codex': ( 'config.json', ),
    }
    return file.name in settings_names.get( coder, ( ) )


def _copy_file_directly(
    source: __.Path, target: __.Path, simulate: bool
) -> bool:
    ''' Copies file directly from source to target location.

        Creates target directory if needed. Returns True if file was
        updated (or would be updated in simulation mode).
    '''
    if simulate:
        return True
    target.parent.mkdir( parents = True, exist_ok = True )
    try: __.shutil.copy2( source, target )
    except ( OSError, IOError ) as exception:
        raise _exceptions.GlobalsPopulationFailure(
            source, target
        ) from exception
    return True


def _merge_settings_file(
    source: __.Path, target: __.Path, simulate: bool
) -> bool:
    ''' Merges JSON settings file preserving user values.

        Loads both source template and target user settings, performs deep
        merge adding missing keys from template while preserving all user
        values. Creates backup before writing merged result. Returns True
        if file was updated (or would be updated in simulation mode).
    '''
    template = _load_json_file( source, target )
    user_settings: dict[ str, __.typx.Any ] = (
        _load_json_file( target, target ) if target.exists( )
        else { } )
    merged = _deep_merge_settings( user_settings, template )
    if simulate:
        return True
    _write_merged_settings( target, merged )
    return True


def _load_json_file(
    filepath: __.Path, target_context: __.Path
) -> dict[ str, __.typx.Any ]:
    ''' Loads JSON file with error handling.

        Raises GlobalsPopulationFailure with source context on any error.
    '''
    try: content = filepath.read_text( encoding = 'utf-8' )
    except ( OSError, IOError ) as exception:
        raise _exceptions.GlobalsPopulationFailure(
            filepath, target_context ) from exception
    try:
        loaded: __.typx.Any = _json.loads( content )
    except ValueError as exception:
        raise _exceptions.GlobalsPopulationFailure(
            filepath, target_context ) from exception
    if not _is_json_dict( loaded ):
        raise _exceptions.GlobalsPopulationFailure( filepath, target_context )
    return loaded


def _write_merged_settings(
    target: __.Path, merged: dict[ str, __.typx.Any ]
) -> None:
    ''' Writes merged settings with backup of existing file.

        Creates target directory if needed. Backs up existing file before
        writing merged result.
    '''
    target.parent.mkdir( parents = True, exist_ok = True )
    if target.exists( ):
        backup_path = target.with_suffix( '.json.backup' )
        try: __.shutil.copy2( target, backup_path )
        except ( OSError, IOError ) as exception:
            raise _exceptions.GlobalsPopulationFailure(
                target, target ) from exception
    try:
        target.write_text(
            _json.dumps( merged, indent = 2 ), encoding = 'utf-8' )
    except ( OSError, IOError ) as exception:
        raise _exceptions.GlobalsPopulationFailure(
            target, target
        ) from exception


def _deep_merge_settings(
    target: dict[ str, __.typx.Any ], source: dict[ str, __.typx.Any ]
) -> dict[ str, __.typx.Any ]:
    ''' Recursively merges source into target preserving target values.

        Implements additive merge: adds keys from source that are missing
        in target. When both contain same key with dict values, recursively
        merges nested dicts. For conflicting scalar values, target value
        wins (user preferences preserved).
    '''
    result = target.copy( )
    for key, source_value in source.items( ):
        if key not in result:
            result[ key ] = source_value
        elif (
            _is_json_dict( result[ key ] )
            and _is_json_dict( source_value )
        ):
            result[ key ] = _deep_merge_settings(
                result[ key ], source_value )
    return result
