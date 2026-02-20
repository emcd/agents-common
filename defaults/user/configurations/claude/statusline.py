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
    ''' Detects current Git branch by parsing .git/HEAD.

        Handles both regular repositories and worktrees. In worktrees,
        .git is a file containing a gitdir reference rather than a directory.
    '''
    search_dir = Path( cwd ).resolve( ) if cwd != '~' else Path.home( )
    while search_dir != search_dir.parent:
        git_path = search_dir / '.git'
        if git_path.exists( ):
            git_dir = _resolve_git_directory( git_path )
            if git_dir is None: return None
            return _read_branch_from_head( git_dir / 'HEAD' )
        search_dir = search_dir.parent
    return None


def _resolve_git_directory( git_path: Path ) -> Path | None:
    ''' Resolves actual git directory, handling worktrees.

        For regular repos, .git is a directory containing HEAD.
        For worktrees, .git is a file with "gitdir: <path>" content.
    '''
    if git_path.is_dir( ):
        return git_path
    # Worktree: .git is a file containing gitdir reference
    try:
        content = git_path.read_text( ).strip( )
    except ( OSError, IOError ):
        return None
    if content.startswith( 'gitdir: ' ):
        gitdir_path = content[ len( 'gitdir: ' ): ]
        resolved = Path( gitdir_path )
        if not resolved.is_absolute( ):
            resolved = ( git_path.parent / gitdir_path ).resolve( )
        return resolved if resolved.is_dir( ) else None
    return None


def _read_branch_from_head( head_path: Path ) -> str | None:
    ''' Reads branch name from HEAD file. '''
    try:
        content = head_path.read_text( ).strip( )
        if content.startswith( 'ref: refs/heads/' ):
            return content[ len( 'ref: refs/heads/' ): ]
        return f"detached@{content[:7]}"
    except ( OSError, IOError ):
        return None


def _format_status(
    cwd: str,
    branch: str | None,
    used_percentage: float | None,
    model_name: str | None,
) -> str:
    ''' Formats status line with token usage, directory, branch, and model. '''
    sections = [ ]
    sections.append( f"📁 {cwd}" )
    if branch: sections.append( f"🌿 {branch}" )
    if model_name: sections.append( f"✨ {model_name}" )
    if used_percentage is not None:
        pct = int( used_percentage )
        if pct < TOKEN_THRESHOLD_LOW: emoji = '🟢'
        elif pct < TOKEN_THRESHOLD_HIGH: emoji = '🟡'
        else: emoji = '🔴'
        sections.append( f"{emoji} {pct}%" )
    return ' | '.join( sections )


def main( ) -> None:
    ''' Displays token usage from context_window and current directory. '''
    input_data = _json_loads( _stdin.read( ) )
    cwd = _abbreviate_home_in_path( input_data.get( 'cwd', '~' ) )
    branch = _detect_git_branch( input_data.get( 'cwd', '~' ) )
    context_window = input_data.get( 'context_window', { } )
    used_percentage = context_window.get( 'used_percentage' )
    model_info = input_data.get( 'model', { } )
    model_name = model_info.get( 'display_name' )
    status = _format_status( cwd, branch, used_percentage, model_name )
    print( status, end = '' )


if __name__ == '__main__':
    try: main( )
    except Exception as exc:
        print( f"⚠️ {exc}", end = '' )
