extends Node

## Prueba headless de los anclajes narrativos N1/N2/N3/N4/N5/N6/N7/N8.
## godot --headless --path . tests/fm_narrative_smoke.tscn
##
## Verifica estructura, sector, distancia a la ruta jugable, ausencia de
## colisiones y luces bajo Narrative, y el pase de materiales PBR (sets
## texturizados, UV triplanar, micro-normales y emisivos intactos). No prueba
## interacción: estos props son narrativos y no deben alterar el Paso 1.

const EXPECTED_IDS := ["N1", "N2", "N3", "N4", "N5", "N6", "N7", "N8"]
const RECEPTION_SECTOR := Rect2(-110.25, 3.81, 40.41, 36.34)
const Z10_SECTOR := Rect2(39.6, -30.6, 30.9, 24.0)
const RECEPTION_ROUTE := [
	Vector2(-90.0, 13.0),
	Vector2(-93.0, 16.5),
	Vector2(-93.0, 24.0),
	Vector2(-92.0, 32.0),
	Vector2(-94.0, 36.4),
]
const Z10_ROUTE := [
	Vector2(47.0, -22.0),
	Vector2(52.0, -21.4),
	Vector2(55.7, -21.4),
	Vector2(58.2, -21.4),
	Vector2(61.4, -21.0),
	Vector2(67.4, -21.0),
]
const SECTORS := {
	"N1": "RECEPTION",
	"N2": "RECEPTION",
	"N3": "RECEPTION",
	"N4": "RECEPTION",
	"N5": "RECEPTION",
	"N6": "RECEPTION",
	"N7": "RECEPTION",
	"N8": "Z10",
}

var scene
var narrative: Node3D
var passes := 0
var fails := 0


func _ready() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	var packed: PackedScene = load("res://scenes/fm/fm_vslice_z10.tscn")
	if packed == null:
		print("FM_NARRATIVE_TEST: FAIL (escena no encontrada)")
		get_tree().quit(1)
		return
	scene = packed.instantiate()
	add_child(scene)
	var guard := 0
	while not scene.level_ready and guard < 600:
		await get_tree().process_frame
		guard += 1
	if not scene.level_ready:
		_fail("la escena no terminó de cargar")
		_finish()
		return

	# El Vigilante no participa en una prueba de geometría narrativa.
	if scene.watcher != null and is_instance_valid(scene.watcher):
		scene.watcher.set_physics_process(false)
		scene.watcher.visible = false
	await get_tree().physics_frame

	narrative = scene.get_node_or_null("Narrative") as Node3D
	_check("narrative_node", narrative != null)
	_check(
		"narrative_is_root_sibling",
		narrative != null and narrative.get_parent() == scene
		and scene.get_node_or_null("Z10Art") != null and scene.get_node_or_null("ReceptionArt") != null
	)
	if narrative == null:
		_finish()
		return

	var roots := get_tree().get_nodes_in_group("fm_narrative")
	print("TEST_NARRATIVE roots=%d expected=%d" % [roots.size(), EXPECTED_IDS.size()])
	_check("narrative_root_count", roots.size() == EXPECTED_IDS.size())

	var ids := {}
	var all_ids_unique := true
	for node in roots:
		if not (node is Node3D):
			all_ids_unique = false
			continue
		var anchor := node as Node3D
		var id := String(anchor.get_meta("narrative_id", ""))
		if id == "" or ids.has(id):
			all_ids_unique = false
		ids[id] = true
		_check("anchor_%s_node3d" % id, anchor is Node3D)
		_check("anchor_%s_meshes" % id, anchor.find_children("*", "MeshInstance3D", true, false).size() >= 3)
		var expected := id in EXPECTED_IDS
		_check("anchor_%s_expected" % id, expected)
		if not expected:
			continue
		var pos := anchor.global_position
		var sector: String = SECTORS.get(id, "")
		var rect := RECEPTION_SECTOR if sector == "RECEPTION" else Z10_SECTOR
		var polyline := RECEPTION_ROUTE if sector == "RECEPTION" else Z10_ROUTE
		var distance := _polyline_distance(Vector2(pos.x, pos.z), polyline)
		var in_sector := rect.has_point(Vector2(pos.x, pos.z))
		print("NARRATIVE %s sector=%s pos=%s distance=%.2f in_sector=%s" % [
			id, sector, str(pos), distance, str(in_sector),
		])
		_check("anchor_%s_route_clear" % id, distance > 1.2)
		_check("anchor_%s_sector" % id, in_sector)
		_check("anchor_%s_sector_meta" % id, String(anchor.get_meta("narrative_sector", "")) == sector)

	_check("narrative_ids_unique", all_ids_unique and ids.size() == EXPECTED_IDS.size())
	for id in EXPECTED_IDS:
		_check("anchor_%s_present" % id, ids.has(id))

	var descendants := _descendants(narrative)
	var collision_shapes := 0
	var collision_objects := 0
	var lights := 0
	for node in descendants:
		if node is CollisionShape3D:
			collision_shapes += 1
		if node is CollisionObject3D:
			collision_objects += 1
		if node is Light3D:
			lights += 1
	print("TEST_NARRATIVE_SAFETY collision_shapes=%d collision_objects=%d lights=%d" % [
		collision_shapes, collision_objects, lights,
	])
	_check("narrative_no_collision_shapes", collision_shapes == 0)
	_check("narrative_no_collision_objects", collision_objects == 0)
	_check("narrative_no_lights", lights == 0)
	_check("narrative_children", narrative.get_child_count() == EXPECTED_IDS.size())

	# Pase de materiales: sets PBR existentes + micro-normales procedurales.
	var mats: Dictionary = narrative.get("_mats")
	var textured_keys := ["steel", "steel_dark", "steel_worn", "rubber"]
	for key in textured_keys:
		var mat := mats.get(key) as StandardMaterial3D
		_check(
			"material_%s_textured_triplanar" % key,
			mat != null and mat.albedo_texture != null and mat.uv1_triplanar
		)
	var anisotropic := true
	for key in textured_keys:
		var mat := mats.get(key) as StandardMaterial3D
		if mat == null or mat.texture_filter != BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC:
			anisotropic = false
	_check("material_textured_anisotropic", anisotropic)
	for key in ["paper", "fabric_dark", "leather", "uniform"]:
		var mat := mats.get(key) as StandardMaterial3D
		_check(
			"material_%s_micro_normal" % key,
			mat != null and mat.normal_enabled and mat.normal_texture != null
		)
	for key in ["screen_checkin", "led_red"]:
		var mat := mats.get(key) as StandardMaterial3D
		_check("material_%s_emissive" % key, mat != null and mat.emission_enabled)

	_finish()


func _descendants(node: Node) -> Array[Node]:
	var result: Array[Node] = []
	for child in node.get_children():
		result.append(child)
		result.append_array(_descendants(child))
	return result


func _polyline_distance(point: Vector2, polyline: Array) -> float:
	var best := INF
	for i in polyline.size() - 1:
		var a: Vector2 = polyline[i]
		var b: Vector2 = polyline[i + 1]
		var ab := b - a
		var length_squared := ab.length_squared()
		var t := 0.0
		if length_squared > 0.0:
			t = clampf((point - a).dot(ab) / length_squared, 0.0, 1.0)
		var closest := a + ab * t
		best = minf(best, point.distance_to(closest))
	return best


func _check(label: String, condition: bool) -> void:
	if condition:
		passes += 1
		print("PASS %s" % label)
	else:
		fails += 1
		print("FAIL %s" % label)


func _fail(message: String) -> void:
	fails += 1
	print("FAIL %s" % message)


func _finish() -> void:
	print("FM_NARRATIVE_TEST: %s (%d PASS / %d FAIL)" % [
		"PASS" if fails == 0 else "FAIL", passes, fails,
	])
	get_tree().quit(0 if fails == 0 else 1)
