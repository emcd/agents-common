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
#  See the License for the specific language governing permissions and      #
#  limitations under the License.                                            #
#                                                                            #
#============================================================================#


''' Tests for CLI entrypoint error handling.

    Covers `agentsmgr.cli.execute`: unexpected exceptions render through
    the error presentation path to stderr before exit 1 (regression for
    issues/agentsmgr/9 silent exit), while `SystemExit` passes through
    untouched.
'''


import pytest

from . import __


def test_100_unexpected_exception_renders_to_stderr(
    monkeypatch, capsys
):
    ''' Unexpected failures print diagnosis to stderr, then exit 1. '''
    cli_module = __.cache_import_module( 'agentsmgr.cli' )
    failure = PermissionError( 'denied' )
    async def _application( ):
        raise failure
    monkeypatch.setattr(
        cli_module.__.tyro, 'cli',
        lambda *arguments, **nomargs: _application )
    with pytest.raises( SystemExit ) as info:
        cli_module.execute( )
    assert info.value.code == 1
    assert info.value.__context__ is failure
    captured = capsys.readouterr( )
    assert 'Unexpected PermissionError' in captured.err
    assert 'Traceback' in captured.err


def test_110_systemexit_passes_through_silently( monkeypatch, capsys ):
    ''' SystemExit from command handling propagates without rendering. '''
    cli_module = __.cache_import_module( 'agentsmgr.cli' )
    async def _application( ):
        raise SystemExit( 2 )
    monkeypatch.setattr(
        cli_module.__.tyro, 'cli',
        lambda *arguments, **nomargs: _application )
    with pytest.raises( SystemExit ) as info:
        cli_module.execute( )
    assert info.value.code == 2
    captured = capsys.readouterr( )
    assert captured.err == ''
