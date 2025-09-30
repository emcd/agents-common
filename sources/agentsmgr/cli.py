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


''' Command-line interface. '''


from . import __
from . import commands as _commands
from . import results as _results


class Presentations( __.enum.Enum ):
    ''' Enumeration for CLI display presentation formats. '''

    Markdown = 'markdown'


class DisplayOptions( __.appcore_cli.DisplayOptions ):
    ''' Consolidated display configuration for CLI output. '''

    presentation: Presentations = Presentations.Markdown


class Globals( __.appcore.state.Globals ):
    ''' Agentsmgr-specific global state container.

        Extends appcore.state.Globals with agentsmgr-specific display
        configuration.
    '''

    display: DisplayOptions = __.dcls.field( default_factory = DisplayOptions )


async def _render_and_print_result(
    result: _results.ResultBase,
    display: DisplayOptions,
    exits: __.ctxl.AsyncExitStack,
    **nomargs: __.typx.Any
) -> None:
    ''' Centralizes result rendering logic with Rich formatting support. '''
    stream = await display.provide_stream( exits )
    match display.presentation:
        case Presentations.Markdown:
            lines = result.render_as_markdown( **nomargs )
            if display.determine_colorization( stream ):
                from rich.console import Console
                from rich.markdown import Markdown
                console = Console( file = stream, force_terminal = True )
                markdown_obj = Markdown( '\n'.join( lines ) )
                console.print( markdown_obj )
            else:
                output = '\n'.join( lines )
                print( output, file = stream )


class Application( __.appcore_cli.Application ):
    ''' Agent configuration management CLI. '''

    display: DisplayOptions = __.dcls.field( default_factory = DisplayOptions )
    command: __.typx.Union[
        __.typx.Annotated[
            _commands.DetectCommand,
            __.tyro.conf.subcommand( 'detect', prefix_name = False ),
        ],
        __.typx.Annotated[
            _commands.PopulateCommand,
            __.tyro.conf.subcommand( 'populate', prefix_name = False ),
        ],
        __.typx.Annotated[
            _commands.SurveyCommand,
            __.tyro.conf.subcommand( 'survey', prefix_name = False ),
        ],
        __.typx.Annotated[
            _commands.ValidateCommand,
            __.tyro.conf.subcommand( 'validate', prefix_name = False ),
        ],
    ] = __.dcls.field( default_factory = _commands.DetectCommand )

    async def execute( self, auxdata: Globals ) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        ''' Executes the specified command. '''
        await self.command( auxdata )

    async def prepare( self, exits: __.ctxl.AsyncExitStack ) -> Globals:
        ''' Prepares agentsmgr-specific global state with display options. '''
        auxdata_base = await super( ).prepare( exits )
        nomargs = {
            field.name: getattr( auxdata_base, field.name )
            for field in __.dcls.fields( auxdata_base )
            if not field.name.startswith( '_' ) }
        return Globals( display = self.display, **nomargs )


def execute( ) -> None:
    ''' Entrypoint for CLI execution. '''
    config = ( __.tyro.conf.HelptextFromCommentsOff, )
    try: __.asyncio.run( __.tyro.cli( Application, config = config )( ) )
    except SystemExit: raise
    except BaseException:
        # TODO: Log exception.
        raise SystemExit( 1 ) from None
