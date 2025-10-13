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


''' Memory file symlink management for coder configurations.

    Provides functionality to create symlinks from coder-specific memory
    filenames to shared project conventions file. Follows patterns from
    .auxiliary/scripts/prepare-agents for consistent behavior.
'''


from . import __


_scribe = __.provide_scribe( __name__ )


def create_memory_symlink(
    source: __.Path,
    link_path: __.Path,
    simulate: bool = False,
) -> bool:
    ''' Creates symlink from coder memory file to project conventions.

        Follows patterns from .auxiliary/scripts/prepare-agents:
        - If link is symlink to correct target: Skip silently
        - If link is symlink to wrong target: Update it
        - If link is broken symlink: Remove and recreate
        - If link is regular file/directory: Warn and skip
        - If link doesn't exist: Create symlink

        Returns True if symlink created/updated, False if skipped.
    '''
    try:
        relative_source = __.os.path.relpath(
            source, start = link_path.parent )
    except ValueError:
        relative_source = str( source.resolve( ) )
    if link_path.is_symlink( ):
        try: current_target = __.os.readlink( link_path )
        except OSError as exception:
            _scribe.warning(
                f"Cannot read symlink {link_path}: {exception}." )
            return False
        if current_target == relative_source:
            return False
        _scribe.info(
            f"Updating symlink {link_path.name}: "
            f"{current_target} → {relative_source}" )
        if not simulate: link_path.unlink( )
    elif link_path.exists( ):
        _scribe.warning(
            f"File or directory already exists at {link_path}. Skipping." )
        return False
    elif not link_path.exists( ) and link_path.is_symlink( ):
        _scribe.info( f"Fixing broken symlink: {link_path.name}" )
        if not simulate: link_path.unlink( )
    if not simulate:
        link_path.symlink_to( relative_source )
        _scribe.info( f"Created memory symlink: {link_path.name}" )
    else:
        _scribe.info(
            f"[SIMULATE] Would create symlink: "
            f"{link_path.name} → {relative_source}" )
    return True


def create_memory_symlinks_for_coders(
    coders: __.cabc.Sequence[ str ],
    target: __.Path,
    renderers: __.cabc.Mapping[ str, __.typx.Any ],
    simulate: bool = False,
) -> tuple[ int, int ]:
    ''' Creates memory symlinks for all configured coders.

        Memory symlinks are always created at project root, pointing to
        project-specific conventions file. They are created regardless
        of targeting mode since memory files are project-specific.

        Returns tuple of (attempted, created) counts.
    '''
    source = target / '.auxiliary' / 'configuration' / 'conventions.md'
    if not source.exists( ):
        raise __.MemoryFileAbsence( source )
    attempted = 0
    created = 0
    for coder_name in coders:
        try: renderer = renderers[ coder_name ]
        except KeyError as exception:
            raise __.CoderAbsence( coder_name ) from exception
        link_path = target / renderer.memory_filename
        attempted += 1
        if create_memory_symlink( source, link_path, simulate ):
            created += 1
    return ( attempted, created )
