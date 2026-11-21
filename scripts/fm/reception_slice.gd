extends Node3D

## Slice jugable local de la recepción NEXUS.
## Carga el GLB de Blender en runtime (el importador de este proyecto no
## registra el archivo), añade colisiones, loot, escondite, trampa y la
## extracción v138.

const GLB_PATH := "res://assets/models/fm/reception_nexus.glb"
const PLAYER_SCENE := preload("res://scenes/fm/fm_player.tscn")
const LOOT_SCRIPT := preload("res://scripts/fm/fm_reception_loot.gd")
const EXTRACTION_SCRIPT := preload("res://scripts/fm/fm_reception_extraction.gd")
const HIDING_SCRIPT := preload("res://scripts/fm/fm_hiding_spot.gd")
const NOISE_TRAP_SCRIPT := preload("res://scripts/fm/fm_noise_trap.gd")
const HUD_SCRIPT := preload("res://scripts/fm/fm_hud.gd")

const SPAWN := Vector3(-12.0, -5.60, -2.85)
const EXTRACTION_CENTER := Vector3(-17.5, -5.65, -10.7)

enum State { PLAYING, WON, LOST }

const LOOT_SPECS := {
	"NEXUS_V05_REC_LOOT_CASE_0": {
		"id": "case", "name": "MALETÍN DE MUESTRAS", "value": 640,
		"mass": 17.0, "min_players": 1,
	},
	"NEXUS_V05_REC_LOOT_SAMPLE_0": {
		"id": "sample", "name": "CONTENEDOR BIOLÓGICO", "value": 900,
		"mass": 9.0, "min_players": 1,
	},
	"NEXUS_V05_REC_LOOT_CRATE_0": {
		"id": "crate", "name": "CAJA DE CARGA", "value": 1800,
		"mass": 42.0, "min_players": 2,
	},
	"NEXUS_V05_REC_LOOT_DOCS_0": {
		"id": "docs", "name": "DOCUMENTACIÓN", "value": 220,
		"mass": 0.6, "min_players": 1,
	},
	"NEXUS_V05_REC_LOOT_DRIVE_0": {
		"id": "drive", "name": "UNIDAD DE DATOS", "value": 1200,
		"mass": 0.4, "min_players": 1,
	},
}

var state: State = State.PLAYING
var player
var hud
var glb_root: Node3D
var extraction
var hiding_spot
var noise_trap
var loot_items: Array[Node3D] = []
var _status_override := ""
var _status_timer := 0.0
var _emergency_lights: Array[OmniLight3D] = []
var _emergency_base_energy: Array[float] = []
var _flicker_time := 0.0
var _door_l: Node3D
var _door_r: Node3D
var _door_l_closed := -17.95
var _door_r_closed := -17.05
var _door_tween: Tween
var _door_collider: StaticBody3D
var _elevator_closing := false
var ambience: AudioStreamPlayer3D

func _ready() -> void:
	_setup_environment()
	if not _load_glb():
		return
	_setup_collisions()
	_setup_physics_debris()
	_cache_elevator_doors()
	_setup_loot()
	_setup_hiding_spot()
	_setup_noise_trap()
	_setup_extraction()
	_setup_player()
	_setup_hud()
	_setup_audio()
	print("RECEPTION_READY loot=%d" % loot_items.size())

func _load_glb() -> bool:
	var document := GLTFDocument.new()
	var gltf_state := GLTFState.new()
	var err: Error = document.append_from_file(GLB_PATH, gltf_state)
	if err != OK:
		push_error("No se pudo cargar el GLB de recepción: %s" % error_string(err))
		return false
	glb_root = document.generate_scene(gltf_state)
	if glb_root == null:
		push_error("GLTFDocument no generó la escena de recepción")
		return false
	glb_root.name = "ReceptionGLB"
	add_child(glb_root)
	for node in glb_root.find_children("*", "AnimationPlayer", true, false):
		var ap := node as AnimationPlayer
		if ap != null:
			ap.stop()
			ap.autoplay = ""
	_tune_glb_lights()
	_tune_glb_materials()
	_setup_lighting()
	_tune_emergency_signage()
	_replace_counter_monitors()
	_setup_counter_details()
	_setup_wall_grime()
	_setup_dust()
	_setup_vignette()
	return true

func _tune_glb_lights() -> void:
	for node in glb_root.find_children("*", "Light3D", true, false):
		var light := node as Light3D
		var lname := light.name.to_lower()
		if "emerg" in lname:
			light.light_energy = 1.1
			light.shadow_enabled = false
			light.visible = true
		elif "extract" in lname:
			light.light_energy = 0.22
			light.shadow_enabled = false
			light.visible = true
		else:
			# Luces generales, de cabina y downlights: apagadas por dirección artística.
			light.light_energy = 0.0
			light.visible = false
		if light is OmniLight3D:
			(light as OmniLight3D).omni_range = 7.0 if "emerg" in lname else 4.0
		elif light is SpotLight3D:
			(light as SpotLight3D).spot_range = 7.0 if "emerg" in lname else 4.0

func _tune_glb_materials() -> void:
	var seen := {}
	for node in glb_root.find_children("*", "MeshInstance3D", true, false):
		var mesh_instance := node as MeshInstance3D
		if mesh_instance.mesh == null:
			continue
		for surface in range(mesh_instance.mesh.get_surface_count()):
			var material := mesh_instance.get_active_material(surface)
			if material == null or not (material is StandardMaterial3D):
				continue
			var key := material.get_instance_id()
			if seen.has(key):
				continue
			seen[key] = true
			var standard := material as StandardMaterial3D
			var tex_name := ""
			if standard.albedo_texture != null:
				tex_name = standard.albedo_texture.resource_path.to_lower()
			var mat_name := (standard.resource_name + " " + tex_name + " " + mesh_instance.name).to_lower()
			standard.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
			if "blood" in mat_name or "sangre" in mat_name:
				standard.albedo_color = Color(0.24, 0.018, 0.010, 1.0)
				standard.roughness = 0.30
				standard.metallic = 0.0
				standard.emission_enabled = false
			elif "water" in mat_name or "oil" in mat_name or "spill" in mat_name or "trail" in mat_name:
				standard.albedo_color = Color(0.055, 0.075, 0.085, 1.0)
				standard.roughness = 0.18
				standard.metallic = 0.15
				standard.emission_enabled = false
			elif "floor" in mat_name or "suelo" in mat_name:
				standard.albedo_color *= Color(0.82, 0.86, 0.92, 1.0)
				standard.roughness = clampf(standard.roughness, 0.55, 0.74)
				standard.metallic = 0.03
				standard.uv1_scale = Vector3(1.15, 1.15, 1.0)
			elif "wall" in mat_name or "concrete" in mat_name or "plaster" in mat_name or "hormigon" in mat_name:
				standard.albedo_color *= Color(0.76, 0.80, 0.86, 1.0)
				standard.roughness = clampf(standard.roughness, 0.72, 0.88)
				standard.metallic = 0.0
			elif "metal" in mat_name or "steel" in mat_name or "rust" in mat_name or "acero" in mat_name:
				standard.albedo_color *= Color(0.74, 0.78, 0.84, 1.0)
				standard.roughness = clampf(standard.roughness, 0.42, 0.68)
			if "sign" in mat_name or "screen" in mat_name or "monitor" in mat_name or "lamp" in mat_name:
				standard.emission_enabled = true
				standard.emission_energy_multiplier = clampf(maxf(standard.emission_energy_multiplier, 0.9), 0.9, 1.6)
			if "tv" in mat_name or "television" in mat_name:
				standard.albedo_color *= Color(0.55, 0.58, 0.62, 1.0)
				standard.metallic = 0.35
				standard.roughness = 0.52
	_tune_blood_surfaces()

func _tune_blood_surfaces() -> void:
	var splat := load("res://assets/art/fm/blood_splat.png") as Texture2D
	var decal_index := 0
	for node in glb_root.find_children("*", "MeshInstance3D", true, false):
		var mesh_instance := node as MeshInstance3D
		var n := mesh_instance.name.to_lower()
		var p := mesh_instance.get_parent()
		while p != null and p != glb_root:
			n += " " + p.name.to_lower()
			p = p.get_parent()
		if not ("blood" in n or "sangre" in n or "spill" in n or "trail" in n or "oil" in n):
			continue
		mesh_instance.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		var scaled_size := mesh_instance.get_aabb().size * mesh_instance.global_transform.basis.get_scale()
		var footprint := maxf(scaled_size.x, scaled_size.z)
		if "nexus_l1_dis_blood" in n and footprint > 0.35:
			var pos := mesh_instance.global_position
			mesh_instance.visible = false
			if splat != null:
				_spawn_blood_decal(pos, footprint, decal_index)
			decal_index += 1
			continue
		if footprint > 2.0:
			mesh_instance.scale.x *= 0.42
			mesh_instance.scale.z *= 0.42
		elif footprint > 1.1:
			mesh_instance.scale.x *= 0.60
			mesh_instance.scale.z *= 0.60

func _spawn_blood_decal(pos: Vector3, footprint: float, index: int) -> void:
	var decal := Decal.new()
	decal.name = "BloodDecal_%02d" % index
	decal.texture_albedo = load("res://assets/art/fm/blood_splat.png") as Texture2D
	decal.modulate = Color(0.60, 0.065, 0.040, 1.0)
	decal.albedo_mix = 0.94
	decal.size = Vector3(clampf(footprint * 0.95, 1.1, 2.6), 1.2, clampf(footprint * 0.78, 0.9, 2.2))
	decal.position = Vector3(pos.x, -5.24, pos.z)
	decal.rotation.y = float(index) * 1.73
	decal.upper_fade = 0.22
	decal.lower_fade = 0.35
	decal.distance_fade_enabled = true
	decal.distance_fade_begin = 18.0
	decal.distance_fade_length = 6.0
	add_child(decal)

func _setup_lighting() -> void:
	# Dirección artística: solo luces de emergencia visibles y la linterna del jugador.
	_add_emergency_fixture(Vector3(-15.0, -2.72, -1.78), Color(1.0, 0.55, 0.22), 1.6, 7.0, true, Vector3(0.30, 0.12, 0.025), Vector3(0.0, 0.0, 0.045))
	_add_emergency_fixture(Vector3(-5.0, -2.72, -1.78), Color(1.0, 0.55, 0.22), 1.6, 7.0, false, Vector3(0.30, 0.12, 0.025), Vector3(0.0, 0.0, 0.045))
	_add_emergency_fixture(Vector3(-19.62, -2.95, -10.52), Color(1.0, 0.18, 0.06), 0.9, 5.5, true, Vector3(0.025, 0.12, 0.30), Vector3(0.045, 0.0, 0.0))
	_add_emergency_fixture(Vector3(-10.0, -2.88, -11.52), Color(1.0, 0.45, 0.16), 1.1, 6.0, false, Vector3(0.30, 0.12, 0.025), Vector3(0.0, 0.0, 0.045))
	_add_emergency_fixture(Vector3(-4.18, -2.90, -6.20), Color(1.0, 0.45, 0.16), 1.0, 6.0, false, Vector3(0.025, 0.12, 0.30), Vector3(-0.045, 0.0, 0.0))
	_add_emergency_fixture(Vector3(-17.5, -3.02, -12.0), Color(1.0, 0.20, 0.06), 0.40, 2.8, false, Vector3(0.18, 0.02, 0.18), Vector3(0.0, -0.035, 0.0))

func _add_emergency_fixture(pos: Vector3, color: Color, energy: float, light_range: float, cast_shadow: bool, lens_size: Vector3, lens_offset: Vector3) -> void:
	var light := OmniLight3D.new()
	light.name = "ReceptionEmergencyLight_%d" % get_child_count()
	light.position = pos
	light.light_color = color
	light.light_energy = energy
	light.omni_range = light_range
	light.shadow_enabled = cast_shadow
	light.shadow_bias = 0.05
	light.light_volumetric_fog_energy = 0.8
	add_child(light)
	_emergency_lights.append(light)
	_emergency_base_energy.append(energy)
	var lens := MeshInstance3D.new()
	lens.name = light.name + "_LENS"
	var mesh := BoxMesh.new()
	mesh.size = lens_size
	lens.mesh = mesh
	lens.position = pos + lens_offset
	lens.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.albedo_color = color
	mat.emission_enabled = true
	mat.emission = color
	mat.emission_energy_multiplier = 2.6
	lens.material_override = mat
	add_child(lens)

func _tune_emergency_signage() -> void:
	_set_sign_material("NEXUS_V05_C_REC_ELEV_SIGN_TEXT_TEXT", Color(0.18, 1.0, 0.48), 2.4)
	_set_sign_material("NEXUS_V05_REC_EXTRACT_SIGN_TEXT", Color(1.0, 0.58, 0.12), 2.2)
	if glb_root.find_child("ReceptionExitSignLabel", true, false) == null:
		var plate := MeshInstance3D.new()
		plate.name = "ReceptionExitSignPlate"
		var plate_mesh := BoxMesh.new()
		plate_mesh.size = Vector3(1.05, 0.28, 0.035)
		plate.mesh = plate_mesh
		plate.position = Vector3(-17.5, -2.24, -11.48)
		var plate_mat := StandardMaterial3D.new()
		plate_mat.albedo_color = Color(0.015, 0.02, 0.022, 1.0)
		plate_mat.metallic = 0.4
		plate_mat.roughness = 0.6
		plate.material_override = plate_mat
		add_child(plate)
		var label := Label3D.new()
		label.name = "ReceptionExitSignLabel"
		label.text = "SALIDA"
		label.font_size = 48
		label.pixel_size = 0.0042
		label.modulate = Color(0.18, 1.0, 0.48, 1.0)
		label.outline_size = 6
		label.outline_modulate = Color(0.0, 0.0, 0.0, 1.0)
		label.position = Vector3(-17.5, -2.24, -11.455)
		add_child(label)
	var exit_sign := glb_root.find_child("NEXUS_V05_C_REC_ELEV_SIGN_TEXT_TEXT", true, false) as Node3D
	if exit_sign != null:
		var glow := OmniLight3D.new()
		glow.name = "ReceptionExitSignGlow"
		glow.position = exit_sign.global_position + Vector3(0.0, 0.0, 0.18)
		glow.light_color = Color(0.18, 1.0, 0.45)
		glow.light_energy = 0.28
		glow.omni_range = 2.4
		glow.shadow_enabled = false
		add_child(glow)

func _set_sign_material(node_name: String, color: Color, energy: float) -> void:
	var node := glb_root.find_child(node_name, true, false) as MeshInstance3D
	if node == null:
		return
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.albedo_color = color
	mat.emission_enabled = true
	mat.emission = color
	mat.emission_energy_multiplier = energy
	node.material_override = mat

func _replace_counter_monitors() -> void:
	for monitor_name in ["NEXUS_ASSET_L1R_REC_MON_A_01", "NEXUS_ASSET_L1R_REC_MON_B_01"]:
		var source := glb_root.find_child(monitor_name, true, false) as Node3D
		if source == null:
			continue
		var bounds: AABB
		if source is MeshInstance3D:
			var source_mesh := source as MeshInstance3D
			bounds = source_mesh.global_transform * source_mesh.get_aabb()
		else:
			bounds = _global_aabb(source)
		if bounds.size == Vector3.ZERO:
			continue
		source.visible = false
		_add_flat_monitor(bounds, monitor_name.contains("_A_"))

func _add_flat_monitor(bounds: AABB, suffix_a: bool) -> void:
	var center := bounds.get_center()
	var w := clampf(bounds.size.x, 0.52, 0.66)
	var h := clampf(bounds.size.y * 0.82, 0.32, 0.42)
	var body := MeshInstance3D.new()
	body.name = "ReceptionFlatMonitor_%s" % ("A" if suffix_a else "B")
	var body_mesh := BoxMesh.new()
	body_mesh.size = Vector3(w, h, 0.055)
	body.mesh = body_mesh
	body.position = center
	var body_mat := StandardMaterial3D.new()
	body_mat.albedo_color = Color(0.025, 0.030, 0.038, 1.0)
	body_mat.metallic = 0.72
	body_mat.roughness = 0.34
	body.material_override = body_mat
	add_child(body)
	var screen := MeshInstance3D.new()
	screen.name = body.name + "_SCREEN"
	var screen_mesh := BoxMesh.new()
	screen_mesh.size = Vector3(w * 0.88, h * 0.76, 0.004)
	screen.mesh = screen_mesh
	screen.position = center + Vector3(0.0, 0.0, 0.031)
	var screen_mat := StandardMaterial3D.new()
	screen_mat.albedo_color = Color(0.015, 0.09, 0.10, 1.0)
	screen_mat.emission_enabled = true
	screen_mat.emission = Color(0.10, 0.62, 0.66)
	screen_mat.emission_energy_multiplier = 0.65
	screen_mat.roughness = 0.18
	screen.material_override = screen_mat
	add_child(screen)
	var stand := MeshInstance3D.new()
	stand.name = body.name + "_STAND"
	var stand_mesh := BoxMesh.new()
	stand_mesh.size = Vector3(0.07, 0.20, 0.07)
	stand.mesh = stand_mesh
	stand.position = Vector3(center.x, bounds.position.y + 0.10, center.z)
	stand.material_override = body_mat
	add_child(stand)
	var base := MeshInstance3D.new()
	base.name = body.name + "_BASE"
	var base_mesh := BoxMesh.new()
	base_mesh.size = Vector3(0.26, 0.02, 0.16)
	base.mesh = base_mesh
	base.position = Vector3(center.x, bounds.position.y + 0.01, center.z)
	base.material_override = body_mat
	add_child(base)

func _setup_counter_details() -> void:
	var glass := MeshInstance3D.new()
	glass.name = "ReceptionCounterGlass"
	var glass_mesh := BoxMesh.new()
	glass_mesh.size = Vector3(3.95, 0.52, 0.012)
	glass.mesh = glass_mesh
	glass.position = Vector3(-12.0, -4.58, -7.96)
	var glass_mat := StandardMaterial3D.new()
	glass_mat.albedo_color = Color(0.48, 0.60, 0.66, 0.14)
	glass_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	glass_mat.metallic = 0.18
	glass_mat.roughness = 0.08
	glass_mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	glass.material_override = glass_mat
	glass.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(glass)
	var post_mat := StandardMaterial3D.new()
	post_mat.albedo_color = Color(0.08, 0.085, 0.09, 1.0)
	post_mat.metallic = 0.85
	post_mat.roughness = 0.28
	for i in range(3):
		var post := MeshInstance3D.new()
		post.name = "ReceptionCounterGlassPost_%d" % i
		var post_mesh := CylinderMesh.new()
		post_mesh.top_radius = 0.022
		post_mesh.bottom_radius = 0.022
		post_mesh.height = 0.54
		post_mesh.radial_segments = 12
		post.mesh = post_mesh
		post.position = Vector3(-13.9 + float(i) * 1.95, -4.58, -7.96)
		post.material_override = post_mat
		add_child(post)
	var reader := MeshInstance3D.new()
	reader.name = "ReceptionCardReader"
	var reader_mesh := BoxMesh.new()
	reader_mesh.size = Vector3(0.14, 0.11, 0.055)
	reader.mesh = reader_mesh
	reader.position = Vector3(-14.18, -4.80, -7.60)
	reader.rotation_degrees.x = -12.0
	var reader_mat := StandardMaterial3D.new()
	reader_mat.albedo_color = Color(0.035, 0.04, 0.045, 1.0)
	reader_mat.metallic = 0.55
	reader_mat.roughness = 0.42
	reader.material_override = reader_mat
	add_child(reader)
	var led := MeshInstance3D.new()
	led.name = "ReceptionCardReaderLED"
	var led_mesh := BoxMesh.new()
	led_mesh.size = Vector3(0.018, 0.006, 0.004)
	led.mesh = led_mesh
	led.position = Vector3(-14.14, -4.76, -7.572)
	led.rotation_degrees.x = -12.0
	var led_mat := StandardMaterial3D.new()
	led_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	led_mat.albedo_color = Color(0.15, 1.0, 0.42, 1.0)
	led_mat.emission_enabled = true
	led_mat.emission = Color(0.12, 0.9, 0.35)
	led_mat.emission_energy_multiplier = 1.6
	led.material_override = led_mat
	add_child(led)
	for i in range(2):
		var grommet := MeshInstance3D.new()
		grommet.name = "ReceptionCableGrommet_%d" % i
		var grommet_mesh := CylinderMesh.new()
		grommet_mesh.top_radius = 0.045
		grommet_mesh.bottom_radius = 0.045
		grommet_mesh.height = 0.012
		grommet_mesh.radial_segments = 16
		grommet.mesh = grommet_mesh
		grommet.position = Vector3(-12.65 + float(i) * 1.3, -4.957, -8.38)
		grommet.material_override = post_mat
		add_child(grommet)

func _setup_wall_grime() -> void:
	_add_wall_decal(Vector3(-13.2, -3.55, -11.43), Vector3(-90.0, 0.0, 0.0), Vector3(3.0, 1.35, 0.30), "res://assets/art/fm/grunge_decal.png", Color(0.24, 0.21, 0.18, 0.55))
	_add_wall_decal(Vector3(-8.4, -3.10, -1.66), Vector3(90.0, 0.0, 0.0), Vector3(2.6, 1.15, 0.30), "res://assets/art/fm/grime_decal.png", Color(0.20, 0.18, 0.16, 0.50))
	_add_wall_decal(Vector3(-19.91, -3.30, -6.4), Vector3(0.0, 0.0, -90.0), Vector3(2.4, 1.20, 0.30), "res://assets/art/fm/grunge_decal.png", Color(0.22, 0.19, 0.16, 0.48))
	_add_wall_decal(Vector3(-4.07, -3.20, -4.6), Vector3(0.0, 0.0, 90.0), Vector3(2.2, 1.10, 0.30), "res://assets/art/fm/grime_decal.png", Color(0.20, 0.18, 0.16, 0.46))

func _add_wall_decal(pos: Vector3, rot: Vector3, decal_size: Vector3, texture_path: String, tint: Color) -> void:
	var texture := load(texture_path) as Texture2D
	if texture == null:
		return
	var decal := Decal.new()
	decal.name = "ReceptionWallGrime_%d" % get_child_count()
	decal.texture_albedo = texture
	decal.modulate = tint
	decal.albedo_mix = 0.55
	decal.size = decal_size
	decal.position = pos
	decal.rotation_degrees = rot
	decal.upper_fade = 0.25
	decal.lower_fade = 0.30
	decal.distance_fade_enabled = true
	decal.distance_fade_begin = 16.0
	decal.distance_fade_length = 5.0
	add_child(decal)

func _setup_dust() -> void:
	var particles := GPUParticles3D.new()
	particles.name = "DustMotes"
	particles.amount = 140
	particles.lifetime = 9.0
	particles.preprocess = 4.0
	particles.position = Vector3(-12.0, -3.40, -6.50)
	particles.visibility_aabb = AABB(Vector3(-8.0, -3.0, -5.0), Vector3(16.0, 6.0, 10.0))
	var process := ParticleProcessMaterial.new()
	process.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_BOX
	process.emission_box_extents = Vector3(7.0, 2.5, 4.5)
	process.direction = Vector3(0.0, 1.0, 0.0)
	process.spread = 35.0
	process.initial_velocity_min = 0.01
	process.initial_velocity_max = 0.04
	process.gravity = Vector3(0.0, -0.008, 0.0)
	process.scale_min = 0.5
	process.scale_max = 1.5
	process.color = Color(0.65, 0.60, 0.50, 0.22)
	particles.process_material = process
	var quad := QuadMesh.new()
	quad.size = Vector2(0.012, 0.012)
	var dust_material := StandardMaterial3D.new()
	dust_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	dust_material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	dust_material.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	dust_material.albedo_color = Color(0.70, 0.66, 0.55, 0.28)
	dust_material.disable_receive_shadows = true
	quad.material = dust_material
	particles.draw_pass_1 = quad
	add_child(particles)
	particles.emitting = true

func _setup_vignette() -> void:
	var shader := load("res://assets/shaders/vignette.gdshader") as Shader
	if shader == null:
		return
	var layer := CanvasLayer.new()
	layer.name = "VignetteLayer"
	layer.layer = 5
	add_child(layer)
	var rect := ColorRect.new()
	rect.name = "Vignette"
	rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.add_child(rect)
	rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	var material := ShaderMaterial.new()
	material.shader = shader
	material.set_shader_parameter("intensity", 0.28)
	material.set_shader_parameter("danger_color", Color(0.10, 0.01, 0.0, 1.0))
	rect.material = material

func _setup_environment() -> void:
	var world := WorldEnvironment.new()
	world.name = "ReceptionWorld"
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.012, 0.016, 0.024)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.24, 0.28, 0.35)
	env.ambient_light_energy = 0.06
	env.tonemap_mode = Environment.TONE_MAPPER_AGX
	env.tonemap_exposure = 1.15
	env.ssao_enabled = true
	env.ssao_radius = 1.05
	env.ssao_intensity = 1.55
	env.ssao_power = 1.35
	env.glow_enabled = true
	env.glow_intensity = 0.5
	env.glow_bloom = 0.10
	env.glow_hdr_threshold = 1.05
	env.fog_enabled = true
	env.fog_light_color = Color(0.14, 0.17, 0.21)
	env.fog_light_energy = 0.4
	env.fog_density = 0.008
	env.fog_height = 0.0
	env.fog_height_density = 0.0
	env.volumetric_fog_enabled = true
	env.volumetric_fog_density = 0.010
	env.volumetric_fog_albedo = Color(0.48, 0.56, 0.68)
	env.volumetric_fog_emission = Color(0.0, 0.0, 0.0)
	env.volumetric_fog_emission_energy = 0.0
	env.volumetric_fog_anisotropy = 0.25
	env.volumetric_fog_length = 24.0
	env.volumetric_fog_detail_spread = 1.6
	env.volumetric_fog_ambient_inject = 0.08
	env.volumetric_fog_sky_affect = 0.0
	env.adjustment_enabled = true
	env.adjustment_contrast = 1.12
	env.adjustment_saturation = 0.95
	env.adjustment_brightness = 1.02
	world.environment = env
	add_child(world)

func _add_box_collision(name: String, center: Vector3, size: Vector3) -> StaticBody3D:
	var body := StaticBody3D.new()
	body.name = name
	body.position = center
	var shape := BoxShape3D.new()
	shape.size = size
	var collider := CollisionShape3D.new()
	collider.shape = shape
	body.add_child(collider)
	add_child(body)
	return body

func _setup_physics_debris() -> void:
	_add_physics_can(Vector3(-16.4, -5.55, -6.6), "Can_West")
	_add_physics_can(Vector3(-7.3, -5.55, -4.2), "Can_East")
	_add_physics_can(Vector3(-13.8, -5.55, -9.8), "Can_Elevator")
	_add_physics_clipboard(Vector3(-10.2, -5.58, -7.15), "Clipboard_Floor")
	_add_physics_carton(Vector3(-8.4, -5.50, -8.4), "Carton_Floor")

func _physics_material(color: Color, metallic: float, roughness: float) -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.albedo_color = color
	mat.metallic = metallic
	mat.roughness = roughness
	return mat

func _add_physics_can(pos: Vector3, node_name: String) -> void:
	var body := RigidBody3D.new()
	body.name = node_name
	body.position = pos
	body.mass = 0.24
	body.continuous_cd = true
	body.collision_layer = 1
	body.collision_mask = 1
	var shape := CylinderShape3D.new()
	shape.radius = 0.045
	shape.height = 0.12
	var collider := CollisionShape3D.new()
	collider.shape = shape
	body.add_child(collider)
	var can := MeshInstance3D.new()
	var can_mesh := CylinderMesh.new()
	can_mesh.top_radius = 0.045
	can_mesh.bottom_radius = 0.045
	can_mesh.height = 0.12
	can_mesh.radial_segments = 16
	can.mesh = can_mesh
	can.material_override = _physics_material(Color(0.42, 0.45, 0.50), 0.82, 0.32)
	body.add_child(can)
	var ring := MeshInstance3D.new()
	var ring_mesh := TorusMesh.new()
	ring_mesh.inner_radius = 0.031
	ring_mesh.outer_radius = 0.044
	ring_mesh.rings = 12
	ring_mesh.ring_segments = 8
	ring.mesh = ring_mesh
	ring.position.y = 0.061
	ring.rotation_degrees.x = 90.0
	ring.material_override = can.material_override
	body.add_child(ring)
	var tab := MeshInstance3D.new()
	var tab_mesh := BoxMesh.new()
	tab_mesh.size = Vector3(0.026, 0.006, 0.042)
	tab.mesh = tab_mesh
	tab.position = Vector3(0.0, 0.064, 0.0)
	tab.material_override = can.material_override
	body.add_child(tab)
	add_child(body)

func _add_physics_clipboard(pos: Vector3, node_name: String) -> void:
	var body := RigidBody3D.new()
	body.name = node_name
	body.position = pos
	body.mass = 0.42
	body.continuous_cd = true
	body.collision_layer = 1
	body.collision_mask = 1
	var shape := BoxShape3D.new()
	shape.size = Vector3(0.24, 0.03, 0.32)
	var collider := CollisionShape3D.new()
	collider.shape = shape
	body.add_child(collider)
	var board := MeshInstance3D.new()
	var board_mesh := BoxMesh.new()
	board_mesh.size = Vector3(0.24, 0.018, 0.32)
	board.mesh = board_mesh
	board.material_override = _physics_material(Color(0.18, 0.10, 0.055), 0.0, 0.82)
	body.add_child(board)
	var paper := MeshInstance3D.new()
	var paper_mesh := BoxMesh.new()
	paper_mesh.size = Vector3(0.205, 0.005, 0.285)
	paper.mesh = paper_mesh
	paper.position.y = 0.012
	paper.material_override = _physics_material(Color(0.72, 0.70, 0.62), 0.0, 0.92)
	body.add_child(paper)
	var clip := MeshInstance3D.new()
	var clip_mesh := BoxMesh.new()
	clip_mesh.size = Vector3(0.085, 0.018, 0.032)
	clip.mesh = clip_mesh
	clip.position = Vector3(0.0, 0.025, -0.13)
	clip.material_override = _physics_material(Color(0.55, 0.57, 0.60), 0.85, 0.34)
	body.add_child(clip)
	add_child(body)

func _add_physics_carton(pos: Vector3, node_name: String) -> void:
	var body := RigidBody3D.new()
	body.name = node_name
	body.position = pos
	body.mass = 1.15
	body.continuous_cd = true
	body.collision_layer = 1
	body.collision_mask = 1
	var shape := BoxShape3D.new()
	shape.size = Vector3(0.38, 0.30, 0.32)
	var collider := CollisionShape3D.new()
	collider.shape = shape
	body.add_child(collider)
	var carton := MeshInstance3D.new()
	var carton_mesh := BoxMesh.new()
	carton_mesh.size = Vector3(0.38, 0.30, 0.32)
	carton.mesh = carton_mesh
	carton.material_override = _physics_material(Color(0.42, 0.30, 0.19), 0.0, 0.88)
	body.add_child(carton)
	var tape := MeshInstance3D.new()
	var tape_mesh := BoxMesh.new()
	tape_mesh.size = Vector3(0.055, 0.004, 0.322)
	tape.mesh = tape_mesh
	tape.position.y = 0.151
	tape.material_override = _physics_material(Color(0.66, 0.56, 0.34), 0.0, 0.72)
	body.add_child(tape)
	add_child(body)

func _setup_collisions() -> void:
	# Suelo y perímetro.
	_add_box_collision("COL_Floor", Vector3(-12.0, -5.80, -6.70), Vector3(16.0, 0.30, 10.0))
	_add_box_collision("COL_East", Vector3(-4.0, -2.82, -6.70), Vector3(0.30, 6.0, 10.0))
	_add_box_collision("COL_West", Vector3(-20.0, -2.82, -6.70), Vector3(0.30, 6.0, 10.0))
	# Muro sur con hueco de puerta; se bloquea el hueco para no caer al vacío.
	_add_box_collision("COL_South_L", Vector3(-16.40, -2.82, -1.70), Vector3(7.20, 6.0, 0.30))
	_add_box_collision("COL_South_R", Vector3(-7.60, -2.82, -1.70), Vector3(7.20, 6.0, 0.30))
	_add_box_collision("COL_South_Door", Vector3(-12.0, -2.82, -1.72), Vector3(1.62, 6.0, 0.16))
	# Muro norte segmentado por el ascensor.
	_add_box_collision("COL_North_L", Vector3(-19.22, -2.82, -11.68), Vector3(1.56, 6.0, 0.30))
	_add_box_collision("COL_North_R", Vector3(-10.28, -2.82, -11.68), Vector3(12.56, 6.0, 0.30))
	_add_box_collision("COL_North_Lintel", Vector3(-17.50, -1.42, -11.68), Vector3(1.88, 3.20, 0.30))
	# Cabina del ascensor.
	_add_box_collision("COL_Cabin_Floor", Vector3(-17.50, -5.80, -12.72), Vector3(1.88, 0.30, 1.80))
	_add_box_collision("COL_Cabin_Back", Vector3(-17.50, -2.82, -13.62), Vector3(1.88, 6.0, 0.20))
	_add_box_collision("COL_Cabin_W", Vector3(-18.44, -2.82, -12.72), Vector3(0.20, 6.0, 1.80))
	_add_box_collision("COL_Cabin_E", Vector3(-16.56, -2.82, -12.72), Vector3(0.20, 6.0, 1.80))
	_add_box_collision("COL_Cabin_Ceiling", Vector3(-17.50, -3.05, -12.72), Vector3(1.88, 0.20, 1.80))
	_door_collider = _add_box_collision(
		"COL_ElevatorDoors",
		Vector3(-17.50, -4.30, -11.55),
		Vector3(1.88, 2.55, 0.12)
	)
	# Mostrador y mobiliario principal.
	_add_box_collision("COL_Counter", Vector3(-12.0, -5.31, -8.0), Vector3(4.36, 0.68, 1.32))
	_add_box_collision("COL_HideCabinet", Vector3(-15.40, -4.60, -2.375), Vector3(1.05, 2.10, 1.05))
	for prop_name in [
		"NEXUS_V05_C_REC_TABLE_TOP",
		"NEXUS_V05_REC_BENCH",
		"NEXUS_ASSET_L1_REC_WAIT_CHAIR_0_ROOT",
		"NEXUS_ASSET_L1_REC_WAIT_CHAIR_1_ROOT",
		"NEXUS_ASSET_L1_REC_WAIT_CHAIR_2_ROOT",
		"NEXUS_L1_DIS_BREAK_COUNTER",
		"NEXUS_L1_DIS_CHAIR_REC_A",
		"NEXUS_L1_DIS_CHAIR_REC_B",
		"NEXUS_V05_REC_PLANTER_0",
		"NEXUS_V05_REC_PLANTER_1",
		"NEXUS_V05_REC_SUITCASE",
		"NEXUS_V05_OFFICE_WALL_W_0",
		"NEXUS_V05_OFFICE_WALL_W_1",
		"NEXUS_V05_OFFICE_WALL_W_2",
		"NEXUS_V05_OFFICE_WALL_N",
		"NEXUS_V05_OFFICE_WALL_E",
		"NEXUS_V05_OFFICE_WALL_OFF_TOP",
		"NEXUS_V05_OFFICE_WALL_REST_TOP",
		"NEXUS_V05_OFFICE_PARTITION",
		"NEXUS_V05_REST_PARTITION",
		"NEXUS_V05_REST_PARTITION_TRIM",
		"NEXUS_V05_OFFICE_DOOR_LEAF",
		"NEXUS_V05_OFFICE_DOOR_GLASS",
		"NEXUS_V05_REST_DOOR_LEAF",
		"NEXUS_V05_RECEPCION_DOOR_LEAF",
		"NEXUS_V05_RECEPCION_DOOR_GLASS",
		"NEXUS_V05_OFFICE_CABINET",
		"NEXUS_V05_OFFICE_HVAC",
		"NEXUS_ASSET_L1_OFFICE_DESK_ROOT",
		"NEXUS_V05_REST_SINK_COUNTER",
		"NEXUS_ASSET_L1_OFFICE_CHAIR_ROOT",
		"NEXUS_ASSET_L1_REC_DESK_CHAIR_ROOT",
		"NEXUS_L1_DIS_CHAIR_OFFICE",
		"NEXUS_L1_DIS_CHAIR_CORR",
		"NEXUS_L1_DIS_BIN_REC",
		"NEXUS_L1_DIS_BREAK_BIN",
		"NEXUS_L1_DIS_BAG_REC_trashbag_LOD1",
		"NEXUS_L1_DIS_MONITOR_REC",
		"NEXUS_L1_DIS_CORR_PANEL_W",
		"NEXUS_V05_OFFICE_BIN",
		"NEXUS_V05_REST_BIN",
		"NEXUS_L1_DIS_REST_BIN_TIPPED",
		"NEXUS_L1_DIS_REST_BUCKET",
		"NEXUS_V05_REST_TOILET_BOWL",
		"NEXUS_V05_REST_TOILET_TANK",
	]:
		_add_glb_aabb_collider(prop_name)

func _add_glb_aabb_collider(node_name: String) -> void:
	var node := glb_root.find_child(node_name, true, false)
	if node == null:
		return
	var box := AABB()
	var has_box := false
	if node is MeshInstance3D:
		box = (node as MeshInstance3D).global_transform * (node as MeshInstance3D).get_aabb()
		has_box = true
	for child in node.find_children("*", "MeshInstance3D", true, false):
		var mesh := child as MeshInstance3D
		var child_box := mesh.global_transform * mesh.get_aabb()
		box = child_box if not has_box else box.merge(child_box)
		has_box = true
	if not has_box or box.size.y < 0.15:
		return
	_add_box_collision("COL_" + node_name, box.get_center(), box.size)

func _cache_elevator_doors() -> void:
	_door_l = glb_root.find_child("NEXUS_V05_C_REC_ELEV_L", true, false) as Node3D
	_door_r = glb_root.find_child("NEXUS_V05_C_REC_ELEV_R", true, false) as Node3D
	if _door_l != null:
		_door_l_closed = _door_l.global_position.x
	if _door_r != null:
		_door_r_closed = _door_r.global_position.x

func _setup_loot() -> void:
	for source_name in LOOT_SPECS.keys():
		var source := glb_root.find_child(source_name, true, false) as Node3D
		if source == null:
			push_warning("Loot no encontrado en GLB: %s" % source_name)
			continue
		var spec: Dictionary = LOOT_SPECS[source_name]
		var bounds := _global_aabb(source)
		var center := bounds.get_center()
		var size := bounds.size
		var item = LOOT_SCRIPT.new()
		item.name = "Loot_%s" % spec["id"]
		item.item_name = spec["name"]
		item.item_mass = float(spec["mass"])
		item.loot_id = spec["id"]
		item.loot_value = int(spec["value"])
		item.min_players = int(spec["min_players"])
		item.global_transform = source.global_transform
		add_child(item)
		item.game = self
		var shape := BoxShape3D.new()
		shape.size = size + Vector3(0.03, 0.03, 0.03)
		var collider := CollisionShape3D.new()
		collider.shape = shape
		collider.position = center - item.global_position
		item.add_child(collider)
		for child in source.get_children():
			child.reparent(item, true)
		source.queue_free()
		loot_items.append(item)

func _global_aabb(node: Node3D) -> AABB:
	var result := AABB()
	var first := true
	for child in node.find_children("*", "MeshInstance3D", true, false):
		var mesh_instance := child as MeshInstance3D
		if mesh_instance == null or mesh_instance.mesh == null:
			continue
		var box: AABB = mesh_instance.global_transform * mesh_instance.get_aabb()
		if first:
			result = box
			first = false
		else:
			result = result.merge(box)
	return result

func _setup_hiding_spot() -> void:
	hiding_spot = HIDING_SCRIPT.new()
	hiding_spot.name = "HideCabinet"
	hiding_spot.display_name = "ARMARIO"
	hiding_spot.position = Vector3(-15.40, -5.65, -2.375)
	hiding_spot.game = self
	var shape := BoxShape3D.new()
	shape.size = Vector3(1.05, 2.05, 1.05)
	var collider := CollisionShape3D.new()
	collider.shape = shape
	hiding_spot.add_child(collider)
	var hide_point := Marker3D.new()
	hide_point.name = "HidePoint"
	hide_point.position = Vector3(0.0, 1.05, 0.0)
	hiding_spot.add_child(hide_point)
	var exit_point := Marker3D.new()
	exit_point.name = "ExitPoint"
	exit_point.position = Vector3(0.0, 0.0, -1.2)
	hiding_spot.add_child(exit_point)
	add_child(hiding_spot)

func _setup_noise_trap() -> void:
	noise_trap = NOISE_TRAP_SCRIPT.new()
	noise_trap.name = "NoiseTrap"
	noise_trap.position = Vector3(-12.5, -5.65, -3.75)
	noise_trap.game = self
	add_child(noise_trap)

func _setup_extraction() -> void:
	extraction = EXTRACTION_SCRIPT.new()
	extraction.name = "ReceptionExtraction"
	extraction.position = Vector3(-12.0, -4.40, -6.70)
	extraction.delivery_center = EXTRACTION_CENTER
	extraction.game = self
	add_child(extraction)
	extraction.extraction_progress.connect(_on_extraction_progress)
	extraction.extraction_completed.connect(_on_extraction_completed)

func _setup_player() -> void:
	player = PLAYER_SCENE.instantiate()
	player.name = "Player"
	player.position = SPAWN
	add_child(player)
	player.add_to_group("fm_player")
	player.set_game(self)
	player.network_client = false
	player.set_flashlight_model(true)
	_tune_player_flashlight()

func _tune_player_flashlight() -> void:
	if player == null or player.flashlight == null:
		return
	player.flashlight.light_color = Color(1.0, 0.90, 0.72)
	player.flashlight.light_energy = 12.0
	player.flashlight.spot_range = 24.0
	player.flashlight.spot_angle = 32.0
	player.flashlight.spot_angle_attenuation = 0.90
	player.flashlight.shadow_enabled = true
	var gradient := Gradient.new()
	gradient.set_color(0, Color(1.0, 1.0, 1.0, 1.0))
	gradient.set_color(1, Color(0.05, 0.05, 0.05, 1.0))
	var projector := GradientTexture2D.new()
	projector.gradient = gradient
	projector.width = 128
	projector.height = 128
	projector.fill = GradientTexture2D.FILL_RADIAL
	projector.fill_from = Vector2(0.5, 0.5)
	projector.fill_to = Vector2(1.0, 0.5)
	player.flashlight.light_projector = projector
	var spill := SpotLight3D.new()
	spill.name = "FlashlightSpill"
	spill.light_color = Color(1.0, 0.86, 0.66)
	spill.light_energy = 2.2
	spill.spot_range = 11.0
	spill.spot_angle = 58.0
	spill.spot_angle_attenuation = 1.7
	spill.shadow_enabled = false
	player.camera.add_child(spill)

func _setup_hud() -> void:
	hud = HUD_SCRIPT.new()
	hud.name = "HUD"
	add_child(hud)
	hud.set_objective("RECUPERAR BOTÍN", "Recepción NEXUS · Nivel 1")
	hud.set_status("LLEVÁ UN OBJETO AL ASCENSOR DE EXTRACCIÓN")
	hud.set_battery(1.0, true)
	hud.set_stamina(1.0)
	hud.set_stress(0.0)

func _setup_audio() -> void:
	Audio.stop_music()
	var source := load("res://assets/audio/ambience/ambience.wav") as AudioStreamWAV
	if source == null:
		return
	var looped := source.duplicate() as AudioStreamWAV
	looped.loop_mode = AudioStreamWAV.LOOP_FORWARD
	looped.loop_begin = 0
	looped.loop_end = int(looped.get_length() * looped.mix_rate)
	ambience = AudioStreamPlayer3D.new()
	ambience.name = "ReceptionAmbience"
	ambience.stream = looped
	ambience.position = Vector3(-12.0, -3.0, -6.7)
	ambience.unit_size = 11.0
	ambience.max_distance = 32.0
	ambience.volume_db = -20.0
	add_child(ambience)
	ambience.play()

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		get_tree().change_scene_to_file("res://scenes/menu.tscn")

func _process(delta: float) -> void:
	if state != State.PLAYING:
		return
	if player == null or not is_instance_valid(player):
		return
	if player.global_position.y < -12.0:
		player.global_position = SPAWN
		player.velocity = Vector3.ZERO
		notify("POSICIÓN RESTABLECIDA")
	_update_emergency_flicker(delta)
	_update_hud()
	if _status_timer > 0.0:
		_status_timer -= delta
		if _status_timer <= 0.0:
			_status_override = ""

func _update_emergency_flicker(delta: float) -> void:
	_flicker_time += delta
	for i in range(_emergency_lights.size()):
		var light := _emergency_lights[i]
		if light == null or not is_instance_valid(light):
			continue
		var base := _emergency_base_energy[i]
		var wobble := sin(_flicker_time * 7.3 + float(i) * 2.1) * 0.55 + sin(_flicker_time * 17.9 + float(i)) * 0.45
		light.light_energy = base * (0.86 + 0.14 * wobble)

func _update_hud() -> void:
	if hud == null:
		return
	hud.set_battery(float(player.battery), bool(player.flashlight_on))
	hud.set_stamina(float(player.get("stamina")) if player.get("stamina") != null else 0.0)
	var stress_value = player.get("stress")
	hud.set_stress(float(stress_value) if stress_value != null else 0.0)
	hud.set_hidden(bool(player.hidden))
	hud.set_prompt(player.get_interaction_prompt())
	hud.set_watcher_observed(false)
	if _status_timer > 0.0:
		hud.set_status(_status_override)
	elif extraction != null and extraction.has_player():
		var delivered := get_delivered_loot_count(EXTRACTION_CENTER, extraction.delivery_radius_m)
		if delivered > 0:
			hud.set_status("EXTRACCIÓN LISTA · PERMANECÉ EN RECEPCIÓN")
		else:
			hud.set_status("LLEVÁ UN OBJETO AL ASCENSOR DE EXTRACCIÓN")
	else:
		hud.set_status("RECEPCIÓN NEXUS · BUSCÁ EL BOTÍN")

func notify(text: String) -> void:
	_status_override = text
	_status_timer = 2.5
	if hud != null:
		hud.set_status(text)

func get_active_player_count() -> int:
	if player != null and is_instance_valid(player):
		return 1
	return 0

func all_alive_players_inside(area: Area3D) -> bool:
	if player == null or not is_instance_valid(player):
		return false
	return area.players_inside.has(player)

func any_alive_player_inside(area: Area3D) -> bool:
	return all_alive_players_inside(area)

func get_delivered_loot_count(center: Vector3, radius: float) -> int:
	var count := 0
	for item in loot_items:
		if item == null or not is_instance_valid(item):
			continue
		if item.global_position.distance_to(center) <= radius:
			count += 1
	return count

func get_total_loot_value() -> int:
	var total := 0
	for item in loot_items:
		if item != null and is_instance_valid(item):
			total += item.loot_value
	return total

func animate_elevator_doors(open: bool) -> void:
	if _door_l == null and _door_r == null:
		return
	if _door_collider != null:
		_door_collider.collision_layer = 0 if open else 1
	if _door_tween != null and _door_tween.is_valid():
		_door_tween.kill()
	_door_tween = create_tween().set_parallel(true)
	var left_target := _door_l_closed - (1.0 if open else 0.0)
	var right_target := _door_r_closed + (1.0 if open else 0.0)
	if _door_l != null:
		_door_tween.tween_property(_door_l, "global_position:x", left_target, 1.5)
	if _door_r != null:
		_door_tween.tween_property(_door_r, "global_position:x", right_target, 1.5)

func _on_extraction_progress(stage: String, seconds_left: float) -> void:
	on_extraction_progress(stage, seconds_left)

func _on_extraction_started() -> void:
	_elevator_closing = false
	animate_elevator_doors(true)
	Audio.play_sfx("deliver", -10.0, 0.9)
	notify("EXTRACCIÓN INICIADA · PERMANECÉ EN RECEPCIÓN")

func _on_extraction_cancelled() -> void:
	if state != State.PLAYING:
		return
	if _elevator_closing:
		animate_elevator_doors(true)
	_elevator_closing = false
	notify("EXTRACCIÓN CANCELADA")

func on_extraction_started() -> void:
	_on_extraction_started()

func on_extraction_cancelled() -> void:
	_on_extraction_cancelled()

func on_extraction_progress(stage: String, seconds_left: float) -> void:
	if hud == null:
		return
	var text := ""
	match stage:
		"activando":
			text = "EXTRACCIÓN EN %0.1f s" % seconds_left
		"apertura":
			text = "ABRIENDO ASCENSOR"
		"espera":
			text = "PERMANECÉ EN RECEPCIÓN · %0.1f s" % seconds_left
		"cierre":
			text = "CERRANDO ASCENSOR"
			if not _elevator_closing:
				_elevator_closing = true
				animate_elevator_doors(false)
				Audio.play_sfx("click", -12.0, 0.72)
		"viaje":
			text = "ASCENSOR EN MOVIMIENTO"
		"llegada":
			text = "EXTRACCIÓN COMPLETADA"
		_:
			text = "EXTRACCIÓN EN CURSO · %0.1f s" % seconds_left
	_status_override = text
	_status_timer = 0.3
	hud.set_status(text)

func _on_extraction_completed(delivered: int) -> void:
	if state != State.PLAYING:
		return
	state = State.WON
	if player != null:
		player.set_physics_process(false)
		player.set_process_input(false)
	Audio.play_sfx("win", -4.0)
	if hud != null:
		hud.show_end("EXTRACCIÓN COMPLETADA", "BOTÍN RECUPERADO: %d" % delivered)
	print("RECEPTION_WON delivered=%d value=%d" % [delivered, get_total_loot_value()])

func on_artifact_picked(who: Node) -> void:
	if who == player and who.carried_item != null:
		notify("OBJETO RECOGIDO · %s" % who.carried_item.item_name)
		if hud != null:
			hud.set_objective("BOTÍN EN MANOS", "Llevalo al ascensor de extracción")

func on_artifact_dropped() -> void:
	notify("OBJETO SOLTADO")

func on_player_hidden(is_hidden: bool) -> void:
	if hud != null:
		hud.set_hidden(is_hidden)
	notify("ESCONDIDO" if is_hidden else "SALISTE DEL ESCONDITE")

func on_noise_trap_triggered() -> void:
	notify("RUIDO · ALGO PUEDE HABER ESCUCHADO")

func emit_noise(_position: Vector3, _radius: float, _kind: String) -> void:
	pass

func on_battery_taken(_index: int, _who: Node) -> void:
	pass

func on_player_caught() -> void:
	if state == State.PLAYING:
		state = State.LOST
		if hud != null:
			hud.show_end("MISIÓN FALLIDA", "FUISTE ALCANZADO")

func debug_complete_extraction() -> void:
	if state == State.PLAYING:
		_on_extraction_completed(get_delivered_loot_count(EXTRACTION_CENTER, 2.4))
