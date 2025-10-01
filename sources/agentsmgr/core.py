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


''' Core types and interfaces for agentsmgr. '''


from . import __


class Renderable( __.typx.Protocol ):
    ''' Protocol for objects that can be rendered as Markdown. '''

    def render_as_markdown( self ) -> tuple[ str, ... ]:
        ''' Renders object as Markdown lines for display. '''
        ...


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


async def render_and_print_result(
    result: Renderable,
    display: DisplayOptions,
    exits: __.ctxl.AsyncExitStack,
) -> None:
    ''' Centralizes result rendering logic with Rich formatting support. '''
    stream = await display.provide_stream( exits )
    match display.presentation:
        case Presentations.Markdown:
            lines = result.render_as_markdown( )
            if display.determine_colorization( stream ):
                from rich.console import Console
                from rich.markdown import Markdown
                console = Console( file = stream, force_terminal = True )
                markdown_obj = Markdown( '\n'.join( lines ) )
                console.print( markdown_obj )
            else:
                output = '\n'.join( lines )
                print( output, file = stream )
