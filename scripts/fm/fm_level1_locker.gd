extends Node3D

## Puerta de taquilla local del Nivel 1.

var game
var locker_id := ""
var width := 0.86
var height := 1.90
var is_open := false
var busy := false
var _tween: Tween

func setup(id: String, width_m: float, height_m: float, game_ref) -> void:
	locker_id = id
	width = width_m
	height = height_m
	game = game_ref
	name = "Locker_%s" % id
	add_to_group("fm_interactable")
	_build()

func _build() -> void:
	var dark := StandardMaterial3D.new()
	dark.albedo_color = Color(0.07, 0.095, 0.10, 1.0)
	dark.metallic = 0.70
	dark.roughness = 0.40
	var inset := StandardMaterial3D.new()
	inset.albedo_color = Color(0.095, 0.13, 0.135, 1.0)
	inset.metallic = 0.55
	inset.roughness = 0.48
	var steel := StandardMaterial3D.new()
	steel.albedo_color = Color(0.44, 0.47, 0.50, 1.0)
	steel.metallic = 0.90
	steel.roughness = 0.28

	var leaf := MeshInstance3D.new()
	var leaf_mesh := BoxMesh.new()
	leaf_mesh.size = Vector3(width, height, 0.045)
	leaf.mesh = leaf_mesh
	leaf.position = Vector3(width * 0.5, height * 0.5, 0.0)
	leaf.material_override = dark
	add_child(leaf)

	var panel := MeshInstance3D.new()
	var panel_mesh := BoxMesh.new()
	panel_mesh.size = Vector3(width * 0.72, height * 0.50, 0.012)
	panel.mesh = panel_mesh
	panel.position = Vector3(width * 0.5, height * 0.58, 0.030)
	panel.material_override = inset
	add_child(panel)

	for i in range(4):
		var vent := MeshInstance3D.new()
		var vent_mesh := BoxMesh.new()
		vent_mesh.size = Vector3(width * 0.38, 0.018, 0.010)
		vent.mesh = vent_mesh
		vent.position = Vector3(width * 0.5, height * 0.78 + i * 0.045, 0.038)
		vent.material_override = dark
		add_child(vent)

	var handle := MeshInstance3D.new()
	var handle_mesh := BoxMesh.new()
	handle_mesh.size = Vector3(0.055, 0.20, 0.045)
	handle.mesh = handle_mesh
	handle.position = Vector3(width * 0.82, height * 0.48, 0.060)
	handle.material_override = steel
	add_child(handle)

	var label := Label3D.new()
	label.text = "NEXUS // %s" % locker_id
	label.font_size = 22
	label.pixel_size = 0.0024
	label.modulate = Color(0.62, 0.76, 0.82, 1.0)
	label.outline_size = 3
	label.outline_modulate = Color(0.0, 0.0, 0.0, 1.0)
	label.position = Vector3(width * 0.5, height * 0.20, 0.048)
	add_child(label)

	_merge_visual_parts()

	var collider := StaticBody3D.new()
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(width, height, 0.10)
	shape.shape = box
	collider.add_child(shape)
	collider.position = Vector3(width * 0.5, height * 0.5, 0.0)
	add_child(collider)

func _merge_visual_parts() -> void:
	var groups := {}
	for child in get_children():
		if child is MeshInstance3D and child.mesh != null and child.material_override != null:
			var material = child.material_override
			if not groups.has(material):
				groups[material] = []
			groups[material].append(child)
	if groups.is_empty():
		return
	var merged := ArrayMesh.new()
	for material in groups.keys():
		var st := SurfaceTool.new()
		st.begin(Mesh.PRIMITIVE_TRIANGLES)
		for mesh_instance in groups[material]:
			st.append_from(mesh_instance.mesh, 0, mesh_instance.transform)
		st.set_material(material)
		st.commit(merged)
	for material in groups.keys():
		for mesh_instance in groups[material]:
			mesh_instance.queue_free()
	var merged_instance := MeshInstance3D.new()
	merged_instance.name = "MergedVisual"
	merged_instance.mesh = merged
	add_child(merged_instance)

func can_interact(player) -> bool:
	return not busy and player != null and global_position.distance_to(player.global_position) <= 2.4

func get_interaction_prompt() -> String:
	return "E CERRAR TAQUILLA" if is_open else "E ABRIR TAQUILLA"

func get_interaction_position() -> Vector3:
	return global_position + Vector3(0.0, 1.1, 0.0)

func interact(_player) -> void:
	if busy:
		return
	is_open = not is_open
	var target := deg_to_rad(-96.0) if is_open else 0.0
	if game != null and game.has_method("emit_noise"):
		game.emit_noise(global_position, 3.0 if is_open else 2.2, "locker")
	Audio.play_sfx("click", -14.0, 0.84 if is_open else 1.0)
	busy = true
	if _tween != null and _tween.is_valid():
		_tween.kill()
	_tween = create_tween()
	_tween.tween_property(self, "rotation:y", target, 0.48).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	_tween.finished.connect(func(): busy = false)
