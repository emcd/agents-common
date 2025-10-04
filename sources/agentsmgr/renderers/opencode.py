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
from .base import RENDERERS, RendererBase, TargetingMode


class OpencodeRenderer( RendererBase ):
    ''' Renderer for OpenCode coder. '''

    name = 'opencode'
    modes_available = frozenset( ( 'per-project', ) )

    def resolve_base_directory(
        self,
        mode: TargetingMode,
        target: __.Path,
        configuration: __.cabc.Mapping[ str, __.typx.Any ],
        environment: __.cabc.Mapping[ str, str ],
    ) -> __.Path:
        ''' Resolves base output directory for OpenCode.

            For per-project mode, returns standard project configuration
            path. Per-user mode not yet implemented.
        '''
        self.validate_target_mode( mode )
        if mode == 'per-project':
            return target / ".auxiliary" / "configuration" / "opencode"
        raise __.TargetModeNoSupport( self.name, mode )


RENDERERS[ 'opencode' ] = OpencodeRenderer( )
