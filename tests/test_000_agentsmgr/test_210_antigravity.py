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


''' Assert correct Antigravity coder support. '''


import json
import subprocess
import sys
import time as _time

from pathlib import Path

import pytest

from . import __


def _project_root( ) -> Path:
    return Path( __file__ ).resolve( ).parents[ 2 ]


def test_210_antigravity_renderer_is_registered( ):
    renderers = __.cache_import_module( 'agentsmgr.renderers' )
    renderer = renderers.RENDERERS[ 'antigravity' ]
    assert renderer.name == 'antigravity'
    assert renderer.mode_default == 'per-project'
    assert renderer.modes_available == frozenset( ( 'per-project', ) )
    assert renderer.memory_filename == 'AGENTS.md'
    assert renderer.item_types_available == frozenset( )


def test_211_antigravity_renderer_provides_no_project_symlinks(
    tmp_path
):
    # Antigravity consumes the shared .agents symlink and root AGENTS.md;
    # no .antigravity root link exists.
    renderers = __.cache_import_module( 'agentsmgr.renderers' )
    renderer = renderers.RENDERERS[ 'antigravity' ]
    assert tuple( renderer.provide_project_symlinks( tmp_path ) ) == ( )


def test_212_antigravity_resolves_per_project_only( ):
    resolver = __.cache_import_module( 'agentsmgr.resolver' )
    names_default = dict( resolver.resolve_coders( [ 'antigravity' ] ) )
    assert 'antigravity' in names_default
    names_project = dict( resolver.resolve_coders(
        [ 'antigravity' ], mode = 'per-project' ) )
    assert 'antigravity' in names_project
    names_user = dict( resolver.resolve_coders(
        [ 'antigravity' ], mode = 'per-user' ) )
    assert 'antigravity' not in names_user


def _render_antigravity_mcp_config( project_name: str ) -> dict:
    import jinja2
    template = (
        _project_root( )
        / 'template' / '.auxiliary' / 'agents'
        / 'mcp_config.json.jinja'
    ).read_text( encoding = 'utf-8' )
    return json.loads( jinja2.Template( template ).render(
        project_name = project_name,
        coders = [ 'antigravity', 'claude', 'codex', 'opencode' ] ) )


def _assert_no_env_block( node ) -> None:
    if isinstance( node, dict ):
        assert 'env' not in node, (
            "Antigravity takes env literally (no ${VAR:-} expansion); "
            "servers must inherit the process environment" )
        for value in node.values( ): _assert_no_env_block( value )
    elif isinstance( node, list ):
        for value in node: _assert_no_env_block( value )


def test_213_antigravity_mcp_config_renders_valid( ):
    # The rendered file is always complete: discoverability is gated
    # at the copier _exclude level (asserted below), so a default
    # render never references the shim it does not ship.
    config = _render_antigravity_mcp_config( 'test-proj' )
    _assert_no_env_block( config )
    agentmux = config[ 'mcpServers' ][ 'agentmux' ]
    assert agentmux[ 'timeoutSeconds' ] == 900
    assert agentmux[ 'command' ] == 'python3'
    assert agentmux[ 'args' ][ 0 ] == (
        '.auxiliary/agents/scripts/mcp-discover-shim.py' )
    assert config[ 'mcpServers' ][ 'nb' ][ 'args' ][ 1 ] == 'test-proj'
    default_excludes = set( _render_exclude_patterns(
        [ 'claude', 'codex', 'opencode' ] ) )
    assert '.auxiliary/agents/mcp_config.json' in default_excludes
    assert (
        '.auxiliary/agents/ANTIGRAVITY-NAMESPACE-NOTE.md'
        in default_excludes )
    selected_excludes = _render_exclude_patterns(
        [ 'antigravity', 'claude', 'codex', 'opencode' ] )
    assert all(
        'mcp_config' not in str( entry )
        and 'ANTIGRAVITY' not in str( entry )
        for entry in selected_excludes )


def _render_exclude_patterns( coders: list ) -> list:
    import jinja2
    import yaml
    copier = yaml.safe_load(
        ( _project_root( ) / 'copier.yaml' ).read_text(
            encoding = 'utf-8' ) )
    return [
        jinja2.Template( pattern ).render( coders = coders )
        for pattern in copier.get( '_exclude', [ ] ) ]


def _shim_path( ) -> Path:
    return (
        _project_root( )
        / 'distribution' / 'per-project' / 'general' / 'scripts'
        / 'mcp-discover-shim.py' )


def test_214_support_shim_usage_error_without_command( ):
    result = subprocess.run(  # noqa: S603
        [ sys.executable, str( _shim_path( ) ) ],
        capture_output = True, check = False, timeout = 30 )
    assert result.returncode == 2
    assert b'usage:' in result.stderr


def test_215_support_shim_answers_discover_and_forwards( ):
    # Fake upstream: one canned reply per input line received.
    upstream = (
        "import sys;"
        "[sys.stdout.write("
        "'{\"jsonrpc\":\"2.0\",\"id\":0,\"result\":\"proxied\"}\\n'"
        ") or sys.stdout.flush() for _ in sys.stdin]"
    )
    discover = (
        b'{"jsonrpc":"2.0","id":1,'
        b'"method":"server/discover","params":{}}\n' )
    passthrough = (
        b'{"jsonrpc":"2.0","id":2,"method":"ping","params":{}}\n' )
    result = subprocess.run(  # noqa: S603
        [ sys.executable, str( _shim_path( ) ),
          sys.executable, '-c', upstream ],
        input = discover + passthrough,
        capture_output = True, check = False, timeout = 30 )
    assert result.returncode == 0
    replies = [
        json.loads( line )
        for line in result.stdout.decode( 'utf-8' ).splitlines( )
        if line.strip( )
    ]
    by_id = { reply.get( 'id' ): reply for reply in replies }
    assert by_id[ 1 ][ 'error' ][ 'code' ] == -32601
    assert any(
        reply.get( 'result' ) == 'proxied' for reply in replies )


def test_216_support_scripts_copied_only_for_antigravity( tmp_path ):
    population = __.cache_import_module( 'agentsmgr.population' )
    distribution = tmp_path / 'distribution'
    scripts = (
        distribution / 'per-project' / 'general' / 'scripts' )
    scripts.mkdir( parents = True )
    ( scripts / 'mcp-discover-shim.py' ).write_text(
        '#!/usr/bin/env python3\n', encoding = 'utf-8' )
    target = tmp_path / 'project'
    target.mkdir( )
    attempted, written, entries = (
        population._copy_support_scripts_from_distribution(
            distribution, target, [ 'claude' ], simulate = False ) )
    assert ( attempted, written ) == ( 0, 0 )
    # Ignore entry retained even when deselected: the managed
    # git-exclude block is rebuilt every run.
    assert entries == (
        '.auxiliary/agents/scripts/mcp-discover-shim.py', )
    assert not ( target / '.auxiliary' ).exists( )
    attempted, written, entries = (
        population._copy_support_scripts_from_distribution(
            distribution, target, [ 'antigravity' ],
            simulate = False ) )
    assert attempted == 1
    assert written == 1
    dest = (
        target / '.auxiliary' / 'agents' / 'scripts'
        / 'mcp-discover-shim.py' )
    assert dest.is_file( )
    assert entries == (
        '.auxiliary/agents/scripts/mcp-discover-shim.py', )


def test_217_deselect_leaves_stale_shim_ignored( tmp_path ):
    # Deselect never deletes: the stale shim stays on disk (manual
    # cleanup per the namespace note) but the exact-path ignore entry
    # is retained so it never surfaces as untracked. Same when the
    # distribution no longer carries the source.
    population = __.cache_import_module( 'agentsmgr.population' )
    distribution = tmp_path / 'distribution'
    scripts = (
        distribution / 'per-project' / 'general' / 'scripts' )
    scripts.mkdir( parents = True )
    ( scripts / 'mcp-discover-shim.py' ).write_text(
        '# owned\n', encoding = 'utf-8' )
    target = tmp_path / 'project'
    dest_dir = target / '.auxiliary' / 'agents' / 'scripts'
    dest_dir.mkdir( parents = True )
    ( dest_dir / 'mcp-discover-shim.py' ).write_text(
        '# owned\n', encoding = 'utf-8' )
    attempted, written, entries = (
        population._copy_support_scripts_from_distribution(
            distribution, target, [ 'claude' ], simulate = False ) )
    assert ( attempted, written ) == ( 0, 0 )
    assert ( dest_dir / 'mcp-discover-shim.py' ).is_file( )
    assert entries == (
        '.auxiliary/agents/scripts/mcp-discover-shim.py', )
    # Source disappears upstream: ignore retained regardless.
    ( scripts / 'mcp-discover-shim.py' ).unlink( )
    attempted, written, entries = (
        population._copy_support_scripts_from_distribution(
            distribution, target, [ 'antigravity' ],
            simulate = False ) )
    assert ( attempted, written ) == ( 0, 0 )
    assert entries == (
        '.auxiliary/agents/scripts/mcp-discover-shim.py', )


@pytest.mark.skipif(
    sys.platform == 'win32',
    reason = 'POSIX open-stdin lifecycle semantics required: on '
    'Windows runners the console-attached shim holding an open '
    'stdin pipe is killed with STATUS_CONTROL_C_EXIT instead of '
    'surfacing the child status; the win32 fallback path is '
    'documented best-effort only' )
def test_218_shim_exits_with_child_status_on_open_stdin( ):
    # Regression: early child exit while the client holds stdin open
    # must surface the child status instead of hanging on input.
    child_code = (
        "import sys, time; time.sleep(0.5); sys.exit(23)" )
    start = _time.monotonic( )
    with subprocess.Popen(  # noqa: S603
        [ sys.executable, str( _shim_path( ) ),
          sys.executable, '-c', child_code ],
        stdin = subprocess.PIPE,
        stdout = subprocess.DEVNULL,
        stderr = subprocess.DEVNULL,
    ) as process:
        try:
            returncode = process.wait( timeout = 20 )
        except subprocess.TimeoutExpired as error:
            process.kill( )
            raise AssertionError(
                "shim hung on open stdin after child exit" ) from error
    elapsed = _time.monotonic( ) - start
    assert returncode == 23
    assert elapsed < 20


def test_219_shim_forwards_both_frames_with_stdin_open( ):
    # Two complete frames written together must both be forwarded
    # before EOF. Observation uses a reader thread plus queue instead
    # of select() so the pin is portable (win32 select is
    # sockets-only); stdin stays open throughout the observation.
    import queue as _frame_queue
    import threading as _frame_reader
    upstream = (
        "import sys\n"
        "for _line in sys.stdin:\n"
        "    sys.stdout.write("
        "'{\"jsonrpc\":\"2.0\",\"id\":0,\"result\":\"proxied\"}\\n')\n"
        "    sys.stdout.flush()\n" )
    frame_one = (
        b'{"jsonrpc":"2.0","id":1,'
        b'"method":"server/discover","params":{}}\n' )
    frame_two = (
        b'{"jsonrpc":"2.0","id":2,"method":"ping","params":{}}\n' )
    with subprocess.Popen(  # noqa: S603
        [ sys.executable, str( _shim_path( ) ),
          sys.executable, '-c', upstream ],
        stdin = subprocess.PIPE,
        stdout = subprocess.PIPE,
        stderr = subprocess.DEVNULL,
        bufsize = 0,
    ) as process:
        assert process.stdin is not None
        assert process.stdout is not None
        lines: _frame_queue.Queue[ bytes ] = _frame_queue.Queue( )
        def _pump( ) -> None:
            try:
                while True:
                    line = process.stdout.readline( )
                    if not line:
                        break
                    lines.put( line )
            except ValueError:
                pass
        reader = _frame_reader.Thread( target = _pump, daemon = True )
        reader.start( )
        process.stdin.write( frame_one + frame_two )
        process.stdin.flush( )
        try:
            first = lines.get( timeout = 20 )
            second = lines.get( timeout = 20 )
        except _frame_queue.Empty as error:
            process.kill( )
            raise AssertionError(
                "second frame was not forwarded before EOF" ) from error
        replies = [ json.loads( first ), json.loads( second ) ]
        process.stdin.close( )
        try:
            returncode = process.wait( timeout = 20 )
        except subprocess.TimeoutExpired as error:
            process.kill( )
            raise AssertionError(
                "shim hung after forwarding both frames" ) from error
    assert returncode == 0
    by_id = { reply.get( 'id' ): reply for reply in replies }
    assert by_id[ 1 ][ 'error' ][ 'code' ] == -32601
    assert any( reply.get( 'result' ) == 'proxied' for reply in replies )


@pytest.mark.skipif(
    sys.platform == 'win32',
    reason = 'POSIX signal semantics required' )
def test_220_shim_term_enters_bounded_shutdown_open_stdin( ):
    # Open-stdin signal case: child ignores SIGTERM and announces
    # readiness while the client holds stdin open. SIGTERM to the shim
    # must enter bounded shutdown (kill fallback) instead of leaving
    # both alive; the kill status normalizes to shell convention.
    import select as _select_signal
    child_code = (
        "import signal, sys, time; "
        "signal.signal(signal.SIGTERM, signal.SIG_IGN); "
        "print('ready', flush=True); "
        "time.sleep(300)" )
    with subprocess.Popen(  # noqa: S603
        [ sys.executable, str( _shim_path( ) ),
          sys.executable, '-c', child_code ],
        stdin = subprocess.PIPE,
        stdout = subprocess.PIPE,
        stderr = subprocess.DEVNULL,
        bufsize = 0,
    ) as process:
        assert process.stdin is not None
        assert process.stdout is not None
        ready, _, _ = _select_signal.select(
            [ process.stdout ], [ ], [ ], 20 )
        assert ready, "child never announced readiness"
        assert process.stdout.readline( ).strip( ) == b'ready'
        process.terminate( )
        try:
            returncode = process.wait( timeout = 60 )
        except subprocess.TimeoutExpired as error:
            process.kill( )
            raise AssertionError(
                "shim ignored SIGTERM with stdin open" ) from error
    assert returncode == 137


@pytest.mark.skipif(
    sys.platform == 'win32',
    reason = 'POSIX signal semantics required' )
def test_221_shim_term_under_backpressure( ):
    # Backpressured TERM: child never reads stdin and ignores SIGTERM;
    # one complete ~256 KiB frame fills the pipe while input stays
    # open. The lifecycle supervisor must never block on the stalled
    # write: SIGTERM enters bounded shutdown ending in kill (137).
    import select as _select_backpressure
    child_code = (
        "import signal, sys, time; "
        "signal.signal(signal.SIGTERM, signal.SIG_IGN); "
        "print('ready', flush=True); "
        "time.sleep(300)" )
    big_frame = b'x' * ( 256 * 1024 ) + b'\n'
    with subprocess.Popen(  # noqa: S603
        [ sys.executable, str( _shim_path( ) ),
          sys.executable, '-c', child_code ],
        stdin = subprocess.PIPE,
        stdout = subprocess.PIPE,
        stderr = subprocess.DEVNULL,
        bufsize = 0,
    ) as process:
        assert process.stdin is not None
        assert process.stdout is not None
        ready, _, _ = _select_backpressure.select(
            [ process.stdout ], [ ], [ ], 20 )
        assert ready, "child never announced readiness"
        assert process.stdout.readline( ).strip( ) == b'ready'
        process.stdin.write( big_frame )
        process.stdin.flush( )
        process.terminate( )
        try:
            returncode = process.wait( timeout = 90 )
        except subprocess.TimeoutExpired as error:
            process.kill( )
            raise AssertionError(
                "shim hung under backpressured TERM" ) from error
    assert returncode == 137


def test_222_shim_delivers_complete_reply_after_exit( ):
    # Truncation regression: child writes one reply over the 64 KiB
    # pipe capacity and exits while the client delays reading. The
    # shim must drain unread + queued output under the wall-clock
    # bound and deliver the complete frame before exiting 0 — not
    # cut off at child death with a partial line. The payload is
    # generated inside the child (short launch command): embedding
    # it in -c would exceed Windows' 32,767-char command line limit.
    import time as _time_backpressure
    child_code = (
        "import sys; "
        "sys.stdout.buffer.write("
        "b'{\"jsonrpc\":\"2.0\",\"id\":7,\"result\":\"' + "
        "b'z' * 65600 + b'\"}\\n'); "
        "sys.stdout.flush()" )
    expected = (
        b'{"jsonrpc":"2.0","id":7,"result":"' + b'z' * 65600
        + b'"}\n' )
    assert len( expected ) > 65536
    start = _time_backpressure.monotonic( )
    with subprocess.Popen(  # noqa: S603
        [ sys.executable, str( _shim_path( ) ),
          sys.executable, '-c', child_code ],
        stdin = subprocess.PIPE,
        stdout = subprocess.PIPE,
        stderr = subprocess.DEVNULL,
        bufsize = 0,
    ) as process:
        assert process.stdin is not None
        assert process.stdout is not None
        process.stdin.close( )
        _time_backpressure.sleep( 2.0 )
        received = process.stdout.read( )
        returncode = process.wait( timeout = 60 )
    elapsed = _time_backpressure.monotonic( ) - start
    assert returncode == 0
    assert elapsed < 60
    assert received == expected
    assert json.loads( received )[ 'id' ] == 7


@pytest.mark.skipif(
    sys.platform == 'win32',
    reason = 'bounded drain-and-report is POSIX-only' )
def test_223_shim_reports_truncated_drain_as_failure( ):
    # Stalled client: child exits 0 after a big reply nobody reads.
    # The bounded drain must give up on schedule, and the shim must
    # NOT report successful passthrough for a known-incomplete drain:
    # a clean child status becomes 124, while a meaningful nonzero
    # child status would be preserved. The payload is generated
    # inside the child (short launch command): embedding it in -c
    # would exceed Windows' 32,767-char command line limit.
    child_code = (
        "import sys; "
        "sys.stdout.buffer.write("
        "b'{\"jsonrpc\":\"2.0\",\"id\":7,\"result\":\"' + "
        "b'z' * 65600 + b'\"}\\n'); "
        "sys.stdout.flush()" )
    with subprocess.Popen(  # noqa: S603
        [ sys.executable, str( _shim_path( ) ),
          sys.executable, '-c', child_code ],
        stdin = subprocess.PIPE,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        bufsize = 0,
    ) as process:
        assert process.stdin is not None
        assert process.stderr is not None
        process.stdin.close( )
        try:
            returncode = process.wait( timeout = 60 )
        except subprocess.TimeoutExpired as error:
            process.kill( )
            raise AssertionError(
                "shim hung on stalled-client drain" ) from error
        stderr = process.stderr.read( )
    assert returncode == 124
    assert b'truncat' in stderr


@pytest.mark.skipif(
    sys.platform == 'win32',
    reason = 'bounded reap with abandon-report is POSIX-only: the '
    'win32 fallback has no bounded wait/terminate/kill chain' )
def test_224_shim_broken_stdout_abandons_and_reaps( ):
    # Abrupt client disconnect with stdin held open: the client closes
    # only the read end, submits one request, and the child replies
    # then sleeps. A broken pipe is always reported writable, so the
    # shim must notice EPIPE, abandon the queue (no waiting on the
    # still-open stdin), and reap the orphaned child — instead of
    # hanging with no abandon diagnostic.
    import select as _select_broken
    child_code = (
        "import sys, time; print('ready', flush=True); "
        "time.sleep(300)" )
    discover = (
        b'{"jsonrpc":"2.0","id":1,'
        b'"method":"server/discover","params":{}}\n' )
    start = _time.monotonic( )
    with subprocess.Popen(  # noqa: S603
        [ sys.executable, str( _shim_path( ) ),
          sys.executable, '-c', child_code ],
        stdin = subprocess.PIPE,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        bufsize = 0,
    ) as process:
        assert process.stdin is not None
        assert process.stdout is not None
        assert process.stderr is not None
        ready, _, _ = _select_broken.select(
            [ process.stdout ], [ ], [ ], 20 )
        assert ready, "child never announced readiness"
        assert process.stdout.readline( ).strip( ) == b'ready'
        process.stdout.close( )
        process.stdin.write( discover )
        process.stdin.flush( )
        try:
            returncode = process.wait( timeout = 90 )
        except subprocess.TimeoutExpired as error:
            process.kill( )
            raise AssertionError(
                "shim hung on broken stdout with stdin open" ) from error
        stderr = process.stderr.read( )
    elapsed = _time.monotonic( ) - start
    # Terminating the orphaned sleeper reports shell-convention 143;
    # the 'abandoning' line proves the immediate path ran instead of
    # hanging on the still-open stdin.
    assert returncode == 143
    assert elapsed < 60
    assert b'abandon' in stderr
