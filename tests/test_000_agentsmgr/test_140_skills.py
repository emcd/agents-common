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


from pathlib import Path

from . import __


def _defaults_location( ) -> Path:
    project_root = Path( __file__ ).resolve( ).parents[ 2 ]
    return project_root / 'defaults'


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


def test_400_populate_directory_discovers_skills( tmp_path ):
    operations_module = __.cache_import_module( 'agentsmgr.operations' )
    generator_module = __.cache_import_module( 'agentsmgr.generator' )
    ContentGenerator = generator_module.ContentGenerator
    generator = ContentGenerator(
        location = _defaults_location( ),
        configuration = { 'coders': [ 'claude' ], 'languages': [ 'python' ] },
        application_configuration = { },
        mode = 'per-project',
    )
    attempted, _ = operations_module.populate_directory(
        generator, tmp_path, simulate = False )
    assert attempted > 0
    skill_file = (
        tmp_path /
        '.auxiliary/configuration/coders/claude/skills/cs-review-todos/SKILL.md'
    )
    assert skill_file.exists( )
    assert 'name: "cs-review-todos"' in skill_file.read_text( )


def test_500_generate_coder_item_type_discovers_skills( tmp_path ):
    operations_module = __.cache_import_module( 'agentsmgr.operations' )
    generator_module = __.cache_import_module( 'agentsmgr.generator' )
    ContentGenerator = generator_module.ContentGenerator
    generator = ContentGenerator(
        location = _defaults_location( ),
        configuration = { 'coders': [ 'claude' ], 'languages': [ 'python' ] },
        application_configuration = { },
        mode = 'per-project',
    )
    attempted, written = operations_module.generate_coder_item_type(
        generator, 'claude', 'skills', tmp_path, simulate = False )
    assert attempted >= 1
    assert written >= 1
    skill_file = (
        tmp_path /
        '.auxiliary/configuration/coders/claude/skills/cs-review-todos/SKILL.md'
    )
    assert skill_file.exists( )


def test_600_generate_coder_item_type_skills_simulate( tmp_path ):
    operations_module = __.cache_import_module( 'agentsmgr.operations' )
    generator_module = __.cache_import_module( 'agentsmgr.generator' )
    ContentGenerator = generator_module.ContentGenerator
    generator = ContentGenerator(
        location = _defaults_location( ),
        configuration = { 'coders': [ 'claude' ], 'languages': [ 'python' ] },
        application_configuration = { },
        mode = 'per-project',
    )
    attempted, written = operations_module.generate_coder_item_type(
        generator, 'claude', 'skills', tmp_path, simulate = True )
    assert attempted >= 1
    assert written == 0
