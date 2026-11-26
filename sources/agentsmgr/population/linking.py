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


''' Symlink and discovery-link management for populated projects. '''


from .. import __
from .. import memorylinks as _memorylinks
from .. import renderers as _renderers
from .. import resolver as _resolver
from .configurations import _format_exclude_path


_scribe = __.provide_scribe( __name__ )


def _create_all_symlinks(
    configuration: __.cabc.Mapping[ str, __.typx.Any ],
    target: __.Path,
    mode: str,
    simulate: bool,
) -> tuple[ str, ... ]:
    ''' Creates all symlinks and returns their names for git exclude.

        Creates memory symlinks for all coders and coder directory
        symlinks for per-project mode. Returns list of all symlink
        names (both newly created and pre-existing) for git exclude
        update.
    '''
    all_symlink_names: list[ str ] = [ ]
    if mode == 'nowhere': return tuple( all_symlink_names )
    links_attempted, links_created, symlink_names_memory = (
        _memorylinks.create_memory_symlinks_for_coders(
            coders = configuration[ 'coders' ],
            target = target,
            simulate = simulate,
        ) )
    all_symlink_names.extend( symlink_names_memory )
    if links_created > 0:
        _scribe.info(
            f"Created {links_created}/{links_attempted} memory symlinks" )
    needs_coder_symlinks = (
        mode == 'per-project'
        or ( mode == 'default' and any(
            coder in _renderers.RENDERERS
            and _renderers.RENDERERS[ coder ].mode_default == 'per-project'
            for coder in configuration[ 'coders' ] ) ) )
    if needs_coder_symlinks:
        (   coder_symlinks_attempted,
            coder_symlinks_created,
            coder_symlink_names ) = (
            _create_coder_directory_symlinks(
                coders = configuration[ 'coders' ],
                target = target,
                simulate = simulate,
            ) )
        all_symlink_names.extend( coder_symlink_names )
        if coder_symlinks_created > 0:
            _scribe.info(
                f"Created {coder_symlinks_created}/"
                f"{coder_symlinks_attempted} coder directory symlinks" )
    openspec_link_path = target / 'openspec'
    openspec_source_path = (
        target / 'documentation' / 'architecture' / 'openspec' )
    if not simulate:
        openspec_source_path.mkdir( parents = True, exist_ok = True )
    _, symlink_name_openspec = _memorylinks.create_memory_symlink(
        openspec_source_path, openspec_link_path, simulate )
    all_symlink_names.append( symlink_name_openspec )
    _scribe.info( "Created 1/1 openspec symlink" )
    return tuple( all_symlink_names )


def _create_coder_directory_symlinks(
    coders: __.cabc.Sequence[ str ],
    target: __.Path,
    simulate: bool = False,
) -> tuple[ int, int, tuple[ str, ... ] ]:
    ''' Creates symlinks from .{coder} to .auxiliary/configuration/coders/.

        For per-project mode, creates symlinks that make coder directories
        accessible at their expected locations (.claude, .opencode, etc.)
        while keeping actual files organized under
        .auxiliary/configuration/coders/.

        Each renderer is responsible for specifying its symlink requirements
        via provide_project_symlinks(). Population logic simply iterates
        coders and asks renderers for their symlinks.

        Only creates symlinks for coders whose default mode is per-project.
        Coders with per-user default mode are skipped since they do not
        use per-project directories.

        Returns tuple of (attempted, created, symlink_names) where
        symlink_names contains names of all symlinks (both newly created
        and pre-existing).
    '''
    attempted = 0
    created = 0
    symlink_names: list[ str ] = [ ]
    for coder_name, renderer in _resolver.resolve_coders(
        coders, mode = 'per-project'
    ):
        for source, link_path in renderer.provide_project_symlinks( target ):
            attempted += 1
            was_created, symlink_name = (
                _memorylinks.create_memory_symlink(
                    source, link_path, simulate ) )
            if was_created: created += 1
            symlink_names.append( symlink_name )
    return ( attempted, created, tuple( symlink_names ) )


def _canonical_skills_directory( project_root: __.Path ) -> __.Path:
    ''' Returns project-canonical skills root under .auxiliary/agents. '''
    return project_root / '.auxiliary' / 'agents' / 'skills'


def _ensure_directory_symlink(
    source: __.Path,
    link_path: __.Path,
    *,
    simulate: bool = False,
    replace_existing: bool = False,
) -> bool:
    ''' Ensures link_path is a symlink to source.

        When replace_existing is true, removes an existing non-symlink
        directory or file at link_path so managed coder skill trees can cut
        over to the canonical package root. When false (default), leaves an
        existing non-symlink path in place and reports a warning — used for
        root ``.agents``, which may belong to another tool. Returns whether
        the symlink was created or updated.
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
        if not replace_existing:
            _scribe.warning(
                f"Path already exists at {link_path}; "
                "not replacing with symlink. Remove or relocate it to "
                "enable agentsmgr skills discovery linking." )
            return False
        _scribe.info(
            f"Replacing existing path with symlink: {link_path}" )
        if not simulate:
            if link_path.is_dir( ): __.shutil.rmtree( link_path )
            else: link_path.unlink( )
    if not simulate:
        link_path.parent.mkdir( parents = True, exist_ok = True )
        link_path.symlink_to( relative_source )
        _scribe.info( f"Created directory symlink: {link_path.name}" )
    else:
        _scribe.info(
            f"[SIMULATE] Would create symlink: "
            f"{link_path} → {relative_source}" )
    return True


def _link_skills_discovery(
    project_root: __.Path,
    coders: __.cabc.Sequence[ str ],
    configuration: __.cabc.Mapping[ str, __.typx.Any ],
    simulate: bool,
) -> tuple[ str, ... ]:
    ''' Links harness discovery paths to the canonical skills tree.

        - Root ``.agents`` → ``.auxiliary/agents`` so ``.agents/skills``
          resolves; never deletes a pre-existing non-symlink ``.agents`` path
        - Per-coder ``<base>/skills`` → canonical skills directory
          (destructive cutover of legacy dual-copy skill trees only)
    '''
    import contextlib as _contextlib
    exclude_entries: list[ str ] = [ ]
    agents_source = project_root / '.auxiliary' / 'agents'
    agents_link = project_root / '.agents'
    if not simulate:
        agents_source.mkdir( parents = True, exist_ok = True )
    if _ensure_directory_symlink(
        agents_source, agents_link,
        simulate = simulate, replace_existing = False,
    ) or agents_link.is_symlink( ):
        exclude_entries.append( agents_link.name )
    canonical = _canonical_skills_directory( project_root )
    if not simulate:
        canonical.mkdir( parents = True, exist_ok = True )
    for _, manager in _resolver.resolve_coders(
        coders, mode = 'per-project'
    ):
        if 'skills' not in manager.item_types_available: continue
        base_directory = manager.resolve_base_directory(
            mode = 'per-project',
            target = project_root,
            configuration = configuration,
            environment = __.os.environ,
        )
        skills_name = manager.calculate_directory_location( 'skills' )
        link_path = base_directory / skills_name
        if _ensure_directory_symlink(
            canonical, link_path,
            simulate = simulate, replace_existing = True,
        ) or link_path.is_symlink( ):
            with _contextlib.suppress( ValueError ):
                exclude_entries.append(
                    _format_exclude_path(
                        link_path.relative_to( project_root ) ) )
    return tuple( exclude_entries )
