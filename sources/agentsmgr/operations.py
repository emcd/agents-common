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


''' Core operations for content generation and directory population.

    This module provides functions for orchestrating content generation,
    including directory population and file writing operations with
    simulation support.
'''


from . import __
from . import exceptions as _exceptions
from . import generator as _generator


def populate_directory(
    generator: _generator.ContentGenerator,
    target: __.Path,
    simulate: bool = False
) -> tuple[ int, int ]:
    ''' Generates all content items to target directory.

        Orchestrates content generation for all coders and item types
        configured in generator. Returns tuple of (items_attempted,
        items_written).
    '''
    items_attempted = 0
    items_written = 0
    for coder_name in generator.configuration[ 'coders' ]:
        for item_type in ( 'commands', 'agents' ):
            attempted, written = generate_coder_item_type(
                generator, coder_name, item_type, target, simulate )
            items_attempted += attempted
            items_written += written
    return ( items_attempted, items_written )


def _content_exists(
    generator: _generator.ContentGenerator,
    item_type: str,
    item_name: str,
    coder: str
) -> bool:
    ''' Checks if content file exists without loading it.

        Uses path resolution from ContentGenerator to check both primary
        and fallback locations. Returns True if content is available.
    '''
    primary_path, fallback_path = generator.resolve_content_paths(
        item_type, item_name, coder )
    if primary_path.exists( ):
        return True
    return bool( fallback_path and fallback_path.exists( ) )


def generate_coder_item_type(
    generator: _generator.ContentGenerator,
    coder: str,
    item_type: str,
    target: __.Path,
    simulate: bool
) -> tuple[ int, int ]:
    ''' Generates items of specific type for a coder.

        Generates all items (commands or agents) for specified coder by
        iterating through configuration files. Pre-checks content
        availability and skips items with missing content. Returns tuple
        of (items_attempted, items_written).
    '''
    items_attempted = 0
    items_written = 0
    if generator.mode == 'nowhere':
        return ( items_attempted, items_written )
    configuration_directory = (
        generator.location / 'configurations' / item_type )
    if not configuration_directory.exists( ):
        return ( items_attempted, items_written )
    for configuration_file in configuration_directory.glob( '*.toml' ):
        item_name = configuration_file.stem
        if not _content_exists( generator, item_type, item_name, coder ):
            __.provide_scribe( __name__ ).warning(
                f"Skipping {item_type}/{item_name} for {coder}: "
                "content not found" )
            continue
        items_attempted += 1
        result = generator.render_single_item(
            item_type, item_name, coder, target )
        if save_content( result.content, result.location, simulate ):
            items_written += 1
    return ( items_attempted, items_written )


def save_content(
    content: str, location: __.Path, simulate: bool = False
) -> bool:
    ''' Saves content to location, creating parent directories as needed.

        Writes content to specified location, creating parent directories
        if necessary. In simulation mode, no actual writing occurs.
        Returns True if file was written, False if simulated.
    '''
    if simulate: return False
    try: location.parent.mkdir( parents = True, exist_ok = True )
    except ( OSError, IOError ) as exception:
        raise _exceptions.FileOperationFailure(
            location.parent, "create directory" ) from exception
    try: location.write_text( content, encoding = 'utf-8' )
    except ( OSError, IOError ) as exception:
        raise _exceptions.FileOperationFailure(
            location, "save content" ) from exception
    return True


def update_git_exclude(
    target: __.Path,
    symlinks: __.cabc.Sequence[ str ],
    simulate: bool = False
) -> int:
    ''' Updates .git/info/exclude with symlink names if not already present.

        Adds symlink names to git exclude file to prevent accidental
        commits of generated symlinks. Processes file line-by-line to
        preserve existing content and avoid duplicates.

        Handles GIT_DIR environment variable and git worktrees by
        resolving the actual git directory location and using the common
        git directory for shared resources.

        Returns count of symlink names added to exclude file.
    '''
    if simulate or not symlinks: return 0
    git_dir = _resolve_git_directory( target )
    if not git_dir: return 0
    exclude_file = git_dir / 'info' / 'exclude'
    if not exclude_file.exists( ): return 0
    try: content = exclude_file.read_text( encoding = 'utf-8' )
    except ( OSError, IOError ) as exception:
        raise _exceptions.FileOperationFailure(
            exclude_file, "read git exclude file" ) from exception
    existing_lines = content.splitlines( )
    existing_patterns = frozenset( existing_lines )
    additions = [
        symlink for symlink in symlinks
        if symlink not in existing_patterns
    ]
    if not additions: return 0
    new_content_lines = existing_lines.copy( )
    if new_content_lines and not new_content_lines[ -1 ].strip( ):
        new_content_lines.extend( additions )
    else:
        new_content_lines.append( '' )
        new_content_lines.extend( additions )
    new_content = '\n'.join( new_content_lines )
    if not new_content.endswith( '\n' ): new_content += '\n'
    try: exclude_file.write_text( new_content, encoding = 'utf-8' )
    except ( OSError, IOError ) as exception:
        raise _exceptions.FileOperationFailure(
            exclude_file, "update git exclude file" ) from exception
    return len( additions )


def _resolve_git_directory(
    start_path: __.Path
) -> __.typx.Optional[ __.Path ]:
    ''' Resolves git directory location, handling GIT_DIR and worktrees.

        Checks GIT_DIR environment variable first, then uses Dulwich to
        discover repository. Returns common git directory (shared across
        worktrees) for access to shared resources like info/exclude.

        Returns None if not in a git repository or on error.
    '''
    from dulwich.repo import Repo
    git_dir_env = __.os.environ.get( 'GIT_DIR' )
    if git_dir_env:
        git_dir_path = __.Path( git_dir_env )
        if git_dir_path.exists( ) and git_dir_path.is_dir( ):
            return _discover_common_git_directory( git_dir_path )
    try: repo = Repo.discover( str( start_path ) )
    except Exception: return None
    git_dir_path = __.Path( repo.controldir( ) )
    return _discover_common_git_directory( git_dir_path )


def _discover_common_git_directory( git_dir: __.Path ) -> __.Path:
    ''' Discovers common git directory, handling worktree commondir.

        For worktrees, reads commondir file to find shared resources.
        For standard repos, returns git_dir unchanged.
    '''
    commondir_file = git_dir / 'commondir'
    if not commondir_file.exists( ):
        return git_dir
    try: common_path = commondir_file.read_text( encoding = 'utf-8' ).strip( )
    except ( OSError, IOError ): return git_dir
    return ( git_dir / common_path ).resolve( )
