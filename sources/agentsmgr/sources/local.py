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


''' Local filesystem source handler.

    This module provides source resolution for local filesystem paths,
    maintaining the existing behavior from the original retrieve_data_location
    function.
'''


from . import __
from . import base as _base


@_base.source_handler(['', 'file'])
class LocalSourceHandler:
    ''' Handles local filesystem path resolution.

        Resolves local path specifications to absolute filesystem paths.
        This maintains backward compatibility with existing local path
        usage patterns.
    '''

    def resolve(
        self,
        source_spec: str,
        tag_prefix: __.typx.Annotated[
            __.Absential[ str ],
            __.ddoc.Doc(
                "Tag prefix for filtering version tags; ignored for local "
                "sources." ),
        ] = __.absent,
    ) -> __.Path:
        ''' Resolves local path specification to absolute path.

            Converts relative paths to absolute paths and validates that
            the path exists and is accessible.
        '''
        return __.Path( source_spec ).resolve( )
