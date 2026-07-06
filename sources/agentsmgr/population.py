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


''' Command for populating agent content from data sources.

    Also provides the generate command for maintainer-facing generation
    from components/ to distribution/.
'''


from . import __
from . import cmdbase as _cmdbase
from . import core as _core
from . import exceptions as _exceptions
from . import generator as _generator
from . import instructions as _instructions
from . import memorylinks as _memorylinks
from . import operations as _operations
from . import renderers as _renderers
from . import resolver as _resolver
from . import results as _results
from . import userdata as _userdata


_scribe = __.provide_scribe( __name__ )


def _produce_default_configuration(
    location: __.Path,
) -> __.cabc.Mapping[ str, __.typx.Any ]:
    ''' Produces default configuration for generate command.

        Uses all known coders from the renderer registry so that
        fallback content is generated for all coders, not just those
        with direct component content.
    '''
    from . import renderers as _renderers
    coders = sorted( _renderers.RENDERERS.keys( ) )
    return { 'coders': coders, 'languages': [ 'python' ] }


SourceArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.tyro.conf.Positional[ str ],
    __.tyro.conf.arg( help = "Data source (local path or git URL)" ),
]
TargetArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.tyro.conf.Positional[ __.Path ],
    __.tyro.conf.arg( help = "Target directory for content generation" ),
]


def _filter_coders_by_mode(
    coders: __.cabc.Sequence[ str ],
    target_mode: _renderers.ExplicitTargetMode,
) -> tuple[ str, ... ]:
    ''' Filters coders by their default targeting mode.

        Returns coders whose mode_default matches the target mode.
        This ensures populate project only handles per-project coders
        and populate user only handles per-user coders, respecting each
        renderer's designed usage pattern.
    '''
    return tuple(
        name
        for name, _renderer in _resolver.resolve_coders(
            coders, mode = target_mode )
    )


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


def _populate_instructions_if_configured(
    configuration: __.cabc.Mapping[ str, __.typx.Any ],
    target: __.Path,
    tag_prefix: __.Absential[ str ],
    simulate: bool,
) -> tuple[ bool, str ]:
    ''' Populates instructions if configured and returns status.

        Returns tuple of (sources_present, instructions_target_path).
        sources_present indicates whether instruction sources were
        configured and processed.
    '''
    if not configuration.get( 'provide_instructions', False ):
        return ( False, '' )
    instructions_sources = configuration.get( 'instructions_sources', [ ] )
    instructions_target = configuration.get(
        'instructions_target', '.auxiliary/instructions' )
    if not instructions_sources:
        return ( False, instructions_target )
    instructions_attempted, instructions_updated = (
        _instructions.populate_instructions(
            instructions_sources,
            target / instructions_target,
            tag_prefix,
            simulate,
        ) )
    _scribe.info(
        f"Updated {instructions_updated}/{instructions_attempted} "
        "instruction files" )
    return ( True, instructions_target )


def _populate_per_user_content(
    location: __.Path,
    coders: __.cabc.Sequence[ str ],
    configuration: __.cabc.Mapping[ str, __.typx.Any ],
    application_configuration: __.cabc.Mapping[ str, __.typx.Any ],
    simulate: bool,
) -> tuple[ int, int ]:
    ''' Populates commands, agents, and skills for per-user coders.

        Copies distribution items to each coder's per-user directory.
        Returns tuple of (items_attempted, items_written).
    '''
    return _copy_distribution_items(
        location, coders, __.Path.cwd( ), configuration,
        'per-user', simulate )


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


def _copy_distribution_items(  # noqa: PLR0913
    distribution: __.Path,
    coders: __.cabc.Sequence[ str ],
    target: __.Path,
    configuration: __.cabc.Mapping[ str, __.typx.Any ],
    mode: _renderers.ExplicitTargetMode,
    simulate: bool,
) -> tuple[ int, int ]:
    ''' Copies distribution items to downstream target paths.

        For each coder, copies the entire
        distribution/<mode>/coders/<coder>/ tree to the target.
        Skills are copied separately from
        distribution/per-project/general/skills/.

        The distribution tree mirrors downstream layout, so this is
        a single copy operation per coder.

        Returns tuple of (items_attempted, items_written).
    '''
    items_attempted = 0
    items_written = 0
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
            attempted, written = _copy_tree(
                coder_source, base_directory, simulate )
            items_attempted += attempted
            items_written += written
        # Copy skills from general directory.
        if mode == 'per-project':
            attempted, written = _copy_skills(
                distribution, base_directory, manager, simulate )
            items_attempted += attempted
            items_written += written
    return ( items_attempted, items_written )


def _copy_tree(
    source: __.Path,
    target: __.Path,
    simulate: bool,
) -> tuple[ int, int ]:
    ''' Copies directory tree from source to target.

        Recursively copies all files and subdirectories.
        Returns tuple of (files_attempted, files_written).
    '''
    files_attempted = 0
    files_written = 0
    for source_file in source.rglob( '*' ):
        if not source_file.is_file( ): continue
        files_attempted += 1
        relative = source_file.relative_to( source )
        dest_path = target / relative
        if _operations.save_content(
            source_file.read_text( encoding = 'utf-8' ),
            dest_path,
            simulate,
        ):
            files_written += 1
    return ( files_attempted, files_written )


def _copy_skills(
    distribution: __.Path,
    base_directory: __.Path,
    manager: _renderers.RendererBase,
    simulate: bool,
) -> tuple[ int, int ]:
    ''' Copies skill files directly from distribution/ to target paths.

        Skills are static artifacts that require no rendering.
        Copies from distribution/per-project/general/skills/<name>.md to
        <base>/skills/<name>/SKILL.md. Returns tuple of (attempted,
        written).
    '''
    items_attempted = 0
    items_written = 0
    skills_dir = (
        distribution / 'per-project' / 'general' / 'skills' )
    if not skills_dir.exists( ):
        return ( items_attempted, items_written )
    skills_output = manager.calculate_directory_location( 'skills' )
    for skill_file in skills_dir.glob( '*.md' ):
        items_attempted += 1
        item_name = skill_file.stem
        dest_path = (
            base_directory / skills_output / item_name / 'SKILL.md' )
        if _operations.save_content(
            skill_file.read_text( encoding = 'utf-8' ),
            dest_path,
            simulate,
        ):
            items_written += 1
    return ( items_attempted, items_written )


def _manage_project_auxiliaries(
    configuration: __.cabc.Mapping[ str, __.typx.Any ],
    target: __.Path,
    tag_prefix: __.Absential[ str ],
    simulate: bool
) -> None:
    ''' Manages auxiliary project files (instructions, symlinks, excludes). '''
    instructions_populated, instructions_target = (
        _populate_instructions_if_configured(
            configuration, target, tag_prefix, simulate ) )
    all_symlink_names: list[ str ] = list( _create_all_symlinks(
        configuration, target, 'per-project', simulate ) )
    git_exclude_entries: list[ str ] = [ ]
    if instructions_populated:
        git_exclude_entries.append( instructions_target )
    git_exclude_entries.extend( all_symlink_names )
    if git_exclude_entries:
        entries_count = _operations.update_git_exclude(
            target, git_exclude_entries, simulate )
        if entries_count > 0:
            _scribe.info(
                f"Managing {entries_count} entries in .git/info/exclude" )


class PopulateProjectCommand( __.appcore_cli.Command ):
    ''' Generates project-scoped agent content from data sources.

        Populates agent commands, definitions, and static resources
        from the specified data source. Copies pre-rendered commands
        and agents from distribution/, generates skills, and copies
        static resources.
    '''

    source: SourceArgument = '.'
    target: TargetArgument = __.dcls.field( default_factory = __.Path.cwd )
    profile: __.typx.Annotated[
        __.typx.Optional[ __.Path ],
        __.tyro.conf.arg(
            help = (
                "Alternative Copier answers file (defaults to "
                "auto-detected)" ),
            prefix_name = False ),
    ] = None
    simulate: __.typx.Annotated[
        bool,
        __.tyro.conf.arg(
            help = "Dry run mode - show generated content",
            prefix_name = False ),
    ] = False
    tag_prefix: __.typx.Annotated[
        __.typx.Optional[ str ],
        __.tyro.conf.arg(
            help = (
                "Prefix for version tags (e.g., 'v', 'stable-', 'prod-'); "
                "only tags with this prefix are considered and the prefix "
                "is stripped before version parsing" ),
            prefix_name = False ),
    ] = None

    @_cmdbase.intercept_errors( )
    async def execute( self, auxdata: __.appcore.state.Globals ) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        ''' Generates project content from data sources. '''
        if not isinstance( auxdata, _core.Globals ):  # pragma: no cover
            raise _exceptions.ContextInvalidity
        _scribe.info(
            f"Populating project content from {self.source} to {self.target}" )
        configuration = await _cmdbase.retrieve_configuration(
            self.target, self.profile )
        per_project_coders = _filter_coders_by_mode(
            configuration[ 'coders' ], 'per-project' )
        if not per_project_coders:
            _scribe.warning(
                "No per-project default coders found in configuration" )
            return
        filtered_configuration = dict( configuration )
        filtered_configuration[ 'coders' ] = per_project_coders
        prefix = __.absent if self.tag_prefix is None else self.tag_prefix
        location = _cmdbase.retrieve_data_location( self.source, prefix )
        _cmdbase.validate_data_source_structure(
            location, ( 'per-project', ) )
        items_attempted, items_copied = _copy_distribution_items(
            location,
            filtered_configuration[ 'coders' ],
            self.target,
            configuration,
            'per-project',
            self.simulate )
        if items_attempted > 0:
            _scribe.info(
                f"Copied {items_copied}/{items_attempted} items" )
        _manage_project_auxiliaries(
            filtered_configuration, self.target, prefix, self.simulate )
        result = _results.ContentGenerationResult(
            source_location = location,
            target_location = self.target,
            coders = tuple( configuration[ 'coders' ] ),
            simulated = self.simulate,
            items_generated = (
                items_attempted if self.simulate else items_copied ),
        )
        await _core.render_and_print_result(
            result, auxdata.display, auxdata.exits )


class PopulateUserCommand( __.appcore_cli.Command ):
    ''' Populates per-user global settings and executables. '''

    source: SourceArgument = '.'
    profile: __.typx.Annotated[
        __.typx.Optional[ __.Path ],
        __.tyro.conf.arg(
            help = (
                "Alternative Copier answers file (defaults to "
                "auto-detected)" ),
            prefix_name = False ),
    ] = None
    simulate: __.typx.Annotated[
        bool,
        __.tyro.conf.arg(
            help = "Dry run mode - show what would be installed",
            prefix_name = False ),
    ] = False
    tag_prefix: __.typx.Annotated[
        __.typx.Optional[ str ],
        __.tyro.conf.arg(
            help = (
                "Prefix for version tags (e.g., 'v', 'stable-', 'prod-'); "
                "only tags with this prefix are considered and the prefix "
                "is stripped before version parsing" ),
            prefix_name = False ),
    ] = None

    @_cmdbase.intercept_errors( )
    async def execute( self, auxdata: __.appcore.state.Globals ) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        ''' Populates user-scoped settings and executables. '''
        if not isinstance( auxdata, _core.Globals ):  # pragma: no cover
            raise _exceptions.ContextInvalidity
        _scribe.info( f"Populating user configuration from {self.source}" )
        configuration = await _cmdbase.retrieve_configuration(
            __.Path.cwd( ), self.profile )
        per_user_coders = _filter_coders_by_mode(
            configuration[ 'coders' ], 'per-user' )
        if not per_user_coders:
            _scribe.warning(
                "No per-user default coders found in configuration" )
            return
        prefix = __.absent if self.tag_prefix is None else self.tag_prefix
        location = _cmdbase.retrieve_data_location( self.source, prefix )
        _cmdbase.validate_data_source_structure(
            location,
            ( 'per-user', ) )
        content_attempted, content_generated = _populate_per_user_content(
            location,
            per_user_coders,
            configuration,
            auxdata.configuration,
            self.simulate,
        )
        if content_attempted > 0:
            _scribe.info(
                f"Generated {content_generated}/{content_attempted} items" )
        globals_attempted, globals_updated = _userdata.populate_globals(
            location,
            per_user_coders,
            auxdata.configuration,
            self.simulate,
        )
        _scribe.info(
            f"Updated {globals_updated}/{globals_attempted} global files" )
        wrappers_attempted, wrappers_installed = (
            _userdata.populate_user_wrappers( location, self.simulate ) )
        if wrappers_attempted > 0:
            _scribe.info(
                f"Installed {wrappers_installed}/{wrappers_attempted} "
                "wrapper scripts" )
        total_items = content_generated + globals_updated + wrappers_installed
        result = _results.ContentGenerationResult(
            source_location = location,
            target_location = __.Path.home( ),
            coders = per_user_coders,
            simulated = self.simulate,
            items_generated = total_items,
        )
        await _core.render_and_print_result(
            result, auxdata.display, auxdata.exits )


class PopulateCommand( __.appcore_cli.Command ):
    ''' Populates agent content and configuration. '''

    command: __.typx.Union[
        __.typx.Annotated[
            PopulateProjectCommand,
            __.tyro.conf.subcommand( 'project', prefix_name = False ),
        ],
        __.typx.Annotated[
            PopulateUserCommand,
            __.tyro.conf.subcommand( 'user', prefix_name = False ),
        ],
    ] = __.dcls.field( default_factory = PopulateProjectCommand )

    async def execute( self, auxdata: __.appcore.state.Globals ) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        await self.command( auxdata )


class GenerateCommand( __.appcore_cli.Command ):
    ''' Generates pre-rendered artifacts from components/ to distribution/.

        Reads 3-tier pipeline source material from components/ and writes
        rendered commands and agents to distribution/. Skills are direct
        distribution artifacts and are not generated.

        Use --check to validate that distribution/ is current without
        writing files.
    '''

    source: __.typx.Annotated[
        str,
        __.tyro.conf.arg(
            help = "Components source path (defaults to 'components')" ),
    ] = 'components'
    output: __.typx.Annotated[
        __.Path,
        __.tyro.conf.arg(
            help = "Distribution output path" ),
    ] = __.Path( 'distribution' )
    check: __.typx.Annotated[
        bool,
        __.tyro.conf.arg(
            help = "Check mode - fail if distribution is stale",
            prefix_name = False ),
    ] = False
    simulate: __.typx.Annotated[
        bool,
        __.tyro.conf.arg(
            help = "Dry run mode - show what would be generated",
            prefix_name = False ),
    ] = False

    @_cmdbase.intercept_errors( )
    async def execute( self, auxdata: __.appcore.state.Globals ) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        ''' Generates distribution artifacts from components. '''
        if not isinstance( auxdata, _core.Globals ):  # pragma: no cover
            raise _exceptions.ContextInvalidity
        _scribe.info(
            f"Generating distribution from {self.source} to {self.output}" )
        location = _cmdbase.retrieve_data_location( self.source )
        _cmdbase.validate_data_source_structure(
            location,
            ( 'configurations', 'contents', 'templates' ) )
        configuration = _produce_default_configuration( location )
        generator = _generator.ContentGenerator(
            location = location,
            configuration = configuration,
            application_configuration = auxdata.configuration,
            mode = 'per-project',
        )
        if self.check:
            items_checked, diff_lines = (
                _operations.check_distribution_staleness(
                    generator, self.output ) )
            if diff_lines:
                _scribe.error(
                    f"Distribution is stale ({items_checked} items checked):" )
                for line in diff_lines:
                    print( line )
                raise SystemExit( 1 )
            _scribe.info(
                f"Distribution is current ({items_checked} items checked)" )
            return
        items_attempted, items_generated = (
            _operations.generate_distribution(
                generator, self.output, self.simulate ) )
        _scribe.info(
            f"Generated {items_generated}/{items_attempted} artifacts" )
        result = _results.ContentGenerationResult(
            source_location = location,
            target_location = self.output,
            coders = tuple( configuration.get( 'coders', ( ) ) ),
            simulated = self.simulate,
            items_generated = items_generated,
        )
        await _core.render_and_print_result(
            result, auxdata.display, auxdata.exits )