extends Node3D

const GLB := preload("res://assets/models/fm/reception_lod_test.glb")

var camera: Camera3D
var groups := {}


func _ready() -> void:
	var root := GLB.instantiate()
	add_child(root)
	await get_tree().process_frame

	camera = Camera3D.new()
	camera.position = Vector3(-90.0, 1.7, 20.0)
	camera.current = true
	add_child(camera)

	var light := DirectionalLight3D.new()
	light.rotation_degrees = Vector3(-45.0, 35.0, 0.0)
	add_child(light)

	var env := WorldEnvironment.new()
	var environment := Environment.new()
	environment.background_mode = Environment.BG_COLOR
	environment.background_color = Color(0.04, 0.04, 0.05)
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.ambient_light_color = Color(0.35, 0.38, 0.42)
	environment.ambient_light_energy = 1.0
	env.environment = environment
	add_child(env)

	for node in root.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi == null or mi.mesh == null:
			continue
		var n := mi.name
		var level := 0
		if "_LOD1" in n:
			level = 1
		elif "_LOD2" in n:
			level = 2
		var base := n.replace("_LOD1", "").replace("_LOD2", "")
		base = base.split(".")[0]
		for suffix in ["_001", "_002", "_003", "_004", "_005"]:
			if base.ends_with(suffix):
				base = base.substr(0, base.length() - suffix.length())
				break
		if not groups.has(base):
			groups[base] = {}
		groups[base][level] = mi

	var visible_by_level := {0: 0, 1: 0, 2: 0}
	var missing := 0
	var multi := 0
	var missing_names: Array[String] = []
	for base in groups:
		var levels: Dictionary = groups[base]
		if not levels.has(0):
			missing += 1
			missing_names.append(str(base))
			continue
		var box: AABB = levels[0].global_transform * levels[0].get_aabb()
		var dist := camera.global_position.distance_to(box.get_center())
		var want := 0
		if dist > 10.0:
			want = 1
		if dist > 20.0:
			want = 2
		while want > 0 and not levels.has(want):
			want -= 1
		var seen := 0
		for level in [0, 1, 2]:
			if levels.has(level):
				levels[level].visible = (level == want)
				if levels[level].visible:
					seen += 1
		if seen != 1:
			multi += 1
		visible_by_level[want] += 1

	print("RECEPTION_LOD_SWITCH groups=%d visible=%d lod0=%d lod1=%d lod2=%d missing_lod0=%d multi_visible=%d" % [
		groups.size(),
		visible_by_level[0] + visible_by_level[1] + visible_by_level[2],
		visible_by_level[0], visible_by_level[1], visible_by_level[2],
		missing, multi,
	])
	if not missing_names.is_empty():
		print("RECEPTION_LOD_SWITCH_MISSING ", missing_names)

	await get_tree().process_frame
	await get_tree().process_frame
	await get_tree().process_frame
	var draw_calls := Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)
	var objects := Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME)
	var primitives := Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)
	print("RECEPTION_LOD_DRAW_CALLS draw_calls=%d objects=%d primitives=%d" % [
		int(draw_calls), int(objects), int(primitives)
	])

	# Base de comparación: solo LOD0 visible, sin conmutación.
	for base in groups:
		var levels: Dictionary = groups[base]
		for level in [0, 1, 2]:
			if levels.has(level):
				levels[level].visible = (level == 0)
	await get_tree().process_frame
	await get_tree().process_frame
	await get_tree().process_frame
	var base_calls := Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)
	var base_objects := Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME)
	var base_primitives := Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)
	print("RECEPTION_DRAW_CALLS_BASELINE draw_calls=%d objects=%d primitives=%d" % [
		int(base_calls), int(base_objects), int(base_primitives)
	])

	if groups.size() == 44 and missing == 0 and multi == 0:
		print("RECEPTION_LOD_SWITCH_OK")
		get_tree().quit(0)
	else:
		print("RECEPTION_LOD_SWITCH_FAIL")
		get_tree().quit(1)
