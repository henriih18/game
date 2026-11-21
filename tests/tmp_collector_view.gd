extends Node

func _ready() -> void:
	var stage := Node3D.new()
	add_child(stage)
	var data := FMCreatureModels.build_collector(stage)
	var cam := Camera3D.new()
	cam.fov = 42.0
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.06, 0.065, 0.07)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.35, 0.38, 0.42)
	env.ambient_light_energy = 0.8
	var we := WorldEnvironment.new()
	we.environment = env
	stage.add_child(we)
	add_child(cam)
	cam.position = Vector3(2.8, 1.6, -5.2)
	cam.look_at(Vector3(0, 1.2, 0), Vector3.UP)
	var key := OmniLight3D.new()
	key.position = Vector3(2.4, 3.4, -4.2)
	key.light_energy = 10.0
	key.omni_range = 12.0
	key.light_color = Color(1.0, 0.86, 0.72)
	key.shadow_enabled = true
	add_child(key)
	var rim := OmniLight3D.new()
	rim.light_energy = 6.0
	rim.omni_range = 9.0
	rim.light_color = Color(0.55, 0.68, 1.0)
	rim.position = Vector3(-2.6, 2.9, 3.2)
	stage.add_child(rim)
	var fill := OmniLight3D.new()
	fill.position = Vector3(-3.2, 2.0, -2.4)
	fill.light_energy = 5.0
	fill.omni_range = 9.0
	fill.light_color = Color(0.55, 0.7, 1.0)
	add_child(fill)
	var floor_mesh := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2(12, 12)
	floor_mesh.mesh = plane
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.09, 0.10, 0.10)
	mat.roughness = 0.92
	floor_mesh.material_override = mat
	floor_mesh.position.y = -0.02
	add_child(floor_mesh)
	for i in 40:
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.save_png("/tmp/opencode/collector_model.png")
	print("COLLECTOR_SHOT ", img.get_width(), "x", img.get_height())
	get_tree().quit()
