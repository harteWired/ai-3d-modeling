# 2026-10-28 — the Fusion relay orphan, and the false green it was serving

**Trigger:** grimnir-master's orphan sweep found `pid 2327776  python3 -  uid 999`, cwd
`/opt/fleet/agents/3d-printing`, reparented to PID 1, up 5d5h, **LISTENING on 127.0.0.1:9876 and
accepting connections**. gm correctly declined to kill it (shared uid ⇒ ownership unprovable from
the process) and asked whether it was ours and intended.

## It was ours, and provably so

Not inferred from the cwd — `/proc/2327776/environ` carried
`CLAUDE_CODE_SESSION_ID=afdd6982-…` and `SYSTEMD_EXEC_PID=2327402`, **identical to this session's
own**. And its start epoch was `1792738803`, **byte-identical** to
`systemctl show fleet-agent@3d-printing -p ExecMainStartTimestamp`. So it was spawned at session
launch, by the MCP client, from `scripts/fusion-mcp-wrapper.sh:7` — the backgrounded
`python3 - <<'EOF' &` relay. gm's "timer-driven, 03:00:03" read was a red herring: that is simply
when this agent's unit started (07:00:03 UTC = 03:00 EDT).

## The real defect: it was a FALSE GREEN on the one port anyone would probe

The relay bound `127.0.0.1:9876` **first** and only discovered its target was dead **per
connection** — the target being `host.docker.internal`, the Jinn/Docker-era name CLAUDE.md gap 1
already records as wrong. Measured consequence:

| probe | result |
|---|---|
| `connect('127.0.0.1', 9876)` | **SUCCEEDS in 0.000s** — reads as a live Fusion bridge |
| `getent hosts host.docker.internal` | NXDOMAIN |
| then `recv()` | EOF at +0.074s (warm negative DNS cache); **>5s on the cold first attempt** |

So *"is the Fusion bridge up?"* answered **yes** for five days. `wchan=inet_csk_accept` the whole
time, 0.000s CPU — healthy at every observable, structurally incapable of relaying a byte. Exactly
the global doc's shape: *the failure path produces the reassuring answer.* It also leaked one
`remote` socket fd per failed attempt (the variable stays referenced until the next `accept()`),
which is the unexplained `fd 5` in gm's report.

## Fixed in `scripts/fusion-mcp-wrapper.sh` — fail loud, do not repoint

Deliberately **NOT** repointed at Daedalus `192.168.1.10:9876`. That is the real target, Daedalus
is confirm-first, and standing up an outbound relay to it is a **gated action, not a code edit**.
The default stays dead on purpose; `FUSION_BRIDGE_HOST`/`FUSION_BRIDGE_PORT` let whoever holds
that approval aim it explicitly (same pattern as `CLI_ANYTHING_OPENSCAD` in gap 4).

1. **Pre-flight `getaddrinfo`** — unresolvable target ⇒ log to stderr, `exit 3`, **never bind**.
   A probe then gets `ECONNREFUSED`: a true negative instead of a manufactured all-clear.
2. **Orphan watchdog** — a thread exits the relay once `getppid() == 1`, so it cannot outlive the
   MCP server holding the port again.
3. **`remote.close()`** on the failure path, closing the fd leak.
4. All relay logging goes to **stderr only** — stdout is the MCP stdio protocol channel.

Proven on the real artifact, all three directions:

- **RED** (default dead target): `ERR:target-unresolvable … refusing to bind`, 0 listeners,
  `ECONNREFUSED`, no orphan.
- **GREEN** (local fixture on 19876): binds, and `hello-bridge` → `FIXTURE-SAW:hello-bridge`
  end to end.
- **WATCHDOG**: parent killed ⇒ listener gone by t+4s, `ERR:parent-exited` in stderr.

The orphan itself was reaped by PID (identity re-confirmed immediately before `kill -TERM`:
cmdline + session id + cwd), then verified **by port** — 0 listeners, `ECONNREFUSED` — with
`:49876` confirmed untouched. Per the `pkill -f` ban, no pattern was used at any point.

## Second, independent blocker on the Fusion MCP — gap 1 is incomplete

The session banner reports `fusion (CONNECT_TIMEOUT)`. Running the wrapper directly shows the
exec'd server **crashing at startup**, which the client can only see as a timeout:

```
fusion360_mcp/server.py:53 in main
    @app.list_tools()
AttributeError: 'Server' object has no attribute 'list_tools'
```

`uvx` resolves `fusion360-mcp-server` against a current `mcp` library whose `Server` API no longer
carries `list_tools`. ⇒ **Even with Fusion running on Daedalus and an approved relay, the MCP
server would not start.** CLAUDE.md gap 1 says the blocker is "Fusion must be started by Matt by
hand"; that is true and **not sufficient** — there is a second, purely local blocker, and this one
is measurable here without touching a confirm-first box. It needs a pinned `mcp` version or a
maintained fork, which is a separate task and was not attempted here.
