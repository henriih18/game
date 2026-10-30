extends Node2D

const TOTAL_GEMS := 3

var gems_collected := 0
var crate_delivered := false

@onready var status_label: Label = $HUD/StatusLabel

func _ready() -> void:
	for gem in $Gems.get_children():
		gem.connect("collected", _on_gem_collected)
	$ExtractionZone.connect("crate_delivered", _on_crate_delivered)

func _on_gem_collected() -> void:
	gems_collected += 1
	_update_status()

func _on_crate_delivered() -> void:
	crate_delivered = true
	$Crate.call("deliver")
	_update_status()

func _update_status() -> void:
	if gems_collected >= TOTAL_GEMS and crate_delivered:
		status_label.text = "¡ROBO COMPLETO!"
		return
	var crate_state := "extraída" if crate_delivered else "pendiente"
	status_label.text = "Gemas: %d/%d  ·  Caja: %s" % [gems_collected, TOTAL_GEMS, crate_state]
