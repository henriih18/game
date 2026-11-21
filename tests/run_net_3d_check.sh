#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/.." || exit 1
mkdir -p /tmp/opencode
timeout 30 godot --headless --path . -- --host3d --nettest > /tmp/opencode/host3d_check.log 2>&1 &
host_pid=$!
sleep 2
timeout 45 godot --headless --path . tests/fm_net_probe.tscn > /tmp/opencode/net3d_probe.log 2>&1
status=$?
kill "$host_pid" 2>/dev/null
wait "$host_pid" 2>/dev/null
cat /tmp/opencode/net3d_probe.log
exit "$status"
