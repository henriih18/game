class_name FMSecurityMaterials
extends RefCounted

## Consolidación de materiales del sector de Seguridad para reducir draw
## calls sin tocar el GLB. El arte de Seguridad usa 123 materiales, muchos de
## ellos casi idénticos (negros mate, acero desnudo, metal blanco, verdes).
## La fusión estática agrupa por material y celda, así que cada material
## redundante cuesta draws en cada celda visible.
##
## Se aplica solo al subárbol `Sectors/SecurityArt`, antes de la fusión, con
## `set_surface_override_material`. `fm_static_merge` usa
## `get_active_material`, que respeta ese override. Los materiales originales
## siguen intactos en el GLB: esto es reversible con el interruptor
## `ENABLE_SECURITY_MATERIALS`.

## Canónicos: el material representante de cada familia. Se elige uno que ya
## existe en el sector para conservar sus texturas y factores originales.
const CANON_WHITE_METAL := "M_SH_Steel_Stainless"
const CANON_WHITE_MATTE := "M_SH_Paint_SecurityGreen"
const CANON_DARK_MATTE := "M_R21B_Paint_Dark"
const CANON_BARE_METAL := "M_R21B_Steel_Bare"
const CANON_DARK_METAL := "M_HERO_Steel_Dark"
const CANON_GREEN := "M_R21B_Paint_Green"
const CANON_OLIVE := "M_R21B_Paint_Olive"
const CANON_OFFWHITE := "M_R21B_Sign_White"
const CANON_CONCRETE := "M_R21B_Concrete"
const CANON_CEILING := "M_HERO_Ops_CeilingTile"

const REMAP := {
	# Metal blanco / cromo. Todos comparten blanco, metallic 1, roughness 1.
	"M_SH_Steel_Galv": CANON_WHITE_METAL,
	"M_SH_Steel_Dark": CANON_WHITE_METAL,
	"M_SH_Aluminum": CANON_WHITE_METAL,
	"M_SH_Brass": CANON_WHITE_METAL,
	# Blanco dielectrico (el GLB los importa sin factores: blanco mate).
	"M_SH_Rubber_Seal": CANON_WHITE_MATTE,
	"M_SH_Plastic_Black": CANON_WHITE_MATTE,
	"M_SH_Cable_Black": CANON_WHITE_MATTE,
	"M_SH_Paint_SecurityGreen": CANON_WHITE_MATTE,
	"M_SH_Paint_SafetyOrange": CANON_WHITE_MATTE,
	"M_SH_Sprinkler_Red": CANON_WHITE_MATTE,
	"M_SH_Diffuser_Off": CANON_WHITE_MATTE,
	"M_HERO_Gypsum": CANON_WHITE_MATTE,
	# Negro mate: plasticos, gomas, cables, pintura oscura y tapiceria.
	"M_HERO_Plastic": CANON_DARK_MATTE,
	"M_HERO_Rubber": CANON_DARK_MATTE,
	"M_R21B_Rubber": CANON_DARK_MATTE,
	"M_R21B_Cable_Black": CANON_DARK_MATTE,
	"M_R21B_Plastic": CANON_DARK_MATTE,
	"M_HERO_Paint_Dark": CANON_DARK_MATTE,
	"M_HERO_Ops_ChairShell": CANON_DARK_MATTE,
	"M_HERO_Ops_ChairFabric": CANON_DARK_MATTE,
	"M_R21B_Hazard_Black": CANON_DARK_MATTE,
	# Acero desnudo: cuatro tonos 0,46-0,52 con metallic 1.
	"M_HERO_Aluminum": CANON_BARE_METAL,
	"M_R21B_Aluminum": CANON_BARE_METAL,
	"M_HERO_Steel_Bare": CANON_BARE_METAL,
	# Acero oscuro estructural.
	"M_R21B_Steel_Dark": CANON_DARK_METAL,
	# Verdes y olivas de pintura industrial.
	"M_HERO_Paint_Green": CANON_GREEN,
	"M_R21B_Paint_GreenDark": CANON_GREEN,
	"M_HERO_Ops_PaintOliveDark": CANON_OLIVE,
	"M_HERO_Ops_PaintOlive": CANON_OLIVE,
	# Etiquetas, lienzos y conos: mismos blancos calidos.
	"M_R21B_Label": CANON_OFFWHITE,
	"M_HERO_Ops_Label": CANON_OFFWHITE,
	"M_R21B_Canvas": CANON_OFFWHITE,
	"M_R21D_ConeWhite": CANON_OFFWHITE,
	# Hormigon y placas de techo.
	"M_HERO_Concrete": CANON_CONCRETE,
	"M_R21C_CeilingTile": CANON_CEILING,
}


static func apply(root: Node3D) -> Dictionary:
	var stats := {"materials": 0, "surfaces": 0, "remapped": 0, "deduped": 0}
	if root == null:
		return stats
	# Primer material de cada nombre: sirve como canónico y deduplica las
	# entradas repetidas que el importador crea con sufijo .001.
	var by_name: Dictionary = {}
	for node in root.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi == null or mi.mesh == null:
			continue
		for i in mi.mesh.get_surface_count():
			var mat := mi.get_active_material(i)
			if mat == null:
				continue
			var mat_name := String(mat.resource_name)
			if mat_name.is_empty():
				continue
			if not by_name.has(mat_name):
				by_name[mat_name] = mat
	stats["materials"] = by_name.size()
	for node in root.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi == null or mi.mesh == null:
			continue
		for i in mi.mesh.get_surface_count():
			var mat := mi.get_active_material(i)
			if mat == null:
				continue
			var mat_name := String(mat.resource_name)
			stats["surfaces"] = int(stats["surfaces"]) + 1
			var target_name := String(REMAP.get(mat_name, mat_name))
			var target := by_name.get(target_name) as Material
			if target == null or target == mat:
				continue
			mi.set_surface_override_material(i, target)
			if target_name == mat_name:
				stats["deduped"] = int(stats["deduped"]) + 1
			else:
				stats["remapped"] = int(stats["remapped"]) + 1
	print("FM_LEVEL1_V06_SECURITY_MATERIALS materials=%d surfaces=%d remapped=%d deduped=%d" % [
		int(stats["materials"]), int(stats["surfaces"]),
		int(stats["remapped"]), int(stats["deduped"]),
	])
	return stats
