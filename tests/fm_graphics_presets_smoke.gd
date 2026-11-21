extends Node

## Prueba de humo del sistema de presets gráficos.
##
## godot --headless --path . tests/fm_graphics_presets_smoke.tscn
##
## Carga el Nivel 1 V06 completo para tener el Environment y las 47 luces
## reales, aplica Bajo / Medio / Alto / Ultra y comprueba:
##   - resolución interna (content scale) y escala 3D;
##   - MSAA, FXAA, debanding y TAA;
##   - SSR, SSAO, glow, niebla volumétrica y niebla de profundidad;
##   - límite de luces con sombra, atlas y calidad de sombra;
##   - que el foco del jugador nunca pierda su sombra;
##   - vuelta al preset por defecto;
##   - que el panel del menú construye sus cuatro botones y aplica al pulsar.
##
## No modifica gameplay, escenas, GLB ni materiales. No guarda nada en disco.

const SCENE_PATH := "res://scenes/fm/level1_v06.tscn"
const PANEL_SCENE := "res://scenes/fm/fm_graphics_panel.tscn"
const ORDER: Array[String] = ["bajo", "medio", "alto", "ultra"]
const SHADOW_COUNTS := {"bajo": 2, "medio": 3, "alto": 3, "ultra": 3}

var passes := 0
var fails := 0
var graphics: FMGraphicsPresets
var scene: Node
var env: Environment
var window: Window


func _ready() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE

	graphics = get_node_or_null("/root/Graphics") as FMGraphicsPresets
	_check("autoload_graphics", graphics != null)
	if graphics == null:
		_finish()
		return

	_check("default_preset", graphics.get_default_preset() == "medio")
	_check("preset_count", graphics.get_preset_ids().size() == ORDER.size())
	for preset_id in ORDER:
		_check("preset_%s_exists" % preset_id, graphics.has_preset(preset_id))

	var packed := load(SCENE_PATH) as PackedScene
	_check("level_scene_load", packed != null)
	if packed == null:
		_finish()
		return

	scene = packed.instantiate()
	add_child(scene)
	var guard := 0
	while not scene.level_ready and guard < 7200:
		await get_tree().process_frame
		guard += 1
	_check("level_ready", scene.level_ready)
	if not scene.level_ready:
		_finish()
		return

	env = scene.level_environment
	_check("level_environment", env != null)
	window = get_window()
	_check("window", window != null)
	await get_tree().process_frame
	await get_tree().process_frame

	for preset_id in ORDER:
		await _apply_and_check(preset_id)

	var default_id := graphics.get_default_preset()
	graphics.apply_preset(default_id)
	await get_tree().process_frame
	await get_tree().process_frame
	var default_preset := graphics.get_preset(default_id)
	_check("restore_default_id", graphics.get_current_preset() == default_id)
	_check("restore_default_ssr", env.ssr_enabled == bool(default_preset["ssr_enabled"]))
	_check("restore_default_ssao", env.ssao_enabled == bool(default_preset["ssao_enabled"]))
	_check("restore_default_fog", env.volumetric_fog_enabled == bool(default_preset["volumetric_fog_enabled"]))
	_check("restore_default_shadows", _shadowed_count() == int(SHADOW_COUNTS[default_id]))
	_check("restore_default_flashlight", _flashlight_shadowed())
	_check("restore_default_viewport", get_viewport().size == Vector2i(1280, 720))
	_check("restore_default_shadow_quality",
		graphics.get_applied_shadow_quality() == int(default_preset["shadow_soft_quality"]))
	_check("restore_default_shadow_atlas",
		graphics.get_applied_shadow_atlas() == int(default_preset["shadow_atlas"]))

	await _check_panel()
	_finish()


func _apply_and_check(preset_id: String) -> void:
	var preset := graphics.get_preset(preset_id)
	_check("apply_%s" % preset_id, graphics.apply_preset(preset_id))
	_check("apply_%s_current" % preset_id, graphics.get_current_preset() == preset_id)
	await get_tree().process_frame
	await get_tree().process_frame

	# Resolución interna y viewport.
	_check("content_mode_%s" % preset_id,
		window.content_scale_mode == Window.CONTENT_SCALE_MODE_CANVAS_ITEMS)
	_check("content_size_%s" % preset_id,
		window.content_scale_size == Vector2i(1280, 720))
	_check("content_factor_%s" % preset_id, is_equal_approx(window.content_scale_factor, 1.0))
	var expected_viewport := Vector2i(1280, 720)
	if bool(preset["native_resolution"]):
		expected_viewport = _native_size()
	_check("viewport_size_%s" % preset_id, get_viewport().size == expected_viewport)

	var viewport := get_viewport()
	_check("vp_scale_%s" % preset_id,
		is_equal_approx(viewport.scaling_3d_scale, float(preset["scaling_3d_scale"])))
	_check("vp_mode_%s" % preset_id,
		viewport.scaling_3d_mode == int(preset["scaling_3d_mode"]))
	_check("vp_msaa_%s" % preset_id, viewport.msaa_3d == int(preset["msaa_3d"]))
	_check("vp_screen_aa_%s" % preset_id,
		viewport.screen_space_aa == int(preset["screen_space_aa"]))
	_check("vp_debanding_%s" % preset_id,
		viewport.use_debanding == bool(preset["use_debanding"]))
	_check("vp_no_taa_%s" % preset_id, not viewport.use_taa)

	# Postproceso.
	_check("ssr_%s" % preset_id, env.ssr_enabled == bool(preset["ssr_enabled"]))
	_check("ssr_steps_%s" % preset_id, env.ssr_max_steps == int(preset["ssr_max_steps"]))
	_check("ssr_fade_in_%s" % preset_id,
		is_equal_approx(env.ssr_fade_in, float(preset["ssr_fade_in"])))
	_check("ssr_fade_out_%s" % preset_id,
		is_equal_approx(env.ssr_fade_out, float(preset["ssr_fade_out"])))
	_check("ssr_tolerance_%s" % preset_id,
		is_equal_approx(env.ssr_depth_tolerance, float(preset["ssr_depth_tolerance"])))
	_check("ssao_%s" % preset_id, env.ssao_enabled == bool(preset["ssao_enabled"]))
	_check("ssao_radius_%s" % preset_id,
		is_equal_approx(env.ssao_radius, float(preset["ssao_radius"])))
	_check("ssao_intensity_%s" % preset_id,
		is_equal_approx(env.ssao_intensity, float(preset["ssao_intensity"])))
	_check("ssao_power_%s" % preset_id,
		is_equal_approx(env.ssao_power, float(preset["ssao_power"])))
	_check("glow_%s" % preset_id, env.glow_enabled == bool(preset["glow_enabled"]))
	_check("glow_intensity_%s" % preset_id,
		is_equal_approx(env.glow_intensity, float(preset["glow_intensity"])))
	_check("glow_bloom_%s" % preset_id,
		is_equal_approx(env.glow_bloom, float(preset["glow_bloom"])))
	_check("glow_strength_%s" % preset_id,
		is_equal_approx(env.glow_strength, float(preset["glow_strength"])))
	_check("glow_threshold_%s" % preset_id,
		is_equal_approx(env.glow_hdr_threshold, float(preset["glow_hdr_threshold"])))
	_check("volfog_%s" % preset_id,
		env.volumetric_fog_enabled == bool(preset["volumetric_fog_enabled"]))
	_check("volfog_density_%s" % preset_id,
		is_equal_approx(env.volumetric_fog_density, float(preset["volumetric_fog_density"])))
	_check("volfog_length_%s" % preset_id,
		is_equal_approx(env.volumetric_fog_length, float(preset["volumetric_fog_length"])))
	_check("volfog_detail_%s" % preset_id,
		is_equal_approx(env.volumetric_fog_detail_spread, float(preset["volumetric_fog_detail_spread"])))
	_check("volfog_anisotropy_%s" % preset_id,
		is_equal_approx(env.volumetric_fog_anisotropy, float(preset["volumetric_fog_anisotropy"])))
	_check("depth_fog_%s" % preset_id, env.fog_enabled == bool(preset["fog_enabled"]))
	_check("depth_fog_density_%s" % preset_id,
		is_equal_approx(env.fog_density, float(preset["fog_density"])))
	_check("depth_fog_energy_%s" % preset_id,
		is_equal_approx(env.fog_light_energy, float(preset["fog_light_energy"])))

	# Sombras y calidad global.
	_check("shadow_count_%s" % preset_id,
		_shadowed_count() == int(SHADOW_COUNTS[preset_id]))
	_check("flashlight_shadow_%s" % preset_id, _flashlight_shadowed())
	_check("shadow_atlas_%s" % preset_id,
		graphics.get_applied_shadow_atlas() == int(preset["shadow_atlas"]))
	_check("shadow_quality_%s" % preset_id,
		graphics.get_applied_shadow_quality() == int(preset["shadow_soft_quality"]))
	_check("ssao_quality_%s" % preset_id,
		graphics.get_applied_ssao_quality() == int(preset["ssao_quality"]))
	_check("volfog_volume_%s" % preset_id,
		graphics.get_applied_volumetric_size() == int(preset["volumetric_volume_size"]))


func _check_panel() -> void:
	var packed := load(PANEL_SCENE) as PackedScene
	_check("panel_scene_load", packed != null)
	if packed == null:
		return
	var panel := packed.instantiate() as FMGraphicsPanel
	_check("panel_script", panel != null)
	if panel == null:
		return
	add_child(panel)
	await get_tree().process_frame
	_check("panel_hidden_on_start", not panel.is_open())
	panel.open()
	await get_tree().process_frame
	_check("panel_open", panel.is_open())
	_check("panel_button_count", panel.get_preset_button_count() == ORDER.size())
	for preset_id in ORDER:
		_check("panel_button_%s" % preset_id, panel.get_preset_button(preset_id) != null)

	var alto := panel.get_preset_button("alto")
	_check("panel_alto_button", alto != null)
	if alto != null:
		alto.pressed.emit()
		await get_tree().process_frame
		_check("panel_applies_alto", graphics.get_current_preset() == "alto")
		_check("panel_alto_ssr", env.ssr_enabled)
		_check("panel_alto_shadows", _shadowed_count() == int(SHADOW_COUNTS["alto"]))

	panel.close_panel()
	await get_tree().process_frame
	_check("panel_closed", not panel.is_open())
	panel.queue_free()
	await get_tree().process_frame


func _shadowed_count() -> int:
	if scene == null or not is_instance_valid(scene):
		return -1
	var count := 0
	for node in scene.find_children("*", "Light3D", true, false):
		var light := node as Light3D
		if light != null and light.shadow_enabled:
			count += 1
	return count


func _flashlight_shadowed() -> bool:
	if scene == null or not is_instance_valid(scene):
		return false
	var flashlight := scene.get_node_or_null("Player/FPCamera/Flashlight") as SpotLight3D
	return flashlight != null and flashlight.shadow_enabled


func _native_size() -> Vector2i:
	var size := DisplayServer.window_get_size()
	if size.x < 320 or size.y < 200:
		return Vector2i(1280, 720)
	return size


func _check(label: String, condition: bool) -> void:
	if condition:
		passes += 1
		print("PASS %s" % label)
	else:
		fails += 1
		print("FAIL %s" % label)


func _finish() -> void:
	for action in ["move_up", "move_down", "move_left", "move_right", "sprint", "crouch", "interact", "drop", "flashlight"]:
		Input.action_release(action)
	print("FM_GRAPHICS_PRESETS_SMOKE: %s (%d PASS / %d FAIL)" % [
		"PASS" if fails == 0 else "FAIL", passes, fails,
	])
	get_tree().quit(0 if fails == 0 else 1)
