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
from .base import RENDERERS, RendererBase, TargetingMode


class CodexRenderer( RendererBase ):
    ''' Renderer for Codex CLI coder.

        Codex CLI does not support per-project configuration as of
        version 0.44.0.
    '''

    name = 'codex'
    modes_available = frozenset( ( 'per-project', ) )

    def resolve_base_directory(
        self,
        mode: TargetingMode,
        target: __.Path,
        configuration: __.cabc.Mapping[ str, __.typx.Any ],
        environment: __.cabc.Mapping[ str, str ],
    ) -> __.Path:
        ''' Resolves base output directory for Codex CLI.

            Uses per-project path structure for consistency, even though
            Codex does not fully support it. Per-user mode will provide
            proper Codex support.
        '''
        self.validate_target_mode( mode )
        if mode == 'per-project':
            return target / ".auxiliary" / "configuration" / "codex"
        raise __.TargetModeNoSupport( self.name, mode )


RENDERERS[ 'codex' ] = CodexRenderer( )
