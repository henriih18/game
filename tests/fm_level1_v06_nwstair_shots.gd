extends Node

const OUTPUT := "/tmp/opencode/nws_godot_"

var _views := [
	["access", Vector3(-72.0, -2.6, -61.0), Vector3(-72.0, -4.2, -67.0), 3.2],
	["door", Vector3(-72.0, -2.35, -67.0), Vector3(-72.0, -2.8, -64.2), 2.8],
	["pumps", Vector3(-74.3, -2.7, -64.8), Vector3(-74.3, -3.8, -66.85), 2.8],
	["electrical", Vector3(-72.6, -2.4, -66.8), Vector3(-75.6, -3.0, -66.4), 2.8],
	["workbench", Vector3(-70.2, -2.6, -67.2), Vector3(-68.4, -3.5, -69.2), 2.4],
	["overview", Vector3(-74.0, -2.6, -66.0), Vector3(-70.5, -3.8, -69.2), 2.6],
]


func _ready() -> void:
	var scene: Node = load("res://scenes/fm/level1_v06.tscn").instantiate()
	add_child(scene)
	while not scene.level_ready:
		await get_tree().process_frame
	await get_tree().create_timer(0.6).timeout
	if scene.watcher != null and is_instance_valid(scene.watcher):
		scene.watcher.set_physics_process(false)
	if scene.security_watcher != null and is_instance_valid(scene.security_watcher):
		scene.security_watcher.set_physics_process(false)
	if scene.hud != null and is_instance_valid(scene.hud):
		scene.hud.visible = false
	var cam := Camera3D.new()
	cam.fov = 68.0
	cam.near = 0.04
	cam.far = 140.0
	add_child(cam)
	cam.current = true
	var lamp := OmniLight3D.new()
	lamp.omni_range = 10.0
	lamp.light_energy = 1.9
	lamp.light_color = Color(0.86, 0.92, 1.0)
	lamp.shadow_enabled = false
	cam.add_child(lamp)
	for view in _views:
		cam.global_position = view[1]
		cam.look_at(view[2], Vector3.UP)
		lamp.light_energy = float(view[3]) if view.size() > 3 else 1.9
		await get_tree().create_timer(0.35).timeout
		await RenderingServer.frame_post_draw
		var img := get_viewport().get_texture().get_image()
		img.save_png("%s%s.png" % [OUTPUT, view[0]])
		print("NWS_SHOT %s %dx%d" % [view[0], img.get_width(), img.get_height()])
	get_tree().quit(0)
