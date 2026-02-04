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
