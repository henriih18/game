class_name FMStaticMerge
extends RefCounted

## Fusión runtime de mallas estáticas del arte de un sector.
##
## El arte del Nivel 1 se exporta desde Blender como cientos de MeshInstance3D
## sueltos (1.705 mallas, 2.991 superficies). Este helper agrupa las superficies
## por celda espacial + material + formato de vértices y las fusiona en un
## ArrayMesh por grupo. Las mallas originales se conservan en el árbol y se
## ocultan, de modo que:
##   - FMGLBCollision ya construyó sus colisiones antes de llamar aquí;
##   - los nombres y rutas de nodo que consultan las pruebas y la compuerta de
##     Seguridad siguen existiendo;
##   - `get_sector_mesh_count()` y los AABB de sector no cambian.
##
## No toca materiales, texturas, luces, colisiones, navegación ni scripts. Solo
## sustituye el dibujo de las mallas estáticas por mallas fusionadas.
##
## Reglas de seguridad:
##   - no fusiona mallas con nombre dinámico (compuerta R21C);
##   - no fusiona mallas cuyo AABB supere `max_diagonal` (suelos, techos y
##     conductos de decenas de metros): su AABB ya domina el culling;
##   - no fusiona mallas invisibles, con skin/skeleton, MultiMesh ni con
##     overrides o propiedades por instancia que la fusión no pueda reproducir
##     (material_override, material_overlay, custom_aabb, rangos de
##     visibilidad, capas, LOD bias, culling extra, GI dinámica);
##   - agrupa por formato de superficie para no mezclar atributos.

const DEFAULT_CELL_SIZE := 16.0
const DEFAULT_MAX_DIAGONAL := 30.0
const DYNAMIC_NAME_PREFIXES: Array[String] = ["R21C_HATCH"]


## Fusiona las mallas estáticas de `sector_root` en un nodo nuevo bajo `level`.
## Devuelve estadísticas y no lanza excepciones: si un grupo no se puede
## commitear, se deja el arte original visible.
static func merge_sector(
	level: Node3D,
	sector_root: Node3D,
	sector_id: String,
	options: Dictionary = {}
) -> Dictionary:
	var result := {
		"sector": sector_id,
		"merged_nodes": 0,
		"hidden_meshes": 0,
		"skipped_meshes": 0,
		"skipped_big": 0,
		"skipped_dynamic": 0,
		"skipped_nonuniform": 0,
		"skipped_transparent": 0,
		"source_surfaces": 0,
		"output_surfaces": 0,
		"failed_buckets": 0,
		"merge_ms": 0,
	}
	if level == null or sector_root == null:
		return result
	var started := Time.get_ticks_msec()
	var cell_size: float = maxf(2.0, float(options.get("cell_size", DEFAULT_CELL_SIZE)))
	var max_diagonal: float = maxf(4.0, float(options.get("max_diagonal", DEFAULT_MAX_DIAGONAL)))
	var skip_transparent: bool = bool(options.get("skip_transparent", true))
	var level_inverse := level.global_transform.affine_inverse()

	var buckets: Dictionary = {}
	var candidates: Array[MeshInstance3D] = []
	for node in sector_root.find_children("*", "MeshInstance3D", true, false):
		var instance := node as MeshInstance3D
		if instance == null or instance.mesh == null:
			result["skipped_meshes"] = int(result["skipped_meshes"]) + 1
			continue
		if not instance.visible or instance.skin != null or not instance.skeleton.is_empty():
			result["skipped_meshes"] = int(result["skipped_meshes"]) + 1
			continue
		# `surface_get_format` solo existe en ArrayMesh. Un PrimitiveMesh
		# (el techo BoxMesh del conector de Seguridad) abortaba la fusión de
		# todo el sector y dejaba sus 534 mallas sin agrupar.
		if not instance.mesh is ArrayMesh:
			result["skipped_meshes"] = int(result["skipped_meshes"]) + 1
			continue
		if _has_unsafe_instance_settings(instance):
			result["skipped_meshes"] = int(result["skipped_meshes"]) + 1
			continue
		if _is_dynamic_name(String(instance.name)):
			result["skipped_dynamic"] = int(result["skipped_dynamic"]) + 1
			continue
		# Una escala no uniforme o un determinante negativo cambia la dirección
		# de las normales y el orden de los triángulos. Son 13 mallas pequeñas:
		# se dejan intactas para no alterar speculares ni caras.
		if not _is_uniform_positive(instance.global_transform.basis):
			result["skipped_nonuniform"] = int(result["skipped_nonuniform"]) + 1
			continue
		var world_box: AABB = instance.global_transform * instance.mesh.get_aabb()
		if world_box.size.length() > max_diagonal:
			result["skipped_big"] = int(result["skipped_big"]) + 1
			continue

		var surface_count := instance.mesh.get_surface_count()
		if surface_count <= 0:
			result["skipped_meshes"] = int(result["skipped_meshes"]) + 1
			continue
		# Las superficies transparentes (polvo, calcomanías, cristales) se
		# ordenan por distancia. El llamador puede dejarlas intactas con
		# `skip_transparent`; en la medición actual fusionarlas no produjo
		# diferencias visibles y evitó ~95 draw calls en la vista de acceso.
		if skip_transparent and _has_transparent_surface(instance, surface_count):
			result["skipped_transparent"] = int(result["skipped_transparent"]) + 1
			continue
		var center := world_box.get_center()
		var cell_x := floori(center.x / cell_size)
		var cell_z := floori(center.z / cell_size)
		var local_transform := level_inverse * instance.global_transform
		var added := false
		for surface in range(surface_count):
			# `get_active_material` respeta los surface_override_material que
			# aplica el arte (p. ej. Z10 apaga la emisión de las luminarias sin
			# tocar el GLB). Usar `surface_get_material` devolvería el material
			# original y encendería esas luminarias al fusionarlas.
			var material := instance.get_active_material(surface)
			if material == null:
				continue
			var surface_format: int = instance.mesh.surface_get_format(surface)
			var key := "%d:%d:%d:%d" % [cell_x, cell_z, material.get_instance_id(), surface_format]
			var bucket: Dictionary = buckets.get(key, {})
			if bucket.is_empty():
				var surface_tool := SurfaceTool.new()
				surface_tool.begin(Mesh.PRIMITIVE_TRIANGLES)
				bucket = {
					"tool": surface_tool,
					"material": material,
					"surfaces": 0,
				}
				buckets[key] = bucket
			var tool := bucket["tool"] as SurfaceTool
			tool.append_from(instance.mesh, surface, local_transform)
			bucket["surfaces"] = int(bucket["surfaces"]) + 1
			result["source_surfaces"] = int(result["source_surfaces"]) + 1
			added = true
		if added:
			candidates.append(instance)

	if buckets.is_empty():
		result["merge_ms"] = Time.get_ticks_msec() - started
		return result

	var merged_root := Node3D.new()
	merged_root.name = "MergedArt_%s" % sector_id
	level.add_child(merged_root)
	var merged_count := 0
	var failed := 0
	for key in buckets:
		var bucket: Dictionary = buckets[key]
		var tool := bucket["tool"] as SurfaceTool
		var material := bucket["material"] as Material
		tool.set_material(material)
		var mesh := tool.commit()
		if mesh == null or mesh.get_surface_count() <= 0:
			failed += 1
			continue
		var merged_instance := MeshInstance3D.new()
		merged_instance.name = "Merge_%s_%03d" % [sector_id, merged_count]
		merged_instance.mesh = mesh
		merged_instance.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
		merged_root.add_child(merged_instance)
		merged_count += 1
		result["output_surfaces"] = int(result["output_surfaces"]) + 1

	# Las originales solo se ocultan si todos los grupos llegaron a commitearse.
	# Un fallo de SurfaceTool deja el arte original visible: es preferible
	# duplicar dibujo durante una prueba a perder arte en el nivel.
	if failed == 0 and merged_count > 0:
		for instance in candidates:
			instance.visible = false
		result["hidden_meshes"] = candidates.size()
	else:
		for child in merged_root.get_children():
			child.queue_free()
		merged_root.queue_free()
		merged_count = 0
		result["output_surfaces"] = 0
	result["merged_nodes"] = merged_count
	result["failed_buckets"] = failed
	if merged_count == 0 and is_instance_valid(merged_root):
		merged_root.queue_free()
	result["merge_ms"] = Time.get_ticks_msec() - started
	return result


static func _is_dynamic_name(node_name: String) -> bool:
	var upper := node_name.to_upper()
	for prefix in DYNAMIC_NAME_PREFIXES:
		if upper.begins_with(prefix):
			return true
	return false



## Propiedades por instancia que la fusión no puede reproducir. Si alguna
## está activa, la malla se deja intacta.
static func _has_unsafe_instance_settings(instance: MeshInstance3D) -> bool:
	if instance.material_override != null or instance.material_overlay != null:
		return true
	if not is_zero_approx(instance.transparency):
		return true
	if instance.custom_aabb != AABB():
		return true
	if instance.visibility_range_begin > 0.0 or instance.visibility_range_end > 0.0:
		return true
	if instance.layers != 1:
		return true
	if not is_equal_approx(instance.lod_bias, 1.0):
		return true
	if not is_zero_approx(instance.extra_cull_margin):
		return true
	if instance.ignore_occlusion_culling:
		return true
	if instance.gi_mode == GeometryInstance3D.GI_MODE_DYNAMIC:
		return true
	return false


static func _is_uniform_positive(basis: Basis) -> bool:
	var sx := basis.x.length()
	var sy := basis.y.length()
	var sz := basis.z.length()
	if absf(sx - sy) > 0.001 or absf(sx - sz) > 0.001:
		return false
	return basis.determinant() > 0.0


static func _has_transparent_surface(instance: MeshInstance3D, surface_count: int) -> bool:
	for surface in range(surface_count):
		var material := instance.get_active_material(surface) as BaseMaterial3D
		if material != null and material.transparency != BaseMaterial3D.TRANSPARENCY_DISABLED:
			return true
	return false
