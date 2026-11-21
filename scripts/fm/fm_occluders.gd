class_name FMOccluders
extends RefCounted

## Oclusión estática del shell del Nivel 1.
##
## Godot necesita occluders explícitos: los muros no ocluyen por sí solos.
## Este helper construye un único `ArrayOccluder3D` con los triángulos reales
## de los muros/techos/suelos del shell (no cajas envolventes), de modo que
## las aberturas de puertas y los vanos siguen siendo visibles. Se ejecuta
## antes de la fusión estática, que oculta las mallas originales.

const SHELL_PREFIXES: Array[String] = [
	"SM_L1_Corridor_", "SM_L1_Conn_", "SM_L1_Stair_",
	"SM_L1_Zone11_", "SM_L1_Zone12",
]

static var _last_stats: Dictionary = {}


static func apply(level: Node3D) -> Dictionary:
	var stats := {"meshes": 0, "vertices": 0, "triangles": 0, "skipped": 0}
	if level == null:
		return stats
	var vertices := PackedVector3Array()
	var indices := PackedInt32Array()
	var base := level.global_transform.affine_inverse()
	for node in level.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi == null or mi.mesh == null or not mi.visible:
			stats["skipped"] = int(stats["skipped"]) + 1
			continue
		if not _is_shell(String(mi.name)):
			continue
		if not mi.mesh is ArrayMesh:
			stats["skipped"] = int(stats["skipped"]) + 1
			continue
		var xform := base * mi.global_transform
		for surface in mi.mesh.get_surface_count():
			var arrays := (mi.mesh as ArrayMesh).surface_get_arrays(surface)
			var verts: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
			if verts.is_empty():
				continue
			var offset := vertices.size()
			for vertex in verts:
				vertices.append(xform * vertex)
			var surface_indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
			if surface_indices.is_empty():
				for i in range(0, verts.size() - 2, 3):
					indices.append(offset + i)
					indices.append(offset + i + 1)
					indices.append(offset + i + 2)
			else:
				for index in surface_indices:
					indices.append(offset + index)
		stats["meshes"] = int(stats["meshes"]) + 1
	stats["vertices"] = vertices.size()
	stats["triangles"] = indices.size() / 3
	if indices.is_empty():
		_last_stats = stats
		return stats
	var occluder := ArrayOccluder3D.new()
	occluder.vertices = vertices
	occluder.indices = indices
	var instance := OccluderInstance3D.new()
	instance.name = "ShellOccluders"
	instance.occluder = occluder
	level.add_child(instance)
	_last_stats = stats
	print("FM_LEVEL1_V06_OCCLUDERS meshes=%d vertices=%d triangles=%d skipped=%d" % [
		int(stats["meshes"]), int(stats["vertices"]),
		int(stats["triangles"]), int(stats["skipped"]),
	])
	return stats


static func _is_shell(mesh_name: String) -> bool:
	if not (mesh_name.contains("_Wall_") or mesh_name.ends_with("_Wall")
			or mesh_name.contains("_Floor") or mesh_name.contains("_Ceiling")):
		return false
	for prefix in SHELL_PREFIXES:
		if mesh_name.begins_with(prefix):
			return true
	return false
