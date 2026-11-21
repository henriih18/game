class_name FMPilotTestPanel
extends StaticBody3D

## Panel de validación del piloto Z10.
## No es un objeto narrativo: sirve para comprobar el raycast de interacción
## de FMPlayer dentro del Conector exportado.

signal activated(count: int)

var activations := 0
var _screen_material: StandardMaterial3D
var _screen_light: OmniLight3D


func _ready() -> void:
	add_to_group("fm_interactable")
	collision_layer = 1
	collision_mask = 1
	_build_body()
	_build_screen()
	_build_collision()


func _build_body() -> void:
	var body := MeshInstance3D.new()
	body.name = "ValidationBody"
	var mesh := BoxMesh.new()
	mesh.size = Vector3(0.55, 1.0, 0.28)
	body.mesh = mesh
	body.position.y = 0.5
	var material := StandardMaterial3D.new()
	material.albedo_color = Color(0.055, 0.065, 0.070)
	material.metallic = 0.55
	material.roughness = 0.52
	body.material_override = material
	add_child(body)

	var plinth := MeshInstance3D.new()
	plinth.name = "ValidationPlinth"
	var plinth_mesh := BoxMesh.new()
	plinth_mesh.size = Vector3(0.62, 0.08, 0.34)
	plinth.mesh = plinth_mesh
	plinth.position.y = 0.04
	var plinth_material := StandardMaterial3D.new()
	plinth_material.albedo_color = Color(0.035, 0.040, 0.043)
	plinth_material.metallic = 0.35
	plinth_material.roughness = 0.62
	plinth.material_override = plinth_material
	add_child(plinth)


func _build_screen() -> void:
	var bezel := MeshInstance3D.new()
	bezel.name = "ValidationBezel"
	var bezel_mesh := BoxMesh.new()
	bezel_mesh.size = Vector3(0.46, 0.34, 0.035)
	bezel.mesh = bezel_mesh
	bezel.position = Vector3(0.0, 0.78, 0.145)
	var bezel_material := StandardMaterial3D.new()
	bezel_material.albedo_color = Color(0.018, 0.021, 0.023)
	bezel_material.metallic = 0.4
	bezel_material.roughness = 0.45
	bezel.material_override = bezel_material
	add_child(bezel)

	var screen := MeshInstance3D.new()
	screen.name = "ValidationScreen"
	var screen_mesh := BoxMesh.new()
	screen_mesh.size = Vector3(0.38, 0.26, 0.012)
	screen.mesh = screen_mesh
	screen.position = Vector3(0.0, 0.78, 0.166)
	_screen_material = StandardMaterial3D.new()
	_screen_material.albedo_color = Color(0.025, 0.020, 0.012)
	_screen_material.emission_enabled = true
	_screen_material.emission = Color(1.0, 0.52, 0.10)
	_screen_material.emission_energy_multiplier = 1.8
	_screen_material.roughness = 0.28
	screen.material_override = _screen_material
	add_child(screen)

	var indicator := MeshInstance3D.new()
	indicator.name = "ValidationIndicator"
	var indicator_mesh := SphereMesh.new()
	indicator_mesh.radius = 0.018
	indicator_mesh.height = 0.036
	indicator.mesh = indicator_mesh
	indicator.position = Vector3(0.235, 0.93, 0.166)
	var indicator_material := StandardMaterial3D.new()
	indicator_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	indicator_material.albedo_color = Color(1.0, 0.42, 0.06)
	indicator_material.emission_enabled = true
	indicator_material.emission = Color(1.0, 0.42, 0.06)
	indicator_material.emission_energy_multiplier = 2.4
	indicator.material_override = indicator_material
	add_child(indicator)

	_screen_light = OmniLight3D.new()
	_screen_light.name = "ValidationScreenLight"
	_screen_light.position = Vector3(0.0, 0.78, 0.30)
	_screen_light.light_color = Color(1.0, 0.55, 0.16)
	_screen_light.light_energy = 0.55
	_screen_light.omni_range = 1.6
	_screen_light.shadow_enabled = false
	add_child(_screen_light)


func _build_collision() -> void:
	var shape := BoxShape3D.new()
	shape.size = Vector3(0.58, 1.02, 0.31)
	var collider := CollisionShape3D.new()
	collider.shape = shape
	collider.position.y = 0.51
	add_child(collider)


func can_interact(_player: Node) -> bool:
	return true


func get_interaction_position() -> Vector3:
	return global_position + Vector3(0.0, 1.15, 0.0)


func get_interaction_prompt() -> String:
	return "E   PROBAR PANEL DE VALIDACIÓN  [%d]" % activations


func interact(_player: Node) -> void:
	activations += 1
	var lit := activations % 2 == 1
	_screen_material.emission = Color(0.10, 1.0, 0.45) if lit else Color(1.0, 0.52, 0.10)
	_screen_light.light_color = Color(0.20, 1.0, 0.50) if lit else Color(1.0, 0.55, 0.16)
	activated.emit(activations)
	print("PILOT_PANEL_INTERACT ", activations)
