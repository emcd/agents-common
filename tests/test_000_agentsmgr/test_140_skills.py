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


''' Skill generation and SKILL.md output behavior. '''


import os as _os

from pathlib import Path

from . import __


def _defaults_location( ) -> Path:
    project_root = Path( __file__ ).resolve( ).parents[ 2 ]
    return project_root / 'distribution'


def test_100_skills_copy_to_skill_md_under_skill_directory( tmp_path ):
    generator_module = __.cache_import_module( 'agentsmgr.generator' )
    ContentGenerator = generator_module.ContentGenerator
    generator = ContentGenerator(
        location = _defaults_location( ),
        configuration = { 'coders': [ 'claude' ], 'languages': [ 'python' ] },
        application_configuration = { },
        mode = 'per-project',
    )
    rendered = generator.render_single_item(
        'skills', 'cs-review-todos', 'claude', tmp_path )
    assert rendered.location == (
        tmp_path /
        '.auxiliary/configuration/coders/claude/skills/cs-review-todos/SKILL.md'
    )
    assert 'name: "cs-review-todos"' in rendered.content
    assert (
        'description: "Review open todos and issues in the project'
        ' notebook using the nb MCP server."'
        in rendered.content
    )


def test_200_skills_are_portable_across_coders( tmp_path ):
    generator_module = __.cache_import_module( 'agentsmgr.generator' )
    ContentGenerator = generator_module.ContentGenerator
    generator = ContentGenerator(
        location = _defaults_location( ),
        configuration = { 'coders': [ 'codex' ], 'languages': [ 'python' ] },
        application_configuration = { },
        mode = 'per-project',
    )
    rendered = generator.render_single_item(
        'skills', 'cs-review-todos', 'codex', tmp_path )
    assert rendered.location == (
        tmp_path /
        '.auxiliary/configuration/coders/codex/skills/cs-review-todos/SKILL.md'
    )
    assert 'name: "cs-review-todos"' in rendered.content


def test_300_skills_use_plural_directory_for_opencode( tmp_path ):
    generator_module = __.cache_import_module( 'agentsmgr.generator' )
    ContentGenerator = generator_module.ContentGenerator
    generator = ContentGenerator(
        location = _defaults_location( ),
        configuration = {
            'coders': [ 'opencode' ],
            'languages': [ 'python' ],
        },
        application_configuration = { },
        mode = 'per-project',
    )
    rendered = generator.render_single_item(
        'skills', 'cs-review-todos', 'opencode', tmp_path )
    assert rendered.location == (
        tmp_path /
        '.auxiliary/configuration/coders/opencode/skills/cs-review-todos/SKILL.md'
    )


def test_400_directory_skill_package_copies_supporting_files( tmp_path ):
    population_module = __.cache_import_module( 'agentsmgr.population' )
    distribution = tmp_path / 'distribution'
    skill_root = (
        distribution / 'per-project' / 'general' / 'skills' / 'demo-skill' )
    ( skill_root / 'scripts' ).mkdir( parents = True )
    ( skill_root / 'references' ).mkdir( parents = True )
    ( skill_root / 'assets' ).mkdir( parents = True )
    ( skill_root / 'SKILL.md' ).write_text(
        '---\nname: demo-skill\ndescription: Demo.\n---\nBody.\n',
        encoding = 'utf-8',
    )
    script_source = skill_root / 'scripts' / 'run.sh'
    script_source.write_text( '#!/bin/sh\necho ok\n', encoding = 'utf-8' )
    script_source.chmod( 0o755 )
    ( skill_root / 'references' / 'notes.md' ).write_text(
        'detail\n', encoding = 'utf-8' )
    ( skill_root / 'assets' / 'icon.bin' ).write_bytes( b'\x00\x01\xff' )
    target = tmp_path / 'project'
    target.mkdir( )
    renderers_module = __.cache_import_module( 'agentsmgr.renderers' )
    manager = renderers_module.RENDERERS[ 'claude' ]
    base_directory = manager.resolve_base_directory(
        mode = 'per-project',
        target = target,
        configuration = { },
        environment = { },
    )
    attempted, written, entries = population_module._copy_skills(
        distribution, base_directory, manager, target, simulate = False )
    dest = (
        base_directory / 'skills' / 'demo-skill' )
    assert attempted == 4
    assert written == 4
    assert ( dest / 'SKILL.md' ).is_file( )
    script_dest = dest / 'scripts' / 'run.sh'
    assert script_dest.read_text(
        encoding = 'utf-8' ) == '#!/bin/sh\necho ok\n'
    if _os.name != 'nt': assert script_dest.stat( ).st_mode & 0o111
    assert ( dest / 'references' / 'notes.md' ).read_text(
        encoding = 'utf-8' ) == 'detail\n'
    assert ( dest / 'assets' / 'icon.bin' ).read_bytes( ) == b'\x00\x01\xff'
    assert any( entry.endswith( 'skills/demo-skill/SKILL.md' )
                for entry in entries )
    assert any( entry.endswith( 'skills/demo-skill/scripts/run.sh' )
                for entry in entries )


def test_500_directory_skill_preferred_over_flat_file( tmp_path ):
    population_module = __.cache_import_module( 'agentsmgr.population' )
    distribution = tmp_path / 'distribution'
    skills_dir = distribution / 'per-project' / 'general' / 'skills'
    skills_dir.mkdir( parents = True )
    ( skills_dir / 'demo-skill.md' ).write_text(
        '---\nname: demo-skill\ndescription: Flat.\n---\nFlat body.\n',
        encoding = 'utf-8',
    )
    package = skills_dir / 'demo-skill'
    package.mkdir( )
    ( package / 'SKILL.md' ).write_text(
        '---\nname: demo-skill\ndescription: Dir.\n---\nDir body.\n',
        encoding = 'utf-8',
    )
    target = tmp_path / 'project'
    target.mkdir( )
    renderers_module = __.cache_import_module( 'agentsmgr.renderers' )
    manager = renderers_module.RENDERERS[ 'claude' ]
    base_directory = manager.resolve_base_directory(
        mode = 'per-project',
        target = target,
        configuration = { },
        environment = { },
    )
    population_module._copy_skills(
        distribution, base_directory, manager, target, simulate = False )
    body = (
        base_directory / 'skills' / 'demo-skill' / 'SKILL.md'
    ).read_text( encoding = 'utf-8' )
    assert 'Dir body.' in body
    assert 'Flat body.' not in body


def test_600_generator_reads_directory_skill_md( tmp_path ):
    generator_module = __.cache_import_module( 'agentsmgr.generator' )
    distribution = tmp_path / 'distribution'
    skill_root = (
        distribution / 'per-project' / 'general' / 'skills' / 'packaged' )
    skill_root.mkdir( parents = True )
    ( skill_root / 'SKILL.md' ).write_text(
        '---\nname: packaged\ndescription: Packaged skill.\n---\nHi.\n',
        encoding = 'utf-8',
    )
    generator = generator_module.ContentGenerator(
        location = distribution,
        configuration = { 'coders': [ 'claude' ], 'languages': [ 'python' ] },
        application_configuration = { },
        mode = 'per-project',
    )
    rendered = generator.render_single_item(
        'skills', 'packaged', 'claude', tmp_path / 'out' )
    assert 'Packaged skill.' in rendered.content
    assert rendered.location.name == 'SKILL.md'
