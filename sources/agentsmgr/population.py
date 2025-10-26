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


''' Command for populating agent content from data sources. '''


from . import __
from . import cmdbase as _cmdbase
from . import core as _core
from . import exceptions as _exceptions
from . import generator as _generator
from . import instructions as _instructions
from . import memorylinks as _memorylinks
from . import operations as _operations
from . import renderers as _renderers
from . import results as _results
from . import userdata as _userdata


_scribe = __.provide_scribe( __name__ )


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
    renderers: __.cabc.Mapping[ str, __.typx.Any ],
) -> tuple[ str, ... ]:
    ''' Filters coders by their default targeting mode.

        Returns coders whose mode_default matches the target mode.
        This ensures populate project only handles per-project coders
        and populate user only handles per-user coders, respecting each
        renderer's designed usage pattern.
    '''
    filtered: list[ str ] = [ ]
    for coder_name in coders:
        try: renderer = renderers[ coder_name ]
        except KeyError as exception:
            raise _exceptions.CoderAbsence( coder_name ) from exception
        if renderer.mode_default == target_mode:
            filtered.append( coder_name )
        else:
            _scribe.debug(
                f"Skipping {coder_name} for {target_mode} mode: "
                f"default mode is {renderer.mode_default}" )
    return tuple( filtered )


def _create_all_symlinks(
    configuration: __.cabc.Mapping[ str, __.typx.Any ],
    target: __.Path,
    mode: str,
    simulate: bool,
) -> tuple[ str, ... ]:
    ''' Creates all symlinks and returns their names for git exclude.

        Creates memory symlinks for all coders and coder directory
        symlinks for per-project mode. Returns tuple of all symlink
        names (both newly created and pre-existing) for git exclude
        update.
    '''
    all_symlink_names: list[ str ] = [ ]
    if mode == 'nowhere': return tuple( all_symlink_names )
    links_attempted, links_created, symlink_names = (
        _memorylinks.create_memory_symlinks_for_coders(
            coders = configuration[ 'coders' ],
            target = target,
            renderers = _renderers.RENDERERS,
            simulate = simulate,
        ) )
    all_symlink_names.extend( symlink_names )
    if links_created > 0:
        _scribe.info(
            f"Created {links_created}/{links_attempted} memory symlinks" )
    needs_coder_symlinks = (
        mode == 'per-project'
        or ( mode == 'default' and any(
            _renderers.RENDERERS[ coder ].mode_default == 'per-project'
            for coder in configuration[ 'coders' ] ) ) )
    if needs_coder_symlinks:
        (   coder_symlinks_attempted,
            coder_symlinks_created,
            coder_symlink_names ) = (
            _create_coder_directory_symlinks(
                coders = configuration[ 'coders' ],
                target = target,
                renderers = _renderers.RENDERERS,
                simulate = simulate,
            ) )
        all_symlink_names.extend( coder_symlink_names )
        if coder_symlinks_created > 0:
            _scribe.info(
                f"Created {coder_symlinks_created}/"
                f"{coder_symlinks_attempted} coder directory symlinks" )
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
        f"Updated {instructions_updated}/"
        f"{instructions_attempted} instruction files" )
    return ( True, instructions_target )


def _populate_per_user_content(
    location: __.Path,
    coders: __.cabc.Sequence[ str ],
    configuration: __.cabc.Mapping[ str, __.typx.Any ],
    application_configuration: __.cabc.Mapping[ str, __.typx.Any ],
    simulate: bool,
) -> tuple[ int, int ]:
    ''' Populates commands and agents for per-user coders.

        Generates content to each coder's per-user directory using
        renderer's resolve_base_directory() with per-user mode.
        Returns tuple of (items_attempted, items_generated).
    '''
    items_attempted = 0
    items_generated = 0
    for coder_name in coders:
        try: renderer = _renderers.RENDERERS[ coder_name ]
        except KeyError as exception:
            raise _exceptions.CoderAbsence( coder_name ) from exception
        coder_configuration = { 'coders': [ coder_name ] }
        generator = _generator.ContentGenerator(
            location = location,
            configuration = coder_configuration,
            application_configuration = application_configuration,
            mode = 'per-user',
        )
        target = renderer.resolve_base_directory(
            'per-user', __.Path.cwd( ), configuration, dict( __.os.environ ) )
        attempted, generated = _operations.populate_directory(
            generator, target, simulate )
        items_attempted += attempted
        items_generated += generated
    return ( items_attempted, items_generated )


def _create_coder_directory_symlinks(
    coders: __.cabc.Sequence[ str ],
    target: __.Path,
    renderers: __.cabc.Mapping[ str, __.typx.Any ],
    simulate: bool = False,
) -> tuple[ int, int, tuple[ str, ... ] ]:
    ''' Creates symlinks from .{coder} to .auxiliary/configuration/coders/.

        For per-project mode, creates symlinks that make coder directories
        accessible at their expected locations (.claude, .opencode, etc.)
        while keeping actual files organized under
        .auxiliary/configuration/coders/.

        Only creates symlinks for coders whose default mode is per-project.
        Coders with per-user default mode are skipped since they do not
        use per-project directories.

        Returns tuple of (attempted, created, symlink_names) where
        symlink_names contains names of all symlinks (both newly created
        and pre-existing).
    '''
    # TODO: Move symlink rendering to coders and call common code from each
    #       one. Should have not have coder-specific logic in this general
    #       function.
    attempted = 0
    created = 0
    symlink_names: list[ str ] = [ ]
    for coder_name in coders:
        try: renderer = renderers[ coder_name ]
        except KeyError as exception:
            raise _exceptions.CoderAbsence( coder_name ) from exception
        if renderer.mode_default != 'per-project':
            _scribe.debug(
                f"Skipping directory symlink for {coder_name}: "
                f"default mode is {renderer.mode_default}" )
            continue
        source = (
            target / '.auxiliary' / 'configuration' / 'coders' / coder_name )
        link_path = target / f'.{coder_name}'
        attempted += 1
        was_created, symlink_name = _memorylinks.create_memory_symlink(
            source, link_path, simulate )
        if was_created: created += 1
        symlink_names.append( symlink_name )
        if coder_name == 'claude':
            mcp_source = (
                target / '.auxiliary' / 'configuration' / 'mcp-servers.json' )
            mcp_link = target / '.mcp.json'
            attempted += 1
            was_created, symlink_name = _memorylinks.create_memory_symlink(
                mcp_source, mcp_link, simulate )
            if was_created: created += 1
            symlink_names.append( symlink_name )
    return ( attempted, created, tuple( symlink_names ) )


class PopulateProjectCommand( __.appcore_cli.Command ):
    ''' Generates project-scoped agent content from data sources. '''

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
            configuration[ 'coders' ], 'per-project', _renderers.RENDERERS )
        if not per_project_coders:
            _scribe.warning(
                "No per-project default coders found in configuration" )
            return
        filtered_configuration = dict( configuration )
        filtered_configuration[ 'coders' ] = per_project_coders
        prefix = __.absent if self.tag_prefix is None else self.tag_prefix
        location = _cmdbase.retrieve_data_location( self.source, prefix )
        _cmdbase.validate_data_source_structure(
            location,
            ( 'configurations', 'contents', 'templates' ) )
        generator = _generator.ContentGenerator(
            location = location,
            configuration = filtered_configuration,
            application_configuration = auxdata.configuration,
            mode = 'per-project',
        )
        items_attempted, items_generated = _operations.populate_directory(
            generator, self.target, self.simulate )
        _scribe.info( f"Generated {items_generated}/{items_attempted} items" )
        instructions_populated, instructions_target = (
            _populate_instructions_if_configured(
                filtered_configuration, self.target, prefix, self.simulate ) )
        all_symlink_names = _create_all_symlinks(
            filtered_configuration, self.target, 'per-project', self.simulate )
        git_exclude_entries: list[ str ] = [ ]
        if instructions_populated:
            git_exclude_entries.append( instructions_target )
        git_exclude_entries.extend( all_symlink_names )
        if git_exclude_entries:
            entries_count = _operations.update_git_exclude(
                self.target, git_exclude_entries, self.simulate )
            if entries_count > 0:
                _scribe.info(
                    f"Managing {entries_count} entries in .git/info/exclude" )
        result = _results.ContentGenerationResult(
            source_location = location,
            target_location = self.target,
            coders = tuple( configuration[ 'coders' ] ),
            simulated = self.simulate,
            items_generated = items_generated,
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
            configuration[ 'coders' ], 'per-user', _renderers.RENDERERS )
        if not per_user_coders:
            _scribe.warning(
                "No per-user default coders found in configuration" )
            return
        prefix = __.absent if self.tag_prefix is None else self.tag_prefix
        location = _cmdbase.retrieve_data_location( self.source, prefix )
        _cmdbase.validate_data_source_structure(
            location,
            ( 'configurations', 'contents', 'templates',
              'user/configurations', 'user/executables' ) )
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
