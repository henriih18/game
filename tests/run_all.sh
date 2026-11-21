#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."

echo "== Vertical slice Z10 -> Recepcion =="
timeout 120 godot --headless --path . tests/fm_vslice_smoke.tscn
timeout 120 godot --headless --path . tests/fm_vslice_walk.tscn
timeout 60 godot --headless --path . tests/fm_vslice_chase.tscn
timeout 60 godot --headless --path . tests/fm_traversal_smoke.tscn

echo "== Inventario, extracción y navegación =="
timeout 60 godot --headless --path . tests/fm_inventory_smoke.tscn
timeout 90 godot --headless --path . tests/fm_inventory_flow.tscn
timeout 60 godot --headless --path . tests/fm_inventory_ui_smoke.tscn
timeout 60 godot --headless --path . tests/fm_extraction_chase.tscn
timeout 90 godot --headless --path . tests/fm_nav_long_chase.tscn
timeout 90 godot --headless --path . tests/fm_desk_chase.tscn
timeout 60 godot --headless --path . tests/fm_reception_hide.tscn
timeout 90 godot --headless --path . tests/fm_queue_chase.tscn
timeout 90 godot --headless --path . tests/fm_extraction_capture.tscn

echo "== Partida completa con IA activa =="
timeout 150 godot --headless --path . tests/fm_full_run.tscn

echo "== Nivel 1 V06 =="
timeout 180 godot --headless --path . tests/fm_level1_v06_smoke.tscn

echo "== Rendimiento Z10 con IA activa (ventana) =="
if [ -n "${DISPLAY:-}" ] || [ -n "${WAYLAND_DISPLAY:-}" ]; then
  timeout 75 godot --path . tests/fm_perf_ai.tscn
else
  echo "SKIP fm_perf_ai: sin DISPLAY/WAYLAND_DISPLAY; ejecutar en escritorio"
fi

echo "== Anclajes narrativos Z10 -> Recepcion =="
timeout 60 godot --headless --path . tests/fm_narrative_smoke.tscn

echo "== Vertical slice offline heredado =="
timeout 45 godot --headless --path . tests/fm_slice_smoke.tscn

echo "== Juego 2D =="
timeout 60 godot --headless --path . --script tests/test_main_2d.gd

echo "== Red 2D =="
timeout 70 bash tests/run_net_check.sh

echo "== Red 3D host-autoritativa =="
timeout 80 bash tests/run_net_3d_check.sh
