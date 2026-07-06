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


''' Distribution model regression tests.

    Tests for the contracts established by the restructure-distribution-model
    proposal: source shape validation, target propagation, fallback artifact
    generation, static resource subpath preservation, and staleness detection.
'''


from pathlib import Path

from . import __


def _distribution_location( ) -> Path:
    project_root = Path( __file__ ).resolve( ).parents[ 2 ]
    return project_root / 'distribution'


def _components_location( ) -> Path:
    project_root = Path( __file__ ).resolve( ).parents[ 2 ]
    return project_root / 'components'


def test_100_populate_accepts_distribution_shape( tmp_path ):
    ''' PopulateProjectCommand should accept distribution/ shape
        (per-project/) not old shape (contents/). '''
    cmdbase_module = __.cache_import_module( 'agentsmgr.cmdbase' )
    location = _distribution_location( )
    # Should not raise DataSourceInvalidity for 'per-project'
    cmdbase_module.validate_data_source_structure(
        location, ( 'per-project', ) )


def test_200_generate_produces_opencode_fallback( tmp_path ):
    ''' generate should produce artifacts for all known coders,
        including OpenCode via fallback to Claude content. '''
    operations_module = __.cache_import_module( 'agentsmgr.operations' )
    generator_module = __.cache_import_module( 'agentsmgr.generator' )
    population_module = __.cache_import_module( 'agentsmgr.population' )
    configuration = population_module._produce_default_configuration(
        _components_location( ) )
    assert 'opencode' in configuration[ 'coders' ]
    # Include fallback configuration so OpenCode uses Claude content
    application_configuration = {
        'content': { 'fallbacks': { 'opencode': 'claude' } },
    }
    generator = generator_module.ContentGenerator(
        location = _components_location( ),
        configuration = configuration,
        application_configuration = application_configuration,
        mode = 'per-project',
    )
    attempted, written = operations_module.generate_distribution(
        generator, tmp_path, simulate = False )
    assert attempted == 42
    assert written == 42
    opencode_commands = (
        tmp_path / 'per-project' / 'coders' / 'opencode' / 'command' )
    assert opencode_commands.exists( )
    # OpenCode uses fallback to Claude content
    assert len( list( opencode_commands.glob( '*.md' ) ) ) == 19


def test_300_distribution_preserves_resource_subpaths( tmp_path ):
    ''' Static resource subpaths should be preserved during copy.
        e.g., prompt/nemotron-3-build.md should not lose prompt/ prefix. '''
    # Verify the source has the correct structure
    location = _distribution_location( )
    prompt_resource = (
        location / 'per-project' / 'coders' / 'opencode' / 'prompt'
        / 'nemotron-3-build.md' )
    assert prompt_resource.exists( ), (
        f"Expected prompt resource at {prompt_resource}" )


def test_400_generate_check_detects_stale_artifacts( tmp_path ):
    ''' generate --check should detect stale or missing artifacts. '''
    operations_module = __.cache_import_module( 'agentsmgr.operations' )
    generator_module = __.cache_import_module( 'agentsmgr.generator' )
    population_module = __.cache_import_module( 'agentsmgr.population' )
    configuration = population_module._produce_default_configuration(
        _components_location( ) )
    application_configuration = {
        'content': { 'fallbacks': { 'opencode': 'claude' } },
    }
    generator = generator_module.ContentGenerator(
        location = _components_location( ),
        configuration = configuration,
        application_configuration = application_configuration,
        mode = 'per-project',
    )
    # First generate to populate the distribution
    operations_module.generate_distribution(
        generator, tmp_path, simulate = False )
    # Check should pass when distribution is current
    items_checked, diffs = operations_module.check_distribution_staleness(
        generator, tmp_path )
    assert items_checked == 42
    assert diffs == [ ]
    # Remove one artifact to simulate staleness
    stale_file = (
        tmp_path / 'per-project' / 'coders' / 'claude' / 'commands'
        / 'cs-architect.md' )
    if stale_file.exists( ):
        stale_file.unlink( )
    items_checked, diffs = operations_module.check_distribution_staleness(
        generator, tmp_path )
    assert items_checked == 42
    assert len( diffs ) > 0
    assert any( 'missing' in d for d in diffs )


def test_500_populate_uses_explicit_target( tmp_path ):
    ''' populate should use the explicit target, not Path.cwd(). '''
    population_module = __.cache_import_module( 'agentsmgr.population' )
    location = _distribution_location( )
    target = tmp_path / 'project'
    target.mkdir( )
    configuration = {
        'coders': [ 'claude' ],
        'languages': [ 'python' ],
    }
    attempted, written = population_module._copy_distribution_items(
        location,
        [ 'claude' ],
        target,
        configuration,
        'per-project',
        simulate = False,
    )
    assert attempted > 0
    assert written > 0
    # Verify items were copied to target, not cwd
    claude_commands = (
        target / '.auxiliary' / 'configuration' / 'coders' / 'claude'
        / 'commands' )
    assert claude_commands.exists( ), (
        f"Expected commands at {claude_commands}" )
