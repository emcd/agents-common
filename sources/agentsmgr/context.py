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
from . import exceptions as _exceptions


ToolSpecification: __.typx.TypeAlias = (
    str | dict[ str, __.typx.Any ] )


_SEMANTIC_TOOLS_CLAUDE: dict[ str, str ] = {
    'read': 'Read',
    'edit': 'Edit',
    'multi-edit': 'MultiEdit',
    'write': 'Write',
    'list-directory': 'LS',
    'glob': 'Glob',
    'grep': 'Grep',
    'todo-write': 'TodoWrite',
    'web-fetch': 'WebFetch',
    'web-search': 'WebSearch',
}

_SEMANTIC_TOOLS_QWEN: dict[ str, str ] = {
    'read': 'read_file',
    'edit': 'edit',
    'multi-edit': 'edit',
    'write': 'write_file',
    'list-directory': 'list_directory',
    'glob': 'glob',
    'grep': 'search_file_content',
    'todo-write': 'todo_write',
    'web-fetch': 'web_fetch',
    'web-search': 'web_search',
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
        Returns empty list if coder is not supported.
    '''
    if coder_name == 'claude':
        return _map_tools_claude( tool_specs )
    if coder_name == 'qwen':
        return _map_tools_qwen( tool_specs )
    return [ ]


def _map_tools_claude(
    tool_specs: __.cabc.Sequence[ ToolSpecification ]
) -> list[ str ]:
    ''' Maps tool specifications to Claude-specific syntax.

        Handles three specification types:
        - String literals (semantic names): 'read' → 'Read'
        - Shell commands: { tool = 'shell', arguments, ... } → 'Bash(...)'
        - MCP tools: { server, tool } → 'mcp__server__tool'

        Returns tools sorted alphabetically for consistent output.
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
                raise _exceptions.ToolSpecificationInvalidity( str( spec ) )
        else:
            raise _exceptions.ToolSpecificationTypeInvalidity(
                type( spec ).__name__
            )
    return sorted( mapped )


def _map_semantic_tool_claude( tool_name: str ) -> str:
    ''' Maps semantic tool name to Claude tool name.

        Uses lookup table for known semantic names.
        Raises ToolSpecificationInvalidity for unknown tools.
    '''
    if tool_name not in _SEMANTIC_TOOLS_CLAUDE:
        raise _exceptions.ToolSpecificationInvalidity( tool_name )
    return _SEMANTIC_TOOLS_CLAUDE[ tool_name ]


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


def _map_tools_qwen(
    tool_specs: __.cabc.Sequence[ ToolSpecification ]
) -> list[ str ]:
    ''' Maps tool specifications to Qwen-specific syntax.

        Handles three specification types:
        - String literals (semantic names): 'read' → 'read_file'
        - Shell commands: { tool = 'shell', arguments, ... } →
          'run_shell_command(...)' in coreTools (prefix matching)
        - MCP tools: { server, tool } → 'mcp__server__tool'

        Returns tools sorted alphabetically for consistent output.
    '''
    mapped: list[ str ] = [ ]
    for spec in tool_specs:
        if isinstance( spec, str ):
            mapped.append( _map_semantic_tool_qwen( spec ) )
        elif isinstance( spec, dict ):
            if 'server' in spec:
                mapped.append( _map_mcp_tool_qwen( spec ) )
            elif spec.get( 'tool' ) == 'shell':
                mapped.append( _map_shell_tool_qwen( spec ) )
            else:
                raise _exceptions.ToolSpecificationInvalidity( str( spec ) )
        else:
            raise _exceptions.ToolSpecificationTypeInvalidity(
                type( spec ).__name__
            )
    return sorted( mapped )


def _map_semantic_tool_qwen( tool_name: str ) -> str:
    ''' Maps semantic tool name to Qwen tool name.

        Uses lookup table for known semantic names.
        Raises ToolSpecificationInvalidity for unknown tools.
    '''
    # TODO: Verify semantic tool mappings are correct for Qwen coder.
    # The structure is identical to Claude version, but tool names differ.
    # Keep implementations separate since each coder has its own tool names.
    if tool_name not in _SEMANTIC_TOOLS_QWEN:
        raise _exceptions.ToolSpecificationInvalidity( tool_name )
    return _SEMANTIC_TOOLS_QWEN[ tool_name ]


def _map_shell_tool_qwen( spec: dict[ str, __.typx.Any ] ) -> str:
    ''' Maps shell command specification to Qwen run_shell_command syntax.

        Qwen uses prefix matching for shell commands - no wildcard needed.
        Format: { tool = 'shell', arguments = 'git status' }
        → 'run_shell_command(git status)'

        allow-extra-arguments is implicit in Qwen's prefix matching.
        Format: { tool = 'shell', arguments = 'git pull',
                   allow-extra-arguments = true }
        → 'run_shell_command(git pull)' (same as without extra-arguments)
    '''
    arguments = spec.get( 'arguments', '' )
    return f"run_shell_command({arguments})"


def _map_mcp_tool_qwen( spec: dict[ str, __.typx.Any ] ) -> str:
    ''' Maps MCP tool specification to Qwen MCP tool syntax.

        Format: { server = 'librovore', tool = 'query-inventory' }
        → 'mcp__librovore__query_inventory'
    '''
    # TODO: Verify this implementation is correct for Qwen coder.
    # Once verified, consider whether consolidation with Claude version
    # is appropriate or if they should remain separate.
    server = spec.get( 'server', '' )
    tool = spec.get( 'tool', '' )
    tool_normalized = tool.replace( '-', '_' )
    return f"mcp__{server}__{tool_normalized}"
