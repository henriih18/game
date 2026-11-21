extends Node3D

const SECTOR := preload("res://assets/models/fm/reception_sector.glb")
const BOUNDS := AABB(Vector3(-110.5, -0.6, 3.5), Vector3(41.0, 6.2, 37.0))
const SPEED := 3.0
const FRAMES := 360

var sector: Node3D
var body: CharacterBody3D
var start_pos: Vector3
var min_y := 99.0


func _ready() -> void:
	sector = SECTOR.instantiate()
	add_child(sector)
	await get_tree().process_frame

	var collision := FMGLBCollision.build(self, sector, BOUNDS)
	print("RECEPTION_COLLISION_BUILD count=%d trimesh=%d" % [
		collision.get("count", 0), collision.get("trimesh", 0)
	])
	var body_node: StaticBody3D = collision.get("body")
	if body_node != null:
		for child in body_node.get_children():
			if child is CollisionShape3D and child.shape is BoxShape3D:
				var bs := child.shape as BoxShape3D
				if maxf(bs.size.x, bs.size.z) > 10.0:
					print("RECEPTION_COLLISION_BIGBOX pos=%s size=%s" % [
						child.position, bs.size
					])

	# Las formas recién creadas necesitan un paso de física antes del raycast.
	await get_tree().physics_frame
	await get_tree().physics_frame

	var floor_hit := _ray(Vector3(-94.0, 3.0, 20.0), Vector3(-94.0, -1.0, 20.0))
	var floor_hit_all := _ray_mask(Vector3(-94.0, 3.0, 20.0), Vector3(-94.0, -1.0, 20.0), 0xFFFFFFFF)
	print("RECEPTION_COLLISION_RAY_LAYER1 %s" % floor_hit)
	print("RECEPTION_COLLISION_RAY_ALL %s" % floor_hit_all)
	if floor_hit.is_empty():
		print("RECEPTION_COLLISION_FAIL no_floor_hit")
		get_tree().quit(1)
		return
	var floor_y: float = floor_hit.get("position", Vector3.ZERO).y
	print("RECEPTION_COLLISION_FLOOR y=%.3f" % floor_y)

	body = CharacterBody3D.new()
	body.name = "TestCapsule"
	body.collision_layer = 2
	body.collision_mask = 1
	body.floor_snap_length = 0.25
	var shape := CapsuleShape3D.new()
	shape.radius = 0.38
	shape.height = 1.70
	var col := CollisionShape3D.new()
	col.shape = shape
	body.add_child(col)
	add_child(body)
	body.global_position = Vector3(-94.0, floor_y + 0.95, 9.5)
	start_pos = body.global_position
	await get_tree().physics_frame
	await get_tree().physics_frame

	for i in range(FRAMES):
		body.velocity.x = 0.0
		body.velocity.z = SPEED
		body.velocity.y -= 9.8 * get_physics_process_delta_time()
		body.move_and_slide()
		min_y = minf(min_y, body.global_position.y)
		await get_tree().physics_frame

	var end_pos := body.global_position
	var travelled := end_pos.z - start_pos.z
	var ok := end_pos.z > 22.0 and min_y > -0.5 and absf(end_pos.x - (-94.0)) < 4.0
	print("RECEPTION_COLLISION_CAPSULE start=(%.2f,%.2f,%.2f) end=(%.2f,%.2f,%.2f) travelled_z=%.2f min_y=%.2f" % [
		start_pos.x, start_pos.y, start_pos.z,
		end_pos.x, end_pos.y, end_pos.z,
		travelled, min_y
	])
	if ok:
		print("RECEPTION_COLLISION_OK")
		get_tree().quit(0)
	else:
		print("RECEPTION_COLLISION_FAIL capsule_blocked_or_fell")
		get_tree().quit(1)


func _ray(from: Vector3, to: Vector3) -> Dictionary:
	return _ray_mask(from, to, 1)


func _ray_mask(from: Vector3, to: Vector3, mask: int) -> Dictionary:
	var query := PhysicsRayQueryParameters3D.create(from, to, mask)
	return get_world_3d().direct_space_state.intersect_ray(query)
