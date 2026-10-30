extends Control

const PORT := 7777
const MAX_PLAYERS := 4
const GAME_SCENE := "res://scenes/main.tscn"
const SLICE_SCENE := "res://scenes/fm/vertical_slice.tscn"
const LOOKDEV_SCENE := "res://scenes/fm/lookdev.tscn"
const DEMO3D_SCENE := "res://scenes/demo3d.tscn"
const DEMO3D_FP_SCENE := "res://scenes/demo3d_fp.tscn"

@onready var ip_edit: LineEdit = $IPEdit
@onready var status: Label = $Status

func _ready() -> void:
	Audio.play_music("menu")
	modulate.a = 0.0
	create_tween().tween_property(self, "modulate:a", 1.0, 0.35)

	_style_button($SliceButton)
	_style_button($HostButton)
	_style_button($JoinButton)
	_style_button($LocalButton)
	_style_button($Demo3DButton)
	_style_button($DemoFPButton)
	_style_button($LookDevButton)
	_style_line_edit($IPEdit)
	_wire_button($SliceButton)
	_wire_button($HostButton)
	_wire_button($JoinButton)
	_wire_button($LocalButton)
	_wire_button($Demo3DButton)
	_wire_button($DemoFPButton)
	_wire_button($LookDevButton)

	$SliceButton.pressed.connect(_slice)
	$HostButton.pressed.connect(_host)
	$JoinButton.pressed.connect(_join)
	$LocalButton.pressed.connect(_local)
	$Demo3DButton.pressed.connect(_demo3d)
	$DemoFPButton.pressed.connect(_demo3d_fp)
	$LookDevButton.pressed.connect(_lookdev)
	$IPEdit.text_submitted.connect(func(_text: String): _join())

	multiplayer.connected_to_server.connect(_on_connected, CONNECT_ONE_SHOT)
	multiplayer.connection_failed.connect(_on_connection_failed, CONNECT_ONE_SHOT)

	_float_title()
	$SliceButton.grab_focus()
	_handle_cmdline.call_deferred()

func _wire_button(button: Button) -> void:
	button.pressed.connect(func(): Audio.play_sfx("click", -11.0))
	button.mouse_entered.connect(func(): Audio.play_sfx("click", -24.0, 1.35))

func _float_title() -> void:
	var title: Label = $Title
	var tween := create_tween().set_loops()
	tween.tween_property(title, "position:y", -7.0, 2.4).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	tween.tween_property(title, "position:y", 0.0, 2.4).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)

func _handle_cmdline() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg == "--host":
			_host()
			return
		if arg == "--slice":
			_slice()
			return
		if arg == "--lookdev":
			_lookdev()
			return
		if arg == "--local":
			_local()
			return
		if arg == "--demo3d":
			_demo3d()
			return
		if arg == "--demo3dfp":
			_demo3d_fp()
			return
		if arg.begins_with("--join="):
			ip_edit.text = arg.get_slice("=", 1)
			_join()
			return

func _style_button(button: Button) -> void:
	var normal := StyleBoxFlat.new()
	normal.bg_color = Color(0.045, 0.075, 0.065, 0.96)
	normal.border_color = Color(0.2, 0.38, 0.29, 0.8)
	normal.set_border_width_all(1)
	normal.set_corner_radius_all(5)
	normal.set_content_margin_all(10)

	var hover := normal.duplicate() as StyleBoxFlat
	hover.bg_color = Color(0.075, 0.13, 0.105, 1.0)
	hover.border_color = Color(0.48, 0.68, 0.42, 0.9)

	var pressed := normal.duplicate() as StyleBoxFlat
	pressed.bg_color = Color(0.025, 0.045, 0.04, 1.0)

	button.add_theme_stylebox_override("normal", normal)
	button.add_theme_stylebox_override("hover", hover)
	button.add_theme_stylebox_override("pressed", pressed)
	button.add_theme_stylebox_override("focus", hover)
	button.add_theme_font_size_override("font_size", 19)
	button.add_theme_color_override("font_color", Color(0.86, 0.9, 0.78, 1.0))
	button.add_theme_color_override("font_hover_color", Color(0.98, 0.9, 0.62, 1.0))

func _style_line_edit(edit: LineEdit) -> void:
	var box := StyleBoxFlat.new()
	box.bg_color = Color(0.025, 0.045, 0.04, 1.0)
	box.border_color = Color(0.24, 0.42, 0.32, 1.0)
	box.set_border_width_all(1)
	box.set_corner_radius_all(5)
	box.set_content_margin_all(9)
	edit.add_theme_stylebox_override("normal", box)
	edit.add_theme_stylebox_override("focus", box)
	edit.add_theme_font_size_override("font_size", 16)
	edit.add_theme_color_override("font_color", Color(0.86, 0.9, 0.8, 1.0))
	edit.add_theme_color_override("font_placeholder_color", Color(0.42, 0.5, 0.44, 1.0))
	edit.add_theme_color_override("caret_color", Color(0.7, 0.82, 0.55, 1.0))

func _host() -> void:
	var peer := ENetMultiplayerPeer.new()
	var err := peer.create_server(PORT, MAX_PLAYERS)
	if err != OK:
		_set_status("No se pudo abrir el puerto %d (error %d)." % [PORT, err], true)
		return
	multiplayer.multiplayer_peer = peer
	get_tree().change_scene_to_file(GAME_SCENE)

func _join() -> void:
	var address := ip_edit.text.strip_edges()
	if address.is_empty():
		_set_status("Escribí la IP del anfitrión (o 127.0.0.1 en esta PC).", true)
		return
	var peer := ENetMultiplayerPeer.new()
	var err := peer.create_client(address, PORT)
	if err != OK:
		_set_status("No se pudo iniciar la conexión (error %d)." % err, true)
		return
	multiplayer.multiplayer_peer = peer
	_set_status("Conectando a %s..." % address, false)

func _local() -> void:
	_close_peer()
	get_tree().change_scene_to_file(GAME_SCENE)

func _slice() -> void:
	_close_peer()
	get_tree().change_scene_to_file(SLICE_SCENE)

func _lookdev() -> void:
	_close_peer()
	get_tree().change_scene_to_file(LOOKDEV_SCENE)

func _close_peer() -> void:
	if multiplayer.multiplayer_peer != null:
		multiplayer.multiplayer_peer.close()
		multiplayer.multiplayer_peer = null

func _demo3d() -> void:
	if multiplayer.multiplayer_peer != null:
		multiplayer.multiplayer_peer.close()
		multiplayer.multiplayer_peer = null
	get_tree().change_scene_to_file(DEMO3D_SCENE)

func _demo3d_fp() -> void:
	if multiplayer.multiplayer_peer != null:
		multiplayer.multiplayer_peer.close()
		multiplayer.multiplayer_peer = null
	get_tree().change_scene_to_file(DEMO3D_FP_SCENE)

func _on_connected() -> void:
	get_tree().change_scene_to_file(GAME_SCENE)

func _on_connection_failed() -> void:
	if multiplayer.multiplayer_peer != null:
		multiplayer.multiplayer_peer.close()
		multiplayer.multiplayer_peer = null
	_set_status("No se pudo conectar. Revisá la IP y que el anfitrión tenga la partida abierta.", true)

func _set_status(message: String, is_error: bool) -> void:
	status.text = message
	var color := Color(1, 0.45, 0.45) if is_error else Color(0.62, 0.65, 0.74)
	status.add_theme_color_override("font_color", color)
