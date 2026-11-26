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


''' Distribution-to-target copy operations. '''


from .. import __
from .. import operations as _operations
from .. import renderers as _renderers
from .. import resolver as _resolver
from .configurations import (
    _coders_include,
    _format_exclude_path,
    _within_project_root,
)
from .linking import _canonical_skills_directory, _link_skills_discovery

_scribe = __.provide_scribe( __name__ )


def _copy_instructions_from_distribution(
    distribution: __.Path,
    target: __.Path,
    instructions_target: str,
    simulate: bool,
) -> tuple[ int, int, tuple[ str, ... ] ]:
    ''' Copies instruction files from distribution/ to target.

        Reads from distribution/per-project/general/instructions/ and
        copies to the configured instructions target path.
        Returns tuple of (files_attempted, files_written, exclude_entries).
    '''
    import contextlib as _contextlib
    source_dir = distribution / 'per-project' / 'general' / 'instructions'
    if not source_dir.exists( ):
        return ( 0, 0, ( ) )
    target_dir = target / instructions_target
    files_attempted = 0
    files_written = 0
    exclude_entries: list[ str ] = [ ]
    for source_file in source_dir.glob( '*' ):
        if not source_file.is_file( ): continue
        files_attempted += 1
        dest_path = target_dir / source_file.name
        if _operations.save_content_text(
            source_file.read_text( encoding = 'utf-8' ),
            dest_path,
            simulate,
        ):
            files_written += 1
        with _contextlib.suppress( ValueError ):
            exclude_entries.append(
                _format_exclude_path( dest_path.relative_to( target ) ) )
    return ( files_attempted, files_written, tuple( exclude_entries ) )


#: Populate-managed support scripts (stable exact paths, relative to
#: ``.auxiliary/agents/scripts/``). The git-exclude entries for these
#: paths are retained unconditionally: the managed exclude block is
#: rebuilt on every run, and dropping an entry on deselect would
#: un-ignore a stale file. Deselected shims are removed by hand per the
#: namespace note, never by guessed ownership.


#: Populate-managed support scripts (stable exact paths, relative to
#: ``.auxiliary/agents/scripts/``). The git-exclude entries for these
#: paths are retained unconditionally: the managed exclude block is
#: rebuilt on every run, and dropping an entry on deselect would
#: un-ignore a stale file. Deselected shims are removed by hand per the
#: namespace note, never by guessed ownership.
SUPPORT_SCRIPTS: tuple[ str, ... ] = ( 'mcp-discover-shim.py', )


def _support_script_excludes(
    target: __.Path,
) -> tuple[ str, ... ]:
    ''' Lists stable git-exclude entries for support scripts.

        Entries are exact paths, independent of distribution contents
        or coder selection, so a deselected or upstream-removed shim
        stays ignored instead of surfacing as untracked.
    '''
    return tuple(
        _format_exclude_path(
            ( target / '.auxiliary' / 'agents' / 'scripts' / name
             ).relative_to( target ) )
        for name in SUPPORT_SCRIPTS )


def _copy_support_scripts_from_distribution(
    distribution: __.Path,
    target: __.Path,
    coders: __.cabc.Sequence[ __.typx.Any ],
    simulate: bool,
) -> tuple[ int, int, tuple[ str, ... ] ]:
    ''' Copies populate-managed support scripts from distribution/.

        Copies each ``SUPPORT_SCRIPTS`` entry present under
        distribution/per-project/general/scripts/ to
        ``.auxiliary/agents/scripts/`` when the ``antigravity`` coder is
        selected (a missing source for a selected coder warns loudly,
        since the rendered MCP config references it). All support
        scripts are populate-managed and git-excluded (temporary compat
        content is never staged).

        Exclude entries are stable exact paths, retained even when
        ``antigravity`` is not selected or the distribution no longer
        carries the file: the managed git-exclude block is rebuilt on
        every run, and dropping an entry would un-ignore a stale file.
        Deselected shims are removed by hand (see the namespace note),
        never by guessed ownership. Writes never follow symlinks and
        never escape the target tree.
        Returns tuple of (files_attempted, files_written, exclude_entries).
    '''
    exclude_entries = _support_script_excludes( target )
    if not _coders_include( coders, 'antigravity' ):
        return ( 0, 0, exclude_entries )
    source_dir = distribution / 'per-project' / 'general' / 'scripts'
    target_dir = target / '.auxiliary' / 'agents' / 'scripts'
    if not _within_project_root( target_dir, target ):
        _scribe.warning(
            f"Support scripts directory {target_dir} escapes the "
            "project root through a symlink; refusing to write. Remove "
            "or relocate it to enable support script installation." )
        return ( 0, 0, exclude_entries )
    files_attempted = 0
    files_written = 0
    for name in SUPPORT_SCRIPTS:
        source_file = source_dir / name
        if not source_file.is_file( ):
            _scribe.warning(
                f"Support script {name} selected but missing from "
                "distribution; the rendered MCP config references it." )
            continue
        dest_path = target_dir / name
        if dest_path.is_symlink( ):
            _scribe.warning(
                f"Support script path {dest_path} is a symlink; "
                "not following it. Remove or relocate it to enable "
                "support script installation." )
            continue
        if not _within_project_root( dest_path.parent, target ):
            _scribe.warning(
                f"Support script path {dest_path} escapes the project "
                "root through a symlink; refusing to write." )
            continue
        files_attempted += 1
        if _operations.save_content_bytes(
            source_file.read_bytes( ),
            dest_path,
            simulate,
        ):
            files_written += 1
            if not simulate:
                __.shutil.copymode( source_file, dest_path )
    return ( files_attempted, files_written, exclude_entries )


def _copy_distribution_items(  # noqa: PLR0913
    distribution: __.Path,
    coders: __.cabc.Sequence[ str ],
    target: __.Path,
    *,
    configuration: __.cabc.Mapping[ str, __.typx.Any ],
    mode: _renderers.ExplicitTargetMode,
    simulate: bool,
) -> tuple[ int, int, tuple[ str, ... ] ]:
    ''' Copies distribution items to downstream target paths.

        For each coder, copies the entire
        distribution/<mode>/coders/<coder>/ tree to the target.
        In per-project mode, skills materialize once under
        ``.auxiliary/agents/skills/`` with discovery symlinks.

        The distribution tree mirrors downstream layout, so this is
        a single copy operation per coder.

        Returns tuple of (items_attempted, items_written, exclude_entries).
    '''
    items_attempted = 0
    items_written = 0
    exclude_entries: list[ str ] = [ ]
    for coder_name, manager in _resolver.resolve_coders(
        coders, mode = mode
    ):
        base_directory = manager.resolve_base_directory(
            mode = mode,
            target = target,
            configuration = configuration,
            environment = __.os.environ,
        )
        coder_source = distribution / mode / 'coders' / coder_name
        # Copy entire coder tree (commands, agents, resources).
        if coder_source.exists( ):
            attempted, written, entries = _copy_tree(
                coder_source, base_directory, target, simulate )
            items_attempted += attempted
            items_written += written
            exclude_entries.extend( entries )
    if mode == 'per-project':
        attempted, written, entries = _copy_skills(
            distribution, target, coders, configuration, simulate )
        items_attempted += attempted
        items_written += written
        exclude_entries.extend( entries )
    return ( items_attempted, items_written, tuple( exclude_entries ) )


def _copy_tree(
    source: __.Path,
    target: __.Path,
    project_root: __.Path,
    simulate: bool,
) -> tuple[ int, int, tuple[ str, ... ] ]:
    ''' Copies directory tree from source to target.

        Recursively copies all files and subdirectories (binary-safe) and
        preserves each source file mode (including executable bits).
        Returns tuple of (files_attempted, files_written, exclude_entries).
    '''
    import contextlib as _contextlib
    files_attempted = 0
    files_written = 0
    exclude_entries: list[ str ] = [ ]
    for source_file in source.rglob( '*' ):
        if not source_file.is_file( ): continue
        files_attempted += 1
        relative = source_file.relative_to( source )
        dest_path = target / relative
        if _operations.save_content_bytes(
            source_file.read_bytes( ),
            dest_path,
            simulate,
        ):
            files_written += 1
            __.shutil.copymode( source_file, dest_path )
        with _contextlib.suppress( ValueError ):
            exclude_entries.append(
                _format_exclude_path(
                    dest_path.relative_to( project_root ) ) )
    return ( files_attempted, files_written, tuple( exclude_entries ) )


def _copy_skills(
    distribution: __.Path,
    project_root: __.Path,
    coders: __.cabc.Sequence[ str ],
    configuration: __.cabc.Mapping[ str, __.typx.Any ],
    simulate: bool,
) -> tuple[ int, int, tuple[ str, ... ] ]:
    ''' Materializes skill packages once and links harness discovery paths.

        Skills are static artifacts that require no rendering. Layout follows
        the Agent Skills specification
        (https://agentskills.io/specification.md). Source layout under
        ``distribution/per-project/general/skills/`` may be either:

        - Directory package (Agent Skills): ``<name>/SKILL.md`` plus optional
          ``scripts/``, ``references/``, ``assets/``, and other supporting
          files — the entire directory is copied to
          ``.auxiliary/agents/skills/<name>/``.
        - Legacy flat file: ``<name>.md`` →
          ``.auxiliary/agents/skills/<name>/SKILL.md``.

        When both a directory package and a flat ``<name>.md`` exist for the
        same name, the directory package wins. Supporting files are not
        language-filtered; a skill is a portable package. After materializing
        the canonical tree, creates discovery symlinks (``.agents`` and
        per-coder ``skills/``). Returns tuple of
        (files_attempted, files_written, exclude_entries).
    '''
    import contextlib as _contextlib
    items_attempted = 0
    items_written = 0
    exclude_entries: list[ str ] = [ ]
    skills_dir = (
        distribution / 'per-project' / 'general' / 'skills' )
    canonical = _canonical_skills_directory( project_root )
    if skills_dir.exists( ):
        directory_skills: dict[ str, __.Path ] = { }
        flat_skills: dict[ str, __.Path ] = { }
        for entry in skills_dir.iterdir( ):
            if entry.is_dir( ) and ( entry / 'SKILL.md' ).is_file( ):
                directory_skills[ entry.name ] = entry
            elif entry.is_file( ) and entry.suffix == '.md':
                flat_skills[ entry.stem ] = entry
        for item_name, source_dir in sorted( directory_skills.items( ) ):
            dest_root = canonical / item_name
            attempted, written, entries = _copy_tree(
                source_dir, dest_root, project_root, simulate )
            items_attempted += attempted
            items_written += written
            exclude_entries.extend( entries )
        for item_name, skill_file in sorted( flat_skills.items( ) ):
            if item_name in directory_skills: continue
            items_attempted += 1
            dest_path = canonical / item_name / 'SKILL.md'
            if _operations.save_content_bytes(
                skill_file.read_bytes( ),
                dest_path,
                simulate,
            ):
                items_written += 1
                __.shutil.copymode( skill_file, dest_path )
            with _contextlib.suppress( ValueError ):
                exclude_entries.append(
                    _format_exclude_path(
                        dest_path.relative_to( project_root ) ) )
    exclude_entries.extend(
        _link_skills_discovery(
            project_root, coders, configuration, simulate ) )
    return ( items_attempted, items_written, tuple( exclude_entries ) )
