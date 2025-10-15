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


''' Codex CLI renderer implementation.

    Provides path resolution and targeting mode validation for Codex CLI.
    Codex CLI only supports per-user configuration as of version 0.44.0.
'''


from . import __
from .base import RENDERERS, ExplicitTargetMode, RendererBase


class CodexRenderer( RendererBase ):
    ''' Renderer for Codex CLI coder.

        Only supports per-user configuration mode. Codex CLI does not
        support per-project configuration as of version 0.44.0. Per-user
        mode respects CODEX_HOME environment variable with fallback to
        configuration overrides and default location.
    '''

    name = 'codex'
    modes_available = frozenset( ( 'per-user', ) )
    mode_default = 'per-user'
    memory_filename = 'AGENTS.md'

    def get_template_flavor( self, item_type: str ) -> str:
        ''' Determines template flavor for Codex CLI.

            Codex uses same markdown format as Claude for all item types,
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
        ''' Resolves base output directory for Codex CLI.

            Only per-user mode is supported. Respects precedence: CODEX_HOME
            environment variable, configuration file override (home key), or
            default ~/.codex location. Per-project mode raises error with
            explanation of Codex CLI limitation.
        '''
        self.validate_mode( mode )
        if mode == 'per-user':
            return self._resolve_user_directory( configuration, environment )
        reason = (
            "Codex CLI does not support per-project configuration. "
            "Only per-user configuration in ~/.codex or $CODEX_HOME "
            "is supported as of version 0.44.0." )
        raise __.TargetModeNoSupport( self.name, mode, reason )

    def _resolve_user_directory(
        self,
        configuration: __.cabc.Mapping[ str, __.typx.Any ],
        environment: __.cabc.Mapping[ str, str ],
    ) -> __.Path:
        ''' Resolves per-user directory following precedence rules.

            Precedence order:
            1. CODEX_HOME environment variable
            2. Configuration file override (home key for this coder)
            3. Default ~/.codex location
        '''
        if 'CODEX_HOME' in environment:
            directory = __.Path( environment[ 'CODEX_HOME' ] )
            return directory.expanduser( )
        coder_configuration = self._extract_coder_configuration(
            configuration )
        if 'home' in coder_configuration:
            directory = __.Path( coder_configuration[ 'home' ] )
            return directory.expanduser( )
        return __.Path.home( ) / '.codex'

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


RENDERERS[ 'codex' ] = CodexRenderer( )
