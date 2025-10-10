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


from . import __


class AbstractSourceHandler( __.typx.Protocol ):
    ''' Protocol for source handlers that resolve specifications to paths.

        Source handlers provide a pluggable way to resolve different types
        of source specifications (local paths, Git URLs, etc.) to local
        filesystem paths where the content can be accessed.
    '''

    def can_handle( self, source_spec: str ) -> bool:
        ''' Determines whether handler can process source specification. '''
        ...

    def resolve( self, source_spec: str ) -> __.Path:
        ''' Resolves source specification to local filesystem path.

            Returns path to directory containing the resolved source content.
            For remote sources, this may involve downloading or cloning to
            a temporary location.
        '''
        ...


# Private registry of source handlers
_SOURCE_HANDLERS: list[ AbstractSourceHandler ] = [ ]


def register_source_handler( handler: AbstractSourceHandler ) -> None:
    ''' Registers a source handler for use by resolve_source_location.

        Handlers are checked in registration order, so register more
        specific handlers before more general ones.
    '''
    _SOURCE_HANDLERS.append( handler )


def resolve_source_location( source_spec: str ) -> __.Path:
    ''' Resolves data source specification to local filesystem path.

        Delegates to registered source handlers based on source specification
        format. Raises DataSourceNoSupport if no handler can process the
        specification.
    '''
    for handler in _SOURCE_HANDLERS:
        if handler.can_handle( source_spec ):
            return handler.resolve( source_spec )
    raise __.DataSourceNoSupport( source_spec )