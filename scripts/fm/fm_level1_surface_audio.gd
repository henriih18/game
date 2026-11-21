extends Node3D

## Audio de pasos por superficie, local al Nivel 1.
## Usa los SFX existentes y sintetiza variantes por pitch/volumen.

var player
var game
var last_surface := "concrete"

func setup(player_ref, game_ref) -> void:
	player = player_ref
	game = game_ref
	name = "Level1SurfaceAudio"

func play_footstep(sprinting: bool, crouching: bool, noise_radius: float) -> bool:
	if player == null or not is_instance_valid(player):
		return false
	last_surface = _surface_at(player.global_position)
	var pitch := 0.92
	var volume := -19.0
	match last_surface:
		"metal":
			pitch = 1.18
			volume = -17.0
		"glass":
			pitch = 1.26
			volume = -18.0
		"wood":
			pitch = 0.82
			volume = -20.0
		"rubber":
			pitch = 0.72
			volume = -22.0
		"tile":
			pitch = 1.06
			volume = -19.0
		"wet":
			pitch = 0.88
			volume = -18.0
		"carpet":
			pitch = 0.68
			volume = -24.0
		_:
			pitch = 0.92
			volume = -19.0
	if sprinting:
		volume += 4.0
	elif crouching:
		volume -= 6.0
	Audio.play_sfx("step", volume, pitch * randf_range(0.96, 1.04))
	if last_surface == "metal" or last_surface == "glass":
		Audio.play_sfx("click", volume - 12.0, pitch * 0.82)
	elif last_surface == "wet":
		Audio.play_sfx("drop", volume - 13.0, 1.35)
	if game != null and game.has_method("emit_noise"):
		game.emit_noise(player.global_position, noise_radius, "step_" + last_surface)
	return true

func _surface_at(position: Vector3) -> String:
	var query := PhysicsRayQueryParameters3D.create(
		position + Vector3(0.0, 0.25, 0.0),
		position + Vector3(0.0, -1.10, 0.0)
	)
	query.collision_mask = 1
	var hit := get_world_3d().direct_space_state.intersect_ray(query)
	if hit.is_empty():
		return "concrete"
	var collider = hit.get("collider")
	if collider == null:
		return "concrete"
	var n := String(collider.name).to_upper()
	if "GRATE" in n or "METAL" in n or "STEEL" in n or "SERVICE_CONN" in n:
		return "metal"
	if "GLASS" in n or "CRISTAL" in n:
		return "glass"
	if "WOOD" in n or "MADERA" in n or "CRATE" in n:
		return "wood"
	if "RUBBER" in n or "GOMA" in n:
		return "rubber"
	if "TILE" in n or "CERAMIC" in n or "REST" in n or "VEST" in n:
		return "tile"
	if "WET" in n or "WATER" in n or "SPILL" in n:
		return "wet"
	if "CARPET" in n or "RUG" in n or "MAT" in n:
		return "carpet"
	return "concrete"
