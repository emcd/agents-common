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


''' Assert correct behavior of Git source handler parsing and checkout. '''


import dulwich.porcelain as _dulwich_porcelain
import pytest

from . import __


def _create_commit(
    repository: __.Path, content: str, message: bytes
) -> None:
    file_path = repository / 'sample.txt'
    file_path.write_text( content, encoding = 'utf-8' )
    _dulwich_porcelain.add( str( repository ), paths = [ 'sample.txt' ] )
    _dulwich_porcelain.commit(
        str( repository ),
        message = message,
        author = b'Agent <agent@example.com>',
        committer = b'Agent <agent@example.com>',
        sign = False,
    )


def _create_repository_with_tagged_commit( tmp_path: __.Path ) -> __.Path:
    repository = tmp_path / 'origin-repo'
    _dulwich_porcelain.init( str( repository ) )
    _create_commit( repository, 'tagged\n', b'commit-tagged' )
    _dulwich_porcelain.tag_create( str( repository ), 'v1.0.0' )
    _create_commit( repository, 'head\n', b'commit-head' )
    return repository


def test_100_parse_git_url_preserves_ssh_auth_syntax( ):
    module = __.cache_import_module( 'agentsmgr.sources.git' )
    handler = module.GitSourceHandler( )
    location = handler._parse_git_url( 'git@github.com:owner/repo.git' )
    assert location.git_url == 'git@github.com:owner/repo.git'
    assert location.ref is None
    assert location.subdir is None


def test_110_parse_git_url_extracts_ref_for_ssh_suffix( ):
    module = __.cache_import_module( 'agentsmgr.sources.git' )
    handler = module.GitSourceHandler( )
    location = handler._parse_git_url(
        'git@github.com:owner/repo.git@v1.2.3#nested/path' )
    assert location.git_url == 'git@github.com:owner/repo.git'
    assert location.ref == 'v1.2.3'
    assert location.subdir == 'nested/path'


def test_120_parse_git_url_ignores_authority_userinfo_at( ):
    module = __.cache_import_module( 'agentsmgr.sources.git' )
    handler = module.GitSourceHandler( )
    location = handler._parse_git_url(
        'https://git@github.com/owner/repo.git' )
    assert location.git_url == 'https://git@github.com/owner/repo.git'
    assert location.ref is None
    assert location.subdir is None


def test_130_parse_git_url_extracts_ref_for_https_suffix( ):
    module = __.cache_import_module( 'agentsmgr.sources.git' )
    handler = module.GitSourceHandler( )
    location = handler._parse_git_url( 'https://github.com/owner/repo@v2.0.0' )
    assert location.git_url == 'https://github.com/owner/repo.git'
    assert location.ref == 'v2.0.0'
    assert location.subdir is None


def test_140_parse_git_url_rejects_empty_ref_suffix( ):
    module = __.cache_import_module( 'agentsmgr.sources.git' )
    handler = module.GitSourceHandler( )
    source_spec = 'https://github.com/owner/repo@'
    with pytest.raises( module.__.DataSourceNoSupport ) as exc_info:
        handler._parse_git_url( source_spec )
    assert str( exc_info.value ) == (
        "Unsupported source format: "
        "https://github.com/owner/repo@ "
        "(invalid Git source specification: empty ref after '@')"
    )


def test_150_parse_git_url_rejects_empty_subdirectory_fragment( ):
    module = __.cache_import_module( 'agentsmgr.sources.git' )
    handler = module.GitSourceHandler( )
    source_spec = 'https://github.com/owner/repo#'
    with pytest.raises( module.__.DataSourceNoSupport ) as exc_info:
        handler._parse_git_url( source_spec )
    assert str( exc_info.value ) == (
        "Unsupported source format: "
        "https://github.com/owner/repo# "
        "(invalid Git source specification: "
        "empty subdirectory fragment after '#')"
    )


def test_160_parse_git_url_rejects_absolute_subdirectory_fragment( ):
    module = __.cache_import_module( 'agentsmgr.sources.git' )
    handler = module.GitSourceHandler( )
    source_spec = 'https://github.com/owner/repo#/tmp'
    with pytest.raises( module.__.DataSourceNoSupport ) as exc_info:
        handler._parse_git_url( source_spec )
    assert str( exc_info.value ) == (
        "Unsupported source format: "
        "https://github.com/owner/repo#/tmp "
        "(invalid Git source specification: "
        "absolute subdirectory fragments are not allowed)"
    )


def test_170_parse_git_url_rejects_parent_traversal_subdirectory( ):
    module = __.cache_import_module( 'agentsmgr.sources.git' )
    handler = module.GitSourceHandler( )
    source_spec = 'https://github.com/owner/repo#../../outside'
    with pytest.raises( module.__.DataSourceNoSupport ) as exc_info:
        handler._parse_git_url( source_spec )
    assert str( exc_info.value ) == (
        "Unsupported source format: "
        "https://github.com/owner/repo#../../outside "
        "(invalid Git source specification: "
        "parent-path traversal in subdirectory is not allowed)"
    )


def test_180_resolve_source_location_supports_relative_local_paths(
    tmp_path, monkeypatch
):
    sources = __.cache_import_module( 'agentsmgr.sources' )
    defaults_path = tmp_path / 'defaults'
    defaults_path.mkdir( )
    monkeypatch.chdir( tmp_path )
    resolved = sources.resolve_source_location( './defaults' )
    assert resolved == defaults_path.resolve( )


def test_200_standard_clone_checks_out_explicit_ref( tmp_path ):
    module = __.cache_import_module( 'agentsmgr.sources.git' )
    handler = module.GitSourceHandler( )
    repository = _create_repository_with_tagged_commit( tmp_path )
    target = tmp_path / 'clone-explicit'
    location = module.GitLocation(
        git_url = str( repository ), ref = 'v1.0.0' )
    handler._perform_standard_clone( location, target )
    sample_content = ( target / 'sample.txt' ).read_text( encoding = 'utf-8' )
    assert sample_content == 'tagged\n'


def test_210_standard_clone_checks_out_latest_tag_when_ref_absent( tmp_path ):
    module = __.cache_import_module( 'agentsmgr.sources.git' )
    handler = module.GitSourceHandler( )
    repository = _create_repository_with_tagged_commit( tmp_path )
    target = tmp_path / 'clone-latest-tag'
    location = module.GitLocation( git_url = str( repository ) )
    handler._perform_standard_clone( location, target )
    sample_content = ( target / 'sample.txt' ).read_text( encoding = 'utf-8' )
    assert sample_content == 'tagged\n'
