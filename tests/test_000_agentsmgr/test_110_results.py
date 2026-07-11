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


''' Test formatting of results objects. '''


import pathlib

from agentsmgr import results as _results


def test_100_content_generation_result_render( ):
    ''' Content generation result renders with bulleted list. '''
    result = _results.ContentGenerationResult(
        source_location = pathlib.Path( "/src" ),
        target_location = pathlib.Path( "/dst" ),
        coders = ( "coder1", "coder2" ),
        simulated = False,
        items_generated = 42
    )
    lines = result.render_as_markdown( )
    # Verify bullet points are used
    assert any( line.startswith( " * Source: " ) for line in lines )
    assert any( line.startswith( " * Target: " ) for line in lines )
    assert " * Coders: coder1, coder2" in lines
    assert "🚀 Populating agent content (simulate=False):" in lines


def test_200_configuration_detection_result_render( ):
    ''' Configuration detection result renders with bulleted list. '''
    result = _results.ConfigurationDetectionResult(
        target = pathlib.Path( "/dst" ),
        coders = ( "coder1", ),
        languages = ( "python", ),
        project_name = "myproj"
    )
    lines = result.render_as_markdown( )
    assert " * Coders: coder1" in lines
    assert " * Languages: python" in lines
    assert " * Project: myproj" in lines
    assert any( line.startswith( " * Target Directory: " ) for line in lines )
