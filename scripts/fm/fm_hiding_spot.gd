class_name FMHidingSpot
extends Area3D

## Escondite interactivo. No garantiza seguridad absoluta:
## El Vigilante puede investigar la zona si oyó al jugador entrar.

@export var display_name := "TAQUILLA"
@export var use_radius := 2.2

var occupant: Node3D = null
var game: Node = null

func _ready() -> void:
	collision_layer = 0
	collision_mask = 2
	monitoring = true
	monitorable = false
	add_to_group("fm_hiding_spot")
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)

func _on_body_entered(body: Node3D) -> void:
	if body.is_in_group("fm_player"):
		body.set_meta("near_hiding_spot", self)

func _on_body_exited(body: Node3D) -> void:
	if body.is_in_group("fm_player") and body.get_meta("near_hiding_spot", null) == self:
		body.set_meta("near_hiding_spot", null)

func can_use(player: Node3D) -> bool:
	return occupant == null or occupant == player

func is_occupied() -> bool:
	return occupant != null and is_instance_valid(occupant)

func hide_player(player: Node3D) -> bool:
	if not can_use(player):
		return false
	occupant = player
	player.hide_in(self)
	return true

func release_player(player: Node3D) -> void:
	if occupant == player:
		occupant = null

func get_hide_point() -> Vector3:
	var marker := get_node_or_null("HidePoint") as Node3D
	return marker.global_position if marker != null else global_position

func get_exit_point() -> Vector3:
	var marker := get_node_or_null("ExitPoint") as Node3D
	return marker.global_position if marker != null else global_position + Vector3(0, 0, 1.2)

func get_look_direction() -> Vector3:
	return -global_transform.basis.z
