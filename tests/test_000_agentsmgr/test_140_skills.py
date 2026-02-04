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


def test_100_skills_render_to_skill_md_under_skill_directory( tmp_path ):
    generator_module = __.cache_import_module( 'agentsmgr.generator' )
    ContentGenerator = generator_module.ContentGenerator
    generator = ContentGenerator(
        location = _defaults_location( ),
        configuration = { 'coders': [ 'claude' ], 'languages': [ 'python' ] },
        application_configuration = { },
        mode = 'per-project',
    )
    rendered = generator.render_single_item(
        'skills', 'project-triage', 'claude', tmp_path )
    assert rendered.location == (
        tmp_path /
        '.auxiliary/configuration/coders/claude/skills/project-triage/SKILL.md'
    )
    assert 'name: "project-triage"' in rendered.content
    assert (
        'description: "Triage a repository and propose a focused next step."'
        in rendered.content
    )
    assert 'allowed-tools: "Glob, Grep, Read"' in rendered.content


def test_200_skills_omit_allowed_tools_when_unsupported( tmp_path ):
    generator_module = __.cache_import_module( 'agentsmgr.generator' )
    ContentGenerator = generator_module.ContentGenerator
    generator = ContentGenerator(
        location = _defaults_location( ),
        configuration = { 'coders': [ 'codex' ], 'languages': [ 'python' ] },
        application_configuration = { },
        mode = 'per-project',
    )
    rendered = generator.render_single_item(
        'skills', 'project-triage', 'codex', tmp_path )
    assert rendered.location == (
        tmp_path /
        '.auxiliary/configuration/coders/codex/skills/project-triage/SKILL.md'
    )
    assert 'allowed-tools:' not in rendered.content
