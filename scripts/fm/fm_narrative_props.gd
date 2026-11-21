extends Node3D

## FRECUENCIA MUERTA — anclajes narrativos del vertical slice Z10 → Recepción.
##
## Construye ocho conjuntos de props narrativos sobre geometría ya existente:
##   N1  Mostrador de recepción
##   N2  Sala de espera
##   N3  Taquillas del personal
##   N4  Control de seguridad
##   N5  Umbral de entrada
##   N6  Pasillo central / rastro de arrastre
##   N7  Extracción / descontaminación
##   N8  Enlace de servicio Z10
##
## Este nodo es HERMANO de Z10Art y ReceptionArt, nunca hijo: FMGLBCollision
## recorre los GLB de arte y añadiría colisiones a cualquier malla que quedase
## dentro de ellos. Aquí solo se usan Node3D, MeshInstance3D y Label3D. No hay
## colisiones, luces, áreas, interactables ni armas.
##
## Se reutilizan mallas reales de Recepción (portapapeles, papeles, sillas)
## mediante nuevas MeshInstance3D que comparten el mesh importado. El resto es
## geometría PBR de detalle construida en runtime.
##
## Pase de materiales: los metales y la goma usan sets PBR ya existentes del
## proyecto; tela, cuero, papel y plástico reciben micro-normales de ruido.
## Las UV son triplanar para no exigir unwrap de las primitivas. No se crean
## assets externos ni se modifican los GLB.

const GROUP_NARRATIVE := "fm_narrative"
const ART_TEX := "res://assets/art/fm/"
const CONNECTOR_TEX := ART_TEX + "generated/conector/"

## Ruta real recorrida por el test end-to-end (x, z). Los anclajes deben quedar
## fuera del eje jugable para no bloquear la navegación ni las capturas.
const Z10_ROUTE := [
	Vector2(47.0, -22.0),
	Vector2(52.0, -21.4),
	Vector2(55.7, -21.4),
	Vector2(58.2, -21.4),
	Vector2(61.4, -21.0),
	Vector2(67.4, -21.0),
]
const RECEPTION_ROUTE := [
	Vector2(-90.0, 13.0),
	Vector2(-93.0, 16.5),
	Vector2(-93.0, 24.0),
	Vector2(-92.0, 32.0),
	Vector2(-94.0, 36.4),
]

const N1_POS := Vector3(-102.2, 1.04, 13.6)
const N2_POS := Vector3(-109.5, 1.02, 22.0)
const N3_POS := Vector3(-106.0, 1.10, 39.5)
const N4_POS := Vector3(-84.0, 1.06, 10.8)
const N5_POS := Vector3(-90.0, 1.4, 8.05)
const N6_POS := Vector3(-97.5, 0.02, 28.5)
const N7_POS := Vector3(-99.0, 0.02, 37.0)
const N8_POS := Vector3(67.8, 1.2, -23.4)

const RECEPTION_FLOOR := 0.0
const RECEPTION_COUNTER_TOP := 1.0
const SECURITY_DESK_TOP := 1.04
const ENTRANCE_GLASS_FRONT_Z := 8.02
const EXTRACTION_DECK_TOP := 0.03

var _mats: Dictionary = {}
var _textures: Dictionary = {}
var _reception_art: Node3D
var _z10_art: Node3D
var _mesh_total := 0
var _textured_materials := 0
var _micro_normal_materials := 0


func _ready() -> void:
	_reception_art = get_parent().get_node_or_null("ReceptionArt/ReceptionSector") as Node3D
	_z10_art = get_parent().get_node_or_null("Z10Art/Z10Sector") as Node3D
	_load_texture_sets()
	_build_materials()

	_build_n1()
	_build_n2()
	_build_n3()
	_build_n4()
	_build_n5()
	_build_n6()
	_build_n7()
	_build_n8()

	print("FM_NARRATIVE_READY anchors=8 meshes=%d textures=%d micro_normals=%d collisions=0 lights=0" % [
		_mesh_total, _textured_materials, _micro_normal_materials,
	])


# ---------------------------------------------------------------------------
# Materiales PBR. Todos son StandardMaterial3D locales. Los sets de metal y
# goma se cargan de assets existentes; el resto recibe micro-normales de ruido.
# Los únicos materiales emisivos son pantallas/LED de los props, que no
# proyectan luz en la escena.
# ---------------------------------------------------------------------------

func _build_materials() -> void:
	_mats["steel"] = _mat("NARR_Steel", Color(0.22, 0.235, 0.245), 0.86, 0.34)
	_mats["steel_dark"] = _mat("NARR_SteelDark", Color(0.075, 0.082, 0.088), 0.78, 0.42)
	_mats["steel_worn"] = _mat("NARR_SteelWorn", Color(0.31, 0.30, 0.28), 0.72, 0.52)
	_mats["chrome"] = _mat("NARR_Chrome", Color(0.52, 0.55, 0.57), 0.94, 0.20)
	_mats["plastic_dark"] = _mat("NARR_PlasticDark", Color(0.018, 0.021, 0.024), 0.08, 0.46)
	_mats["plastic_grey"] = _mat("NARR_PlasticGrey", Color(0.13, 0.14, 0.145), 0.04, 0.58)
	_mats["plastic_white"] = _mat("NARR_PlasticWhite", Color(0.56, 0.57, 0.55), 0.03, 0.42)
	_mats["plastic_blue"] = _mat("NARR_PlasticBlue", Color(0.055, 0.13, 0.20), 0.04, 0.44)
	_mats["rubber"] = _mat("NARR_Rubber", Color(0.012, 0.013, 0.014), 0.0, 0.92)
	_mats["glove"] = _mat("NARR_Glove", Color(0.205, 0.155, 0.092), 0.0, 0.94)
	_mats["paper"] = _mat("NARR_Paper", Color(0.63, 0.61, 0.54), 0.0, 0.92)
	_mats["paper_aged"] = _mat("NARR_PaperAged", Color(0.46, 0.43, 0.35), 0.0, 0.96)
	_mats["card"] = _mat("NARR_Card", Color(0.58, 0.60, 0.58), 0.02, 0.50)
	_mats["card_red"] = _mat("NARR_CardRed", Color(0.29, 0.025, 0.022), 0.02, 0.48)
	_mats["badge_yellow"] = _mat("NARR_BadgeYellow", Color(0.58, 0.42, 0.035), 0.02, 0.56)
	_mats["lanyard"] = _mat("NARR_Lanyard", Color(0.035, 0.065, 0.095), 0.0, 0.95)
	_mats["fabric_dark"] = _mat("NARR_FabricDark", Color(0.035, 0.040, 0.038), 0.0, 0.98)
	_mats["leather"] = _mat("NARR_Leather", Color(0.165, 0.092, 0.048), 0.02, 0.82)
	_mats["uniform"] = _mat("NARR_Uniform", Color(0.105, 0.135, 0.170), 0.0, 0.92)
	_mats["hazmat"] = _mat("NARR_HazmatSuit", Color(0.49, 0.42, 0.085), 0.02, 0.82)
	_mats["hazmat_dirty"] = _mat("NARR_HazmatDirty", Color(0.35, 0.31, 0.10), 0.0, 0.94)
	_mats["visor"] = _mat("NARR_Visor", Color(0.018, 0.030, 0.028), 0.18, 0.14)
	_mats["ceramic"] = _mat("NARR_Ceramic", Color(0.66, 0.64, 0.59), 0.0, 0.38)
	_mats["coffee"] = _mat("NARR_Coffee", Color(0.075, 0.032, 0.012), 0.0, 0.24)
	_mats["coffee_stain"] = _mat("NARR_CoffeeStain", Color(0.055, 0.030, 0.014), 0.0, 0.66)
	_mats["blood"] = _mat("NARR_BloodDry", Color(0.145, 0.018, 0.013), 0.0, 0.64)
	_mats["blood_dark"] = _mat("NARR_BloodDark", Color(0.075, 0.008, 0.006), 0.0, 0.72)
	_mats["blood_fresh"] = _mat("NARR_BloodFresh", Color(0.21, 0.020, 0.014), 0.0, 0.36)
	_mats["blood_hand"] = _mat("NARR_BloodHand", Color(0.285, 0.026, 0.018), 0.0, 0.40)
	_mats["tape_yellow"] = _mat("NARR_TapeYellow", Color(0.66, 0.50, 0.045), 0.0, 0.66)
	_mats["tape_red"] = _mat("NARR_TapeRed", Color(0.34, 0.022, 0.018), 0.0, 0.70)
	_mats["screen_dead"] = _mat("NARR_ScreenDead", Color(0.012, 0.018, 0.016), 0.18, 0.12)
	_mats["screen_checkin"] = _emissive_mat(
		"NARR_ScreenCheckIn", Color(0.020, 0.055, 0.034), Color(0.10, 0.68, 0.30), 0.55, 0.18
	)
	_mats["screen_radio"] = _emissive_mat(
		"NARR_ScreenRadio", Color(0.035, 0.040, 0.028), Color(0.32, 0.52, 0.12), 0.28, 0.30
	)
	_mats["led_red"] = _emissive_mat(
		"NARR_LedRed", Color(0.24, 0.006, 0.002), Color(1.0, 0.035, 0.010), 2.2, 0.20
	)
	_mats["led_green"] = _emissive_mat(
		"NARR_LedGreen", Color(0.010, 0.16, 0.045), Color(0.08, 0.95, 0.28), 1.2, 0.18
	)
	_mats["lens_glass"] = _mat("NARR_LensGlass", Color(0.34, 0.38, 0.34), 0.30, 0.10)
	_mats["sample_liquid"] = _emissive_mat(
		"NARR_SampleLiquid", Color(0.035, 0.16, 0.055), Color(0.06, 0.55, 0.16), 0.32, 0.16
	)

	# Texturas PBR existentes. Los tints son claros para no apagar el albedo;
	# la rugosidad de la textura manda sobre el valor base.
	_apply_texture_set(
		_mats["steel"], "metal_panel", Color(0.58, 0.62, 0.66), 0.78, 1.0,
		Vector3(1.0, 1.0, 1.0), 0.75
	)
	_apply_texture_set(
		_mats["steel_dark"], "metal_panel", Color(0.30, 0.33, 0.36), 0.72, 1.0,
		Vector3(1.4, 1.4, 1.4), 0.80
	)
	_apply_texture_set(
		_mats["steel_worn"], "rust", Color(0.50, 0.44, 0.38), 0.55, 1.0,
		Vector3(1.6, 1.6, 1.6), 0.90
	)
	_apply_texture_set(
		_mats["rubber"], "rubber", Color(0.85, 0.85, 0.85), 0.0, 1.0,
		Vector3(3.0, 3.0, 3.0), 0.55
	)

	# Micro-normales procedurales para superficies sin set fotográfico.
	var fabric_noise := _make_noise_normal(0.11, 2.2)
	var leather_noise := _make_noise_normal(0.16, 3.0)
	var paper_noise := _make_noise_normal(0.30, 1.0)
	var plastic_noise := _make_noise_normal(0.24, 0.6)
	for key in ["fabric_dark", "uniform", "hazmat", "hazmat_dirty", "lanyard"]:
		_apply_micro_normal(_mats[key], fabric_noise, 0.22, Vector3(4.0, 4.0, 4.0))
	for key in ["glove", "leather"]:
		_apply_micro_normal(_mats[key], leather_noise, 0.35, Vector3(2.5, 2.5, 2.5))
	for key in ["paper", "paper_aged", "card", "card_red"]:
		_apply_micro_normal(_mats[key], paper_noise, 0.14, Vector3(5.0, 5.0, 5.0))
	for key in ["plastic_dark", "plastic_grey", "plastic_blue", "plastic_white", "badge_yellow"]:
		_apply_micro_normal(_mats[key], plastic_noise, 0.08, Vector3(4.0, 4.0, 4.0))


func _load_texture(path: String) -> Texture2D:
	if path.is_empty():
		return null
	var texture := load(path) as Texture2D
	if texture == null:
		push_warning("FM_NARRATIVE no pudo cargar %s" % path)
	return texture


func _add_texture_set(key: String, albedo_path: String, normal_path: String, rough_path: String) -> void:
	_textures[key] = {
		"albedo": _load_texture(albedo_path),
		"normal": _load_texture(normal_path),
		"rough": _load_texture(rough_path),
	}


func _load_texture_sets() -> void:
	_add_texture_set(
		"metal_panel",
		ART_TEX + "metal_panel_albedo.png",
		ART_TEX + "metal_panel_normal.png",
		ART_TEX + "metal_panel_roughness.png"
	)
	_add_texture_set(
		"rust",
		ART_TEX + "rust_albedo.png",
		ART_TEX + "rust_normal.png",
		ART_TEX + "rust_roughness.png"
	)
	_add_texture_set(
		"rubber",
		CONNECTOR_TEX + "rubber_albedo.png",
		CONNECTOR_TEX + "rubber_normal.png",
		CONNECTOR_TEX + "rubber_rough.png"
	)


func _apply_texture_set(
	mat: StandardMaterial3D,
	key: String,
	tint: Color,
	metallic: float,
	roughness: float,
	uv_scale: Vector3,
	normal_scale: float
) -> void:
	var set: Dictionary = _textures.get(key, {})
	if set.get("albedo") != null:
		mat.albedo_texture = set["albedo"]
	mat.albedo_color = tint
	mat.metallic = metallic
	mat.roughness = roughness
	if set.get("normal") != null:
		mat.normal_enabled = true
		mat.normal_texture = set["normal"]
		mat.normal_scale = normal_scale
	if set.get("rough") != null:
		mat.roughness_texture = set["rough"]
	mat.uv1_triplanar = true
	mat.uv1_scale = uv_scale
	mat.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
	_textured_materials += 1


func _apply_micro_normal(
	mat: StandardMaterial3D,
	normal_texture: Texture2D,
	normal_scale: float,
	uv_scale: Vector3
) -> void:
	mat.normal_enabled = true
	mat.normal_texture = normal_texture
	mat.normal_scale = normal_scale
	mat.uv1_triplanar = true
	mat.uv1_scale = uv_scale
	mat.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
	_micro_normal_materials += 1


func _make_noise_normal(frequency: float, bump_strength: float) -> NoiseTexture2D:
	var noise := FastNoiseLite.new()
	noise.noise_type = FastNoiseLite.TYPE_SIMPLEX_SMOOTH
	noise.frequency = frequency
	noise.fractal_type = FastNoiseLite.FRACTAL_FBM
	noise.fractal_octaves = 3
	var texture := NoiseTexture2D.new()
	texture.width = 256
	texture.height = 256
	texture.seamless = true
	texture.normalize = true
	texture.as_normal_map = true
	texture.bump_strength = bump_strength
	texture.noise = noise
	return texture


func _mat(mat_name: String, color: Color, metallic: float, roughness: float) -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.resource_name = mat_name
	mat.albedo_color = color
	mat.metallic = metallic
	mat.roughness = roughness
	return mat


func _emissive_mat(
	mat_name: String, color: Color, emission: Color, energy: float, roughness: float
) -> StandardMaterial3D:
	var mat := _mat(mat_name, color, 0.06, roughness)
	mat.emission_enabled = true
	mat.emission = emission
	mat.emission_energy_multiplier = energy
	return mat


# ---------------------------------------------------------------------------
# Anclajes
# ---------------------------------------------------------------------------

func _anchor(id: String, node_name: String, pos: Vector3, sector := "RECEPTION") -> Node3D:
	var root := Node3D.new()
	root.name = node_name
	root.position = pos
	root.add_to_group(GROUP_NARRATIVE)
	root.set_meta("narrative_id", id)
	root.set_meta("narrative_sector", sector)
	add_child(root)
	return root


# ------------------------------- N1 ---------------------------------------

func _build_n1() -> void:
	var root := _anchor("N1", "N1_ReceptionCounter", N1_POS)
	var y := RECEPTION_COUNTER_TOP - N1_POS.y  # base de los objetos sobre el mostrador

	# Terminal CHECK-IN: kiosco bajo de recepción, pantalla inclinada hacia el
	# visitante y etiqueta legible. La pantalla es emisiva, no una luz.
	var terminal := Node3D.new()
	terminal.name = "CheckInTerminal"
	terminal.position = Vector3(0.92, y, 0.10)
	terminal.rotation.y = -0.10
	root.add_child(terminal)
	_box(terminal, "Foot", Vector3(0.0, 0.018, 0.0), Vector3(0.34, 0.036, 0.24), _mats["plastic_dark"])
	_box(terminal, "Column", Vector3(0.0, 0.13, 0.05), Vector3(0.055, 0.20, 0.055), _mats["steel_dark"])
	var display := Node3D.new()
	display.name = "Display"
	display.position = Vector3(0.0, 0.34, 0.015)
	display.rotation.x = -0.16
	terminal.add_child(display)
	_box(display, "Bezel", Vector3.ZERO, Vector3(0.36, 0.25, 0.052), _mats["plastic_dark"])
	_box(display, "Screen", Vector3(0.0, 0.0, -0.029), Vector3(0.30, 0.19, 0.004), _mats["screen_checkin"])
	_label(
		display,
		"CheckInLabel",
		"CHECK-IN",
		Vector3(0.0, 0.050, -0.033),
		24,
		0.0024,
		Color(0.56, 1.0, 0.68, 1.0),
		Vector3(0.0, PI, 0.0),
	)
	_box(display, "ScanLed", Vector3(0.145, -0.095, -0.030), Vector3(0.014, 0.014, 0.004), _mats["led_green"])
	_box(terminal, "CableCover", Vector3(-0.09, 0.022, 0.13), Vector3(0.06, 0.012, 0.07), _mats["rubber"])

	# Registro de visitas: portapapeles real de Recepción reutilizado, con hojas
	# sueltas y bolígrafo.
	var clipboard_src := _find_mesh("ReceptionArt/ReceptionSector", "REC10_CLIPBOARD")
	var log_root := _reuse_centered(
		clipboard_src, root, "VisitorLog", Vector3(-0.62, y + 0.007, 0.02), Vector3(0.0, 0.34, 0.0)
	)
	if log_root.get_child_count() == 0:
		_box(log_root, "FallbackBoard", Vector3.ZERO, Vector3(0.20, 0.012, 0.28), _mats["paper_aged"])
	_label(
		log_root,
		"VisitorLogLabel",
		"REGISTRO DE VISITAS",
		Vector3(0.0, 0.010, -0.02),
		17,
		0.0016,
		Color(0.12, 0.11, 0.09, 1.0),
		Vector3(-PI * 0.5, 0.0, 0.0),
	)
	_reuse_centered(
		_find_mesh("ReceptionArt/ReceptionSector", "REC10_PAPER_00"),
		root,
		"LoosePaperA",
		Vector3(-1.0, y + 0.006, -0.16),
		Vector3(0.0, -0.22, 0.0),
	)
	_reuse_centered(
		_find_mesh("ReceptionArt/ReceptionSector", "REC10_PAPER_01"),
		root,
		"LoosePaperB",
		Vector3(-0.90, y + 0.010, -0.22),
		Vector3(0.0, 0.41, 0.0),
	)
	_cylinder(
		root, "Pen", Vector3(-0.34, y + 0.012, -0.10), 0.006, 0.145, _mats["plastic_blue"],
		Vector3(0.0, 0.20, PI * 0.5), 8
	)

	# Bandeja de badges con tarjetas y cordones.
	var tray := Node3D.new()
	tray.name = "BadgeTray"
	tray.position = Vector3(0.49, y, -0.53)
	tray.rotation.y = 0.08
	root.add_child(tray)
	_box(tray, "TrayBase", Vector3(0.0, 0.007, 0.0), Vector3(0.38, 0.014, 0.25), _mats["plastic_grey"])
	_box(tray, "TrayLipFront", Vector3(0.0, 0.020, -0.119), Vector3(0.38, 0.026, 0.012), _mats["plastic_grey"])
	_box(tray, "TrayLipBack", Vector3(0.0, 0.020, 0.119), Vector3(0.38, 0.026, 0.012), _mats["plastic_grey"])
	_box(tray, "TrayLipL", Vector3(-0.184, 0.020, 0.0), Vector3(0.012, 0.026, 0.25), _mats["plastic_grey"])
	_box(tray, "TrayLipR", Vector3(0.184, 0.020, 0.0), Vector3(0.012, 0.026, 0.25), _mats["plastic_grey"])
	for i in 3:
		var bx := -0.105 + float(i) * 0.105
		var badge := Node3D.new()
		badge.name = "Badge_%d" % i
		badge.position = Vector3(bx, 0.022, 0.012)
		badge.rotation.y = -0.18 + float(i) * 0.16
		tray.add_child(badge)
		_box(badge, "Card", Vector3.ZERO, Vector3(0.082, 0.004, 0.054), _mats["card"])
		_box(badge, "Stripe", Vector3(0.0, 0.0025, -0.020), Vector3(0.082, 0.001, 0.009), _mats["tape_red"])
		_box(badge, "Lanyard", Vector3(0.0, 0.001, 0.043), Vector3(0.018, 0.002, 0.115), _mats["lanyard"])
	_label(
		tray,
		"BadgeTrayLabel",
		"BADGES",
		Vector3(0.0, 0.035, -0.133),
		16,
		0.0017,
		Color(0.72, 0.74, 0.70, 1.0),
		Vector3(0.0, PI, 0.0),
	)

	# Café: taza de cerámica, posavasos y anillo de humedad sobre el mostrador.
	var coffee := Node3D.new()
	coffee.name = "CoffeeCup"
	coffee.position = Vector3(-0.24, y, -0.62)
	root.add_child(coffee)
	_cylinder(coffee, "Saucer", Vector3(0.0, 0.004, 0.0), 0.065, 0.008, _mats["ceramic"], Vector3.ZERO, 20)
	var cup := CylinderMesh.new()
	cup.top_radius = 0.043
	cup.bottom_radius = 0.035
	cup.height = 0.088
	cup.radial_segments = 20
	_mesh_instance(coffee, "Cup", cup, _mats["ceramic"], Vector3(0.0, 0.052, 0.0))
	_cylinder(coffee, "Coffee", Vector3(0.0, 0.094, 0.0), 0.034, 0.004, _mats["coffee"], Vector3.ZERO, 16)
	_torus(
		coffee, "Handle", Vector3(0.047, 0.056, 0.0), 0.022, 0.033, _mats["ceramic"],
		Vector3(PI * 0.5, 0.0, 0.0), 10, 5
	)
	_torus(
		root, "CoffeeRing", Vector3(-0.08, y + 0.003, -0.50), 0.044, 0.052,
		_mats["coffee_stain"], Vector3.ZERO, 16, 4
	)
	_cylinder(root, "CoffeeDrop", Vector3(-0.16, y + 0.003, -0.44), 0.008, 0.003, _mats["coffee_stain"], Vector3.ZERO, 10)

	# Silla volcada junto al mostrador. Se reutiliza la malla real de Recepción.
	var chair_src := _find_mesh("ReceptionArt/ReceptionSector", "REC06_CHAIR_HERO")
	var chair_pivot := _reuse_from_base(
		chair_src, root, "ToppledChair",
		Vector3(-1.46, -N1_POS.y + 0.36, -1.28),
		Vector3(0.0, 0.62, deg_to_rad(96.0))
	)
	if chair_pivot.get_child_count() == 0:
		_fallback_toppled_chair(chair_pivot, Vector3.ZERO, Vector3(0.0, 0.38, deg_to_rad(96.0)))
	_reuse_centered(
		_find_mesh("ReceptionArt/ReceptionSector", "REC10_PAPER_02"),
		root,
		"FloorPaperN1",
		Vector3(-0.55, -N1_POS.y + 0.006, 0.72),
		Vector3(0.0, -0.55, 0.0),
	)


# ------------------------------- N4 ---------------------------------------

func _build_n4() -> void:
	var root := _anchor("N4", "N4_SecurityControl", N4_POS)
	var y := SECURITY_DESK_TOP - N4_POS.y  # base sobre el escritorio de seguridad
	var floor_y := RECEPTION_FLOOR - N4_POS.y

	# Libreta de novedades sobre el borde oeste del escritorio.
	var notebook := _reuse_centered(
		_find_mesh("ReceptionArt/ReceptionSector", "REC10_CLIPBOARD"),
		root,
		"Notebook",
		Vector3(-1.00, y + 0.007, 0.17),
		Vector3(0.0, -0.28, 0.0),
	)
	if notebook.get_child_count() == 0:
		_box(notebook, "FallbackNotebook", Vector3.ZERO, Vector3(0.20, 0.012, 0.28), _mats["paper_aged"])
	_label(
		notebook, "NotebookLabel", "NOVEDADES", Vector3(0.0, 0.010, 0.0), 16, 0.0015,
		Color(0.10, 0.10, 0.08, 1.0), Vector3(-PI * 0.5, 0.0, 0.0)
	)

	# Radio de seguridad con LED de recepción.
	var radio := Node3D.new()
	radio.name = "SecurityRadio"
	radio.position = Vector3(0.39, y, -0.28)
	radio.rotation.y = 0.34
	root.add_child(radio)
	_box(radio, "Body", Vector3(0.0, 0.031, 0.0), Vector3(0.086, 0.058, 0.175), _mats["plastic_dark"])
	_box(radio, "Grip", Vector3(0.0, 0.062, 0.030), Vector3(0.070, 0.004, 0.095), _mats["rubber"])
	_box(radio, "Speaker", Vector3(0.0, 0.034, -0.070), Vector3(0.056, 0.030, 0.004), _mats["plastic_grey"])
	_box(radio, "Screen", Vector3(0.018, 0.043, -0.089), Vector3(0.030, 0.014, 0.003), _mats["screen_radio"])
	_box(radio, "Led", Vector3(-0.032, 0.052, -0.089), Vector3(0.008, 0.008, 0.003), _mats["led_red"])
	_cylinder(radio, "Antenna", Vector3(-0.032, 0.142, 0.012), 0.0035, 0.160, _mats["rubber"], Vector3(0.0, 0.0, 0.10), 6)
	_box(radio, "Ptt", Vector3(0.050, 0.032, 0.020), Vector3(0.010, 0.034, 0.045), _mats["steel_dark"])

	# Badge DENEGADO sobre el borde delantero del escritorio.
	var badge := Node3D.new()
	badge.name = "DeniedBadge"
	badge.position = Vector3(0.02, y + 0.003, -0.335)
	badge.rotation.y = -0.16
	root.add_child(badge)
	_box(badge, "Card", Vector3.ZERO, Vector3(0.105, 0.004, 0.068), _mats["card"])
	_box(badge, "DeniedStripe", Vector3(0.0, 0.0025, -0.024), Vector3(0.105, 0.001, 0.013), _mats["card_red"])
	_label(
		badge, "DeniedLabel", "DENEGADO", Vector3(0.0, 0.005, 0.002), 18, 0.0016,
		Color(0.42, 0.015, 0.012, 1.0), Vector3(-PI * 0.5, 0.0, 0.0)
	)

	# Cinta de precinto cortada: dos tramos sobre el escritorio y uno en el suelo.
	_box(root, "CutTapeDeskA", Vector3(-0.42, y + 0.005, -0.27), Vector3(0.26, 0.003, 0.045), _mats["tape_red"], Vector3(0.0, 0.20, 0.0))
	_box(root, "CutTapeDeskB", Vector3(-0.13, y + 0.006, -0.31), Vector3(0.18, 0.003, 0.045), _mats["tape_red"], Vector3(0.0, -0.42, 0.0))
	_box(
		root, "CutTapeFloor", Vector3(0.56, floor_y + 0.010, -0.55), Vector3(0.30, 0.003, 0.042),
		_mats["tape_yellow"], Vector3(0.0, 0.85, 0.0)
	)
	_box(
		root, "CutTapeFloorB", Vector3(0.75, floor_y + 0.010, -0.40), Vector3(0.16, 0.003, 0.042),
		_mats["tape_yellow"], Vector3(0.0, -0.35, 0.0)
	)

	# Monitor CCTV muerto, descolgado del escritorio y apoyado en el suelo con
	# la pantalla agrietada hacia el pasillo. Se inclina ligeramente hacia atrás.
	var monitor := Node3D.new()
	monitor.name = "DeadCctvMonitor"
	monitor.position = Vector3(0.91, floor_y + 0.020, -0.47)
	monitor.rotation = Vector3(0.30, 0.16, 0.0)
	root.add_child(monitor)
	_box(monitor, "Body", Vector3(0.0, 0.175, 0.0), Vector3(0.37, 0.30, 0.060), _mats["plastic_dark"])
	_box(monitor, "Bezel", Vector3(0.0, 0.175, -0.033), Vector3(0.345, 0.275, 0.010), _mats["plastic_grey"])
	_box(monitor, "DeadScreen", Vector3(0.0, 0.178, -0.039), Vector3(0.300, 0.215, 0.004), _mats["screen_dead"])
	_box(monitor, "CrackA", Vector3(-0.032, 0.190, -0.042), Vector3(0.205, 0.003, 0.002), _mats["steel_worn"], Vector3(0.0, 0.0, 0.55))
	_box(monitor, "CrackB", Vector3(0.035, 0.172, -0.042), Vector3(0.130, 0.003, 0.002), _mats["steel_worn"], Vector3(0.0, 0.0, -0.76))
	_box(monitor, "CrackC", Vector3(-0.045, 0.150, -0.042), Vector3(0.105, 0.002, 0.002), _mats["steel_worn"], Vector3(0.0, 0.0, 0.18))
	_box(monitor, "StandNeck", Vector3(0.0, 0.085, 0.055), Vector3(0.055, 0.170, 0.050), _mats["plastic_grey"])
	_box(monitor, "StandFoot", Vector3(0.0, 0.012, 0.105), Vector3(0.180, 0.024, 0.110), _mats["plastic_grey"])
	_box(monitor, "Vent", Vector3(0.0, 0.295, 0.005), Vector3(0.180, 0.018, 0.025), _mats["steel_dark"])
	_label(
		monitor, "CctvLabel", "CCTV-03", Vector3(0.0, 0.058, -0.044), 15, 0.0013,
		Color(0.55, 0.57, 0.54, 1.0), Vector3(0.0, PI, 0.0)
	)
	_cylinder(
		monitor, "BrokenCable", Vector3(-0.17, 0.010, 0.10), 0.008, 0.34,
		_mats["rubber"], Vector3(0.0, 0.65, PI * 0.5), 6
	)
	_cylinder(
		monitor, "CableEnd", Vector3(-0.33, 0.010, 0.20), 0.008, 0.10,
		_mats["rubber"], Vector3(0.0, -0.25, PI * 0.5), 6
	)

	# Silla volcada del puesto de control, reutilizando la malla de Recepción.
	var chair_src := _find_mesh("ReceptionArt/ReceptionSector", "REC07_SECURITY_CHAIR_HERO")
	var chair_pivot := _reuse_from_base(
		chair_src, root, "ToppledSecurityChair",
		Vector3(-1.62, floor_y + 0.36, 0.62),
		Vector3(0.0, -0.55, deg_to_rad(94.0))
	)
	if chair_pivot.get_child_count() == 0:
		_fallback_toppled_chair(chair_pivot, Vector3.ZERO, Vector3(0.0, -0.55, deg_to_rad(94.0)))
	_reuse_centered(
		_find_mesh("ReceptionArt/ReceptionSector", "REC10_PAPER_09"),
		root,
		"SecurityPaperFloor",
		Vector3(-0.45, floor_y + 0.006, -0.22),
		Vector3(0.0, 0.48, 0.0),
	)


# ------------------------------- N5 ---------------------------------------

func _build_n5() -> void:
	var root := _anchor("N5", "N5_EntranceThreshold", N5_POS)
	var floor_y := RECEPTION_FLOOR - N5_POS.y
	var glass_z := ENTRANCE_GLASS_FRONT_Z - N5_POS.z - 0.008

	# Los dos paños de vidrio reales del umbral (x = -92,8 y -87,2) reciben
	# huellas, grietas y cinta. No se duplica el vidrio para no provocar z-fighting.
	_handprint(root, "HandprintW", Vector3(-2.80, -0.05, glass_z), 0.08, 1.05)
	_handprint(root, "HandprintE", Vector3(2.80, -0.22, glass_z), -0.20, 0.96)
	_glass_crack(root, "GlassCrackW", Vector3(-2.92, 0.10, glass_z + 0.001), 0.0, 0.30)
	_glass_crack(root, "GlassCrackE", Vector3(2.69, 0.02, glass_z + 0.001), 0.50, 0.24)

	# Cinta de cuarentena sobre el paño oeste; el centro x=-90..-88 queda libre.
	_box(
		root, "QuarantineTapeW", Vector3(-2.42, -0.16, glass_z - 0.002),
		Vector3(0.92, 0.085, 0.004), _mats["tape_yellow"], Vector3(0.0, 0.0, 0.08)
	)
	_box(
		root, "QuarantineTapeWStripeA", Vector3(-2.64, -0.16, glass_z - 0.004),
		Vector3(0.10, 0.085, 0.003), _mats["tape_red"], Vector3(0.0, 0.0, 0.08)
	)
	_box(
		root, "QuarantineTapeWStripeB", Vector3(-2.18, -0.16, glass_z - 0.004),
		Vector3(0.10, 0.085, 0.003), _mats["tape_red"], Vector3(0.0, 0.0, 0.08)
	)
	_label(
		root, "QuarantineLabel", "CUARENTENA", Vector3(-2.42, -0.16, glass_z - 0.007),
		16, 0.0017, Color(0.12, 0.10, 0.06, 1.0), Vector3(0.0, PI, 0.08)
	)

	# Cinta suelta en el suelo, fuera del paso central.
	_box(
		root, "FloorTapeA", Vector3(-2.55, floor_y + 0.010, 0.20),
		Vector3(0.58, 0.003, 0.075), _mats["tape_yellow"], Vector3(0.0, 0.72, 0.0)
	)
	_box(
		root, "FloorTapeB", Vector3(-2.15, floor_y + 0.011, 0.58),
		Vector3(0.38, 0.003, 0.070), _mats["tape_yellow"], Vector3(0.0, -0.18, 0.0)
	)

	# Lanyard y badge de visitante caídos junto al paño oeste.
	var lanyard := Node3D.new()
	lanyard.name = "DroppedLanyard"
	lanyard.position = Vector3(-2.30, floor_y + 0.008, 0.62)
	lanyard.rotation.y = 0.62
	root.add_child(lanyard)
	_box(lanyard, "StrapA", Vector3(-0.07, 0.004, 0.0), Vector3(0.020, 0.003, 0.28), _mats["lanyard"])
	_box(lanyard, "StrapB", Vector3(0.07, 0.004, 0.015), Vector3(0.020, 0.003, 0.24), _mats["lanyard"], Vector3(0.0, 0.22, 0.0))
	_box(lanyard, "BadgeCard", Vector3(0.0, 0.006, 0.17), Vector3(0.092, 0.004, 0.060), _mats["card"])
	_box(lanyard, "BadgeStripe", Vector3(0.0, 0.0085, 0.150), Vector3(0.092, 0.001, 0.012), _mats["badge_yellow"])
	_label(
		lanyard, "BadgeName", "VISITANTE", Vector3(0.0, 0.010, 0.178), 14, 0.0013,
		Color(0.10, 0.10, 0.08, 1.0), Vector3(-PI * 0.5, 0.0, 0.0)
	)

	# Sangre seca en el suelo, concentrada al oeste del eje de paso.
	var blood := Node3D.new()
	blood.name = "DriedBloodThreshold"
	blood.position = Vector3(-2.12, floor_y + 0.012, 0.86)
	root.add_child(blood)
	_cylinder(blood, "Pool", Vector3.ZERO, 0.16, 0.003, _mats["blood_dark"], Vector3.ZERO, 18).scale = Vector3(1.45, 1.0, 0.78)
	_cylinder(blood, "PoolCore", Vector3(-0.03, 0.002, 0.01), 0.095, 0.003, _mats["blood"], Vector3.ZERO, 16).scale = Vector3(1.35, 1.0, 0.72)
	_box(blood, "SmearA", Vector3(-0.21, 0.002, 0.03), Vector3(0.24, 0.003, 0.08), _mats["blood"], Vector3(0.0, 0.42, 0.0))
	_box(blood, "SmearB", Vector3(-0.34, 0.002, 0.11), Vector3(0.18, 0.003, 0.04), _mats["blood"], Vector3(0.0, 0.68, 0.0))
	_cylinder(blood, "DropA", Vector3(0.16, 0.002, -0.13), 0.020, 0.003, _mats["blood_fresh"], Vector3.ZERO, 10)
	_cylinder(blood, "DropB", Vector3(0.21, 0.002, -0.20), 0.011, 0.003, _mats["blood_fresh"], Vector3.ZERO, 8)
	_cylinder(blood, "DropC", Vector3(-0.08, 0.002, -0.22), 0.013, 0.003, _mats["blood"], Vector3.ZERO, 8)


# ------------------------------- N6 ---------------------------------------

func _build_n6() -> void:
	var root := _anchor("N6", "N6_CentralCorridorTrail", N6_POS)
	var floor_y := RECEPTION_FLOOR - N6_POS.y

	# Rastro de arrastre: segmentos planos y gotas. El rastro se mantiene al
	# oeste de x=-96, lejos del eje de la ruta (x=-93).
	var trail_points := [
		Vector3(-2.35, floor_y + 0.012, -0.72),
		Vector3(-1.95, floor_y + 0.012, -0.48),
		Vector3(-1.54, floor_y + 0.012, -0.24),
		Vector3(-1.10, floor_y + 0.012, -0.06),
		Vector3(-0.62, floor_y + 0.012, 0.10),
		Vector3(-0.14, floor_y + 0.012, 0.28),
		Vector3(0.34, floor_y + 0.012, 0.50),
		Vector3(0.82, floor_y + 0.012, 0.68),
		Vector3(1.22, floor_y + 0.012, 0.94),
	]
	var widths := [0.34, 0.31, 0.29, 0.27, 0.25, 0.24, 0.22, 0.20]
	for i in trail_points.size() - 1:
		var a: Vector3 = trail_points[i]
		var b: Vector3 = trail_points[i + 1]
		var mid := (a + b) * 0.5
		var delta := b - a
		var length := Vector2(delta.x, delta.z).length()
		var yaw := -atan2(delta.z, delta.x)
		_box(
			root, "DragSegment_%02d" % i, mid,
			Vector3(length + 0.20, 0.003, widths[i]), _mats["blood_dark"], Vector3(0.0, yaw, 0.0)
		)
		_box(
			root, "DragCore_%02d" % i, mid + Vector3(0.0, 0.002, 0.0),
			Vector3(length + 0.10, 0.002, widths[i] * 0.36), _mats["blood"], Vector3(0.0, yaw, 0.0)
		)
	# Dedos/salpicaduras laterales.
	var drop_positions := [
		Vector3(-2.15, floor_y + 0.013, -0.88),
		Vector3(-1.72, floor_y + 0.013, -0.60),
		Vector3(-1.28, floor_y + 0.013, -0.45),
		Vector3(-0.78, floor_y + 0.013, -0.22),
		Vector3(-0.34, floor_y + 0.013, 0.02),
		Vector3(0.18, floor_y + 0.013, 0.12),
		Vector3(0.74, floor_y + 0.013, 0.34),
		Vector3(1.10, floor_y + 0.013, 0.54),
	]
	for i in drop_positions.size():
		var radius := 0.010 + float(i % 3) * 0.004
		_cylinder(
			root, "TrailDrop_%02d" % i, drop_positions[i], radius, 0.003,
			_mats["blood_fresh"], Vector3.ZERO, 8
		)

	# Guante de trabajo caído.
	var glove := Node3D.new()
	glove.name = "DroppedGlove"
	glove.position = Vector3(0.38, floor_y + 0.004, -0.18)
	glove.rotation.y = 0.52
	root.add_child(glove)
	_box(glove, "Palm", Vector3(0.0, 0.016, 0.0), Vector3(0.105, 0.028, 0.155), _mats["glove"])
	_box(glove, "Cuff", Vector3(0.0, 0.020, 0.092), Vector3(0.100, 0.040, 0.050), _mats["glove"])
	_box(glove, "Thumb", Vector3(-0.060, 0.016, 0.020), Vector3(0.055, 0.026, 0.042), _mats["glove"], Vector3(0.0, 0.0, -0.55))
	for i in 4:
		var fx := -0.036 + float(i) * 0.024
		var fl := 0.060 - absf(float(i) - 1.5) * 0.006
		_box(
			glove, "Finger_%d" % i, Vector3(fx, 0.015, -0.100 - fl * 0.30),
			Vector3(0.020, 0.024, fl), _mats["glove"], Vector3(0.0, 0.0, 0.0)
		)
	_box(glove, "Seam", Vector3(0.0, 0.031, 0.0), Vector3(0.012, 0.002, 0.14), _mats["fabric_dark"])

	# Maletín de muestras y vial roto.
	var case_root := Node3D.new()
	case_root.name = "SampleCase"
	case_root.position = Vector3(-0.62, floor_y + 0.004, 0.76)
	case_root.rotation.y = -0.28
	root.add_child(case_root)
	_box(case_root, "CaseBody", Vector3(0.0, 0.065, 0.0), Vector3(0.44, 0.130, 0.30), _mats["plastic_white"])
	_box(case_root, "CaseSeam", Vector3(0.0, 0.075, 0.0), Vector3(0.445, 0.006, 0.305), _mats["steel_dark"])
	_box(case_root, "CaseLip", Vector3(0.0, 0.130, 0.0), Vector3(0.36, 0.012, 0.24), _mats["plastic_white"])
	_box(case_root, "HandleBar", Vector3(0.0, 0.160, 0.0), Vector3(0.16, 0.020, 0.036), _mats["plastic_blue"])
	_box(case_root, "HandlePostL", Vector3(-0.075, 0.145, 0.0), Vector3(0.018, 0.032, 0.030), _mats["plastic_blue"])
	_box(case_root, "HandlePostR", Vector3(0.075, 0.145, 0.0), Vector3(0.018, 0.032, 0.030), _mats["plastic_blue"])
	_box(case_root, "LatchL", Vector3(-0.145, 0.115, -0.155), Vector3(0.040, 0.030, 0.010), _mats["steel"])
	_box(case_root, "LatchR", Vector3(0.145, 0.115, -0.155), Vector3(0.040, 0.030, 0.010), _mats["steel"])
	_box(case_root, "BioLabel", Vector3(0.0, 0.090, -0.154), Vector3(0.080, 0.070, 0.004), _mats["badge_yellow"])
	_label(
		case_root, "SampleLabel", "MUESTRA", Vector3(0.0, 0.090, -0.158), 14, 0.0014,
		Color(0.09, 0.08, 0.05, 1.0), Vector3(0.0, PI, 0.0)
	)
	# Vial de vidrio roto junto al maletín.
	_cylinder(
		case_root, "VialBody", Vector3(0.28, 0.022, 0.12), 0.020, 0.085,
		_mats["lens_glass"], Vector3(0.0, 0.0, PI * 0.5), 10
	)
	_cylinder(
		case_root, "VialCap", Vector3(0.325, 0.022, 0.12), 0.024, 0.018,
		_mats["plastic_dark"], Vector3(0.0, 0.0, PI * 0.5), 10
	)
	_cylinder(
		root, "VialSpill", Vector3(-0.34, floor_y + 0.010, 0.84), 0.055, 0.002,
		_mats["sample_liquid"], Vector3.ZERO, 14
	)

	# Radio caída con LED de recepción encendido.
	var radio := Node3D.new()
	radio.name = "DroppedRadio"
	radio.position = Vector3(0.86, floor_y + 0.030, -0.77)
	radio.rotation.y = -0.42
	root.add_child(radio)
	_box(radio, "Body", Vector3(0.0, 0.0, 0.0), Vector3(0.085, 0.058, 0.175), _mats["plastic_dark"])
	_box(radio, "Grip", Vector3(0.0, 0.031, 0.030), Vector3(0.068, 0.004, 0.090), _mats["rubber"])
	_box(radio, "Speaker", Vector3(0.0, 0.002, -0.070), Vector3(0.056, 0.030, 0.004), _mats["plastic_grey"])
	_box(radio, "Screen", Vector3(0.016, 0.010, -0.089), Vector3(0.030, 0.014, 0.003), _mats["screen_radio"])
	_box(radio, "Led", Vector3(-0.032, 0.018, -0.089), Vector3(0.009, 0.009, 0.004), _mats["led_red"])
	_cylinder(radio, "Antenna", Vector3(-0.030, 0.108, 0.010), 0.0035, 0.145, _mats["rubber"], Vector3(0.0, 0.0, 0.10), 6)
	_box(radio, "Ptt", Vector3(0.050, -0.002, 0.025), Vector3(0.010, 0.032, 0.044), _mats["steel_dark"])

	# Linterna caída, apagada, con la lente de cristal.
	var torch := Node3D.new()
	torch.name = "DroppedFlashlight"
	torch.position = Vector3(1.12, floor_y + 0.036, 0.14)
	torch.rotation.y = 0.18
	root.add_child(torch)
	_cylinder(torch, "Body", Vector3(0.0, 0.0, 0.0), 0.026, 0.190, _mats["steel_dark"], Vector3(0.0, 0.0, PI * 0.5), 12)
	_cylinder(torch, "Head", Vector3(0.108, 0.0, 0.0), 0.036, 0.070, _mats["steel_worn"], Vector3(0.0, 0.0, PI * 0.5), 12)
	_cylinder(torch, "Lens", Vector3(0.145, 0.0, 0.0), 0.032, 0.006, _mats["lens_glass"], Vector3(0.0, 0.0, PI * 0.5), 16)
	_cylinder(torch, "TailCap", Vector3(-0.104, 0.0, 0.0), 0.028, 0.020, _mats["rubber"], Vector3(0.0, 0.0, PI * 0.5), 12)
	_box(torch, "Switch", Vector3(-0.02, 0.028, 0.0), Vector3(0.032, 0.006, 0.022), _mats["plastic_dark"])

	# Marcas de arrastre adicionales y una pequeña mancha bajo el guante.
	_box(
		root, "ScuffA", Vector3(-0.06, floor_y + 0.010, 0.70),
		Vector3(0.44, 0.002, 0.018), _mats["steel_worn"], Vector3(0.0, -0.18, 0.0)
	)
	_box(
		root, "ScuffB", Vector3(0.42, floor_y + 0.010, 0.88),
		Vector3(0.34, 0.002, 0.014), _mats["steel_worn"], Vector3(0.0, 0.34, 0.0)
	)


# ------------------------------- N7 ---------------------------------------

func _build_n7() -> void:
	var root := _anchor("N7", "N7_ExtractionDecon", N7_POS)
	var floor_y := EXTRACTION_DECK_TOP - N7_POS.y  # base sobre la plataforma de extracción

	# Carro de descontaminación con ruedas, bandeja, pulverizador y trapos.
	var cart := Node3D.new()
	cart.name = "DeconCart"
	cart.position = Vector3(0.55, floor_y, 0.45)
	cart.rotation.y = 0.06
	root.add_child(cart)
	for i in 4:
		var wx := -0.27 if i % 2 == 0 else 0.27
		var wz := -0.16 if i < 2 else 0.16
		_cylinder(cart, "Wheel_%d" % i, Vector3(wx, 0.045, wz), 0.045, 0.026, _mats["rubber"], Vector3(0.0, 0.0, PI * 0.5), 12)
		_box(cart, "Fork_%d" % i, Vector3(wx, 0.075, wz), Vector3(0.026, 0.055, 0.018), _mats["steel_dark"])
	_box(cart, "LowerShelf", Vector3(0.0, 0.20, 0.0), Vector3(0.66, 0.030, 0.40), _mats["steel_worn"])
	for i in 4:
		var px := -0.30 if i % 2 == 0 else 0.30
		var pz := -0.18 if i < 2 else 0.18
		_box(cart, "Post_%d" % i, Vector3(px, 0.54, pz), Vector3(0.026, 0.66, 0.026), _mats["steel"])
	_box(cart, "Tray", Vector3(0.0, 0.885, 0.0), Vector3(0.72, 0.050, 0.46), _mats["steel"])
	_box(cart, "TrayLipL", Vector3(-0.350, 0.925, 0.0), Vector3(0.020, 0.035, 0.46), _mats["steel_worn"])
	_box(cart, "TrayLipR", Vector3(0.350, 0.925, 0.0), Vector3(0.020, 0.035, 0.46), _mats["steel_worn"])
	_box(cart, "TrayLipF", Vector3(0.0, 0.925, -0.220), Vector3(0.72, 0.035, 0.020), _mats["steel_worn"])
	_box(cart, "TrayLipB", Vector3(0.0, 0.925, 0.220), Vector3(0.72, 0.035, 0.020), _mats["steel_worn"])
	_box(cart, "HandlePostL", Vector3(-0.28, 1.10, 0.19), Vector3(0.030, 0.34, 0.030), _mats["steel"])
	_box(cart, "HandlePostR", Vector3(0.28, 1.10, 0.19), Vector3(0.030, 0.34, 0.030), _mats["steel"])
	_cylinder(cart, "HandleGrip", Vector3(0.0, 1.27, 0.19), 0.025, 0.58, _mats["rubber"], Vector3(0.0, 0.0, PI * 0.5), 10)
	# Pulverizador de descontaminación.
	_cylinder(cart, "SprayerBody", Vector3(-0.18, 0.975, 0.02), 0.058, 0.150, _mats["plastic_white"], Vector3.ZERO, 12)
	_cylinder(cart, "SprayerShoulder", Vector3(-0.18, 1.052, 0.02), 0.035, 0.035, _mats["plastic_white"], Vector3.ZERO, 12)
	_box(cart, "SprayerTrigger", Vector3(-0.10, 1.055, 0.03), Vector3(0.070, 0.030, 0.045), _mats["plastic_grey"])
	_cylinder(cart, "SprayerNozzle", Vector3(-0.18, 1.072, -0.045), 0.010, 0.09, _mats["plastic_dark"], Vector3(PI * 0.5, 0.0, 0.0), 8)
	# Trapos doblados y bandeja de muestras pequeñas.
	_box(cart, "FoldedTowel", Vector3(0.18, 0.940, 0.02), Vector3(0.22, 0.045, 0.16), _mats["fabric_dark"])
	_box(cart, "SmallSampleBox", Vector3(0.20, 0.972, -0.13), Vector3(0.18, 0.080, 0.13), _mats["plastic_blue"])
	_box(cart, "SmallSampleLid", Vector3(0.20, 1.014, -0.13), Vector3(0.17, 0.010, 0.12), _mats["plastic_grey"])
	_box(cart, "SmallSampleLabel", Vector3(0.20, 0.972, -0.198), Vector3(0.07, 0.045, 0.004), _mats["badge_yellow"])
	# Cubo de residuos en el estante inferior.
	_cylinder(cart, "WasteBucket", Vector3(0.16, 0.325, 0.02), 0.115, 0.22, _mats["tape_yellow"], Vector3.ZERO, 14)
	_cylinder(cart, "WasteBucketRim", Vector3(0.16, 0.437, 0.02), 0.122, 0.014, _mats["rubber"], Vector3.ZERO, 14)

	# Traje hazmat colgado de un soporte de descontaminación.
	var suit_stand := Node3D.new()
	suit_stand.name = "HazmatSuitStand"
	suit_stand.position = Vector3(-0.35, floor_y, -0.55)
	suit_stand.rotation.y = 0.16
	root.add_child(suit_stand)
	_box(suit_stand, "BaseA", Vector3(0.0, 0.012, 0.0), Vector3(0.64, 0.024, 0.070), _mats["steel_dark"])
	_box(suit_stand, "BaseB", Vector3(0.0, 0.012, 0.0), Vector3(0.070, 0.024, 0.64), _mats["steel_dark"])
	_cylinder(suit_stand, "Mast", Vector3(0.0, 0.92, 0.0), 0.020, 1.80, _mats["steel"], Vector3.ZERO, 8)
	_box(suit_stand, "Crossbar", Vector3(0.0, 1.82, 0.0), Vector3(0.62, 0.028, 0.028), _mats["steel"])
	_box(suit_stand, "HookL", Vector3(-0.20, 1.79, 0.0), Vector3(0.018, 0.070, 0.018), _mats["steel"])
	_box(suit_stand, "HookR", Vector3(0.20, 1.79, 0.0), Vector3(0.018, 0.070, 0.018), _mats["steel"])
	# El traje cuelga con la capucha a la altura de los hombros. Cápsulas y
	# esferas suavizan la silueta; pliegues y suciedad rompen la lectura de caja.
	_box(suit_stand, "StrapL", Vector3(-0.18, 1.70, 0.0), Vector3(0.022, 0.20, 0.016), _mats["fabric_dark"])
	_box(suit_stand, "StrapR", Vector3(0.18, 1.70, 0.0), Vector3(0.022, 0.20, 0.016), _mats["fabric_dark"])
	_capsule(suit_stand, "SuitTorso", Vector3(0.0, 1.22, 0.0), 0.220, 0.66, _mats["hazmat"], Vector3.ZERO, 16, 8).scale = Vector3(1.10, 1.0, 0.68)
	_sphere(suit_stand, "ShoulderL", Vector3(-0.235, 1.49, 0.0), 0.108, _mats["hazmat"], Vector3(1.0, 0.85, 0.72))
	_sphere(suit_stand, "ShoulderR", Vector3(0.235, 1.49, 0.0), 0.108, _mats["hazmat"], Vector3(1.0, 0.85, 0.72))
	_box(suit_stand, "SuitChestSeam", Vector3(0.0, 1.27, -0.151), Vector3(0.018, 0.42, 0.006), _mats["hazmat_dirty"])
	_box(suit_stand, "SuitWaist", Vector3(0.0, 0.94, 0.0), Vector3(0.44, 0.080, 0.238), _mats["hazmat_dirty"])
	_box(suit_stand, "SuitBelt", Vector3(0.0, 0.905, 0.0), Vector3(0.45, 0.036, 0.246), _mats["rubber"])
	_box(suit_stand, "SuitPocket", Vector3(-0.12, 1.27, -0.150), Vector3(0.12, 0.13, 0.008), _mats["hazmat_dirty"])
	_box(suit_stand, "SuitGrimeA", Vector3(0.13, 1.12, -0.151), Vector3(0.10, 0.16, 0.006), _mats["hazmat_dirty"], Vector3(0.0, 0.0, 0.35))
	_box(suit_stand, "SuitGrimeB", Vector3(-0.14, 1.40, 0.127), Vector3(0.13, 0.10, 0.006), _mats["hazmat_dirty"], Vector3(0.0, 0.0, -0.28))
	_capsule(suit_stand, "SuitArmL", Vector3(-0.285, 1.20, 0.0), 0.072, 0.52, _mats["hazmat"], Vector3(0.0, 0.0, -0.09), 12, 6)
	_capsule(suit_stand, "SuitArmR", Vector3(0.285, 1.20, 0.0), 0.072, 0.52, _mats["hazmat"], Vector3(0.0, 0.0, 0.09), 12, 6)
	_capsule(suit_stand, "SuitLegL", Vector3(-0.125, 0.52, 0.0), 0.085, 0.82, _mats["hazmat"], Vector3(0.0, 0.0, 0.03), 12, 6)
	_capsule(suit_stand, "SuitLegR", Vector3(0.125, 0.52, 0.0), 0.085, 0.82, _mats["hazmat"], Vector3(0.0, 0.0, -0.03), 12, 6)
	_box(suit_stand, "SuitFoldArmL", Vector3(-0.286, 1.00, -0.055), Vector3(0.10, 0.020, 0.055), _mats["hazmat_dirty"], Vector3(0.0, 0.0, -0.18))
	_box(suit_stand, "SuitFoldLegR", Vector3(0.125, 0.34, -0.070), Vector3(0.12, 0.020, 0.060), _mats["hazmat_dirty"], Vector3(0.0, 0.0, 0.15))
	_box(suit_stand, "BootL", Vector3(-0.125, 0.060, -0.045), Vector3(0.175, 0.12, 0.285), _mats["rubber"])
	_box(suit_stand, "BootR", Vector3(0.125, 0.060, -0.045), Vector3(0.175, 0.12, 0.285), _mats["rubber"])
	var hood := SphereMesh.new()
	hood.radius = 0.155
	hood.height = 0.30
	hood.radial_segments = 16
	hood.rings = 8
	_mesh_instance(suit_stand, "Hood", hood, _mats["hazmat"], Vector3(0.0, 1.66, 0.0)).scale = Vector3(1.0, 1.0, 0.92)
	_sphere(suit_stand, "Visor", Vector3(0.0, 1.66, -0.132), 0.105, _mats["visor"], Vector3(1.0, 0.68, 0.34))
	_torus(
		suit_stand, "HoodRim", Vector3(0.0, 1.66, -0.118), 0.112, 0.132,
		_mats["hazmat_dirty"], Vector3(PI * 0.5, 0.0, 0.0), 16, 5
	)
	_cylinder(
		suit_stand, "Respirator", Vector3(0.0, 1.595, -0.160), 0.042, 0.035,
		_mats["plastic_dark"], Vector3(PI * 0.5, 0.0, 0.0), 12
	)
	_cylinder(
		suit_stand, "Filter", Vector3(0.0, 1.595, -0.185), 0.054, 0.018,
		_mats["steel_worn"], Vector3(PI * 0.5, 0.0, 0.0), 12
	)
	_box(suit_stand, "GloveL", Vector3(-0.335, 0.90, 0.0), Vector3(0.125, 0.10, 0.15), _mats["glove"])
	_box(suit_stand, "GloveR", Vector3(0.335, 0.90, 0.0), Vector3(0.125, 0.10, 0.15), _mats["glove"])
	_label(
		suit_stand, "SuitLabel", "NEXUS · DECON", Vector3(0.0, 1.24, -0.158), 14, 0.0012,
		Color(0.12, 0.11, 0.075, 1.0), Vector3(0.0, PI, 0.0)
	)

	# Portapapeles real de Recepción sobre el carro.
	var clipboard := _reuse_centered(
		_find_mesh("ReceptionArt/ReceptionSector", "REC10_CLIPBOARD"),
		root,
		"DeconClipboard",
		Vector3(0.44, floor_y + 0.920, 0.43),
		Vector3(0.0, 0.18, 0.0),
	)
	if clipboard.get_child_count() == 0:
		_box(clipboard, "FallbackClipboard", Vector3.ZERO, Vector3(0.20, 0.012, 0.28), _mats["paper_aged"])
	_label(
		clipboard, "DeconClipboardLabel", "DECON", Vector3(0.0, 0.010, 0.0), 15, 0.0015,
		Color(0.10, 0.10, 0.08, 1.0), Vector3(-PI * 0.5, 0.0, 0.0)
	)

	# Cartel de suelo de la zona de descontaminación.
	var sign := Node3D.new()
	sign.name = "DeconSign"
	sign.position = Vector3(0.02, floor_y, 1.12)
	sign.rotation.y = 0.10
	root.add_child(sign)
	_box(sign, "SignLegL", Vector3(-0.23, 0.38, 0.0), Vector3(0.045, 0.76, 0.045), _mats["steel_worn"], Vector3(0.0, 0.0, -0.10))
	_box(sign, "SignLegR", Vector3(0.23, 0.38, 0.0), Vector3(0.045, 0.76, 0.045), _mats["steel_worn"], Vector3(0.0, 0.0, 0.10))
	_box(sign, "SignBoard", Vector3(0.0, 0.66, 0.0), Vector3(0.58, 0.38, 0.035), _mats["badge_yellow"], Vector3(-0.10, 0.0, 0.0))
	_box(sign, "SignStripe", Vector3(0.0, 0.48, -0.020), Vector3(0.58, 0.055, 0.006), _mats["tape_red"], Vector3(-0.10, 0.0, 0.0))
	_label(
		sign, "DeconSignLabel", "DECON\nNIVEL 1", Vector3(0.0, 0.70, -0.022), 20, 0.0022,
		Color(0.075, 0.070, 0.050, 1.0), Vector3(-0.10, PI, 0.0)
	)

	# Cajas de muestras al este. Este prop es hijo local en x=+10 (mundo -89),
	# fuera del centro de extracción (-94) y de su radio de 2,4 m.
	var samples := Node3D.new()
	samples.name = "SampleContainersEast"
	samples.position = Vector3(10.0, floor_y, 0.18)
	samples.rotation.y = -0.12
	root.add_child(samples)
	_box(samples, "CoolerBig", Vector3(0.0, 0.155, 0.0), Vector3(0.42, 0.31, 0.32), _mats["plastic_white"])
	_box(samples, "CoolerBigLid", Vector3(0.0, 0.315, 0.0), Vector3(0.43, 0.025, 0.33), _mats["plastic_grey"])
	_box(samples, "CoolerBigHandle", Vector3(0.0, 0.355, 0.0), Vector3(0.20, 0.035, 0.040), _mats["plastic_dark"])
	_box(samples, "CoolerBigLatchL", Vector3(-0.13, 0.245, -0.163), Vector3(0.045, 0.055, 0.010), _mats["steel"])
	_box(samples, "CoolerBigLatchR", Vector3(0.13, 0.245, -0.163), Vector3(0.045, 0.055, 0.010), _mats["steel"])
	_box(samples, "BioSticker", Vector3(0.0, 0.185, -0.163), Vector3(0.085, 0.085, 0.004), _mats["badge_yellow"])
	_label(
		samples, "SampleText", "MUESTRAS\nNEXUS", Vector3(0.0, 0.185, -0.167), 14, 0.0013,
		Color(0.075, 0.065, 0.040, 1.0), Vector3(0.0, PI, 0.0)
	)
	_box(samples, "CoolerSmall", Vector3(0.36, 0.115, 0.20), Vector3(0.30, 0.23, 0.25), _mats["plastic_blue"])
	_box(samples, "CoolerSmallLid", Vector3(0.36, 0.235, 0.20), Vector3(0.31, 0.020, 0.26), _mats["plastic_grey"])
	_box(samples, "CoolerSmallHandle", Vector3(0.36, 0.265, 0.20), Vector3(0.15, 0.030, 0.035), _mats["plastic_dark"])
	_cylinder(samples, "Canister", Vector3(-0.31, 0.100, 0.22), 0.075, 0.20, _mats["plastic_white"], Vector3.ZERO, 14)
	_cylinder(samples, "CanisterCap", Vector3(-0.31, 0.210, 0.22), 0.040, 0.025, _mats["plastic_blue"], Vector3.ZERO, 12)
	_box(samples, "SampleTag", Vector3(-0.31, 0.120, 0.300), Vector3(0.065, 0.050, 0.004), _mats["badge_yellow"])


# ------------------------------- N2 ---------------------------------------

func _build_n2() -> void:
	var root := _anchor("N2", "N2_WaitingArea", N2_POS)
	var floor_y := RECEPTION_FLOOR - N2_POS.y
	var bench_top := 0.9875 - N2_POS.y
	var table_top := 0.465 - N2_POS.y

	# Maleta vertical en el hueco entre los dos bancos, apoyada en la pared
	# oeste. El cuerpo, las cinchas, los cierres y la etiqueta deben leerse
	# como equipaje real, no como una caja genérica.
	var suitcase := Node3D.new()
	suitcase.name = "WaitingSuitcase"
	suitcase.position = Vector3(-0.38, floor_y + 0.27, -0.20)
	suitcase.rotation.y = 0.08
	root.add_child(suitcase)
	_box(suitcase, "Body", Vector3.ZERO, Vector3(0.14, 0.54, 0.46), _mats["leather"])
	_box(suitcase, "StrapTop", Vector3(0.0, 0.15, 0.0), Vector3(0.146, 0.030, 0.468), _mats["rubber"])
	_box(suitcase, "StrapBottom", Vector3(0.0, -0.15, 0.0), Vector3(0.146, 0.030, 0.468), _mats["rubber"])
	for i in 4:
		var sx := -0.071 if i % 2 == 0 else 0.071
		var sz := -0.222 if i < 2 else 0.222
		_box(
			suitcase, "Corner_%d" % i, Vector3(sx, 0.255, sz),
			Vector3(0.012, 0.030, 0.026), _mats["steel_worn"]
		)
	_box(suitcase, "HandlePostL", Vector3(0.0, 0.565, -0.070), Vector3(0.018, 0.055, 0.018), _mats["steel_worn"])
	_box(suitcase, "HandlePostR", Vector3(0.0, 0.565, 0.070), Vector3(0.018, 0.055, 0.018), _mats["steel_worn"])
	_cylinder(
		suitcase, "HandleGrip", Vector3(0.0, 0.594, 0.0), 0.014, 0.12,
		_mats["rubber"], Vector3(PI * 0.5, 0.0, 0.0), 10
	)
	for i in 2:
		var lz := -0.115 if i == 0 else 0.115
		_box(suitcase, "Latch_%d" % i, Vector3(0.073, 0.225, lz), Vector3(0.012, 0.045, 0.050), _mats["steel"])
	_box(suitcase, "Tag", Vector3(0.077, 0.020, 0.150), Vector3(0.006, 0.052, 0.090), _mats["card"])
	_label(
		suitcase, "TagLabel", "NEXUS", Vector3(0.081, 0.020, 0.150), 10, 0.0010,
		Color(0.10, 0.10, 0.08, 1.0), Vector3(0.0, PI * 0.5, 0.0)
	)

	# Mochila de mano en el suelo, junto a la maleta y separada del banco B.
	var backpack := Node3D.new()
	backpack.name = "WaitingBackpack"
	backpack.position = Vector3(-0.05, floor_y, 0.38)
	backpack.rotation.y = -0.12
	root.add_child(backpack)
	_box(backpack, "Body", Vector3(0.0, 0.210, 0.0), Vector3(0.18, 0.42, 0.32), _mats["plastic_dark"])
	_box(backpack, "FrontPocket", Vector3(0.095, 0.205, 0.0), Vector3(0.045, 0.18, 0.21), _mats["leather"])
	_box(backpack, "PocketZip", Vector3(0.120, 0.290, 0.0), Vector3(0.006, 0.012, 0.17), _mats["steel_worn"])
	_box(backpack, "TopLid", Vector3(0.0, 0.425, 0.0), Vector3(0.185, 0.025, 0.30), _mats["fabric_dark"])
	_box(backpack, "HandleBar", Vector3(0.0, 0.452, 0.0), Vector3(0.10, 0.026, 0.035), _mats["rubber"])
	for i in 2:
		var sz := -0.090 if i == 0 else 0.090
		_box(backpack, "Strap_%d" % i, Vector3(-0.095, 0.220, sz), Vector3(0.018, 0.30, 0.038), _mats["rubber"])
	_box(backpack, "Buckle", Vector3(-0.106, 0.290, 0.0), Vector3(0.010, 0.035, 0.055), _mats["plastic_grey"])
	_box(backpack, "Zipper", Vector3(0.0, 0.432, 0.0), Vector3(0.155, 0.006, 0.012), _mats["chrome"])

	# Abrigo doblado sobre el banco B, con las mangas colgando por el borde
	# este. El cuerpo queda dentro del asiento para no flotar.
	var coat := Node3D.new()
	coat.name = "FoldedCoat"
	coat.position = Vector3(-0.05, bench_top + 0.045, 1.35)
	coat.rotation.y = -0.10
	root.add_child(coat)
	_box(coat, "Body", Vector3.ZERO, Vector3(0.44, 0.075, 0.36), _mats["uniform"])
	_box(coat, "Collar", Vector3(-0.08, 0.055, 0.12), Vector3(0.28, 0.035, 0.10), _mats["fabric_dark"], Vector3(0.0, 0.16, 0.0))
	_box(coat, "Fold", Vector3(0.06, 0.048, -0.04), Vector3(0.30, 0.022, 0.22), _mats["plastic_dark"])
	for i in 2:
		var sz := 0.075 if i == 0 else 0.145
		_box(coat, "Sleeve_%d" % i, Vector3(0.245, -0.175, sz), Vector3(0.085, 0.40, 0.115), _mats["uniform"], Vector3(0.0, 0.08, 0.05))
	_box(coat, "Cuff", Vector3(0.255, -0.365, 0.110), Vector3(0.090, 0.030, 0.120), _mats["fabric_dark"])
	for i in 2:
		_cylinder(
			coat, "Button_%d" % i, Vector3(-0.13, 0.043, -0.10 + float(i) * 0.10), 0.009, 0.006,
			_mats["plastic_grey"], Vector3(PI * 0.5, 0.0, 0.0), 8
		)

	# Revista y taza sobre la mesa real de la sala de espera.
	var magazine := Node3D.new()
	magazine.name = "WaitingMagazine"
	magazine.position = Vector3(2.05, table_top + 0.006, -0.24)
	magazine.rotation.y = -0.18
	root.add_child(magazine)
	_box(magazine, "Pages", Vector3.ZERO, Vector3(0.22, 0.008, 0.28), _mats["paper"])
	_box(magazine, "Cover", Vector3(0.0, 0.005, 0.0), Vector3(0.225, 0.003, 0.285), _mats["plastic_blue"])
	_box(magazine, "CoverStripe", Vector3(0.0, 0.007, 0.100), Vector3(0.225, 0.002, 0.055), _mats["badge_yellow"])

	var cup := Node3D.new()
	cup.name = "WaitingCup"
	cup.position = Vector3(2.42, table_top + 0.045, 0.02)
	root.add_child(cup)
	_cylinder(cup, "Body", Vector3.ZERO, 0.040, 0.090, _mats["ceramic"], Vector3.ZERO, 16)
	_cylinder(cup, "Rim", Vector3(0.0, 0.046, 0.0), 0.041, 0.006, _mats["ceramic"], Vector3.ZERO, 16)
	_cylinder(cup, "Coffee", Vector3(0.0, 0.040, 0.0), 0.033, 0.002, _mats["coffee"], Vector3.ZERO, 16)
	_torus(cup, "Handle", Vector3(0.046, 0.0, 0.0), 0.017, 0.028, _mats["ceramic"], Vector3(0.0, 0.0, PI * 0.5), 14, 5)
	_torus(
		root, "CoffeeRing", Vector3(2.22, table_top + 0.002, -0.10), 0.033, 0.043,
		_mats["coffee_stain"], Vector3.ZERO, 18, 4
	)

	# Mancha seca en la alfombra y papel caído en el suelo.
	_cylinder(
		root, "RugCoffeeStain", Vector3(1.60, floor_y + 0.034, -0.80), 0.105, 0.002,
		_mats["coffee_stain"], Vector3.ZERO, 18
	).scale = Vector3(1.35, 1.0, 0.78)
	_cylinder(
		root, "RugCoffeeCore", Vector3(1.57, floor_y + 0.035, -0.78), 0.060, 0.002,
		_mats["coffee"], Vector3.ZERO, 16
	).scale = Vector3(1.25, 1.0, 0.72)
	_box(
		root, "WaitingFloorPaper", Vector3(1.18, floor_y + 0.006, -1.00),
		Vector3(0.21, 0.002, 0.28), _mats["paper_aged"], Vector3(0.0, 0.34, 0.0)
	)
	_box(
		root, "WaitingFloorPaperB", Vector3(1.34, floor_y + 0.007, -0.92),
		Vector3(0.16, 0.002, 0.22), _mats["paper"], Vector3(0.0, -0.22, 0.0)
	)


# ------------------------------- N3 ---------------------------------------

func _build_n3() -> void:
	var root := _anchor("N3", "N3_StaffLockers", N3_POS)
	var floor_y := RECEPTION_FLOOR - N3_POS.y
	var panel_z := -0.205
	var door_z := -0.200

	# Interior abierto simulado delante de la taquilla real. El panel oscuro
	# cubre la puerta cerrada del GLB sin modificarla; el marco y el estante
	# crean profundidad sin añadir colisión.
	_box(root, "InteriorPanel", Vector3(0.0, -0.15, panel_z), Vector3(0.54, 1.64, 0.020), _mats["steel_dark"])
	_box(root, "FrameTop", Vector3(0.0, 0.67, panel_z - 0.012), Vector3(0.60, 0.045, 0.030), _mats["steel"])
	_box(root, "FrameBottom", Vector3(0.0, -0.97, panel_z - 0.012), Vector3(0.60, 0.045, 0.030), _mats["steel"])
	_box(root, "FrameLeft", Vector3(-0.28, -0.15, panel_z - 0.012), Vector3(0.045, 1.64, 0.030), _mats["steel"])
	_box(root, "FrameRight", Vector3(0.28, -0.15, panel_z - 0.012), Vector3(0.045, 1.64, 0.030), _mats["steel"])
	_box(root, "InteriorShelf", Vector3(0.0, -0.10, -0.300), Vector3(0.50, 0.025, 0.20), _mats["steel_worn"])
	_box(root, "ShelfLip", Vector3(0.0, -0.082, -0.395), Vector3(0.50, 0.035, 0.012), _mats["steel_worn"])
	_cylinder(
		root, "HangingRod", Vector3(0.0, 0.64, -0.280), 0.008, 0.48,
		_mats["chrome"], Vector3(0.0, 0.0, PI * 0.5), 8
	)

	# Puerta abierta con bisagra al oeste; gira hacia el pasillo (norte).
	var door := Node3D.new()
	door.name = "OpenLockerDoor"
	door.position = Vector3(-0.26, floor_y, door_z)
	door.rotation.y = 1.42
	root.add_child(door)
	_box(door, "Panel", Vector3(0.26, 0.95, 0.0), Vector3(0.52, 1.62, 0.025), _mats["steel_worn"])
	_box(door, "DoorRibA", Vector3(0.26, 0.55, -0.015), Vector3(0.46, 0.040, 0.008), _mats["steel"])
	_box(door, "DoorRibB", Vector3(0.26, 1.25, -0.015), Vector3(0.46, 0.040, 0.008), _mats["steel"])
	for i in 2:
		_cylinder(
			door, "Hinge_%d" % i, Vector3(0.0, 0.22 + float(i) * 1.25, 0.0), 0.012, 0.055,
			_mats["chrome"], Vector3(0.0, 0.0, PI * 0.5), 8
		)
	_box(door, "DoorHandle", Vector3(0.47, 1.00, -0.030), Vector3(0.035, 0.10, 0.022), _mats["chrome"])
	_box(door, "DoorLock", Vector3(0.47, 0.84, -0.030), Vector3(0.028, 0.045, 0.018), _mats["steel_worn"])

	# Uniforme colgado de una percha dentro de la taquilla.
	_torus(root, "HangerHook", Vector3(0.0, 0.630, -0.280), 0.028, 0.042, _mats["steel_worn"], Vector3(PI * 0.5, 0.0, 0.0), 12, 4)
	_box(root, "HangerBar", Vector3(0.0, 0.605, -0.280), Vector3(0.34, 0.018, 0.018), _mats["steel_worn"])
	_box(root, "UniformTorso", Vector3(0.0, 0.260, -0.285), Vector3(0.34, 0.46, 0.16), _mats["uniform"])
	_box(root, "UniformCollar", Vector3(0.0, 0.480, -0.285), Vector3(0.22, 0.055, 0.17), _mats["fabric_dark"])
	for i in 2:
		var sx := -0.205 if i == 0 else 0.205
		_box(root, "UniformSleeve_%d" % i, Vector3(sx, 0.240, -0.285), Vector3(0.10, 0.38, 0.12), _mats["uniform"], Vector3(0.0, 0.0, -0.06 if i == 0 else 0.06))
	_box(root, "UniformPocket", Vector3(-0.085, 0.300, -0.370), Vector3(0.10, 0.10, 0.008), _mats["fabric_dark"])
	_box(root, "UniformNameTag", Vector3(0.095, 0.320, -0.371), Vector3(0.055, 0.026, 0.004), _mats["badge_yellow"])
	_label(
		root, "UniformName", "NEXUS", Vector3(0.095, 0.320, -0.374), 9, 0.0010,
		Color(0.09, 0.09, 0.07, 1.0)
	)

	# Tarjeta, llave y foto personal sobre el estante y el fondo.
	_box(root, "StaffCard", Vector3(0.10, -0.085, -0.350), Vector3(0.090, 0.004, 0.060), _mats["card"])
	_box(root, "StaffCardStripe", Vector3(0.10, -0.082, -0.365), Vector3(0.090, 0.001, 0.012), _mats["badge_yellow"])
	_box(root, "ShelfKey", Vector3(-0.12, -0.083, -0.335), Vector3(0.012, 0.004, 0.050), _mats["chrome"], Vector3(0.0, 0.42, 0.0))
	_torus(root, "KeyRing", Vector3(-0.12, -0.081, -0.300), 0.014, 0.022, _mats["chrome"], Vector3(PI * 0.5, 0.0, 0.0), 10, 4)
	_box(root, "Polaroid", Vector3(-0.13, 0.160, -0.218), Vector3(0.072, 0.090, 0.004), _mats["paper"])
	_box(root, "PolaroidImage", Vector3(-0.13, 0.160, -0.221), Vector3(0.055, 0.065, 0.002), _mats["plastic_blue"])
	_box(root, "PolaroidTape", Vector3(-0.13, 0.205, -0.220), Vector3(0.030, 0.014, 0.003), _mats["tape_yellow"])

	# Nota manuscrita en el fondo interior, por encima del uniforme. Mira al
	# norte (hacia el pasillo).
	_box(root, "WarningNote", Vector3(0.0, 0.540, -0.218), Vector3(0.23, 0.110, 0.003), _mats["paper"])
	_label(
		root, "WarningNoteText", "NO SALGAS\nPOR RECEPCIÓN", Vector3(0.0, 0.540, -0.221), 12, 0.0014,
		Color(0.12, 0.025, 0.020, 1.0), Vector3(0.0, PI, 0.0)
	)
	_box(root, "NoteTapeA", Vector3(-0.085, 0.590, -0.220), Vector3(0.040, 0.016, 0.003), _mats["tape_yellow"], Vector3(0.0, 0.0, 0.28))
	_box(root, "NoteTapeB", Vector3(0.085, 0.590, -0.220), Vector3(0.040, 0.016, 0.003), _mats["tape_yellow"], Vector3(0.0, 0.0, -0.28))

	# Puerta caída en el suelo, reutilizando la malla real de Z10.
	var fallen := _reuse_from_base(
		_find_mesh("Z10Art/Z10Sector", "DET_Z10_LockerDoor"),
		root,
		"FallenLockerDoor",
		Vector3(0.80, floor_y + 0.010, -0.70),
		Vector3(0.0, 0.55, 0.0),
	)
	if fallen.get_child_count() == 0:
		_box(fallen, "FallbackDoor", Vector3(0.0, 0.025, 0.0), Vector3(0.52, 0.050, 0.90), _mats["steel_dark"])
	_box(fallen, "HazardStripe", Vector3(0.0, 0.105, 0.0), Vector3(0.42, 0.002, 0.080), _mats["tape_yellow"])
	_box(fallen, "MaintenanceTag", Vector3(0.0, 0.107, 0.150), Vector3(0.16, 0.002, 0.100), _mats["paper"])
	_box(root, "FallenDoorScuffA", Vector3(0.30, floor_y + 0.006, -0.72), Vector3(0.55, 0.002, 0.045), _mats["tape_yellow"], Vector3(0.0, 0.55, 0.0))
	_box(root, "FallenDoorScuffB", Vector3(0.92, floor_y + 0.006, -0.60), Vector3(0.40, 0.002, 0.035), _mats["steel_worn"], Vector3(0.0, 0.30, 0.0))
	_box(root, "FallenDoorTag", Vector3(1.08, floor_y + 0.012, -0.78), Vector3(0.075, 0.003, 0.050), _mats["card"], Vector3(0.0, 0.42, 0.0))


# ------------------------------- N8 ---------------------------------------

func _build_n8() -> void:
	var root := _anchor("N8", "N8_ServiceLink", N8_POS, "Z10")
	var floor_y := RECEPTION_FLOOR - N8_POS.y

	# Estante de pared con el registro de turno y un blíster de pilas vacío.
	# El tablero toca la pared norte para no quedar flotando.
	_box(root, "ShelfBoard", Vector3(-0.35, -0.080, -0.460), Vector3(0.92, 0.040, 0.240), _mats["steel_worn"])
	_box(root, "ShelfLip", Vector3(-0.35, -0.058, -0.342), Vector3(0.92, 0.035, 0.014), _mats["steel"])
	for i in 2:
		var bx := -0.76 if i == 0 else 0.06
		_box(root, "ShelfBracketV_%d" % i, Vector3(bx, -0.160, -0.555), Vector3(0.030, 0.160, 0.030), _mats["steel_dark"])
		_box(root, "ShelfBracketH_%d" % i, Vector3(bx, -0.085, -0.465), Vector3(0.030, 0.030, 0.190), _mats["steel_dark"])

	var logbook := Node3D.new()
	logbook.name = "ServiceLogbook"
	logbook.position = Vector3(-0.60, -0.035, -0.455)
	logbook.rotation.y = 0.14
	root.add_child(logbook)
	_box(logbook, "Cover", Vector3.ZERO, Vector3(0.27, 0.035, 0.19), _mats["plastic_blue"])
	_box(logbook, "Pages", Vector3(0.0, 0.016, 0.0), Vector3(0.255, 0.020, 0.18), _mats["paper_aged"])
	_box(logbook, "Spine", Vector3(-0.135, 0.0, 0.0), Vector3(0.012, 0.036, 0.19), _mats["tape_red"])
	_label(
		logbook, "LogbookTitle", "REGISTRO\nENLACE Z10", Vector3(0.0, 0.019, 0.0), 11, 0.0012,
		Color(0.11, 0.10, 0.075, 1.0), Vector3(-PI * 0.5, 0.0, 0.0)
	)
	_cylinder(
		root, "LogbookPen", Vector3(-0.15, -0.055, -0.390), 0.006, 0.13,
		_mats["plastic_blue"], Vector3(PI * 0.5, 0.0, 0.0), 8
	)

	var blister := Node3D.new()
	blister.name = "EmptyBatteryBlister"
	blister.position = Vector3(0.52, -0.030, -0.450)
	blister.rotation.y = -0.18
	root.add_child(blister)
	_box(blister, "Card", Vector3.ZERO, Vector3(0.16, 0.010, 0.11), _mats["card"])
	_box(blister, "Plastic", Vector3(0.0, 0.016, 0.0), Vector3(0.145, 0.022, 0.095), _mats["plastic_white"])
	for i in 4:
		var bx := -0.040 if i % 2 == 0 else 0.040
		var bz := -0.025 if i < 2 else 0.025
		_cylinder(
			blister, "EmptySocket_%d" % i, Vector3(bx, 0.030, bz), 0.015, 0.004,
			_mats["plastic_dark"], Vector3.ZERO, 10
		)
	_box(blister, "TornCorner", Vector3(0.062, 0.006, -0.043), Vector3(0.030, 0.004, 0.025), _mats["paper_aged"], Vector3(0.0, 0.0, 0.20))
	_label(
		blister, "BlisterLabel", "9V", Vector3(0.0, 0.026, 0.0), 10, 0.0010,
		Color(0.055, 0.055, 0.045, 1.0), Vector3(-PI * 0.5, 0.0, 0.0)
	)

	# Nota clavada en la pared, visible desde el pasillo (mira al sur).
	_box(root, "RadioWarningNote", Vector3(-0.15, 0.150, -0.400), Vector3(0.28, 0.180, 0.004), _mats["paper"])
	_label(
		root, "RadioWarningText", "NO CONFÍES\nEN LA RADIO", Vector3(-0.15, 0.150, -0.396), 16, 0.0015,
		Color(0.12, 0.025, 0.020, 1.0)
	)
	for i in 2:
		var tx := -0.245 if i == 0 else 0.055
		_box(root, "NoteTapeTop_%d" % i, Vector3(tx, 0.220, -0.398), Vector3(0.038, 0.015, 0.004), _mats["tape_yellow"], Vector3(0.0, 0.0, -0.20))

	# Radio muerta en el suelo, con la tapa de pilas abierta y dos pilas.
	var radio := Node3D.new()
	radio.name = "DeadServiceRadio"
	radio.position = Vector3(-0.58, floor_y + 0.040, -0.36)
	radio.rotation.y = 0.28
	root.add_child(radio)
	_box(radio, "Body", Vector3.ZERO, Vector3(0.24, 0.080, 0.16), _mats["plastic_dark"])
	_box(radio, "Faceplate", Vector3(0.0, 0.043, -0.006), Vector3(0.20, 0.010, 0.13), _mats["steel_worn"])
	_box(radio, "Speaker", Vector3(-0.055, 0.050, -0.071), Vector3(0.080, 0.030, 0.004), _mats["plastic_grey"])
	_box(radio, "Screen", Vector3(0.058, 0.051, -0.071), Vector3(0.045, 0.020, 0.004), _mats["screen_dead"])
	_cylinder(radio, "KnobA", Vector3(-0.095, 0.054, 0.050), 0.012, 0.018, _mats["plastic_grey"], Vector3.ZERO, 10)
	_cylinder(radio, "KnobB", Vector3(0.095, 0.054, 0.050), 0.010, 0.016, _mats["plastic_grey"], Vector3.ZERO, 10)
	_cylinder(radio, "Antenna", Vector3(-0.108, 0.150, 0.010), 0.0035, 0.180, _mats["rubber"], Vector3(0.0, 0.0, 0.18), 6)
	_box(radio, "BatteryCover", Vector3(0.18, 0.030, 0.04), Vector3(0.012, 0.070, 0.14), _mats["plastic_grey"], Vector3(0.0, 0.18, 0.0))
	_box(radio, "BatteryA", Vector3(-0.040, 0.050, -0.052), Vector3(0.030, 0.055, 0.030), _mats["plastic_blue"], Vector3(0.0, 0.0, PI * 0.5))
	_box(radio, "BatteryB", Vector3(0.040, 0.050, -0.052), Vector3(0.030, 0.055, 0.030), _mats["plastic_blue"], Vector3(0.0, 0.0, PI * 0.5))

	# Huella de sangre sobre la hoja oeste de la puerta del enlace. El pivote
	# gira el plano XY de _handprint para que mire al oeste (-X).
	var hand_pivot := Node3D.new()
	hand_pivot.name = "ServiceDoorHandprintPivot"
	hand_pivot.position = Vector3(1.305, 0.150, 2.050)
	hand_pivot.rotation.y = -PI * 0.5
	root.add_child(hand_pivot)
	_handprint(hand_pivot, "ServiceDoorHandprint", Vector3.ZERO, 0.10, 1.02)

	# Cinta rasgada en el marco de la puerta.
	_box(root, "TornTapeA", Vector3(1.290, 0.420, 2.390), Vector3(0.004, 0.120, 0.038), _mats["tape_yellow"], Vector3(0.0, 0.0, -0.12))
	_box(root, "TornTapeB", Vector3(1.292, 0.500, 2.345), Vector3(0.004, 0.070, 0.034), _mats["tape_red"], Vector3(0.0, 0.0, 0.28))



func _mesh_instance(
	parent: Node3D, node_name: String, mesh: Mesh, material: Material, pos: Vector3,
	rot := Vector3.ZERO
) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	mi.name = node_name
	mi.mesh = mesh
	mi.material_override = material
	mi.position = pos
	mi.rotation = rot
	parent.add_child(mi)
	_mesh_total += 1
	return mi


func _box(
	parent: Node3D, node_name: String, pos: Vector3, size: Vector3, material: Material,
	rot := Vector3.ZERO
) -> MeshInstance3D:
	var mesh := BoxMesh.new()
	mesh.size = size
	return _mesh_instance(parent, node_name, mesh, material, pos, rot)


func _cylinder(
	parent: Node3D, node_name: String, pos: Vector3, radius: float, height: float,
	material: Material, rot := Vector3.ZERO, sides := 12
) -> MeshInstance3D:
	var mesh := CylinderMesh.new()
	mesh.top_radius = radius
	mesh.bottom_radius = radius
	mesh.height = height
	mesh.radial_segments = sides
	mesh.rings = 1
	return _mesh_instance(parent, node_name, mesh, material, pos, rot)


func _torus(
	parent: Node3D, node_name: String, pos: Vector3, inner_radius: float, outer_radius: float,
	material: Material, rot := Vector3.ZERO, rings := 16, ring_segments := 6
) -> MeshInstance3D:
	var mesh := TorusMesh.new()
	mesh.inner_radius = inner_radius
	mesh.outer_radius = outer_radius
	mesh.rings = rings
	mesh.ring_segments = ring_segments
	return _mesh_instance(parent, node_name, mesh, material, pos, rot)


func _capsule(
	parent: Node3D, node_name: String, pos: Vector3, radius: float, height: float,
	material: Material, rot := Vector3.ZERO, radial_segments := 12, rings := 6
) -> MeshInstance3D:
	var mesh := CapsuleMesh.new()
	mesh.radius = radius
	mesh.height = height
	mesh.radial_segments = radial_segments
	mesh.rings = rings
	return _mesh_instance(parent, node_name, mesh, material, pos, rot)


func _sphere(
	parent: Node3D, node_name: String, pos: Vector3, radius: float, material: Material,
	scl := Vector3.ONE
) -> MeshInstance3D:
	var mesh := SphereMesh.new()
	mesh.radius = radius
	mesh.height = radius * 2.0
	mesh.radial_segments = 16
	mesh.rings = 8
	var instance := _mesh_instance(parent, node_name, mesh, material, pos)
	instance.scale = scl
	return instance


func _label(
	parent: Node3D, node_name: String, text: String, pos: Vector3, font_size: int,
	pixel_size: float, color: Color, rot := Vector3.ZERO
) -> Label3D:
	var label := Label3D.new()
	label.name = node_name
	label.text = text
	label.font_size = font_size
	label.pixel_size = pixel_size
	label.modulate = color
	label.outline_size = 3
	label.outline_modulate = Color(0.01, 0.01, 0.01, 0.75)
	label.position = pos
	label.rotation = rot
	parent.add_child(label)
	return label


func _find_mesh(art_path: String, mesh_name: String) -> MeshInstance3D:
	var art := get_parent().get_node_or_null(art_path) as Node3D
	if art == null:
		return null
	return art.find_child(mesh_name, true, false) as MeshInstance3D


## Copia una malla existente centrada en un pivote nuevo. El mesh importado se
## comparte; no se duplica la geometría ni se toca el GLB.
func _reuse_centered(
	source: MeshInstance3D, parent: Node3D, node_name: String, pos: Vector3, rot := Vector3.ZERO
) -> Node3D:
	var pivot := Node3D.new()
	pivot.name = node_name
	pivot.position = pos
	pivot.rotation = rot
	parent.add_child(pivot)
	if source == null or source.mesh == null:
		return pivot
	var copy := _source_mesh_instance(source, node_name + "_Mesh")
	copy.position = -source.mesh.get_aabb().get_center()
	pivot.add_child(copy)
	return pivot


## Copia una malla existente apoyando su centro de base en el pivote. Se usa
## para sillas volcadas: el pivote queda a la altura de apoyo y la rotación no
## entierra la malla en el suelo.
func _reuse_from_base(
	source: MeshInstance3D, parent: Node3D, node_name: String, pos: Vector3, rot := Vector3.ZERO
) -> Node3D:
	var pivot := Node3D.new()
	pivot.name = node_name
	pivot.position = pos
	pivot.rotation = rot
	parent.add_child(pivot)
	if source == null or source.mesh == null:
		return pivot
	var aabb := source.mesh.get_aabb()
	var center := aabb.get_center()
	var base_center := Vector3(center.x, aabb.position.y, center.z)
	var copy := _source_mesh_instance(source, node_name + "_Mesh")
	copy.position = -base_center
	pivot.add_child(copy)
	return pivot


func _source_mesh_instance(source: MeshInstance3D, node_name: String) -> MeshInstance3D:
	var copy := MeshInstance3D.new()
	copy.name = node_name
	copy.mesh = source.mesh
	copy.material_override = source.material_override
	copy.cast_shadow = source.cast_shadow
	copy.gi_mode = source.gi_mode
	for i in source.mesh.get_surface_count():
		var override := source.get_surface_override_material(i)
		if override != null:
			copy.set_surface_override_material(i, override)
	_mesh_total += 1
	return copy


# ---------------------------------------------------------------------------
# Detalles reutilizables
# ---------------------------------------------------------------------------

func _handprint(
	parent: Node3D, node_name: String, pos: Vector3, tilt: float, hand_scale: float
) -> void:
	var hand := Node3D.new()
	hand.name = node_name
	hand.position = pos
	hand.rotation.z = tilt
	hand.scale = Vector3.ONE * hand_scale
	parent.add_child(hand)
	_box(hand, "Palm", Vector3.ZERO, Vector3(0.108, 0.112, 0.0035), _mats["blood_hand"])
	_box(hand, "PalmHeel", Vector3(0.0, -0.074, 0.0), Vector3(0.094, 0.048, 0.0035), _mats["blood"])
	var fingers := [
		Vector3(-0.041, 0.094, 0.0),
		Vector3(-0.014, 0.106, 0.0),
		Vector3(0.013, 0.102, 0.0),
		Vector3(0.039, 0.086, 0.0),
	]
	for i in fingers.size():
		var finger_pos: Vector3 = fingers[i]
		var length := 0.066 - float(absf(float(i) - 1.5)) * 0.005
		_box(
			hand, "Finger_%d" % i,
			finger_pos + Vector3(0.0, length * 0.35, 0.0),
			Vector3(0.020, length, 0.0035), _mats["blood_hand"],
			Vector3(0.0, 0.0, 0.04 - float(i) * 0.035)
		)
	_box(hand, "Thumb", Vector3(-0.082, 0.010, 0.0), Vector3(0.024, 0.066, 0.0035), _mats["blood_hand"], Vector3(0.0, 0.0, -0.72))
	# Regueros secos bajo la mano.
	_box(hand, "DripA", Vector3(-0.025, -0.150, 0.0), Vector3(0.010, 0.090, 0.0030), _mats["blood_dark"])
	_box(hand, "DripB", Vector3(0.030, -0.125, 0.0), Vector3(0.007, 0.060, 0.0030), _mats["blood_dark"])


func _glass_crack(
	parent: Node3D, node_name: String, pos: Vector3, tilt: float, length: float
) -> void:
	var crack := Node3D.new()
	crack.name = node_name
	crack.position = pos
	crack.rotation.z = tilt
	parent.add_child(crack)
	_box(crack, "Main", Vector3.ZERO, Vector3(0.004, length, 0.0025), _mats["steel_worn"])
	_box(crack, "BranchA", Vector3(0.025, 0.055, 0.0), Vector3(0.003, length * 0.45, 0.0025), _mats["steel_worn"], Vector3(0.0, 0.0, 0.65))
	_box(crack, "BranchB", Vector3(-0.024, -0.030, 0.0), Vector3(0.003, length * 0.38, 0.0025), _mats["steel_worn"], Vector3(0.0, 0.0, -0.58))


func _fallback_toppled_chair(parent: Node3D, pos: Vector3, rot: Vector3) -> void:
	var chair := Node3D.new()
	chair.name = "FallbackChair"
	chair.position = pos
	chair.rotation = rot
	parent.add_child(chair)
	_box(chair, "Seat", Vector3.ZERO, Vector3(0.45, 0.06, 0.45), _mats["fabric_dark"])
	_box(chair, "Back", Vector3(0.0, 0.35, 0.22), Vector3(0.45, 0.55, 0.06), _mats["fabric_dark"])
	for i in 4:
		var lx := -0.18 if i % 2 == 0 else 0.18
		var lz := -0.18 if i < 2 else 0.18
		_box(chair, "Leg_%d" % i, Vector3(lx, -0.24, lz), Vector3(0.04, 0.42, 0.04), _mats["steel_dark"])
