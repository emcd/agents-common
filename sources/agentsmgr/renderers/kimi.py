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


''' Kimi CLI renderer implementation.

    Provides path resolution and targeting mode validation for Kimi CLI.
    Kimi CLI only supports per-user configuration via ~/.kimi/config.toml.
'''


from . import __
from .base import RENDERERS as _RENDERERS
from .base import ExplicitTargetMode as _ExplicitTargetMode
from .base import RendererBase as _RendererBase


class KimiRenderer( _RendererBase ):
    ''' Renderer for Kimi CLI coder.

        Only supports per-user configuration mode. Kimi CLI stores its
        configuration in ~/.kimi/config.toml (TOML format). Per-user mode
        returns the ~/.kimi directory path.
    '''

    name = 'kimi'
    modes_available = frozenset( ( 'per-user', ) )
    mode_default = 'per-user'
    # Note: Kimi CLI reads AGENTS.md via ${KIMI_AGENTS_MD} template variable.
    # There is no separate KIMI.md memory file.
    memory_filename = 'AGENTS.md'

    def calculate_directory_location( self, item_type: str ) -> str:
        ''' Returns directory name for item type.

            Kimi does not support custom commands or agents in the same
            way as Claude. Skills are stored in ~/.kimi/skills/ as
            separate SKILL.md files with YAML frontmatter.

            Returns empty string to indicate no directory (items not
            supported for Kimi).
        '''
        return ''

    def get_template_flavor( self, item_type: str ) -> str:
        ''' Determines template flavor for Kimi CLI.

            Kimi does not support the same command/agent format as Claude.
            Returns empty string to indicate no template flavor.
        '''
        return ''

    def provide_project_symlinks(
        self, target: __.Path
    ) -> __.cabc.Sequence[ tuple[ __.Path, __.Path ] ]:
        ''' Provides symlinks required for Kimi CLI in per-project mode.

            Kimi does not support per-project mode, so this method
            returns empty sequence. Only per-user mode is supported.
        '''
        return [ ]

    def resolve_base_directory(
        self,
        mode: _ExplicitTargetMode,
        target: __.Path,
        configuration: __.cabc.Mapping[ str, __.typx.Any ],
        environment: __.cabc.Mapping[ str, str ],
    ) -> __.Path:
        ''' Resolves base output directory for Kimi CLI.

            Only per-user mode is supported. Returns the ~/.kimi directory
            path. Note that Kimi CLI uses a single config.toml file in this
            directory, not multiple files. Per-project mode raises error.
        '''
        self.validate_mode( mode )
        if mode == 'per-user':
            return self._resolve_user_directory( configuration, environment )
        reason = (
            "Kimi CLI does not support per-project configuration. "
            "Only per-user configuration in ~/.kimi/config.toml "
            "is supported." )
        raise __.TargetModeNoSupport( self.name, mode, reason )

    def _resolve_user_directory(
        self,
        configuration: __.cabc.Mapping[ str, __.typx.Any ],
        environment: __.cabc.Mapping[ str, str ],
    ) -> __.Path:
        ''' Resolves per-user directory following precedence rules.

            Kimi CLI does not have an environment variable for config
            directory location. Always returns ~/.kimi.

            Precedence order:
            1. Configuration file override (directory key for this coder)
            2. Default ~/.kimi location
        '''
        coder_configuration = self._extract_coder_configuration(
            configuration )
        if 'directory' in coder_configuration:
            directory = __.Path( coder_configuration[ 'directory' ] )
            return directory.expanduser( )
        return __.Path.home( ) / '.kimi'

    def _extract_coder_configuration(
        self, configuration: __.cabc.Mapping[ str, __.typx.Any ]
    ) -> __.cabc.Mapping[ str, __.typx.Any ]:
        ''' Extracts configuration for this specific coder.

            Looks for coder entry in configuration coders array by name.
        '''
        coders = configuration.get( 'coders', ( ) )
        for coder in coders:  # type: ignore[various]
            if coder.get( 'name' ) == self.name:
                return coder
        return { }


_RENDERERS[ 'kimi' ] = KimiRenderer( )
