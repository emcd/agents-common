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


''' Maintainer-facing command-line interface with validate command. '''


from . import __
from .validation import ValidateCommand as _ValidateCommand


class MaintainerApplication( __.appcore_cli.Application ):
    ''' Maintainer-facing agents configuration management CLI. '''

    display: __.core.DisplayOptions = __.dcls.field(
        default_factory = __.core.DisplayOptions )
    command: __.typx.Annotated[
        _ValidateCommand,
        __.tyro.conf.subcommand( 'validate', prefix_name = False ),
    ] = __.dcls.field( default_factory = _ValidateCommand )

    async def execute( self, auxdata: __.Globals ) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        await self.command( auxdata )

    async def prepare(
        self, exits: __.ctxl.AsyncExitStack
    ) -> __.Globals:
        auxdata_base = await super( ).prepare( exits )
        nomargs = {
            field.name: getattr( auxdata_base, field.name )
            for field in __.dcls.fields( auxdata_base )
            if not field.name.startswith( '_' ) }
        return __.Globals( display = self.display, **nomargs )


def execute( ) -> None:
    ''' Entrypoint for maintainer-facing CLI execution. '''
    config = ( __.tyro.conf.HelptextFromCommentsOff, )
    try:
        __.asyncio.run(
            __.tyro.cli( MaintainerApplication, config = config )( ) )
    except SystemExit: raise
    except BaseException:
        # TODO: Log exception.
        raise SystemExit( 1 ) from None
