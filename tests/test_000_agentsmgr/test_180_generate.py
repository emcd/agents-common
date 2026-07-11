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

    Covers default mode and answers-file mode, mutual-exclusion rules
    between --answers-file / --check / --simulate, and the requirement
    that --answers-file needs explicit --output. Tests supply the
    output directory themselves via pytest's tmp_path; the production
    CLI does not manage temporary output.
'''


import asyncio
import contextlib
import shutil
import subprocess
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


# --- Public option names ---


def test_100_generate_help_exposes_unprefixed_options( ):
    ''' `agentsmgr generate --help` exposes --source, --output, --check,
        --simulate, --answers-file without the `--command.` subcommand
        prefix. '''
    agentsmgr = shutil.which( 'agentsmgr' )
    assert agentsmgr is not None, "agentsmgr CLI not on PATH"
    result = subprocess.run(  # noqa: S603
        [ agentsmgr, 'generate', '--help' ],
        capture_output = True, text = True, check = True )
    help_text = result.stdout
    for option in (
        '--source', '--output', '--check', '--simulate', '--answers-file',
    ):
        assert option in help_text, f"help text missing {option}"
    # Variant and preserve are no longer public surface.
    assert '--variant' not in help_text
    assert '--preserve' not in help_text


# --- Default mode ---


def test_200_default_mode_renders_to_explicit_output( tmp_path ):
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


# --- Answers-file mode ---


def test_400_answers_file_mode_with_explicit_output( tmp_path ):
    ''' --answers-file --output PATH renders to the explicit path. '''
    target = tmp_path / 'out'
    _run_application( [
        '--answers-file', str( _profile_path( 'default' ) ),
        '--output', str( target ),
        '--source', str( _components_location( ) ),
    ] )
    assert target.exists( )
    assert any( target.rglob( '*.md' ) )


def test_410_answers_file_mode_rejects_simulate( tmp_path, capsys ):
    ''' --simulate is not valid with --answers-file. '''
    with pytest.raises( SystemExit ) as info:
        _run_application( [
            '--answers-file', str( _profile_path( 'default' ) ),
            '--output', str( tmp_path / 'out' ),
            '--simulate',
        ] )
    assert isinstance(
        info.value.__context__, _exceptions.ConfigurationInvalidity )


def test_420_answers_file_mode_rejects_check( tmp_path, capsys ):
    ''' --check is not valid with --answers-file. '''
    with pytest.raises( SystemExit ) as info:
        _run_application( [
            '--answers-file', str( _profile_path( 'default' ) ),
            '--output', str( tmp_path / 'out' ),
            '--check',
        ] )
    assert isinstance(
        info.value.__context__, _exceptions.ConfigurationInvalidity )


def test_430_answers_file_requires_output( tmp_path ):
    ''' --answers-file without --output is rejected. The production CLI
        no longer auto-allocates a temp directory. '''
    with pytest.raises( SystemExit ) as info:
        _run_application( [
            '--answers-file', str( _profile_path( 'default' ) ),
            '--source', str( _components_location( ) ),
        ] )
    assert isinstance(
        info.value.__context__, _exceptions.ConfigurationInvalidity )
    assert 'requires' in str( info.value.__context__ ).lower()
