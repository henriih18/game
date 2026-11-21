extends Node3D

## Nivel 1 completo: recepción, corredor, seguridad, control, vestuarios,
## almacén, mantenimiento, conector de servicio y oficina/aseo.
## Carga el GLB completo en runtime y añade la capa jugable local.

const GLB_PATH := "res://assets/models/fm/level1_nexus.glb"
const PLAYER_SCENE := preload("res://scenes/fm/fm_player.tscn")
const LOOT_SCRIPT := preload("res://scripts/fm/fm_reception_loot.gd")
const EXTRACTION_SCRIPT := preload("res://scripts/fm/fm_reception_extraction.gd")
const HIDING_SCRIPT := preload("res://scripts/fm/fm_hiding_spot.gd")
const NOISE_TRAP_SCRIPT := preload("res://scripts/fm/fm_noise_trap.gd")
const HUD_SCRIPT := preload("res://scripts/fm/fm_hud.gd")
const WATCHER_SCENE := preload("res://scenes/fm/fm_watcher.tscn")
const DOOR_SCRIPT := preload("res://scripts/fm/fm_level1_door.gd")
const DRAWER_SCRIPT := preload("res://scripts/fm/fm_level1_drawer.gd")
const LOCKER_SCRIPT := preload("res://scripts/fm/fm_level1_locker.gd")
const ALARM_SCRIPT := preload("res://scripts/fm/fm_level1_alarm.gd")
const SURFACE_AUDIO_SCRIPT := preload("res://scripts/fm/fm_level1_surface_audio.gd")
const ART_PASS_SCRIPT := preload("res://scripts/fm/fm_level1_art_pass.gd")

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

const LOOT_TARGETS := {
	"NEXUS_V05_REC_LOOT_CASE_0": Vector3(5.6, -5.55, -6.4),
	"NEXUS_V05_REC_LOOT_SAMPLE_0": Vector3(-16.5, -5.55, 6.0),
	"NEXUS_V05_REC_LOOT_CRATE_0": Vector3(2.0, -5.55, 6.0),
	"NEXUS_V05_REC_LOOT_DOCS_0": Vector3(-6.2, -4.84, -6.9),
	"NEXUS_V05_REC_LOOT_DRIVE_0": Vector3(13.0, -4.90, -5.8),
}

var state: State = State.PLAYING
var player
var hud
var glb_root: Node3D
var extraction
var watcher
var loot_items: Array[Node3D] = []
var ambience: AudioStreamPlayer3D
var _status_override := ""
var _status_timer := 0.0
var _emergency_lights: Array[OmniLight3D] = []
var _emergency_base_energy: Array[float] = []
var _flicker_time := 0.0
var _collider_count := 0
var _elevator_l: Node3D
var _elevator_r: Node3D
var _elevator_l_body: AnimatableBody3D
var _elevator_r_body: AnimatableBody3D
var _elevator_l_closed := 0.0
var _elevator_r_closed := 0.0
var _elevator_tween: Tween
var _mipmap_cache := {}
var _mipmap_fixed := 0
var level_ready := false
var _red_alert := false
var _monitor_screen_a: Texture2D
var _monitor_screen_b: Texture2D
var _alert_debug_down := false

func _ready() -> void:
	_setup_environment()
	if not _load_glb():
		return
	await get_tree().process_frame
	_setup_collisions()
	_cache_elevator_doors()
	_setup_doors()
	_setup_drawers()
	_setup_lockers()
	_setup_alarms()
	_setup_east_shutter()
	_disable_general_emission()
	_setup_physics_debris()
	_tune_blood_surfaces()
	_replace_counter_monitors()
	_setup_counter_details()
	_tune_emergency_signage()
	_setup_wall_grime()
	_setup_wet_patches()
	_setup_story_decals()
	_setup_emergency_lights()
	_setup_wayfinding()
	_setup_atmosphere_particles()
	_setup_loot()
	_setup_hiding_spots()
	_setup_noise_traps()
	_setup_extraction()
	_setup_player()
	_setup_watcher()
	_setup_hud()
	_setup_audio()
	_setup_postprocess()
	var art_pass := ART_PASS_SCRIPT.new()
	art_pass.name = "Level1ArtPass"
	add_child(art_pass)
	art_pass.apply(self)
	_ensure_material_mipmaps()
	level_ready = true
	print("LEVEL1_READY loot=%d colliders=%d" % [loot_items.size(), _collider_count])

## Las texturas embebidas en los GLB llegan sin mipmaps. Se regeneran una sola
## vez al final del montaje, cuando ya existen todos los props y materiales.
func _ensure_material_mipmaps() -> void:
	_mipmap_cache.clear()
	_mipmap_fixed = 0
	var mats := {}
	for node in find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi == null or mi.mesh == null:
			continue
		for i in range(mi.mesh.get_surface_count()):
			var mat := mi.mesh.surface_get_material(i)
			if mat != null:
				mats[mat.get_instance_id()] = mat
	for id in mats:
		var mat = mats[id]
		if not (mat is StandardMaterial3D):
			continue
		var sm := mat as StandardMaterial3D
		var albedo := _mipmapped_texture(sm.albedo_texture)
		if albedo != null:
			sm.albedo_texture = albedo
		var normal := _mipmapped_texture(sm.normal_texture, true)
		if normal != null:
			sm.normal_texture = normal
		var rough := _mipmapped_texture(sm.roughness_texture)
		if rough != null:
			sm.roughness_texture = rough
		var emission := _mipmapped_texture(sm.emission_texture)
		if emission != null:
			sm.emission_texture = emission
		if sm.ao_enabled:
			var ao := _mipmapped_texture(sm.ao_texture)
			if ao != null:
				sm.ao_texture = ao
	print("LEVEL1_MIPMAPS materials=%d regenerated=%d" % [mats.size(), _mipmap_fixed])

func _mipmapped_texture(tex: Texture2D, renormalize := false) -> Texture2D:
	if tex == null:
		return null
	var key := "%d:%s" % [tex.get_instance_id(), renormalize]
	if _mipmap_cache.has(key):
		return _mipmap_cache[key]
	var result := tex
	if tex is ImageTexture:
		var img := tex.get_image()
		if img != null and not img.has_mipmaps() and img.get_width() > 1 and img.get_height() > 1:
			var copy := Image.new()
			copy.copy_from(img)
			if copy.is_compressed() and copy.decompress() != OK:
				_mipmap_cache[key] = tex
				return tex
			copy.generate_mipmaps(renormalize)
			result = ImageTexture.create_from_image(copy)
			_mipmap_fixed += 1
	_mipmap_cache[key] = result
	return result

func _load_glb() -> bool:
	var document := GLTFDocument.new()
	var gltf_state := GLTFState.new()
	var err: Error = document.append_from_file(GLB_PATH, gltf_state)
	if err != OK:
		push_error("No se pudo cargar el GLB del Nivel 1: %s" % err)
		return false
	glb_root = document.generate_scene(gltf_state)
	if glb_root == null:
		push_error("El GLB del Nivel 1 no generó escena")
		return false
	glb_root.name = "Level1GLB"
	add_child(glb_root)
	return true

func _setup_environment() -> void:
	var world := WorldEnvironment.new()
	world.name = "Level1World"
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.006, 0.008, 0.012)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.20, 0.24, 0.30)
	env.ambient_light_energy = 0.075
	env.tonemap_mode = Environment.TONE_MAPPER_AGX
	env.tonemap_exposure = 1.16
	env.ssao_enabled = true
	env.ssao_radius = 1.0
	env.ssao_intensity = 1.6
	env.ssao_power = 1.35
	env.ssr_enabled = true
	env.ssr_max_steps = 32
	env.ssr_fade_in = 0.15
	env.ssr_fade_out = 2.0
	env.ssr_depth_tolerance = 0.25
	env.glow_enabled = true
	env.glow_intensity = 0.5
	env.glow_bloom = 0.08
	env.glow_hdr_threshold = 1.0
	env.fog_enabled = true
	env.fog_light_color = Color(0.07, 0.085, 0.11)
	env.fog_light_energy = 0.25
	env.fog_density = 0.006
	env.volumetric_fog_enabled = true
	env.volumetric_fog_density = 0.010
	env.volumetric_fog_albedo = Color(0.42, 0.49, 0.60)
	env.volumetric_fog_emission = Color(0.0, 0.0, 0.0)
	env.volumetric_fog_emission_energy = 0.0
	env.volumetric_fog_anisotropy = 0.28
	env.volumetric_fog_length = 32.0
	env.volumetric_fog_detail_spread = 1.7
	env.volumetric_fog_ambient_inject = 0.04
	env.volumetric_fog_sky_affect = 0.0
	env.adjustment_enabled = true
	env.adjustment_contrast = 1.08
	env.adjustment_saturation = 1.0
	env.adjustment_brightness = 1.02
	world.environment = env
	add_child(world)

func _skip_collider(name: String) -> bool:
	# Las hojas del ascensor necesitan colliders móviles; se crean aparte en
	# _cache_elevator_doors() para que acompañen a la animación.
	if name in [
		"NEXUS_V05_C_REC_ELEV_L", "NEXUS_V05_C_REC_ELEV_R",
		"NEXUS_V05_ELEV_DOOR_SEAL_L", "NEXUS_V05_ELEV_DOOR_SEAL_R",
		"NEXUS_V05_ELEV_DOOR_SKIRT_L", "NEXUS_V05_ELEV_DOOR_SKIRT_R",
	]:
		return true
	var upper := name.to_upper()
	for token in [
		"BLOOD", "PAPER", "DECAL", "SIGN", "TEXT", "SCREEN", "LIGHT",
		"LAMP", "BULB", "LED", "CABLE", "WIRE", "HOSE", "CORD", "ROPE",
		"SMOKE", "SPRINK", "ARROW", "HAZ", "RUG", "MAT", "CARPET",
		"FOLIAGE", "LOOT", "TRAP", "EXTRACT", "RING", "TRIGGER",
		"MARKER", "BASEBOARD", "WAINSCOT", "TRIM", "SKIRT", "PLATE",
		"FLOOR_LINE", "FLOOR_SIGN", "FLOORPAPER", "DIFFUSER",
		"GRILLE", "VENT_SLAT", "TRAY_RAIL", "RUNG",
		# Decals de suciedad/humedad que no deben generar cuerpos estáticos.
		"WALLSTAIN", "STORE_STAIN", "DIS_WATER", "DIS_OIL", "DIS_HAND",
		"GRIME", "DAMP_PATCH",
	]:
		if token in upper:
			return true
	return false

func _setup_collisions() -> void:
	var seen := {}
	for node in glb_root.find_children("*", "MeshInstance3D", true, false):
		var mesh_instance := node as MeshInstance3D
		if mesh_instance == null or mesh_instance.mesh == null:
			continue
		if _skip_collider(mesh_instance.name):
			continue
		var box: AABB = mesh_instance.global_transform * mesh_instance.get_aabb()
		var size := box.size
		if size.y < 0.10:
			continue
		if maxf(size.x, size.z) < 0.24:
			continue
		if size.length() > 70.0:
			continue
		var key := "%.2f|%.2f|%.2f|%.2f|%.2f|%.2f" % [
			box.position.x, box.position.y, box.position.z,
			size.x, size.y, size.z,
		]
		if seen.has(key):
			continue
		seen[key] = true
		_add_box_collision("COL_%03d_%s" % [_collider_count, mesh_instance.name], box.get_center(), size)
		_collider_count += 1
	print("LEVEL1_COLLIDERS ", _collider_count)

func _setup_doors() -> void:
	# Decal de pared claro que flotaba junto al acceso de Seguridad.
	var stain := glb_root.find_child("NEXUS_V05_D_CORR_WALLSTAIN_0", true, false)
	if stain != null:
		stain.visible = false
	_add_door("RECEPCION", Vector3(-12.86, -5.65, -1.70), 95.0, {
		"type": "auto_slide", "lock": "none", "powered": true,
	})
	_add_door("SEGURIDAD", Vector3(2.14, -5.65, -1.70), 95.0, {
		"type": "armored_swing", "lock": "security", "code": "0451",
	})
	_add_door("CONTROL", Vector3(12.14, -5.65, -1.70), 95.0, {
		"type": "double_swing_seq", "lock": "basic",
	})
	_add_door("ALMACEN", Vector3(-2.86, -5.65, 1.70), -95.0, {
		"type": "heavy_slide", "lock": "basic", "players": 2,
	})
	_add_door("VESTUARIOS", Vector3(-14.86, -5.65, 1.70), -95.0, {
		"type": "light_swing", "lock": "basic",
	})
	_add_door("MANTENIMIENTO", Vector3(12.14, -5.65, 1.70), -95.0, {
		"type": "maintenance_swing", "lock": "maintenance",
	})

func _add_door(id: String, pos: Vector3, angle_deg: float, config: Dictionary = {}) -> void:
	var door = DOOR_SCRIPT.new()
	door.position = pos
	add_child(door)
	door.setup(id, 1.58, 3.00, 1.0, angle_deg, self, config)

func set_red_alert(active: bool) -> void:
	_red_alert = active
	for door in find_children("Door_*", "Node3D", true, false):
		if door.has_method("set_red_alert"):
			door.set_red_alert(active)

func get_door_states() -> Array:
	var out: Array = []
	for door in find_children("Door_*", "Node3D", true, false):
		if door.has_method("get_network_state"):
			out.append(door.get_network_state())
	return out

func apply_door_states(states: Array) -> void:
	for state in states:
		if not (state is Dictionary):
			continue
		var id := String(state.get("id", ""))
		var door := find_child("Door_%s" % id, true, false)
		if door != null and door.has_method("apply_network_state"):
			door.apply_network_state(state)

func _setup_drawers() -> void:
	for i in range(3):
		_add_drawer(
			"NEXUS_V05_OFFICE_CABINET_DRAWER_%d" % i,
			Vector3(0.32, 0.0, 0.0),
			"CAJÓN OFICINA %d" % (i + 1)
		)
	for i in range(3):
		_add_drawer(
			"NEXUS_V05_SEC_CAB_DRAWER_%d" % i,
			Vector3(0.0, 0.0, 0.35),
			"CAJÓN SEGURIDAD %d" % (i + 1)
		)
	for i in range(2):
		_add_drawer(
			"NEXUS_V05_REC_COUNTER_DRAWER_FRONT_%d" % i,
			Vector3(0.0, 0.0, 0.32),
			"CAJÓN MOSTRADOR %d" % (i + 1)
		)

func _add_drawer(node_name: String, offset: Vector3, label: String) -> void:
	var target := glb_root.find_child(node_name, true, false) as Node3D
	if target == null:
		return
	var interact = DRAWER_SCRIPT.new()
	add_child(interact)
	interact.setup(target, offset, label, self)

func _setup_lockers() -> void:
	for spec in [
		["A", Vector3(-18.28, -5.65, 2.40)],
		["B", Vector3(-17.38, -5.65, 2.40)],
		["C", Vector3(-11.90, -5.65, 2.40)],
		["D", Vector3(-11.00, -5.65, 2.40)],
	]:
		var locker = LOCKER_SCRIPT.new()
		locker.position = spec[1]
		add_child(locker)
		locker.setup(spec[0], 0.86, 1.90, self)

func _setup_alarms() -> void:
	for spec in [
		["STORE", Vector3(-10.0, -4.15, -1.62), Vector3(-2.0, -5.6, 5.5)],
		["SECURITY", Vector3(0.0, -4.15, -1.62), Vector3(3.0, -5.6, -6.0)],
		["MAINT", Vector3(10.0, -4.15, -1.62), Vector3(13.0, -5.6, 5.0)],
	]:
		var alarm = ALARM_SCRIPT.new()
		add_child(alarm)
		alarm.setup(spec[0], spec[1], spec[2], self)

func _setup_east_shutter() -> void:
	_add_box_collision("COL_EastShutter", Vector3(22.0, -3.7, 0.0), Vector3(0.30, 3.9, 3.4))
	var shutter := MeshInstance3D.new()
	shutter.name = "EastShutterPanel"
	var shutter_mesh := BoxMesh.new()
	shutter_mesh.size = Vector3(0.18, 3.8, 3.3)
	shutter.mesh = shutter_mesh
	shutter.position = Vector3(22.0, -3.7, 0.0)
	var shutter_mat := StandardMaterial3D.new()
	shutter_mat.albedo_color = Color(0.055, 0.06, 0.065, 1.0)
	shutter_mat.metallic = 0.72
	shutter_mat.roughness = 0.38
	shutter.material_override = shutter_mat
	add_child(shutter)
	var stripe := MeshInstance3D.new()
	stripe.name = "EastShutterHazard"
	var stripe_mesh := BoxMesh.new()
	stripe_mesh.size = Vector3(0.02, 0.16, 3.2)
	stripe.mesh = stripe_mesh
	stripe.position = Vector3(21.9, -5.48, 0.0)
	var stripe_mat := StandardMaterial3D.new()
	stripe_mat.albedo_color = Color(0.75, 0.42, 0.05, 1.0)
	stripe_mat.roughness = 0.72
	stripe.material_override = stripe_mat
	add_child(stripe)
	var label := Label3D.new()
	label.name = "EastShutterLabel"
	label.text = "ACCESO AL NÚCLEO\nBLOQUEADO"
	label.font_size = 44
	label.pixel_size = 0.004
	label.modulate = Color(1.0, 0.62, 0.18, 1.0)
	label.outline_size = 6
	label.outline_modulate = Color(0.0, 0.0, 0.0, 1.0)
	label.position = Vector3(21.86, -2.55, 0.0)
	label.rotation_degrees.y = -90.0
	add_child(label)

func _disable_general_emission() -> void:
	for node in glb_root.find_children("*", "MeshInstance3D", true, false):
		var mesh_instance := node as MeshInstance3D
		if mesh_instance.mesh == null:
			continue
		var n := mesh_instance.name.to_upper()
		var disable := false
		for token in [
			"CORR_STRIP", "MANTENIMIENTO_STRIP", "ALMACEN_STRIP",
			"CONTROL_ACCESO_STRIP", "SERVICE_CONN_LIGHT_LENS",
			"MAINT_LAMP", "STORE_LAMP", "CORR_WALL_LAMP",
			"ELEV_CAB_LIGHT_PANEL", "ACC_PANEL_LIGHT",
			"COVERALL", "CYLINDER_1",
		]:
			if token in n:
				disable = true
				break
		if not disable:
			continue
		for surface in range(mesh_instance.mesh.get_surface_count()):
			var base := mesh_instance.get_active_material(surface)
			if base is StandardMaterial3D:
				var tuned := (base as StandardMaterial3D).duplicate() as StandardMaterial3D
				tuned.emission_enabled = false
				tuned.emission_energy_multiplier = 0.0
				if "GLASS" in n:
					tuned.albedo_color = Color(0.08, 0.09, 0.10, 0.35)
					tuned.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
				else:
					tuned.albedo_color = Color(0.055, 0.06, 0.065, 1.0)
					tuned.metallic = 0.45
					tuned.roughness = 0.42
				mesh_instance.set_surface_override_material(surface, tuned)
		mesh_instance.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF

func _setup_physics_debris() -> void:
	_add_physics_can(Vector3(-10.5, -5.55, 0.6), "Can_Corridor_W")
	_add_physics_can(Vector3(8.0, -5.55, -0.6), "Can_Corridor_E")
	_add_physics_clipboard(Vector3(4.0, -5.58, 0.4), "Clipboard_Corridor")
	_add_physics_carton(Vector3(2.5, -5.50, 7.8), "Carton_Store_A")
	_add_physics_carton(Vector3(1.0, -5.50, 4.5), "Carton_Store_B")
	_add_physics_can(Vector3(-4.5, -5.55, 7.5), "Can_Store")
	_add_physics_can(Vector3(12.0, -5.55, 6.5), "Can_Maint_A")
	_add_physics_can(Vector3(16.0, -5.55, 4.5), "Can_Maint_B")
	_add_physics_clipboard(Vector3(-6.8, -5.58, -6.2), "Clipboard_Office")
	_add_physics_can(Vector3(4.2, -5.55, -5.4), "Can_Security_A")
	_add_physics_clipboard(Vector3(5.4, -5.58, -4.6), "Clipboard_Security")
	_add_physics_can(Vector3(-16.2, -5.55, 5.2), "Can_Vest_A")
	_add_physics_clipboard(Vector3(-16.8, -5.58, 6.9), "Clipboard_Vest")
	_add_physics_carton(Vector3(-14.6, -5.50, 7.7), "Carton_Vest")
	_add_physics_carton(Vector3(15.2, -5.50, 3.8), "Carton_Maint")
	_add_physics_can(Vector3(13.2, -5.55, 5.3), "Can_Maint_C")
	_add_physics_can(Vector3(14.2, -5.55, -4.8), "Can_Control")
	_add_physics_carton(Vector3(12.2, -5.50, -4.0), "Carton_Control")

func _physics_material(color: Color, metallic: float, roughness: float) -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.albedo_color = color
	mat.metallic = metallic
	mat.roughness = roughness
	return mat

func _tune_rigid_body(body: RigidBody3D) -> void:
	body.linear_damp = 0.38
	body.angular_damp = 0.55
	var pm := PhysicsMaterial.new()
	pm.friction = 0.82
	pm.bounce = 0.06
	pm.rough = true
	body.physics_material_override = pm

func _make_noisy(body: RigidBody3D, radius: float) -> void:
	body.contact_monitor = true
	body.max_contacts_reported = 1
	body.set_meta("noise_spawn_ms", Time.get_ticks_msec())
	body.body_entered.connect(_on_physics_prop_hit.bind(body, radius))

func _on_physics_prop_hit(_other: Node, body: RigidBody3D, radius: float) -> void:
	if body == null or not is_instance_valid(body):
		return
	var now := Time.get_ticks_msec()
	if now - int(body.get_meta("noise_spawn_ms", 0)) < 700:
		return
	if now - int(body.get_meta("last_noise_ms", 0)) < 350:
		return
	body.set_meta("last_noise_ms", now)
	emit_noise(body.global_position, radius, "prop")
	Audio.play_sfx("drop", -14.0, randf_range(0.82, 1.08))

func _add_physics_can(pos: Vector3, node_name: String) -> void:
	var body := RigidBody3D.new()
	body.name = node_name
	body.position = pos
	body.mass = 0.24
	body.continuous_cd = true
	_tune_rigid_body(body)
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
	_make_noisy(body, 3.0)
	add_child(body)

func _add_physics_clipboard(pos: Vector3, node_name: String) -> void:
	var body := RigidBody3D.new()
	body.name = node_name
	body.position = pos
	body.mass = 0.42
	body.continuous_cd = true
	_tune_rigid_body(body)
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
	_make_noisy(body, 1.8)
	add_child(body)

func _add_physics_carton(pos: Vector3, node_name: String) -> void:
	var body := RigidBody3D.new()
	body.name = node_name
	body.position = pos
	body.mass = 1.15
	body.continuous_cd = true
	_tune_rigid_body(body)
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
	_make_noisy(body, 4.0)
	add_child(body)

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

func _replace_counter_monitors() -> void:
	for monitor_name in [
		"NEXUS_ASSET_L1R_REC_MON_A_01",
		"NEXUS_ASSET_L1R_REC_MON_B_01",
		"NEXUS_ASSET_L1R_SEC_DESK_MON_0_01",
		"NEXUS_ASSET_L1R_SEC_DESK_MON_1_01",
		"NEXUS_ASSET_L1R_SEC_DESK_MON_2_01",
		"NEXUS_ASSET_L1R_ACC_MON_A_01",
		"NEXUS_ASSET_L1R_ACC_MON_B_01",
		"NEXUS_ASSET_L1R_CTRL_EAST_MON_02",
		"NEXUS_ASSET_L1R_OFFICE_MONITOR_01",
	]:
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

func _monitor_texture(primary: bool) -> Texture2D:
	var cached: Texture2D = _monitor_screen_a if primary else _monitor_screen_b
	if cached != null:
		return cached
	var path := "res://assets/art/fm/generated/screen_cyan.png" if primary else "res://assets/art/fm/generated/screen_green.png"
	var img := Image.new()
	if img.load(path) != OK:
		return null
	img.generate_mipmaps()
	var tex := ImageTexture.create_from_image(img)
	if primary:
		_monitor_screen_a = tex
	else:
		_monitor_screen_b = tex
	return tex

func _add_flat_monitor(bounds: AABB, suffix_a: bool) -> void:
	var center := bounds.get_center()
	var w := clampf(bounds.size.x, 0.52, 0.66)
	var h := clampf(bounds.size.y * 0.82, 0.32, 0.42)
	var body := MeshInstance3D.new()
	body.name = "Level1FlatMonitor_%s" % ("A" if suffix_a else "B")
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
	var screen_mesh := QuadMesh.new()
	screen_mesh.size = Vector2(w * 0.88, h * 0.76)
	screen.mesh = screen_mesh
	screen.position = center + Vector3(0.0, 0.0, 0.048)
	var screen_mat := StandardMaterial3D.new()
	var screen_tex: Texture2D = _monitor_texture(suffix_a)
	screen_mat.albedo_texture = screen_tex
	screen_mat.albedo_color = Color.WHITE
	screen_mat.emission_enabled = false
	screen_mat.emission_texture = null
	screen_mat.roughness = 0.20
	screen_mat.metallic = 0.0
	screen_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	screen_mat.disable_receive_shadows = true
	screen_mat.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
	screen.material_override = screen_mat
	screen.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
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
	glass.name = "Level1CounterGlass"
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
		post.name = "Level1CounterGlassPost_%d" % i
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
	reader.name = "Level1CardReader"
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
	led.name = "Level1CardReaderLED"
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

func _tune_emergency_signage() -> void:
	# El GLB trae un rótulo SALIDA sobre la puerta del ascensor que se
	# solapaba con el cartel dinámico de esta escena. Se conserva uno solo.
	for node_name in ["NEXUS_V05_C_REC_ELEV_SIGN_TEXT_TEXT", "NEXUS_V05_C_REC_ELEV_SIGN_PLATE"]:
		var duplicate := glb_root.find_child(node_name, true, false) as Node3D
		if duplicate != null:
			duplicate.visible = false
	_set_sign_material("NEXUS_V05_REC_EXTRACT_SIGN_TEXT", Color(1.0, 0.58, 0.12), 2.2)
	if glb_root.find_child("Level1ExitSignLabel", true, false) == null:
		var plate := MeshInstance3D.new()
		plate.name = "Level1ExitSignPlate"
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
		label.name = "Level1ExitSignLabel"
		label.text = "SALIDA"
		label.font_size = 48
		label.pixel_size = 0.0042
		label.modulate = Color(0.18, 1.0, 0.48, 1.0)
		label.outline_size = 6
		label.outline_modulate = Color(0.0, 0.0, 0.0, 1.0)
		label.position = Vector3(-17.5, -2.24, -11.455)
		add_child(label)

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

func _setup_wall_grime() -> void:
	_add_wall_decal(Vector3(-13.2, -3.55, -11.43), Vector3(-90.0, 0.0, 0.0), Vector3(3.0, 1.35, 0.30), "res://assets/art/fm/grunge_decal.png", Color(0.24, 0.21, 0.18, 0.55))
	_add_wall_decal(Vector3(-8.4, -3.10, -1.66), Vector3(90.0, 0.0, 0.0), Vector3(2.6, 1.15, 0.30), "res://assets/art/fm/grime_decal.png", Color(0.20, 0.18, 0.16, 0.50))
	_add_wall_decal(Vector3(-19.91, -3.30, -6.4), Vector3(0.0, 0.0, -90.0), Vector3(2.4, 1.20, 0.30), "res://assets/art/fm/grunge_decal.png", Color(0.22, 0.19, 0.16, 0.48))
	_add_wall_decal(Vector3(-4.07, -3.20, -4.6), Vector3(0.0, 0.0, 90.0), Vector3(2.2, 1.10, 0.30), "res://assets/art/fm/grime_decal.png", Color(0.20, 0.18, 0.16, 0.46))
	_add_wall_decal(Vector3(3.0, -3.25, -10.30), Vector3(-90.0, 0.0, 0.0), Vector3(2.6, 1.20, 0.30), "res://assets/art/fm/grunge_decal.png", Color(0.23, 0.20, 0.17, 0.48))
	_add_wall_decal(Vector3(13.0, -3.25, -10.30), Vector3(-90.0, 0.0, 0.0), Vector3(2.2, 1.05, 0.30), "res://assets/art/fm/grime_decal.png", Color(0.22, 0.19, 0.16, 0.45))
	_add_wall_decal(Vector3(-2.0, -3.20, 10.30), Vector3(90.0, 0.0, 0.0), Vector3(2.8, 1.25, 0.30), "res://assets/art/fm/grunge_decal.png", Color(0.24, 0.20, 0.16, 0.50))
	_add_wall_decal(Vector3(6.18, -3.20, 5.5), Vector3(0.0, 0.0, -90.0), Vector3(2.5, 1.15, 0.30), "res://assets/art/fm/grime_decal.png", Color(0.21, 0.18, 0.15, 0.48))
	_add_wall_decal(Vector3(-9.18, -3.20, 5.5), Vector3(0.0, 0.0, 90.0), Vector3(2.3, 1.10, 0.30), "res://assets/art/fm/grunge_decal.png", Color(0.22, 0.19, 0.16, 0.46))

func _add_wall_decal(pos: Vector3, rot: Vector3, decal_size: Vector3, texture_path: String, tint: Color) -> void:
	var texture := load(texture_path) as Texture2D
	if texture == null:
		return
	var decal := Decal.new()
	decal.name = "Level1WallGrime_%d" % get_child_count()
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

func _setup_wet_patches() -> void:
	var wet := load("res://assets/art/fm/floor_wet.tres") as Material
	if wet == null:
		return
	for spec in [
		["Reception", Vector3(-12.0, -5.638, -4.8), Vector2(4.8, 2.2)],
		["Corridor", Vector3(0.0, -5.638, 0.8), Vector2(2.8, 1.25)],
		["CorridorW", Vector3(-12.0, -5.638, 0.55), Vector2(3.2, 1.0)],
		["CorridorE", Vector3(9.0, -5.638, -0.35), Vector2(2.8, 1.0)],
		["Vest", Vector3(-14.0, -5.638, 5.8), Vector2(2.2, 1.20)],
		["Maint", Vector3(13.0, -5.638, 5.4), Vector2(2.6, 1.40)],
		["Store", Vector3(-2.0, -5.638, 5.9), Vector2(2.4, 1.30)],
	]:
		var patch := MeshInstance3D.new()
		patch.name = "WetPatch_%s" % spec[0]
		var plane := PlaneMesh.new()
		plane.size = spec[2]
		plane.subdivide_width = 2
		plane.subdivide_depth = 2
		patch.mesh = plane
		patch.position = spec[1]
		patch.material_override = wet
		patch.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		add_child(patch)

func _setup_story_decals() -> void:
	var specs := [
		{"tex": "res://assets/art/fm/blood_splat.png", "pos": Vector3(-18.2, -5.18, 0.85), "size": Vector3(1.7, 1.2, 1.5), "alpha": 0.55, "rot": 18.0},
		{"tex": "res://assets/art/fm/puddle.png", "pos": Vector3(-12.4, -5.18, -0.75), "size": Vector3(2.4, 1.2, 1.7), "alpha": 0.45, "rot": -14.0},
		{"tex": "res://assets/art/fm/grunge_decal.png", "pos": Vector3(-7.8, -5.18, 0.95), "size": Vector3(3.0, 1.2, 2.0), "alpha": 0.34, "rot": 62.0},
		{"tex": "res://assets/art/fm/blood_trail.png", "pos": Vector3(-3.6, -5.18, -0.55), "size": Vector3(2.8, 1.2, 1.3), "alpha": 0.50, "rot": 92.0},
		{"tex": "res://assets/art/fm/glass_crack.png", "pos": Vector3(2.2, -5.18, 0.95), "size": Vector3(1.25, 1.2, 1.25), "alpha": 0.48, "rot": 8.0},
		{"tex": "res://assets/art/fm/puddle.png", "pos": Vector3(9.2, -5.18, -0.85), "size": Vector3(2.1, 1.2, 1.55), "alpha": 0.42, "rot": 38.0},
		{"tex": "res://assets/art/fm/grime_decal.png", "pos": Vector3(16.2, -5.18, 0.80), "size": Vector3(2.6, 1.2, 1.8), "alpha": 0.30, "rot": -22.0},
		{"tex": "res://assets/art/fm/blood_splat.png", "pos": Vector3(-13.60, -5.18, -3.90), "size": Vector3(1.9, 1.2, 1.6), "alpha": 0.55, "rot": 34.0},
		{"tex": "res://assets/art/fm/grunge_decal.png", "pos": Vector3(-8.80, -5.18, -4.60), "size": Vector3(2.5, 1.2, 1.8), "alpha": 0.28, "rot": -12.0},
		{"tex": "res://assets/art/fm/blood_trail.png", "pos": Vector3(4.20, -5.18, -5.20), "size": Vector3(2.2, 1.2, 1.1), "alpha": 0.48, "rot": 12.0},
		{"tex": "res://assets/art/fm/grunge_decal.png", "pos": Vector3(0.90, -5.18, -5.70), "size": Vector3(2.2, 1.2, 1.5), "alpha": 0.26, "rot": 50.0},
		{"tex": "res://assets/art/fm/blood_splat.png", "pos": Vector3(12.80, -5.18, -5.90), "size": Vector3(1.5, 1.2, 1.3), "alpha": 0.44, "rot": -25.0},
		{"tex": "res://assets/art/fm/grime_decal.png", "pos": Vector3(10.60, -5.18, -6.50), "size": Vector3(2.0, 1.2, 1.4), "alpha": 0.24, "rot": 70.0},
		{"tex": "res://assets/art/fm/puddle.png", "pos": Vector3(-14.20, -5.18, 5.90), "size": Vector3(2.6, 1.2, 1.7), "alpha": 0.36, "rot": 20.0},
		{"tex": "res://assets/art/fm/blood_splat.png", "pos": Vector3(-16.40, -5.18, 4.20), "size": Vector3(1.4, 1.2, 1.2), "alpha": 0.45, "rot": -40.0},
		{"tex": "res://assets/art/fm/blood_splat.png", "pos": Vector3(-3.20, -5.18, 5.80), "size": Vector3(1.6, 1.2, 1.3), "alpha": 0.46, "rot": 16.0},
		{"tex": "res://assets/art/fm/grunge_decal.png", "pos": Vector3(1.40, -5.18, 6.40), "size": Vector3(2.4, 1.2, 1.7), "alpha": 0.26, "rot": -30.0},
		{"tex": "res://assets/art/fm/puddle.png", "pos": Vector3(2.10, -5.18, 4.10), "size": Vector3(1.7, 1.2, 1.4), "alpha": 0.34, "rot": 45.0},
		{"tex": "res://assets/art/fm/puddle.png", "pos": Vector3(14.10, -5.18, 5.10), "size": Vector3(2.5, 1.2, 1.6), "alpha": 0.36, "rot": -18.0},
		{"tex": "res://assets/art/fm/grunge_decal.png", "pos": Vector3(9.40, -5.18, 5.80), "size": Vector3(2.2, 1.2, 1.5), "alpha": 0.26, "rot": 24.0},
		{"tex": "res://assets/art/fm/blood_splat.png", "pos": Vector3(-6.60, -5.18, -4.90), "size": Vector3(1.0, 1.2, 1.0), "alpha": 0.46, "rot": 68.0},
		{"tex": "res://assets/art/fm/grime_decal.png", "pos": Vector3(-7.40, -5.18, -2.70), "size": Vector3(1.2, 1.2, 1.0), "alpha": 0.24, "rot": -10.0},
	]
	var idx := 0
	for spec in specs:
		var decal := Decal.new()
		decal.name = "StoryDecal_%02d" % idx
		decal.texture_albedo = load(spec["tex"]) as Texture2D
		if decal.texture_albedo == null:
			continue
		decal.position = spec["pos"]
		decal.size = spec["size"]
		decal.rotation_degrees = Vector3(0.0, spec["rot"], 0.0)
		decal.modulate = Color(1.0, 1.0, 1.0, spec["alpha"])
		decal.albedo_mix = 0.82
		decal.normal_fade = 0.35
		decal.upper_fade = 0.25
		decal.lower_fade = 0.25
		decal.distance_fade_enabled = true
		decal.distance_fade_begin = 14.0
		decal.distance_fade_length = 6.0
		add_child(decal)
		idx += 1

func _setup_emergency_lights() -> void:
	# Recepción: única zona con apoyo funcional. Tres luminarias locales.
	_add_emergency_fixture(Vector3(-13.40, -3.00, -1.90), Color(1.0, 0.55, 0.22), 0.85, 5.5, true, Vector3(0.26, 0.09, 0.025), Vector3(0.0, 0.0, 0.045))
	_add_emergency_fixture(Vector3(-19.79, -2.90, -10.60), Color(1.0, 0.20, 0.06), 0.70, 5.0, false, Vector3(0.025, 0.09, 0.26), Vector3(0.045, 0.0, 0.0))
	_add_emergency_fixture(Vector3(-4.18, -2.90, -6.20), Color(1.0, 0.45, 0.16), 0.65, 4.8, false, Vector3(0.025, 0.12, 0.30), Vector3(-0.045, 0.0, 0.0))
	# Corredor: dos luminarias distantes entre sí. El resto queda a oscuras.
	_add_emergency_fixture(Vector3(-5.0, -2.80, -1.62), Color(1.0, 0.32, 0.12), 0.42, 3.8, false, Vector3(0.30, 0.12, 0.025), Vector3(0.0, 0.0, 0.045))
	_add_emergency_fixture(Vector3(5.0, -2.80, -1.62), Color(1.0, 0.32, 0.12), 0.42, 3.8, false, Vector3(0.30, 0.12, 0.025), Vector3(0.0, 0.0, 0.045))
	# Umbral de cada sala: una luz escasa, sin iluminar la habitación completa.
	_add_emergency_fixture(Vector3(3.0, -2.75, -1.80), Color(1.0, 0.40, 0.15), 0.60, 4.4, false, Vector3(0.30, 0.12, 0.025), Vector3(0.0, 0.0, 0.045))
	_add_emergency_fixture(Vector3(13.0, -2.75, -1.80), Color(1.0, 0.28, 0.10), 0.52, 4.0, false, Vector3(0.30, 0.12, 0.025), Vector3(0.0, 0.0, 0.045))
	_add_emergency_fixture(Vector3(-14.0, -2.75, 1.80), Color(1.0, 0.40, 0.15), 0.52, 4.0, false, Vector3(0.30, 0.12, 0.025), Vector3(0.0, 0.0, 0.045))
	_add_emergency_fixture(Vector3(-2.0, -2.75, 1.80), Color(1.0, 0.38, 0.14), 0.58, 4.4, false, Vector3(0.30, 0.12, 0.025), Vector3(0.0, 0.0, 0.045))
	_add_emergency_fixture(Vector3(13.0, -2.75, 1.80), Color(1.0, 0.28, 0.10), 0.52, 4.0, false, Vector3(0.30, 0.12, 0.025), Vector3(0.0, 0.0, 0.045))
	# Conector, oficina, aseo y ascensor: una luz mínima por espacio.
	_add_emergency_fixture(Vector3(5.80, -2.55, 3.10), Color(1.0, 0.42, 0.16), 0.42, 3.4, false, Vector3(0.025, 0.10, 0.26), Vector3(0.045, 0.0, 0.0))
	_add_emergency_fixture(Vector3(-8.22, -2.80, -5.0), Color(1.0, 0.30, 0.10), 0.45, 3.5, false, Vector3(0.025, 0.10, 0.26), Vector3(-0.045, 0.0, 0.0))
	_add_emergency_fixture(Vector3(-8.22, -2.80, -3.0), Color(1.0, 0.30, 0.10), 0.40, 3.2, false, Vector3(0.025, 0.10, 0.24), Vector3(-0.045, 0.0, 0.0))
	_add_emergency_fixture(Vector3(-17.50, -3.02, -12.0), Color(1.0, 0.20, 0.06), 0.22, 2.4, false, Vector3(0.16, 0.02, 0.16), Vector3(0.0, -0.035, 0.0))

func _add_emergency_fixture(pos: Vector3, color: Color, energy: float, light_range: float, cast_shadow: bool, lens_size: Vector3, lens_offset: Vector3) -> void:
	var light := OmniLight3D.new()
	light.name = "EmergencyLight_%d" % _emergency_lights.size()
	light.position = pos
	light.light_color = color
	light.light_energy = energy
	light.omni_range = light_range
	# Sólo una fracción de las luminarias de emergencia proyecta sombra:
	# 29 mapas de sombra simultáneos castigaban la GPU sin aportar lectura.
	light.shadow_enabled = cast_shadow and (_emergency_lights.size() % 5 == 0)
	light.shadow_bias = 0.05
	light.light_volumetric_fog_energy = 0.7
	add_child(light)
	_emergency_lights.append(light)
	_emergency_base_energy.append(energy)
	var dir := lens_offset.normalized() if lens_offset.length() > 0.001 else Vector3(0.0, 0.0, 1.0)
	# Carcasa metálica: evita que la lente emisiva parezca una placa suelta.
	var housing := MeshInstance3D.new()
	housing.name = light.name + "_HOUSING"
	var housing_mesh := BoxMesh.new()
	housing_mesh.size = lens_size + Vector3(0.075, 0.075, 0.030)
	housing.mesh = housing_mesh
	housing.position = pos + lens_offset - dir * 0.028
	housing.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	var housing_mat := StandardMaterial3D.new()
	housing_mat.albedo_color = Color(0.035, 0.040, 0.045, 1.0)
	housing_mat.metallic = 0.62
	housing_mat.roughness = 0.46
	housing.material_override = housing_mat
	add_child(housing)
	# Suspensión hasta el forjado: la luminaria deja de flotar en el aire.
	var stem := MeshInstance3D.new()
	stem.name = light.name + "_STEM"
	var stem_mesh := CylinderMesh.new()
	stem_mesh.top_radius = 0.012
	stem_mesh.bottom_radius = 0.012
	stem_mesh.height = 2.2
	stem.mesh = stem_mesh
	stem.position = housing.position + Vector3(0.0, 1.1, 0.0)
	stem.material_override = housing_mat
	stem.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(stem)
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
	mat.emission_energy_multiplier = 2.4
	lens.material_override = mat
	add_child(lens)

func _setup_wayfinding() -> void:
	var strip_mat := StandardMaterial3D.new()
	strip_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	strip_mat.albedo_color = Color(0.08, 0.42, 0.34, 1.0)
	strip_mat.emission_enabled = true
	strip_mat.emission = Color(0.05, 0.48, 0.36)
	strip_mat.emission_energy_multiplier = 0.85
	for side in [-1.0, 1.0]:
		var strip := MeshInstance3D.new()
		strip.name = "Level1Wayfinding_%s" % ("S" if side < 0.0 else "N")
		var mesh := BoxMesh.new()
		mesh.size = Vector3(43.4, 0.006, 0.035)
		strip.mesh = mesh
		strip.position = Vector3(0.0, -5.632, side * 1.58)
		strip.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		strip.material_override = strip_mat
		add_child(strip)

func _setup_atmosphere_particles() -> void:
	var dust := GPUParticles3D.new()
	dust.name = "Level1Dust"
	dust.amount = 160
	dust.lifetime = 12.0
	dust.preprocess = 5.0
	dust.position = Vector3(0.0, -3.4, 0.0)
	dust.visibility_aabb = AABB(Vector3(-22.0, -2.5, -2.0), Vector3(44.0, 4.0, 4.0))
	var dust_process := ParticleProcessMaterial.new()
	dust_process.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_BOX
	dust_process.emission_box_extents = Vector3(21.0, 1.5, 1.4)
	dust_process.direction = Vector3(0.0, 1.0, 0.0)
	dust_process.spread = 32.0
	dust_process.initial_velocity_min = 0.008
	dust_process.initial_velocity_max = 0.03
	dust_process.gravity = Vector3(0.0, -0.006, 0.0)
	dust_process.scale_min = 0.5
	dust_process.scale_max = 1.4
	dust_process.color = Color(0.65, 0.62, 0.54, 0.18)
	dust.process_material = dust_process
	var dust_quad := QuadMesh.new()
	dust_quad.size = Vector2(0.01, 0.01)
	var dust_mat := StandardMaterial3D.new()
	dust_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	dust_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	dust_mat.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	dust_mat.albedo_color = Color(0.72, 0.68, 0.58, 0.22)
	dust_mat.disable_receive_shadows = true
	dust_quad.material = dust_mat
	dust.draw_pass_1 = dust_quad
	add_child(dust)
	dust.emitting = true

	var steam := GPUParticles3D.new()
	steam.name = "Level1Steam"
	steam.amount = 42
	steam.lifetime = 5.0
	steam.preprocess = 2.0
	steam.position = Vector3(13.0, -2.5, 5.0)
	steam.visibility_aabb = AABB(Vector3(-3.0, -2.0, -3.0), Vector3(6.0, 4.0, 6.0))
	var steam_process := ParticleProcessMaterial.new()
	steam_process.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_BOX
	steam_process.emission_box_extents = Vector3(1.0, 0.25, 1.0)
	steam_process.direction = Vector3(0.0, 1.0, 0.0)
	steam_process.spread = 18.0
	steam_process.initial_velocity_min = 0.05
	steam_process.initial_velocity_max = 0.16
	steam_process.gravity = Vector3(0.0, -0.015, 0.0)
	steam_process.scale_min = 0.7
	steam_process.scale_max = 1.8
	steam_process.color = Color(0.72, 0.82, 0.92, 0.10)
	steam.process_material = steam_process
	var steam_quad := QuadMesh.new()
	steam_quad.size = Vector2(0.55, 0.55)
	var gradient := Gradient.new()
	gradient.set_color(0, Color(1.0, 1.0, 1.0, 0.55))
	gradient.set_color(1, Color(1.0, 1.0, 1.0, 0.0))
	var soft := GradientTexture2D.new()
	soft.gradient = gradient
	soft.width = 64
	soft.height = 64
	soft.fill = GradientTexture2D.FILL_RADIAL
	soft.fill_from = Vector2(0.5, 0.5)
	soft.fill_to = Vector2(1.0, 0.5)
	var steam_mat := StandardMaterial3D.new()
	steam_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	steam_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	steam_mat.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	steam_mat.albedo_texture = soft
	steam_mat.albedo_color = Color(0.72, 0.82, 0.92, 0.16)
	steam_mat.disable_receive_shadows = true
	steam_quad.material = steam_mat
	steam.draw_pass_1 = steam_quad
	add_child(steam)
	steam.emitting = true

func _setup_postprocess() -> void:
	var shader := load("res://assets/shaders/fm_postprocess.gdshader") as Shader
	if shader == null:
		return
	var layer := CanvasLayer.new()
	layer.name = "Level1Postprocess"
	layer.layer = 1
	add_child(layer)
	var rect := ColorRect.new()
	rect.name = "Postprocess"
	rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.add_child(rect)
	rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	var material := ShaderMaterial.new()
	material.shader = shader
	material.set_shader_parameter("vignette_intensity", 0.22)
	material.set_shader_parameter("grain_amount", 0.018)
	material.set_shader_parameter("aberration", 0.00035)
	material.set_shader_parameter("contrast", 1.0)
	material.set_shader_parameter("saturation", 1.04)
	rect.material = material

func _cache_elevator_doors() -> void:
	_elevator_l = glb_root.find_child("NEXUS_V05_C_REC_ELEV_L", true, false) as Node3D
	_elevator_r = glb_root.find_child("NEXUS_V05_C_REC_ELEV_R", true, false) as Node3D
	if _elevator_l != null:
		_elevator_l_closed = _elevator_l.global_position.x
		_elevator_l_body = _ensure_elevator_leaf_collider(_elevator_l)
	if _elevator_r != null:
		_elevator_r_closed = _elevator_r.global_position.x
		_elevator_r_body = _ensure_elevator_leaf_collider(_elevator_r)

func _ensure_elevator_leaf_collider(leaf: Node3D) -> AnimatableBody3D:
	if leaf == null:
		return null
	var mesh := leaf as MeshInstance3D
	if mesh == null or mesh.mesh == null:
		return null
	var bounds := mesh.get_aabb()
	var body := AnimatableBody3D.new()
	body.name = "ElevatorLeafBody"
	body.sync_to_physics = true
	body.collision_layer = 1
	body.collision_mask = 1
	var shape := BoxShape3D.new()
	shape.size = bounds.size
	var collider := CollisionShape3D.new()
	collider.name = "CollisionShape3D"
	collider.shape = shape
	collider.position = bounds.get_center()
	body.add_child(collider)
	add_child(body)
	# El cuerpo debe ser hermano de la hoja, no hijo: un AnimatableBody3D
	# hijo no actualiza su transformación física al mover el padre con un tween.
	body.global_transform = leaf.global_transform
	return body

func animate_elevator_doors(open: bool) -> void:
	if _elevator_l == null and _elevator_r == null:
		return
	if _elevator_tween != null and _elevator_tween.is_valid():
		_elevator_tween.kill()
	_elevator_tween = create_tween().set_parallel(true)
	if _elevator_l != null:
		_elevator_tween.tween_property(_elevator_l, "global_position:x", _elevator_l_closed - (1.0 if open else 0.0), 1.5)
	if _elevator_r != null:
		_elevator_tween.tween_property(_elevator_r, "global_position:x", _elevator_r_closed + (1.0 if open else 0.0), 1.5)
	if _elevator_l_body != null:
		_elevator_tween.tween_property(_elevator_l_body, "global_position:x", _elevator_l_closed - (1.0 if open else 0.0), 1.5)
	if _elevator_r_body != null:
		_elevator_tween.tween_property(_elevator_r_body, "global_position:x", _elevator_r_closed + (1.0 if open else 0.0), 1.5)

func _setup_loot() -> void:
	for source_name in LOOT_SPECS.keys():
		var source := glb_root.find_child(source_name, true, false) as Node3D
		if source == null:
			push_warning("Loot no encontrado: %s" % source_name)
			continue
		if LOOT_TARGETS.has(source_name):
			source.global_position = LOOT_TARGETS[source_name]
			source.force_update_transform()
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
		print("LEVEL1_LOOT ", spec["id"], " at ", item.global_position)

func _setup_hiding_spots() -> void:
	_add_hiding_spot("HideCabinet", "ARMARIO", Vector3(-15.40, -5.65, -2.375))
	_add_hiding_spot("HideLocker", "TAQUILLA", Vector3(-18.20, -5.65, 5.5))
	_add_hiding_spot("HideShelf", "ESTANTERÍA", Vector3(-7.20, -5.65, 5.5))

func _add_hiding_spot(spot_name: String, label: String, pos: Vector3) -> void:
	var spot = HIDING_SCRIPT.new()
	spot.name = spot_name
	spot.display_name = label
	spot.position = pos
	spot.game = self
	var shape := BoxShape3D.new()
	shape.size = Vector3(1.05, 2.05, 1.05)
	var collider := CollisionShape3D.new()
	collider.shape = shape
	spot.add_child(collider)
	var hide_point := Marker3D.new()
	hide_point.name = "HidePoint"
	hide_point.position = Vector3(0.0, 1.05, 0.0)
	spot.add_child(hide_point)
	var exit_point := Marker3D.new()
	exit_point.name = "ExitPoint"
	exit_point.position = Vector3(0.0, 0.0, -1.2)
	spot.add_child(exit_point)
	add_child(spot)

func _setup_noise_traps() -> void:
	_add_noise_trap("NoiseTrap_Corridor", Vector3(-2.0, -5.65, 0.7))
	_add_noise_trap("NoiseTrap_Warehouse", Vector3(-2.0, -5.65, 6.2))

func _add_noise_trap(trap_name: String, pos: Vector3) -> void:
	var trap = NOISE_TRAP_SCRIPT.new()
	trap.name = trap_name
	trap.position = pos
	trap.game = self
	add_child(trap)

func _setup_extraction() -> void:
	extraction = EXTRACTION_SCRIPT.new()
	extraction.name = "ReceptionExtraction"
	extraction.position = Vector3(-12.0, -4.4, -6.7)
	extraction.game = self
	extraction.delivery_center = EXTRACTION_CENTER
	extraction.extraction_started.connect(_on_extraction_started)
	extraction.extraction_progress.connect(_on_extraction_progress)
	extraction.extraction_completed.connect(_on_extraction_completed)
	add_child(extraction)

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
	var surface_audio = SURFACE_AUDIO_SCRIPT.new()
	add_child(surface_audio)
	surface_audio.setup(player, self)
	player.footstep_surface_provider = surface_audio

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

func _setup_watcher() -> void:
	watcher = WATCHER_SCENE.instantiate()
	watcher.name = "Watcher"
	watcher.position = Vector3(14.0, -5.65, 0.0)
	add_child(watcher)
	watcher.set_game(self)
	watcher.set_player(player)
	var patrol_points: Array[Vector3] = [
		Vector3(14.0, -5.65, 0.0),
		Vector3(4.0, -5.65, 0.0),
		Vector3(-6.0, -5.65, 0.0),
		Vector3(-16.0, -5.65, 0.0),
		Vector3(-6.0, -5.65, 0.0),
		Vector3(4.0, -5.65, 0.0),
	]
	watcher.set_patrol_points(patrol_points)

func _setup_hud() -> void:
	hud = HUD_SCRIPT.new()
	hud.name = "HUD"
	add_child(hud)
	hud.set_objective("RECUPERAR BOTÍN", "Nivel 1 · Instalación NEXUS")
	hud.set_status("EXPLORÁ LA INSTALACIÓN Y VOLVÉ A RECEPCIÓN")
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
	ambience.name = "Level1Ambience"
	ambience.stream = looped
	ambience.position = Vector3(-2.0, -3.0, 0.0)
	ambience.unit_size = 10.0
	ambience.max_distance = 60.0
	ambience.volume_db = -16.0
	add_child(ambience)
	ambience.play()
	for spec in [
		["Reception", Vector3(-12.0, -3.0, -6.7), 0.94, -20.0],
		["Security", Vector3(3.0, -3.0, -6.0), 1.04, -22.0],
		["Control", Vector3(13.0, -3.0, -6.0), 0.88, -22.0],
		["Vest", Vector3(-14.0, -3.0, 6.0), 1.08, -23.0],
		["Store", Vector3(-2.0, -3.0, 6.0), 0.82, -22.0],
		["Maint", Vector3(13.0, -3.0, 6.0), 0.76, -22.0],
	]:
		var room := AudioStreamPlayer3D.new()
		room.name = "Ambience_%s" % spec[0]
		room.stream = looped
		room.position = spec[1]
		room.pitch_scale = spec[2]
		room.volume_db = spec[3]
		room.unit_size = 6.0
		room.max_distance = 22.0
		room.attenuation_model = AudioStreamPlayer3D.ATTENUATION_INVERSE_DISTANCE
		add_child(room)
		room.play()

func _process(delta: float) -> void:
	if state != State.PLAYING:
		return
	var f9 := Input.is_key_pressed(KEY_F9)
	if f9 and not _alert_debug_down:
		set_red_alert(not _red_alert)
		notify("ALERTA ROJA ACTIVA · PUERTAS BLOQUEADAS" if _red_alert else "ALERTA ROJA DESACTIVADA")
	_alert_debug_down = f9
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
	if hud == null or player == null:
		return
	hud.set_battery(float(player.battery), bool(player.flashlight_on))
	hud.set_stamina(float(player.get("stamina")) if player.get("stamina") != null else 0.0)
	var stress_value = player.get("stress")
	hud.set_stress(float(stress_value) if stress_value != null else 0.0)
	hud.set_hidden(bool(player.hidden))
	hud.set_prompt(player.get_interaction_prompt())
	hud.set_watcher_observed(bool(watcher != null and watcher.observed))
	if _status_timer > 0.0:
		hud.set_status(_status_override)
	elif extraction != null and extraction.has_player():
		var delivered := get_delivered_loot_count(EXTRACTION_CENTER, extraction.delivery_radius_m)
		if delivered > 0:
			hud.set_status("EXTRACCIÓN LISTA · PERMANECÉ EN RECEPCIÓN")
		else:
			hud.set_status("LLEVÁ UN OBJETO AL ASCENSOR DE EXTRACCIÓN")
	else:
		hud.set_status("EXPLORÁ LA INSTALACIÓN Y VOLVÉ A RECEPCIÓN")

func notify(text: String) -> void:
	_status_override = text
	_status_timer = 2.5
	if hud != null:
		hud.set_status(text)

func emit_noise(position: Vector3, radius: float, kind: String) -> void:
	if watcher != null and is_instance_valid(watcher):
		watcher.hear_noise(position, radius)

func get_active_player_count() -> int:
	return 1 if player != null and is_instance_valid(player) else 0

func all_alive_players_inside(area: Area3D) -> bool:
	return area != null and area.players_inside.has(player)

func any_alive_player_inside(area: Area3D) -> bool:
	return area != null and area.players_inside.has(player)

func get_delivered_loot_count(center: Vector3, radius: float) -> int:
	# El procedimiento de extracción admite tanto el botín depositado en el
	# radio del ascensor como el que un jugador presente lleva en las manos.
	var delivered := {}
	for item in loot_items:
		if item != null and is_instance_valid(item) and item.global_position.distance_to(center) <= radius:
			delivered[item.get_instance_id()] = true
	if player != null and is_instance_valid(player):
		var carried = player.carried_item
		if carried != null and is_instance_valid(carried) and loot_items.has(carried):
			if extraction != null and extraction.players_inside.has(player):
				delivered[carried.get_instance_id()] = true
	return delivered.size()

func get_total_loot_value() -> int:
	var total := 0
	for item in loot_items:
		if item != null and is_instance_valid(item):
			total += int(item.loot_value)
	return total

func on_artifact_picked(who: Node) -> void:
	if who == player and who.carried_item != null:
		notify("OBJETO RECOGIDO · %s" % who.carried_item.item_name)
		if hud != null:
			hud.set_objective("BOTÍN EN MANOS", "Llevalo al ascensor de recepción")

func on_artifact_dropped() -> void:
	notify("OBJETO SOLTADO")

func on_player_hidden(is_hidden: bool) -> void:
	if hud != null:
		hud.set_hidden(is_hidden)
	notify("ESCONDIDO" if is_hidden else "SALISTE DEL ESCONDITE")

func on_player_caught(_who = null) -> void:
	if state != State.PLAYING:
		return
	_end(State.LOST, "DETECTADO", "El Vigilante te encontró")

func on_extraction_started() -> void:
	animate_elevator_doors(true)
	Audio.play_sfx("deliver", -10.0, 0.9)
	notify("EXTRACCIÓN INICIADA · PERMANECÉ EN RECEPCIÓN")

func on_extraction_cancelled() -> void:
	if state == State.PLAYING:
		animate_elevator_doors(false)
		notify("EXTRACCIÓN CANCELADA")

func on_extraction_progress(stage: String, seconds_left: float) -> void:
	if state != State.PLAYING:
		return
	match stage:
		"activando":
			notify("EXTRACCIÓN EN %0.1f s" % seconds_left)
		"apertura":
			notify("ABRIENDO ASCENSOR")
		"espera":
			notify("PERMANECÉ EN RECEPCIÓN · %0.1f s" % seconds_left)
		"cierre":
			animate_elevator_doors(false)
			notify("CERRANDO SECUENCIA")
		"viaje":
			notify("VIAJE DE EXTRACCIÓN")
		"llegada":
			notify("LLEGADA · CONFIRMANDO")

func _on_extraction_started() -> void:
	on_extraction_started()

func _on_extraction_cancelled() -> void:
	on_extraction_cancelled()

func _on_extraction_progress(stage: String, seconds_left: float) -> void:
	on_extraction_progress(stage, seconds_left)

func _on_extraction_completed(delivered: int) -> void:
	if state != State.PLAYING:
		return
	_end(State.WON, "EXTRACCIÓN COMPLETADA", "BOTÍN RECUPERADO: %d" % delivered)

func _end(result: State, title: String, subtitle: String) -> void:
	state = result
	if player != null:
		player.set_physics_process(false)
		player.set_process_input(false)
	if result == State.WON:
		Audio.play_sfx("win", -4.0)
	else:
		Audio.play_sfx("lose", -4.0)
	if hud != null:
		hud.show_end(title, subtitle)
	print("LEVEL1_END ", result, " ", title, " ", subtitle)

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

func _global_aabb(node: Node3D) -> AABB:
	var result := AABB()
	var first := true
	if node is MeshInstance3D:
		var mesh := node as MeshInstance3D
		if mesh.mesh != null:
			result = mesh.global_transform * mesh.get_aabb()
			first = false
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
