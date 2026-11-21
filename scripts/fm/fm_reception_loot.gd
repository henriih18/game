extends FMCarryItem
class_name FMReceptionLoot

## Recuperable de la recepción. Usa las mallas del GLB en lugar del
## núcleo procedural de FMCarryItem.

@export var loot_id := ""
@export var loot_value := 0
@export var min_players := 1
@export var fragile := false

func _ready() -> void:
	# La recepción está en y=-5.65; el límite por defecto de -4 lo
	# devolvería a su posición inicial constantemente.
	fall_limit_y = -20.0
	super._ready()

func _build_visual() -> void:
	# El visual lo aportan las mallas del GLB, reparentadas por reception_slice.
	pass

func can_pickup(_player: Node3D) -> bool:
	if min_players <= 1:
		return true
	if game == null:
		return false
	return int(game.get_active_player_count()) >= min_players

func pickup(player: Node3D) -> bool:
	if not can_pickup(player):
		if game != null:
			game.notify("REQUIERE 2 PERSONAS")
		return false
	return super.pickup(player)
