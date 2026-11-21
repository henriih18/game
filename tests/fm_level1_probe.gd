extends Node

func _ready() -> void:
	var scene = load("res://scenes/fm/level1.tscn").instantiate()
	add_child(scene)
	await get_tree().create_timer(2.5).timeout
	var space := get_viewport().world_3d.direct_space_state
	var rooms := {
		"REC": Vector3(-12.0, -4.0, -6.5),
		"SEG": Vector3(3.0, -4.0, -5.5),
		"CTL": Vector3(13.0, -4.0, -5.5),
		"VEST": Vector3(-15.0, -4.0, 5.5),
		"ALM": Vector3(-3.0, -4.0, 5.5),
		"MANT": Vector3(13.0, -4.0, 5.5),
		"OFI": Vector3(-6.3, -4.0, -4.5),
	}
	for key in rooms:
		var c: Vector3 = rooms[key]
		for dir in [Vector3.UP, Vector3.DOWN]:
			var q := PhysicsRayQueryParameters3D.create(c, c + dir * 12.0)
			var hit := space.intersect_ray(q)
			print("PROBE ", key, " ", "UP" if dir == Vector3.UP else "DOWN", " ", ("none" if hit.is_empty() else "%s y=%.2f" % [hit.collider.name, hit.position.y]))
		for pair in [["X+", Vector3.RIGHT], ["X-", Vector3.LEFT], ["Z+", Vector3.BACK], ["Z-", Vector3.FORWARD]]:
			var q2 := PhysicsRayQueryParameters3D.create(c, c + pair[1] * 20.0)
			var h2 := space.intersect_ray(q2)
			print("PROBE ", key, " ", pair[0], " ", ("none" if h2.is_empty() else "%s d=%.2f" % [h2.collider.name, c.distance_to(h2.position)]))
	get_tree().quit()
