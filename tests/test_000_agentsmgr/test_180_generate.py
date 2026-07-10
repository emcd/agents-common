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
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. #
#  See the License for the specific language governing permissions and      #
#  limitations under the License.                                            #
#                                                                            #
#============================================================================#


''' Tests for `agentsmgr generate` mode contract.

    Covers the three modes (default, variant, answers-file), the
    mutual-exclusion rules between --variant, --answers-file, --check,
    --simulate, --preserve, and --output, and the temp-directory
    cleanup/preserve behavior.

    Temp allocation is isolated per test via the `isolate_temp_dirs`
    fixture, which monkeypatches `tempfile.mkdtemp` to force
    `dir=tmp_path`. This avoids touching global /tmp and prevents
    race-prone assertions on shared state.
'''


import asyncio
import contextlib
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest
import tyro

from agentsmgr import cli as _cli
from agentsmgr import exceptions as _exceptions


def _run_application( args: list[ str ] ) -> None:
    ''' Invokes the agentsmgr CLI through the public entrypoint. '''
    async def run( ) -> None:
        application = tyro.cli(
            _cli.Application,
            args = [ '--display.no-colorize', 'generate', *args ],
        )
        async with contextlib.AsyncExitStack( ) as exits:
            auxdata = await application.prepare( exits )
            await application.execute( auxdata )
    asyncio.run( run( ) )


def _components_location( ) -> Path:
    return Path( __file__ ).resolve( ).parents[ 2 ] / 'components'


def _profile_path( name: str ) -> Path:
    return (
        Path( __file__ ).resolve( ).parents[ 2 ]
        / 'tests' / 'data' / 'profiles' / f'answers-{name}.yaml' )


# --- Temp-isolation fixture ---


@pytest.fixture
def isolate_temp_dirs( monkeypatch, tmp_path ):
    ''' Redirects tempfile.mkdtemp calls in population.py to use
        tmp_path. The original mkdtemp is restored on teardown via
        monkeypatch. Tests should assert and clean only paths under
        the returned tmp_path, never under global /tmp.

        Note: tempfile.mkdtemp has signature (suffix, prefix, dir) —
        not (prefix, suffix, dir) — so we forward all args as
        keyword-only via ``**kwargs`` to avoid positional confusion. '''
    original = tempfile.mkdtemp
    def redirected( *args, **kwargs ):
        kwargs.setdefault( 'dir', str( tmp_path ) )
        return original( *args, **kwargs )
    monkeypatch.setattr( tempfile, 'mkdtemp', redirected )
    return tmp_path


# --- Public option names ---


def test_100_generate_help_exposes_unprefixed_options( ):
    ''' `agentsmgr generate --help` exposes --source, --output, --check,
        --simulate, --variant, --answers-file, --preserve without
        the `--command.` subcommand prefix. '''
    agentsmgr = shutil.which( 'agentsmgr' )
    assert agentsmgr is not None, "agentsmgr CLI not on PATH"
    result = subprocess.run(  # noqa: S603
        [ agentsmgr, 'generate', '--help' ],
        capture_output = True, text = True, check = True )
    help_text = result.stdout
    for option in (
        '--source', '--output', '--check', '--simulate',
        '--variant', '--answers-file', '--preserve',
    ):
        assert option in help_text, f"help text missing {option}"
    # And --output help mentions the per-mode default
    assert 'temp' in help_text.lower()
    # And the variant --output restriction is documented (the docs wrap
    # awkwardly in rich output but the intent is to call it invalid).
    assert 'not valid' in help_text.lower()
    assert 'variant' in help_text.lower()


# --- Default mode ---


def test_200_default_mode_renders_to_distribution(
    tmp_path, isolate_temp_dirs,
):
    ''' Default mode (no flags) writes to distribution/ (or a custom
        --output). Smoke test that the new flag surface doesn't break
        the existing path. '''
    target = tmp_path / 'distribution'
    _run_application( [
        '--source', str( _components_location( ) ),
        '--output', str( target ),
    ] )
    assert target.exists( )
    assert any( target.rglob( '*.md' ) )


# --- Variant mode ---


def test_300_variant_mode_uses_temp_and_cleans_up(
    tmp_path, isolate_temp_dirs,
):
    ''' --variant renders to a temp dir under isolate_temp_dirs and
        cleans up by default. After execution, the temp dir is gone. '''
    _run_application( [
        '--variant', 'default',
        '--source', str( _components_location( ) ),
    ] )
    leftover = list( tmp_path.glob( 'agents-validate-*' ) )
    assert not leftover, f"Temp dirs not cleaned up: {leftover}"


def test_310_variant_mode_preserves_temp_when_requested(
    tmp_path, isolate_temp_dirs,
):
    ''' --variant --preserve keeps the temp dir. After execution,
        exactly one preserved dir exists under isolate_temp_dirs and
        contains rendered content. The test cleans it up at teardown. '''
    _run_application( [
        '--variant', 'default',
        '--preserve',
        '--source', str( _components_location( ) ),
    ] )
    preserved = list( tmp_path.glob( 'agents-validate-*' ) )
    assert len( preserved ) == 1, (
        f"Expected exactly one preserved dir, got {preserved}" )
    assert any( preserved[ 0 ].rglob( '*.md' ) )
    shutil.rmtree( preserved[ 0 ] )  # explicit teardown


def test_320_variant_mode_rejects_simulate( tmp_path, capsys ):
    ''' --simulate is invalid in variant mode. '''
    with pytest.raises( SystemExit ) as info:
        _run_application( [
            '--variant', 'default',
            '--simulate',
        ] )
    assert isinstance(
        info.value.__context__, _exceptions.ConfigurationInvalidity )


def test_330_variant_mode_rejects_check( tmp_path, capsys ):
    ''' --check is invalid in variant mode. '''
    with pytest.raises( SystemExit ) as info:
        _run_application( [
            '--variant', 'default',
            '--check',
        ] )
    assert isinstance(
        info.value.__context__, _exceptions.ConfigurationInvalidity )


def test_340_variant_mode_rejects_output(
    tmp_path, isolate_temp_dirs, capsys,
):
    ''' --output is invalid in variant mode (always temp). The error
        message uses "invalid"/"not valid" language to match docs. '''
    with pytest.raises( SystemExit ) as info:
        _run_application( [
            '--variant', 'default',
            '--output', str( tmp_path / 'x' ),
        ] )
    assert isinstance(
        info.value.__context__, _exceptions.ConfigurationInvalidity )
    message = str( info.value.__context__ ).lower()
    assert 'invalid' in message or 'not valid' in message
    assert 'variant' in message
    # No temp dir should have been allocated
    leftover = list( tmp_path.glob( 'agents-validate-*' ) )
    assert not leftover, f"Temp dir leaked: {leftover}"


# --- Answers-file mode ---


def test_400_answers_file_mode_defaults_to_temp(
    tmp_path, isolate_temp_dirs,
):
    ''' --answers-file without --output renders to a temp dir under
        isolate_temp_dirs (safe). Temp is cleaned up after execution. '''
    _run_application( [
        '--answers-file', str( _profile_path( 'default' ) ),
        '--source', str( _components_location( ) ),
    ] )
    leftover = list( tmp_path.glob( 'agents-answers-*' ) )
    assert not leftover, f"Temp dirs not cleaned up: {leftover}"


def test_405_answers_file_mode_does_not_leak_temp_on_invalid_answers(
    tmp_path, isolate_temp_dirs,
):
    ''' Regression: a missing/invalid answers file must not leak
        agents-answers-* temp directories. The config load happens
        before the temp dir is allocated. '''
    missing = tmp_path / 'nonexistent-answers.yaml'
    with pytest.raises( SystemExit ) as info:
        _run_application( [
            '--answers-file', str( missing ),
            '--source', str( _components_location( ) ),
        ] )
    # ConfigurationAbsence (missing) or ConfigurationInvalidity
    # (malformed) — both are subclasses of Omnierror.
    assert isinstance(
        info.value.__context__, _exceptions.Omnierror )
    leftover = list( tmp_path.glob( 'agents-answers-*' ) )
    assert not leftover, (
        f"Invalid answers input left temp dirs behind: {leftover}" )


def test_410_answers_file_mode_with_explicit_output(
    tmp_path, isolate_temp_dirs,
):
    ''' --answers-file --output PATH writes to PATH (caller's choice).
        The output is preserved (it's an explicit user choice, not a
        temp dir). '''
    target = tmp_path / 'out'
    _run_application( [
        '--answers-file', str( _profile_path( 'default' ) ),
        '--output', str( target ),
        '--source', str( _components_location( ) ),
    ] )
    assert target.exists( )
    assert any( target.rglob( '*.md' ) )
    # No temp dir was allocated in the isolated directory
    leftover = list( tmp_path.glob( 'agents-answers-*' ) )
    assert not leftover, (
        f"--output PATH should not allocate a temp dir, but found: {leftover}"
    )


def test_420_answers_file_mode_preserves_temp_when_requested(
    tmp_path, isolate_temp_dirs,
):
    ''' --answers-file --preserve keeps the temp dir under
        isolate_temp_dirs. '''
    _run_application( [
        '--answers-file', str( _profile_path( 'default' ) ),
        '--preserve',
        '--source', str( _components_location( ) ),
    ] )
    preserved = list( tmp_path.glob( 'agents-answers-*' ) )
    assert len( preserved ) == 1, (
        f"Expected exactly one preserved dir, got {preserved}" )
    assert any( preserved[ 0 ].rglob( '*.md' ) )
    shutil.rmtree( preserved[ 0 ] )  # explicit teardown


def test_430_answers_file_mode_rejects_simulate( tmp_path, capsys ):
    ''' --simulate is invalid in answers-file mode. '''
    with pytest.raises( SystemExit ) as info:
        _run_application( [
            '--answers-file', str( _profile_path( 'default' ) ),
            '--simulate',
        ] )
    assert isinstance(
        info.value.__context__, _exceptions.ConfigurationInvalidity )


def test_440_answers_file_mode_rejects_check( tmp_path, capsys ):
    ''' --check is invalid in answers-file mode. '''
    with pytest.raises( SystemExit ) as info:
        _run_application( [
            '--answers-file', str( _profile_path( 'default' ) ),
            '--check',
        ] )
    assert isinstance(
        info.value.__context__, _exceptions.ConfigurationInvalidity )


# --- Mutual exclusion ---


def test_500_variant_and_answers_file_are_mutually_exclusive(
    tmp_path, capsys,
):
    ''' --variant and --answers-file cannot be combined. '''
    with pytest.raises( SystemExit ) as info:
        _run_application( [
            '--variant', 'default',
            '--answers-file', str( _profile_path( 'default' ) ),
        ] )
    assert isinstance(
        info.value.__context__, _exceptions.ConfigurationInvalidity )


def test_510_preserve_requires_variant_or_answers_file(
    tmp_path, capsys,
):
    ''' --preserve is invalid in default mode (nothing to preserve). '''
    with pytest.raises( SystemExit ) as info:
        _run_application( [
            '--preserve',
            '--source', str( _components_location( ) ),
            '--output', str( tmp_path / 'out' ),
        ] )
    assert isinstance(
        info.value.__context__, _exceptions.ConfigurationInvalidity )
