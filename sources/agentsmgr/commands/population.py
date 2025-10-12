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
from . import base as _base
from . import generator as _generator
from . import memorylinks as _memorylinks
from . import operations as _operations
from . import userdata as _userdata


_scribe = __.provide_scribe( __name__ )


def _create_coder_directory_symlinks(
    coders: __.cabc.Sequence[ str ],
    target: __.Path,
    renderers: __.cabc.Mapping[ str, __.typx.Any ],
    simulate: bool = False,
) -> tuple[ int, int ]:
    ''' Creates symlinks from .{coder} to .auxiliary/configuration/coders/.

        For per-project mode, creates symlinks that make coder directories
        accessible at their expected locations (.claude, .opencode, etc.)
        while keeping actual files organized under
        .auxiliary/configuration/coders/.

        Returns tuple of (attempted, created) counts.
    '''
    attempted = 0
    created = 0
    for coder_name in coders:
        try: renderers[ coder_name ]
        except KeyError as exception:
            raise __.CoderAbsence( coder_name ) from exception

        # Source: actual location under .auxiliary/configuration/coders/
        source = (
            target / '.auxiliary' / 'configuration' / 'coders' / coder_name )
        # Link: expected location for coder (.claude, .opencode, etc.)
        link_path = target / f'.{coder_name}'

        attempted += 1
        if _memorylinks.create_memory_symlink( source, link_path, simulate ):
            created += 1

        # Create .mcp.json symlink for Claude coder specifically
        if coder_name == 'claude':
            mcp_source = (
                target / '.auxiliary' / 'configuration' / 'mcp-servers.json' )
            mcp_link = target / '.mcp.json'
            attempted += 1
            if _memorylinks.create_memory_symlink(
                mcp_source, mcp_link, simulate ):
                created += 1

    return ( attempted, created )


class PopulateCommand( __.appcore_cli.Command ):
    ''' Generates dynamic agent content from data sources. '''

    source: __.typx.Annotated[
        str,
        __.tyro.conf.arg(
            help = "Data source (local path or git URL)",
            prefix_name = False ),
    ] = '.'
    target: __.typx.Annotated[
        __.Path,
        __.tyro.conf.arg(
            help = "Target directory for content generation",
            prefix_name = False ),
    ] = __.dcls.field( default_factory = __.Path.cwd )
    simulate: __.typx.Annotated[
        bool,
        __.tyro.conf.arg(
            help = "Dry run mode - show generated content",
            prefix_name = False ),
    ] = False
    mode: __.typx.Annotated[
        __.TargetMode,
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

    @_base.intercept_errors( )
    async def execute( self, auxdata: __.appcore.state.Globals ) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        ''' Generates content from data sources and displays result. '''
        if not isinstance( auxdata, __.Globals ):  # pragma: no cover
            raise __.ContextInvalidity
        _scribe.info(
            f"Populating agent content from {self.source} to {self.target}" )
        configuration = await _base.retrieve_configuration( self.target )
        coder_count = len( configuration[ 'coders' ] )
        _scribe.debug( f"Detected configuration with {coder_count} coders" )
        _scribe.debug( f"Using {self.mode} targeting mode" )
        location = _base.retrieve_data_location( self.source )
        generator = _generator.ContentGenerator(
            location = location,
            configuration = configuration,
            application_configuration = auxdata.configuration,
            mode = self.mode,
        )
        items_attempted, items_generated = _operations.populate_directory(
            generator, self.target, self.simulate )
        _scribe.info( f"Generated {items_generated}/{items_attempted} items" )
        if self.mode != 'nowhere':
            links_attempted, links_created = (
                _memorylinks.create_memory_symlinks_for_coders(
                    coders = configuration[ 'coders' ],
                    target = self.target,
                    renderers = __.RENDERERS,
                    simulate = self.simulate,
                ) )
            if links_created > 0:
                _scribe.info(
                    f"Created {links_created}/{links_attempted} "
                    "memory symlinks" )
            # Create coder directory symlinks for per-project mode
            if self.mode == 'per-project':
                coder_symlinks_attempted, coder_symlinks_created = (
                    _create_coder_directory_symlinks(
                        coders = configuration[ 'coders' ],
                        target = self.target,
                        renderers = __.RENDERERS,
                        simulate = self.simulate,
                    ) )
                if coder_symlinks_created > 0:
                    _scribe.info(
                        f"Created {coder_symlinks_created}/"
                        f"{coder_symlinks_attempted} coder directory symlinks")
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
        result = __.ContentGenerationResult(
            source_location = location,
            target_location = self.target,
            coders = tuple( configuration[ 'coders' ] ),
            simulated = self.simulate,
            items_generated = items_generated,
        )
        await __.render_and_print_result(
            result, auxdata.display, auxdata.exits )
