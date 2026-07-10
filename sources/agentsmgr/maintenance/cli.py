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
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. #
#  See the License for the specific language governing permissions and      #
#  limitations under the License.                                            #
#                                                                            #
#============================================================================#


''' Maintainer-facing command-line interface.

    After the copiertv migration, the only remaining maintainer command
    is ``validate``, which renders the distribution tree from
    ``components/`` using a variant answers file from
    ``tests/data/profiles/`` into an isolated temp directory. Copier
    template rendering validation is now provided by copiertv.
'''


from . import __
from . import content as _content


class MaintainerApplication( __.appcore_cli.Application ):
    ''' Maintainer-facing agents configuration management CLI. '''

    display: __.core.DisplayOptions = __.dcls.field(
        default_factory = __.core.DisplayOptions )
    command: _content.ValidateCommand = __.dcls.field(
        default_factory = _content.ValidateCommand )

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