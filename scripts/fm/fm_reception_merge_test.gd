extends Node3D

const GLB := preload("res://assets/models/fm/reception_lod_test.glb")

var camera: Camera3D


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

	var buckets := {}
	for node in root.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi == null or mi.mesh == null:
			continue
		if "_LOD1" in mi.name or "_LOD2" in mi.name:
			mi.visible = false
			continue
		var mesh := mi.mesh
		for surface in range(mesh.get_surface_count()):
			var material := mesh.surface_get_material(surface)
			var key: Variant = material if material != null else "__null__"
			if not buckets.has(key):
				var st := SurfaceTool.new()
				st.begin(Mesh.PRIMITIVE_TRIANGLES)
				if material != null:
					st.set_material(material)
				buckets[key] = st
			var st: SurfaceTool = buckets[key]
			st.append_from(mesh, surface, mi.global_transform)
		mi.visible = false

	var merged := 0
	for key in buckets:
		var st: SurfaceTool = buckets[key]
		var array_mesh := st.commit()
		if array_mesh == null:
			continue
		var out := MeshInstance3D.new()
		out.name = "MERGED_%02d" % merged
		out.mesh = array_mesh
		add_child(out)
		merged += 1

	await get_tree().process_frame
	await get_tree().process_frame
	await get_tree().process_frame
	var draw_calls := Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)
	var objects := Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME)
	var primitives := Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)
	print("RECEPTION_MERGE materials=%d merged=%d draw_calls=%d objects=%d primitives=%d" % [
		buckets.size(), merged, int(draw_calls), int(objects), int(primitives)
	])
	if merged > 0 and int(draw_calls) < 94:
		print("RECEPTION_MERGE_OK")
		get_tree().quit(0)
	else:
		print("RECEPTION_MERGE_FAIL")
		get_tree().quit(1)
