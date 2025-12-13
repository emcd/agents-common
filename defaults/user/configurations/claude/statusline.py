#!/usr/bin/env python3
''' Custom statusline for Claude Code showing token usage. '''

from json import loads as _json_loads
from pathlib import Path
from sys import stdin as _stdin


TOKEN_THRESHOLD_LOW = 50
TOKEN_THRESHOLD_HIGH = 75


def _abbreviate_home_in_path( path: str ) -> str:
    ''' Replaces home directory prefix with tilde. '''
    home = str( Path.home( ) )
    if path.startswith( home ): return '~' + path[ len( home ): ]
    return path


def _detect_git_branch( cwd: str ) -> str | None:
    ''' Detects current Git branch by parsing .git/HEAD. '''
    git_dir = Path( cwd ).resolve( ) if cwd != '~' else Path.home( )
    while git_dir != git_dir.parent:
        git_head = git_dir / '.git' / 'HEAD'
        if git_head.exists( ):
            try:
                content = git_head.read_text( ).strip( )
                if content.startswith( 'ref: refs/heads/' ):
                    return content[ len( 'ref: refs/heads/' ): ]
                return f"detached@{content[:7]}"
            except ( OSError, IOError ): return None
        git_dir = git_dir.parent
    return None


def _extract_token_info(
    context_window: dict[ str, int ]
) -> tuple[ int, int, float ] | None:
    ''' Extracts token usage from context_window field. '''
    total_input = context_window.get( 'total_input_tokens' )
    total_output = context_window.get( 'total_output_tokens' )
    context_size = context_window.get( 'context_window_size' )
    if total_input is None or total_output is None or context_size is None:
        return None
    if context_size == 0: return None
    total = total_input + total_output
    percentage = ( total / context_size ) * 100
    return ( total, context_size, percentage )


def _format_status(
    cwd: str,
    branch: str | None,
    token_info: tuple[ int, int, float ] | None,
    model_name: str | None,
) -> str:
    ''' Formats status line with token usage, directory, branch, and model. '''
    sections = [ ]
    if token_info:
        total, context_size, percentage = token_info
        if percentage < TOKEN_THRESHOLD_LOW: emoji = '🟢'
        elif percentage < TOKEN_THRESHOLD_HIGH: emoji = '🟡'
        else: emoji = '🔴'
        total_k = total // 1000
        context_k = context_size // 1000
        pct = f"{percentage:.0f}"
        sections.append( f"{emoji} {total_k}k/{context_k}k ({pct}%)" )
    sections.append( f"📁 {cwd}" )
    if branch: sections.append( f"🌿 {branch}" )
    if model_name: sections.append( f"🧠 {model_name}" )
    return ' | '.join( sections )


def main( ) -> None:
    ''' Displays token usage from context_window and current directory. '''
    input_data = _json_loads( _stdin.read( ) )
    cwd = _abbreviate_home_in_path( input_data.get( 'cwd', '~' ) )
    branch = _detect_git_branch( input_data.get( 'cwd', '~' ) )
    context_window = input_data.get( 'context_window', { } )
    token_info = _extract_token_info( context_window )
    model_info = input_data.get( 'model', { } )
    model_name = model_info.get( 'display_name' )
    status = _format_status( cwd, branch, token_info, model_name )
    print( status, end = '' )


if __name__ == '__main__':
    try: main( )
    except Exception as exc:
        print( f"⚠️ {exc}", end = '' )
