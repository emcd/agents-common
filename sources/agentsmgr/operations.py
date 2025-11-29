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


_MANAGED_BLOCK_BEGIN = '# BEGIN: Managed by agentsmgr (emcd-agents)'
_MANAGED_BLOCK_WARNING = '# Do not manually edit entries in this block.'
_MANAGED_BLOCK_END = '# END: Managed by agentsmgr (emcd-agents)'


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
    entries: __.cabc.Collection[ str ],
    simulate: bool = False
) -> int:
    ''' Updates .git/info/exclude with managed block of agentsmgr entries.

        Maintains a clearly-marked block of entries managed by agentsmgr,
        with complete replacement on each update. Entries are sorted
        lexicographically within the block. User entries outside the
        managed block are preserved.

        Handles GIT_DIR environment variable and git worktrees by
        resolving the actual git directory location and using the common
        git directory for shared resources.

        Returns count of entries in managed block.
    '''
    if simulate: return 0
    git_dir = _resolve_git_directory( target )
    if not git_dir: return 0
    exclude_file = git_dir / 'info' / 'exclude'
    if not exclude_file.exists( ): return 0
    try: content = exclude_file.read_text( encoding = 'utf-8' )
    except ( OSError, IOError ) as exception:
        raise _exceptions.FileOperationFailure(
            exclude_file, "read git exclude file" ) from exception
    normalized_entries = sorted( {
        entry.strip( ) for entry in entries if entry.strip( )
    } )
    if not normalized_entries:
        new_content = _remove_managed_block( content )
        if new_content == content: return 0
    else:
        new_content = _update_managed_block( content, normalized_entries )
    try: exclude_file.write_text( new_content, encoding = 'utf-8' )
    except ( OSError, IOError ) as exception:
        raise _exceptions.FileOperationFailure(
            exclude_file, "update git exclude file" ) from exception
    return len( normalized_entries )


def _update_managed_block(
    content: str, entries: __.cabc.Sequence[ str ]
) -> str:
    ''' Updates content with new managed block containing sorted entries.

        Locates existing managed block (if present) and replaces it with
        new block. If no block exists, appends to end of file. Preserves
        user content outside the managed block.
    '''
    lines = content.splitlines( )
    before_block, after_block = _partition_around_managed_block( lines )
    block_lines = [ _MANAGED_BLOCK_BEGIN, _MANAGED_BLOCK_WARNING ]
    block_lines.extend( entries )
    block_lines.append( _MANAGED_BLOCK_END )
    if before_block and before_block[ -1 ].strip( ):
        before_block.append( '' )
    result_lines = before_block + block_lines
    if after_block:
        result_lines.append( '' )
        result_lines.extend( after_block )
    return '\n'.join( result_lines ) + '\n'


def _remove_managed_block( content: str ) -> str:
    ''' Removes managed block from content, preserving user entries.

        Locates and removes managed block if present. Returns content
        unchanged if no block found.
    '''
    lines = content.splitlines( )
    before_block, after_block = _partition_around_managed_block( lines )
    if not before_block and not after_block:
        return content
    result_lines = before_block
    if result_lines and after_block:
        if result_lines[ -1 ].strip( ):
            result_lines.append( '' )
        result_lines.extend( after_block )
    elif after_block:
        result_lines = after_block
    if not result_lines: return ''
    return '\n'.join( result_lines ) + '\n'


def _partition_around_managed_block(
    lines: __.cabc.Sequence[ str ]
) -> tuple[ list[ str ], list[ str ] ]:
    ''' Partitions lines into content before and after managed block.

        Locates managed block markers and returns (before, after) tuple.
        If block is malformed or not found, returns (all_lines, []).
        Malformed blocks are treated as non-existent.
    '''
    try: begin_index = lines.index( _MANAGED_BLOCK_BEGIN )
    except ValueError: return ( list( lines ), [ ] )
    try: end_index = lines.index( _MANAGED_BLOCK_END, begin_index )
    except ValueError:
        __.provide_scribe( __name__ ).warning(
            "Malformed agentsmgr block in .git/info/exclude; rebuilding." )
        return ( list( lines ), [ ] )
    if end_index < begin_index:
        __.provide_scribe( __name__ ).warning(
            "Malformed agentsmgr block in .git/info/exclude; rebuilding." )
        return ( list( lines ), [ ] )
    before_block = list( lines[ :begin_index ] )
    while before_block and not before_block[ -1 ].strip( ):
        before_block.pop( )
    after_block = list( lines[ end_index + 1: ] )
    while after_block and not after_block[ 0 ].strip( ):
        after_block.pop( 0 )
    return ( before_block, after_block )

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

def copy_coder_resources(
    source_root: __.Path,
    target_root: __.Path,
    coders: __.cabc.Sequence[ str ],
    simulate: bool = False
) -> tuple[ int, int ]:
    ''' Copies static resources for specified coders.

        Iterates through coders and copies resources from
        source_root/<coder> to target_root/<coder>.
        Returns tuple of (coders_attempted, coders_processed).
    '''
    attempted = 0
    processed = 0
    for coder in coders:
        source = source_root / coder
        target = target_root / coder
        if not source.exists( ):
            __.provide_scribe( __name__ ).debug(
                f"No resources found for {coder} at {source}" )
            continue
        attempted += 1
        if copy_resource_content( source, target, simulate ):
            processed += 1
    return ( attempted, processed )

def copy_resource_content(
    source: __.Path, target: __.Path, simulate: bool
) -> bool:
    ''' Recursively copies directory contents.

        Copies all files and subdirectories from source to target,
        overwriting existing files. Handles directory creation.
    '''
    if simulate: return True
    try:
        target.mkdir( parents = True, exist_ok = True )
    except ( OSError, IOError ) as exception:
        raise _exceptions.CoderResourceCopyFailure(
            source, target
        ) from exception
    try:
        __.shutil.copytree( source, target, dirs_exist_ok = True )
    except ( OSError, IOError ) as exception:
        raise _exceptions.CoderResourceCopyFailure(
            source, target
        ) from exception
    return True
