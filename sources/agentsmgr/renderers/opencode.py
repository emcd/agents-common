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


''' OpenCode renderer implementation.

    Provides path resolution and targeting mode validation for OpenCode,
    which supports both per-user and per-project configuration.
'''


from . import __
from .base import RENDERERS, ExplicitTargetMode, RendererBase


class OpencodeRenderer( RendererBase ):
    ''' Renderer for OpenCode coder.

        Supports both per-user and per-project configuration modes.
        Per-user mode respects OPENCODE_CONFIG environment variable
        with fallback to configuration overrides and XDG-like default.
    '''

    name = 'opencode'
    modes_available = frozenset( ( 'per-user', 'per-project' ) )
    mode_default = 'per-project'
    memory_filename = 'AGENTS.md'

    _LOCATIONS_MAP = __.immut.Dictionary( {
        'agents': 'agent',
        'commands': 'command',
    } )

    def calculate_directory_location( self, item_type: str ) -> str:
        ''' Returns singular directory names for OpenCode configuration.
        
            OpenCode expects singular directory names (agent, command) rather
            than the plural forms used by other coders.
        '''
        return self._LOCATIONS_MAP.get( item_type, item_type )

    def get_template_flavor( self, item_type: str ) -> str:
        ''' Determines template flavor for OpenCode.

            OpenCode shares markdown command format with Claude but uses
            its own agent format, so returns 'claude' for commands and
            'opencode' for agents.
        '''
        if item_type == 'commands':
            return 'claude'
        return 'opencode'

    def resolve_base_directory(
        self,
        mode: ExplicitTargetMode,
        target: __.Path,
        configuration: __.cabc.Mapping[ str, __.typx.Any ],
        environment: __.cabc.Mapping[ str, str ],
    ) -> __.Path:
        ''' Resolves base output directory for OpenCode.

            For per-project mode, returns .opencode in project root.
            For per-user mode, respects precedence: OPENCODE_CONFIG
            environment variable, configuration file override, or
            XDG-like ~/.config/opencode default.
        '''
        self.validate_mode( mode )
        if mode == 'per-project':
            return target / ".auxiliary/configuration/coders/opencode"
        if mode == 'per-user':
            return self._resolve_user_directory( configuration, environment )
        raise __.TargetModeNoSupport( self.name, mode )

    def _resolve_user_directory(
        self,
        configuration: __.cabc.Mapping[ str, __.typx.Any ],
        environment: __.cabc.Mapping[ str, str ],
    ) -> __.Path:
        ''' Resolves per-user directory following precedence rules.

            Precedence order:
            1. OPENCODE_CONFIG environment variable (directory containing
               opencode.json settings file)
            2. Configuration file override (directory for this coder)
            3. XDG-like default ~/.config/opencode
        '''
        if 'OPENCODE_CONFIG' in environment:
            directory = __.Path( environment[ 'OPENCODE_CONFIG' ] )
            return directory.expanduser( )
        coder_configuration = self._extract_coder_configuration(
            configuration )
        if 'directory' in coder_configuration:
            directory = __.Path( coder_configuration[ 'directory' ] )
            return directory.expanduser( )
        return __.Path.home( ) / '.config' / 'opencode'

    def _extract_coder_configuration(
        self, configuration: __.cabc.Mapping[ str, __.typx.Any ]
    ) -> __.cabc.Mapping[ str, __.typx.Any ]:
        ''' Extracts configuration for this specific coder.

            Looks for coder entry in configuration coders array by name.
        '''
        coders = configuration.get( 'coders', ( ) )
        for coder in coders:
            if coder.get( 'name' ) == self.name:
                return coder
        return { }


RENDERERS[ 'opencode' ] = OpencodeRenderer( )
