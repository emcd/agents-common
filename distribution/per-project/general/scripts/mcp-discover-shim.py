#!/usr/bin/env python3
# vim: set filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-

''' Stdio MCP shim: answer server/discover with -32601 for rmcp 1.x.

    TEMPORARY compatibility content for Antigravity CLI, which probes
    MCP servers with ``server/discover`` before ``initialize``
    (MCP 2026-07-28 / SEP-2575). ``agentmux`` on ``rmcp`` 1.x exits with
    ``ExpectedInitializeRequest`` on that probe instead of answering.
    Removal trigger: ``agentmux`` release on ``rmcp >= 3.x`` with
    ``server/discover`` support, at which point invoke
    ``agentmux host mcp`` directly. Populate-managed and git-excluded;
    never stage this file.

    Forwarding runs as a single-threaded event loop over nonblocking
    file descriptors, so no lifecycle decision ever blocks on IO: slow
    or stalled readers in either direction apply backpressure through
    bounded buffers instead of hanging shutdown. Shutdown is bounded
    everywhere (drain, wait, terminate, kill each carry timeouts).
'''


import contextlib
import json
import os
import select
import signal
import subprocess
import sys
import threading
import time


_MIN_ARGV = 2
_METHOD_NOT_FOUND = -32601
_READ_SIZE = 65536
_SELECT_TIMEOUT = 1.0
_DRAIN_TIMEOUT = 5.0
_EXIT_TIMEOUT = 10.0
_MAX_PENDING = 64 * 1024 * 1024


def _build_not_found_reply( request_id ) -> bytes:
    reply = {
        'jsonrpc': '2.0',
        'id': request_id,
        'error': {
            'code': _METHOD_NOT_FOUND,
            'message': 'Method not found',
        },
    }
    return (
        json.dumps( reply, separators = ( ',', ':' ) ) + '\n'
    ).encode( 'utf-8' )


class _Forwarder:
    ''' Single-threaded stdio event loop between client and child.

        All descriptors are nonblocking; every wait carries a timeout,
        so child exit, signal shutdown, and EOF propagation stay
        observable under backpressure in either direction. Pending
        buffers are capped at the read gates: stdin stops being polled
        once unread, unframed, or undelivered bytes reach the cap
        (backpressure correctly reaches the stalled reader instead of
        growing memory). A dead child never cuts the drain short:
        reaping first flushes queued and unread output under a
        wall-clock bound, so ordinary replies are never silently
        truncated — only a client stalled past the bound loses bytes.
    '''

    def __init__( self, child ):
        self.child = child
        if child.stdin is None or child.stdout is None:
            raise ValueError
        self.stdin_fd = sys.stdin.fileno( )
        self.stdout_fd = sys.stdout.fileno( )
        self.child_stdin = child.stdin
        self.child_stdout = child.stdout
        self.child_stdin_no = child.stdin.fileno( )
        self.child_stdout_no = child.stdout.fileno( )
        for fd in (
            self.stdin_fd,
            self.stdout_fd,
            self.child_stdin_no,
            self.child_stdout_no,
        ):
            os.set_blocking( fd, False )
        self.to_child = bytearray( )
        self.to_parent = bytearray( )
        self.in_partial = bytearray( )
        self.stdout_broken = False
        self.stdin_eof = False
        self.child_out_eof = False
        self.child_stdin_closed = False
        self.stdin_closed_at = 0.0

    def run( self, stop_event ) -> None:
        ''' Forwards until shutdown, death, exhaustion, or broken sink.

            A broken stdout ends the loop promptly: with no readable
            client, queued bytes are undeliverable and further
            forwarding only burns child compute. Reaping reports the
            abandonment instead of hanging on still-open stdin.
        '''
        while True:
            if stop_event.is_set( ):
                return
            if self.child.poll( ) is not None:
                return
            if self.stdout_broken:
                return
            readable, writable = self._select_sets( )
            try:
                got_readable, got_writable, _ = select.select(
                    readable, writable, [ ], _SELECT_TIMEOUT )
            except OSError:
                return
            for fd in got_readable:
                self._on_readable( fd )
            for fd in got_writable:
                self._on_writable( fd )
            self._pump_eof_states( )
            if self._forwarding_done( ):
                return

    def _select_sets( self ):
        readable = [ ]
        if (
            not self.stdin_eof
            and len( self.to_child ) < _MAX_PENDING
            and len( self.to_parent ) < _MAX_PENDING
            and len( self.in_partial ) < _MAX_PENDING
        ):
            readable.append( self.stdin_fd )
        if not self.child_out_eof and len( self.to_parent ) < _MAX_PENDING:
            readable.append( self.child_stdout_no )
        writable = [ ]
        if self.to_child and not self.child_stdin_closed:
            writable.append( self.child_stdin_no )
        if self.to_parent and not self.stdout_broken:
            writable.append( self.stdout_fd )
        return readable, writable

    def _on_readable( self, fd ) -> None:
        try:
            chunk = os.read( fd, _READ_SIZE )
        except ( BlockingIOError, InterruptedError ):
            return
        except OSError:
            chunk = b''
        if not chunk:
            if fd == self.stdin_fd:
                self.stdin_eof = True
            else:
                self.child_out_eof = True
            return
        if fd == self.stdin_fd:
            self.in_partial += chunk
            self._extract_frames( )
        else:
            self.to_parent += chunk

    def _extract_frames( self ) -> None:
        while True:
            newline = self.in_partial.find( b'\n' )
            if newline < 0:
                break
            raw_line = bytes( self.in_partial[ : newline + 1 ] )
            del self.in_partial[ : newline + 1 ]
            self._route_frame( raw_line )

    def _route_frame( self, raw_line ) -> None:
        try:
            message = json.loads( raw_line )
        except ( UnicodeDecodeError, json.JSONDecodeError ):
            message = None
        if (
            isinstance( message, dict )
            and message.get( 'method' ) == 'server/discover'
            and 'id' in message
        ):
            self.to_parent += _build_not_found_reply(
                message[ 'id' ] )
            return
        self.to_child += raw_line

    def _on_writable( self, fd ) -> None:
        if fd == self.child_stdin_no:
            pending = self.to_child
        else:
            pending = self.to_parent
        if not pending:
            return
        try:
            written = os.write( fd, bytes( pending ) )
        except ( BlockingIOError, InterruptedError ):
            return
        except OSError:
            self._on_write_error( fd )
            return
        del pending[ : written ]

    def _on_write_error( self, fd ) -> None:
        if fd == self.child_stdin_no:
            # The child closed its stdin: pending bytes are
            # undeliverable, so drop them instead of holding the
            # forwarding loop open on a dead end.
            self.to_child.clear( )
            self._close_child_stdin( )
        else:
            # Our own stdout is broken (client went away): no later
            # write can succeed, so stop selecting it instead of
            # busy-spinning on an always-writable broken pipe.
            self.stdout_broken = True

    def _pump_eof_states( self ) -> None:
        if self.stdin_eof and self.in_partial:
            self._route_frame( bytes( self.in_partial ) )
            self.in_partial = bytearray( )
        if (
            self.stdin_eof
            and not self.to_child
            and not self.child_stdin_closed
        ):
            self._close_child_stdin( )
            self.stdin_closed_at = time.monotonic( )

    def _close_child_stdin( self ) -> None:
        with contextlib.suppress( OSError ):
            self.child_stdin.close( )
        self.child_stdin_closed = True

    def _forwarding_done( self ) -> bool:
        if not self.stdin_eof or not self.child_stdin_closed:
            return False
        if self.to_child:
            return False
        if self.child.poll( ) is None:
            idle_for = time.monotonic( ) - self.stdin_closed_at
            return idle_for >= _EXIT_TIMEOUT
        return True

    def reap( self ) -> int:
        ''' Drains queued output, then reaps the child under timeouts.

            The drain runs whether the child is alive or already dead:
            returning on child exit must not discard unread or queued
            bytes. Only a client stalled past the wall-clock bound
            loses output, and that loss is reported: a drain that gives
            up with output still queued turns an otherwise clean child
            status into a nonzero exit (124), while a meaningful
            nonzero child status is always preserved.
            Negative signal statuses normalize to shell convention
            (128 + signal number); an unreapable child reports 124
            after logging, leaving the orphan for init.
        '''
        drained = self._drain_outputs( )
        try:
            code = self.child.wait( timeout = _EXIT_TIMEOUT )
        except subprocess.TimeoutExpired:
            sys.stderr.write(
                "mcp-discover-shim: child ignored shutdown; "
                "terminating.\n" )
            code = None
        if code is None:
            self.child.terminate( )
            try:
                code = self.child.wait( timeout = _EXIT_TIMEOUT )
            except subprocess.TimeoutExpired:
                self.child.kill( )
                try:
                    code = self.child.wait(
                        timeout = _EXIT_TIMEOUT )
                except subprocess.TimeoutExpired:
                    sys.stderr.write(
                        "mcp-discover-shim: child unreaped after "
                        "kill; leaving it for init.\n" )
                    return 124
        if code < 0:
            return 128 - code
        if not drained and code == 0:
            return 124
        return code

    def _drain_outputs( self ) -> bool:
        ''' Flushes unread child output and queued bytes, bounded.

            Reads the child path to EOF and writes everything queued
            to our stdout; stops early on a broken stdout (the client
            is gone, so delivery is impossible) or the wall-clock bound
            (stalled client), logging the shortfall in both cases.
            Returns True when fully drained, False when output was
            left behind.
        '''
        if self.stdout_broken:
            sys.stderr.write(
                "mcp-discover-shim: stdout broken; "
                "abandoning queued output.\n" )
            return False
        deadline = time.monotonic( ) + _DRAIN_TIMEOUT
        while True:
            if self.child_out_eof and not self.to_parent:
                return True
            if self.stdout_broken:
                sys.stderr.write(
                    "mcp-discover-shim: stdout broke during drain; "
                    "abandoning queued output.\n" )
                return False
            remaining = deadline - time.monotonic( )
            if remaining <= 0:
                sys.stderr.write(
                    "mcp-discover-shim: drain bound exceeded with "
                    "output still queued; truncating.\n" )
                return False
            readable = [ ]
            if (
                not self.child_out_eof
                and len( self.to_parent ) < _MAX_PENDING
            ):
                readable.append( self.child_stdout_no )
            writable = [ ]
            if self.to_parent and not self.stdout_broken:
                writable.append( self.stdout_fd )
            if not readable and not writable:
                return True
            try:
                got_readable, got_writable, _ = select.select(
                    readable, writable, [ ], remaining )
            except OSError:
                return False
            for fd in got_readable:
                self._on_readable( fd )
            for fd in got_writable:
                self._on_writable( fd )


def _pump_stdin_blocking( child ) -> None:
    ''' Forwards stdin to the child with blocking reads.

        Shares the discover-reply rule with the event loop; used only
        where descriptor polling is unavailable.
    '''
    import contextlib
    child_stdin = child.stdin
    if child_stdin is None:
        return
    try:
        while True:
            line = sys.stdin.buffer.readline( )
            if not line:
                break
            try:
                message = json.loads( line )
            except ( UnicodeDecodeError, json.JSONDecodeError ):
                message = None
            if (
                isinstance( message, dict )
                and message.get( 'method' ) == 'server/discover'
                and 'id' in message
            ):
                payload = _build_not_found_reply( message[ 'id' ] )
                try:
                    sys.stdout.buffer.write( payload )
                    sys.stdout.buffer.flush( )
                except OSError:
                    break
                continue
            try:
                child_stdin.write( line )
                child_stdin.flush( )
            except ( BrokenPipeError, OSError ):
                break
    finally:
        with contextlib.suppress( OSError ):
            child_stdin.close( )


def _run_blocking_fallback( child ) -> int:
    ''' Best-effort forwarding without descriptor polling.

        Platforms without select( ) on pipes get plain blocking IO;
        lifecycle guarantees are POSIX-only and documented as such.
    '''
    import contextlib
    reader = threading.Thread(
        target = _pump_stdin_blocking, args = ( child, ),
        daemon = True,
    )
    reader.start( )
    child_stdout = child.stdout
    if child_stdout is None:
        return 1
    with contextlib.suppress( BrokenPipeError, OSError ):
        while True:
            line = child_stdout.readline( )
            if not line:
                break
            sys.stdout.buffer.write( line )
            sys.stdout.buffer.flush( )
    reader.join( timeout = 5.0 )
    code = child.wait( )
    if code < 0:
        return 128 - code
    return code


def _run_forwarder( child ) -> int:
    ''' Runs the event loop with signal-driven bounded shutdown. '''
    stop_event = threading.Event( )

    def _forward_signal( signum, _frame ):
        stop_event.set( )
        if child.poll( ) is None:
            with contextlib.suppress( ProcessLookupError, OSError ):
                child.send_signal( signum )

    signal.signal( signal.SIGTERM, _forward_signal )
    signal.signal( signal.SIGINT, _forward_signal )

    if sys.platform == 'win32':
        return _run_blocking_fallback( child )
    try:
        forwarder = _Forwarder( child )
    except OSError as exception:
        sys.stderr.write(
            f"mcp-discover-shim: cannot use event loop: {exception}\n" )
        return _run_blocking_fallback( child )
    forwarder.run( stop_event )
    return forwarder.reap( )


def main( ) -> int:
    if len( sys.argv ) < _MIN_ARGV:
        sys.stderr.write(
            'usage: mcp-discover-shim.py <command> [args...]\n'
        )
        return 2

    try:
        child = subprocess.Popen(  # noqa: S603
            sys.argv[ 1: ],
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = None,
        )
    except FileNotFoundError as exception:
        sys.stderr.write(
            f"mcp-discover-shim: cannot execute {sys.argv[1]!r}: "
            f"{exception}\n"
        )
        return 127
    if child.stdin is None or child.stdout is None:
        return 1
    return _run_forwarder( child )


if __name__ == '__main__':
    raise SystemExit( main( ) )
