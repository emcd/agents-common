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
    simulation support. Also provides generation from components/ to
    distribution/ with staleness checking.
'''


import difflib as _difflib

from . import __
from . import exceptions as _exceptions
from . import generator as _generator
from . import renderers as _renderers


_MANAGED_BLOCK_BEGIN = '# BEGIN: Managed by agentsmgr (emcd-agents)'
_MANAGED_BLOCK_WARNING = '# Do not manually edit entries in this block.'
_MANAGED_BLOCK_END = '# END: Managed by agentsmgr (emcd-agents)'
_EXTENSION_PARTS_MINIMUM = 2


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
    _ensure_output_directories( generator, target, simulate )
    for coder_name in generator.configuration[ 'coders' ]:
        try: renderer = _renderers.RENDERERS[ coder_name ]
        except KeyError: continue
        for item_type in renderer.item_types_available:
            attempted, written = generate_coder_item_type(
                generator, coder_name, item_type, target, simulate )
            items_attempted += attempted
            items_written += written
    return ( items_attempted, items_written )

def _ensure_output_directories(
    generator: _generator.ContentGenerator,
    target: __.Path,
    simulate: bool,
) -> None:
    if simulate or generator.mode == 'nowhere': return
    for coder_name in generator.configuration[ 'coders' ]:
        try: renderer = _renderers.RENDERERS[ coder_name ]
        except KeyError: continue
        if generator.mode == 'default': actual_mode = renderer.mode_default
        else: actual_mode = generator.mode
        if actual_mode not in ( 'per-user', 'per-project' ): continue
        if actual_mode not in renderer.modes_available: continue
        base_directory = renderer.resolve_base_directory(
            mode = actual_mode,
            target = target,
            configuration = generator.application_configuration,
            environment = __.os.environ,
        )
        for item_type in renderer.item_types_available:
            dirname = renderer.produce_output_structure( item_type )
            ( base_directory / dirname ).mkdir(
                parents = True, exist_ok = True )


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
        iterating through configuration files. Skills are direct
        distribution artifacts and are not generated from components.
        Pre-checks content availability and skips items with missing
        content. Returns tuple of (items_attempted, items_written).
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
        (
            "/{0}".format( entry.strip( ) )
            if entry.strip( ) and not entry.strip( ).startswith( '/' )
            else entry.strip( )
        )
        for entry in entries if entry.strip( )
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


def generate_distribution(
    generator: _generator.ContentGenerator,
    distribution: __.Path,
    simulate: bool = False,
) -> tuple[ int, int ]:
    ''' Generates pre-rendered artifacts from components/ to distribution/.

        Reads from the 3-tier pipeline source (configurations, templates,
        per-coder contents) and writes rendered commands and agents to
        distribution/. Skills are not generated; they are direct
        distribution artifacts.

        Returns tuple of (items_attempted, items_written).
    '''
    items_attempted = 0
    items_written = 0
    for coder_name in generator.configuration[ 'coders' ]:
        try: renderer = _renderers.RENDERERS[ coder_name ]
        except KeyError: continue
        for item_type in renderer.item_types_available:
            if item_type == 'skills':
                continue  # Skills are direct distribution artifacts.
            attempted, written = _generate_for_distribution(
                generator, coder_name, item_type, distribution, simulate )
            items_attempted += attempted
            items_written += written
    return ( items_attempted, items_written )


def _generate_for_distribution(
    generator: _generator.ContentGenerator,
    coder: str,
    item_type: str,
    distribution: __.Path,
    simulate: bool,
) -> tuple[ int, int ]:
    ''' Generates items of a type for a coder into distribution/.

        Reads configuration and content from components/, renders through
        the 3-tier pipeline, and writes to
        distribution/per-project/coders/<coder>/<item_type>/.
        Returns tuple of (items_attempted, items_written).
    '''
    items_attempted = 0
    items_written = 0
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
            item_type, item_name, coder, distribution )
        renderer = _renderers.RENDERERS[ coder ]
        dirname = renderer.produce_output_structure( item_type )
        output_path = (
            distribution / 'per-project' / 'coders' / coder / dirname /
            f"{item_name}.{_parse_output_extension( result.location )}" )
        if save_content( result.content, output_path, simulate ):
            items_written += 1
    return ( items_attempted, items_written )


def _parse_output_extension( location: __.Path ) -> str:
    ''' Extracts output extension from rendered location path.

        Skips the last suffix (which is the item name suffix) and returns
        the meaningful extension. For SKILL.md returns "md".
    '''
    name = location.name
    if name == 'SKILL.md': return 'md'
    parts = name.split( '.' )
    if len( parts ) >= _EXTENSION_PARTS_MINIMUM: return parts[ -1 ]
    return 'md'


def check_distribution_staleness(
    generator: _generator.ContentGenerator,
    distribution: __.Path,
) -> tuple[ int, list[ str ] ]:
    ''' Checks for staleness between components/ and distribution/.

        Regenerates from components/ and compares against existing
        distribution/ files. Also detects orphaned artifacts that exist
        in distribution/ but are no longer generated from components/.
        Returns tuple of (items_checked, diff_lines).
        Empty diff_lines means distribution is current.
    '''
    items_checked = 0
    all_diffs: list[ str ] = [ ]
    expected_paths: set[ __.Path ] = set( )
    for coder_name in generator.configuration[ 'coders' ]:
        try: renderer = _renderers.RENDERERS[ coder_name ]
        except KeyError: continue
        for item_type in renderer.item_types_available:
            if item_type == 'skills':
                continue
            checked, diffs, paths = _check_staleness_for_type(
                generator, coder_name, item_type, distribution )
            items_checked += checked
            all_diffs.extend( diffs )
            expected_paths.update( paths )
    # Detect orphaned artifacts in generated directories
    orphans = _detect_orphaned_artifacts(
        distribution, generator.configuration[ 'coders' ], expected_paths )
    all_diffs.extend( orphans )
    return ( items_checked, all_diffs )


def _check_staleness_for_type(
    generator: _generator.ContentGenerator,
    coder: str,
    item_type: str,
    distribution: __.Path,
) -> tuple[ int, list[ str ], set[ __.Path ] ]:
    ''' Checks staleness for items of a specific type.

        Renders from components/ and compares against distribution/.
        Returns tuple of (items_checked, diff_lines, expected_paths).
    '''
    items_checked = 0
    diffs: list[ str ] = [ ]
    expected_paths: set[ __.Path ] = set( )
    configuration_directory = (
        generator.location / 'configurations' / item_type )
    if not configuration_directory.exists( ):
        return ( items_checked, diffs, expected_paths )
    for configuration_file in configuration_directory.glob( '*.toml' ):
        item_name = configuration_file.stem
        if not _content_exists( generator, item_type, item_name, coder ):
            continue
        items_checked += 1
        result = generator.render_single_item(
            item_type, item_name, coder, distribution )
        renderer = _renderers.RENDERERS[ coder ]
        dirname = renderer.produce_output_structure( item_type )
        output_path = (
            distribution / 'per-project' / 'coders' / coder / dirname /
            f"{item_name}.{_parse_output_extension( result.location )}" )
        expected_paths.add( output_path )
        if not output_path.exists( ):
            diffs.append(
                f"+ {item_type}/{item_name}: "
                f"missing from distribution" )
            continue
        existing_content = output_path.read_text( encoding = 'utf-8' )
        if result.content != existing_content:
            diff_lines = list( _difflib.unified_diff(
                existing_content.splitlines( ),
                result.content.splitlines( ),
                fromfile = f"distribution/{item_type}/{output_path.name}",
                tofile = f"components/{item_type}/{item_name}",
                lineterm = '' ) )
            diffs.extend( diff_lines )
    return ( items_checked, diffs, expected_paths )


def _detect_orphaned_artifacts(
    distribution: __.Path,
    coders: __.cabc.Sequence[ str ],
    expected_paths: set[ __.Path ],
) -> list[ str ]:
    ''' Detects orphaned artifacts in distribution/.

        Scans distribution/per-project/coders/<coder>/ for generated
        item directories (commands, agents, command, agent) and reports
        any files not in the expected_paths set.
    '''
    orphans: list[ str ] = [ ]
    generated_dirs = ( 'commands', 'agents', 'command', 'agent' )
    for coder in coders:
        coder_dir = distribution / 'per-project' / 'coders' / coder
        if not coder_dir.exists( ): continue
        for dirname in generated_dirs:
            item_dir = coder_dir / dirname
            if not item_dir.exists( ): continue
            orphans.extend(
                f"- {coder}/{dirname}/{item_file.name}: orphaned artifact"
                for item_file in item_dir.glob( '*.md' )
                if item_file not in expected_paths
            )
    return orphans
