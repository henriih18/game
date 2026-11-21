extends Node3D

## Fase 3A: recepción NEXUS y corredor principal.
## Pase artístico desacoplado de la lógica de juego. No mueve nodos existentes,
## no elimina interacciones y no añade colisiones a la decoración elevada.

const HDRI_PATH := "res://assets/HDRI/Instalaciones industriales y abandonadas/abandoned_workshop_2k.hdr"
const GEN := "res://assets/art/fm/generated/"
const KIT_GLB := "res://assets/models/fm/art3a1/level1_art3a1_kit.glb"
const DRESSING_GLB := "res://assets/models/fm/art3a2/level1_dressing.glb"
const GENERATOR_GLB := "res://assets/models/fm/props/industrial_generator.glb"
const TEX := "res://assets/texturas/"

var level: Node3D
var glb_root: Node3D
var _textures := {}
var _materials := {}
var _screens := {}
var _material_hits := 0
var _detail_meshes := 0

func apply(level_node: Node3D) -> void:
	level = level_node
	glb_root = level.glb_root
	_load_textures()
	_build_materials()
	_setup_environment()
	_tune_emergency_lights()
	_apply_material_overrides()
	_fix_security_wall()
	_load_kit()
	_load_dressing()
	_upgrade_storage_crates()
	_fix_prop_materials()
	_fix_office_access()
	_replace_maintenance_generator()
	_detail_boiler()
	_upgrade_loaded_screens()
	_replace_control_screen()
	_spawn_room_props()
	_build_reception_details()
	_build_corridor_details()
	_add_reflection_probes()
	_add_cinematic_lights()
	# Debe ejecutarse después de crear las luces: si se llama antes, no
	# encuentra los nodos ART_Corridor/ART_RoomFill y la atenuación no aplica.
	_dim_rooms_outside_reception()
	_apply_distance_culling()
	_compress_scene_albedos()
	_compress_scene_secondary_textures()
	print("ART_PASS ready materials=%d details=%d" % [_material_hits, _detail_meshes])

# ---------------------------------------------------------------- texturas

func _load_texture(path: String) -> Texture2D:
	if path.is_empty():
		return null
	var img := Image.new()
	var err := img.load(path)
	if err != OK:
		push_warning("ART_PASS no pudo cargar %s (error %s)" % [path, err])
		return null
	img.generate_mipmaps()
	return ImageTexture.create_from_image(img)

func _add_texture_set(key: String, albedo_path: String, normal_path: String, rough_path: String) -> void:
	_textures[key] = {
		"albedo": _load_texture(albedo_path),
		"normal": _load_texture(normal_path),
		"rough": _load_texture(rough_path),
	}

func _load_textures() -> void:
	_add_texture_set("floor",
		TEX + "Hormigon y cemento/concrete_floor_01_2k.blend/textures/concrete_floor_01_diff_2k.jpg",
		GEN + "gen_concrete_floor_01_normal.png",
		TEX + "Hormigon y cemento/concrete_floor_01_2k.blend/textures/concrete_floor_01_rough_2k.jpg")
	# Pared de hormigón pintado creada en la fase 2 y ya coherente con la
	# identidad visual del Nivel 1. Se conserva el yeso desgastado como set
	# independiente para parches y zonas dañadas.
	_add_texture_set("wall",
		"res://assets/art/fm/concrete_wall_albedo.png",
		"res://assets/art/fm/concrete_wall_normal.png",
		"res://assets/art/fm/concrete_wall_roughness.png")
	_add_texture_set("plaster",
		TEX + "Pintura y paredes/worn_plaster_wall_2k.blend/textures/worn_plaster_wall_diff_2k.jpg",
		GEN + "gen_worn_plaster_wall_normal.png",
		GEN + "gen_worn_plaster_wall_rough.png")
	_add_texture_set("wainscot",
		TEX + "Pintura y paredes/factory_wall_2k.blend/textures/factory_wall_diff_2k.jpg",
		GEN + "gen_factory_wall_normal.png",
		TEX + "Pintura y paredes/factory_wall_2k.blend/textures/factory_wall_rough_2k.jpg")
	_add_texture_set("steel",
		TEX + "Metal y oxidacion/rusty_metal_sheet_2k.blend/textures/rusty_metal_sheet_diff_2k.jpg",
		GEN + "gen_rusty_metal_sheet_normal_src.png",
		GEN + "gen_rusty_metal_sheet_rough_src.png")
	_add_texture_set("painted",
		TEX + "Metal y oxidacion/green_metal_rust_2k.blend/textures/green_metal_rust_diff_2k.jpg",
		GEN + "gen_green_metal_rust_normal_src.png",
		GEN + "gen_green_metal_rust_rough_src.png")
	_add_texture_set("wood",
		"res://assets/Modelos 3D/Mobiliario y almacenamiento/wooden_crate_01_2k.blend/textures/wooden_crate_01_diff_2k.jpg",
		GEN + "gen_wooden_crate_01_normal.png",
		GEN + "gen_wooden_crate_01_rough.png")
	_add_texture_set("concrete_panel",
		TEX + "Hormigon y cemento/concrete_wall_003_2k.blend/textures/concrete_wall_003_diff_2k.jpg",
		GEN + "gen_concrete_wall_003_normal.png",
		TEX + "Hormigon y cemento/concrete_wall_003_2k.blend/textures/concrete_wall_003_rough_2k.jpg")

# ---------------------------------------------------------------- materiales

func _make_pbr(label: String, tex_key: String, tint: Color, metallic: float, roughness: float, uv: Vector3, normal_scale: float = 1.0) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.resource_name = "ART_" + label
	var set: Dictionary = _textures.get(tex_key, {})
	if set.get("albedo") != null:
		m.albedo_texture = set["albedo"]
	m.albedo_color = tint
	m.metallic = metallic
	m.roughness = roughness
	if set.get("normal") != null:
		m.normal_enabled = true
		m.normal_texture = set["normal"]
		m.normal_scale = normal_scale
	if set.get("rough") != null:
		m.roughness_texture = set["rough"]
	m.uv1_scale = uv
	m.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
	return m

func _make_solid(label: String, color: Color, metallic: float, roughness: float) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.resource_name = "ART_" + label
	m.albedo_color = color
	m.metallic = metallic
	m.roughness = roughness
	m.metallic_specular = 0.45
	return m

func _make_emissive(label: String, color: Color, energy: float) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.resource_name = "ART_" + label
	m.albedo_color = color * 0.25
	m.emission_enabled = true
	m.emission = color
	m.emission_energy_multiplier = energy
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	return m

func _build_materials() -> void:
	_screens["green"] = _load_texture(GEN + "screen_green.png")
	_screens["amber"] = _load_texture(GEN + "screen_amber.png")
	_screens["cyan"] = _load_texture(GEN + "screen_cyan.png")
	_screens["extract"] = _load_texture(GEN + "screen_extract.png")
	_screens["elev"] = _load_texture(GEN + "screen_elev.png")
	_materials["steel"] = _make_pbr("steel", "steel", Color(0.60, 0.66, 0.74), 0.58, 1.0, Vector3(2.0, 2.0, 1.0))
	_materials["painted"] = _make_pbr("painted", "painted", Color(0.55, 0.70, 0.62), 0.05, 1.0, Vector3(1.5, 1.5, 1.0))
	_materials["wall"] = _make_pbr("wall", "wall", Color(0.96, 1.0, 0.97), 0.0, 1.0, Vector3(1.6, 1.6, 1.0))
	_materials["wall_dark"] = _make_pbr("wall_dark", "wall", Color(0.48, 0.52, 0.51), 0.0, 1.0, Vector3(1.6, 1.6, 1.0))
	_materials["wainscot"] = _make_pbr("wainscot", "wainscot", Color(0.30, 0.43, 0.38), 0.05, 0.56, Vector3(2.0, 2.0, 1.0))
	_materials["floor"] = _make_pbr("floor", "floor", Color(0.42, 0.50, 0.58), 0.0, 1.0, Vector3(3.0, 3.0, 1.0))
	_materials["floor"].clearcoat_enabled = false
	_materials["rack"] = _make_pbr("rack", "painted", Color(0.30, 0.46, 0.37), 0.10, 1.0, Vector3(1.5, 1.5, 1.0))
	_materials["wood"] = _make_pbr("wood", "wood", Color(0.38, 0.28, 0.19), 0.0, 0.72, Vector3(1.5, 1.5, 1.0))
	_materials["concrete_panel"] = _make_pbr("concrete_panel", "concrete_panel", Color(0.42, 0.48, 0.54), 0.0, 0.85, Vector3(2.0, 2.0, 1.0))
	_materials["rubber"] = _make_solid("rubber", Color(0.035, 0.040, 0.045), 0.0, 0.84)
	_materials["paper"] = _make_solid("paper", Color(0.72, 0.69, 0.62), 0.0, 0.90)
	_materials["hazard"] = _make_solid("hazard", Color(0.72, 0.42, 0.055), 0.0, 0.66)
	_materials["emissive_cool"] = _make_emissive("emissive_cool", Color(0.30, 0.78, 0.95), 2.4)
	_materials["emissive_warm"] = _make_emissive("emissive_warm", Color(1.0, 0.28, 0.08), 1.6)
	_materials["emissive_strip"] = _make_emissive("emissive_strip", Color(0.18, 0.62, 0.78), 0.85)
	_materials["glass"] = _make_glass()
	_materials["detail_steel"] = _make_pbr("detail_steel", "steel", Color(0.66, 0.71, 0.78), 0.55, 1.0, Vector3(1.8, 1.8, 1.0))
	_materials["detail_painted"] = _make_pbr("detail_painted", "painted", Color(0.52, 0.68, 0.60), 0.04, 1.0, Vector3(1.6, 1.6, 1.0))
	_materials["detail_dark"] = _make_pbr("detail_dark", "wainscot", Color(0.27, 0.39, 0.34), 0.06, 0.62, Vector3(2.0, 2.0, 1.0))
	_materials["detail_duct"] = _make_pbr("detail_duct", "wainscot", Color(0.09, 0.13, 0.12), 0.10, 0.74, Vector3(1.8, 1.8, 1.0))
	_materials["boiler_skin"] = _make_pbr("boiler_skin", "steel", Color(0.38, 0.28, 0.23), 0.42, 1.0, Vector3(1.2, 1.2, 1.0))
	_materials["crate_card"] = _make_pbr("crate_card", "wood", Color(0.56, 0.44, 0.30), 0.0, 1.0, Vector3(1.0, 1.0, 1.0))
	_materials["crate_pale"] = _make_pbr("crate_pale", "wood", Color(0.70, 0.62, 0.48), 0.0, 1.0, Vector3(1.0, 1.0, 1.0))
	_materials["crate_dark"] = _make_pbr("crate_dark", "wood", Color(0.34, 0.28, 0.21), 0.0, 1.0, Vector3(1.0, 1.0, 1.0))

func _make_glass() -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.resource_name = "ART_glass"
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.albedo_color = Color(0.12, 0.22, 0.28, 0.10)
	m.metallic = 0.0
	m.roughness = 0.085
	m.refraction_enabled = true
	m.refraction_scale = 0.012
	m.cull_mode = BaseMaterial3D.CULL_DISABLED
	m.shading_mode = BaseMaterial3D.SHADING_MODE_PER_PIXEL
	m.clearcoat_enabled = true
	m.clearcoat = 0.28
	m.clearcoat_roughness = 0.12
	return m

# ---------------------------------------------------------------- entorno

func _has_property(obj: Object, name: String) -> bool:
	for p in obj.get_property_list():
		if p.name == name:
			return true
	return false

func _setup_environment() -> void:
	var world := level.find_child("Level1World", true, false) as WorldEnvironment
	if world == null or world.environment == null:
		return
	var env := world.environment
	var sky := Sky.new()
	sky.radiance_size = Sky.RADIANCE_SIZE_256
	var hdr_img := Image.new()
	if hdr_img.load(HDRI_PATH) == OK:
		var hdr_tex := ImageTexture.create_from_image(hdr_img)
		var pano := PanoramaSkyMaterial.new()
		pano.panorama = hdr_tex
		if _has_property(pano, "energy_multiplier"):
			pano.set("energy_multiplier", 0.35)
		sky.sky_material = pano
	else:
		var proc := ProceduralSkyMaterial.new()
		proc.sky_top_color = Color(0.012, 0.026, 0.040)
		proc.sky_horizon_color = Color(0.070, 0.105, 0.135)
		proc.ground_bottom_color = Color(0.010, 0.012, 0.015)
		proc.ground_horizon_color = Color(0.040, 0.055, 0.070)
		if _has_property(proc, "sky_energy_multiplier"):
			proc.set("sky_energy_multiplier", 0.55)
		sky.sky_material = proc
	env.sky = sky
	env.background_mode = Environment.BG_SKY
	env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	env.reflected_light_source = Environment.REFLECTION_SOURCE_SKY
	# Fuera de recepción la lectura debe depender de la linterna y de unas
	# pocas emergencias locales. El ambiente de cielo queda casi anulado.
	env.ambient_light_energy = 0.035
	if _has_property(env, "ambient_light_sky_contribution"):
		env.ambient_light_sky_contribution = 0.45
	if _has_property(env, "background_energy_multiplier"):
		env.background_energy_multiplier = 0.20
	env.tonemap_mode = Environment.TONE_MAPPER_AGX
	env.tonemap_exposure = 1.05
	env.ssao_enabled = true
	env.ssao_radius = 1.15
	env.ssao_intensity = 1.25
	env.ssao_power = 1.35
	env.ssr_enabled = true
	env.ssr_max_steps = 40
	env.ssr_fade_in = 0.15
	env.ssr_fade_out = 2.0
	env.ssr_depth_tolerance = 0.25
	env.ssil_enabled = true
	env.ssil_radius = 2.0
	env.ssil_intensity = 1.2
	env.ssil_sharpness = 0.98
	env.ssil_normal_rejection = 1.0
	env.glow_enabled = true
	env.glow_intensity = 0.18
	env.glow_bloom = 0.03
	env.glow_hdr_threshold = 1.45
	env.fog_enabled = true
	env.fog_light_color = Color(0.07, 0.10, 0.13)
	env.fog_light_energy = 0.32
	env.fog_density = 0.005
	env.volumetric_fog_enabled = true
	env.volumetric_fog_density = 0.012
	env.volumetric_fog_albedo = Color(0.55, 0.65, 0.78)
	env.volumetric_fog_emission = Color(0.0, 0.0, 0.0)
	env.volumetric_fog_emission_energy = 0.0
	env.volumetric_fog_anisotropy = 0.35
	env.volumetric_fog_length = 38.0
	env.volumetric_fog_detail_spread = 1.6
	env.volumetric_fog_ambient_inject = 0.08
	env.volumetric_fog_sky_affect = 0.0
	env.adjustment_enabled = true
	env.adjustment_contrast = 1.06
	env.adjustment_saturation = 1.04
	env.adjustment_brightness = 1.02

func _tune_emergency_lights() -> void:
	var lights = level.get("_emergency_lights")
	var bases = level.get("_emergency_base_energy")
	if not (lights is Array):
		return
	for i in range(lights.size()):
		var l = lights[i]
		if not is_instance_valid(l):
			continue
		var base := float(l.light_energy)
		var tuned := base * 0.52
		if bases is Array and i < bases.size():
			base = float(bases[i])
			tuned = base * 0.52
			# El parpadeo recalcula la energía cada frame desde este array.
			# Atenuar sólo light_energy se perdía en el siguiente frame.
			bases[i] = tuned
		l.light_energy = tuned
		l.light_color = l.light_color.lerp(Color(1.0, 0.58, 0.30), 0.10)
		l.light_volumetric_fog_energy = 0.28
	for lens in level.find_children("*EmergencyLight*_LENS", "MeshInstance3D", true, false):
		var mi := lens as MeshInstance3D
		if mi and mi.mesh:
			var mat := mi.get_active_material(0) as StandardMaterial3D
			if mat and mat.emission_enabled:
				mat.emission_energy_multiplier *= 0.20

# ---------------------------------------------------------------- materiales GLB

func _material_key(mat: Material) -> String:
	var n := mat.resource_name
	if n.is_empty():
		return ""
	var dot := n.find(".")
	if dot > 0:
		n = n.substr(0, dot)
	return n

func _copy_pbr(dst: StandardMaterial3D, src_key: String, tint: Color, metallic: float, roughness: float, uv: Vector3, normal_scale: float = 1.0, clearcoat: float = 0.0, triplanar: bool = true) -> void:
	var src := _materials.get(src_key) as StandardMaterial3D
	if src == null:
		return
	dst.albedo_texture = src.albedo_texture
	dst.albedo_color = tint
	dst.metallic = metallic
	dst.roughness = roughness
	dst.roughness_texture = src.roughness_texture
	dst.normal_enabled = src.normal_enabled
	dst.normal_texture = src.normal_texture
	dst.normal_scale = normal_scale
	var use_triplanar := triplanar
	# Los props tienen UVs propias: el triplanar sólo es necesario en las
	# grandes superficies arquitectónicas sin UV del GLB.
	if use_triplanar and src_key in ["steel", "painted", "wood", "rack"]:
		use_triplanar = false
	dst.uv1_triplanar = use_triplanar
	dst.uv1_world_triplanar = use_triplanar
	if use_triplanar:
		# Escala métrica uniforme: evita el estiramiento de las superficies
		# arquitectónicas que no tienen UV utilizables en el GLB.
		var s := 0.55
		match src_key:
			"floor":
				s = 0.45
			"wall", "wall_dark":
				s = 0.32
			"wainscot":
				s = 0.60
			"steel":
				s = 0.70
			"painted":
				s = 0.65
			"wood":
				s = 0.75
			"concrete_panel":
				s = 0.50
			"rack":
				s = 0.65
		dst.uv1_scale = Vector3(s, s, s)
	else:
		dst.uv1_scale = uv
	dst.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
	dst.emission_enabled = false
	dst.clearcoat_enabled = clearcoat > 0.0
	if clearcoat > 0.0:
		dst.clearcoat = clearcoat
		dst.clearcoat_roughness = 0.10

func _set_solid(dst: StandardMaterial3D, color: Color, metallic: float, roughness: float) -> void:
	dst.albedo_texture = null
	dst.normal_enabled = false
	dst.roughness_texture = null
	dst.albedo_color = color
	dst.metallic = metallic
	dst.roughness = roughness
	dst.metallic_specular = 0.42
	dst.emission_enabled = false
	dst.uv1_scale = Vector3.ONE

func _set_glass(dst: StandardMaterial3D) -> void:
	dst.albedo_texture = null
	dst.normal_enabled = false
	dst.roughness_texture = null
	dst.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	dst.albedo_color = Color(0.12, 0.22, 0.28, 0.10)
	dst.metallic = 0.0
	dst.roughness = 0.085
	dst.refraction_enabled = true
	dst.refraction_scale = 0.012
	dst.cull_mode = BaseMaterial3D.CULL_DISABLED
	dst.shading_mode = BaseMaterial3D.SHADING_MODE_PER_PIXEL
	dst.clearcoat_enabled = true
	dst.clearcoat = 0.28
	dst.clearcoat_roughness = 0.12

func _set_shard(dst: StandardMaterial3D) -> void:
	# Esquirlas de vidrio grueso: translúcidas, pero con color y cuerpo
	# suficientes para leerse sobre el suelo oscuro.
	dst.albedo_texture = null
	dst.normal_enabled = false
	dst.roughness_texture = null
	dst.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	dst.albedo_color = Color(0.14, 0.30, 0.28, 0.48)
	dst.metallic = 0.0
	dst.roughness = 0.12
	dst.metallic_specular = 0.60
	dst.cull_mode = BaseMaterial3D.CULL_DISABLED
	dst.shading_mode = BaseMaterial3D.SHADING_MODE_PER_PIXEL
	dst.clearcoat_enabled = true
	dst.clearcoat = 0.45
	dst.clearcoat_roughness = 0.06
	dst.emission_enabled = false

func _set_water(dst: StandardMaterial3D) -> void:
	# Superficies de agua estancada: oscuras, muy lisas y con transparencia
	# suficiente para leer el fondo sin convertirse en espejos negros.
	dst.albedo_texture = null
	dst.normal_enabled = false
	dst.roughness_texture = null
	dst.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	dst.albedo_color = Color(0.028, 0.052, 0.054, 0.42)
	dst.metallic = 0.0
	dst.roughness = 0.055
	dst.metallic_specular = 0.55
	dst.cull_mode = BaseMaterial3D.CULL_DISABLED
	dst.shading_mode = BaseMaterial3D.SHADING_MODE_PER_PIXEL
	dst.refraction_enabled = true
	dst.refraction_scale = 0.020
	dst.clearcoat_enabled = true
	dst.clearcoat = 0.55
	dst.clearcoat_roughness = 0.04
	dst.emission_enabled = false

func _set_mirror(dst: StandardMaterial3D, tint: Color) -> void:
	# Un espejo perfectamente liso quema la linterna en un blob blanco.
	# Un acabado de acero pulido difumina el reflejo sin perder la lectura.
	dst.albedo_texture = null
	dst.normal_enabled = false
	dst.roughness_texture = null
	dst.transparency = BaseMaterial3D.TRANSPARENCY_DISABLED
	dst.albedo_color = tint
	dst.metallic = 0.62
	dst.roughness = 0.22
	dst.metallic_specular = 0.35
	dst.cull_mode = BaseMaterial3D.CULL_BACK
	dst.emission_enabled = false

func _set_screen(dst: StandardMaterial3D, color: Color, energy: float) -> void:
	dst.albedo_texture = null
	dst.normal_enabled = false
	dst.roughness_texture = null
	dst.albedo_color = Color(0.012, 0.022, 0.024)
	dst.metallic = 0.0
	dst.roughness = 0.24
	dst.emission_enabled = true
	dst.emission = color
	dst.emission_energy_multiplier = energy

func _set_screen_texture(dst: StandardMaterial3D, tex_key: String, energy: float) -> void:
	var tex: Texture2D = _screens.get(tex_key)
	if tex == null:
		_set_screen(dst, Color(0.14, 0.62, 0.56), energy)
		return
	dst.albedo_texture = tex
	dst.albedo_color = Color.WHITE
	dst.metallic = 0.05
	dst.roughness = 0.20
	dst.normal_enabled = false
	dst.roughness_texture = null
	dst.emission_enabled = true
	dst.emission = Color.WHITE
	dst.emission_texture = tex
	dst.emission_energy_multiplier = energy
	dst.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
	dst.uv1_scale = Vector3.ONE

func _override_material(mat: Material) -> void:
	if not (mat is StandardMaterial3D):
		return
	var dst := mat as StandardMaterial3D
	var key := _material_key(dst)
	if key.begins_with("NEXUS_V05_MAT_Floor_Worn"):
		_copy_pbr(dst, "floor", Color(0.42, 0.50, 0.58), 0.0, 1.0, Vector3(3.0, 3.0, 1.0), 1.0, 0.0)
	elif key.begins_with("NEXUS_V05_MAT_Rec_Floor"):
		_copy_pbr(dst, "floor", Color(0.42, 0.50, 0.58), 0.0, 1.0, Vector3(3.0, 3.0, 1.0), 1.0, 0.0)
	elif key.begins_with("NEXUS_V05_MAT_Counter_Front"):
		_copy_pbr(dst, "painted", Color(0.24, 0.38, 0.32), 0.10, 0.56, Vector3(1.5, 1.5, 1.0))
	elif key.begins_with("NEXUS_V05_MAT_Counter_Reveal"):
		_copy_pbr(dst, "steel", Color(0.46, 0.52, 0.58), 0.70, 0.48, Vector3(1.4, 1.4, 1.0))
	elif key.begins_with("NEXUS_V05_MAT_Counter_Top"):
		_copy_pbr(dst, "wood", Color(0.34, 0.25, 0.17), 0.0, 0.58, Vector3(1.2, 1.2, 1.0))
	elif key.begins_with("NEXUS_V05_MAT_Rec_Ceiling"):
		_copy_pbr(dst, "wall_dark", Color(0.48, 0.52, 0.51), 0.0, 1.0, Vector3(1.6, 1.6, 1.0))
	elif key.begins_with("NEXUS_V05_MAT_Rec_Painted_Green"):
		_copy_pbr(dst, "wainscot", Color(0.30, 0.43, 0.38), 0.05, 0.56, Vector3(2.0, 2.0, 1.0))
	elif key.begins_with("NEXUS_V05_MAT_Rec_Wood"):
		_copy_pbr(dst, "wood", Color(0.34, 0.25, 0.17), 0.0, 0.62, Vector3(1.2, 1.2, 1.0))
	elif key.begins_with("NEXUS_V05_MAT_Baseboard"):
		_copy_pbr(dst, "steel", Color(0.18, 0.22, 0.25), 0.55, 0.60, Vector3(1.5, 1.5, 1.0))
	elif key.begins_with("NEXUS_V05_MAT_CableTray"):
		_copy_pbr(dst, "steel", Color(0.42, 0.48, 0.55), 0.75, 0.52, Vector3(1.2, 1.2, 1.0))
	elif key.begins_with("NEXUS_V05_MAT_Conduit"):
		_copy_pbr(dst, "steel", Color(0.44, 0.50, 0.57), 0.70, 0.52, Vector3(1.2, 1.2, 1.0))
	elif key.begins_with("NEXUS_V05_MAT_Rec_Wainscot"):
		_copy_pbr(dst, "wainscot", Color(0.30, 0.43, 0.38), 0.05, 0.56, Vector3(2.0, 2.0, 1.0))
	elif key.begins_with("NEXUS_V05_MAT_Rec_Wall"):
		_copy_pbr(dst, "wall", Color(0.96, 1.0, 0.97), 0.0, 1.0, Vector3(1.6, 1.6, 1.0))
	elif key.begins_with("NEXUS_Concrete_Dark"):
		_copy_pbr(dst, "wall_dark", Color(0.48, 0.52, 0.51), 0.0, 1.0, Vector3(1.6, 1.6, 1.0))
	elif key.begins_with("NEXUS_Concrete"):
		_copy_pbr(dst, "wall", Color(0.96, 1.0, 0.97), 0.0, 1.0, Vector3(1.6, 1.6, 1.0))
	elif key.begins_with("NEXUS_Painted_Metal"):
		_copy_pbr(dst, "painted", Color(0.55, 0.70, 0.62), 0.05, 1.0, Vector3(1.5, 1.5, 1.0))
	elif key.begins_with("NEXUS_V05_MAT_Pipe_Red"):
		_copy_pbr(dst, "steel", Color(0.72, 0.13, 0.10), 0.18, 0.90, Vector3(1.0, 1.0, 1.0))
	elif key.begins_with("NEXUS_Steel"):
		_copy_pbr(dst, "steel", Color(0.60, 0.66, 0.74), 0.58, 1.0, Vector3(2.0, 2.0, 1.0))
	elif key.begins_with("NEXUS_Rack_Paint"):
		_copy_pbr(dst, "rack", Color(0.30, 0.46, 0.37), 0.10, 1.0, Vector3(1.5, 1.5, 1.0))
	elif key.begins_with("NEXUS_V05_MAT_Galv_Dark"):
		_copy_pbr(dst, "steel", Color(0.22, 0.26, 0.30), 0.52, 0.90, Vector3(1.5, 1.5, 1.0))
	elif key.begins_with("NEXUS_V05_MAT_Galv"):
		_copy_pbr(dst, "steel", Color(0.45, 0.50, 0.56), 0.52, 0.90, Vector3(1.5, 1.5, 1.0))
	elif key.begins_with("NEXUS_OffWhite"):
		_copy_pbr(dst, "wall", Color(0.70, 0.74, 0.72), 0.0, 1.0, Vector3(1.6, 1.6, 1.0))
	elif key.begins_with("NEXUS_Clinical"):
		_copy_pbr(dst, "wall", Color(0.82, 0.86, 0.84), 0.0, 0.92, Vector3(1.6, 1.6, 1.0))
	elif key.begins_with("NEXUS_Debris"):
		_copy_pbr(dst, "concrete_panel", Color(0.38, 0.35, 0.32), 0.0, 0.92, Vector3(1.2, 1.2, 1.0))
	elif key.begins_with("NEXUS_Dark_Metal"):
		_copy_pbr(dst, "steel", Color(0.13, 0.15, 0.17), 0.85, 0.60, Vector3(1.8, 1.8, 1.0))
	elif key.begins_with("NEXUS_GrillDark"):
		_copy_pbr(dst, "steel", Color(0.14, 0.16, 0.17), 0.80, 0.62, Vector3(1.8, 1.8, 1.0))
	elif key.begins_with("wooden_crate_02"):
		_copy_pbr(dst, "wood", Color(0.62, 0.48, 0.32), 0.0, 1.0, Vector3(1.0, 1.0, 1.0))
	elif key.begins_with("industrial_pastic_container") or key.begins_with("plastic_container"):
		_set_solid(dst, Color(0.09, 0.15, 0.19), 0.0, 0.52)
	elif key.begins_with("plastic_crate_01"):
		_set_solid(dst, Color(0.12, 0.22, 0.16), 0.0, 0.58)
	elif key.begins_with("NEXUS_Wood"):
		_copy_pbr(dst, "wood", Color(0.38, 0.28, 0.19), 0.0, 0.72, Vector3(1.5, 1.5, 1.0))
	elif key.begins_with("NEXUS_Glass"):
		_set_glass(dst)
	elif key.begins_with("NEXUS_Water") or key.begins_with("NEXUS_Meltwater"):
		_set_water(dst)
	elif key.begins_with("NEXUS_V05_MAT_Shard"):
		_set_shard(dst)
	elif key.begins_with("NEXUS_Rubber"):
		_set_solid(dst, Color(0.035, 0.040, 0.045), 0.0, 0.84)
	elif key.begins_with("NEXUS_V05_MAT_Sign_Battery"):
		_set_solid(dst, Color(0.015, 0.030, 0.032), 0.0, 0.38)
		dst.emission_enabled = true
		dst.emission = Color(0.035, 0.22, 0.20)
		dst.emission_energy_multiplier = 0.35
	elif key.begins_with("NEXUS_L1_MAT_Paper"):
		_set_solid(dst, Color(0.72, 0.69, 0.62), 0.0, 0.90)
	elif key.begins_with("NEXUS_Rug_Dark"):
		_set_solid(dst, Color(0.075, 0.095, 0.115), 0.0, 0.94)
	elif key.begins_with("NEXUS_V05_MAT_ExtractGlow"):
		_set_screen(dst, Color(0.14, 0.86, 0.56), 1.25)
	elif key.begins_with("NEXUS_V05_MAT_ExtractScreen"):
		_set_screen_texture(dst, "extract", 0.85)
	elif key.begins_with("NEXUS_V05_MAT_Elev_Screen"):
		_set_screen_texture(dst, "elev", 0.65)
	elif key.begins_with("NEXUS_Screen"):
		_set_screen_texture(dst, "cyan", 0.55)
	elif key.begins_with("television_02"):
		_set_screen_texture(dst, "cyan", 0.45)
		dst.uv1_scale = Vector3(1.0, 1.0, 1.0)
	elif key.begins_with("NEXUS_CorridorLight"):
		dst.emission_enabled = true
		dst.emission_energy_multiplier = minf(dst.emission_energy_multiplier, 1.15)
		dst.albedo_color = Color(0.12, 0.10, 0.06)
	elif key.begins_with("industrial_wall_lamp"):
		dst.emission_enabled = true
		dst.emission_energy_multiplier = minf(dst.emission_energy_multiplier, 3.0)
		dst.albedo_color = Color(0.30, 0.32, 0.34)
	elif "mirror" in key.to_lower():
		var mirror_tint := Color(0.44, 0.49, 0.52)
		if key.contains("ELEV"):
			mirror_tint = Color(0.38, 0.43, 0.46)
		_set_mirror(dst, mirror_tint)
		if key.contains("ELEV"):
			dst.roughness = 0.38
			dst.metallic = 0.45
	else:
		return
	_material_hits += 1

func _apply_material_overrides() -> void:
	var seen := {}
	for node in glb_root.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi == null or mi.mesh == null:
			continue
		for i in range(mi.mesh.get_surface_count()):
			var mat := mi.mesh.surface_get_material(i)
			if mat == null:
				continue
			var id := mat.get_instance_id()
			if seen.has(id):
				continue
			seen[id] = true
			_override_material(mat)

# ---------------------------------------------------------------- luces

func _add_spot(light_name: String, pos: Vector3, target: Vector3, color: Color, energy: float, range: float, angle: float, shadow: bool, fog_energy: float) -> SpotLight3D:
	var l := SpotLight3D.new()
	l.name = light_name
	l.position = pos
	l.light_color = color
	l.light_energy = energy
	l.spot_range = range
	l.spot_angle = angle
	l.spot_attenuation = 1.15
	l.spot_angle_attenuation = 0.85
	l.light_size = 0.18
	l.shadow_enabled = shadow
	l.shadow_bias = 0.04
	l.light_volumetric_fog_energy = fog_energy
	add_child(l)
	l.look_at(target, Vector3.UP)
	return l

func _add_omni(light_name: String, pos: Vector3, color: Color, energy: float, range: float, shadow: bool) -> OmniLight3D:
	var l := OmniLight3D.new()
	l.name = light_name
	l.position = pos
	l.light_color = color
	l.light_energy = energy
	l.omni_range = range
	l.omni_attenuation = 1.0
	l.shadow_enabled = shadow
	l.shadow_bias = 0.05
	l.light_volumetric_fog_energy = 0.55
	add_child(l)
	return l

func _add_cinematic_lights() -> void:
	# Recepción: clave fría desde el techo, relleno frío y un acento cálido de mostrador.
	_add_spot("ART_ReceptionKey", Vector3(-12.0, -1.84, -5.6), Vector3(-12.0, -5.4, -7.4), Color(0.70, 0.84, 1.0), 3.4, 14.0, 60.0, true, 2.0)
	_add_spot("ART_ReceptionCounter", Vector3(-12.0, -1.86, -8.6), Vector3(-12.0, -4.8, -7.5), Color(1.0, 0.56, 0.28), 1.2, 7.0, 52.0, false, 0.9)
	_add_omni("ART_ReceptionFill", Vector3(-12.0, -3.4, -2.9), Color(0.46, 0.62, 0.92), 1.05, 9.0, false)
	_add_omni("ART_ReceptionBackFill", Vector3(-18.0, -3.1, -9.6), Color(0.40, 0.56, 0.82), 0.65, 7.0, false)
	_add_omni("ART_ReceptionBackWash", Vector3(-12.0, -3.2, -10.7), Color(0.56, 0.70, 1.0), 1.9, 7.5, false)
	_add_spot("ART_ReceptionWallWash", Vector3(-12.0, -1.90, -9.8), Vector3(-12.0, -3.6, -11.55), Color(0.62, 0.76, 1.0), 2.2, 7.0, 68.0, false, 0.8)
	_add_omni("ART_ReceptionLeftWash", Vector3(-19.0, -3.2, -6.0), Color(0.52, 0.66, 0.92), 0.80, 6.0, false)
	_add_omni("ART_ReceptionCounterGlow", Vector3(-12.0, -4.72, -7.35), Color(0.35, 0.70, 0.95), 0.45, 3.2, false)
	_add_spot("ART_ReceptionLinear", Vector3(-12.0, -1.86, -8.40), Vector3(-12.0, -5.15, -8.0), Color(0.78, 0.86, 1.0), 2.0, 7.5, 55.0, false, 1.6)

	# Fuera de recepción no se añaden focos ni rellenos artificiales: la
	# iluminación local son las luminarias de emergencia y la linterna.

func _add_reflection_probes() -> void:
	_add_probe("ART_RP_Reception", Vector3(-12.0, -3.55, -6.7), Vector3(16.0, 4.0, 10.0))
	_add_probe("ART_RP_Corridor", Vector3(0.0, -3.55, 0.0), Vector3(44.0, 4.0, 4.0))

func _add_probe(probe_name: String, pos: Vector3, size: Vector3) -> void:
	var p := ReflectionProbe.new()
	p.name = probe_name
	p.position = pos
	p.size = size
	p.interior = true
	p.box_projection = true
	p.enable_shadows = false
	p.update_mode = ReflectionProbe.UPDATE_ONCE
	p.max_distance = 30.0
	p.blend_distance = 1.0
	add_child(p)

# ---------------------------------------------------------------- geometría

func _box(parts: Array, pos: Vector3, size: Vector3, basis: Basis = Basis()) -> void:
	var m := BoxMesh.new()
	m.size = size
	parts.append([m, Transform3D(basis, pos)])

func _cyl(parts: Array, pos: Vector3, radius: float, height: float, basis: Basis = Basis(), segments: int = 16) -> void:
	var m := CylinderMesh.new()
	m.top_radius = radius
	m.bottom_radius = radius
	m.height = height
	m.radial_segments = segments
	m.rings = 1
	parts.append([m, Transform3D(basis, pos)])

func _bolt(parts: Array, pos: Vector3, basis: Basis = Basis()) -> void:
	_cyl(parts, pos, 0.011, 0.022, basis, 6)

func _merge(name: String, parts: Array, mat: Material, parent: Node3D, cast_shadow: bool = true) -> MeshInstance3D:
	if parts.is_empty():
		return null
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	for part in parts:
		st.append_from(part[0], 0, part[1])
	var mesh := st.commit()
	if mesh == null:
		return null
	var mi := MeshInstance3D.new()
	mi.name = name
	mi.mesh = mesh
	mi.material_override = mat
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON if cast_shadow else GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	parent.add_child(mi)
	_detail_meshes += 1
	return mi

func _add_column_collider(x: float, z: float) -> void:
	var body := StaticBody3D.new()
	body.name = "ART_ColumnCol_%s_%s" % [int(x), int(z)]
	body.position = Vector3(x, -3.95, z)
	var shape := BoxShape3D.new()
	shape.size = Vector3(0.22, 3.40, 0.28)
	var cs := CollisionShape3D.new()
	cs.shape = shape
	body.add_child(cs)
	add_child(body)

func _fix_security_wall() -> void:
	# El muro de vigilancia usa televisiones antiguas cuya pantalla no se lee.
	# Se sustituyen visualmente por monitores planos con contenido legible.
	var index := 0
	for node in glb_root.find_children("*SEC_WALL_*_02", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi == null:
			continue
		var pos := mi.global_position
		mi.visible = false
		_spawn_wall_monitor(pos + Vector3(0.0, 0.0, 0.07), index)
		index += 1
	print("ART_SECURITY_WALL monitors=", index)

func _spawn_wall_monitor(pos: Vector3, index: int) -> void:
	var body := MeshInstance3D.new()
	body.name = "ART_SecWallMonitor_%d" % index
	var body_mesh := BoxMesh.new()
	body_mesh.size = Vector3(0.82, 0.58, 0.07)
	body.mesh = body_mesh
	body.position = pos
	var body_mat := StandardMaterial3D.new()
	body_mat.albedo_color = Color(0.018, 0.022, 0.026)
	body_mat.metallic = 0.55
	body_mat.roughness = 0.42
	body.material_override = body_mat
	add_child(body)
	var screen := MeshInstance3D.new()
	screen.name = body.name + "_SCREEN"
	var quad := QuadMesh.new()
	quad.size = Vector2(0.72, 0.48)
	screen.mesh = quad
	screen.position = pos + Vector3(0.0, 0.0, 0.041)
	var screen_mat := StandardMaterial3D.new()
	var tex: Texture2D = _screens.get("cyan") if index % 2 == 0 else _screens.get("green")
	screen_mat.albedo_texture = tex
	screen_mat.albedo_color = Color.WHITE
	screen_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	screen_mat.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
	screen.material_override = screen_mat
	screen.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(screen)

func _load_kit() -> void:
	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	var err: Error = doc.append_from_file(KIT_GLB, state)
	if err != OK:
		push_warning("ART3A1 kit no cargó: %s" % err)
		return
	var root := doc.generate_scene(state)
	if root == null:
		return
	root.name = "ART3A1_Kit"
	add_child(root)
	for node in root.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi.mesh == null:
			continue
		for i in range(mi.mesh.get_surface_count()):
			var m := mi.mesh.surface_get_material(i)
			if m == null:
				continue
			var n := m.resource_name.to_lower()
			if "glass" in n or "cyanstrip" in n or "amberstrip" in n:
				mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
				break
	for parapet in level.glb_root.find_children("*OFFICE_PARAPET*", "", true, false):
		parapet.visible = false
	# El kit incluye una segunda luna de mostrador que se solapa con la del
	# Nivel 1. Se conserva la del nivel y se unifica su material con ART_glass.
	var kit_glass := root.find_child("ART3A1_MERGED_Glass", true, false) as MeshInstance3D
	if kit_glass != null:
		kit_glass.visible = false
	var counter_glass := level.find_child("Level1CounterGlass", true, false) as MeshInstance3D
	if counter_glass != null and _materials.get("glass") != null:
		counter_glass.material_override = _materials["glass"]
	print("ART3A1_KIT loaded")

func _dim_rooms_outside_reception() -> void:
	# Red de seguridad: si una versión anterior dejó luces de relleno, se
	# eliminan. Las emergencias ya vienen atenuadas desde level1.gd.
	for node in level.find_children("ART_Corridor*", "Light3D", true, false):
		node.queue_free()
	for node in level.find_children("ART_RoomFill_*", "Light3D", true, false):
		node.queue_free()

func _load_dressing() -> void:
	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	var err: Error = doc.append_from_file(DRESSING_GLB, state)
	if err != OK:
		push_warning("ART3A2 dressing no cargó: %s" % err)
		return
	var root := doc.generate_scene(state)
	if root == null:
		return
	root.name = "ART3A2_Dressing"
	add_child(root)
	for node in root.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi.mesh == null:
			continue
		# Las sombras de todo el dressing duplicaban la carga de geometría.
		# Se activan solo en muebles y piezas grandes, que son las que
		# necesitan apoyo visual; los props pequeños siguen sin sombra.
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		var world_size: Vector3 = mi.get_aabb().size * mi.global_transform.basis.get_scale()
		var lower_name: String = mi.name.to_lower()
		var is_flat := "screen" in lower_name or "lamp" in lower_name or "light" in lower_name or "glass" in lower_name or "decal" in lower_name
		if not is_flat and world_size.y > 0.70 and world_size.x * world_size.z > 0.35:
			mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	print("ART3A2_DRESSING loaded")
	# Las tiras emisivas de techo de las salas se sustituyen por luminarias con carcasa.
	for node in level.glb_root.find_children("*", "MeshInstance3D", true, false):
		var un: String = node.name.to_upper()
		if "_STRIP" in un and not "CORR_STRIP" in un:
			node.visible = false
		elif "FOLIAGE" in un:
			node.visible = false
		elif ("LINTEL" in un or "_ABOVE_" in un or "STORE_HOIST_CTRL" in un) and node is MeshInstance3D:
			var dark_trim := StandardMaterial3D.new()
			dark_trim.albedo_color = Color(0.075, 0.085, 0.095)
			dark_trim.metallic = 0.55
			dark_trim.roughness = 0.58
			for di in range((node as MeshInstance3D).mesh.get_surface_count()):
				(node as MeshInstance3D).set_surface_override_material(di, dark_trim)
		elif "MAINT_GEN" in un and not "ALTA" in un and node is MeshInstance3D:
			var gen_mat := StandardMaterial3D.new()
			gen_mat.albedo_color = Color(0.055, 0.070, 0.065)
			gen_mat.metallic = 0.55
			gen_mat.roughness = 0.62
			for gi in range((node as MeshInstance3D).mesh.get_surface_count()):
				(node as MeshInstance3D).set_surface_override_material(gi, gen_mat)
		elif "GAP_1_7_2" in un and node is MeshInstance3D:
			var gap_mat := StandardMaterial3D.new()
			gap_mat.albedo_color = Color(0.10, 0.12, 0.13)
			gap_mat.metallic = 0.55
			gap_mat.roughness = 0.60
			for gi in range((node as MeshInstance3D).mesh.get_surface_count()):
				(node as MeshInstance3D).set_surface_override_material(gi, gap_mat)


# ---------------------------------------------------------------- props de sala

var _prop_cache := {}

func _prop_scene(key: String) -> Node3D:
	if _prop_cache.has(key):
		return _prop_cache[key]
	var path := "res://assets/models/fm/props/%s.glb" % key
	if not FileAccess.file_exists(path):
		return null
	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	if doc.append_from_file(path, state) != OK:
		push_warning("Prop no cargó: %s" % key)
		return null
	var root := doc.generate_scene(state)
	if root == null:
		return null
	_prop_cache[key] = root
	return root

func _spawn_prop(key: String, pos: Vector3, yaw_deg: float, scale: float = 1.0, shadow: bool = true, collide: bool = false) -> void:
	var base := _prop_scene(key)
	if base == null:
		return
	var inst := base.duplicate() as Node3D
	inst.name = "PROP_%s_%d" % [key, get_child_count()]
	inst.position = pos
	inst.rotation_degrees = Vector3(0, yaw_deg, 0)
	inst.scale = Vector3(scale, scale, scale)
	add_child(inst)
	var combined := AABB()
	var has_box := false
	for mi in inst.find_children("*", "MeshInstance3D", true, false):
		var mesh_inst := mi as MeshInstance3D
		mesh_inst.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON if shadow else GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		if collide and mesh_inst.mesh != null:
			var b: AABB = mesh_inst.transform * mesh_inst.get_aabb()
			if has_box:
				combined = combined.merge(b)
			else:
				combined = b
				has_box = true
	if collide and has_box:
		var body := StaticBody3D.new()
		body.name = "PropCollider"
		var shape := BoxShape3D.new()
		shape.size = combined.size
		var cs := CollisionShape3D.new()
		cs.shape = shape
		cs.position = combined.get_center()
		body.add_child(cs)
		inst.add_child(body)

func _upgrade_storage_crates() -> void:
	# Los bloques de escombros y cajas compartían un material plano. Se
	# asignan variantes de madera/cartón por instancia para romper la repetición.
	var variants: Array[Material] = [_materials["crate_card"], _materials["crate_pale"], _materials["crate_dark"]]
	var index := 0
	for node in glb_root.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi == null:
			continue
		var n := mi.name.to_upper()
		if n.contains("_TAPE") or n.contains("_BAND"):
			continue
		if not (n.contains("CRATE") or n.contains("CARDBOARD_BOX") or n.contains("PALLET_CRATE") or n.contains("WOODEN_CRATE_02")):
			continue
		mi.material_override = variants[index % variants.size()]
		index += 1
	print("ART_CRATES varied=", index)

func _fix_prop_materials() -> void:
	# Los GLB de sillas, mesas, relojes y señales conservan metallic=1 y
	# roughness=1 del exportador: parecen yeso metálico. Se ajustan una sola
	# vez por material, sin tocar sus texturas.
	var specs := [
		["SchoolChair_01", 0.18, 0.62],
		["metal_office_desk", 0.42, 0.48],
		["WetFloorSign_01", 0.05, 0.58],
		["wall_clock", 0.15, 0.55],
	]
	var fixed := {}
	for node in level.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi == null or mi.mesh == null:
			continue
		for surface in range(mi.mesh.get_surface_count()):
			var mat := mi.get_active_material(surface) as StandardMaterial3D
			if mat == null:
				continue
			var id := mat.get_instance_id()
			if fixed.has(id):
				continue
			var key := String(mat.resource_name)
			for spec in specs:
				if key.findn(spec[0]) >= 0:
					mat.metallic = spec[1]
					mat.roughness = spec[2]
					fixed[id] = true
					break
	print("ART_PROPS fixed=", fixed.size())

func _fix_office_access() -> void:
	# Un monitor de suelo quedó centrado en el hueco oeste de oficina y su
	# collider AABB bloqueaba por completo el paso. Es utilería decorativa:
	# se retira junto con su colisión para recuperar el acceso.
	for node_name in [
		"NEXUS_L1_DIS_OFFICE_MONITOR_FLOOR",
		"NEXUS_L1_DIS_OFFICE_MONITOR_SCREEN",
	]:
		var prop := level.find_child(node_name, true, false) as Node3D
		if prop != null:
			prop.visible = false
	var collider := level.find_child("COL_108_NEXUS_L1_DIS_OFFICE_MONITOR_FLOOR", true, false)
	if collider != null:
		collider.queue_free()
		print("ART_OFFICE_ACCESS removed floor monitor collider")

func _replace_maintenance_generator() -> void:
	# La caja negra original era una primitiva con un ventilador plano.
	# Se sustituye por un generador industrial con geometría y PBR propios.
	for node in glb_root.find_children("*", "MeshInstance3D", true, false):
		var n := node.name.to_upper()
		if n.contains("NEXUS_V05_MAINT_GEN") or n.contains("NEXUS_V05_B_MAINT_GEN_") or n.contains("MAINT_ALTA_") or n.contains("MAINT_PANEL_BOX_"):
			node.visible = false
	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	if doc.append_from_file(GENERATOR_GLB, state) != OK:
		push_warning("No se pudo cargar el generador industrial")
		return
	var root := doc.generate_scene(state)
	if root == null:
		return
	root.name = "ART_Maintenance_Generator"
	add_child(root)
	root.scale = Vector3.ONE * 1.45
	root.rotation_degrees.y = 180.0
	root.force_update_transform()
	var box := _world_aabb(root)
	root.global_position = Vector3(13.0, -5.65 - box.position.y, 7.9)
	# Bancada metálica bajo el equipo, oscura para no competir con el amarillo.
	var pad := MeshInstance3D.new()
	pad.name = "ART_Generator_Pad"
	var pad_mesh := BoxMesh.new()
	pad_mesh.size = Vector3(3.0, 0.12, 1.75)
	pad.mesh = pad_mesh
	pad.material_override = _materials["wall_dark"]
	pad.position = Vector3(13.0, -5.60, 7.9)
	add_child(pad)
	print("ART_GENERATOR replaced")

func _world_aabb(node: Node3D) -> AABB:
	var result := AABB()
	var first := true
	for child in node.find_children("*", "MeshInstance3D", true, false):
		var mi := child as MeshInstance3D
		if mi == null or mi.mesh == null or not mi.visible:
			continue
		var box: AABB = mi.global_transform * mi.get_aabb()
		if first:
			result = box
			first = false
		else:
			result = result.merge(box)
	return result

func _detail_boiler() -> void:
	# La caldera recibe un acabado metálico apagado sólo en su cuerpo; no se
	# impone triplanar a todos los objetos de metal oxidado de la escena.
	var body := glb_root.find_child("NEXUS_V05_B_MAINT_BOILER_BODY", true, false) as MeshInstance3D
	if body != null and _materials.get("boiler_skin") != null:
		body.material_override = _materials["boiler_skin"]
	# Remaches y volante de válvula para que la caldera no sea un cilindro liso.
	var parts: Array = []
	for band_y in [-5.0, -4.32, -3.62]:
		for i in range(14):
			var a := TAU * float(i) / 14.0
			var p := Vector3(17.3 + cos(a) * 0.885, band_y, 8.2 + sin(a) * 0.885)
			_bolt(parts, p, Basis(Vector3(0.0, 1.0, 0.0), a))
	if not parts.is_empty():
		_merge("ART_Boiler_Rivets", parts, _materials["detail_steel"], self)
	var wheel := MeshInstance3D.new()
	wheel.name = "ART_Boiler_Handwheel"
	var torus := TorusMesh.new()
	torus.inner_radius = 0.17
	torus.outer_radius = 0.23
	torus.rings = 20
	torus.ring_segments = 8
	wheel.mesh = torus
	wheel.position = Vector3(17.0, -1.92, 8.2)
	wheel.material_override = _materials["detail_steel"]
	add_child(wheel)
	var spokes: Array = []
	for i in range(4):
		var a := TAU * float(i) / 4.0
		_box(spokes, Vector3(17.0 + cos(a) * 0.10, -1.92, 8.2 + sin(a) * 0.10), Vector3(0.17, 0.025, 0.025), Basis(Vector3.UP, -a))
	_merge("ART_Boiler_Spokes", spokes, _materials["detail_steel"], self)
	var plate := MeshInstance3D.new()
	plate.name = "ART_Boiler_LabelPlate"
	var pm := BoxMesh.new()
	pm.size = Vector3(0.74, 0.26, 0.018)
	plate.mesh = pm
	plate.position = Vector3(17.3, -3.55, 7.32)
	var pm_mat := StandardMaterial3D.new()
	pm_mat.albedo_color = Color(0.035, 0.040, 0.038)
	pm_mat.metallic = 0.35
	pm_mat.roughness = 0.52
	plate.material_override = pm_mat
	add_child(plate)
	var label := Label3D.new()
	label.name = "ART_Boiler_Label"
	label.text = "CALDERA 02\nPRESIÓN CRÍTICA"
	label.font_size = 34
	label.pixel_size = 0.0026
	label.modulate = Color(1.0, 0.66, 0.26)
	label.outline_size = 4
	label.outline_modulate = Color(0.0, 0.0, 0.0)
	label.no_depth_test = true
	label.render_priority = 2
	label.rotation_degrees.y = 180.0
	label.position = Vector3(17.3, -3.55, 7.40)
	add_child(label)
	print("ART_BOILER detailed")

func _upgrade_loaded_screens() -> void:
	var seen := {}
	for node in find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi == null or mi.mesh == null:
			continue
		for i in range(mi.mesh.get_surface_count()):
			var mat := mi.mesh.surface_get_material(i)
			if mat == null:
				continue
			var id := mat.get_instance_id()
			if seen.has(id):
				continue
			seen[id] = true
			var key := _material_key(mat)
			if key.begins_with("ART3A2_Screen") and mat is StandardMaterial3D:
				_set_screen_texture(mat as StandardMaterial3D, "amber", 0.60)
	# Algunos monitores del kit traen una pantalla hija sin material: se veía
	# el fondo gris del modelo. Se le asigna la interfaz táctica del nivel.
	for node in find_children("*_SCREEN", "MeshInstance3D", true, false):
		var screen_mi := node as MeshInstance3D
		if screen_mi == null or screen_mi.mesh == null:
			continue
		if screen_mi.material_override != null:
			continue
		if screen_mi.get_active_material(0) != null:
			continue
		var screen_mat := StandardMaterial3D.new()
		screen_mat.resource_name = "ART_ScreenOverlay"
		_set_screen_texture(screen_mat, "cyan", 0.30)
		screen_mi.material_override = screen_mat

func _replace_control_screen() -> void:
	# El kit de dressing trae un único prop con la textura aplicada a todas las
	# caras de una caja: desde la sala se veían dos paneles grises con barras,
	# no una pantalla. Se sustituye por un banco de dos monitores orientados
	# hacia el interior de control.
	var old := level.find_child("DRESS_Screen", true, false) as MeshInstance3D
	if old != null:
		old.visible = false
	var body_mat := StandardMaterial3D.new()
	body_mat.albedo_color = Color(0.020, 0.025, 0.030, 1.0)
	body_mat.metallic = 0.55
	body_mat.roughness = 0.38
	var specs := [
		[-6.98, "amber"],
		[-5.96, "cyan"],
	]
	for i in range(specs.size()):
		var z: float = specs[i][0]
		var tex: Texture2D = _screens.get(specs[i][1])
		var body := MeshInstance3D.new()
		body.name = "ART_ControlScreen_%s" % ("A" if i == 0 else "B")
		var body_mesh := BoxMesh.new()
		body_mesh.size = Vector3(0.09, 0.64, 1.04)
		body.mesh = body_mesh
		body.position = Vector3(9.62, -4.20, z)
		body.material_override = body_mat
		body.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		add_child(body)
		var screen := MeshInstance3D.new()
		screen.name = body.name + "_SCREEN"
		var screen_mesh := QuadMesh.new()
		screen_mesh.size = Vector2(0.98, 0.56)
		screen.mesh = screen_mesh
		# QuadMesh mira a +Z; se gira 90° para mirar a +X, hacia la sala.
		screen.position = Vector3(9.668, -4.20, z)
		screen.rotation.y = PI * 0.5
		var screen_mat := StandardMaterial3D.new()
		screen_mat.albedo_texture = tex
		screen_mat.albedo_color = Color.WHITE
		screen_mat.emission_enabled = tex != null
		screen_mat.emission_texture = tex
		screen_mat.emission = Color.WHITE
		screen_mat.emission_energy_multiplier = 0.55
		screen_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		screen_mat.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
		screen.material_override = screen_mat
		screen.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		add_child(screen)

func _spawn_room_props() -> void:
	var mode := OS.get_environment("FM_PROP_MODE")
	if mode == "none":
		print("ART3A2_PROPS skipped mode=none")
		return
	var props := [
		# Recepción
		["potted_plant", Vector3(-18.1, -5.65, -3.05), 0.0, 1.0],
		["potted_plant", Vector3(-8.1, -5.65, -10.6), 20.0, 0.9],
		["drawer", Vector3(-19.25, -5.65, -10.1), 90.0, 1.0, true],
		["fire_alarm", Vector3(-19.72, -3.45, -6.0), 90.0, 1.0],
		# Oficina
		["shelves", Vector3(-7.65, -5.65, -5.15), 90.0, 1.0, true],
		["microscope", Vector3(-6.1, -4.60, -7.2), 0.0, 1.0],
		# Aseo
		["medical_box", Vector3(-6.35, -4.84, -4.42), 0.0, 1.0],
		# Seguridad
		["utility_box", Vector3(7.58, -5.65, -8.2), -90.0, 1.0, true],
		["radio", Vector3(2.0, -4.50, -6.32), 180.0, 1.0],
		["stool", Vector3(4.8, -5.65, -4.2), 0.0, 1.0],
		["camera", Vector3(7.55, -2.9, -9.2), -135.0, 1.0],
		# Control
		["utility_box", Vector3(14.58, -5.65, -8.4), -90.0, 1.0, true],
		["radio", Vector3(12.0, -4.50, -6.32), 180.0, 1.0],
		["camera", Vector3(14.55, -2.9, -9.2), -135.0, 1.0],
		["stool", Vector3(10.0, -5.65, -5.0), 0.0, 1.0],
		# Vestuarios
		["stool", Vector3(-16.8, -5.65, 4.0), 0.0, 1.0],
		["crate", Vector3(-17.6, -5.65, 7.9), 22.0, 1.0, true],
		["fire_alarm", Vector3(-9.28, -3.45, 6.0), -90.0, 1.0],
		["medical_box", Vector3(-17.2, -5.30, 5.8), 0.0, 1.0],
		# Almacén
		["crate", Vector3(-6.8, -5.65, 8.5), 12.0, 1.0, true],
		["crate", Vector3(-6.2, -5.65, 8.3), -18.0, 1.0, true],
		["barrel", Vector3(1.4, -5.65, 8.8), 0.0, 1.0, true],
		["barrel", Vector3(0.8, -5.65, 8.6), 0.0, 1.0, true],
		["fire_alarm", Vector3(-7.72, -3.50, 5.0), 90.0, 1.0],
		# Mantenimiento
		["power_box", Vector3(18.0, -5.40, 8.8), -90.0, 1.0, true],
		["drawer", Vector3(7.1, -5.65, 9.0), 180.0, 1.0, true],
		["barrel", Vector3(17.9, -5.65, 3.2), 0.0, 1.0, true],
		["barrel", Vector3(17.2, -5.65, 3.9), 0.0, 1.0, true],
		["stool", Vector3(9.5, -5.65, 6.0), 0.0, 1.0],
		["medical_box", Vector3(6.35, -3.80, 8.4), 90.0, 1.0],
		# Corredor
		["fire_alarm", Vector3(-10.0, -3.50, -1.62), 0.0, 1.0],
		["fire_alarm", Vector3(9.0, -3.50, 1.62), 180.0, 1.0],
		["camera", Vector3(-16.0, -2.75, -1.55), 60.0, 1.0],
		["utility_box", Vector3(20.4, -5.65, -1.0), 180.0, 1.0, true],
	]
	var spawned := 0
	for spec in props:
		var key: String = spec[0]
		if mode == "plants" and key != "potted_plant":
			continue
		if mode == "furniture" and key in ["potted_plant", "radio", "microscope", "medical_box", "stool", "fire_alarm", "camera", "barrel", "crate"]:
			continue
		if mode == "small" and key in ["potted_plant", "drawer", "shelves", "utility_box", "power_box"]:
			continue
		var do_collide: bool = spec.size() > 4 and bool(spec[4])
		_spawn_prop(key, spec[1], spec[2], spec[3], true, do_collide)
		spawned += 1
	print("ART3A2_PROPS ", spawned)
	_add_static_box("ART_Col_ControlDesk", Vector3(9.45, -5.15, -6.0), Vector3(0.95, 1.0, 2.50))
	_add_static_box("ART_Col_RackSecurity", Vector3(7.55, -4.70, -8.95), Vector3(0.62, 1.80, 0.86))
	_add_static_box("ART_Col_RackControl", Vector3(14.45, -4.70, -8.95), Vector3(0.62, 1.80, 0.86))

func _add_static_box(body_name: String, center: Vector3, size: Vector3) -> void:
	var body := StaticBody3D.new()
	body.name = body_name
	body.position = center
	var shape := BoxShape3D.new()
	shape.size = size
	var cs := CollisionShape3D.new()
	cs.shape = shape
	body.add_child(cs)
	add_child(body)

func _build_reception_details() -> void:
	var root := Node3D.new()
	root.name = "ART_ReceptionDetails"
	add_child(root)
	var steel: Array = []
	var painted: Array = []
	var dark: Array = []
	var glow: Array = []
	var wood: Array = []
	var hazard: Array = []

	# El mostrador y su cristal se sustituyen por el kit de Blender ART3A1.

	# Costuras y remates de la pared posterior.
	for x in range(-19, -4, 2):
		if absi(x + 12) < 2:
			continue
		_box(steel, Vector3(float(x), -3.45, -11.58), Vector3(0.035, 2.40, 0.035))
	_box(steel, Vector3(-12.0, -2.30, -11.58), Vector3(15.8, 0.04, 0.04))
	_box(steel, Vector3(-12.0, -4.55, -11.58), Vector3(15.8, 0.04, 0.04))

	# Paneles de pared posterior, dejando libre el logo central.
	for x in [-18.0, -6.0]:
		_box(painted, Vector3(x, -3.30, -11.62), Vector3(3.20, 1.90, 0.05))
		_box(steel, Vector3(x, -4.28, -11.57), Vector3(3.30, 0.05, 0.06))
		_box(steel, Vector3(x, -2.32, -11.57), Vector3(3.30, 0.05, 0.06))
		_box(steel, Vector3(x - 1.62, -3.30, -11.57), Vector3(0.05, 2.00, 0.06))
		_box(steel, Vector3(x + 1.62, -3.30, -11.57), Vector3(0.05, 2.00, 0.06))

	# Bandeja de cables en techo.
	_box(steel, Vector3(-12.0, -1.98, -9.60), Vector3(13.0, 0.04, 0.32))
	_box(steel, Vector3(-12.0, -1.94, -9.45), Vector3(13.0, 0.10, 0.03))
	_box(steel, Vector3(-12.0, -1.94, -9.75), Vector3(13.0, 0.10, 0.03))
	for i in range(26):
		_box(steel, Vector3(-18.5 + float(i) * 0.5, -1.96, -9.60), Vector3(0.03, 0.03, 0.30))
	for i in range(7):
		_box(steel, Vector3(-18.5 + float(i) * 2.0, -1.87, -9.60), Vector3(0.04, 0.18, 0.04))

	# Conducto rectangular en techo.
	_box(painted, Vector3(-12.0, -2.15, -4.10), Vector3(13.0, 0.34, 0.55))
	for i in range(14):
		_box(steel, Vector3(-18.5 + float(i) * 1.0, -2.15, -4.10), Vector3(0.05, 0.36, 0.57))

	# Downlights y canalización de pared.
	for x in [-16.0, -12.0, -8.0]:
		_cyl(steel, Vector3(x, -1.80, -5.6), 0.16, 0.05, Basis(), 16)
		_cyl(glow, Vector3(x, -1.84, -5.6), 0.12, 0.012, Basis(), 16)
	_cyl(steel, Vector3(-4.32, -4.0, -10.50), 0.045, 2.20, Basis(), 12)
	_box(steel, Vector3(-4.32, -3.0, -10.55), Vector3(0.28, 0.38, 0.12))

	# Banda de listones de madera bajo el logo corporativo.
	for i in range(15):
		_box(wood, Vector3(-14.2 + float(i) * 0.30, -4.02, -11.50), Vector3(0.060, 0.70, 0.040))
	_box(steel, Vector3(-12.0, -4.40, -11.49), Vector3(4.8, 0.04, 0.04))
	_box(steel, Vector3(-12.0, -3.64, -11.49), Vector3(4.8, 0.04, 0.04))

	# Luminaria lineal sobre el mostrador.
	_box(steel, Vector3(-12.0, -1.90, -8.40), Vector3(9.5, 0.08, 0.28))
	_box(glow, Vector3(-12.0, -1.95, -8.40), Vector3(9.2, 0.02, 0.18))

	# Luz bajo mostrador y línea de peligro en el acceso.
	_box(hazard, Vector3(-12.0, -5.638, -2.20), Vector3(4.0, 0.006, 0.08))

	_merge("ART_Reception_Steel", steel, _materials["detail_steel"], root)
	_merge("ART_Reception_Painted", painted, _materials["detail_painted"], root)
	_merge("ART_Reception_Dark", dark, _materials["detail_dark"], root)
	_merge("ART_Reception_Glow", glow, _materials["emissive_cool"], root, false)
	_merge("ART_Reception_Wood", wood, _materials["wood"], root)
	_merge("ART_Reception_Hazard", hazard, _materials["hazard"], root, false)

func _build_corridor_details() -> void:
	var root := Node3D.new()
	root.name = "ART_CorridorDetails"
	add_child(root)
	var steel: Array = []
	var painted: Array = []
	var dark: Array = []
	var glow: Array = []
	var strip: Array = []
	var hazard: Array = []

	# Bandeja portacables continua.
	_box(steel, Vector3(0.0, -1.95, -1.30), Vector3(42.0, 0.04, 0.28))
	_box(steel, Vector3(0.0, -1.91, -1.45), Vector3(42.0, 0.08, 0.03))
	_box(steel, Vector3(0.0, -1.91, -1.15), Vector3(42.0, 0.08, 0.03))
	for i in range(84):
		_box(steel, Vector3(-21.0 + float(i) * 0.5, -1.93, -1.30), Vector3(0.03, 0.03, 0.28))
	for i in range(15):
		_box(steel, Vector3(-21.0 + float(i) * 3.0, -1.85, -1.30), Vector3(0.04, 0.22, 0.04))

	# Tubería principal con bridas y abrazaderas.
	var along_x := Basis(Vector3(0, 0, 1), PI * 0.5)
	_cyl(steel, Vector3(0.0, -2.30, 1.40), 0.10, 42.0, along_x, 20)
	for i in range(11):
		_cyl(steel, Vector3(-20.0 + float(i) * 4.0, -2.30, 1.40), 0.14, 0.06, along_x, 20)
	for i in range(21):
		_box(steel, Vector3(-20.0 + float(i) * 2.0, -2.44, 1.40), Vector3(0.06, 0.28, 0.16))

	# Tubería secundaria.
	_cyl(steel, Vector3(0.0, -2.60, 1.52), 0.06, 42.0, along_x, 16)
	for i in range(8):
		_cyl(steel, Vector3(-18.0 + float(i) * 6.0, -2.60, 1.52), 0.09, 0.05, along_x, 16)
	for i in range(15):
		_box(steel, Vector3(-21.0 + float(i) * 3.0, -2.70, 1.52), Vector3(0.05, 0.22, 0.12))

	# El conducto del corredor se sustituye por el kit de Blender ART3A1.

	# Canalización fina sobre la pared.
	_cyl(steel, Vector3(0.0, -2.05, 1.55), 0.035, 42.0, along_x, 12)
	for i in range(15):
		_box(steel, Vector3(-21.0 + float(i) * 3.0, -2.12, 1.55), Vector3(0.05, 0.10, 0.08))

	# Columnas estructurales y vigas que rompen la repetición del corredor.
	for x in [-20.0, -16.0, -8.0, 0.0, 8.0, 16.0, 20.0]:
		for z in [-1.53, 1.53]:
			_box(dark, Vector3(x, -3.95, z), Vector3(0.20, 3.40, 0.24))
			_box(steel, Vector3(x, -5.60, z), Vector3(0.28, 0.10, 0.32))
			_box(steel, Vector3(x, -2.29, z), Vector3(0.28, 0.07, 0.32))
			_box(hazard, Vector3(x, -5.42, z), Vector3(0.22, 0.08, 0.26))
			for by in [-0.10, 0.10]:
				_bolt(steel, Vector3(x, -5.54, z + by), Basis(Vector3(1, 0, 0), PI * 0.5))
			_add_column_collider(x, z)
	for x in [-18.0, -10.0, -2.0, 6.0, 14.0]:
		_box(dark, Vector3(x, -1.84, 0.0), Vector3(0.20, 0.18, 3.36))
		_box(steel, Vector3(x, -1.75, 0.0), Vector3(0.24, 0.04, 3.40))

	# Marcos metálicos y herrajes de las puertas del corredor.
	var door_frames := [
		[-14.0, 1.66], [-12.0, -1.66], [-2.0, 1.66],
		[3.0, -1.66], [13.0, -1.66], [13.0, 1.66],
	]
	for frame in door_frames:
		var fx: float = frame[0]
		var fz: float = frame[1]
		_box(steel, Vector3(fx - 0.84, -4.10, fz), Vector3(0.06, 3.02, 0.06))
		_box(steel, Vector3(fx + 0.84, -4.10, fz), Vector3(0.06, 3.02, 0.06))
		_box(steel, Vector3(fx, -2.62, fz), Vector3(1.74, 0.06, 0.06))
		_box(steel, Vector3(fx, -5.58, fz), Vector3(1.74, 0.06, 0.06))

	# Tubería secundaria de pared izquierda y abrazaderas.
	_cyl(steel, Vector3(0.0, -2.56, -1.45), 0.05, 42.0, along_x, 14)
	for i in range(14):
		_box(steel, Vector3(-20.0 + float(i) * 3.0, -2.66, -1.45), Vector3(0.05, 0.18, 0.10))

	# Tira de luz fría continua en el borde superior de ambas paredes.
	_box(strip, Vector3(0.0, -2.20, -1.63), Vector3(41.0, 0.018, 0.018))
	_box(strip, Vector3(0.0, -2.20, 1.63), Vector3(41.0, 0.018, 0.018))

	# Cabeceras de panel que cubren el paramento alto sobre los módulos.
	for x in [-8.7, 8.7]:
		for z in [-1.52, 1.52]:
			_box(dark, Vector3(x, -2.12, z), Vector3(3.50, 0.86, 0.06))
			_box(steel, Vector3(x, -2.56, z - 0.02), Vector3(3.58, 0.05, 0.08))
			_box(steel, Vector3(x, -1.71, z - 0.02), Vector3(3.58, 0.05, 0.08))
			_box(steel, Vector3(x - 1.75, -2.12, z - 0.02), Vector3(0.05, 0.86, 0.08))
			_box(steel, Vector3(x + 1.75, -2.12, z - 0.02), Vector3(0.05, 0.86, 0.08))
			_box(hazard, Vector3(x, -1.80, z - 0.06), Vector3(0.55, 0.10, 0.02))

	# Sofito técnico sobre el acceso, cubre el paramento claro existente.
	_box(dark, Vector3(-7.6, -2.72, -1.52), Vector3(4.20, 0.30, 0.30))
	_box(steel, Vector3(-7.6, -2.89, -1.52), Vector3(4.28, 0.05, 0.34))
	_box(steel, Vector3(-7.6, -2.56, -1.52), Vector3(4.28, 0.05, 0.34))
	_box(hazard, Vector3(-7.6, -2.89, -1.36), Vector3(0.70, 0.10, 0.02))
	for x in [-9.4, -7.6, -5.8]:
		_box(steel, Vector3(x, -2.56, -1.52), Vector3(0.05, 0.06, 0.36))
		_bolt(steel, Vector3(x, -2.89, -1.38), Basis(Vector3(1, 0, 0), PI * 0.5))

	# Dintel metálico sobre el acceso, sustituye el parapeto claro visible.
	_box(dark, Vector3(-6.25, -2.64, -1.89), Vector3(3.95, 0.28, 0.24))
	_box(steel, Vector3(-6.25, -2.50, -1.89), Vector3(4.03, 0.045, 0.28))
	_box(steel, Vector3(-6.25, -2.78, -1.89), Vector3(4.03, 0.045, 0.28))
	_box(hazard, Vector3(-6.25, -2.64, -1.75), Vector3(0.70, 0.10, 0.02))

	# Bulkhead oscuro sobre el acceso, simétrico en ambas paredes.
	for bz in [-1.52, 1.52]:
		_box(dark, Vector3(-7.6, -2.28, bz), Vector3(5.60, 0.92, 0.12))
		_box(steel, Vector3(-7.6, -2.76, bz), Vector3(5.68, 0.05, 0.16))
		_box(steel, Vector3(-7.6, -1.80, bz), Vector3(5.68, 0.05, 0.16))
		_box(steel, Vector3(-10.35, -2.28, bz), Vector3(0.06, 0.92, 0.16))
		_box(steel, Vector3(-4.85, -2.28, bz), Vector3(0.06, 0.92, 0.16))
		_box(hazard, Vector3(-7.6, -2.72, bz + 0.08), Vector3(0.72, 0.10, 0.02))

	# Revestimiento de servicio que cubre el paramento alto izquierdo/derecho.
	for cz in [-1.40, 1.40]:
		_box(dark, Vector3(-7.7, -2.60, cz), Vector3(5.60, 1.60, 0.08))
		_box(steel, Vector3(-7.7, -3.38, cz), Vector3(5.68, 0.05, 0.12))
		_box(steel, Vector3(-7.7, -1.82, cz), Vector3(5.68, 0.05, 0.12))
		_box(steel, Vector3(-10.48, -2.60, cz), Vector3(0.05, 1.60, 0.12))
		_box(steel, Vector3(-4.92, -2.60, cz), Vector3(0.05, 1.60, 0.12))
		for rx in [-9.8, -8.7, -7.6, -6.5, -5.4]:
			_box(steel, Vector3(rx, -2.60, cz + 0.05), Vector3(0.030, 1.52, 0.030))
		_box(hazard, Vector3(-5.55, -2.30, cz + 0.07), Vector3(0.40, 0.10, 0.02))

	# Luminarias industriales y tubos emisivos.
	for x in [-15.0, -5.0, 5.0, 15.0]:
		_box(steel, Vector3(x, -1.86, 0.0), Vector3(1.40, 0.07, 0.24))
		_cyl(glow, Vector3(x - 0.35, -1.92, -0.05), 0.025, 1.20, along_x, 12)
		_cyl(glow, Vector3(x + 0.35, -1.92, 0.05), 0.025, 1.20, along_x, 12)

	# Marcas de peligro junto a los accesos.
	for x in [-14.0, -12.0, -2.0, 3.0, 13.0]:
		_box(hazard, Vector3(x, -5.638, 1.55), Vector3(1.0, 0.006, 0.06))

	_merge("ART_Corridor_Steel", steel, _materials["detail_steel"], root)
	_merge("ART_Corridor_Painted", painted, _materials["detail_painted"], root)
	_merge("ART_Corridor_Dark", dark, _materials["detail_dark"], root)
	_merge("ART_Corridor_Glow", glow, _materials["emissive_cool"], root, false)
	_merge("ART_Corridor_Strip", strip, _materials["emissive_strip"], root, false)
	_merge("ART_Corridor_Hazard", hazard, _materials["hazard"], root, false)

func _compress_scene_albedos() -> void:
	# La escena superaba los 3,7 GB de VRAM con texturas 2K sin comprimir.
	# Se comprimen los albedos opacos a S3TC (4:1) conservando mipmaps.
	var cache := {}
	var count := 0
	for node in level.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi == null:
			continue
		var materials: Array[Material] = []
		if mi.material_override != null:
			materials.append(mi.material_override)
		if mi.mesh != null:
			for i in range(mi.mesh.get_surface_count()):
				var m := mi.mesh.surface_get_material(i)
				if m != null:
					materials.append(m)
		for m in materials:
			if not (m is StandardMaterial3D):
				continue
			var sm := m as StandardMaterial3D
			var tex := sm.albedo_texture
			if tex == null:
				continue
			var id := tex.get_instance_id()
			if cache.has(id):
				if cache[id] != null:
					sm.albedo_texture = cache[id]
				continue
			cache[id] = null
			var img := tex.get_image()
			if img == null or img.get_width() < 64 or img.get_height() < 64:
				continue
			if img.is_compressed():
				continue
			if not img.has_mipmaps():
				img.generate_mipmaps()
			# Los albedos grandes y opacos se comprimen; el resto sólo recibe
			# mipmaps para eliminar aliasing en superficies inclinadas.
			if img.get_width() >= 512 and not img.detect_alpha():
				if img.compress(Image.COMPRESS_S3TC) != OK:
					continue
			var new_tex := ImageTexture.create_from_image(img)
			cache[id] = new_tex
			sm.albedo_texture = new_tex
			count += 1
	print("ART_TEXTURES compressed=", count)

func _compress_scene_secondary_textures() -> void:
	# Las normales y roughness 2K sin comprimir eran el grueso de la VRAM.
	# Las normales se limitan a 1K (calidad visual suficiente a distancia) y
	# los mapas de datos se reducen a 512 y se comprimen a S3TC.
	var cache := {}
	var changed := 0
	for node in level.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi == null:
			continue
		var materials: Array[Material] = []
		if mi.material_override != null:
			materials.append(mi.material_override)
		if mi.mesh != null:
			for i in range(mi.mesh.get_surface_count()):
				var m := mi.mesh.surface_get_material(i)
				if m != null:
					materials.append(m)
		for m in materials:
			if not (m is StandardMaterial3D):
				continue
			var sm := m as StandardMaterial3D
			var specs := [
				["normal_texture", 1024, false],
				["roughness_texture", 512, true],
				["ao_texture", 512, true],
				["emission_texture", 1024, true],
			]
			for spec in specs:
				var tex: Texture2D = sm.get(spec[0])
				if tex == null:
					continue
				var target: int = spec[1]
				var compress: bool = spec[2]
				var key := "%d_%d_%s" % [tex.get_instance_id(), target, compress]
				if cache.has(key):
					if cache[key] != null:
						sm.set(spec[0], cache[key])
					continue
				cache[key] = null
				var img := tex.get_image()
				if img == null:
					continue
				var w := img.get_width()
				var h := img.get_height()
				if w < 64 or h < 64:
					continue
				if w > target or h > target:
					var scale := float(target) / float(maxi(w, h))
					img.resize(maxi(1, int(w * scale)), maxi(1, int(h * scale)), Image.INTERPOLATE_LANCZOS)
				if not img.has_mipmaps():
					img.generate_mipmaps()
				if compress and not img.is_compressed() and not img.detect_alpha():
					if img.compress(Image.COMPRESS_S3TC) != OK:
						continue
				var new_tex := ImageTexture.create_from_image(img)
				cache[key] = new_tex
				sm.set(spec[0], new_tex)
				changed += 1
	print("ART_TEXTURES secondary=", changed)

func _apply_distance_culling() -> void:
	var tokens := ["PAPER", "BLOOD", "DECAL", "GRIME", "DEBRIS", "SHARD", "CAN_", "BOTTLE", "CUP", "TRASHBAG", "NOTEPAD", "CLIP", "STAPLER", "PENCIL", "SCREWDRIVER", "WRENCH", "PLIERS", "GLOVE", "HAT_", "BOOT"]
	for node in glb_root.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi == null:
			continue
		var upper := mi.name.to_upper()
		for token in tokens:
			if token in upper:
				mi.visibility_range_end = 18.0
				mi.visibility_range_end_margin = 2.0
				mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
				break
