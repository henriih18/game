# FRECUENCIA MUERTA — Modelo del jugador (2026-11-18)

## 1. Origen

- Fuente: `objetos-modelados/personaje-jugador/mesh-optimizer-1795023690983.glb`
  (29,9 MB). El GLB original no se ha modificado.
- Copia de seguridad: `docs/backups/FM_PLAYER_TECH_2026-11-18/`.
- Archivo de trabajo: `nexus/nivel_01/FM_PLAYER_WORK.blend`.
- Archivo con binding y animaciones: `nexus/nivel_01/FM_PLAYER_WORK_BOUND.blend`.
- GLB final: `assets/models/fm/player_generated_v5.glb` (239k tris).
- Alternativa ligera: `assets/models/fm/player_generated_v4.glb` (152k tris, 29 MB).

## 2. Pasada técnica

| Paso | Resultado |
|---|---|
| Escala | 1,75 m, transformaciones aplicadas, pies en z0 |
| Dimensiones | 0,672 × 0,496 × 1,750 m |
| Decimación | Decimate COLLAPSE 0,55 + triangulación (versión final) |
| Limpieza | `remove_doubles` 1e-6, `dissolve_degenerate` 1e-6, vértices sueltos, normales |
| Malla final | **257.187 vértices, 239.185 polígonos, 239.186 triángulos** |
| Orientación | frente hacia −Y (glTF/Godot) |
| Materiales | `Material_0`, 2 imágenes 2048² |
| UVs | conservadas del modelo original |

La malla generada por IA está fragmentada en **8.862 componentes** (ropa,
cuerpo y accesorios separados), lo que condiciona el rig y el binding.

## 3. Rig

`PlayerRig`, 23 huesos:

- `root` (no deform)
- `hips`, `spine_01`, `spine_02`, `chest`, `neck`, `head`
- por lado L/R: `clavicle`, `upper_arm`, `forearm`, `hand`,
  `thigh`, `shin`, `foot`, `toe`

El esqueleto es un game rig provisional, no un Rigify de producción. El
frente del personaje mira a −Y y la armadura conserva una rotación Z de 180°
para compensar la orientación de la malla.

## 4. Binding

- `ARMATURE_AUTO` falló por la fragmentación de la malla
  (`Bone Heat Weighting: failed to find solution`).
- Primer intento de pesos por cercanía: 0 vértices sin peso, pero desgarros
  en cadera con poses extremas.
- Pesos rígidos por componente: válidos para prueba, pero deformación de
  figura articulada.
- **Binding final**: `blender-character-rigging/scripts/bind_mesh.py`,
  método `proxy` (transferencia voxel), límite 4 influencias, limpieza 0.01.

Resultado:

```json
{"ok": true, "method": "proxy", "groups": 22,
 "unweighted_verts": 0, "max_influences": 4}
```

Los pesos quedaron limitados a 4 influencias por vértice. La deformación es aceptable para un placeholder
jugable; no es una deformación orgánica fina.

## 5. Animaciones

Dos acciones guardadas en `FM_PLAYER_WORK_BOUND.blend`:

| Acción | Frames | Contenido |
|---|---:|---|
| `Player_Walk` | 25 (1–25) | ciclo de caminata: pierna izquierda adelante 25°, derecha atrás −25°, brazos opuestos ±20°, rodillas y pies; poses 1/7/13/19/25 |
| `Player_Idle` | 48 (1–48) | respiración sutil de spine/chest/head y balanceo mínimo de brazos |

Ambas tienen fake user. El GLB exporta las dos animaciones (69 canales cada
una).

### 5.1 Corrección de los huesos del pie

Los pies de la malla apuntaban hacia −Y (delante), pero los huesos `foot.L/R`
y `toe.L/R` tenían sus colas hacia +Y en mundo por la rotación Z de 180° de la
armadura. Se corrigieron en Edit Mode:

- `foot.L/R`: cabeza en y local +0,01 → cola en y local +0,14, z 0,03.
- `toe.L/R`: cabeza en y +0,14 → cola en y +0,24, z 0,03, conectado.
- Roll recalculado con `GLOBAL_POS_Z`.

En mundo quedan: `foot` (∓0,12, −0,01, 0,10) → (∓0,12, −0,14, 0,03) y
`toe` (∓0,12, −0,14, 0,03) → (∓0,12, −0,24, 0,03). La marcha se validó en
frames 7 y 13, frontal y lateral, sin desgarros y con los pies orientados
hacia delante.

## 6. GLB final

`assets/models/fm/player_generated_v5.glb`:

| Dato | Valor |
|---|---:|
| Tamaño | **44.490.492 bytes** |
| Nodos | 25 |
| Mallas | 1 |
| Skins | 1 |
| Joints | 23 |
| Animaciones | **2** (`Player_Idle`, `Player_Walk`) |
| Canales por animación | 69 |
| Materiales | 1 |
| Imágenes | 2 (1024 en la sesión de export) |
| Vértices glTF | 257.187 |
| Triángulos | 239.186 |
| Cámaras / luces | 0 / 0 |

Las texturas se bajan a 1024 solo en memoria durante el export; el `.blend`
conserva las originales de 2048.

## 7. QA y limitaciones

`blender-asset-qa` sobre `Player_Game` a 239.186 tris (profile game,
eps 0.002, tol 0.08, no_modifiers, max_tris 400000):

- **FAIL** — 2.462 caras UV de área cero, 7.363 aristas con winding
  inconsistente, 5.687 pares de z-fighting, 272 aristas non-manifold,
  29.916 wire edges, 3.043 vértices duplicados, 15.865 islas y 23.076 pares
  back-to-back.
- La deuda crece al conservar más triángulos del modelo AI original; no es
  un fallo del rig ni de las animaciones.

El modelo se conserva por calidad visual. La alternativa ligera
`player_generated_v4.glb` (152.183 tris, 29 MB) mantiene el aspecto y reduce
el peso; `player_generated_v5.glb` es la versión de máxima fidelidad
(239.186 tris, 43 MB).

Otras limitaciones:

- Deformación articulada, no orgánica; hombros, codos y caderas no tienen
  corrección fina.
- Topología irregular y 8.862 componentes en el original.
- Sin LODs, sin collider de cápsula, sin separación de brazos/manos para
  primera persona.
- No integrado en `fm_player.gd` ni en la escena del Nivel 1.

## 8. Renders

- `/tmp/opencode/player_055_neutral.png`
- `/tmp/opencode/player_055_walk_f7.png`
- `/tmp/opencode/player_055_walk_f13.png`
- `/tmp/opencode/player_bound_neutral.png`
- `/tmp/opencode/player_bound_walk.png`
- `/tmp/opencode/player_bound_stress.png`
- `/tmp/opencode/player_walk_f7.png`
- `/tmp/opencode/player_walk_f13.png`
- `/tmp/opencode/player_feet_f7.png`
- `/tmp/opencode/player_feet_f13.png`
- `/tmp/opencode/player_walk_side_f7.png`
- `/tmp/opencode/player_walk_side_f13.png`

## 9. Siguiente paso

1. Elegir versión de entrega: v5 (239k, máxima fidelidad) o v4 (152k,
   29 MB) para el presupuesto del nivel.
2. Importar en Godot y validar skin, 23 huesos y las dos animaciones.
3. Integrar como placeholder en `fm_player.gd` con cápsula de 1,75 m,
   altura de cámara y primera persona.
4. Para calidad final: retopología manual, pesos suaves por zonas, LODs,
   limpieza de UVs/winding y texturas 1K/2K optimizadas.

Sin commit hasta autorización.
