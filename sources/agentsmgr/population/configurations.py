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


''' Configuration defaults, coder filtering, and path helpers.
'''


from .. import __
from .. import renderers as _renderers
from .. import resolver as _resolver


_scribe = __.provide_scribe( __name__ )


def _produce_default_configuration(
    location: __.Path,
) -> __.cabc.Mapping[ str, __.typx.Any ]:
    ''' Produces default configuration for generate command.

        Uses all known coders from the renderer registry so that
        fallback content is generated for all coders, not just those
        with direct component content.
    '''
    coders = sorted( _renderers.RENDERERS.keys( ) )
    return { 'coders': coders, 'languages': [ 'python' ] }


SourceArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.tyro.conf.Positional[ str ],
    __.tyro.conf.arg( help = "Data source (local path or git URL)" ),
]


TargetArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.tyro.conf.Positional[ __.Path ],
    __.tyro.conf.arg( help = "Target directory for content generation" ),
]


def _filter_coders_by_mode(
    coders: __.cabc.Sequence[ str ],
    target_mode: _renderers.ExplicitTargetMode,
) -> tuple[ str, ... ]:
    ''' Filters coders by their default targeting mode.

        Returns coders whose mode_default matches the target mode.
        This ensures populate project only handles per-project coders
        and populate user only handles per-user coders, respecting each
        renderer's designed usage pattern.
    '''
    return tuple(
        name
        for name, _renderer in _resolver.resolve_coders(
            coders, mode = target_mode )
    )


def _format_exclude_path( path: __.Path ) -> str:
    ''' Formats a project-relative path for git exclude syntax. '''
    return path.as_posix( )


def _coders_include(
    coders: __.cabc.Sequence[ __.typx.Any ],
    name: str,
) -> bool:
    ''' Reports whether named coder is in a coders selection.

        Supports both plain-name and mapping (``{'name': ...}``) entries.
    '''
    for coder in coders:
        if isinstance( coder, str ) and coder == name: return True
        if isinstance( coder, dict ):
            candidate = __.typx.cast( dict[ str, __.typx.Any ], coder )
            if candidate.get( 'name' ) == name: return True
    return False


def _within_project_root(
    path: __.Path, project_root: __.Path,
) -> bool:
    ''' Reports whether a path resolves inside the project root.

        Guards managed writes against escaping the target through
        symlinked directories: any existing symlink component that
        resolves outside the root fails the check.
    '''
    try:
        resolved = path.resolve( )
        root = project_root.resolve( )
    except OSError:
        return False
    return resolved == root or root in resolved.parents
