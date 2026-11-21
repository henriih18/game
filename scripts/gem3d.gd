class_name Gem3D
extends Node3D

var collected := false
var _base_y := 0.8
var _time := 0.0
var _phase := 0.0
var _light: OmniLight3D
var _visual: Node3D

func _ready() -> void:
	_base_y = position.y
	_phase = randf() * TAU
	_time = _phase
	_build_visual()

func _build_visual() -> void:
	_visual = Node3D.new()
	_visual.name = "Visual"
	add_child(_visual)

	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.1, 0.78, 0.36)
	mat.roughness = 0.2
	mat.metallic = 0.35
	mat.emission_enabled = true
	mat.emission = Color(0.12, 0.85, 0.38)
	mat.emission_energy_multiplier = 0.75

	var top := MeshInstance3D.new()
	var top_mesh := CylinderMesh.new()
	top_mesh.top_radius = 0.0
	top_mesh.bottom_radius = 0.34
	top_mesh.height = 0.52
	top_mesh.radial_segments = 6
	top_mesh.rings = 1
	top.mesh = top_mesh
	top.material_override = mat
	top.position.y = 0.26
	_visual.add_child(top)

	var bottom := MeshInstance3D.new()
	var bottom_mesh := CylinderMesh.new()
	bottom_mesh.top_radius = 0.34
	bottom_mesh.bottom_radius = 0.0
	bottom_mesh.height = 0.52
	bottom_mesh.radial_segments = 6
	bottom_mesh.rings = 1
	bottom.mesh = bottom_mesh
	bottom.material_override = mat
	bottom.position.y = -0.26
	_visual.add_child(bottom)

	var glow := MeshInstance3D.new()
	var glow_mesh := SphereMesh.new()
	glow_mesh.radius = 0.5
	glow_mesh.height = 0.85
	glow_mesh.radial_segments = 16
	glow_mesh.rings = 8
	glow.mesh = glow_mesh
	var glow_mat := StandardMaterial3D.new()
	glow_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	glow_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	glow_mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	glow_mat.albedo_color = Color(0.3, 1.0, 0.6, 0.025)
	glow.material_override = glow_mat
	glow.scale = Vector3(0.8, 0.8, 0.8)
	_visual.add_child(glow)

	_light = OmniLight3D.new()
	_light.light_color = Color(0.3, 1.0, 0.55)
	_light.light_energy = 0.5
	_light.omni_range = 2.2
	add_child(_light)

func _process(delta: float) -> void:
	if collected:
		return
	_time += delta
	position.y = _base_y + sin(_time * 2.1) * 0.12
	rotation.y += delta * 1.6
	_visual.rotation.z = sin(_time * 1.3) * 0.08

func collect() -> void:
	if collected:
		return
	collected = true
	visible = false
	_light.visible = false
