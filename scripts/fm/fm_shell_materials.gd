class_name FMShellMaterials
extends RefCounted

## Materiales compartidos para el shell blockout de pasillos, conectores y
## escaleras. Las mallas del shell no tienen UVs, así que se usa proyección
## triplanar en espacio de mundo. Los materiales se aplican con
## `material_override` antes de la fusión estática, que respeta el override.
##
## Solo se tocan mallas `SM_L1_*` del shell; el arte de las salas y los props
## conservan sus materiales originales.

const WALL_BC := "res://assets/art/fm/z10_hero/surfaces/T_Z10_WALL_PLASTER_2K_BC.png"
# El set de shell solo trae BC + ORM (y una máscara R aparte). No hay mapa
# normal, así que se deja vacío en vez de apuntar a un recurso inexistente.
const WALL_N := ""
const WALL_ORM := "res://assets/art/fm/z10_hero/surfaces/T_Z10_WALL_PLASTER_2K_ORM.png"
const FLOOR_BC := "res://assets/art/fm/z10_hero/surfaces/T_Z10_FLOOR_CONCRETE_2K_BC.png"
const FLOOR_N := ""
const FLOOR_ORM := "res://assets/art/fm/z10_hero/surfaces/T_Z10_FLOOR_CONCRETE_2K_ORM.png"

const SHELL_PREFIXES: Array[String] = [
	"SM_L1_Corridor_", "SM_L1_Conn_", "SM_L1_Stair_",
	"SM_L1_Zone11_", "SM_L1_Zone12",
]

static var _cache: Dictionary = {}


static func apply(level: Node3D) -> Dictionary:
	var stats := {"wall": 0, "floor": 0, "ceiling": 0, "skipped": 0}
	if level == null:
		return stats
	var wall := _material("M_Shell_Wall", WALL_BC, WALL_N, WALL_ORM,
		Color(0.46, 0.54, 0.50), 0.24, 0.55)
	var floor_mat := _material("M_Shell_Floor", FLOOR_BC, FLOOR_N, FLOOR_ORM,
		Color(0.54, 0.56, 0.53), 0.24, 0.45)
	var ceiling := _material("M_Shell_Ceiling", WALL_BC, WALL_N, WALL_ORM,
		Color(0.20, 0.23, 0.22), 0.22, 0.40)
	for node in level.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi == null or mi.mesh == null:
			continue
		# Las copias ocultas del blockout (duplicados de Z10) no necesitan
		# material: además, el merge las cuenta como omitidas.
		if not mi.visible:
			continue
		var mesh_name := String(mi.name)
		if not _is_shell(mesh_name):
			continue
		var source := _source_material_name(mi)
		var chosen: StandardMaterial3D = null
		var key := ""
		if source.contains("Wall_Corridor") or source.contains("Wall_Blockout"):
			chosen = wall
			key = "wall"
		elif source.contains("Corridor_Floor"):
			chosen = floor_mat
			key = "floor"
		elif source.contains("Ceiling_Blockout"):
			chosen = ceiling
			key = "ceiling"
		else:
			# Peldaños y mesetas conservan su material claro original: con la
			# textura oscura perdían legibilidad y solo se veían las bandas.
			stats["skipped"] = int(stats["skipped"]) + 1
			continue
		mi.material_override = chosen
		stats[key] = int(stats[key]) + 1
	print("FM_LEVEL1_V06_SHELL_MATERIALS wall=%d floor=%d ceiling=%d skipped=%d" % [
		int(stats["wall"]), int(stats["floor"]), int(stats["ceiling"]),
		int(stats["skipped"]),
	])
	return stats


static func _is_shell(mesh_name: String) -> bool:
	for prefix in SHELL_PREFIXES:
		if mesh_name.begins_with(prefix):
			return true
	return false


static func _source_material_name(mi: MeshInstance3D) -> String:
	if mi.mesh.get_surface_count() <= 0:
		return ""
	var mat := mi.mesh.surface_get_material(0)
	if mat == null:
		return ""
	var name := String(mat.resource_name)
	if name.is_empty():
		name = String(mat.get("resource_path")).get_file()
	return name


static func _material(name: String, bc_path: String, n_path: String, orm_path: String,
		tint: Color, triplanar_scale: float, normal_strength: float) -> StandardMaterial3D:
	if _cache.has(name):
		return _cache[name]
	var mat := StandardMaterial3D.new()
	mat.resource_name = name
	var bc := load(bc_path) as Texture2D
	var normal: Texture2D = null
	if not n_path.is_empty():
		normal = load(n_path) as Texture2D
	var orm := load(orm_path) as Texture2D
	mat.albedo_texture = bc
	mat.albedo_color = tint
	mat.normal_enabled = normal != null
	mat.normal_texture = normal
	mat.normal_scale = normal_strength
	mat.orm_texture = orm
	mat.roughness = 0.86
	mat.metallic = 0.0
	mat.metallic_specular = 0.35
	mat.uv1_triplanar = true
	mat.uv1_world_triplanar = true
	mat.uv1_scale = Vector3(triplanar_scale, triplanar_scale, triplanar_scale)
	mat.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
	_cache[name] = mat
	return mat
