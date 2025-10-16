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


''' Qwen Code renderer implementation.

    Provides path resolution and targeting mode validation for Qwen Code,
    which supports both per-user and per-project configuration.
'''


from . import __
from . import base as _base


class QwenRenderer( _base.RendererBase ):
    ''' Renderer for Qwen Code coder.

        Supports both per-user and per-project configuration modes.
        Per-user mode defaults to ~/.qwen/ with configuration file
        override support via directory field in coder config.
    '''

    name = 'qwen'
    modes_available = frozenset( ( 'per-user', 'per-project' ) )
    mode_default = 'per-project'
    memory_filename = 'QWEN.md'

    def get_template_flavor( self, item_type: str ) -> str:
        ''' Determines template flavor for Qwen Code.

            Qwen shares markdown command format with Claude/Gemini
            (via gemini.toml.jinja for TOML) but uses own agent format
            with YAML frontmatter, so returns 'gemini' for commands
            and 'qwen' for agents.
        '''
        if item_type == 'commands':
            return 'gemini'
        return 'qwen'

    def resolve_base_directory(
        self,
        mode: _base.ExplicitTargetMode,
        target: __.Path,
        configuration: __.cabc.Mapping[ str, __.typx.Any ],
        environment: __.cabc.Mapping[ str, str ],
    ) -> __.Path:
        ''' Resolves base output directory for Qwen Code.

            Per-project: .auxiliary/configuration/coders/qwen/
            Per-user: ~/.qwen/ with configuration file overrides.
        '''
        self.validate_mode( mode )
        if mode == 'per-project':
            return target / ".auxiliary/configuration/coders/qwen"
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
            1. Configuration file override (directory field for this coder)
            2. Default ~/.qwen/ location

            Note: Qwen does not provide environment variable override
            for user config path (unlike Claude's CLAUDE_CONFIG_DIR).
        '''
        coder_configuration = self._extract_coder_configuration(
            configuration )
        if 'directory' in coder_configuration:
            directory = __.Path( coder_configuration[ 'directory' ] )
            return directory.expanduser( )
        return __.Path.home( ) / '.qwen'

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


_base.RENDERERS[ 'qwen' ] = QwenRenderer( )
