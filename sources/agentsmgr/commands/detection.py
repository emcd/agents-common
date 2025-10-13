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


''' Command for detecting Copier configuration in target directories. '''


from . import __
from . import base as _base


_scribe = __.provide_scribe( __name__ )


class DetectCommand( __.appcore_cli.Command ):
    ''' Detects and displays current Copier configuration for agents. '''

    source: __.typx.Annotated[
        __.Path,
        __.tyro.conf.arg(
            help = "Target directory to search for configuration.",
            prefix_name = False ),
    ] = __.dcls.field( default_factory = __.Path.cwd )

    @_base.intercept_errors( )
    async def execute( self, auxdata: __.appcore.state.Globals ) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        ''' Detects agent configuration and displays formatted result. '''
        if not isinstance( auxdata, __.Globals ):  # pragma: no cover
            raise __.ContextInvalidity
        _scribe.info( f"Detecting agent configuration in {self.source}" )
        configuration = await _base.retrieve_configuration( self.source )
        _scribe.debug( f"Found configuration: {configuration}" )
        result = __.ConfigurationDetectionResult(
            target = self.source,
            coders = tuple( configuration[ 'coders' ] ),
            languages = tuple( configuration[ 'languages' ] ),
            project_name = configuration.get( 'project_name' ),
        )
        await __.render_and_print_result(
            result, auxdata.display, auxdata.exits )
