extends Node

func _ready() -> void:
	var packed := load("res://scenes/fm/level1.tscn")
	var scene = packed.instantiate()
	add_child(scene)
	await get_tree().create_timer(2.5).timeout
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	if scene.player != null:
		scene.player.rotation.y = 0.0
		scene.player.camera.rotation.x = -0.045
		scene.player.camera.rotation.y = 0.0
	await get_tree().create_timer(1.0).timeout
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.save_png("/tmp/opencode/level1_godot.png")
	print("LEVEL1_SHOT %dx%d" % [img.get_width(), img.get_height()])
	get_tree().quit()
