class_name FMScenarioDressing
extends Node3D

## Decorado, arquitectura secundaria, deterioro y narrativa ambiental del slice.
## No contiene lógica de juego ni colisiones: todo es presentación.
## Reutiliza los materiales PBR de assets/art/fm y las texturas de detalle nuevas.

const BLOOD := preload("res://assets/art/fm/blood_splat.png")
const BLOOD_TRAIL := preload("res://assets/art/fm/blood_trail.png")
const HANDPRINT := preload("res://assets/art/fm/handprint.png")
const PUDDLE := preload("res://assets/art/fm/puddle.png")
const GRIME := preload("res://assets/art/fm/grime_decal.png")
const CRACK := preload("res://assets/art/fm/glass_crack.png")
const SMOKE := preload("res://assets/art/fm/smoke.png")

var _mats: Dictionary = {}
var _time := 0.0
var _flicker: Array[Dictionary] = []

func build(materials: Dictionary, include_corridor := true) -> void:
	_mats = materials
	if include_corridor:
		_architecture()
		_corridor_details()
		_narrative_damage()
	_lab_details()
	_extraction_details()
	_atmosphere()

func _process(delta: float) -> void:
	_time += delta
	for item in _flicker:
		var light := item.get("light") as OmniLight3D
		if light == null or not is_instance_valid(light):
			continue
		var phase: float = item.get("phase", 0.0)
		var base: float = item.get("energy", 0.8)
		var pulse := 0.82 + 0.18 * sin(_time * 7.0 + phase)
		if sin(_time * 1.7 + phase * 2.0) > 0.86:
			pulse *= 0.25
		light.light_energy = base * pulse

func _mat(key: String) -> Material:
	return _mats.get(key, _mats.get("dark", null))

func _simple(color: Color, roughness := 0.8, metallic := 0.0) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = color
	m.roughness = roughness
	m.metallic = metallic
	return m

func _emissive(color: Color, energy := 1.2) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = color * 0.35
	m.emission_enabled = true
	m.emission = color
	m.emission_energy_multiplier = energy
	m.roughness = 0.35
	return m

func _decal_material(texture: Texture2D, tint: Color, alpha := 1.0, unshaded := true) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_texture = texture
	m.albedo_color = Color(tint.r, tint.g, tint.b, alpha)
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.cull_mode = BaseMaterial3D.CULL_DISABLED
	m.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
	if unshaded:
		m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	else:
		m.roughness = 0.16
		m.metallic = 0.25
	return m

func _box(pos: Vector3, size: Vector3, mat: Material, rot := Vector3.ZERO) -> MeshInstance3D:
	var mesh := BoxMesh.new()
	mesh.size = size
	var node := MeshInstance3D.new()
	node.mesh = mesh
	node.material_override = mat
	node.position = pos
	node.rotation_degrees = rot
	add_child(node)
	return node

func _cyl(pos: Vector3, radius: float, height: float, mat: Material, rot := Vector3.ZERO, top := -1.0) -> MeshInstance3D:
	var mesh := CylinderMesh.new()
	mesh.bottom_radius = radius
	mesh.top_radius = radius if top < 0.0 else top
	mesh.height = height
	mesh.radial_segments = 12
	var node := MeshInstance3D.new()
	node.mesh = mesh
	node.material_override = mat
	node.position = pos
	node.rotation_degrees = rot
	add_child(node)
	return node

func _quad(pos: Vector3, size: Vector2, mat: Material, rot := Vector3.ZERO) -> MeshInstance3D:
	var mesh := QuadMesh.new()
	mesh.size = size
	var node := MeshInstance3D.new()
	node.mesh = mesh
	node.material_override = mat
	node.position = pos
	node.rotation_degrees = rot
	add_child(node)
	return node

func _sign(text: String, pos: Vector3, size: int, color: Color, rot := Vector3.ZERO) -> void:
	var root := Node3D.new()
	root.position = pos
	root.rotation_degrees = rot
	add_child(root)
	var width := maxf(0.72, text.length() * size * 0.00205 + 0.20)
	var height := size * 0.0038 + 0.17
	var backing := MeshInstance3D.new()
	var backing_mesh := BoxMesh.new()
	backing_mesh.size = Vector3(width + 0.05, height + 0.05, 0.035)
	backing.mesh = backing_mesh
	backing.material_override = _simple(Color(0.025, 0.032, 0.030), 0.62, 0.25)
	backing.position = Vector3(0, 0, 0.018)
	root.add_child(backing)
	var inner := MeshInstance3D.new()
	var inner_mesh := BoxMesh.new()
	inner_mesh.size = Vector3(width, height, 0.02)
	inner.mesh = inner_mesh
	inner.material_override = _simple(Color(0.07, 0.085, 0.075), 0.8, 0.1)
	inner.position = Vector3(0, 0, 0.038)
	root.add_child(inner)
	var label := Label3D.new()
	label.text = text
	label.font_size = size
	label.pixel_size = 0.0038
	label.modulate = color
	label.outline_size = 5
	label.outline_modulate = Color(0.005, 0.008, 0.01, 0.95)
	label.position = Vector3(0, 0, 0.052)
	label.billboard = BaseMaterial3D.BILLBOARD_DISABLED
	root.add_child(label)

func _label(text: String, pos: Vector3, size: int, color: Color, rot := Vector3.ZERO) -> Label3D:
	var label := Label3D.new()
	label.text = text
	label.font_size = size
	label.pixel_size = 0.0038
	label.modulate = color
	label.outline_size = 5
	label.outline_modulate = Color(0.005, 0.008, 0.01, 0.95)
	label.position = pos
	label.rotation_degrees = rot
	label.billboard = BaseMaterial3D.BILLBOARD_DISABLED
	add_child(label)
	return label

func _omni(pos: Vector3, color: Color, energy: float, radius: float, flicker := false) -> OmniLight3D:
	var light := OmniLight3D.new()
	light.position = pos
	light.light_color = color
	light.light_energy = energy
	light.omni_range = radius
	light.shadow_enabled = false
	light.light_volumetric_fog_energy = 0.45
	add_child(light)
	if flicker:
		_flicker.append({"light": light, "energy": energy, "phase": float(_flicker.size()) * 1.7})
	return light

func _cable(a: Vector3, b: Vector3, radius: float, mat: Material) -> MeshInstance3D:
	var delta := b - a
	var length := delta.length()
	var mesh := CylinderMesh.new()
	mesh.bottom_radius = radius
	mesh.top_radius = radius
	mesh.height = maxf(length, 0.02)
	mesh.radial_segments = 6
	var node := MeshInstance3D.new()
	node.mesh = mesh
	node.material_override = mat
	node.position = (a + b) * 0.5
	if length > 0.0001:
		node.quaternion = Quaternion(Vector3.UP, delta / length)
	add_child(node)
	return node

func _multimesh(parent: Node3D, mesh: Mesh, mat: Material, transforms: Array[Transform3D], shadows := true) -> MultiMeshInstance3D:
	var multi := MultiMesh.new()
	multi.transform_format = MultiMesh.TRANSFORM_3D
	multi.instance_count = transforms.size()
	multi.mesh = mesh
	for i in transforms.size():
		multi.set_instance_transform(i, transforms[i])
	var node := MultiMeshInstance3D.new()
	node.multimesh = multi
	node.material_override = mat
	node.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON if shadows else GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	parent.add_child(node)
	return node

func _floor_decal(pos: Vector3, size: Vector2, texture: Texture2D, color: Color, yaw := 0.0, alpha := 1.0) -> void:
	var mat := _decal_material(texture, color, alpha)
	_quad(pos, size, mat, Vector3(-90.0, yaw, 0.0))

func _wall_decal(pos: Vector3, size: Vector2, texture: Texture2D, color: Color, yaw: float, alpha := 1.0) -> void:
	var mat := _decal_material(texture, color, alpha)
	_quad(pos, size, mat, Vector3(0.0, yaw, 0.0))

func _architecture() -> void:
	var metal := _mat("metal_dirty")
	var dark := _mat("dark")
	# Costillas y zócalos del corredor.
	for z in range(-8, 11, 2):
		for side in [-1.0, 1.0]:
			_box(Vector3(2.71 * side, 1.85, float(z)), Vector3(0.09, 3.2, 0.18), metal)
	_box(Vector3(2.74, 0.10, 1.0), Vector3(0.12, 0.20, 23.0), dark)
	_box(Vector3(-2.74, 0.10, 1.0), Vector3(0.12, 0.20, 23.0), dark)
	# Vigas de techo.
	for z in [-7.0, -4.0, -1.0, 2.0, 5.0, 8.0]:
		_box(Vector3(0, 3.88, z), Vector3(5.4, 0.13, 0.18), metal)
	# Bandeja de cables y cableado.
	for x in [-2.02, -1.72]:
		_box(Vector3(x, 3.55, 1.0), Vector3(0.055, 0.07, 22.5), dark)
	for i in range(6):
		var x := -1.98 + i * 0.052
		_box(Vector3(x, 3.59 + (i % 2) * 0.018, 1.0), Vector3(0.022, 0.022, 22.0), _simple(Color(0.10, 0.08, 0.06) if i % 3 else Color(0.20, 0.08, 0.03), 0.8))
	for z in [-7.0, -2.0, 3.0, 8.0]:
		_box(Vector3(-1.87, 3.48, z), Vector3(0.62, 0.08, 0.06), metal)
	# Tuberías: cian, óxido y roja ya existente.
	_cyl(Vector3(-2.35, 2.70, 1.0), 0.085, 22.2, _mat("rust"), Vector3(90, 0, 0))
	_cyl(Vector3(2.34, 2.44, 0.0), 0.065, 21.5, _mat("metal"), Vector3(90, 0, 0))
	for z in [-7.0, -3.0, 1.0, 5.0, 9.0]:
		_box(Vector3(-2.35, 2.70, z), Vector3(0.24, 0.22, 0.07), dark)
		_box(Vector3(2.34, 2.44, z), Vector3(0.20, 0.18, 0.06), dark)
	# Rejillas de ventilación.
	_vent(Vector3(2.69, 2.85, -6.2), 0.8, 0.5, 0.0)
	_vent(Vector3(-2.69, 2.85, 1.8), 0.65, 0.42, PI)
	_vent(Vector3(-2.69, 3.0, -4.8), 0.55, 0.35, PI)
	# Cajas eléctricas y conductos.
	for z in [2.2, -4.4]:
		_box(Vector3(2.68, 1.72, z), Vector3(0.32, 0.48, 0.16), _mat("dark"))
		_box(Vector3(2.66, 1.72, z - 0.01), Vector3(0.24, 0.34, 0.02), _mat("warning_yellow"))
		for dx in [-0.09, 0.09]:
			_cyl(Vector3(2.65 + dx, 1.22, z), 0.025, 1.1, dark)
	# Cámaras de seguridad.
	_camera(Vector3(2.55, 3.45, -8.2), -0.4)
	_camera(Vector3(-2.55, 3.45, -1.0), PI + 0.4)
	# Lámparas y balizas de emergencia.
	_emergency(Vector3(-2.58, 2.45, 6.4), PI)
	_emergency(Vector3(2.58, 2.45, -7.0), PI)
	_emergency(Vector3(0, 3.72, -9.55), 0.0, true)
	# Pasarela de cables sueltos.
	_cable(Vector3(-2.1, 3.43, 4.2), Vector3(-2.2, 2.35, 3.5), 0.018, _simple(Color(0.02, 0.025, 0.03)))
	_cable(Vector3(-1.8, 3.4, 4.1), Vector3(-2.45, 2.0, 3.0), 0.014, _simple(Color(0.18, 0.06, 0.03)))
	_cable(Vector3(1.9, 3.4, -3.2), Vector3(2.2, 1.8, -2.7), 0.015, _simple(Color(0.03, 0.03, 0.03)))
	# Apliques de pared del lado derecho: evitan que el corredor quede a oscuras.
	for z in [4.0, -4.0, -8.0]:
		_box(Vector3(2.67, 2.60, z), Vector3(0.12, 0.30, 0.20), _mat("dark"))
		_box(Vector3(2.60, 2.60, z), Vector3(0.02, 0.12, 0.13), _mat("cyan_dim"))
		_omni(Vector3(2.35, 2.55, z), Color(0.45, 0.65, 0.90), 0.55, 4.8)

func _vent(pos: Vector3, w: float, h: float, yaw: float) -> void:
	var dark := _mat("dark")
	_box(pos, Vector3(w, h, 0.055), dark, Vector3(0, yaw / PI * 180.0, 0))
	for i in range(4):
		_box(pos + Vector3(0, -h * 0.32 + i * h * 0.21, -0.035), Vector3(w * 0.78, h * 0.07, 0.02), _mat("metal"), Vector3(0, yaw / PI * 180.0, 0))

func _camera(pos: Vector3, yaw: float) -> void:
	var dark := _mat("dark")
	var body := _box(pos, Vector3(0.24, 0.16, 0.30), dark, Vector3(0, yaw / PI * 180.0, -8.0))
	_cyl(pos + Vector3(0, -0.01, -0.17).rotated(Vector3.UP, yaw), 0.07, 0.08, _mat("glass"), Vector3(90, 0, 0))
	var led := MeshInstance3D.new()
	var sphere := SphereMesh.new()
	sphere.radius = 0.022
	sphere.height = 0.044
	led.mesh = sphere
	led.material_override = _emissive(Color(1.0, 0.08, 0.05), 2.6)
	led.position = pos + Vector3(0.10, 0.075, -0.13).rotated(Vector3.UP, yaw)
	add_child(led)

func _emergency(pos: Vector3, yaw: float, ceiling := false) -> void:
	var red := _mat("red")
	_box(pos, Vector3(0.30, 0.16, 0.16), _mat("dark"), Vector3(0, yaw / PI * 180.0, 0))
	_box(pos + Vector3(0, 0, -0.09).rotated(Vector3.UP, yaw), Vector3(0.24, 0.08, 0.035), red, Vector3(0, yaw / PI * 180.0, 0))
	_omni(pos + Vector3(0, -0.18, 0), Color(1.0, 0.08, 0.045), 0.65 if not ceiling else 1.15, 4.2 if not ceiling else 5.0, true)
	if ceiling:
		_cyl(pos + Vector3(0, 0.18, 0), 0.16, 0.1, _mat("dark"))

func _corridor_details() -> void:
	# Flechas de evacuación pintadas en el suelo.
	for z in [7.0, -0.5, -7.0]:
		for side in [-1.0, 1.0]:
			_box(Vector3(0.0, 0.018, z), Vector3(0.48, 0.004, 0.08), _mat("warning_yellow"), Vector3(0, 35.0 * side, 0))
	# Señalética.
	_sign("SALIDA DE EMERGENCIA", Vector3(2.66, 2.05, 3.6), 13, Color(0.55, 0.95, 0.66), Vector3(0, -90, 0))
	_sign("AUTORIZACIÓN NIVEL 3", Vector3(2.66, 2.00, -8.45), 11, Color(0.9, 0.72, 0.35), Vector3(0, -90, 0))
	_sign("ZONA CONTAMINADA", Vector3(-2.66, 2.20, 5.45), 13, Color(1.0, 0.38, 0.22), Vector3(0, 90, 0))
	# Suciedad, agua y sangre.
	_floor_decal(Vector3(1.2, 0.015, 4.8), Vector2(2.8, 2.0), PUDDLE, Color(0.48, 0.65, 0.68), 0.2, 0.72)
	_floor_decal(Vector3(-1.5, 0.016, -3.4), Vector2(2.1, 1.5), PUDDLE, Color(0.40, 0.56, 0.60), -0.3, 0.62)
	_floor_decal(Vector3(1.75, 0.017, -7.2), Vector2(1.5, 1.1), PUDDLE, Color(0.34, 0.48, 0.52), 0.5, 0.55)
	_wall_decal(Vector3(2.675, 1.2, 5.4), Vector2(1.3, 1.0), GRIME, Color(0.36, 0.30, 0.22), -90.0, 0.35)
	_wall_decal(Vector3(-2.675, 1.35, -5.5), Vector2(1.1, 1.4), GRIME, Color(0.30, 0.26, 0.20), 90.0, 0.32)
	_wall_decal(Vector3(1.2, 1.05, 9.55), Vector2(1.8, 1.1), HANDPRINT, Color(0.55, 0.10, 0.08), 180.0, 0.85)
	# Rastro que viene del laboratorio hacia el corredor.
	for i in range(5):
		var z := 5.0 - i * 1.35
		_floor_decal(Vector3(-2.4 + i * 0.28, 0.018, z), Vector2(1.1, 0.55), BLOOD_TRAIL, Color(0.62, 0.12, 0.09), 0.1 + i * 0.1, 0.62 - i * 0.05)
	_floor_decal(Vector3(-1.6, 0.019, 1.2), Vector2(1.5, 1.0), BLOOD, Color(0.55, 0.08, 0.06), 0.3, 0.6)
	# Escombros y cristales.
	_debris()
	_papers()

func _debris() -> void:
	var transforms: Array[Transform3D] = []
	var rng := RandomNumberGenerator.new()
	rng.seed = 77123
	for i in range(16):
		var pos := Vector3(rng.randf_range(-2.2, 2.2), 0.04, rng.randf_range(-8.0, 8.5))
		var basis := Basis(Vector3.UP, rng.randf() * TAU)
		var size := Vector3(rng.randf_range(0.06, 0.22), rng.randf_range(0.025, 0.09), rng.randf_range(0.08, 0.32))
		transforms.append(Transform3D(basis.scaled(size), pos))
	var mesh := BoxMesh.new()
	mesh.size = Vector3.ONE
	_multimesh(self, mesh, _mat("rust"), transforms)
	# Cristales del tanque.
	var shards: Array[Transform3D] = []
	for i in range(12):
		var pos := Vector3(rng.randf_range(-8.4, -6.3), 0.03, rng.randf_range(2.7, 4.1))
		var basis := Basis(Vector3.UP, rng.randf() * TAU).scaled(Vector3(rng.randf_range(0.06, 0.18), 0.012, rng.randf_range(0.10, 0.28)))
		shards.append(Transform3D(basis, pos))
	var glass_mesh := BoxMesh.new()
	glass_mesh.size = Vector3.ONE
	_multimesh(self, glass_mesh, _mat("glass"), shards, false)

func _papers() -> void:
	var transforms: Array[Transform3D] = []
	var rng := RandomNumberGenerator.new()
	rng.seed = 31337
	for i in range(18):
		var pos := Vector3(rng.randf_range(-9.1, -3.1), 0.018, rng.randf_range(0.4, 5.0))
		var basis := Basis(Vector3.UP, rng.randf() * TAU).scaled(Vector3(rng.randf_range(0.12, 0.20), 0.003, rng.randf_range(0.15, 0.24)))
		transforms.append(Transform3D(basis, pos))
	for i in range(8):
		var pos := Vector3(rng.randf_range(-2.0, 2.0), 0.018, rng.randf_range(-8.5, 8.8))
		var basis := Basis(Vector3.UP, rng.randf() * TAU).scaled(Vector3(rng.randf_range(0.11, 0.18), 0.0025, rng.randf_range(0.14, 0.22)))
		transforms.append(Transform3D(basis, pos))
	var paper := BoxMesh.new()
	paper.size = Vector3.ONE
	_multimesh(self, paper, _simple(Color(0.30, 0.29, 0.25), 0.96), transforms, false)

func _lab_details() -> void:
	var metal := _mat("metal_dirty")
	var dark := _mat("dark")
	# Consola de observación en la pared oeste.
	for i in range(3):
		var z := 1.2 + i * 0.92
		_box(Vector3(-9.40, 1.55, z), Vector3(0.16, 0.72, 0.78), dark)
		_quad(Vector3(-9.30, 1.58, z), Vector2(0.62, 0.38), _mat("screen"), Vector3(0, 90, 0))
		_label("OBSERVACIÓN 0%d" % (i + 1), Vector3(-9.32, 1.94, z), 8, Color(0.35, 0.78, 0.68), Vector3(0, 90, 0))
	_box(Vector3(-9.15, 1.05, 2.05), Vector3(0.55, 0.06, 2.5), metal)
	_omni(Vector3(-8.95, 1.8, 2.1), Color(0.20, 0.55, 1.0), 0.55, 3.4)
	# Mesa auxiliar con instrumental.
	_box(Vector3(-8.95, 0.82, 0.55), Vector3(1.05, 0.08, 0.62), metal)
	for x in [-0.42, 0.42]:
		_box(Vector3(-8.95 + x, 0.40, 0.55), Vector3(0.06, 0.8, 0.06), dark)
	_cyl(Vector3(-9.25, 0.96, 0.55), 0.07, 0.22, _mat("glass"))
	_cyl(Vector3(-8.85, 0.94, 0.55), 0.10, 0.14, _mat("glass"))
	_box(Vector3(-8.48, 0.91, 0.50), Vector3(0.22, 0.10, 0.18), dark)
	# Cuerpo en bolsa sobre el suelo, con rastro.
	_box(Vector3(-8.45, 0.12, 3.45), Vector3(1.8, 0.20, 0.62), _simple(Color(0.13, 0.15, 0.14), 0.62), Vector3(0, 9, 4))
	for z in [-0.24, 0.0, 0.24]:
		_box(Vector3(-8.45 + z, 0.22, 3.45), Vector3(0.08, 0.03, 0.68), _simple(Color(0.32, 0.30, 0.24), 0.7), Vector3(0, 9, 4))
	_floor_decal(Vector3(-8.25, 0.018, 3.25), Vector2(2.4, 1.15), BLOOD, Color(0.50, 0.07, 0.05), 0.1, 0.7)
	_floor_decal(Vector3(-7.55, 0.019, 2.65), Vector2(1.6, 0.8), BLOOD_TRAIL, Color(0.5, 0.08, 0.06), 0.55, 0.55)
	# Soporte de suero.
	_cyl(Vector3(-8.2, 1.15, 3.85), 0.022, 1.9, metal)
	_cyl(Vector3(-8.2, 0.28, 3.85), 0.22, 0.03, metal)
	_box(Vector3(-8.2, 1.72, 3.85), Vector3(0.3, 0.03, 0.03), metal)
	_cyl(Vector3(-8.2, 1.50, 3.85), 0.06, 0.28, _mat("glass"))
	# Contención: grieta, cinta y aviso.
	_wall_decal(Vector3(-7.4, 1.55, 3.075), Vector2(1.7, 2.0), CRACK, Color(0.75, 0.92, 0.88), 0.0, 0.8)
	_sign("CONTENCIÓN FALLIDA", Vector3(-7.4, 2.95, 3.08), 15, Color(1.0, 0.35, 0.18))

	# Charcos verdes y goteo.
	_floor_decal(Vector3(-6.8, 0.018, 2.9), Vector2(2.4, 1.5), PUDDLE, Color(0.28, 0.85, 0.38), 0.15, 0.55)
	# Taquilla y cajas de investigación.
	_box(Vector3(-9.18, 0.36, 4.45), Vector3(0.55, 0.72, 0.55), dark)
	_box(Vector3(-9.18, 0.74, 4.45), Vector3(0.48, 0.04, 0.48), _mat("rust"))
	# Monitor caído.
	_box(Vector3(-4.25, 0.18, 1.55), Vector3(0.55, 0.34, 0.22), dark, Vector3(0, 32, 70))
	_quad(Vector3(-4.18, 0.26, 1.48), Vector2(0.42, 0.24), _mat("screen"), Vector3(-70, 32, 0))

func _extraction_details() -> void:
	var metal := _mat("metal_dirty")
	var dark := _mat("dark")
	# Cajas y carretes junto a la extracción.
	_box(Vector3(-2.7, 0.42, -11.4), Vector3(0.8, 0.84, 0.8), _mat("metal_dirty"))
	_box(Vector3(-2.65, 0.84, -11.4), Vector3(0.74, 0.04, 0.74), _mat("hazard"))
	_box(Vector3(2.55, 0.36, -11.0), Vector3(0.65, 0.72, 0.65), _mat("rust"))
	_cyl(Vector3(2.55, 0.55, -12.0), 0.48, 0.18, dark, Vector3(90, 0, 0))
	_cyl(Vector3(2.55, 0.55, -12.0), 0.30, 0.20, _mat("rust"), Vector3(90, 0, 0))
	# Barandilla de seguridad junto al pad.
	for x in [-2.0, 2.0]:
		_cyl(Vector3(x, 0.55, -10.4), 0.035, 1.1, metal)
	_box(Vector3(0, 1.08, -10.4), Vector3(4.0, 0.06, 0.06), _mat("warning_yellow"))
	_sign("PUNTO DE EXTRACCIÓN", Vector3(0, 2.25, -10.55), 15, Color(0.45, 1.0, 0.60), Vector3(0, 180, 0))
	_sign("MANTENGA LA ZONA DESPEJADA", Vector3(0, 2.02, -10.55), 9, Color(0.55, 0.78, 0.62), Vector3(0, 180, 0))
	# Baliza y cajas de herramientas.
	_emergency(Vector3(-2.55, 2.4, -11.7), PI, true)
	_box(Vector3(1.5, 0.12, -11.7), Vector3(0.8, 0.22, 0.5), _mat("warning_yellow"), Vector3(0, 20, 0))

func _narrative_damage() -> void:
	var dark := _mat("dark")
	# Panel de techo desprendido y cables colgando.
	var panel := _box(Vector3(0.9, 3.55, 4.1), Vector3(1.25, 0.06, 0.9), _mat("ceiling"), Vector3(-7, 14, 12))
	_cable(Vector3(1.2, 3.8, 4.2), Vector3(1.4, 2.7, 4.4), 0.018, _simple(Color(0.02, 0.02, 0.025)))
	_cable(Vector3(0.8, 3.75, 3.8), Vector3(1.0, 2.2, 3.2), 0.014, _simple(Color(0.18, 0.05, 0.03)))
	# Escombros en el laboratorio.
	for i in range(9):
		var x := -8.8 + i * 0.18
		_box(Vector3(x, 0.06, 1.1 + (i % 3) * 0.2), Vector3(0.22, 0.10, 0.16), _mat("rust"), Vector3(0, i * 19.0, 8))
	# Puerta interior dañada junto al laboratorio.
	_box(Vector3(-2.72, 1.0, 5.9), Vector3(0.08, 2.0, 0.9), dark, Vector3(0, 0, 4))
	_box(Vector3(-2.70, 1.0, 5.9), Vector3(0.02, 0.10, 0.7), _mat("warning_yellow"), Vector3(0, 0, 4))
	# Cartel de riesgo biológico y evacuación.
	_sign("RIESGO BIOLÓGICO", Vector3(-2.66, 2.55, 4.0), 12, Color(1.0, 0.62, 0.20), Vector3(0, 90, 0))
	_sign("EVACUACIÓN", Vector3(-2.66, 1.72, 2.7), 10, Color(0.55, 0.9, 0.58), Vector3(0, 90, 0))

func _atmosphere() -> void:
	# Haces volumétricos fríos y una niebla local muy sutil.
	for z in [6.0, 0.0, -6.0]:
		var spot := SpotLight3D.new()
		spot.position = Vector3(0, 3.7, z)
		spot.rotation_degrees = Vector3(-90, 0, 0)
		spot.light_color = Color(0.52, 0.72, 1.0)
		spot.light_energy = 0.42
		spot.spot_range = 7.5
		spot.spot_angle = 48.0
		spot.shadow_enabled = false
		spot.light_volumetric_fog_energy = 1.2
		add_child(spot)
	# Vapor de una tubería dañada.
	_steam(Vector3(-8.9, 2.25, 1.1), 1.0)
	_steam(Vector3(2.1, 2.2, -5.8), 0.8)
	# Papel y polvo ya existen en el nivel; aquí solo se añade un poco de niebla baja.
	var fog := FogVolume.new()
	var fog_mat := FogMaterial.new()
	fog_mat.density = 0.035
	fog_mat.albedo = Color(0.18, 0.28, 0.26)
	fog_mat.height_falloff = 0.8
	fog.size = Vector3(5.0, 1.2, 12.0)
	fog.position = Vector3(0, 0.65, 0.0)
	fog.material = fog_mat
	add_child(fog)

func _steam(pos: Vector3, amount: float) -> void:
	var particles := CPUParticles3D.new()
	particles.amount = maxi(3, int(7 * amount))
	particles.lifetime = 2.4
	particles.position = pos
	var quad := QuadMesh.new()
	quad.size = Vector2(0.7, 0.7)
	particles.mesh = quad
	var mat := _decal_material(SMOKE, Color(0.55, 0.62, 0.62), 0.16)
	particles.material_override = mat
	particles.direction = Vector3(0, 1, 0)
	particles.spread = 28.0
	particles.initial_velocity_min = 0.15
	particles.initial_velocity_max = 0.55
	particles.gravity = Vector3(0, 0.12, 0)
	particles.scale_amount_min = 0.5
	particles.scale_amount_max = 1.4
	add_child(particles)
