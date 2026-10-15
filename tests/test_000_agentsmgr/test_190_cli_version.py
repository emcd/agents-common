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


''' Tests for `agentsmgr --version`.

    Covers the console-script entrypoint used by hatch installs and
    ``uv tool`` installs: the flag prints the running package version
    and exits without running a subcommand.
'''


import asyncio
import shutil
import subprocess

from agentsmgr import __version__ as _package_version
from agentsmgr.__.nomina import package_name as _package_name
from agentsmgr.cli import Application


def _agentsmgr_executable( ) -> str:
    agentsmgr = shutil.which( 'agentsmgr' )
    assert agentsmgr is not None, "agentsmgr CLI not on PATH"
    return agentsmgr


def test_100_version_flag_reports_package_version( ):
    ''' `agentsmgr --version` prints the running package version. '''
    result = subprocess.run(  # noqa: S603
        [ _agentsmgr_executable( ), '--version' ],
        capture_output = True, text = True, check = True )
    expected = '{0} {1}'.format( _package_name, _package_version )
    assert result.stdout.strip( ) == expected
    assert result.stderr == ''


def test_110_help_exposes_version_flag( ):
    ''' `agentsmgr --help` lists --version and not --no-version. '''
    result = subprocess.run(  # noqa: S603
        [ _agentsmgr_executable( ), '--help' ],
        capture_output = True, text = True, check = True )
    assert '--version' in result.stdout
    assert '--no-version' not in result.stdout


def test_200_version_short_circuits_command( capsys ):
    ''' Application --version prints the package version and skips detect. '''
    asyncio.run( Application( version = True )( ) )
    captured = capsys.readouterr( )
    assert captured.out.strip( ) == '{0} {1}'.format(
        _package_name, _package_version )
    assert captured.err == ''
