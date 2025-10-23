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

        Returns tuple of (attempted, created, symlink_names) where
        symlink_names contains names of all symlinks (both newly created
        and pre-existing).
    '''
    attempted = 0
    created = 0
    symlink_names: list[ str ] = [ ]
    for coder_name in coders:
        try: renderers[ coder_name ]
        except KeyError as exception:
            raise _exceptions.CoderAbsence( coder_name ) from exception

        # Source: actual location under .auxiliary/configuration/coders/
        source = (
            target / '.auxiliary' / 'configuration' / 'coders' / coder_name )
        # Link: expected location for coder (.claude, .opencode, etc.)
        link_path = target / f'.{coder_name}'

        attempted += 1
        was_created, symlink_name = _memorylinks.create_memory_symlink(
            source, link_path, simulate )
        if was_created: created += 1
        symlink_names.append( symlink_name )

        # Create .mcp.json symlink for Claude coder specifically
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


class PopulateCommand( __.appcore_cli.Command ):
    ''' Generates dynamic agent content from data sources. '''

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
    mode: __.typx.Annotated[
        _renderers.TargetMode,
        __.tyro.conf.arg(
            help = (
                "Targeting mode: default (use coder defaults), per-user, "
                "per-project, or nowhere (skip generation)" ),
            prefix_name = False ),
    ] = 'default'
    update_globals: __.typx.Annotated[
        bool,
        __.tyro.conf.arg(
            help = "Update per-user global files (orthogonal to mode)",
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
        ''' Generates content from data sources and displays result. '''
        if not isinstance( auxdata, _core.Globals ):  # pragma: no cover
            raise _exceptions.ContextInvalidity
        _scribe.info(
            f"Populating agent content from {self.source} to {self.target}" )
        configuration = await _cmdbase.retrieve_configuration(
            self.target, self.profile )
        coder_count = len( configuration[ 'coders' ] )
        _scribe.debug( f"Detected configuration with {coder_count} coders" )
        _scribe.debug( f"Using {self.mode} targeting mode" )
        prefix = (
            __.absent if self.tag_prefix is None
            else self.tag_prefix )
        location = _cmdbase.retrieve_data_location( self.source, prefix )
        generator = _generator.ContentGenerator(
            location = location,
            configuration = configuration,
            application_configuration = auxdata.configuration,
            mode = self.mode,
        )
        items_attempted, items_generated = _operations.populate_directory(
            generator, self.target, self.simulate )
        _scribe.info( f"Generated {items_generated}/{items_attempted} items" )
        instructions_populated, instructions_target = (
            _populate_instructions_if_configured(
                configuration, self.target, prefix, self.simulate ) )
        all_symlink_names = _create_all_symlinks(
            configuration, self.target, self.mode, self.simulate )
        git_exclude_entries: list[ str ] = [ ]
        if instructions_populated:
            git_exclude_entries.append( instructions_target )
        git_exclude_entries.extend( all_symlink_names )
        if self.update_globals:
            globals_attempted, globals_updated = (
                _userdata.populate_globals(
                    location,
                    configuration[ 'coders' ],
                    auxdata.configuration,
                    self.simulate,
                ) )
            _scribe.info(
                f"Updated {globals_updated}/{globals_attempted} "
                "global files" )
        if git_exclude_entries:
            excludes_added = _operations.update_git_exclude(
                self.target, git_exclude_entries, self.simulate )
            if excludes_added > 0:
                _scribe.info(
                    f"Added {excludes_added} entries to .git/info/exclude" )
        result = _results.ContentGenerationResult(
            source_location = location,
            target_location = self.target,
            coders = tuple( configuration[ 'coders' ] ),
            simulated = self.simulate,
            items_generated = items_generated,
        )
        await _core.render_and_print_result(
            result, auxdata.display, auxdata.exits )
