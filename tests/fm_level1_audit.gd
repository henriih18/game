extends Node

func _ready() -> void:
	var scene = load("res://scenes/fm/level1.tscn").instantiate()
	add_child(scene)
	await get_tree().create_timer(2.5).timeout
	var space := get_viewport().world_3d.direct_space_state
	for pt in [Vector3(-12, -4, -3.0), Vector3(-12, -4, -9.0), Vector3(-18, -4, 0.0), Vector3(0, -4, 0.0), Vector3(18, -4, 0.0)]:
		var q := PhysicsRayQueryParameters3D.create(pt, pt + Vector3.UP * 10.0)
		var hit := space.intersect_ray(q)
		print("CEIL ", pt, " ", ("none" if hit.is_empty() else "%s y=%.2f" % [hit.collider.name, hit.position.y]))
	var lights := []
	for n in scene.find_children("*", "Light3D", true, false):
		lights.append(n)
	print("LIGHTCOUNT ", lights.size())
	for l in lights:
		var extra := ""
		if l is SpotLight3D:
			extra = " spot=%.1f angle=%.1f" % [l.spot_range, l.spot_angle]
		elif l is OmniLight3D:
			extra = " omni=%.1f" % l.omni_range
		print("LIGHT ", l.name, " ", l.get_class(), " pos=", l.global_position, " col=", l.light_color, " e=%.2f" % l.light_energy, extra)
	var mats := {}
	for mi in scene.glb_root.find_children("*", "MeshInstance3D", true, false):
		if mi.mesh == null:
			continue
		for s in range(mi.mesh.get_surface_count()):
			var m = mi.mesh.surface_get_material(s)
			if m == null:
				continue
			var key = m.resource_name
			if not mats.has(key):
				mats[key] = {"count": 0, "albedo": m.albedo_color if m is StandardMaterial3D else Color.BLACK, "metal": m.metallic if m is StandardMaterial3D else 0.0, "rough": m.roughness if m is StandardMaterial3D else 0.0, "tex": (m.albedo_texture != null) if m is StandardMaterial3D else false, "example": mi.name}
			mats[key]["count"] += 1
	for key in mats:
		var d = mats[key]
		print("MAT ", key, " n=", d["count"], " alb=", d["albedo"], " m=%.2f r=%.2f tex=%s ex=%s" % [d["metal"], d["rough"], d["tex"], d["example"]])
	get_tree().quit()
