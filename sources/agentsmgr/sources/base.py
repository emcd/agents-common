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


''' Base abstractions for source handlers.

    This module provides the foundational protocols and functions for
    resolving various types of data sources to local filesystem paths.
'''


from .. import nomina as _nomina
from . import __


class AbstractSourceHandler( __.immut.Protocol, __.typx.Protocol ):
    ''' Protocol for source handlers that resolve specifications to paths.

        Source handlers provide a pluggable way to resolve different types
        of source specifications (local paths, Git URLs, etc.) to local
        filesystem paths where the content can be accessed.
    '''

    @__.abc.abstractmethod
    def resolve(
        self,
        source_spec: str,
        tag_prefix: _nomina.TagPrefixArgument = __.absent,
    ) -> __.Path:
        ''' Resolves source specification to local filesystem path.

            Returns path to directory containing the resolved source content.
            For remote sources, this may involve downloading or cloning to
            a temporary location.
        '''
        raise NotImplementedError


# Private registry mapping URL schemes to source handlers
_SCHEME_HANDLERS: __.accret.Dictionary[ str, AbstractSourceHandler ] = (
    __.accret.Dictionary( ) )


def register_source_handler(
    handler: __.typx.Annotated[
        AbstractSourceHandler,
        __.ddoc.Doc( ''' The source handler instance ''' )
    ],
    schemes: __.typx.Annotated[
        __.cabc.Iterable[ str ],
        __.ddoc.Doc( ''' URL schemes this handler supports
            (e.g., ['github:', 'gitlab:']) ''' )
    ]
) -> None:
    ''' Registers a source handler for specific URL schemes. '''
    for scheme in schemes:
        _SCHEME_HANDLERS[ scheme ] = handler


def source_handler(
    schemes: __.typx.Annotated[
        __.cabc.Iterable[ str ],
        __.ddoc.Doc( ''' URL schemes this handler supports
            (e.g., ['github:', 'gitlab:']) ''' )
    ]
) -> __.cabc.Callable[
    [ type[ AbstractSourceHandler ] ], type[ AbstractSourceHandler ]
]:
    ''' Decorator for automatic source handler registration.

        Usage:
            @source_handler(['github:', 'gitlab:'])
            class GitSourceHandler:
                ...
    '''
    def decorator(
        handler_class: type[ AbstractSourceHandler ]
    ) -> type[ AbstractSourceHandler ]:
        register_source_handler( handler_class( ), schemes )
        return handler_class
    return decorator


def resolve_source_location(
    source_spec: str,
    tag_prefix: _nomina.TagPrefixArgument = __.absent,
) -> __.Path:
    ''' Resolves data source specification to local filesystem path.

        Delegates to registered source handlers based on URL scheme.
        Uses urlparse to extract the scheme from the specification.

        Raises DataSourceNoSupport if no handler can process the specification.
    '''
    if source_spec.startswith( 'git@' ):
        if 'git@' in _SCHEME_HANDLERS:
            return _SCHEME_HANDLERS[ 'git@' ].resolve(
                source_spec, tag_prefix )
        raise __.DataSourceNoSupport( source_spec )
    parsed = __.urlparse.urlparse( source_spec )
    if parsed.scheme in _SCHEME_HANDLERS:
        return _SCHEME_HANDLERS[ parsed.scheme ].resolve(
            source_spec, tag_prefix )
    raise __.DataSourceNoSupport( source_spec )