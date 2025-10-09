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


''' Core operations for content generation and directory population.

    This module provides functions for orchestrating content generation,
    including directory population and file writing operations with
    simulation support.
'''


from . import __
from . import generator as _generator


def populate_directory(
    generator: _generator.ContentGenerator,
    target: __.Path,
    simulate: bool = False
) -> tuple[ int, int ]:
    ''' Generates all content items to target directory.

        Orchestrates content generation for all coders and item types
        configured in generator. Returns tuple of (items_attempted,
        items_written).
    '''
    items_attempted = 0
    items_written = 0
    for coder_name in generator.configuration[ 'coders' ]:
        for item_type in ( 'commands', 'agents' ):
            attempted, written = produce_coder_item_type(
                generator, coder_name, item_type, target, simulate )
            items_attempted += attempted
            items_written += written
    return ( items_attempted, items_written )


def produce_coder_item_type(
    generator: _generator.ContentGenerator,
    coder: str,
    item_type: str,
    target: __.Path,
    simulate: bool
) -> tuple[ int, int ]:
    ''' Produces items of specific type for a coder.

        Generates all items (commands or agents) for specified coder by
        iterating through configuration files. Returns tuple of
        (items_attempted, items_written).
    '''
    items_attempted = 0
    items_written = 0
    if generator.mode == 'nowhere':
        return ( items_attempted, items_written )
    configuration_directory = (
        generator.location / 'configurations' / item_type )
    if not configuration_directory.exists( ):
        return ( items_attempted, items_written )
    for configuration_file in configuration_directory.glob( '*.toml' ):
        items_attempted += 1
        result = generator.render_single_item(
            item_type, configuration_file.stem, coder, target )
        if update_content( result.content, result.location, simulate ):
            items_written += 1
    return ( items_attempted, items_written )


def update_content(
    content: str, location: __.Path, simulate: bool = False
) -> bool:
    ''' Updates content file, creating directories as needed.

        Writes content to specified location, creating parent directories
        if necessary. In simulation mode, no actual writing occurs.
        Returns True if file was written, False if simulated.
    '''
    if simulate: return False
    try: location.parent.mkdir( parents = True, exist_ok = True )
    except ( OSError, IOError ) as exception:
        raise __.FileOperationFailure(
            location.parent, "create directory" ) from exception
    try: location.write_text( content, encoding = 'utf-8' )
    except ( OSError, IOError ) as exception:
        raise __.FileOperationFailure(
            location, "update content" ) from exception
    return True
