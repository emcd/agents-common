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
from . import base as _base


class GitLocation( __.immut.DataclassObject ):
    ''' Git source location with URL, optional ref, and optional subdir. '''
    git_url: str
    ref: __.typx.Optional[ str ] = None
    subdir: __.typx.Optional[ str ] = None


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


class GitRefAbsence( __.DataSourceNoSupport ):
    ''' Git reference absence in repository. '''

    def __init__( self, ref: str, git_url: str ):
        self.ref = ref
        self.git_url = git_url
        message = f"Git ref '{ref}' not found in repository: {git_url}"
        super( ).__init__( message )


@_base.source_handler([
    'github:', 'gitlab:', 'git+https:',
    'https://github.com/', 'https://gitlab.com/', 'git@'
])
class GitSourceHandler:
    ''' Handles Git repository source resolution with Dulwich.

        Supports multiple URL schemes and converts them to Git URLs for
        cloning. Implements fragment syntax for subdirectory specification.
    '''

    def resolve( self, source_spec: str ) -> __.Path:
        ''' Resolves Git source to local temporary directory.

            Clones the repository to a temporary location and returns the
            path to the specified subdirectory or repository root.
        '''
        location = self._parse_git_url( source_spec )
        temp_dir = self._create_temp_directory( )
        try:
            self._clone_repository( location, temp_dir )
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
        ''' Parses source specification into Git URL, ref, and subdirectory.

            Supports URL scheme mapping and fragment syntax for subdirectory
            specification. Also supports @ref syntax for Git references.
        '''
        url_part = source_spec
        ref = None
        subdir = None
        if '#' in url_part:
            url_part, subdir = url_part.split( '#', 1 )
        if '@' in url_part:
            url_part, ref = url_part.split( '@', 1 )
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

        return GitLocation( git_url = git_url, ref = ref, subdir = subdir )

    def _create_temp_directory( self ) -> __.Path:
        ''' Creates temporary directory for repository cloning. '''
        temp_dir = __.tempfile.mkdtemp( prefix = 'agentsmgr-git-' )
        return __.Path( temp_dir )

    def _clone_repository(
        self, location: GitLocation, target_dir: __.Path
    ) -> None:
        ''' Clones Git repository using Dulwich.

            Performs shallow clone for default branch or full clone for refs,
            then checks out the specified reference if provided.
        '''
        try:
            _dulwich_porcelain.clone(
                location.git_url,
                str( target_dir ),
                bare = False,
                depth = None,
            )
            if location.ref is None:
                latest_tag = self._get_latest_tag( target_dir )
                if latest_tag:
                    self._checkout_ref( target_dir, latest_tag )
            else:
                # Checkout specified ref
                self._checkout_ref( target_dir, location.ref )
        except Exception as exception:
            error_msg = str( exception ).lower( )
            if location.ref is not None and (
                'not found' in error_msg or 'does not exist' in error_msg
            ):
                raise GitRefAbsence(
                    location.ref, location.git_url ) from exception
            raise GitCloneFailure(
                location.git_url, str( exception ) ) from exception

    def _get_latest_tag( self, repo_dir: __.Path ) -> __.typx.Optional[ str ]:
        ''' Gets the latest tag from the repository by commit date. '''
        from dulwich.repo import Repo
        try:
            repo = Repo( str( repo_dir ) )
        except Exception:
            return None
        try:
            tag_refs = repo.refs.as_dict( b"refs/tags" )
        except Exception:
            return None
        if not tag_refs:
            return None
        tag_times: list[ tuple[ int, str ] ] = [ ]
        for tag_name_bytes, commit_sha in tag_refs.items( ):
            commit = self._get_tag_commit( repo, commit_sha )
            if commit is not None:
                tag_name = tag_name_bytes.decode( 'utf-8' )
                tag_times.append( ( commit.commit_time, tag_name ) )
        if not tag_times:
            return None
        tag_times.sort( reverse = True )
        return tag_times[ 0 ][ 1 ]

    def _get_tag_commit(
        self, repo: __.typx.Any, commit_sha: bytes
    ) -> __.typx.Any:
        ''' Gets commit object for a tag, handling annotated tags. '''
        try:
            commit = repo[ commit_sha ]
            while hasattr( commit, 'object' ):
                commit = repo[ commit.object ]
        except Exception:
            return None
        else:
            return commit

    def _checkout_ref( self, repo_dir: __.Path, ref: str ) -> None:
        ''' Checks out a specific reference by cloning with branch param. '''
        from dulwich.repo import Repo
        try:
            repo = Repo( str( repo_dir ) )
        except Exception as exception:
            raise GitRefAbsence( ref, str( repo_dir ) ) from exception
        ref_bytes = ref.encode( )
        tag_ref = f"refs/tags/{ref}".encode( )
        branch_ref = f"refs/heads/{ref}".encode( )
        if tag_ref in repo.refs or branch_ref in repo.refs:
            return
        try:
            repo[ ref_bytes ]
        except KeyError:
            self._raise_ref_not_found( ref, str( repo_dir ) )

    def _raise_ref_not_found( self, ref: str, repo_dir: str ) -> None:
        ''' Raises GitRefAbsence for invalid reference. '''
        raise GitRefAbsence( ref, repo_dir )

    def _raise_subdir_not_found( self, subdir: str, source_spec: str ) -> None:
        ''' Raises GitSubdirectoryAbsence for missing subdirectory. '''
        raise GitSubdirectoryAbsence( subdir, source_spec )
