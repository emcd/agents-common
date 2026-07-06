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

import tyro

from . import __


def _distribution_location( ) -> Path:
    project_root = Path( __file__ ).resolve( ).parents[ 2 ]
    return project_root / 'distribution'


def _components_location( ) -> Path:
    project_root = Path( __file__ ).resolve( ).parents[ 2 ]
    return project_root / 'components'


def _project_root( ) -> Path:
    return Path( __file__ ).resolve( ).parents[ 2 ]


def _repository_git_directory( ) -> Path:
    project_root = Path( __file__ ).resolve( ).parents[ 2 ]
    return ( project_root / '.git' ).resolve( )


def _create_agents_answers_file( target: Path ) -> None:
    configuration_directory = target / '.auxiliary' / 'configuration'
    configuration_directory.mkdir( parents = True, exist_ok = True )
    ( configuration_directory / 'copier-answers--agents.yaml' ).write_text(
        '\n'.join( (
            'coders:',
            '- claude',
            '- opencode',
            'languages:',
            '- python',
            'provide_instructions: true',
            'instructions_target: .auxiliary/instructions',
        ) ) + '\n',
        encoding = 'utf-8' )
    ( configuration_directory / 'AGENTS.md' ).write_text(
        'test', encoding = 'utf-8' )


def _populate_project( distribution: Path, target: Path ) -> None:
    ''' Populates a project through the public application command path. '''
    import asyncio as _asyncio
    import contextlib as _contextlib
    cli_module = __.cache_import_module( 'agentsmgr.cli' )
    async def run_application( ) -> None:
        application = tyro.cli(
            cli_module.Application,
            args = [
                '--display.no-colorize',
                'populate',
                'project',
                str( distribution ),
                str( target ),
            ],
        )
        async with _contextlib.AsyncExitStack( ) as exits:
            auxdata = await application.prepare( exits )
            await application.execute( auxdata )
    _asyncio.run( run_application( ) )


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
    population_module = __.cache_import_module( 'agentsmgr.population' )
    location = _distribution_location( )
    target = tmp_path / 'project'
    target.mkdir( )
    configuration = {
        'coders': [ 'opencode' ],
        'languages': [ 'python' ],
    }
    attempted, written, _ = population_module._copy_distribution_items(
        location,
        [ 'opencode' ],
        target,
        configuration,
        'per-project',
        simulate = False,
    )
    assert attempted > 0
    assert written > 0
    prompt_resource = (
        target / '.auxiliary' / 'configuration' / 'coders' / 'opencode'
        / 'prompt' / 'nemotron-3-build.md' )
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
    # Remove one artifact to simulate staleness (missing)
    stale_file = (
        tmp_path / 'per-project' / 'coders' / 'claude' / 'commands'
        / 'cs-architect.md' )
    if stale_file.exists( ):
        stale_file.unlink( )
    items_checked, diffs = operations_module.check_distribution_staleness(
        generator, tmp_path )
    assert items_checked == 42
    assert any( 'missing' in d for d in diffs )
    # Add an orphaned artifact to detect extra files
    orphan_dir = (
        tmp_path / 'per-project' / 'coders' / 'claude' / 'commands' )
    orphan_dir.mkdir( parents = True, exist_ok = True )
    ( orphan_dir / 'zz-orphan.md' ).write_text( 'orphan' )
    items_checked, diffs = operations_module.check_distribution_staleness(
        generator, tmp_path )
    assert any( 'orphaned' in d for d in diffs )


def test_600_git_exclude_file_level_entries( tmp_path ):
    ''' Integration test for .git/info/exclude contents.

        Verifies that populate writes file-level exclude entries
        (not directory-level) and reconciles stale entries when
        distribution files are removed.
    '''
    import shutil
    # Use a temp copy of distribution to avoid mutating tracked files
    source_location = _distribution_location( )
    location = tmp_path / 'distribution'
    shutil.copytree( str( source_location ), str( location ) )
    # Create a temp git repo as the target
    target = tmp_path / 'project'
    target.mkdir( )
    has_git = _init_git_repo( target )
    if not has_git:
        import pytest
        pytest.skip( "git not available in test environment" )
    _create_agents_answers_file( target )
    exclude_file = target / '.git' / 'info' / 'exclude'
    # First populate
    _populate_project( location, target )
    # Read exclude file
    exclude_content = exclude_file.read_text( encoding = 'utf-8' )
    # Verify file-level entries exist (not directory-level)
    assert (
        '/.auxiliary/configuration/coders/claude/commands/cs-architect.md'
        in exclude_content )
    assert (
        '/.auxiliary/configuration/coders/opencode/prompt/nemotron-3-build.md'
        in exclude_content )
    assert '/.claude' in exclude_content
    assert '/.opencode' in exclude_content
    assert '/.mcp.json' in exclude_content
    assert '/AGENTS.md' in exclude_content
    assert '/CLAUDE.md' in exclude_content
    assert '/opencode.jsonc' in exclude_content
    assert '/openspec' in exclude_content
    # Verify no directory-level entries for generated artifacts
    assert (
        '/.auxiliary/configuration/coders/claude/commands\n'
        not in exclude_content )
    assert (
        '/.auxiliary/configuration/coders/claude/agents\n'
        not in exclude_content )
    # Simulate removal: re-copy with one file missing
    stale_file = (
        location / 'per-project' / 'coders' / 'claude' / 'commands'
        / 'cs-architect.md' )
    stale_file.unlink( )
    _populate_project( location, target )
    exclude_content2 = exclude_file.read_text( encoding = 'utf-8' )
    # Stale entry should be removed
    assert (
        '/.auxiliary/configuration/coders/claude/commands/cs-architect.md'
        not in exclude_content2 )
    # Other entries should remain
    assert (
        '/.auxiliary/configuration/coders/opencode/prompt/nemotron-3-build.md'
        in exclude_content2 )
    assert '/.opencode' in exclude_content2


def test_650_git_exclude_ignores_ambient_git_dir( tmp_path, monkeypatch ):
    ''' Explicit target should control which git exclude file is updated. '''
    operations_module = __.cache_import_module( 'agentsmgr.operations' )
    decoy = tmp_path / 'decoy'
    decoy.mkdir( )
    target = tmp_path / 'project'
    target.mkdir( )
    if not _init_git_repo( decoy ) or not _init_git_repo( target ):
        import pytest
        pytest.skip( "git not available in test environment" )
    decoy_exclude = decoy / '.git' / 'info' / 'exclude'
    target_exclude = target / '.git' / 'info' / 'exclude'
    decoy_before = decoy_exclude.read_text( encoding = 'utf-8' )
    monkeypatch.setenv( 'GIT_DIR', str( decoy / '.git' ) )
    operations_module.update_git_exclude(
        target, ( '.codex', ), simulate = False )
    assert decoy_exclude.read_text( encoding = 'utf-8' ) == decoy_before
    assert '/.codex' in target_exclude.read_text( encoding = 'utf-8' )


def test_700_instructions_copied_from_distribution( tmp_path ):
    ''' Instructions should be copied from distribution/, not fetched
        from network. Verifies the expected corpus is present. '''
    population_module = __.cache_import_module( 'agentsmgr.population' )
    location = _distribution_location( )
    target = tmp_path / 'project'
    target.mkdir( )
    # Verify instruction files exist in distribution
    instructions_dir = location / 'per-project' / 'general' / 'instructions'
    assert instructions_dir.exists( )
    instruction_files = list( instructions_dir.glob( '*.rst' ) )
    # Verify specific expected files are present
    expected_files = {
        'practices.rst', 'practices-python.rst', 'style.rst',
        'nomenclature.rst', 'tests.rst', 'validation.rst',
    }
    actual_names = { f.name for f in instruction_files }
    for name in expected_files:
        assert name in actual_names, f"Missing expected instruction: {name}"
    # Copy instructions
    attempted, written, entries = (
        population_module._copy_instructions_from_distribution(
            location, target, '.auxiliary/instructions', simulate = False ) )
    assert attempted == len( instruction_files )
    assert written == len( instruction_files )
    # Verify files were copied to target
    target_instructions = target / '.auxiliary' / 'instructions'
    assert target_instructions.exists( )
    for name in expected_files:
        dest_file = target_instructions / name
        assert dest_file.exists( ), f"Missing instruction: {name}"
    # Verify exclude entries are file-level
    for entry in entries:
        assert entry.startswith( '.auxiliary/instructions/' ), (
            f"Expected file-level entry, got: {entry}" )
        assert not entry.endswith( '/' ), (
            f"Entry should not be directory: {entry}" )


def test_800_provide_instructions_false_disables_copy( tmp_path ):
    ''' When provide_instructions is false, _manage_project_auxiliaries
        should not copy instruction files or produce instruction exclude
        entries. '''
    population_module = __.cache_import_module( 'agentsmgr.population' )
    location = _distribution_location( )
    target = tmp_path / 'project'
    target.mkdir( )
    # Create minimal git structure for _create_all_symlinks
    ( target / '.auxiliary' / 'configuration' ).mkdir( parents = True )
    ( target / '.auxiliary' / 'configuration' / 'AGENTS.md' ).write_text(
        'test', encoding = 'utf-8' )
    configuration = {
        'coders': [ 'claude' ],
        'languages': [ 'python' ],
        'provide_instructions': False,
    }
    population_module._manage_project_auxiliaries(
        configuration, location, target, ( ), simulate = False )
    # Verify no instruction files were copied
    target_instructions = target / '.auxiliary' / 'instructions'
    assert not target_instructions.exists( ) or \
        len( list( target_instructions.glob( '*' ) ) ) == 0


def test_900_instructions_sources_not_consulted( tmp_path ):
    ''' Populate should use distribution/ for instructions, not
        instructions_sources configuration. '''
    population_module = __.cache_import_module( 'agentsmgr.population' )
    location = _distribution_location( )
    target = tmp_path / 'project'
    target.mkdir( )
    # Create minimal git structure
    ( target / '.auxiliary' / 'configuration' ).mkdir( parents = True )
    ( target / '.auxiliary' / 'configuration' / 'AGENTS.md' ).write_text(
        'test', encoding = 'utf-8' )
    # Provide instructions_sources config but populate should ignore it
    configuration = {
        'coders': [ 'claude' ],
        'languages': [ 'python' ],
        'provide_instructions': True,
        'instructions_sources': [
            { 'source': 'github:emcd/python-project-common@docs-1' }
        ],
    }
    population_module._manage_project_auxiliaries(
        configuration, location, target, ( ), simulate = False )
    # Verify instructions were copied from distribution/ (local), not network
    target_instructions = target / '.auxiliary' / 'instructions'
    assert target_instructions.exists( )
    copied_files = list( target_instructions.glob( '*.rst' ) )
    assert len( copied_files ) > 0
    # Verify the files match the distribution corpus
    source_instructions = (
        location / 'per-project' / 'general' / 'instructions' )
    source_files = list( source_instructions.glob( '*.rst' ) )
    assert len( copied_files ) == len( source_files )


def _init_git_repo( path: Path ) -> bool:
    ''' Initializes a git repo for testing.

        Attempts real git init first, falls back to creating minimal
        directory structure if git is not available.
        Returns True if a real git repo was created, False otherwise.
    '''
    import os as _os
    import shutil as _shutil
    import subprocess as _sp
    assert path.resolve( ) != _project_root( )
    assert path.resolve( ) != _repository_git_directory( )
    assert ( path / '.git' ).resolve( ) != _repository_git_directory( )
    git = _shutil.which( 'git' )
    if git:
        environment = {
            key: value for key, value in _os.environ.items( )
            if not key.startswith( 'GIT_' )
        }
        result = _sp.run(  # noqa: S603
            [ git, 'init' ], cwd = str( path ),
            capture_output = True, check = False, env = environment )
        if ( result.returncode == 0
             and ( path / '.git' / 'info' / 'exclude' ).exists( ) ):
            return True
    # Fallback: create minimal git structure for dulwich
    git_dir = path / '.git'
    info_dir = git_dir / 'info'
    info_dir.mkdir( parents = True, exist_ok = True )
    ( info_dir / 'exclude' ).write_text( '', encoding = 'utf-8' )
    ( git_dir / 'HEAD' ).write_text(
        'ref: refs/heads/main\n', encoding = 'utf-8' )
    ( git_dir / 'config' ).write_text(
        '[core]\n\trepositoryformatversion = 0\n\tfilemode = true\n',
        encoding = 'utf-8' )
    return False


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
    attempted, written, exclude_entries = (
        population_module._copy_distribution_items(
            location,
            [ 'claude' ],
            target,
            configuration,
            'per-project',
            simulate = False,
        ) )
    assert attempted > 0
    assert written > 0
    # Verify items were copied to target, not cwd
    claude_commands = (
        target / '.auxiliary' / 'configuration' / 'coders' / 'claude'
        / 'commands' )
    assert claude_commands.exists( ), (
        f"Expected commands at {claude_commands}" )
    # Verify exclude entries are file-level paths relative to project root
    assert len( exclude_entries ) > 0
    for entry in exclude_entries:
        assert not entry.startswith( '/' ), (
            f"Exclude entry should be relative: {entry}" )
        assert (
            'commands/' in entry
            or 'agents/' in entry
            or 'skills/' in entry
        ), f"Exclude entry should reference distributed file: {entry}"
