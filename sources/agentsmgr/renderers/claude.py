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


''' Claude Code renderer implementation.

    Provides path resolution and targeting mode validation for Claude Code,
    which supports both per-user and per-project configuration.
'''


from . import __
from .base import RENDERERS, ExplicitTargetMode, RendererBase


class ClaudeRenderer( RendererBase ):
    ''' Renderer for Claude Code coder.

        Supports both per-user and per-project configuration modes.
        Per-user mode respects CLAUDE_CONFIG_DIR environment variable
        with fallback to configuration overrides and default location.
    '''

    name = 'claude'
    modes_available = frozenset( ( 'per-user', 'per-project' ) )
    mode_default = 'per-project'
    memory_filename = 'CLAUDE.md'

    def get_template_flavor( self, item_type: str ) -> str:
        ''' Determines template flavor for Claude Code.

            Claude uses markdown format for both commands and agents,
            so always returns 'claude' flavor.
        '''
        return 'claude'

    def resolve_base_directory(
        self,
        mode: ExplicitTargetMode,
        target: __.Path,
        configuration: __.cabc.Mapping[ str, __.typx.Any ],
        environment: __.cabc.Mapping[ str, str ],
    ) -> __.Path:
        ''' Resolves base output directory for Claude Code.

            For per-project mode, returns .claude in project root.
            For per-user mode, respects precedence: CLAUDE_CONFIG_DIR
            environment variable, configuration file override, or default
            ~/.claude location.
        '''
        self.validate_mode( mode )
        if mode == 'per-project':
            return target / ".auxiliary/configuration/coders/claude"
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
            1. CLAUDE_CONFIG_DIR environment variable
            2. Configuration file override (directory for this coder)
            3. Default ~/.claude location
        '''
        if 'CLAUDE_CONFIG_DIR' in environment:
            directory = __.Path( environment[ 'CLAUDE_CONFIG_DIR' ] )
            return directory.expanduser( )
        coder_configuration = self._extract_coder_configuration(
            configuration )
        if 'directory' in coder_configuration:
            directory = __.Path( coder_configuration[ 'directory' ] )
            return directory.expanduser( )
        return __.Path.home( ) / '.claude'

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


RENDERERS[ 'claude' ] = ClaudeRenderer( )
