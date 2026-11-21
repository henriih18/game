class_name FMGraphicsPresets
extends Node

## Presets gráficos de FRECUENCIA MUERTA — primer pase seguro.
##
## Autoload `Graphics`. No toca lógica de gameplay: solo ventana/viewport,
## Environment, calidad global de Renderer y el flag `shadow_enabled` de las
## luces que ya venían con sombra en la escena.
##
## Escala interna:
##   Bajo / Medio → viewport de 1280×720 (el mismo que usa el proyecto con
##   window/stretch/mode="canvas_items"). Bajo además renderiza el 3D a 0,85×
##   con FSR 1.0 (1088×612) y lo reescala a 720p.
##   Alto / Ultra → el viewport se fuerza al tamaño de la ventana (1080p si
##   la ventana es 1080p). La UI sigue maquetada a 1280×720 y se escala 1,5×,
##   así que el HUD y el menú conservan su tamaño relativo.
##
## Sombras:
##   Se conserva la línea base de cada luz (la primera vez que se ve) y solo
##   se apagan sombras que ya estaban encendidas. Nunca se enciende una sombra
##   que la escena traía apagada. El foco del jugador tiene prioridad absoluta.
##   Límites: Bajo 2, Medio 3, Alto 4, Ultra 8 (hoy solo hay 4 en el nivel).
##
## El sistema vuelve a aplicar el preset cuando aparece un WorldEnvironment o
## una luz nueva (carga del nivel, instancias de gameplay) mediante una
## revisión diferida, sin integrarse en los scripts de juego.
##
## Uso:
##   Graphics.apply_preset("alto")
##   Graphics.apply_preset(Graphics.get_default_preset())
##
## No guarda el preset en disco: la selección dura la sesión. Persistirla es
## una decisión pendiente para cuando exista el menú de opciones definitivo.

signal preset_changed(preset_id: String)

const DEFAULT_PRESET := "medio"
const PRESET_ORDER: Array[String] = ["bajo", "medio", "alto", "ultra"]

const BASE_WIDTH := 1280
const BASE_HEIGHT := 720

## Metadato por luz con su estado original de sombra. Se guarda en la propia
## luz para que no haya que limpiar IDs de instancias liberadas.
const META_BASELINE_SHADOW := &"fm_gfx_baseline_shadow"

## Los valores son la fuente de verdad del sistema y de la prueba de humo.
## No cambiar uno sin actualizar `tests/fm_graphics_presets_smoke.gd`.
const PRESETS := {
	"bajo": {
		"id": "bajo",
		"label": "Bajo",
		"summary": "720p · 3D 612p con FSR · sin SSR/SSAO · niebla de profundidad",
		"native_resolution": false,
		"render_width": 1280,
		"render_height": 720,
		"scaling_3d_mode": Viewport.SCALING_3D_MODE_FSR,
		"scaling_3d_scale": 0.85,
		"msaa_3d": Viewport.MSAA_DISABLED,
		"screen_space_aa": Viewport.SCREEN_SPACE_AA_FXAA,
		"use_debanding": true,
		"ssr_enabled": false,
		"ssr_max_steps": 8,
		"ssr_fade_in": 0.05,
		"ssr_fade_out": 0.5,
		"ssr_depth_tolerance": 0.1,
		"ssr_half_size": true,
		"ssao_enabled": false,
		"ssao_radius": 0.8,
		"ssao_intensity": 0.8,
		"ssao_power": 1.2,
		"ssao_light_affect": 0.05,
		"ssao_quality": RenderingServer.ENV_SSAO_QUALITY_VERY_LOW,
		"ssao_half_size": true,
		"glow_enabled": true,
		"glow_intensity": 0.14,
		"glow_bloom": 0.0,
		"glow_strength": 0.9,
		"glow_hdr_threshold": 1.1,
		"volumetric_fog_enabled": false,
		"volumetric_fog_density": 0.006,
		"volumetric_fog_length": 32.0,
		"volumetric_fog_detail_spread": 3.0,
		"volumetric_fog_anisotropy": 0.15,
		"volumetric_fog_sky_affect": 0.0,
		"volumetric_volume_size": 32,
		"fog_enabled": true,
		"fog_density": 0.004,
		"fog_light_energy": 0.4,
		"fog_light_color": Color(0.55, 0.6, 0.68, 1.0),
		"shadow_light_limit": 2,
		"shadow_atlas": 1024,
		"directional_shadow_atlas": 1024,
		"shadow_soft_quality": RenderingServer.SHADOW_QUALITY_SOFT_VERY_LOW,
	},
	"medio": {
		"id": "medio",
		"label": "Medio",
		"summary": "720p · 3D 720p · SSR/SSAO suave · niebla volumétrica · 3 sombras",
		"native_resolution": false,
		"render_width": 1280,
		"render_height": 720,
		"scaling_3d_mode": Viewport.SCALING_3D_MODE_BILINEAR,
		"scaling_3d_scale": 1.0,
		"msaa_3d": Viewport.MSAA_DISABLED,
		"screen_space_aa": Viewport.SCREEN_SPACE_AA_FXAA,
		"use_debanding": true,
		"ssr_enabled": true,
		"ssr_max_steps": 24,
		"ssr_fade_in": 0.1,
		"ssr_fade_out": 1.0,
		"ssr_depth_tolerance": 0.15,
		"ssr_half_size": true,
		"ssao_enabled": true,
		"ssao_radius": 1.0,
		"ssao_intensity": 1.0,
		"ssao_power": 1.5,
		"ssao_light_affect": 0.1,
		"ssao_quality": RenderingServer.ENV_SSAO_QUALITY_LOW,
		"ssao_half_size": true,
		"glow_enabled": true,
		"glow_intensity": 0.18,
		"glow_bloom": 0.0,
		"glow_strength": 1.0,
		"glow_hdr_threshold": 1.0,
		"volumetric_fog_enabled": true,
		"volumetric_fog_density": 0.008,
		"volumetric_fog_length": 48.0,
		"volumetric_fog_detail_spread": 2.5,
		"volumetric_fog_anisotropy": 0.25,
		"volumetric_fog_sky_affect": 0.0,
		"volumetric_volume_size": 48,
		"fog_enabled": false,
		"fog_density": 0.004,
		"fog_light_energy": 0.4,
		"fog_light_color": Color(0.55, 0.6, 0.68, 1.0),
		"shadow_light_limit": 3,
		"shadow_atlas": 2048,
		"directional_shadow_atlas": 2048,
		"shadow_soft_quality": RenderingServer.SHADOW_QUALITY_SOFT_LOW,
	},
	"alto": {
		"id": "alto",
		"label": "Alto",
		"summary": "1080p nativo · MSAA 2x · SSR/SSAO completos · 4 sombras",
		"native_resolution": true,
		"render_width": 1920,
		"render_height": 1080,
		"scaling_3d_mode": Viewport.SCALING_3D_MODE_BILINEAR,
		"scaling_3d_scale": 1.0,
		"msaa_3d": Viewport.MSAA_2X,
		"screen_space_aa": Viewport.SCREEN_SPACE_AA_DISABLED,
		"use_debanding": true,
		"ssr_enabled": true,
		"ssr_max_steps": 48,
		"ssr_fade_in": 0.15,
		"ssr_fade_out": 2.0,
		"ssr_depth_tolerance": 0.2,
		"ssr_half_size": false,
		"ssao_enabled": true,
		"ssao_radius": 1.2,
		"ssao_intensity": 1.2,
		"ssao_power": 1.5,
		"ssao_light_affect": 0.1,
		"ssao_quality": RenderingServer.ENV_SSAO_QUALITY_MEDIUM,
		"ssao_half_size": false,
		"glow_enabled": true,
		"glow_intensity": 0.2,
		"glow_bloom": 0.01,
		"glow_strength": 1.0,
		"glow_hdr_threshold": 1.0,
		"volumetric_fog_enabled": true,
		"volumetric_fog_density": 0.01,
		"volumetric_fog_length": 64.0,
		"volumetric_fog_detail_spread": 2.0,
		"volumetric_fog_anisotropy": 0.25,
		"volumetric_fog_sky_affect": 0.0,
		"volumetric_volume_size": 64,
		"fog_enabled": false,
		"fog_density": 0.004,
		"fog_light_energy": 0.4,
		"fog_light_color": Color(0.55, 0.6, 0.68, 1.0),
		"shadow_light_limit": 4,
		"shadow_atlas": 2048,
		"directional_shadow_atlas": 4096,
		"shadow_soft_quality": RenderingServer.SHADOW_QUALITY_SOFT_MEDIUM,
	},
	"ultra": {
		"id": "ultra",
		"label": "Ultra",
		"summary": "1080p nativo · MSAA 4x · SSR/SSAO alto · todas las sombras",
		"native_resolution": true,
		"render_width": 1920,
		"render_height": 1080,
		"scaling_3d_mode": Viewport.SCALING_3D_MODE_BILINEAR,
		"scaling_3d_scale": 1.0,
		"msaa_3d": Viewport.MSAA_4X,
		"screen_space_aa": Viewport.SCREEN_SPACE_AA_DISABLED,
		"use_debanding": true,
		"ssr_enabled": true,
		"ssr_max_steps": 64,
		"ssr_fade_in": 0.15,
		"ssr_fade_out": 2.0,
		"ssr_depth_tolerance": 0.2,
		"ssr_half_size": false,
		"ssao_enabled": true,
		"ssao_radius": 1.4,
		"ssao_intensity": 1.4,
		"ssao_power": 1.6,
		"ssao_light_affect": 0.1,
		"ssao_quality": RenderingServer.ENV_SSAO_QUALITY_HIGH,
		"ssao_half_size": false,
		"glow_enabled": true,
		"glow_intensity": 0.22,
		"glow_bloom": 0.02,
		"glow_strength": 1.1,
		"glow_hdr_threshold": 1.0,
		"volumetric_fog_enabled": true,
		"volumetric_fog_density": 0.012,
		"volumetric_fog_length": 80.0,
		"volumetric_fog_detail_spread": 1.5,
		"volumetric_fog_anisotropy": 0.3,
		"volumetric_fog_sky_affect": 0.0,
		"volumetric_volume_size": 96,
		"fog_enabled": false,
		"fog_density": 0.004,
		"fog_light_energy": 0.4,
		"fog_light_color": Color(0.55, 0.6, 0.68, 1.0),
		"shadow_light_limit": 8,
		"shadow_atlas": 4096,
		"directional_shadow_atlas": 4096,
		"shadow_soft_quality": RenderingServer.SHADOW_QUALITY_SOFT_HIGH,
	},
}

var _current_id := ""
var _applied_shadow_lights := 0
var _applied_shadow_atlas := 0
var _applied_directional_shadow_atlas := 0
var _applied_shadow_quality := -1
var _applied_ssao_quality := -1
var _applied_volumetric_size := 0
var _refresh_queued := false
var _applying_content_scale := false


func _ready() -> void:
	_current_id = DEFAULT_PRESET
	# El tamaño de ventana puede cambiar en Alto/Ultra (resolución nativa).
	var window := get_window()
	if window != null and not window.size_changed.is_connected(_on_window_size_changed):
		window.size_changed.connect(_on_window_size_changed)
	# El nivel se carga después del autoload: reaplicar cuando aparezcan el
	# WorldEnvironment y las luces reales.
	get_tree().node_added.connect(_on_node_added)
	call_deferred("_apply_current_deferred")


func _apply_current_deferred() -> void:
	if _current_id.is_empty():
		return
	apply_preset(_current_id)


func _on_window_size_changed() -> void:
	if _current_id.is_empty() or _applying_content_scale:
		return
	var preset: Dictionary = PRESETS[_current_id]
	if bool(preset["native_resolution"]):
		_apply_content_scale(preset)


func _on_node_added(node: Node) -> void:
	if node is Light3D or node is WorldEnvironment:
		_schedule_refresh()


func _schedule_refresh() -> void:
	if _refresh_queued:
		return
	_refresh_queued = true
	call_deferred("_refresh_targets")


func _refresh_targets() -> void:
	_refresh_queued = false
	if _current_id.is_empty():
		return
	var preset: Dictionary = PRESETS[_current_id]
	var env := _find_environment()
	if env != null:
		_apply_environment(env, preset)
	_apply_environment_quality(preset)
	_apply_shadow_atlas(preset)
	_apply_light_limits(preset)


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------

func get_preset_ids() -> Array[String]:
	return PRESET_ORDER.duplicate()


func has_preset(preset_id: String) -> bool:
	return PRESETS.has(preset_id)


func get_current_preset() -> String:
	return _current_id


func get_default_preset() -> String:
	return DEFAULT_PRESET


func get_preset(preset_id: String) -> Dictionary:
	if not PRESETS.has(preset_id):
		return {}
	return (PRESETS[preset_id] as Dictionary).duplicate(true)


func get_applied_shadow_light_count() -> int:
	return _applied_shadow_lights


func get_applied_shadow_atlas() -> int:
	return _applied_shadow_atlas


func get_applied_shadow_quality() -> int:
	return _applied_shadow_quality


func get_applied_ssao_quality() -> int:
	return _applied_ssao_quality


func get_applied_volumetric_size() -> int:
	return _applied_volumetric_size


func describe_preset(preset_id: String) -> String:
	if not PRESETS.has(preset_id):
		return "Preset desconocido: %s" % preset_id
	var p: Dictionary = PRESETS[preset_id]
	var resolution := "viewport %dx%d interno" % [int(p["render_width"]), int(p["render_height"])]
	if bool(p["native_resolution"]):
		resolution = "viewport nativo al tamaño de la ventana (UI 720p escalada)"
	var aa := "MSAA off"
	match int(p["msaa_3d"]):
		Viewport.MSAA_2X:
			aa = "MSAA 2x"
		Viewport.MSAA_4X:
			aa = "MSAA 4x"
		Viewport.MSAA_8X:
			aa = "MSAA 8x"
	if int(p["screen_space_aa"]) == Viewport.SCREEN_SPACE_AA_FXAA:
		aa += " + FXAA"
	var scale_3d := float(p["scaling_3d_scale"])
	var fsr := "FSR 1.0" if int(p["scaling_3d_mode"]) == Viewport.SCALING_3D_MODE_FSR else "bilineal"
	var lines: Array[String] = [
		"%s — %s" % [str(p["label"]).to_upper(), str(p["summary"])],
		"Resolución: %s · 3D %.2f× (%s)" % [resolution, scale_3d, fsr],
		"Sombras: máximo %d luces · atlas %d · filtro %d" % [
			int(p["shadow_light_limit"]), int(p["shadow_atlas"]), int(p["shadow_soft_quality"]),
		],
		"SSR: %s (%d pasos, half=%s) · SSAO: %s (r %.1f, int %.1f)" % [
			"on" if bool(p["ssr_enabled"]) else "off", int(p["ssr_max_steps"]),
			str(p["ssr_half_size"]), "on" if bool(p["ssao_enabled"]) else "off",
			float(p["ssao_radius"]), float(p["ssao_intensity"]),
		],
		"Niebla volumétrica: %s (densidad %.3f, largo %.0f) · Glow: %s (%.2f)" % [
			"on" if bool(p["volumetric_fog_enabled"]) else "off",
			float(p["volumetric_fog_density"]), float(p["volumetric_fog_length"]),
			"on" if bool(p["glow_enabled"]) else "off", float(p["glow_intensity"]),
		],
		"Niebla de profundidad: %s · Antialiasing: %s" % [
			"on (densidad %.3f)" % float(p["fog_density"]) if bool(p["fog_enabled"]) else "off",
			aa,
		],
	]
	return "\n".join(lines)


## Aplica un preset completo. Devuelve false si el id no existe.
func apply_preset(preset_id: String) -> bool:
	if not PRESETS.has(preset_id):
		push_warning("FM_GRAPHICS: preset desconocido '%s'" % preset_id)
		return false
	_current_id = preset_id
	var p: Dictionary = PRESETS[preset_id]
	_apply_content_scale(p)
	_apply_viewport(get_viewport(), p)
	_apply_environment_quality(p)
	_apply_shadow_atlas(p)
	var env := _find_environment()
	if env != null:
		_apply_environment(env, p)
	_apply_light_limits(p)
	_log_preset(p, env != null)
	preset_changed.emit(preset_id)
	return true


# ---------------------------------------------------------------------------
# Resolución y viewport
# ---------------------------------------------------------------------------

func _apply_content_scale(p: Dictionary) -> void:
	var window := get_window()
	if window == null:
		return
	_applying_content_scale = true
	# La UI se mantiene siempre maquetada a 1280×720. En Alto/Ultra se sube
	# solo el viewport de render; el canvas se sigue escalando 1,5× a 1080p.
	window.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	window.content_scale_aspect = Window.CONTENT_SCALE_ASPECT_KEEP
	window.content_scale_factor = 1.0
	window.content_scale_size = Vector2i(BASE_WIDTH, BASE_HEIGHT)
	var viewport := get_viewport()
	if viewport != null:
		var target := Vector2i(BASE_WIDTH, BASE_HEIGHT)
		if bool(p["native_resolution"]):
			target = _native_window_size()
		if viewport.size != target:
			viewport.size = target
	_applying_content_scale = false


func _native_window_size() -> Vector2i:
	var size := DisplayServer.window_get_size()
	# En headless el tamaño puede ser 0; el preset debe seguir siendo válido.
	if size.x < 320 or size.y < 200:
		return Vector2i(BASE_WIDTH, BASE_HEIGHT)
	return size


func _apply_viewport(viewport: Viewport, p: Dictionary) -> void:
	if viewport == null:
		return
	viewport.scaling_3d_mode = int(p["scaling_3d_mode"])
	viewport.scaling_3d_scale = float(p["scaling_3d_scale"])
	viewport.msaa_3d = int(p["msaa_3d"])
	viewport.msaa_2d = Viewport.MSAA_DISABLED
	viewport.screen_space_aa = int(p["screen_space_aa"])
	viewport.use_taa = false
	viewport.use_debanding = bool(p["use_debanding"])


# ---------------------------------------------------------------------------
# Environment y calidad global
# ---------------------------------------------------------------------------

func _find_environment() -> Environment:
	var nodes := get_tree().root.find_children("*", "WorldEnvironment", true, false)
	var best: WorldEnvironment = null
	var best_depth := 1 << 30
	for node in nodes:
		var world := node as WorldEnvironment
		if world == null or world.environment == null:
			continue
		var depth := 0
		var parent := world.get_parent()
		while parent != null:
			depth += 1
			parent = parent.get_parent()
		if depth < best_depth:
			best_depth = depth
			best = world
	return best.environment if best != null else null


func _apply_environment(env: Environment, p: Dictionary) -> void:
	env.ssr_enabled = bool(p["ssr_enabled"])
	env.ssr_max_steps = int(p["ssr_max_steps"])
	env.ssr_fade_in = float(p["ssr_fade_in"])
	env.ssr_fade_out = float(p["ssr_fade_out"])
	env.ssr_depth_tolerance = float(p["ssr_depth_tolerance"])

	env.ssao_enabled = bool(p["ssao_enabled"])
	env.ssao_radius = float(p["ssao_radius"])
	env.ssao_intensity = float(p["ssao_intensity"])
	env.ssao_power = float(p["ssao_power"])
	env.ssao_light_affect = float(p["ssao_light_affect"])

	env.glow_enabled = bool(p["glow_enabled"])
	env.glow_intensity = float(p["glow_intensity"])
	env.glow_bloom = float(p["glow_bloom"])
	env.glow_strength = float(p["glow_strength"])
	env.glow_hdr_threshold = float(p["glow_hdr_threshold"])

	env.volumetric_fog_enabled = bool(p["volumetric_fog_enabled"])
	env.volumetric_fog_density = float(p["volumetric_fog_density"])
	env.volumetric_fog_length = float(p["volumetric_fog_length"])
	env.volumetric_fog_detail_spread = float(p["volumetric_fog_detail_spread"])
	env.volumetric_fog_anisotropy = float(p["volumetric_fog_anisotropy"])
	env.volumetric_fog_sky_affect = float(p["volumetric_fog_sky_affect"])

	var fog_color: Color = p["fog_light_color"]
	env.fog_enabled = bool(p["fog_enabled"])
	env.fog_density = float(p["fog_density"])
	env.fog_light_energy = float(p["fog_light_energy"])
	env.fog_light_color = fog_color
	env.fog_sky_affect = 0.0
	env.fog_aerial_perspective = 0.0


func _apply_environment_quality(p: Dictionary) -> void:
	RenderingServer.environment_set_ssr_half_size(bool(p["ssr_half_size"]))
	RenderingServer.environment_set_ssao_quality(
		int(p["ssao_quality"]), bool(p["ssao_half_size"]), 0.5, 2, 50.0, 300.0
	)
	RenderingServer.environment_set_volumetric_fog_volume_size(
		int(p["volumetric_volume_size"]), int(p["volumetric_volume_size"])
	)
	RenderingServer.environment_set_volumetric_fog_filter_active(
		bool(p["volumetric_fog_enabled"])
	)
	_applied_ssao_quality = int(p["ssao_quality"])
	_applied_volumetric_size = int(p["volumetric_volume_size"])


# ---------------------------------------------------------------------------
# Sombras
# ---------------------------------------------------------------------------

func _apply_shadow_atlas(p: Dictionary) -> void:
	var viewport := get_viewport()
	var atlas := int(p["shadow_atlas"])
	if viewport != null and _applied_shadow_atlas != atlas:
		RenderingServer.viewport_set_positional_shadow_atlas_size(
			viewport.get_viewport_rid(), atlas, true
		)
		_applied_shadow_atlas = atlas
	var directional_atlas := int(p["directional_shadow_atlas"])
	if _applied_directional_shadow_atlas != directional_atlas:
		RenderingServer.directional_shadow_atlas_set_size(directional_atlas, true)
		_applied_directional_shadow_atlas = directional_atlas
	var quality := int(p["shadow_soft_quality"])
	if _applied_shadow_quality != quality:
		RenderingServer.positional_soft_shadow_filter_set_quality(quality)
		RenderingServer.directional_soft_shadow_filter_set_quality(quality)
		_applied_shadow_quality = quality


func _apply_light_limits(p: Dictionary) -> void:
	var limit := int(p["shadow_light_limit"])
	var candidates: Array[Dictionary] = []
	for node in get_tree().root.find_children("*", "Light3D", true, false):
		var light := node as Light3D
		if light == null:
			continue
		var baseline := bool(light.get_meta(META_BASELINE_SHADOW, light.shadow_enabled))
		light.set_meta(META_BASELINE_SHADOW, baseline)
		# Restaura la línea base antes de recortar: cambiar de preset nunca
		# deja una sombra apagada para siempre.
		light.shadow_enabled = baseline
		if baseline:
			candidates.append({
				"light": light,
				"priority": _shadow_priority(light),
			})
	candidates.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
		return float(a["priority"]) > float(b["priority"])
	)
	var enabled := 0
	for index in range(candidates.size()):
		var light := candidates[index]["light"] as Light3D
		var on := index < limit
		light.shadow_enabled = on
		if on:
			enabled += 1
	_applied_shadow_lights = enabled


func _shadow_priority(light: Light3D) -> float:
	var score := 0.0
	# El foco del jugador es la sombra más importante de la escena.
	if _is_player_light(light):
		score += 1.0e9
	if light is SpotLight3D:
		score += 1.0e7
	elif light is DirectionalLight3D:
		score += 2.0e7
	# Energía y alcance aproximan la importancia visual de las estáticas.
	var reach := 1.0
	if light is OmniLight3D:
		reach = (light as OmniLight3D).omni_range
	elif light is SpotLight3D:
		reach = (light as SpotLight3D).spot_range
	score += light.light_energy * reach
	return score


func _is_player_light(light: Light3D) -> bool:
	var node: Node = light.get_parent()
	while node != null:
		if node.is_in_group("fm_player"):
			return true
		node = node.get_parent()
	return false


func _log_preset(p: Dictionary, has_environment: bool) -> void:
	var window := get_window()
	var scale_size := Vector2i.ZERO
	if window != null:
		scale_size = window.content_scale_size
	var viewport_size := Vector2i.ZERO
	var viewport := get_viewport()
	if viewport != null:
		viewport_size = viewport.size
	print("FM_GRAPHICS_PRESET id=%s viewport=%dx%d content=%dx%d native=%s 3d=%.2f mode=%d msaa=%d ssaa=%d shadows=%d/%d atlas=%d env=%s ssr=%s/%d ssao=%s glow=%s fog=%s/%.3f depth_fog=%s" % [
		str(p["id"]), viewport_size.x, viewport_size.y, scale_size.x, scale_size.y,
		str(p["native_resolution"]),
		float(p["scaling_3d_scale"]), int(p["scaling_3d_mode"]), int(p["msaa_3d"]),
		int(p["screen_space_aa"]), _applied_shadow_lights, _candidate_shadow_count(),
		_applied_shadow_atlas, str(has_environment),
		"on" if bool(p["ssr_enabled"]) else "off", int(p["ssr_max_steps"]),
		"on" if bool(p["ssao_enabled"]) else "off",
		"on" if bool(p["glow_enabled"]) else "off",
		"on" if bool(p["volumetric_fog_enabled"]) else "off",
		float(p["volumetric_fog_density"]),
		"on" if bool(p["fog_enabled"]) else "off",
	])


func _candidate_shadow_count() -> int:
	var count := 0
	for node in get_tree().root.find_children("*", "Light3D", true, false):
		var light := node as Light3D
		if light != null and bool(light.get_meta(META_BASELINE_SHADOW, light.shadow_enabled)):
			count += 1
	return count
