#!/bin/bash
# Relay 127.0.0.1:9876 -> $FUSION_BRIDGE_HOST:$FUSION_BRIDGE_PORT, then exec the MCP server.
# The fusion360-mcp Python server always connects to localhost:9876 (hardcoded in the lib).
#
# 2026-10-28: the default target `host.docker.internal` is a Jinn/Docker-era name that does NOT
# resolve on Grimnir (measured: NXDOMAIN). It is deliberately NOT repointed. The real Fusion
# bridge target is Daedalus 192.168.1.10:9876 (see CLAUDE.md gap 1); Daedalus is a confirm-first
# box, so standing up an outbound relay to it is a GATED action, not a code edit. Whoever holds
# that approval sets FUSION_BRIDGE_HOST/FUSION_BRIDGE_PORT explicitly; the default stays dead.
#
# Why the pre-flight resolve check below is load-bearing: the relay used to bind FIRST and
# discover the dead target per-connection, so it accepted every client and then dropped it. A
# probe of 127.0.0.1:9876 therefore SUCCEEDED and proved nothing -- a false green on the one
# port anyone would test to ask "is the Fusion bridge up?". It also outlived its parent as an
# orphan still holding the port (measured 2026-10-28: pid 2327776, 5d5h, reparented to PID 1,
# found by grimnir-master's orphan sweep, not by anything of ours). Unresolvable target now
# yields ECONNREFUSED -- a true negative -- and no bound socket to inherit.

set -u
: "${FUSION_BRIDGE_HOST:=host.docker.internal}"
: "${FUSION_BRIDGE_PORT:=9876}"
export FUSION_BRIDGE_HOST FUSION_BRIDGE_PORT

python3 - <<'EOF' &
import os, socket, sys, threading, time

host = os.environ["FUSION_BRIDGE_HOST"]
port = int(os.environ["FUSION_BRIDGE_PORT"])

def log(msg):
    # stderr ONLY -- stdout is the MCP stdio protocol channel; writing there corrupts the stream
    print(f"fusion-relay: {msg}", file=sys.stderr, flush=True)

# Pre-flight: refuse to bind a port we cannot relay through.
try:
    socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
except socket.gaierror as e:
    log(f"ERR:target-unresolvable {host}:{port} ({e}) -- refusing to bind 127.0.0.1:9876, "
        f"because a listener that drops every connection reads as a live bridge. "
        f"Set FUSION_BRIDGE_HOST/PORT if you hold approval for the real target.")
    sys.exit(3)

def exit_if_orphaned():
    # The wrapper execs the MCP server, so this relay's parent is that server. If it dies we
    # get reparented to PID 1 and would sit on 127.0.0.1:9876 indefinitely. Don't.
    while True:
        if os.getppid() == 1:
            log("ERR:parent-exited -- shutting down rather than orphaning on 127.0.0.1:9876")
            os._exit(0)
        time.sleep(5)

def pipe(src, dst):
    try:
        while chunk := src.recv(4096):
            dst.sendall(chunk)
    finally:
        src.close(); dst.close()

threading.Thread(target=exit_if_orphaned, daemon=True).start()

srv = socket.socket()
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(('127.0.0.1', 9876))
srv.listen(5)
log(f"listening on 127.0.0.1:9876 -> {host}:{port}")

while True:
    client, _ = srv.accept()
    remote = socket.socket()
    try:
        remote.connect((host, port))
    except Exception as e:
        log(f"ERR:relay-connect-failed {host}:{port} ({type(e).__name__}: {e})")
        remote.close(); client.close()   # close BOTH -- the old version leaked `remote`
        continue
    for a, b in [(client, remote), (remote, client)]:
        threading.Thread(target=pipe, args=(a, b), daemon=True).start()
EOF

sleep 0.5  # let the relay bind (or refuse) before the MCP server tries to connect
exec "${HOME}/.local/bin/uvx" fusion360-mcp-server --mode socket
