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


''' Assert correct behavior of coder renderers. '''


import pytest

from . import __


def test_020_codex_renderer_supports_per_project( tmp_path ):
    renderers = __.cache_import_module( 'agentsmgr.renderers' )
    renderer = renderers.RENDERERS[ 'codex' ]
    assert renderer.mode_default == 'per-project'
    assert 'per-project' in renderer.modes_available
    assert 'per-user' in renderer.modes_available
    base = renderer.resolve_base_directory(
        mode = 'per-project',
        target = tmp_path,
        configuration = { },
        environment = { },
    )
    assert base == tmp_path / '.auxiliary/configuration/coders/codex'


def test_021_codex_renderer_respects_codex_home( tmp_path ):
    renderers = __.cache_import_module( 'agentsmgr.renderers' )
    renderer = renderers.RENDERERS[ 'codex' ]
    base = renderer.resolve_base_directory(
        mode = 'per-user',
        target = tmp_path,
        configuration = { },
        environment = { 'CODEX_HOME': str( tmp_path / 'codex-home' ) },
    )
    assert base == tmp_path / 'codex-home'


def test_022_codex_renderer_provides_codex_symlink( tmp_path ):
    renderers = __.cache_import_module( 'agentsmgr.renderers' )
    renderer = renderers.RENDERERS[ 'codex' ]
    symlinks = tuple( renderer.provide_project_symlinks( tmp_path ) )
    assert symlinks == (
        (
            tmp_path / '.auxiliary/configuration/coders/codex',
            tmp_path / '.codex',
        ),
    )


@pytest.mark.parametrize(
    ( 'coder_name', 'expected_tail' ),
    (
        ( 'claude', '.claude' ),
        ( 'codex', '.codex' ),
        ( 'opencode', '.config/opencode' ),
    ),
)
def test_023_renderers_accept_string_coders_for_per_user_defaults(
    tmp_path,
    coder_name,
    expected_tail,
):
    renderers = __.cache_import_module( 'agentsmgr.renderers' )
    renderer = renderers.RENDERERS[ coder_name ]
    base = renderer.resolve_base_directory(
        mode = 'per-user',
        target = tmp_path,
        configuration = { 'coders': [ coder_name ] },
        environment = { },
    )
    assert base == __.Path.home( ) / expected_tail


def test_024_filter_coders_by_mode_warns_on_unknown_coder( ):
    population = __.cache_import_module( 'agentsmgr.population' )
    filtered = population._filter_coders_by_mode(
        [ 'claude', 'nonexistent_coder', 'codex' ],
        'per-project',
    )
    assert 'claude' in filtered
    assert 'codex' in filtered
    assert 'nonexistent_coder' not in filtered


def test_025_resolve_coders_yields_known_coders( ):
    resolver = __.cache_import_module( 'agentsmgr.resolver' )
    results = dict( resolver.resolve_coders( [ 'claude', 'codex' ] ) )
    assert 'claude' in results
    assert 'codex' in results
    assert len( results ) == 2


def test_026_resolve_coders_skips_unknown_coders( ):
    resolver = __.cache_import_module( 'agentsmgr.resolver' )
    results = dict( resolver.resolve_coders(
        [ 'claude', 'nonexistent_coder', 'codex' ] ) )
    assert 'claude' in results
    assert 'codex' in results
    assert 'nonexistent_coder' not in results
    assert len( results ) == 2


def test_027_resolve_coders_filters_by_mode( ):
    resolver = __.cache_import_module( 'agentsmgr.resolver' )
    results = dict( resolver.resolve_coders(
        [ 'claude', 'codex' ], mode = 'per-project' ) )
    assert 'claude' in results
    assert 'codex' in results


def test_028_resolve_coders_excludes_non_matching_mode( ):
    resolver = __.cache_import_module( 'agentsmgr.resolver' )
    results = dict( resolver.resolve_coders(
        [ 'claude', 'codex' ], mode = 'per-user' ) )
    assert len( results ) == 0
