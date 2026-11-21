class_name FMGLBCollision
extends RefCounted

## Constructor de colisiones estáticas para GLB cargados en runtime.
##
## Regla principal: una malla compuesta NO debe generar una caja con su AABB
## completo, porque puede bloquear huecos (portales, marcos, aros de risers).
## Se usa trimesh para esas mallas y para geometría grande con muchos vértices.
## El resto se simplifica a cajas.

const SKIP_TOKENS: Array[String] = [
	"BLOOD", "PAPER", "DECAL", "SIGN", "TEXT", "SCREEN", "LIGHT",
	"LAMP", "BULB", "LED", "CABLE", "WIRE", "HOSE", "CORD", "ROPE",
	"SMOKE", "SPRINK", "ARROW", "HAZ", "RUG", "MAT", "CARPET",
	"FOLIAGE", "LOOT", "TRAP", "EXTRACT", "RING", "TRIGGER",
	"MARKER", "BASEBOARD", "WAINSCOT", "TRIM", "SKIRT", "PLATE",
	"FLOOR_LINE", "FLOOR_SIGN", "FLOORPAPER", "DIFFUSER",
	"GRILLE", "VENT_SLAT", "TRAY_RAIL", "RUNG",
	"WALLSTAIN", "STORE_STAIN", "DIS_WATER", "DIS_OIL", "DIS_HAND",
	"GRIME", "DAMP_PATCH",
]

## Mallas que deben usar trimesh aunque su AABB sea pequeño.
const COMPOUND_TOKENS: Array[String] = [
	"PORTAL", "FRAME", "DOORFRAME", "RISERIDENTIFICATION",
]

const LARGE_VOLUME := 8.0
const LARGE_VERTEX_COUNT := 300


static func build(parent: Node3D, root: Node3D, bounds: AABB) -> Dictionary:
	var body := StaticBody3D.new()
	body.name = "StaticCollision"
	body.collision_layer = 1
	body.collision_mask = 0
	parent.add_child(body)
	# Mantener el cuerpo en el origen del mundo aunque el padre esté rotado.
	body.top_level = true

	var seen := {}
	var count := 0
	var trim_count := 0

	for node in root.find_children("*", "MeshInstance3D", true, false):
		var mesh_instance := node as MeshInstance3D
		if mesh_instance == null or mesh_instance.mesh == null:
			continue
		var upper := mesh_instance.name.to_upper()
		if _should_skip(upper):
			continue

		var box: AABB = mesh_instance.global_transform * mesh_instance.get_aabb()
		if not box.intersects(bounds):
			continue
		var size := box.size
		if size.y < 0.10:
			# Las losas/superficies planas también deben colisionar. Se les da
			# un grosor mínimo de 4 cm para que el raycast y la cápsula las
			# detecten; las calcomanías y alfombras ya se filtran por token.
			if maxf(size.x, size.z) < 1.0:
				continue
			var thin_size := Vector3(size.x, maxf(size.y, 0.04), size.z)
			_add_box(body, box.get_center(), thin_size)
			count += 1
			continue
		if maxf(size.x, size.z) < 0.24:
			continue
		if size.length() > 70.0:
			continue

		if _use_trimesh(upper, box, mesh_instance.mesh):
			var trim_shape := mesh_instance.mesh.create_trimesh_shape()
			if trim_shape != null:
				var trim_collider := CollisionShape3D.new()
				trim_collider.shape = trim_shape
				trim_collider.transform = mesh_instance.global_transform
				body.add_child(trim_collider)
				trim_count += 1
				count += 1
			continue

		var key := "%.2f|%.2f|%.2f|%.2f|%.2f|%.2f" % [
			box.position.x, box.position.y, box.position.z,
			size.x, size.y, size.z,
		]
		if seen.has(key):
			continue
		seen[key] = true
		_add_box(body, box.get_center(), size)
		count += 1

	return {
		"body": body,
		"count": count,
		"trimesh": trim_count,
	}


static func _should_skip(upper: String) -> bool:
	for token in SKIP_TOKENS:
		if token in upper:
			return true
	return false


static func _use_trimesh(upper: String, box: AABB, mesh: Mesh) -> bool:
	for token in COMPOUND_TOKENS:
		if token in upper:
			return true
	if box.get_volume() > LARGE_VOLUME and _vertex_count(mesh) > LARGE_VERTEX_COUNT:
		return true
	return false


static func _vertex_count(mesh: Mesh) -> int:
	var total := 0
	for surface in range(mesh.get_surface_count()):
		total += mesh.surface_get_array_len(surface)
	if total > 0:
		return total
	return mesh.get_faces().size()


static func _add_box(body: StaticBody3D, center: Vector3, size: Vector3) -> void:
	var shape := BoxShape3D.new()
	shape.size = size
	var collider := CollisionShape3D.new()
	collider.shape = shape
	collider.position = center
	body.add_child(collider)
