extends Node3D

const MAT_CONCRETE := preload("res://assets/art/fm/concrete_wall.tres")
const MAT_METAL := preload("res://assets/art/fm/metal_panel.tres")
const MAT_FLOOR := preload("res://assets/art/fm/floor_wet.tres")
const MAT_RUST := preload("res://assets/art/fm/rust.tres")
const MAT_HAZARD := preload("res://assets/art/fm/hazard.tres")
const MAT_CYAN := preload("res://assets/art/fm/emissive_cyan.tres")
const MAT_RED := preload("res://assets/art/fm/emissive_red.tres")
const MAT_ORANGE := preload("res://assets/art/fm/emissive_orange.tres")
const MAT_GREEN := preload("res://assets/art/fm/emissive_green.tres")
const MAT_RUBBER := preload("res://assets/art/fm/rubber.tres")
const MAT_DARK := preload("res://assets/art/fm/dark_metal.tres")
const MAT_YELLOW := preload("res://assets/art/fm/warning_yellow.tres")
const MAT_GLASS := preload("res://assets/art/fm/glass.tres")
const MAT_GOO := preload("res://assets/art/fm/goo.tres")
const MAT_SCREEN := preload("res://assets/art/fm/screen.tres")

const CORRIDOR_MIN_X := -2.7
const CORRIDOR_MAX_X := 2.7
const CORRIDOR_MIN_Z := -10.0
const CORRIDOR_MAX_Z := 12.0
const ROOM_HEIGHT := 3.8

var _mats: Dictionary = {}
var _views: Array[Camera3D] = []
var _vignette: ColorRect
var _overlay: CanvasLayer

func _ready() -> void:
	_prepare_materials()
	_build_environment()
	_build_room()
	_build_lab()
	_build_props()
	_build_lights()
	_build_atmosphere()
	_build_reflection_probe()
	_build_cameras()
	_build_overlay()
	set_view(0)
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--view="):
			set_view(int(arg.get_slice("=", 1)))

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("pause"):
		get_viewport().set_input_as_handled()
		get_tree().change_scene_to_file("res://scenes/menu.tscn")

func _prepare_materials() -> void:
	var concrete: StandardMaterial3D = MAT_CONCRETE.duplicate()
	concrete.uv1_scale = Vector3(4.0, 4.0, 1.0)
	concrete.albedo_color = Color(1.08, 1.12, 1.08, 1.0)
	_mats["concrete"] = concrete
	var metal: StandardMaterial3D = MAT_METAL.duplicate()
	metal.uv1_scale = Vector3(5.0, 5.0, 1.0)
	metal.albedo_color = Color(0.72, 0.82, 0.88, 1.0)
	_mats["metal"] = metal
	var ceiling: StandardMaterial3D = concrete.duplicate()
	ceiling.uv1_scale = Vector3(3.0, 2.0, 1.0)
	ceiling.albedo_color = Color(0.86, 0.92, 0.90, 1.0)
	ceiling.roughness = 0.94
	_mats["ceiling"] = ceiling
	_mats["rust"] = MAT_RUST
	_mats["hazard"] = MAT_HAZARD
	_mats["cyan"] = MAT_CYAN
	var cyan_dim: StandardMaterial3D = MAT_CYAN.duplicate()
	cyan_dim.emission_energy_multiplier = 0.8
	_mats["cyan_dim"] = cyan_dim
	var cyan_faint: StandardMaterial3D = MAT_CYAN.duplicate()
	cyan_faint.emission_energy_multiplier = 0.4
	_mats["cyan_faint"] = cyan_faint
	_mats["red"] = MAT_RED
	var red_dim: StandardMaterial3D = MAT_RED.duplicate()
	red_dim.emission_energy_multiplier = 0.4
	_mats["red_dim"] = red_dim
	_mats["orange"] = MAT_ORANGE
	_mats["green"] = MAT_GREEN
	_mats["rubber"] = MAT_RUBBER
	_mats["dark"] = MAT_DARK
	_mats["yellow"] = MAT_YELLOW
	_mats["glass"] = MAT_GLASS.duplicate()
	_mats["glass"].cull_mode = BaseMaterial3D.CULL_DISABLED
	var goo: StandardMaterial3D = MAT_GOO.duplicate()
	goo.transparency = BaseMaterial3D.TRANSPARENCY_DISABLED
	goo.albedo_color = Color(0.03, 0.46, 0.15, 1.0)
	goo.emission_energy_multiplier = 0.9
	goo.roughness = 0.34
	_mats["goo"] = goo
	_mats["screen"] = MAT_SCREEN.duplicate()
	_mats["screen"].cull_mode = BaseMaterial3D.CULL_DISABLED
	_mats["screen"].emission_energy_multiplier = 4.0
	var floor_mat: StandardMaterial3D = MAT_FLOOR.duplicate()
	floor_mat.uv1_scale = Vector3(3.5, 7.0, 1.0)
	floor_mat.albedo_color = Color(1.55, 1.55, 1.5, 1.0)
	_mats["floor"] = floor_mat
	var floor_lab: StandardMaterial3D = MAT_FLOOR.duplicate()
	floor_lab.uv1_scale = Vector3(5.0, 4.0, 1.0)
	floor_lab.albedo_color = Color(1.45, 1.45, 1.4, 1.0)
	_mats["floor_lab"] = floor_lab
	var metal_dirty: StandardMaterial3D = MAT_METAL.duplicate()
	metal_dirty.albedo_color = Color(0.70, 0.80, 0.86, 1.0)
	metal_dirty.roughness = 0.54
	metal_dirty.metallic = 0.38
	_mats["metal_dirty"] = metal_dirty
	var grunge := StandardMaterial3D.new()
	grunge.albedo_texture = load("res://assets/art/fm/grunge_decal.png")
	grunge.albedo_color = Color(0.55, 0.48, 0.38, 0.42)
	grunge.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	grunge.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	grunge.cull_mode = BaseMaterial3D.CULL_DISABLED
	_mats["grunge"] = grunge

func _mat(key: String) -> Material:
	return _mats[key]

func _build_environment() -> void:
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.002, 0.004, 0.006)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.16, 0.22, 0.25)
	env.ambient_light_energy = 0.58
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.tonemap_exposure = 1.18
	env.tonemap_white = 1.0
	env.glow_enabled = true
	env.glow_intensity = 0.82
	env.glow_strength = 1.0
	env.glow_bloom = 0.12
	env.glow_hdr_threshold = 0.9
	env.fog_enabled = true
	env.fog_light_color = Color(0.06, 0.14, 0.15)
	env.fog_light_energy = 0.75
	env.fog_density = 0.0065
	env.fog_aerial_perspective = 0.25
	env.fog_sky_affect = 0.0
	env.volumetric_fog_enabled = true
	env.volumetric_fog_density = 0.011
	env.volumetric_fog_albedo = Color(0.42, 0.52, 0.52)
	env.volumetric_fog_emission = Color(0.0, 0.0, 0.0)
	env.volumetric_fog_emission_energy = 0.0
	env.volumetric_fog_anisotropy = 0.35
	env.volumetric_fog_length = 64.0
	env.volumetric_fog_detail_spread = 2.0
	env.volumetric_fog_ambient_inject = 0.28
	env.volumetric_fog_sky_affect = 0.0
	env.volumetric_fog_temporal_reprojection_enabled = true
	env.volumetric_fog_temporal_reprojection_amount = 0.9
	env.ssao_enabled = true
	env.ssao_radius = 1.1
	env.ssao_intensity = 1.6
	env.ssao_power = 1.4
	env.ssao_detail = 0.6
	env.ssao_horizon = 0.08
	env.ssao_sharpness = 0.9
	env.ssao_light_affect = 0.2
	env.ssil_enabled = false
	env.ssr_enabled = true
	env.ssr_max_steps = 32
	env.ssr_fade_in = 0.1
	env.ssr_fade_out = 2.0
	env.ssr_depth_tolerance = 0.2
	env.adjustment_enabled = true
	env.adjustment_brightness = 1.08
	env.adjustment_contrast = 1.06
	env.adjustment_saturation = 1.03
	var world := WorldEnvironment.new()
	world.environment = env
	add_child(world)

func _build_room() -> void:
	_plane(Vector3(0, 0, 1.0), Vector2(5.4, 22.0), "floor")
	# Baseboards and floor edges.
	for x in [-2.62, 2.62]:
		_box(Vector3(x, 0.12, 1.0), Vector3(0.12, 0.24, 22.0), "dark")
	# Right wall.
	var z := -8.9
	while z < 11.0:
		_wall_panel(Vector3(2.7, 0, z), 2.1, 0.0)
		z += 2.2
	# Left wall, with the laboratory opening between z=2 and z=6.
	for z2 in [-8.9, -6.7, -4.5, -2.3, -0.1]:
		_wall_panel(Vector3(-2.7, 0, z2), 2.1, 0.0)
	for z2 in [7.1, 9.3, 11.5]:
		_wall_panel(Vector3(-2.7, 0, z2), 2.1, 0.0)
	# Far wall and door opening.
	_wall_panel(Vector3(-2.0, 0, -10.0), 1.35, 90.0)
	_wall_panel(Vector3(2.0, 0, -10.0), 1.35, 90.0)
	_box(Vector3(0, 3.35, -10.0), Vector3(3.0, 0.9, 0.22), "concrete")
	# Ceiling.
	z = -8.9
	while z < 11.0:
		_box(Vector3(0, 3.82, z), Vector3(5.4, 0.12, 2.1), "ceiling")
		_box(Vector3(0, 3.68, z + 1.1), Vector3(5.4, 0.18, 0.16), "metal_dirty")
		z += 2.2
	# Laboratory entrance frame and threshold.
	_box(Vector3(-2.7, 1.9, 1.95), Vector3(0.3, 3.8, 0.24), "dark")
	_box(Vector3(-2.7, 1.9, 6.05), Vector3(0.3, 3.8, 0.24), "dark")
	_box(Vector3(-2.7, 3.58, 4.0), Vector3(0.3, 0.24, 4.1), "dark")
	_plane(Vector3(-2.55, 0.014, 4.0), Vector2(0.35, 3.8), "hazard")
	_build_door()
	_build_pipes()
	_build_corridor_details()

func _wall_panel(base: Vector3, length: float, side_rotation: float) -> void:
	var thickness := 0.22
	var size := Vector3(thickness, 1.2, length)
	var lower := _box(base + Vector3(0, 0.6, 0), size, "concrete")
	lower.rotation_degrees.y = side_rotation
	var upper_size := Vector3(thickness, 2.6, length)
	var upper := _box(base + Vector3(0, 2.5, 0), upper_size, "metal")
	upper.rotation_degrees.y = side_rotation
	var trim_size := Vector3(thickness + 0.06, 0.08, length)
	var trim := _box(base + Vector3(0, 1.2, 0), trim_size, "dark")
	trim.rotation_degrees.y = side_rotation
	# panel seams
	var seam_size := Vector3(thickness + 0.03, 2.6, 0.035)
	for edge in [-1.0, 1.0]:
		var offset := Vector3(0, 0, edge * length * 0.5)
		if abs(side_rotation) > 1.0:
			offset = Vector3(edge * length * 0.5, 0, 0)
		var seam := _box(base + Vector3(0, 2.5, 0) + offset, seam_size, "dark")
		seam.rotation_degrees.y = side_rotation

func _build_door() -> void:
	var z := -9.78
	_box(Vector3(-1.58, 1.7, z), Vector3(0.34, 3.4, 0.38), "dark")
	_box(Vector3(1.58, 1.7, z), Vector3(0.34, 3.4, 0.38), "dark")
	_box(Vector3(0, 3.32, z), Vector3(3.5, 0.34, 0.38), "dark")
	for x in [-0.66, 0.66]:
		_box(Vector3(x, 1.35, z - 0.02), Vector3(1.28, 2.62, 0.12), "metal_dirty")
		# vertical ribs
		for off in [-0.48, 0.0, 0.48]:
			_box(Vector3(x + off, 1.35, z + 0.07), Vector3(0.035, 2.42, 0.035), "dark")
		_box(Vector3(x, 0.16, z + 0.07), Vector3(1.18, 0.16, 0.03), "hazard")
	# Center seam and warning lights.
	_box(Vector3(0, 1.35, z + 0.09), Vector3(0.035, 2.55, 0.04), "dark")
	_box(Vector3(0, 3.14, z + 0.1), Vector3(2.45, 0.18, 0.16), "dark")
	_box(Vector3(0, 3.14, z + 0.2), Vector3(2.2, 0.06, 0.08), "red_dim")
	_box(Vector3(0, 2.95, z + 0.24), Vector3(2.0, 0.045, 0.06), "cyan_dim")
	# Keypad.
	_box(Vector3(1.82, 1.45, z + 0.28), Vector3(0.24, 0.36, 0.08), "dark")
	_quad(Vector3(1.82, 1.47, z + 0.325), Vector2(0.15, 0.15), "screen")
	_box(Vector3(1.82, 1.32, z + 0.34), Vector3(0.05, 0.05, 0.025), "green")
	# Door sign.
	_label("SECTOR 04", Vector3(0, 3.52, z + 0.24), 28, Color(1.0, 0.55, 0.14), Vector3.ZERO)
	_label("NEXUS // CONTENCIÓN", Vector3(0, 3.30, z + 0.245), 12, Color(0.65, 0.85, 0.82), Vector3.ZERO)
	# Hazard floor strip in front of the door.
	_plane(Vector3(0, 0.011, -8.85), Vector2(2.9, 0.9), "rubber")
	_plane(Vector3(0, 0.013, -8.85), Vector2(2.7, 0.7), "hazard")
	_plane(Vector3(0, 0.014, -8.25), Vector2(2.7, 0.06), "yellow")
	# Warning light and a cool front light so the door is readable.
	_omni(Vector3(0, 2.85, -9.2), Color(1.0, 0.08, 0.04), 0.55, 5.0, 0.8)
	_spot(Vector3(0.0, 3.28, -7.7), Vector3(0.0, 1.1, -9.8), Color(0.68, 0.82, 0.9), 1.5, 50.0, 9.0, true)
	_spot(Vector3(0.0, 2.30, -7.2), Vector3(0.0, 1.7, -9.75), Color(0.55, 0.72, 0.82), 1.2, 60.0, 6.0, false)
	_omni(Vector3(0.0, 2.4, -6.5), Color(0.25, 0.45, 0.52), 1.4, 7.0, 0.6)
	# Door frame vertical red strip.
	_box(Vector3(-1.52, 2.35, z + 0.16), Vector3(0.05, 0.8, 0.05), "red_dim")
	_box(Vector3(1.52, 2.35, z + 0.16), Vector3(0.05, 0.8, 0.05), "red_dim")

func _build_pipes() -> void:
	for x in [-2.16, 2.16]:
		_cylinder(Vector3(x, 3.27, 1.0), 0.105, 21.6, "rust", Vector3(90, 0, 0))
		var z := -9.0
		while z < 12.0:
			_cylinder(Vector3(x, 3.27, z), 0.16, 0.09, "dark", Vector3(90, 0, 0))
			z += 3.0
	# Heavy red pipe on the right wall.
	_cylinder(Vector3(2.46, 2.7, 1.0), 0.15, 21.0, "rust", Vector3(90, 0, 0))
	for z in [-7.5, -3.5, 0.5, 4.5, 8.5]:
		_cylinder(Vector3(2.46, 2.7, z), 0.21, 0.1, "dark", Vector3(90, 0, 0))
	# Vertical service pipe and valve.
	_cylinder(Vector3(-2.4, 1.75, -4.4), 0.085, 3.5, "rust")
	_torus(Vector3(-2.4, 1.1, -4.4), 0.18, 0.27, "rust", Vector3(90, 0, 0))
	# Conduits and cables.
	for i in 3:
		var y := 3.42 - i * 0.045
		_cylinder(Vector3(-2.35, y, 1.0), 0.025, 21.0, "rubber", Vector3(90, 0, 0))
	for i in 2:
		_cylinder(Vector3(2.36, 3.38 - i * 0.05, 1.0), 0.022, 21.0, "rubber", Vector3(90, 0, 0))
	# Ceiling junction boxes.
	for z in [-6.5, 1.5, 8.0]:
		_box(Vector3(-2.36, 3.48, z), Vector3(0.22, 0.22, 0.32), "dark")
		_box(Vector3(-2.36, 3.36, z), Vector3(0.12, 0.04, 0.12), "cyan")

func _build_corridor_details() -> void:
	# Wall vents.
	_vent(Vector3(2.58, 2.35, -3.7), Vector3(0.04, 0.86, 1.0), -90.0)
	_vent(Vector3(2.58, 2.35, 6.5), Vector3(0.04, 0.86, 1.0), -90.0)
	_vent(Vector3(-2.58, 2.1, 9.2), Vector3(0.04, 0.7, 0.85), 90.0)
	# Signs.
	_label("NEXUS", Vector3(2.57, 2.95, 7.7), 54, Color(0.25, 0.95, 0.9), Vector3(0, -90, 0), 10)
	_label("RECOVERY DIVISION", Vector3(2.57, 2.72, 7.7), 18, Color(0.7, 0.33, 0.12), Vector3(0, -90, 0), 8)
	_label("MANTENIMIENTO", Vector3(2.57, 2.15, -2.0), 22, Color(1.0, 0.62, 0.18), Vector3(0, -90, 0), 8)
	_label("RIESGO BIOLÓGICO", Vector3(-2.57, 2.25, 4.1), 22, Color(1.0, 0.62, 0.18), Vector3(0, 90, 0), 8)
	# Floor grates.
	_grate(Vector3(1.9, 0.008, 8.2), Vector2(0.9, 1.7))
	_grate(Vector3(-1.9, 0.008, -1.4), Vector2(0.8, 1.4))
	# Grime decals.
	_decal(Vector3(0.0, 0.011, 2.0), Vector2(4.0, 3.0), -90.0, 0.4)
	_decal(Vector3(-5.9, 0.012, 4.4), Vector2(3.6, 2.4), -90.0, 0.55)
	_decal(Vector3(2.55, 1.1, 4.2), Vector2(2.2, 1.6), -90.0, 1.4)
	# Loose conduit and small service box.

func _build_lab() -> void:
	_plane(Vector3(-7.35, 0.003, 2.4), Vector2(9.3, 8.4), "floor_lab")
	# Lab shell.
	_wall_panel(Vector3(-12.0, 0, 2.4), 8.4, 0.0)
	_wall_panel(Vector3(-7.35, 0, -1.8), 9.3, 90.0)
	_wall_panel(Vector3(-7.35, 0, 6.6), 9.3, 90.0)
	_box(Vector3(-7.35, 3.82, 2.4), Vector3(9.3, 0.12, 8.4), "ceiling")
	for x in [-10.0, -7.35, -4.7]:
		_box(Vector3(x, 3.68, 2.4), Vector3(0.16, 0.2, 8.4), "metal_dirty")
	# Lab entry threshold and warning line.
	_plane(Vector3(-2.55, 0.014, 4.0), Vector2(0.35, 3.8), "hazard")
	# Containment tank.
	_cylinder(Vector3(-8.25, 0.16, 2.2), 1.28, 0.32, "dark")
	_cylinder(Vector3(-8.25, 1.65, 2.2), 1.12, 2.7, "glass")
	_cylinder(Vector3(-8.25, 1.45, 2.2), 0.89, 2.2, "goo")
	_torus(Vector3(-8.25, 0.42, 2.2), 1.1, 1.25, "dark")
	_torus(Vector3(-8.25, 2.82, 2.2), 1.1, 1.27, "rust")
	_torus(Vector3(-8.25, 3.0, 2.2), 1.0, 1.12, "cyan_dim")
	for i in 6:
		var a := TAU * float(i) / 6.0
		var x := -8.25 + cos(a) * 1.05
		var z := 2.2 + sin(a) * 1.05
		_box(Vector3(x, 1.6, z), Vector3(0.08, 2.7, 0.08), "dark")
	# Silhouette inside the tank.
	var body := _sphere(Vector3(-8.25, 1.35, 3.02), 0.5, "dark")
	body.scale = Vector3(0.75, 1.65, 0.55)
	body.rotation_degrees.z = -12.0
	var core := _sphere(Vector3(-8.25, 1.45, 3.10), 0.26, "green")
	core.scale = Vector3(0.7, 1.3, 0.55)
	var head := _sphere(Vector3(-8.25, 2.28, 3.04), 0.27, "dark")
	head.scale = Vector3(0.9, 1.05, 0.72)
	var shoulders := _sphere(Vector3(-8.25, 1.88, 3.02), 0.40, "dark")
	shoulders.scale = Vector3(1.0, 0.55, 0.62)
	for side in [-1.0, 1.0]:
		var arm := _sphere(Vector3(-8.25 + side * 0.37, 1.58, 3.04), 0.18, "dark")
		arm.scale = Vector3(0.55, 1.7, 0.55)
		arm.rotation_degrees.z = side * 8.0
	# Tank pipes.
	_cylinder(Vector3(-8.25, 3.0, 2.2), 0.12, 0.8, "rust")
	_cylinder(Vector3(-8.25, 3.45, 2.2), 0.12, 3.5, "rust")
	_cylinder(Vector3(-8.25, 3.4, 2.2), 0.08, 5.0, "rubber", Vector3(90, 0, 0))
	# Tank glow.
	_omni(Vector3(-8.25, 1.3, 2.2), Color(0.18, 1.0, 0.36), 2.1, 6.0, 1.4)
	# Gurney and covered shape.
	_gurney(Vector3(-10.0, 0, 5.0))
	# Desk and monitor.
	_desk(Vector3(-10.8, 0, 5.65), Vector3(-11.8, 1.4, 5.75))
	# Cabinet wall.
	_cabinet(Vector3(-11.55, 0, -1.2))
	_cabinet(Vector3(-11.55, 0, 0.15))
	# Lab screens.
	_screen(Vector3(-11.85, 2.4, 4.6), Vector2(1.9, 1.0), "BIO-LAB 04", 90.0)
	_screen(Vector3(-11.85, 1.55, 4.6), Vector2(1.2, 0.5), "MONITOREO", 90.0)
	# Lab crates and clutter.
	for i in 3:
		_crate(Vector3(-10.9 + i * 0.55, 0.32, 0.9 + i * 0.02), 0.62)
	_barrel(Vector3(-10.9, 0.52, -0.5))
	# Lab sign.
	_label("BIO-LAB 04", Vector3(-11.85, 3.05, 3.6), 24, Color(0.3, 1.0, 0.9), Vector3(0, 90, 0), 8)
	# A hiding locker in the lab.
	_locker(Vector3(-11.45, 1.1, 1.45), 90.0)
	# Ceiling ring fixture.
	_torus(Vector3(-8.25, 3.3, 2.2), 1.22, 1.38, "cyan_faint")
	_omni(Vector3(-8.25, 3.2, 2.2), Color(0.32, 0.9, 1.0), 1.1, 6.0, 0.7)
	_spot(Vector3(-8.25, 3.42, 2.2), Vector3(-8.25, 0.2, 2.2), Color(0.35, 0.82, 1.0), 2.1, 52.0, 7.0, true)
	# Front fill on the tank glass and the room.
	_spot(Vector3(-4.8, 2.35, 3.7), Vector3(-8.25, 1.45, 2.2), Color(0.65, 0.85, 1.0), 2.3, 48.0, 9.0, true)
	_omni(Vector3(-7.3, 3.15, 2.4), Color(0.35, 0.55, 0.62), 1.8, 9.0, 0.8)
	_omni(Vector3(-10.3, 2.2, 4.6), Color(0.3, 0.5, 0.58), 1.5, 7.0, 0.6)
	_omni(Vector3(-4.1, 2.15, 4.9), Color(0.3, 0.55, 0.62), 2.0, 7.5, 0.5)
	_omni(Vector3(-11.0, 2.1, 0.6), Color(0.36, 0.55, 0.62), 1.2, 6.0, 0.4)
	# Gurney light.
	_spot(Vector3(-10.0, 3.55, 5.0), Vector3(-10.0, 0.7, 5.0), Color(0.7, 0.86, 1.0), 3.2, 48.0, 5.5, true)
	_spot(Vector3(-10.8, 3.4, 5.65), Vector3(-10.8, 0.8, 5.65), Color(1.0, 0.76, 0.5), 2.4, 46.0, 5.0, false)
	# Screen glow.
	_omni(Vector3(-11.55, 2.1, 4.6), Color(0.2, 0.65, 0.72), 0.9, 3.2, 0.5)
	# Lab red emergency.
	_omni(Vector3(-11.7, 2.5, -1.3), Color(1.0, 0.06, 0.03), 1.2, 5.0, 1.2)
	_box(Vector3(-11.7, 2.75, -1.3), Vector3(0.8, 0.08, 0.08), "red")

func _build_props() -> void:
	# Corridor crates and barrels, kept out of the camera axis.
	_crate(Vector3(2.12, 0.37, 1.7), 0.72)
	_crate(Vector3(2.12, 1.12, 1.7), 0.62)
	_crate(Vector3(2.18, 0.3, 0.72), 0.56)
	_barrel(Vector3(2.12, 0.55, 2.65))
	_barrel(Vector3(-2.1, 0.55, 1.0))
	# A cart with a toolbox, against the left wall.
	_cart(Vector3(-2.1, 0, 0.15))
	# Caution cone, not emissive.
	_cylinder(Vector3(0.7, 0.25, 2.7), 0.18, 0.5, "yellow")
	_box(Vector3(0.7, 0.03, 2.7), Vector3(0.38, 0.05, 0.38), "dark")
	# Wall-mounted first aid / extinguisher with a dark housing.
	_box(Vector3(2.6, 1.35, 0.7), Vector3(0.08, 0.55, 0.4), "dark")
	_box(Vector3(2.54, 1.35, 0.7), Vector3(0.08, 0.45, 0.28), "red_dim")
	_box(Vector3(2.5, 1.35, 0.7), Vector3(0.02, 0.22, 0.05), "yellow")
	_box(Vector3(2.5, 1.35, 0.7), Vector3(0.02, 0.05, 0.22), "yellow")
	# Loose floor plates.
	_box(Vector3(-1.4, 0.014, -6.2), Vector3(0.7, 0.02, 0.45), "metal_dirty")
	_box(Vector3(1.2, 0.014, 1.0), Vector3(0.55, 0.02, 0.7), "metal_dirty")

func _build_lights() -> void:
	_ceiling_fixture(8.4, true)
	_ceiling_fixture(1.5, true)
	_ceiling_fixture(-5.4, false)
	# Cool fill along the corridor to reveal walls and props.
	_omni(Vector3(0.0, 2.5, 6.2), Color(0.28, 0.5, 0.58), 1.4, 7.0, 0.5)
	_omni(Vector3(0.0, 2.5, -1.5), Color(0.24, 0.42, 0.5), 1.1, 7.0, 0.5)
	# Warm work light near the crates.
	_omni(Vector3(1.4, 2.2, 3.3), Color(1.0, 0.45, 0.12), 0.9, 4.0, 0.6)
	# Cold fill near the lab entrance.
	_omni(Vector3(-2.1, 2.5, 4.0), Color(0.2, 0.55, 0.65), 1.1, 5.0, 0.7)
	# Dim end-of-corridor light behind the camera.
	_omni(Vector3(0, 2.3, 10.8), Color(0.3, 0.65, 0.72), 0.7, 5.0, 0.5)
	# Red emergency wall lamp.
	_box(Vector3(2.58, 2.55, -2.0), Vector3(0.1, 0.34, 0.52), "dark")
	_box(Vector3(2.52, 2.55, -2.0), Vector3(0.04, 0.18, 0.36), "red")
	_omni(Vector3(2.3, 2.5, -2.0), Color(1.0, 0.08, 0.04), 0.8, 4.0, 0.6)
	# Lab overhead.
	_spot(Vector3(-7.3, 3.55, 2.4), Vector3(-7.3, 0.0, 2.4), Color(0.55, 0.78, 1.0), 3.8, 58.0, 8.0, true)
	_omni(Vector3(-5.0, 2.1, 4.8), Color(0.22, 0.45, 0.55), 1.4, 6.0, 0.5)

func _ceiling_fixture(z: float, shadow: bool) -> void:
	_box(Vector3(0, 3.61, z), Vector3(1.8, 0.11, 0.25), "dark")
	_box(Vector3(0, 3.52, z), Vector3(1.55, 0.045, 0.1), "cyan")
	_spot(Vector3(0, 3.45, z), Vector3(0, 0.0, z), Color(0.65, 0.86, 1.0), 5.5, 52.0, 9.5, shadow)
	_omni(Vector3(0, 3.35, z), Color(0.45, 0.7, 0.8), 1.0, 3.2, 0.7)

func _build_atmosphere() -> void:
	# Dust in the main corridor.
	_dust(Vector3(0, 1.6, 2.0), Vector3(2.4, 1.7, 10.0), 80)
	# Dust in the lab.
	_dust(Vector3(-7.3, 1.5, 2.4), Vector3(4.2, 1.5, 4.0), 40)
	# Steam from a valve on the right wall.
	_steam(Vector3(2.43, 2.55, -3.5), 28)
	# A low ground mist near the door.
	var fog := FogVolume.new()
	fog.size = Vector3(5.0, 1.6, 4.0)
	fog.position = Vector3(0, 0.65, -7.0)
	var fm := FogMaterial.new()
	fm.density = 0.018
	fm.albedo = Color(0.14, 0.22, 0.23)
	fm.edge_fade = 0.45
	fm.height_falloff = 0.2
	fog.material = fm
	add_child(fog)

func _build_reflection_probe() -> void:
	var probe := ReflectionProbe.new()
	probe.size = Vector3(5.3, 3.7, 21.0)
	probe.origin_offset = Vector3(0, 1.9, 1.0)
	probe.interior = true
	probe.box_projection = true
	probe.update_mode = ReflectionProbe.UPDATE_ONCE
	probe.intensity = 0.65
	probe.max_distance = 32.0
	add_child(probe)

func _build_cameras() -> void:
	_views.append(_camera(Vector3(0.0, 1.62, 8.3), Vector3(0.0, 1.45, -9.3), 72.0))
	_views.append(_camera(Vector3(-3.7, 1.72, 5.9), Vector3(-8.8, 1.1, 1.4), 74.0))
	_views.append(_camera(Vector3(1.25, 1.62, -5.3), Vector3(-0.1, 1.35, -9.8), 68.0))
	_views.append(_camera(Vector3(-8.25, 1.75, 6.2), Vector3(-8.25, 1.3, 2.2), 70.0))

func _build_overlay() -> void:
	_overlay = CanvasLayer.new()
	_overlay.layer = 10
	add_child(_overlay)
	var shade := ColorRect.new()
	shade.set_anchors_preset(Control.PRESET_FULL_RECT)
	shade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	shade.color = Color(0, 0, 0, 0)
	var shader := Shader.new()
	shader.code = """
shader_type canvas_item;
void fragment() {
	vec2 uv = SCREEN_UV;
	vec2 c = uv - vec2(0.5);
	c.x *= 1.08;
	float d = length(c);
	float v = smoothstep(0.32, 0.84, d);
	COLOR = vec4(0.0, 0.0, 0.0, v * 0.42);
}
"""
	var mat := ShaderMaterial.new()
	mat.shader = shader
	shade.material = mat
	_overlay.add_child(shade)
	var accent := ColorRect.new()
	accent.position = Vector2(28, 26)
	accent.size = Vector2(3, 42)
	accent.color = Color(1.0, 0.48, 0.12)
	accent.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_overlay.add_child(accent)
	var title := Label.new()
	title.text = "NEXUS  //  RECUPERACIÓN"
	title.position = Vector2(44, 24)
	title.add_theme_font_size_override("font_size", 14)
	title.add_theme_color_override("font_color", Color(0.47, 0.94, 0.88))
	title.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.9))
	title.add_theme_constant_override("outline_size", 4)
	_overlay.add_child(title)
	var sector := Label.new()
	sector.text = "SECTOR 04  ·  LABORATORIO SUBTERRÁNEO"
	sector.position = Vector2(44, 44)
	sector.add_theme_font_size_override("font_size", 11)
	sector.add_theme_color_override("font_color", Color(0.72, 0.77, 0.72))
	sector.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.9))
	sector.add_theme_constant_override("outline_size", 4)
	_overlay.add_child(sector)
	var bottom := Label.new()
	bottom.text = "FRECUENCIA MUERTA  ·  LOOK DEV 02"
	bottom.position = Vector2(28, 688)
	bottom.add_theme_font_size_override("font_size", 11)
	bottom.add_theme_color_override("font_color", Color(0.95, 0.55, 0.2, 0.85))
	bottom.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.9))
	bottom.add_theme_constant_override("outline_size", 4)
	_overlay.add_child(bottom)

func set_view(index: int) -> void:
	if _views.is_empty():
		return
	var view := clampi(index, 0, _views.size() - 1)
	for i in _views.size():
		_views[i].current = (i == view)

# --- helpers ---------------------------------------------------------------

func _box(pos: Vector3, size: Vector3, mat: String) -> MeshInstance3D:
	var mesh := BoxMesh.new()
	mesh.size = size
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	mi.material_override = _mat(mat)
	mi.position = pos
	add_child(mi)
	return mi

func _plane(pos: Vector3, size: Vector2, mat: String) -> MeshInstance3D:
	var mesh := PlaneMesh.new()
	mesh.size = size
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	mi.material_override = _mat(mat)
	mi.position = pos
	add_child(mi)
	return mi

func _quad(pos: Vector3, size: Vector2, mat: String, rot_deg := Vector3.ZERO) -> MeshInstance3D:
	var mesh := QuadMesh.new()
	mesh.size = size
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	mi.material_override = _mat(mat)
	mi.position = pos
	mi.rotation_degrees = rot_deg
	add_child(mi)
	return mi

func _cylinder(pos: Vector3, radius: float, height: float, mat: String, rot_deg := Vector3.ZERO) -> MeshInstance3D:
	var mesh := CylinderMesh.new()
	mesh.top_radius = radius
	mesh.bottom_radius = radius
	mesh.height = height
	mesh.radial_segments = 24
	mesh.rings = 2
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	mi.material_override = _mat(mat)
	mi.position = pos
	mi.rotation_degrees = rot_deg
	add_child(mi)
	return mi

func _torus(pos: Vector3, inner: float, outer: float, mat: String, rot_deg := Vector3.ZERO) -> MeshInstance3D:
	var mesh := TorusMesh.new()
	mesh.inner_radius = inner
	mesh.outer_radius = outer
	mesh.rings = 32
	mesh.ring_segments = 12
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	mi.material_override = _mat(mat)
	mi.position = pos
	mi.rotation_degrees = rot_deg
	add_child(mi)
	return mi

func _sphere(pos: Vector3, radius: float, mat: String) -> MeshInstance3D:
	var mesh := SphereMesh.new()
	mesh.radius = radius
	mesh.height = radius * 2.0
	mesh.radial_segments = 24
	mesh.rings = 12
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	mi.material_override = _mat(mat)
	mi.position = pos
	add_child(mi)
	return mi

func _label(text: String, pos: Vector3, size: int, color: Color, rot_deg := Vector3.ZERO, outline := 6) -> Label3D:
	var label := Label3D.new()
	label.text = text
	label.font_size = size
	label.pixel_size = 0.0065
	label.modulate = color
	label.outline_size = outline
	label.outline_modulate = Color(0, 0, 0, 0.9)
	label.shaded = false
	label.double_sided = true
	label.no_depth_test = false
	label.position = pos
	label.rotation_degrees = rot_deg
	add_child(label)
	return label

func _omni(pos: Vector3, color: Color, energy: float, radius: float, fog_energy: float = 1.0) -> OmniLight3D:
	var light := OmniLight3D.new()
	light.position = pos
	light.light_color = color
	light.light_energy = energy
	light.omni_range = radius
	light.omni_attenuation = 1.2
	light.light_volumetric_fog_energy = fog_energy
	light.shadow_enabled = false
	add_child(light)
	return light

func _spot(pos: Vector3, target: Vector3, color: Color, energy: float, angle: float, range: float, shadow: bool) -> SpotLight3D:
	var light := SpotLight3D.new()
	light.position = pos
	light.light_color = color
	light.light_energy = energy
	light.spot_angle = angle
	light.spot_range = range
	light.spot_attenuation = 1.1
	light.spot_angle_attenuation = 0.8
	light.shadow_enabled = shadow
	light.light_volumetric_fog_energy = 1.4
	add_child(light)
	if absf(pos.x - target.x) < 0.001 and absf(pos.z - target.z) < 0.001:
		light.rotation_degrees = Vector3(-90.0, 0.0, 0.0)
	else:
		light.look_at(target, Vector3.UP)
	return light

func _vent(pos: Vector3, size: Vector3, rot_y: float) -> void:
	_box(pos, size, "dark")
	var count := 6
	for i in count:
		var y := pos.y + (float(i) - 2.5) * 0.13
		_box(Vector3(pos.x, y, pos.z), Vector3(size.x - 0.01, 0.05, size.z * 0.82), "metal_dirty")
	var mi := _box(pos, size, "dark")
	mi.rotation_degrees.y = rot_y

func _grate(pos: Vector3, size: Vector2) -> void:
	_box(pos + Vector3(0, 0.01, 0), Vector3(size.x, 0.02, 0.05), "dark")
	_box(pos + Vector3(0, 0.01, 0), Vector3(0.05, 0.02, size.y), "dark")
	var count := 7
	for i in count:
		var x := pos.x - size.x * 0.5 + size.x * float(i) / float(count - 1)
		_box(Vector3(x, pos.y + 0.015, pos.z), Vector3(0.025, 0.02, size.y), "metal_dirty")

func _decal(pos: Vector3, size: Vector2, rot_x: float, rot_y: float) -> void:
	var mi := _quad(pos, size, "grunge", Vector3(rot_x, rot_y, 0))
	mi.rotation_degrees = Vector3(rot_x, rot_y, 0)

func _crate(pos: Vector3, size: float) -> void:
	_box(pos, Vector3(size, size, size), "metal_dirty")
	var edge := 0.035
	for sx in [-1.0, 1.0]:
		for sy in [-1.0, 1.0]:
			_box(pos + Vector3(sx * size * 0.5, sy * size * 0.5, size * 0.5), Vector3(edge, edge, size), "dark")
	for sz in [-1.0, 1.0]:
		for sy in [-1.0, 1.0]:
			_box(pos + Vector3(sz * size * 0.5, sy * size * 0.5, size * 0.5), Vector3(size, edge, edge), "dark")
	_box(pos + Vector3(0, 0.0, size * 0.51), Vector3(size * 0.62, size * 0.12, 0.03), "hazard")

func _barrel(pos: Vector3) -> void:
	_cylinder(pos, 0.34, 1.0, "rust")
	_cylinder(pos + Vector3(0, 0.22, 0), 0.37, 0.05, "dark")
	_cylinder(pos - Vector3(0, 0.22, 0), 0.37, 0.05, "dark")
	_cylinder(pos + Vector3(0, 0.48, 0), 0.3, 0.03, "dark")

func _cart(pos: Vector3) -> void:
	_box(pos + Vector3(0, 0.78, 0), Vector3(0.9, 0.08, 0.55), "metal_dirty")
	for x in [-0.35, 0.35]:
		for z in [-0.2, 0.2]:
			_cylinder(pos + Vector3(x, 0.38, z), 0.035, 0.72, "dark")
	_box(pos + Vector3(0, 0.9, 0), Vector3(0.38, 0.24, 0.3), "yellow")
	_box(pos + Vector3(0, 1.03, 0), Vector3(0.3, 0.03, 0.05), "dark")

func _gurney(pos: Vector3) -> void:
	_box(pos + Vector3(0, 0.58, 0), Vector3(2.0, 0.1, 0.78), "metal_dirty")
	for x in [-0.82, 0.82]:
		for z in [-0.3, 0.3]:
			_cylinder(pos + Vector3(x, 0.27, z), 0.035, 0.54, "dark")
	_box(pos + Vector3(0, 0.7, 0), Vector3(1.8, 0.13, 0.68), "rubber")
	# covered body
	var body := _sphere(pos + Vector3(0.05, 0.82, 0), 0.48, "rubber")
	body.scale = Vector3(1.8, 0.25, 0.55)
	body.rotation_degrees.z = 4.0
	_box(pos + Vector3(-0.6, 0.92, 0), Vector3(1.5, 0.035, 0.5), "dark")
	_box(pos + Vector3(0.65, 0.78, 0.36), Vector3(0.04, 1.6, 0.04), "rust")

func _desk(pos: Vector3, screen_pos: Vector3) -> void:
	_box(pos + Vector3(0, 0.82, 0), Vector3(2.0, 0.1, 0.8), "metal_dirty")
	for x in [-0.8, 0.8]:
		for z in [-0.3, 0.3]:
			_box(pos + Vector3(x, 0.4, z), Vector3(0.07, 0.8, 0.07), "dark")
	_box(pos + Vector3(0.0, 1.55, 0.25), Vector3(0.62, 0.48, 0.12), "dark")
	_quad(pos + Vector3(0.0, 1.55, 0.315), Vector2(0.48, 0.3), "screen")
	_box(pos + Vector3(0.0, 1.26, 0.25), Vector3(0.3, 0.07, 0.15), "rubber")
	_box(pos + Vector3(-0.35, 0.9, 0.18), Vector3(0.38, 0.02, 0.22), "dark")
	_box(pos + Vector3(0.38, 0.91, 0.18), Vector3(0.26, 0.03, 0.18), "metal_dirty")
	_label("NEXUS", screen_pos, 18, Color(0.3, 0.95, 0.85), Vector3(0, 90, 0), 5)

func _cabinet(pos: Vector3) -> void:
	_box(pos + Vector3(0, 1.0, 0), Vector3(0.8, 2.0, 0.8), "metal_dirty")
	_box(pos + Vector3(0.42, 1.05, 0), Vector3(0.03, 1.75, 0.62), "dark")
	_box(pos + Vector3(0.44, 1.08, 0.22), Vector3(0.02, 0.26, 0.06), "green")
	_box(pos + Vector3(0.44, 0.45, 0.22), Vector3(0.02, 0.1, 0.06), "yellow")
	# jars on top
	for i in 3:
		_cylinder(pos + Vector3(-0.25 + i * 0.25, 2.13, 0), 0.075, 0.26, "glass")
		_cylinder(pos + Vector3(-0.25 + i * 0.25, 2.08, 0), 0.055, 0.16, "green")

func _screen(pos: Vector3, size: Vector2, text: String, rot_y := 0.0) -> void:
	var frame := _box(pos + Vector3(0, 0, -0.035), Vector3(size.x + 0.12, size.y + 0.12, 0.06), "dark")
	frame.rotation_degrees.y = rot_y
	var screen := _quad(pos + Vector3(0, 0, 0.005), size, "screen")
	screen.rotation_degrees.y = rot_y
	var label := _label(text, pos + Vector3(0, -size.y * 0.5 - 0.12, 0.03), 16, Color(0.45, 0.95, 0.9), Vector3(0, rot_y, 0), 4)
	label.position = pos + Vector3(0, -size.y * 0.5 - 0.12, 0.03)

func _locker(pos: Vector3, rot_y: float) -> void:
	var mi := _box(pos, Vector3(0.8, 2.2, 0.7), "metal_dirty")
	mi.rotation_degrees.y = rot_y
	for i in 4:
		var slat := _box(pos + Vector3(-0.26, 0.85 - i * 0.08, 0.36), Vector3(0.22, 0.035, 0.03), "dark")
		slat.rotation_degrees.y = rot_y
	_box(pos + Vector3(0.3, 1.0, 0.37), Vector3(0.04, 0.22, 0.03), "dark")

func _dust(pos: Vector3, extents: Vector3, amount: int) -> void:
	var p := GPUParticles3D.new()
	p.amount = amount
	p.lifetime = 14.0
	p.preprocess = 6.0
	p.position = pos
	p.local_coords = false
	p.visibility_aabb = AABB(Vector3(-20, -3, -20), Vector3(40, 12, 40))
	var pm := ParticleProcessMaterial.new()
	pm.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_BOX
	pm.emission_box_extents = extents
	pm.gravity = Vector3(0.0, 0.006, 0.0)
	pm.initial_velocity_min = 0.005
	pm.initial_velocity_max = 0.03
	pm.scale_min = 0.01
	pm.scale_max = 0.03
	pm.color = Color(0.75, 0.86, 0.85, 0.20)
	p.process_material = pm
	var quad := QuadMesh.new()
	quad.size = Vector2(0.04, 0.04)
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.albedo_texture = load("res://assets/art/fm/smoke.png")
	mat.albedo_color = Color(0.8, 0.9, 0.9, 0.18)
	mat.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	quad.material = mat
	p.draw_pass_1 = quad
	add_child(p)

func _steam(pos: Vector3, amount: int) -> void:
	var p := CPUParticles3D.new()
	p.amount = amount
	p.lifetime = 2.6
	p.preprocess = 0.8
	p.position = pos
	p.local_coords = false
	p.direction = Vector3(0.0, 1.0, 0.0)
	p.spread = 22.0
	p.gravity = Vector3(0.02, 0.09, 0.0)
	p.initial_velocity_min = 0.25
	p.initial_velocity_max = 0.7
	p.scale_amount_min = 0.4
	p.scale_amount_max = 1.2
	p.color = Color(0.8, 0.88, 0.88, 0.16)
	p.emission_shape = CPUParticles3D.EMISSION_SHAPE_SPHERE
	p.emission_sphere_radius = 0.12
	var quad := QuadMesh.new()
	quad.size = Vector2(0.55, 0.55)
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.albedo_texture = load("res://assets/art/fm/smoke.png")
	mat.albedo_color = Color(0.8, 0.88, 0.88, 0.18)
	mat.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	quad.material = mat
	p.mesh = quad
	add_child(p)

func _camera(pos: Vector3, target: Vector3, fov: float) -> Camera3D:
	var cam := Camera3D.new()
	cam.position = pos
	cam.fov = fov
	cam.near = 0.05
	cam.far = 80.0
	add_child(cam)
	cam.look_at(target, Vector3.UP)
	var lamp := SpotLight3D.new()
	lamp.position = Vector3(0.08, -0.02, 0.0)
	lamp.light_color = Color(1.0, 0.86, 0.66)
	lamp.light_energy = 0.8
	lamp.spot_range = 12.0
	lamp.spot_angle = 42.0
	lamp.spot_attenuation = 1.2
	lamp.shadow_enabled = false
	lamp.light_volumetric_fog_energy = 0.25
	cam.add_child(lamp)
	return cam
