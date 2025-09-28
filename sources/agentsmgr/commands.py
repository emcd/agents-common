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


''' Command implementations for agentsmgr CLI. '''


import yaml as _yaml

from . import __
from . import exceptions as _exceptions


class DetectCommand( __.appcore_cli.Command ):
    ''' Detects and displays current Copier configuration for agents. '''

    target: __.typx.Annotated[
        __.Path,
        __.tyro.conf.arg(
            help = "Target directory to search for configuration." ),
    ] = __.dcls.field( default_factory = __.Path.cwd )

    async def execute( self, auxdata: __.appcore.state.Globals ) -> None:
        ''' Detects and displays agent configuration from Copier answers. '''
        try: configuration = await self._detect_configuration( self.target )
        except _exceptions.ConfigurationAbsence as exception:
            print( f"❌ {exception}" )
            raise SystemExit( 1 ) from None
        except _exceptions.ConfigurationInvalidity as exception:
            print( f"❌ {exception}" )
            raise SystemExit( 1 ) from None
        await self._display_configuration( configuration )

    async def _detect_configuration(
        self, target: __.Path
    ) -> __.cabc.Mapping[ str, __.typx.Any ]:
        ''' Loads configuration from Copier answers file. '''
        answers_file = (
            target / ".auxiliary/configuration/copier-answers--agents.yaml" )
        if not answers_file.exists( ):
            raise _exceptions.ConfigurationAbsence( target )
        try: content = answers_file.read_text( encoding = 'utf-8' )
        except ( OSError, IOError ) as exception:
            raise _exceptions.ConfigurationAbsence( ) from exception
        try:
            configuration: __.cabc.Mapping[ str, __.typx.Any ] = (
                _yaml.safe_load( content ) )
        except _yaml.YAMLError as exception:
            raise _exceptions.ConfigurationInvalidity( ) from exception
        if not isinstance( configuration, __.cabc.Mapping ):
            raise _exceptions.ConfigurationInvalidity( )
        await self._validate_configuration( configuration )
        return configuration

    async def _validate_configuration(
        self, configuration: __.cabc.Mapping[ str, __.typx.Any ]
    ) -> None:
        ''' Validates required configuration fields. '''
        if not configuration.get( "coders" ):
            raise _exceptions.ConfigurationInvalidity( )
        if not configuration.get( "languages" ):
            raise _exceptions.ConfigurationInvalidity( )

    async def _display_configuration(
        self, configuration: __.cabc.Mapping[ str, __.typx.Any ]
    ) -> None:
        ''' Displays configuration in a readable format. '''
        print( "🔍 Agent Configuration Detected:" )
        print( f"   Coders: {', '.join( configuration[ 'coders' ] )}" )
        print( f"   Languages: {', '.join( configuration[ 'languages' ] )}" )
        if "project_name" in configuration:
            print( f"   Project: {configuration[ 'project_name' ]}" )
        print( f"   Target Directory: {self.target.resolve( )}" )
