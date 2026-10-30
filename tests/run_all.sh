#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."

echo "== Vertical slice =="
timeout 45 godot --headless --path . tests/fm_slice_smoke.tscn

echo "== Juego 2D =="
timeout 60 godot --headless --path . --script tests/test_main_2d.gd

echo "== Red 2D =="
timeout 70 bash tests/run_net_check.sh
