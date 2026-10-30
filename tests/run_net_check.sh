#!/usr/bin/env bash
set -u
cd /home/riyo/Documentos/game || exit 1
timeout 30 godot --headless --path . -- --host > /tmp/opencode/host_check.log 2>&1 &
host_pid=$!
sleep 2
timeout 45 godot --headless --path . --script tests/net_client_test.gd
status=$?
kill "$host_pid" 2>/dev/null
wait "$host_pid" 2>/dev/null
exit "$status"
