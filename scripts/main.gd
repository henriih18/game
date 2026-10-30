extends Node2D

const TOTAL_COINS := 3

var coins_collected := 0

@onready var coin_label: Label = $HUD/CoinLabel

func _ready() -> void:
	for coin in $Coins.get_children():
		coin.collected.connect(_on_coin_collected)

func _on_coin_collected() -> void:
	coins_collected += 1
	if coins_collected >= TOTAL_COINS:
		coin_label.text = "¡Robo completo!"
	else:
		coin_label.text = "Monedas: %d / %d" % [coins_collected, TOTAL_COINS]
