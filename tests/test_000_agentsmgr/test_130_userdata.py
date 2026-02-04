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


''' Assert correct behavior of user settings population helpers. '''


from . import __


def test_130_merge_settings_file_toml_preserves_user_values( tmp_path ):
    userdata = __.cache_import_module( 'agentsmgr.userdata' )
    source = tmp_path / 'config.toml'
    target = tmp_path / 'user-config.toml'

    source.write_text(
        '\n'.join(
            [
                'model = "gpt-5.2"',
                'model_reasoning_effort = "high"',
                '',
                '[notice]',
                'hide_rate_limit_model_nudge = true',
                '',
            ]
        ),
        encoding = 'utf-8',
    )
    target.write_text(
        '\n'.join(
            [
                'model = "gpt-4.1"',
                '',
                '[notice]',
                'hide_rate_limit_model_nudge = false',
                '',
            ]
        ),
        encoding = 'utf-8',
    )

    userdata._merge_settings_file( source, target, simulate = False )
    merged = target.read_text( encoding = 'utf-8' )
    assert 'model = "gpt-4.1"' in merged
    assert 'model_reasoning_effort = "high"' in merged
    assert 'hide_rate_limit_model_nudge = false' in merged

    # Ensure backup exists when overwriting an existing TOML settings file.
    assert target.with_suffix( '.toml.backup' ).exists( )

