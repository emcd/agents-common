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


''' Coder resolution utilities.

    Provides helpers for resolving coder names to their registered
    renderers, with optional mode filtering and unknown-coder warnings.
'''


from . import __
from . import renderers as _renderers


_scribe = __.provide_scribe( __name__ )


def resolve_coders(
    coders: __.cabc.Sequence[ str ],
    mode: __.Absential[ _renderers.ExplicitTargetMode ] = __.absent,
) -> __.typx.Iterator[ tuple[ str, _renderers.RendererBase ] ]:
    ''' Resolves coder names to registered renderers.

        Yields (coder_name, renderer) pairs for known coders. Skips
        unknown coders with a warning. When mode is provided, skips
        coders whose mode_default does not match with a debug message.
    '''
    for coder_name in coders:
        try: renderer = _renderers.RENDERERS[ coder_name ]
        except KeyError:
            _scribe.warning(
                f"Skipping unknown coder: {coder_name}" )
            continue
        if (  not __.is_absent( mode )
              and renderer.mode_default != mode ):
            _scribe.debug(
                f"Skipping {coder_name} for {mode} mode: "
                f"default mode is {renderer.mode_default}" )
            continue
        yield coder_name, renderer
