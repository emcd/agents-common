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


''' Antigravity CLI renderer implementation.

    Provides path resolution and targeting mode validation for Google
    Antigravity CLI (``agy``).

    Antigravity support is deliberately thinner than the other coders:
    Antigravity reads workspace configuration from the shared ``.agents/``
    directory (which populate symlinks to the canonical agents tree), root
    ``AGENTS.md`` for memory, and ``.agents/skills/`` for skills discovery,
    so no per-coder base directory, root dotlink, or memory link is
    required beyond what the shared layout already provides. The renderer
    exists so the ``antigravity`` coder name resolves without warnings
    and participates in per-project population.
'''


from . import __
from .base import RENDERERS as _RENDERERS
from .base import ExplicitTargetMode as _ExplicitTargetMode
from .base import RendererBase as _RendererBase
from .base import extract_coder_configuration as _extract_coder_configuration


class AntigravityRenderer( _RendererBase ):
    ''' Renderer for Antigravity CLI coder.

        Per-project mode only: Antigravity global configuration
        (``~/.gemini/``) is user-owned and seat-managed, not populated.
        Workspace configuration (``mcp_config.json``) is template-rendered
        into the canonical agents tree, which the root ``.agents`` symlink
        exposes; support scripts are populate-managed and git-excluded.
    '''

    name = 'antigravity'
    modes_available = frozenset( ( 'per-project', ) )
    mode_default = 'per-project'
    memory_filename = 'AGENTS.md'
    item_types_available = frozenset( )

    def get_template_flavor( self, item_type: str ) -> str:
        ''' Determines template flavor for Antigravity CLI.

            Antigravity renders no generated content items, so the
            default flavor applies (unused in practice).
        '''
        return 'claude'

    def provide_project_symlinks(
        self, target: __.Path
    ) -> __.cabc.Sequence[ tuple[ __.Path, __.Path ] ]:
        ''' Provides symlinks required for Antigravity CLI.

            None: Antigravity consumes the shared ``.agents`` symlink
            and root ``AGENTS.md`` link, so no ``.antigravity`` root
            link exists (Antigravity reads no such directory).
        '''
        return [ ]

    def resolve_base_directory(
        self,
        mode: _ExplicitTargetMode,
        target: __.Path,
        configuration: __.cabc.Mapping[ str, __.typx.Any ],
        environment: __.cabc.Mapping[ str, str ],
    ) -> __.Path:
        ''' Resolves base output directory for Antigravity CLI.

            Per-project: ``.auxiliary/configuration/coders/antigravity``
            (reserved; no content materializes there under the unified
            canonical-tree layout).
        '''
        self.validate_mode( mode )
        if mode == 'per-project':
            return target / ".auxiliary/configuration/coders/antigravity"
        raise __.TargetModeNoSupport( self.name, mode )

    def _extract_coder_configuration(
        self, configuration: __.cabc.Mapping[ str, __.typx.Any ]
    ) -> __.cabc.Mapping[ str, __.typx.Any ]:
        ''' Extracts configuration for this specific coder.

            Looks for coder entry in configuration coders array by name.
        '''
        return _extract_coder_configuration( configuration, self.name )


_RENDERERS[ 'antigravity' ] = AntigravityRenderer( )
