class_name FMCreatureModels
extends RefCounted

## Modelos procedurales de criaturas para el vertical slice.
## Son recursos independientes: no usan las imágenes de referencia como textura.
## El Vigilante y el Imitador respetan las siluetas y rasgos de modelos-referencia.png.

const FLESH_ALBEDO := preload("res://assets/art/fm/flesh_albedo.png")
const FLESH_NORMAL := preload("res://assets/art/fm/flesh_normal.png")
const FLESH_ROUGHNESS := preload("res://assets/art/fm/flesh_roughness.png")
const BONE_ALBEDO := preload("res://assets/art/fm/bone_albedo.png")
const CLOTH_ALBEDO := preload("res://assets/art/fm/cloth_albedo.png")

static func build_vigilante(parent: Node3D) -> Dictionary:
	return _build_humanoid(parent, false)

static func build_imitator(parent: Node3D) -> Dictionary:
	return _build_humanoid(parent, true)

static func _build_humanoid(parent: Node3D, imitator: bool) -> Dictionary:
	var root := Node3D.new()
	root.name = "ImitadorVisual" if imitator else "VigilanteVisual"
	parent.add_child(root)

	var tint := Color(0.36, 0.42, 0.38, 1.0) if imitator else Color(0.30, 0.19, 0.14, 1.0)
	var skin := _skin_material(tint)
	var bone := _simple_material(BONE_ALBEDO, Color(0.74, 0.68, 0.55), 0.76)
	var bone_dim := _simple_material(BONE_ALBEDO, Color(0.34, 0.31, 0.25), 0.92)
	var cloth := _simple_material(CLOTH_ALBEDO, Color(0.11, 0.09, 0.08), 0.97)
	var mouth := StandardMaterial3D.new()
	mouth.albedo_color = Color(0.004, 0.002, 0.002, 1.0)
	mouth.roughness = 0.84
	mouth.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED

	# Proporciones: el Imitador es más delgado y de cabeza grande; el Vigilante
	# tiene el torso más ancho, púas y brazos desproporcionadamente largos.
	var body := Node3D.new()
	body.name = "Body"
	root.add_child(body)
	var leg_top := 1.10 if imitator else 1.16
	var shoulder_y := 2.10 if imitator else 2.22
	var head_y := 2.42 if imitator else 2.44

	# Torso orgánico de una sola pieza: caja torácica ancha, cintura hundida y
	# hombros estrechos. Evita el aspecto de cápsulas apiladas.
	var torso_rings := [
		Vector4(1.02, 0.135 if imitator else 0.150, 0.105 if imitator else 0.118, 0.0),
		Vector4(1.20, 0.150 if imitator else 0.168, 0.118 if imitator else 0.132, 0.0),
		Vector4(1.42, 0.115 if imitator else 0.128, 0.092 if imitator else 0.102, -0.01),
		Vector4(1.68, 0.185 if imitator else 0.205, 0.132 if imitator else 0.148, -0.02),
		Vector4(1.92, 0.205 if imitator else 0.228, 0.148 if imitator else 0.165, -0.035),
		Vector4(2.12, 0.155 if imitator else 0.172, 0.118 if imitator else 0.130, -0.055),
		Vector4(2.26, 0.092 if imitator else 0.102, 0.080 if imitator else 0.088, -0.080),
	]
	_organic_torso(body, torso_rings, skin)
	# Jirones de tela alrededor de la cintura, sin una cápsula sólida.
	_box(body, Vector3(0, 1.27, -0.185), Vector3(0.36, 0.055, 0.018), cloth)
	_box(body, Vector3(0, 1.27, 0.185), Vector3(0.34, 0.050, 0.016), cloth)
	for side in [-1.0, 1.0]:
		_box(body, Vector3(0.215 * side, 1.26, 0.0), Vector3(0.018, 0.055, 0.30), cloth)
		var strip := _box(body, Vector3(0.10 * side, 1.04, -0.17), Vector3(0.055, 0.30 + 0.08 * (1.0 + side), 0.012), cloth)
		strip.rotation_degrees.z = 4.0 * side

	# Costillas apenas insinuadas bajo la piel; el Imitador conserva un torso liso.
	if not imitator:
		for i in range(4):
			var y := 1.63 + i * 0.12
			var spread := 0.148 + i * 0.009
			for side in [-1.0, 1.0]:
				_limb(body, Vector3(0.010, y, -0.165), Vector3(spread * side, y - 0.045, -0.132), 0.009, bone_dim)
		_capsule(body, Vector3(0, 1.82, -0.158), 0.010, 0.44, bone_dim, Vector3(1.0, 1.0, 1.0))
		for side in [-1.0, 1.0]:
			_limb(body, Vector3(0.02 * side, 2.06, -0.135), Vector3(0.30 * side, 2.04, -0.09), 0.011, bone_dim)

	# Columna y púas dorsales.
	for i in range(5):
		var sy := 1.48 + i * 0.17
		_cone(body, Vector3(0, sy, 0.22), Vector3(0, 0.30, 0.95), 0.22 + i * 0.025, 0.048, bone)

	if not imitator:
		for side in [-1.0, 1.0]:
			_cone(body, Vector3(0.31 * side, 2.20, 0.02), Vector3(0.55 * side, 0.45, -0.05), 0.40, 0.042, bone)
			_cone(body, Vector3(0.45 * side, 2.06, 0.06), Vector3(0.72 * side, 0.62, 0.10), 0.28, 0.032, bone)
			_cone(body, Vector3(0.24 * side, 1.78, 0.17), Vector3(0.45 * side, 0.52, 0.72), 0.23, 0.040, bone)

	# Piernas largas y delgadas.
	for side in [-1.0, 1.0]:
		var hip := Vector3(0.15 * side, leg_top, 0.0)
		var knee := Vector3(0.20 * side, 0.58, 0.055)
		var ankle := Vector3(0.22 * side, 0.10, -0.025)
		_tapered_limb(body, hip, knee, 0.086 if imitator else 0.094, 0.060 if imitator else 0.068, skin)
		_tapered_limb(body, knee, ankle, 0.058 if imitator else 0.065, 0.040 if imitator else 0.047, skin)
		_sphere(body, knee, 0.060 if imitator else 0.068, skin, Vector3(1.0, 0.86, 1.0))
		_capsule(body, Vector3(0.23 * side, 0.070, -0.105), 0.070, 0.32, skin, Vector3(0.90, 0.46, 1.85))
		for toe in range(3):
			_capsule(body, Vector3(0.23 * side + (toe - 1) * 0.043, 0.050, -0.270), 0.022, 0.14, skin, Vector3(0.9, 0.5, 1.0))

	# Brazos articulados como grupos para poder animarlos.
	var arms: Array[Node3D] = []
	for side in [-1.0, 1.0]:
		var arm := Node3D.new()
		arm.name = "BrazoIzq" if side < 0 else "BrazoDer"
		arm.position = Vector3(0.36 * side, shoulder_y, -0.05)
		body.add_child(arm)
		arms.append(arm)
		var elbow := Vector3(0.22 * side, -0.62, -0.16)
		var wrist := Vector3(0.30 * side, -1.62 if imitator else -1.56, -0.30)
		_tapered_limb(arm, Vector3.ZERO, elbow, 0.068 if imitator else 0.080, 0.048 if imitator else 0.057, skin)
		_tapered_limb(arm, elbow, wrist, 0.045 if imitator else 0.054, 0.032 if imitator else 0.039, skin)
		_sphere(arm, elbow, 0.050 if imitator else 0.058, skin, Vector3(1.0, 0.84, 1.0))
		# Púas en el antebrazo (solo Vigilante).
		if not imitator:
			_cone(arm, elbow + Vector3(0.10 * side, -0.10, 0.03), Vector3(0.50 * side, -0.35, 0.10), 0.20, 0.040, bone)
			_cone(arm, elbow + Vector3(0.08 * side, -0.28, 0.02), Vector3(0.55 * side, -0.20, 0.15), 0.16, 0.035, bone)
		var hand := Node3D.new()
		hand.position = wrist + Vector3(0, -0.09, -0.04)
		arm.add_child(hand)
		_capsule(hand, Vector3.ZERO, 0.090, 0.26, skin, Vector3(0.90, 1.0, 0.50))
		for finger in range(4):
			var fx: float = (-0.075 + finger * 0.050) * side
			var base := Vector3(fx, -0.10, -0.005)
			var tip := base + Vector3(fx * 0.42, -0.44 - finger * 0.020, -0.10)
			_limb(hand, base, tip, 0.022, skin)
			_cone(hand, tip, Vector3(0, -0.52, -0.86), 0.09, 0.017, bone_dim)
		var thumb_base := Vector3(-0.09 * side, -0.07, -0.02)
		var thumb_tip := thumb_base + Vector3(-0.10 * side, -0.23, -0.10)
		_limb(hand, thumb_base, thumb_tip, 0.030, skin)
		_cone(hand, thumb_tip, Vector3(-0.25 * side, -0.40, -0.82), 0.09, 0.020, bone_dim)

	# Cuello y cabeza alargada, unidos sin hueco visible.
	_capsule(body, Vector3(0, 2.22, -0.08), 0.100, 0.44, skin, Vector3(0.86, 1.0, 0.86))
	var head := Node3D.new()
	head.name = "Head"
	head.position = Vector3(0, head_y - 0.05, -0.17)
	head.rotation_degrees.x = -8.0
	body.add_child(head)
	_capsule(head, Vector3(0, 0.24, 0.0), 0.142 if imitator else 0.148, 0.78, skin, Vector3(0.98, 1.18, 0.86))
	if not imitator:
		for side in [-1.0, 1.0]:
			_sphere(head, Vector3(0.060 * side, 0.31, -0.145), 0.014, mouth, Vector3(1.10, 0.42, 0.18))

	# Boca vertical: abertura negra y estrecha integrada en la cara.
	var jaw := Node3D.new()
	jaw.name = "Jaw"
	jaw.position = Vector3(0, 0.10, -0.155)
	head.add_child(jaw)
	_capsule(jaw, Vector3(0, 0.02, 0.0), 0.043, 0.48, mouth, Vector3(0.86, 1.0, 0.20))
	for side in [-1.0, 1.0]:
		for tooth in range(2):
			var ty := 0.135 - tooth * 0.150
			_cone(jaw, Vector3(0.030 * side, ty, -0.006), Vector3(-0.46 * side, 0.0, -0.50), 0.030, 0.007, bone)
	for side in [-1.0, 1.0]:
		_cone(head, Vector3(0.026 * side, 0.245, -0.170), Vector3(-0.42 * side, -0.10, -0.56), 0.026, 0.006, bone)

	# Mentón y mejillas suaves para integrar la boca en el cráneo.
	_sphere(head, Vector3(0, -0.01, -0.115), 0.082, skin, Vector3(1.0, 0.75, 0.46))
	for side in [-1.0, 1.0]:
		_sphere(head, Vector3(0.100 * side, 0.13, -0.125), 0.060, skin, Vector3(0.90, 1.0, 0.42))

	# Iluminación interna muy tenue: hace legible la cara en pasillos oscuros.
	var glow := OmniLight3D.new()
	glow.light_color = Color(0.78, 0.58, 0.44) if not imitator else Color(0.58, 0.82, 0.66)
	glow.light_energy = 0.02
	glow.omni_range = 0.62 if imitator else 0.72
	glow.shadow_enabled = false
	glow.position = Vector3(0, 1.86, -0.24)
	body.add_child(glow)

	# Sombra de contacto.
	var shadow := MeshInstance3D.new()
	var shadow_mesh := CylinderMesh.new()
	shadow_mesh.top_radius = 0.42 if imitator else 0.52
	shadow_mesh.bottom_radius = shadow_mesh.top_radius
	shadow_mesh.height = 0.01
	shadow_mesh.radial_segments = 18
	shadow.mesh = shadow_mesh
	var shadow_mat := StandardMaterial3D.new()
	shadow_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	shadow_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	shadow_mat.albedo_color = Color(0, 0, 0, 0.38)
	shadow.material_override = shadow_mat
	shadow.position.y = 0.012
	root.add_child(shadow)

	if imitator:
		root.scale = Vector3(0.84, 0.84, 0.84)

	return {
		"root": root,
		"body": body,
		"head": head,
		"jaw": jaw,
		"left_arm": arms[0],
		"right_arm": arms[1],
		"glow": glow,
	}


static func _skin_material(tint: Color) -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.albedo_texture = FLESH_ALBEDO
	mat.albedo_color = tint
	mat.normal_enabled = true
	mat.normal_texture = FLESH_NORMAL
	mat.normal_scale = 0.85
	mat.roughness_texture = FLESH_ROUGHNESS
	mat.roughness = 0.90
	mat.metallic = 0.0
	mat.rim_enabled = true
	mat.rim = 0.18
	mat.rim_tint = 0.42
	mat.uv1_scale = Vector3(2.2, 2.2, 2.2)
	mat.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
	return mat


static func _simple_material(texture: Texture2D, tint: Color, roughness: float) -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.albedo_texture = texture
	mat.albedo_color = tint
	mat.roughness = roughness
	mat.uv1_scale = Vector3(2.0, 2.0, 2.0)
	return mat


static func _mesh(parent: Node3D, mesh: Mesh, mat: Material, pos: Vector3,
		rot_deg := Vector3.ZERO, scl := Vector3.ONE) -> MeshInstance3D:
	var node := MeshInstance3D.new()
	node.mesh = mesh
	node.material_override = mat
	node.position = pos
	node.rotation_degrees = rot_deg
	node.scale = scl
	parent.add_child(node)
	return node


static func _capsule(parent: Node3D, pos: Vector3, radius: float, height: float,
		mat: Material, scl := Vector3.ONE) -> MeshInstance3D:
	var mesh := CapsuleMesh.new()
	mesh.radius = radius
	mesh.height = maxf(height, radius * 2.02)
	mesh.radial_segments = 10
	mesh.rings = 5
	return _mesh(parent, mesh, mat, pos, Vector3.ZERO, scl)


static func _sphere(parent: Node3D, pos: Vector3, radius: float, mat: Material,
		scl := Vector3.ONE) -> MeshInstance3D:
	var mesh := SphereMesh.new()
	mesh.radius = radius
	mesh.height = radius * 2.0
	mesh.radial_segments = 10
	mesh.rings = 6
	return _mesh(parent, mesh, mat, pos, Vector3.ZERO, scl)


static func _box(parent: Node3D, pos: Vector3, size: Vector3, mat: Material) -> MeshInstance3D:
	var mesh := BoxMesh.new()
	mesh.size = size
	return _mesh(parent, mesh, mat, pos)


static func _cone(parent: Node3D, pos: Vector3, direction: Vector3, length: float,
		radius: float, mat: Material) -> MeshInstance3D:
	var mesh := CylinderMesh.new()
	mesh.top_radius = 0.0
	mesh.bottom_radius = radius
	mesh.height = length
	mesh.radial_segments = 6
	var node := _mesh(parent, mesh, mat, pos)
	node.quaternion = Quaternion(Vector3.UP, direction.normalized())
	return node


static func _organic_torso(parent: Node3D, rings: Array, mat: Material) -> MeshInstance3D:
	var sides := 12
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	for i in range(rings.size()):
		var ring: Vector4 = rings[i]
		for s in range(sides):
			var angle := TAU * float(s) / float(sides)
			st.set_uv(Vector2(float(s) / sides, float(i) / maxf(1.0, float(rings.size() - 1))))
			st.add_vertex(Vector3(cos(angle) * ring.y, ring.x, sin(angle) * ring.z + ring.w))
	for i in range(rings.size() - 1):
		for s in range(sides):
			var s2 := (s + 1) % sides
			var a := i * sides + s
			var b := i * sides + s2
			var c := (i + 1) * sides + s
			var d := (i + 1) * sides + s2
			st.add_index(a)
			st.add_index(c)
			st.add_index(b)
			st.add_index(b)
			st.add_index(c)
			st.add_index(d)
	st.generate_normals()
	var instance := MeshInstance3D.new()
	instance.name = "TorsoOrganico"
	instance.mesh = st.commit()
	instance.material_override = mat
	parent.add_child(instance)
	return instance


static func _tapered_limb(parent: Node3D, a: Vector3, b: Vector3, r1: float, r2: float, mat: Material) -> MeshInstance3D:
	var delta := b - a
	var length := delta.length()
	var mesh := CylinderMesh.new()
	mesh.top_radius = r2
	mesh.bottom_radius = r1
	mesh.height = maxf(length, 0.01)
	mesh.radial_segments = 9
	mesh.rings = 1
	var node := _mesh(parent, mesh, mat, (a + b) * 0.5)
	if length > 0.0001:
		node.quaternion = Quaternion(Vector3.UP, delta / length)
	return node


static func _limb(parent: Node3D, a: Vector3, b: Vector3, radius: float, mat: Material) -> MeshInstance3D:
	var delta := b - a
	var length := delta.length()
	var mesh := CapsuleMesh.new()
	mesh.radius = radius
	mesh.height = maxf(length, radius * 2.02)
	mesh.radial_segments = 8
	mesh.rings = 4
	var node := _mesh(parent, mesh, mat, (a + b) * 0.5)
	if length > 0.0001:
		node.quaternion = Quaternion(Vector3.UP, delta / length)
	return node
