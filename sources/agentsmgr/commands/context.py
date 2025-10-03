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


''' Template rendering context normalization and tool mapping.

    Provides context transformation for template rendering, including
    hyphen-to-underscore normalization and coder-specific tool mapping.
'''


from . import __


ToolSpecification: __.typx.TypeAlias = (
    str | dict[ str, __.typx.Any ] )


_SEMANTIC_TOOLS_CLAUDE: dict[ str, str ] = {
    'read': 'Read',
    'edit': 'Edit',
    'write': 'Write',
    'list-directory': 'LS',
    'glob': 'Glob',
    'grep': 'Grep',
}


def normalize_render_context(
    context_data: __.cabc.Mapping[ str, __.typx.Any ],
    coder_config: __.cabc.Mapping[ str, __.typx.Any ],
) -> dict[ str, __.typx.Any ]:
    ''' Normalizes template rendering context with tool mapping.

        Transforms hyphenated keys to underscored keys, wraps configurations
        in SimpleNamespace objects for dot-notation access, and maps
        allowed-tools specifications to coder-specific syntax.
    '''
    coder_name = coder_config.get( 'name', 'unknown' )
    normalized_context = {
        key.replace( '-', '_' ): value
        for key, value in context_data.items( ) }
    if 'allowed_tools' in normalized_context:
        raw_tools = normalized_context[ 'allowed_tools' ]
        normalized_context[ 'allowed_tools' ] = (
            _map_tools_for_coder( raw_tools, coder_name ) )
    context_namespace = __.types.SimpleNamespace( **normalized_context )
    coder_namespace = __.types.SimpleNamespace( **coder_config )
    return {
        'context': context_namespace,
        'coder': coder_namespace,
    }


def _map_tools_for_coder(
    tool_specs: __.cabc.Sequence[ ToolSpecification ],
    coder_name: str,
) -> list[ str ]:
    ''' Maps tool specifications to coder-specific syntax.

        Dispatches to coder-specific mapping function based on coder name.
        Currently supports Claude; extensible for other coders.
    '''
    if coder_name == 'claude':
        return _map_tools_claude( tool_specs )
    return [ ]


def _map_tools_claude(
    tool_specs: __.cabc.Sequence[ ToolSpecification ]
) -> list[ str ]:
    ''' Maps tool specifications to Claude-specific syntax.

        Handles three specification types:
        - String literals (semantic names): 'read' → 'Read'
        - Shell commands: { tool = 'shell', arguments, ... } → 'Bash(...)'
        - MCP tools: { server, tool } → 'mcp__server__tool'
    '''
    mapped: list[ str ] = [ ]
    for spec in tool_specs:
        if isinstance( spec, str ):
            mapped.append( _map_semantic_tool_claude( spec ) )
        elif isinstance( spec, dict ):
            if 'server' in spec:
                mapped.append( _map_mcp_tool_claude( spec ) )
            elif spec.get( 'tool' ) == 'shell':
                mapped.append( _map_shell_tool_claude( spec ) )
            else:
                raise __.ConfigurationInvalidity(
                    __.ConfigurationInvalidity.UNRECOGNIZED_TOOL_SPEC )
        else:
            raise __.ConfigurationInvalidity(
                __.ConfigurationInvalidity.TOOL_SPEC_TYPE_ERROR )
    return mapped


def _map_semantic_tool_claude( tool_name: str ) -> str:
    ''' Maps semantic tool name to Claude tool name.

        Uses lookup table for known semantic names.
        Unknown names are returned as-is.
    '''
    return _SEMANTIC_TOOLS_CLAUDE.get( tool_name, tool_name )


def _map_shell_tool_claude( spec: dict[ str, __.typx.Any ] ) -> str:
    ''' Maps shell command specification to Claude Bash tool syntax.

        Format: { tool = 'shell', arguments = 'git status' }
        → 'Bash(git status)'

        With wildcard: { tool = 'shell', arguments = 'git pull',
                         allow-extra-arguments = true }
        → 'Bash(git pull:*)'
    '''
    arguments = spec.get( 'arguments', '' )
    allow_extra = spec.get( 'allow-extra-arguments', False )
    if allow_extra:
        return f"Bash({arguments}:*)"
    return f"Bash({arguments})"


def _map_mcp_tool_claude( spec: dict[ str, __.typx.Any ] ) -> str:
    ''' Maps MCP tool specification to Claude MCP tool syntax.

        Format: { server = 'librovore', tool = 'query-inventory' }
        → 'mcp__librovore__query_inventory'
    '''
    server = spec.get( 'server', '' )
    tool = spec.get( 'tool', '' )
    tool_normalized = tool.replace( '-', '_' )
    return f"mcp__{server}__{tool_normalized}"
