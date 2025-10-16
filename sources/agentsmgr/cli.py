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
from . import core as _core
from . import detection as _detection
from . import population as _population


class Application( __.appcore_cli.Application ):
    ''' Agents configuration management CLI. '''

    display: _core.DisplayOptions = __.dcls.field(
        default_factory = _core.DisplayOptions )
    command: __.typx.Union[
        __.typx.Annotated[
            _detection.DetectCommand,
            __.tyro.conf.subcommand( 'detect', prefix_name = False ),
        ],
        __.typx.Annotated[
            _population.PopulateCommand,
            __.tyro.conf.subcommand( 'populate', prefix_name = False ),
        ],
    ] = __.dcls.field( default_factory = _detection.DetectCommand )

    async def execute( self, auxdata: _core.Globals ) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        await self.command( auxdata )

    async def prepare( self, exits: __.ctxl.AsyncExitStack ) -> _core.Globals:
        auxdata_base = await super( ).prepare( exits )
        nomargs = {
            field.name: getattr( auxdata_base, field.name )
            for field in __.dcls.fields( auxdata_base )
            if not field.name.startswith( '_' ) }
        return _core.Globals( display = self.display, **nomargs )


def execute( ) -> None:
    ''' Entrypoint for CLI execution. '''
    config = ( __.tyro.conf.HelptextFromCommentsOff, )
    try: __.asyncio.run( __.tyro.cli( Application, config = config )( ) )
    except SystemExit: raise
    except BaseException:
        # TODO: Log exception.
        raise SystemExit( 1 ) from None
