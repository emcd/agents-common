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


GitApiTag: __.typx.TypeAlias = __.cabc.Mapping[ str, __.typx.Any ]


_scribe = __.provide_scribe( __name__ )


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
    'github', 'gitlab', 'git+https', 'https', 'git@'
])
class GitSourceHandler:
    ''' Handles Git repository source resolution with Dulwich.

        Supports multiple URL schemes and converts them to Git URLs for
        cloning. Implements fragment syntax for subdirectory specification.
    '''

    def resolve(
        self,
        source_spec: str,
        tag_prefix: __.typx.Annotated[
            __.Absential[ str ],
            __.ddoc.Doc(
                "Prefix for filtering version tags when no explicit ref "
                "is specified. Only tags starting with this prefix will be "
                "considered, and the prefix will be stripped before version "
                "parsing." ),
        ] = __.absent,
    ) -> __.Path:
        ''' Resolves Git source to local temporary directory.

            Clones the repository to a temporary location and returns the
            path to the specified subdirectory or repository root.
        '''
        location = self._parse_git_url( source_spec )
        temp_dir = self._create_temp_directory( )
        try:
            self._clone_repository( location, temp_dir, tag_prefix )
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
        self,
        location: GitLocation,
        target_dir: __.Path,
        tag_prefix: __.Absential[ str ] = __.absent,
    ) -> None:
        ''' Clones Git repository using Dulwich with optimizations.

            For GitHub/GitLab repositories without explicit ref, attempts
            API-based tag resolution followed by shallow clone. Falls back
            to standard full clone on any failure.
        '''
        try:
            if location.ref is None:
                cloned = self._attempt_optimized_clone(
                    location, target_dir, tag_prefix )
                if cloned: return
            self._perform_standard_clone( location, target_dir, tag_prefix )
        except Exception as exception:
            error_msg = str( exception ).lower( )
            if location.ref is not None and (
                'not found' in error_msg or 'does not exist' in error_msg
            ):
                raise GitRefAbsence(
                    location.ref, location.git_url ) from exception
            raise GitCloneFailure(
                location.git_url, str( exception ) ) from exception

    def _attempt_optimized_clone(
        self,
        location: GitLocation,
        target_dir: __.Path,
        tag_prefix: __.Absential[ str ] = __.absent,
    ) -> bool:
        ''' Attempts optimized clone using API and shallow clone.

            Returns True if successful, False if optimization should fall
            back to standard clone.
        '''
        latest_tag = self._resolve_latest_tag_via_api(
            location.git_url, tag_prefix )
        if latest_tag is None: return False
        _scribe.info(
            f"Resolved latest tag '{latest_tag}' via API for repository: "
            f"{location.git_url}" )
        try:
            self._perform_shallow_clone(
                location.git_url, target_dir, latest_tag )
        except Exception:
            _scribe.info(
                f"Shallow clone failed, falling back to standard clone for "
                f"repository: {location.git_url}" )
            return False
        else:
            _scribe.info(
                f"Performed shallow clone for tag '{latest_tag}' in "
                f"repository: {location.git_url}" )
            return True

    def _perform_shallow_clone(
        self, git_url: str, target_dir: __.Path, ref: str
    ) -> None:
        ''' Performs shallow clone of specific ref using Dulwich.

            Uses depth=1 and branch parameters for efficient cloning.
        '''
        with open( __.os.devnull, 'wb' ) as devnull:
            _dulwich_porcelain.clone(
                git_url,
                str( target_dir ),
                bare = False,
                depth = 1,
                branch = ref.encode( ),
                errstream = devnull,
            )

    def _perform_standard_clone(
        self,
        location: GitLocation,
        target_dir: __.Path,
        tag_prefix: __.Absential[ str ] = __.absent,
    ) -> None:
        ''' Performs standard full clone with optional ref checkout.

            This is the fallback path for repositories that cannot use
            API optimization or when explicit ref is provided.
        '''
        with open( __.os.devnull, 'wb' ) as devnull:
            _dulwich_porcelain.clone(
                location.git_url,
                str( target_dir ),
                bare = False,
                depth = None,
                errstream = devnull,
            )
        if location.ref is None:
            latest_tag = self._get_latest_tag( target_dir, tag_prefix )
            if latest_tag:
                _scribe.info(
                    f"Selected latest tag '{latest_tag}' for repository: "
                    f"{location.git_url}" )
                self._checkout_ref( target_dir, latest_tag )
            else:
                _scribe.info(
                    f"No version tags found, using default branch for "
                    f"repository: {location.git_url}" )
        else:
            _scribe.info(
                f"Using explicit ref '{location.ref}' for repository: "
                f"{location.git_url}" )
            self._checkout_ref( target_dir, location.ref )

    def _extract_version(
        self,
        tag_name: str,
        prefix: __.Absential[ str ] = __.absent,
    ) -> __.typx.Optional[ __.Version ]:
        ''' Extracts and parses semantic version from tag name.

            If prefix is provided, only processes tags that start with the
            prefix and strips it before parsing. If prefix is absent, tries
            parsing the tag name directly. Returns None if tag cannot be
            parsed as a valid semantic version.
        '''
        version_string = tag_name
        if not __.is_absent( prefix ):
            if not tag_name.startswith( prefix ):
                return None
            version_string = tag_name[ len( prefix ): ]
        try:
            return __.Version( version_string )
        except __.InvalidVersion:
            return None

    def _get_latest_tag(
        self,
        repo_dir: __.Path,
        tag_prefix: __.Absential[ str ] = __.absent,
    ) -> __.typx.Optional[ str ]:
        ''' Gets the latest tag from the repository by semantic version.

            Optionally filters tags by prefix before selecting latest.
            Uses packaging.version.Version for semantic comparison. If no
            tags can be parsed as versions, returns None (falls back to
            default branch).
        '''
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
        versioned_tags: list[ tuple[ __.Version, str ] ] = [ ]
        for tag_name_bytes, commit_sha in tag_refs.items( ):
            commit = self._get_tag_commit( repo, commit_sha )
            if commit is not None:
                tag_name = tag_name_bytes.decode( 'utf-8' )
                version = self._extract_version( tag_name, tag_prefix )
                if version is not None:
                    versioned_tags.append( ( version, tag_name ) )
        if versioned_tags:
            versioned_tags.sort( reverse = True )
            return versioned_tags[ 0 ][ 1 ]
        return None

    def _get_tag_commit(
        self, repo: __.typx.Any, commit_sha: bytes
    ) -> __.typx.Any:
        ''' Gets commit object for a tag, handling annotated tags. '''
        try:
            commit = repo[ commit_sha ]
            while hasattr( commit, 'object' ):
                # object attribute is a tuple (class, sha)
                commit = repo[ commit.object[ 1 ] ]
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

    def _detect_git_host( self, git_url: str ) -> __.typx.Optional[ str ]:
        ''' Detects Git hosting provider from URL.

            Returns 'github', 'gitlab', or None for other providers.
        '''
        if git_url.startswith( 'git@' ):
            parts = git_url.split( '@', 1 )
            if len( parts ) > 1:
                host_part = parts[ 1 ].split( ':', 1 )[ 0 ]
                if 'github.com' in host_part: return 'github'
                if 'gitlab.com' in host_part: return 'gitlab'
        else:
            parsed = __.urlparse.urlparse( git_url )
            hostname = parsed.netloc.lower( )
            if 'github.com' in hostname: return 'github'
            if 'gitlab.com' in hostname: return 'gitlab'
        return None

    def _acquire_github_authentication_token(
        self
    ) -> __.typx.Optional[ str ]:
        ''' Acquires GitHub authentication token from environment or gh CLI.

            Checks GITHUB_TOKEN environment variable first, then attempts
            to retrieve token from gh CLI. Returns None if neither source
            is available.
        '''
        token = __.os.environ.get( 'GITHUB_TOKEN' )
        if token: return token
        try:
            result = __.subprocess.run(
                [ 'gh', 'auth', 'token' ],
                capture_output = True,
                text = True,
                timeout = 5,
                check = False )
            if result.returncode == 0:
                return result.stdout.strip( )
        except ( FileNotFoundError, __.subprocess.TimeoutExpired ):
            pass
        return None

    def _acquire_gitlab_authentication_token(
        self
    ) -> __.typx.Optional[ str ]:
        ''' Acquires GitLab authentication token from environment.

            Checks GITLAB_TOKEN environment variable. Returns None if not
            available.
        '''
        return __.os.environ.get( 'GITLAB_TOKEN' )

    def _retrieve_github_tags(
        self, owner: str, repository: str
    ) -> __.typx.Optional[ list[ GitApiTag ] ]:
        ''' Retrieves tags from GitHub API.

            Returns list of tag dictionaries or None on failure. Each tag
            contains 'name' and 'commit' fields.
        '''
        token = self._acquire_github_authentication_token( )
        url = f"https://api.github.com/repos/{owner}/{repository}/tags"
        request = __.urlreq.Request( url )
        if token:
            request.add_header( 'Authorization', f"token {token}" )
        request.add_header( 'Accept', 'application/vnd.github.v3+json' )
        try:
            with __.urlreq.urlopen( request, timeout = 10 ) as response:
                return __.json.loads( response.read( ) )
        except ( __.urlerr.URLError, __.urlerr.HTTPError, Exception ):
            return None

    def _retrieve_gitlab_tags(
        self, owner: str, repository: str
    ) -> __.typx.Optional[ list[ GitApiTag ] ]:
        ''' Retrieves tags from GitLab API.

            Returns list of tag dictionaries or None on failure. Each tag
            contains 'name' and 'commit' fields.
        '''
        token = self._acquire_gitlab_authentication_token( )
        project_path = f"{owner}%2F{repository}"
        url = (
            f"https://gitlab.com/api/v4/projects/{project_path}/"
            f"repository/tags" )
        request = __.urlreq.Request( url )
        if token:
            request.add_header( 'PRIVATE-TOKEN', token )
        try:
            with __.urlreq.urlopen( request, timeout = 10 ) as response:
                return __.json.loads( response.read( ) )
        except ( __.urlerr.URLError, __.urlerr.HTTPError, Exception ):
            return None

    def _extract_repository_information(
        self, git_url: str
    ) -> __.typx.Optional[ tuple[ str, str ] ]:
        ''' Extracts owner and repository name from Git URL.

            Returns tuple of (owner, repository) or None if URL format is
            not recognized. Handles both SSH (git@host:owner/repo) and
            HTTPS (https://host/owner/repo) formats.
        '''
        host = self._detect_git_host( git_url )
        if host is None: return None
        path = None
        if git_url.startswith( 'git@' ):
            parts = git_url.split( ':', maxsplit = 1 )
            path = parts[ 1 ] if len( parts ) > 1 else None
        else:
            parsed = __.urlparse.urlparse( git_url )
            path = parsed.path.lstrip( '/' )
        if path is None: return None
        path = path.removesuffix( '.git' )
        path_parts = path.split( '/', maxsplit = 1 )
        if len( path_parts ) > 1:
            return ( path_parts[ 0 ], path_parts[ 1 ] )
        return None

    def _select_latest_tag_from_api(
        self,
        tags: list[ GitApiTag ],
        tag_prefix: __.Absential[ str ] = __.absent,
    ) -> __.typx.Optional[ str ]:
        ''' Selects latest tag from API results by semantic version.

            Filters by tag prefix if provided, then selects tag with
            highest semantic version. Returns None if no valid version
            tags are found.
        '''
        versioned_tags: list[ tuple[ __.Version, str ] ] = [ ]
        for tag in tags:
            tag_name = tag[ 'name' ]
            version = self._extract_version( tag_name, tag_prefix )
            if version is not None:
                versioned_tags.append( ( version, tag_name ) )
        if versioned_tags:
            versioned_tags.sort( reverse = True )
            return versioned_tags[ 0 ][ 1 ]
        return None

    def _resolve_latest_tag_via_api(
        self,
        git_url: str,
        tag_prefix: __.Absential[ str ] = __.absent,
    ) -> __.typx.Optional[ str ]:
        ''' Resolves latest tag using GitHub or GitLab API.

            Returns tag name or None if API resolution fails or is not
            applicable.
        '''
        host = self._detect_git_host( git_url )
        if host is None: return None
        repo_info = self._extract_repository_information( git_url )
        if repo_info is None: return None
        owner, repository = repo_info
        if host == 'github':
            tags = self._retrieve_github_tags( owner, repository )
        elif host == 'gitlab':
            tags = self._retrieve_gitlab_tags( owner, repository )
        else:
            return None
        if tags is None: return None
        return self._select_latest_tag_from_api( tags, tag_prefix )
