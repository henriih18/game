# FRECUENCIA MUERTA — HANDOFF P0b.5c (feeds de sprinkler Z10)

Fecha: 2026-11-10

## Estado

- `.blend` guardado: `nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend` (guardado explícito vía socket).
- Blender PID **10897** abierto; MCP `localhost:9876`; helper `/tmp/opencode/bpy_run.py`.
- Sin commit.

## P0b.5c — feeds de sprinkler Z10

- `scripts/fm/fm_p0b5c_feeds.py` ejecutado: `P0B5C_FEEDS_DONE`, QA PASS.
- `P0B5_FEED_A`: **7.560 tris / 3.828 verts**; x 46.275, y 15.805..17.035.
- `P0B5_FEED_B`: **8.116 tris / 4.108 verts**; x 55.725, y 17.035..23.800.
- 0 non-manifold, 0 degenerados, UV presente.
- `PROP_Z10_SprinklerFeeds` retirado a `Z10_RETIRED_P0B4`.
- Válvula de feed B movida a `y0 + depth*0.45` (≈ y20.1) para que sea visible.
- QA: `docs/fm_p0b5c_qa.json`.
- Backup: `docs/backups/FM_LEVEL1_V06_ARCH_before_p0b5c_feeds.blend`.
- Renders reejecutados: `docs/fm_p0b5c_feeds_close.png`, `docs/fm_p0b5c_feeds_wide.png` (`P0B5C_RENDER_DONE`).

## Recepción (cerrado)

- R13, LOD, switch y merge validados.
- Merge por material: 45 materiales → 28 draw calls (`RECEPTION_MERGE_OK`).
- Docs: `docs/FM_RECEPTION_R13.md`, `docs/FM_RECEPTION_LOD.md`, `docs/FM_RECEPTION_COLLISION.md`.

## Siguiente instrucción

1. Revisar `docs/fm_p0b5c_feeds_close.png` y `_wide.png`: confirmar que se leen válvula, volante y manómetro.
2. Si se aprueban, documentar P0b.5c en `docs/FM_P0B.md` (nueva §5.10) y actualizar §7.
3. Reexportar `assets/models/fm/z10_sector.glb` con `scripts/fm/fm_z10_sector_export.py` y validar en Godot; los conteos deben subir por las 2 mallas nuevas y bajar por el objeto viejo retirado.
4. Continuar con S-10..S-15 de Z10: ducto antes de muros, hueco de 6 m del conducto este, sleeves huérfanos, bandeja oeste sin sleeves, cabezas de sprinkler insuficientes y risers sin placa/sleeve.
5. Texturas/bake, desgaste fino y narrativa al final.

## Reglas que no cambian

- Sin armas, sin combate, sin matar criaturas.
- Godot 4.7.2 Forward+; Blender 5.2.3 LTS.
- Estándar hero; reutilizar maestros; no reconstruir; no tocar `fotos-referencia/`.
- Patinillos de Recepción/Seguridad: **pendientes por decisión del usuario**.
- **Sin commit** salvo pedido explícito.
