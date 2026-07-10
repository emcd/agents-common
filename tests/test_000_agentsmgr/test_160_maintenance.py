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


''' Tests for maintainer CLI command structure and copiertv config. '''


from pathlib import Path

import tomli as _tomli
import tyro

from agentsmgr.maintenance import cli as _cli
from agentsmgr.maintenance import content as _content


def test_100_maintainer_cli_defaults_to_validate( ):
    ''' Maintainer CLI defaults to ValidateCommand directly. '''
    application = _cli.MaintainerApplication( )
    assert isinstance( application.command, _content.ValidateCommand )


def test_110_maintainer_cli_parses_variant_positional( ):
    ''' Maintainer CLI parses variant as positional argument. '''
    application = tyro.cli(
        _cli.MaintainerApplication,
        args = [ 'default' ],
    )
    assert isinstance( application.command, _content.ValidateCommand )
    assert application.command.variant == 'default'


def test_120_copiertv_config_declares_template_and_answers( ):
    ''' copiertv config file exists and references the template and
        variant answers directories. '''
    project_root = Path( _cli.__file__ ).resolve( ).parents[ 3 ]
    config_file = (
        project_root / '.auxiliary' / 'configuration'
        / 'copiertv' / 'general.toml' )
    assert config_file.is_file( ), (
        f"copiertv config not found at {config_file}" )
    data = _tomli.loads( config_file.read_text( encoding = 'utf-8' ) )
    options = data.get( 'options', { } )
    template_directory = options.get( 'template-directory' )
    assert template_directory is not None, (
        "copiertv config must declare options.template-directory" )
    assert ( project_root / template_directory ).is_dir( ), (
        f"copiertv options.template-directory {template_directory!r} "
        f"does not resolve to an existing directory under {project_root}" )
    answers = data.get( 'answers', { } )
    answers_directory = answers.get( 'directory' )
    assert answers_directory is not None, (
        "copiertv config must declare answers.directory" )
    assert ( project_root / answers_directory ).is_dir( ), (
        f"copiertv answers.directory {answers_directory!r} "
        f"does not resolve to an existing directory under {project_root}" )