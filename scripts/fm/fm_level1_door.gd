extends Node3D

## Puerta industrial del Nivel 1.
## Seis tipos con estado propio, cerraduras, alerta, energia y cooperacion.
## La malla viene del kit de Blender; este script solo anima nodos y colisiones.

const KIT_GLB := "res://assets/models/fm/doors/level1_doors.glb"
const RUST_NORMAL := preload("res://assets/art/fm/rust_normal.png")
const RUST_ROUGHNESS := preload("res://assets/art/fm/rust_roughness.png")
const LABELS := {
	"RECEPCION": "RECEPCIÓN",
	"SEGURIDAD": "SEGURIDAD",
	"CONTROL": "CONTROL",
	"ALMACEN": "ALMACÉN",
	"VESTUARIOS": "VESTUARIOS",
	"MANTENIMIENTO": "MANTENIMIENTO",
}
const SPEEDS := {
	"auto_slide": 0.85,
	"armored_swing": 0.78,
	"double_swing_seq": 0.72,
	"heavy_slide": 1.55,
	"light_swing": 0.55,
	"maintenance_swing": 0.68,
}

static var _kit_source: Node3D = null

var game
var door_id := ""
var width := 1.58
var height := 3.00
var hinge_sign := 1.0
var open_angle_deg := 95.0
var is_open := false
var busy := false

var door_type := "light_swing"
var lock_mode := "none"          # none | basic | security | maintenance
var access_code := "0451"
var required_players := 1
var powered := true
var red_alert := false
var _alert_locked := false

var _leaf_a: Node3D
var _leaf_b: Node3D
var _status_mesh: MeshInstance3D
var _status_mat: StandardMaterial3D
var _tween: Tween
var _leaf_tweens: Array[Tween] = []

var _keypad_active := false
var _entered := ""
var _unlocked := false
var _manual_released := false
var _denied_flash := 0.0
var _seq_stage := 0
var _seq_window := 0.0
var _coop_stage := 0
var _coop_window := 0.0
var _coop_player = null
var _hold_active := false
var _hold_player = null
var _hold_time := 0.0
var _auto_close := 0.0

var _latch: AudioStreamPlayer3D
var _motor: AudioStreamPlayer3D
var _alarm: AudioStreamPlayer3D
var _key: AudioStreamPlayer3D


func setup(id: String, width_m: float, height_m: float, side: float, angle_deg: float, game_ref, config: Dictionary = {}) -> void:
	door_id = id
	width = width_m
	height = height_m
	hinge_sign = side
	open_angle_deg = angle_deg
	game = game_ref
	door_type = String(config.get("type", "light_swing"))
	lock_mode = String(config.get("lock", "none"))
	access_code = String(config.get("code", "0451"))
	required_players = int(config.get("players", 1))
	powered = bool(config.get("powered", true))
	name = "Door_%s" % id
	add_to_group("fm_interactable")
	add_to_group("fm_door")
	_build()
	_build_audio()
	_refresh_status()


# ------------------------------------------------------------------ construccion

static func _ensure_kit() -> bool:
	if _kit_source != null:
		return true
	if not FileAccess.file_exists(KIT_GLB):
		push_warning("DOOR_KIT no existe: %s" % KIT_GLB)
		return false
	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	var err: Error = doc.append_from_file(KIT_GLB, state)
	if err != OK:
		push_warning("DOOR_KIT no carga: %s" % err)
		return false
	_kit_source = doc.generate_scene(state)
	return _kit_source != null


func _build() -> void:
	if not _ensure_kit():
		_build_fallback()
		return
	var template: Node = _kit_source.find_child("DOOR_KIT_%s" % door_id, true, false)
	if template == null:
		push_warning("DOOR_KIT sin plantilla para %s" % door_id)
		_build_fallback()
		return
	var kit: Node = template.duplicate()
	add_child(kit)
	_upgrade_kit_materials(kit)
	_leaf_a = _find_part(kit, "LeafA")
	_leaf_b = _find_part(kit, "LeafB")
	if _leaf_a == null:
		push_warning("DOOR_KIT sin LeafA para %s" % door_id)
		_build_fallback()
		return
	_add_leaf_collider(_leaf_a, _leaf_center_a(), _leaf_width_a())
	if _leaf_b != null:
		_add_leaf_collider(_leaf_b, _leaf_center_b(), _leaf_width_b())
	_find_status_mesh(kit)

	# Colision del marco: solo los montantes, para no cerrar el vano.
	_add_frame_collider(-0.045, 0.09)
	_add_frame_collider(width + 0.045, 0.09)

	# Las piezas de cristal y emisivas no proyectan sombra dura.
	for node in kit.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi.mesh == null:
			continue
		for i in range(mi.mesh.get_surface_count()):
			var mat := mi.mesh.surface_get_material(i)
			if mat == null:
				continue
			var n := mat.resource_name.to_lower()
			if "glass" in n or "frost" in n or "status" in n or "cyan" in n or "red" in n:
				mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
				break


func _find_part(root: Node, prefix: String) -> Node3D:
	for node in root.find_children(prefix + "*", "", true, false):
		var n := String(node.name)
		if n == prefix or n.begins_with(prefix + "_") or n.begins_with(prefix + "."):
			return node as Node3D
	return null

func _build_fallback() -> void:
	# Solo se usa si el GLB falta. Mantiene la puerta jugable.
	push_error("DOOR_FALLBACK %s" % door_id)
	var body := StaticBody3D.new()
	body.name = "Door_%s_FallbackCollider" % door_id
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(width, height, 0.18)
	shape.shape = box
	shape.position = Vector3(width * 0.5, height * 0.5, 0.0)
	body.add_child(shape)
	add_child(body)
	_leaf_a = body


func _leaf_width_a() -> float:
	return width * 0.5 + 0.012 if _leaf_b != null or door_type in ["auto_slide", "heavy_slide", "double_swing_seq"] else width - 0.04


func _leaf_width_b() -> float:
	return width * 0.5 + 0.012


func _leaf_center_a() -> float:
	return _leaf_width_a() * 0.5


func _leaf_center_b() -> float:
	return -_leaf_width_b() * 0.5


func _add_leaf_collider(leaf: Node3D, center_x: float, size_x: float) -> void:
	var body := StaticBody3D.new()
	body.name = "DoorCollider_%s_%s" % [door_id, leaf.name]
	body.collision_layer = 1
	body.collision_mask = 1
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(size_x, height - 0.06, 0.18)
	shape.shape = box
	shape.position = Vector3(center_x, height * 0.5, 0.0)
	body.add_child(shape)
	leaf.add_child(body)


func _add_frame_collider(center_x: float, size_x: float) -> void:
	var body := StaticBody3D.new()
	body.name = "DoorCollider_%s_Frame" % door_id
	body.collision_layer = 1
	body.collision_mask = 1
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(size_x, height + 0.14, 0.24)
	shape.shape = box
	shape.position = Vector3(center_x, height * 0.5, 0.0)
	body.add_child(shape)
	add_child(body)


func _add_keypad_hint() -> void:
	var hint := Label3D.new()
	hint.name = "DoorKeypadHint"
	hint.text = "CÓD. 0451"
	hint.font_size = 30
	hint.pixel_size = 0.00125
	hint.modulate = Color(0.95, 0.62, 0.22, 1.0)
	hint.outline_size = 5
	hint.outline_modulate = Color(0.0, 0.0, 0.0, 0.9)
	hint.position = Vector3(width + 0.30, 1.205, 0.165)
	add_child(hint)

func _upgrade_kit_materials(kit: Node) -> void:
	# DOOR_Rust salía del exportador sólo con albedo. Se completa con el set
	# PBR local ya existente para que el óxido responda a la linterna.
	var seen := {}
	for node in kit.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi.mesh == null:
			continue
		for i in range(mi.mesh.get_surface_count()):
			var mat := mi.mesh.surface_get_material(i)
			if mat == null or not (mat is StandardMaterial3D):
				continue
			var src := mat as StandardMaterial3D
			if not src.resource_name.begins_with("DOOR_Rust"):
				continue
			var copy: StandardMaterial3D = seen.get(src.get_instance_id())
			if copy == null:
				copy = src.duplicate() as StandardMaterial3D
				copy.normal_enabled = true
				copy.normal_texture = RUST_NORMAL
				copy.normal_scale = 1.0
				copy.roughness_texture = RUST_ROUGHNESS
				copy.roughness = 1.0
				copy.metallic = 0.32
				copy.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
				seen[src.get_instance_id()] = copy
			mi.set_surface_override_material(i, copy)

func _tint_material(kit: Node, mat_name: String, tint: Color) -> void:
	for node in kit.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi.mesh == null or mi.mesh.get_surface_count() == 0 or mi.material_override != null:
			continue
		var mat := mi.mesh.surface_get_material(0)
		if mat != null and mat.resource_name == mat_name:
			var copy := mat.duplicate() as StandardMaterial3D
			if copy != null:
				copy.albedo_color = tint
				mi.material_override = copy

func _find_status_mesh(kit: Node) -> void:
	var chosen := kit.find_child("%s_Status_Status" % door_id, true, false) as MeshInstance3D
	if chosen == null:
		for node in kit.find_children("*", "MeshInstance3D", true, false):
			var candidate := node as MeshInstance3D
			if candidate.mesh == null or candidate.mesh.get_surface_count() == 0:
				continue
			var m := candidate.mesh.surface_get_material(0)
			if m != null and "status" in m.resource_name.to_lower() and candidate.name.to_lower().contains("status_status"):
				chosen = candidate
				break
	if chosen != null:
		_status_mesh = chosen
		var mat := chosen.mesh.surface_get_material(0)
		_status_mat = mat.duplicate() as StandardMaterial3D if mat != null else StandardMaterial3D.new()
		if _status_mat == null:
			_status_mat = StandardMaterial3D.new()
		_status_mat.emission_enabled = true
		chosen.material_override = _status_mat



func _build_audio() -> void:
	_latch = _make_3d("click", -7.0, 0.92, 9.0)
	_motor = _make_3d("drop", -12.0, 0.50, 16.0)
	_alarm = _make_3d("alarm", -14.0, 0.90, 22.0)
	_key = _make_3d("tick", -11.0, 1.18, 7.0)


func _make_3d(sound: String, db: float, pitch: float, dist: float) -> AudioStreamPlayer3D:
	var p := AudioStreamPlayer3D.new()
	p.name = "DoorAudio_%s" % sound
	var stream: AudioStream = load("res://assets/audio/sfx/%s.wav" % sound)
	if stream == null:
		return p
	p.stream = stream
	p.volume_db = db
	p.pitch_scale = pitch
	p.max_distance = dist
	p.unit_size = 6.0
	add_child(p)
	return p


# ------------------------------------------------------------------ interaccion

func can_interact(player) -> bool:
	if busy or player == null:
		return false
	return global_position.distance_to(player.global_position) <= 3.4


func get_interaction_prompt() -> String:
	if _keypad_active:
		return "CÓDIGO: %s   [ENTER] CONFIRMAR   [ESC] CANCELAR" % ("*".repeat(_entered.length()) if _entered.length() > 0 else "____")
	if red_alert and door_type != "maintenance_swing":
		return "ALERTA ROJA · PUERTA BLOQUEADA"
	if door_type == "heavy_slide":
		if is_open:
			return "E CERRAR PUERTA PESADA"
		if _coop_stage == 1:
			return "E SEGUNDO OPERADOR · ABRIR   |   MANTÉN E 4 s · LIBERAR EN SOLITARIO"
		return "E AGARRAR HOJA PESADA · 2 OPERADORES"
	if door_type == "double_swing_seq":
		if is_open:
			return "E CERRAR PUERTA DOBLE"
		if _seq_stage == 1:
			return "E ABRIR HOJA B · MANTÉN LA SECUENCIA"
		return "E LIBERAR HOJA A"
	if door_type == "maintenance_swing" and not _manual_released:
		return "MANTÉN E · LIBERACIÓN MANUAL"
	if door_type == "auto_slide" and not powered:
		return "MANTÉN E · APERTURA MANUAL SIN ENERGÍA"
	if door_type == "armored_swing" and lock_mode == "security" and not _unlocked:
		return "E INTRODUCIR CÓDIGO DE SEGURIDAD"
	return "E CERRAR PUERTA" if is_open else "E ABRIR PUERTA"


func get_interaction_position() -> Vector3:
	return to_global(Vector3(width * 0.5, 1.15, 0.0))


func interact(player) -> void:
	if player == null or busy:
		return
	if _denied_flash > 0.0:
		return
	if _keypad_active:
		_submit_code()
		return
	if red_alert and door_type != "maintenance_swing":
		_deny()
		return
	if door_type == "armored_swing" and lock_mode == "security" and not _unlocked:
		_keypad_active = true
		_entered = ""
		_play(_key)
		_refresh_status()
		return
	if door_type == "maintenance_swing" and not _manual_released:
		_hold_active = true
		_hold_player = player
		_hold_time = 0.0
		return
	if door_type == "auto_slide" and not powered:
		_hold_active = true
		_hold_player = player
		_hold_time = 0.0
		return
	if door_type == "heavy_slide":
		if is_open:
			set_open(false)
			return
		if _coop_stage == 0:
			_coop_stage = 1
			_coop_window = 6.0
			_coop_player = player
			_hold_active = true
			_hold_player = player
			_hold_time = 0.0
			_play(_latch, -12.0)
			_refresh_status()
			return
		if player != _coop_player:
			_coop_stage = 0
			_coop_player = null
			_hold_active = false
			_open_heavy()
			return
		return
	if door_type == "double_swing_seq":
		if is_open:
			set_open(false)
			_seq_stage = 0
			return
		if _seq_stage == 0:
			_seq_stage = 1
			_seq_window = 7.0
			_animate_leaf_a(true)
			_play(_latch)
			_refresh_status()
			return
		_animate_leaf_b(true)
		is_open = true
		_seq_stage = 0
		_refresh_status()
		return
	set_open(not is_open)


func _unhandled_input(event: InputEvent) -> void:
	if not _keypad_active:
		return
	if not (event is InputEventKey) or not event.pressed or event.echo:
		return
	var key := event as InputEventKey
	var code := key.keycode
	if code >= KEY_0 and code <= KEY_9:
		_enter_digit(str(code - KEY_0))
	elif code >= KEY_KP_0 and code <= KEY_KP_9:
		_enter_digit(str(code - KEY_KP_0))
	elif code == KEY_BACKSPACE:
		if _entered.length() > 0:
			_entered = _entered.substr(0, _entered.length() - 1)
	elif code == KEY_ENTER or code == KEY_KP_ENTER:
		_submit_code()
	elif code == KEY_ESCAPE:
		_keypad_active = false
		_entered = ""
		_refresh_status()
	else:
		return
	get_viewport().set_input_as_handled()


func _enter_digit(d: String) -> void:
	if _entered.length() >= 8:
		return
	_entered += d
	_play(_key, -15.0, 1.05)


func _submit_code() -> void:
	if _entered == access_code:
		_keypad_active = false
		_unlocked = true
		_entered = ""
		_play(_latch)
		_refresh_status()
		set_open(true)
	else:
		_entered = ""
		_denied_flash = 0.8
		_play(_alarm, -18.0)
		_refresh_status()


func _deny() -> void:
	_denied_flash = 0.55
	_play(_alarm, -20.0)
	_refresh_status()


# ------------------------------------------------------------------ estado / animacion

func set_open(value: bool, instant: bool = false) -> void:
	if _leaf_a == null:
		return
	var changed := value != is_open
	is_open = value
	_seq_stage = 0
	_seq_window = 0.0
	_auto_close = 0.0
	if instant:
		_kill_tweens()
		_apply_pose(value)
		busy = false
		_refresh_status()
		if changed:
			_emit_door_noise()
		return
	if not changed:
		return
	busy = true
	_kill_tweens()
	var dur: float = SPEEDS.get(door_type, 0.62)
	if door_type == "heavy_slide":
		dur = 1.6
	var tw := create_tween()
	tw.set_parallel(true)
	if door_type in ["auto_slide", "heavy_slide"]:
		var shift := width * 0.5
		if _leaf_a != null:
			tw.tween_property(_leaf_a, "position:x", -shift if value else 0.0, dur).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
		if _leaf_b != null:
			tw.tween_property(_leaf_b, "position:x", width + shift if value else width, dur).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	elif door_type == "double_swing_seq":
		if _leaf_a != null:
			tw.tween_property(_leaf_a, "rotation:y", deg_to_rad(open_angle_deg) if value else 0.0, dur).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
		if _leaf_b != null:
			tw.tween_property(_leaf_b, "rotation:y", -deg_to_rad(open_angle_deg) if value else 0.0, dur).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	else:
		if _leaf_a != null:
			tw.tween_property(_leaf_a, "rotation:y", deg_to_rad(open_angle_deg) if value else 0.0, dur).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	tw.set_parallel(false)
	tw.tween_callback(func() -> void:
		busy = false
		_refresh_status()
	)
	_leaf_tweens.append(tw)
	_play(_motor if door_type in ["auto_slide", "heavy_slide"] else _latch)
	_refresh_status()
	_emit_door_noise()


func _animate_leaf_a(value: bool) -> void:
	if _leaf_a == null:
		return
	var dur: float = SPEEDS.get(door_type, 0.7)
	var tw := create_tween()
	tw.tween_property(_leaf_a, "rotation:y", deg_to_rad(open_angle_deg) if value else 0.0, dur).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	_leaf_tweens.append(tw)


func _animate_leaf_b(value: bool) -> void:
	if _leaf_b == null:
		return
	var dur: float = SPEEDS.get(door_type, 0.7)
	var tw := create_tween()
	tw.tween_property(_leaf_b, "rotation:y", -deg_to_rad(open_angle_deg) if value else 0.0, dur).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	_leaf_tweens.append(tw)


func _apply_pose(value: bool) -> void:
	var ang := deg_to_rad(open_angle_deg)
	if door_type in ["auto_slide", "heavy_slide"]:
		var shift := width * 0.5
		if _leaf_a != null:
			_leaf_a.position.x = -shift if value else 0.0
		if _leaf_b != null:
			_leaf_b.position.x = width + shift if value else width
	elif door_type == "double_swing_seq":
		if _leaf_a != null:
			_leaf_a.rotation.y = ang if value else 0.0
		if _leaf_b != null:
			_leaf_b.rotation.y = -ang if value else 0.0
	else:
		if _leaf_a != null:
			_leaf_a.rotation.y = ang if value else 0.0


func _kill_tweens() -> void:
	for tw in _leaf_tweens:
		if tw != null and tw.is_valid():
			tw.kill()
	_leaf_tweens.clear()
	if _tween != null and _tween.is_valid():
		_tween.kill()
	_tween = null


func _emit_door_noise() -> void:
	if game == null or not game.has_method("emit_noise"):
		return
	var radius := 7.0 if is_open else 5.0
	if door_type == "heavy_slide":
		radius = 16.0
	elif door_type == "auto_slide":
		radius = 8.0
	game.emit_noise(to_global(Vector3(width * 0.5, 0.0, 0.0)), radius, "door")


func _open_heavy() -> void:
	_play(_motor, -6.0, 0.42)
	set_open(true)
	_play(_alarm, -16.0, 0.62)
	var tw := create_tween()
	tw.tween_interval(0.4)
	_leaf_tweens.append(tw)


func _complete_hold() -> void:
	_hold_active = false
	if door_type == "maintenance_swing":
		_manual_released = true
		set_open(true)
		_play(_motor, -8.0, 0.55)
		if game != null and game.has_method("emit_noise"):
			game.emit_noise(to_global(Vector3(width * 0.5, 0.0, 0.0)), 11.0, "door")
	elif door_type == "heavy_slide":
		_coop_stage = 0
		_coop_player = null
		_open_heavy()
	elif door_type == "auto_slide":
		set_open(true)
	else:
		set_open(true)
	_refresh_status()


func _cancel_hold() -> void:
	_hold_active = false
	_hold_time = 0.0


# ------------------------------------------------------------------ proceso

func _process(delta: float) -> void:
	if _denied_flash > 0.0:
		_denied_flash = maxf(0.0, _denied_flash - delta)
		if _denied_flash == 0.0:
			_refresh_status()

	if _keypad_active:
		var p := _player_near()
		if p == null:
			_keypad_active = false
			_entered = ""
			_refresh_status()

	if _hold_active:
		if _hold_player == null or not is_instance_valid(_hold_player):
			_cancel_hold()
		elif global_position.distance_to(_hold_player.global_position) > 3.4:
			_cancel_hold()
		elif not Input.is_action_pressed("interact"):
			_cancel_hold()
		else:
			var needed := 1.4
			if door_type == "heavy_slide":
				needed = 4.0
			elif red_alert:
				needed = 2.2
			_hold_time += delta
			if _hold_time >= needed:
				_complete_hold()

	if _seq_stage == 1:
		_seq_window -= delta
		if _seq_window <= 0.0:
			_seq_stage = 0
			_animate_leaf_a(false)
			_refresh_status()

	if _coop_stage == 1:
		_coop_window -= delta
		if _coop_window <= 0.0:
			_coop_stage = 0
			_coop_player = null
			_cancel_hold()
			_refresh_status()

	if door_type == "auto_slide":
		_process_auto(delta)


func _process_auto(delta: float) -> void:
	if red_alert:
		return
	if not powered:
		if is_open and not busy:
			_auto_close -= delta
			if _auto_close <= -6.0:
				set_open(false)
		return
	var p := _player_near()
	var moving := true
	if p != null:
		var vel = p.get("velocity")
		moving = vel == null or (vel as Vector3).length() > 0.18
	var near := p != null and (is_open or moving)
	if near:
		_auto_close = 1.8
		if not is_open and not busy:
			set_open(true)
	else:
		_auto_close -= delta
		if is_open and not busy and _auto_close <= 0.0:
			set_open(false)


func _player_near() -> Node3D:
	var best: Node3D = null
	var best_d := 999.0
	for node in get_tree().get_nodes_in_group("fm_player"):
		var p := node as Node3D
		if p == null:
			continue
		var local := global_transform.affine_inverse() * p.global_position
		if local.x < -0.8 or local.x > width + 0.8:
			continue
		if absf(local.z) > 2.8:
			continue
		if local.y < -0.6 or local.y > height + 0.6:
			continue
		var d := absf(local.z) + absf(local.x - width * 0.5) * 0.15
		if d < best_d:
			best_d = d
			best = p
	return best


func debug_advance_hold(seconds: float) -> void:
	if not _hold_active:
		return
	_hold_time += seconds
	var needed := 1.4
	if door_type == "heavy_slide":
		needed = 4.0
	elif red_alert:
		needed = 2.2
	if _hold_time >= needed:
		_complete_hold()


func submit_code(code: String) -> bool:
	_entered = code
	var ok := code == access_code
	if ok:
		_keypad_active = false
		_unlocked = true
		_entered = ""
		_refresh_status()
		set_open(true)
	else:
		_entered = ""
		_denied_flash = 0.8
		_refresh_status()
	return ok


# ------------------------------------------------------------------ alerta / energia / red

func set_red_alert(active: bool) -> void:
	red_alert = active
	_alert_locked = active
	if active:
		_keypad_active = false
		_entered = ""
		_cancel_hold()
		if is_open:
			set_open(false)
		if _alarm != null:
			_play(_alarm, -8.0, 0.82)
	_refresh_status()


func set_powered(value: bool) -> void:
	powered = value
	if not powered:
		_cancel_hold()
	_refresh_status()


func get_network_state() -> Dictionary:
	return {
		"id": door_id,
		"type": door_type,
		"open": is_open,
		"locked": (lock_mode == "security" and not _unlocked) or (lock_mode == "maintenance" and not _manual_released),
		"alert": red_alert,
		"alert_locked": _alert_locked,
		"powered": powered,
		"manual_released": _manual_released,
	}


func apply_network_state(state: Dictionary) -> void:
	if state.has("powered"):
		set_powered(bool(state["powered"]))
	if state.has("alert"):
		set_red_alert(bool(state["alert"]))
	if lock_mode == "security":
		_unlocked = not bool(state.get("locked", not _unlocked))
	elif lock_mode == "maintenance":
		_manual_released = not bool(state.get("locked", not _manual_released))
	if state.has("manual_released"):
		_manual_released = bool(state["manual_released"])
	set_open(bool(state.get("open", is_open)), true)
	_refresh_status()


func _refresh_status() -> void:
	if _status_mesh == null or _status_mat == null:
		return
	var col := Color(0.10, 0.65, 0.55)
	var energy := 1.4
	if red_alert or _denied_flash > 0.0:
		col = Color(1.0, 0.08, 0.035)
		energy = 2.2
	elif door_type == "auto_slide" and not powered:
		col = Color(1.0, 0.40, 0.05)
		energy = 1.6
	elif door_type == "armored_swing" and lock_mode == "security" and not _unlocked:
		col = Color(0.95, 0.22, 0.04)
		energy = 1.6
	elif door_type == "maintenance_swing" and not _manual_released:
		col = Color(1.0, 0.36, 0.04)
		energy = 1.5
	elif _coop_stage == 1 or _seq_stage == 1:
		col = Color(1.0, 0.52, 0.06)
		energy = 1.6
	elif is_open:
		col = Color(0.10, 0.85, 0.55)
		energy = 1.8
	_status_mat.albedo_color = Color(col.r * 0.25, col.g * 0.25, col.b * 0.25, 1.0)
	_status_mat.emission_enabled = true
	_status_mat.emission = col
	_status_mat.emission_energy_multiplier = energy


func _play(player: AudioStreamPlayer3D, db: float = -999.0, pitch: float = -1.0) -> void:
	if player == null or player.stream == null:
		return
	if db > -900.0:
		player.volume_db = db
	if pitch > 0.0:
		player.pitch_scale = pitch
	player.play()
