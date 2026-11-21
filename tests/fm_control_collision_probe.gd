extends Node

func _ready() -> void:
	var packed := load("res://scenes/fm/level1_v06.tscn") as PackedScene
	var scene = packed.instantiate()
	add_child(scene)
	var guard := 0
	while not scene.level_ready and guard < 3600:
		await get_tree().process_frame
		guard += 1
	var body := scene.get_node_or_null("Collision_Control")
	print("PROBE body=", body, " colliders=", scene.collider_counts.get("Control", -1))
	if body != null:
		for c in body.get_children():
			if not (c is CollisionShape3D):
				continue
			var cs := c as CollisionShape3D
			var p := cs.global_position
			if cs.shape is BoxShape3D:
				var half: Vector3 = (cs.shape as BoxShape3D).size * 0.5
				var lo := p - half
				var hi := p + half
				if hi.x >= -92.5 and lo.x <= -90.5 and hi.z >= -48.0 and lo.z <= -46.0:
					print("PROBE box ", cs.name, " pos=", p, " size=", (cs.shape as BoxShape3D).size, " lo=", lo, " hi=", hi)
			elif p.x >= -93.5 and p.x <= -89.5 and p.z >= -48.5 and p.z <= -45.0:
				print("PROBE other ", cs.name, " pos=", p, " class=", cs.shape.get_class())
	get_tree().quit()
