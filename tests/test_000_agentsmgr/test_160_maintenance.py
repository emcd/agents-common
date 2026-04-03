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


''' Tests for maintainer CLI command routing and template workflows. '''


from pathlib import Path

import tyro

from agentsmgr import cmdbase as _cmdbase
from agentsmgr.maintenance import content as _content
from agentsmgr.maintenance import cli as _cli
from agentsmgr.maintenance import template as _template


class _AuxdataStub:

    def __init__( self, data_directory: Path ) -> None:
        self._data_directory = data_directory

    def provide_data_location( self ) -> Path:
        return self._data_directory


def test_100_maintainer_cli_defaults_to_content_validate( ):
    ''' Maintainer CLI defaults to content validate command dispatcher. '''
    application = _cli.MaintainerApplication( )
    assert isinstance( application.command, _content.CommandDispatcher )
    assert isinstance(
        application.command.command, _content.ValidateCommand )


def test_110_maintainer_cli_parses_template_survey_subcommand( ):
    ''' Maintainer CLI parses template survey subcommand tree. '''
    application = tyro.cli(
        _cli.MaintainerApplication,
        args = [ 'template', 'survey' ],
    )
    assert isinstance( application.command, _template.CommandDispatcher )
    assert isinstance( application.command.command, _template.SurveyCommand )


def test_120_maintainer_cli_parses_content_survey_subcommand( ):
    ''' Maintainer CLI parses content survey subcommand tree. '''
    application = tyro.cli(
        _cli.MaintainerApplication,
        args = [ 'content', 'survey' ],
    )
    assert isinstance( application.command, _content.CommandDispatcher )
    assert isinstance( application.command.command, _content.SurveyCommand )


def test_130_template_survey_variants_discovers_profile_answers( ):
    ''' Template survey returns variants from tests/data/profiles. '''
    project_root = Path( _template.__file__ ).resolve( ).parents[ 3 ]
    auxdata = _AuxdataStub( project_root / 'data' )
    assert _template.survey_variants( auxdata ) == ( 'default', 'maximum' )


def test_140_cmdbase_surveys_variants_from_project_root( ):
    ''' Variant survey uses project-local profiles in current repository. '''
    auxdata = _AuxdataStub( Path( '/unlikely/agentsmgr-data-location' ) )
    assert _cmdbase.survey_variant_names( auxdata ) == (
        'default', 'maximum' )
