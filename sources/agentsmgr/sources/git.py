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


''' Git-based source handler with Dulwich.

    This module provides source resolution for Git repositories, supporting
    various URL schemes and subdirectory specifications via fragment syntax.
'''


import dulwich.porcelain as _dulwich_porcelain

from . import __


# Type aliases for Git source components
class GitLocation( __.typx.NamedTuple ):
    ''' Git source location with URL and optional subdirectory. '''
    git_url: str
    subdir: __.typx.Optional[ str ]


class GitCloneFailure( __.Omnierror, OSError ):
    ''' Git repository cloning operation failure. '''

    def __init__( self, git_url: str, reason: str = '' ):
        self.git_url = git_url
        self.reason = reason
        message = f"Failed to clone Git repository: {git_url}"
        if reason: message = f"{message} ({reason})"
        super( ).__init__( message )


class GitSubdirectoryAbsence( __.DataSourceNoSupport ):
    ''' Git repository subdirectory absence. '''

    def __init__( self, subdir: str, source_spec: str ):
        self.subdir = subdir
        self.source_spec = source_spec
        message = (
            f"Subdirectory '{subdir}' not found in repository: {source_spec}" )
        super( ).__init__( message )


class GitSourceHandler:
    ''' Handles Git repository source resolution with Dulwich.

        Supports multiple URL schemes and converts them to Git URLs for
        cloning. Implements fragment syntax for subdirectory specification.
    '''

    def can_handle( self, source_spec: str ) -> bool:
        ''' Determines whether source specification is a Git URL.

            Supports github:, git+https:, and full https://github.com URLs.
        '''
        return source_spec.startswith( (
            'github:', 'gitlab:', 'git+https:', 'https://github.com/',
            'https://gitlab.com/', 'git@'
        ) )

    def resolve( self, source_spec: str ) -> __.Path:
        ''' Resolves Git source to local temporary directory.

            Clones the repository to a temporary location and returns the
            path to the specified subdirectory or repository root.
        '''
        location = self._parse_git_url( source_spec )
        temp_dir = self._create_temp_directory( )
        try:
            self._clone_repository( location.git_url, temp_dir )
            if location.subdir:
                subdir_path = temp_dir / location.subdir
                if not subdir_path.exists( ):
                    self._raise_subdir_not_found(
                        location.subdir, source_spec )
                result_path = subdir_path
            else:
                result_path = temp_dir
        except Exception as exception:
            # Clean up on failure
            __.shutil.rmtree( temp_dir, ignore_errors = True )
            if isinstance( exception, __.DataSourceNoSupport ):
                raise
            raise GitCloneFailure(
                location.git_url, str( exception ) ) from exception
        else:
            return result_path

    def _parse_git_url( self, source_spec: str ) -> GitLocation:
        ''' Parses source specification into Git URL and subdirectory.

            Supports URL scheme mapping and fragment syntax for subdirectory
            specification.
        '''
        # Extract fragment (subdirectory) if present
        if '#' in source_spec:
            url_part, subdir = source_spec.split( '#', 1 )
        else:
            url_part, subdir = source_spec, None

        # Map URL schemes to Git URLs
        if url_part.startswith( 'github:' ):
            repo_path = url_part[ len( 'github:' ): ]
            git_url = f"https://github.com/{repo_path}.git"
        elif url_part.startswith( 'gitlab:' ):
            repo_path = url_part[ len( 'gitlab:' ): ]
            git_url = f"https://gitlab.com/{repo_path}.git"
        elif url_part.startswith( 'git+https:' ):
            git_url = url_part[ len( 'git+' ): ]
        elif url_part.startswith( 'https://github.com/' ):
            # Convert GitHub web URLs to Git URLs
            if url_part.endswith( '.git' ):
                git_url = url_part
            else:
                git_url = f"{url_part.rstrip( '/' )}.git"
        elif url_part.startswith( 'https://gitlab.com/' ):
            # Convert GitLab web URLs to Git URLs
            if url_part.endswith( '.git' ):
                git_url = url_part
            else:
                git_url = f"{url_part.rstrip( '/' )}.git"
        else:
            # Direct git URLs (git@github.com:user/repo.git)
            git_url = url_part

        return GitLocation( git_url = git_url, subdir = subdir )

    def _create_temp_directory( self ) -> __.Path:
        ''' Creates temporary directory for repository cloning. '''
        temp_dir = __.tempfile.mkdtemp( prefix = 'agentsmgr-git-' )
        return __.Path( temp_dir )

    def _clone_repository( self, git_url: str, target_dir: __.Path ) -> None:
        ''' Clones Git repository using Dulwich.

            Performs shallow clone for efficiency with depth=1.
        '''
        try:
            _dulwich_porcelain.clone(
                git_url,
                str( target_dir ),
                bare = False,
                depth = 1,  # Shallow clone for efficiency
            )
        except Exception as exception:
            raise GitCloneFailure( git_url, str( exception ) ) from exception

    def _raise_subdir_not_found( self, subdir: str, source_spec: str ) -> None:
        ''' Raises GitSubdirectoryAbsence for missing subdirectory. '''
        raise GitSubdirectoryAbsence( subdir, source_spec )