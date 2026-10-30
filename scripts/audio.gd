extends Node

const MUSIC_DB := -17.0
const MUSIC_FADE := 0.9
const SFX_VOICES := 16

const MUSIC := {
	"menu": preload("res://assets/audio/music/menu.wav"),
	"heist": preload("res://assets/audio/music/heist.wav"),
}

const SFX := {
	"gem": preload("res://assets/audio/sfx/gem.wav"),
	"grab": preload("res://assets/audio/sfx/grab.wav"),
	"drop": preload("res://assets/audio/sfx/drop.wav"),
	"deliver": preload("res://assets/audio/sfx/deliver.wav"),
	"win": preload("res://assets/audio/sfx/win.wav"),
	"lose": preload("res://assets/audio/sfx/lose.wav"),
	"click": preload("res://assets/audio/sfx/click.wav"),
	"step": preload("res://assets/audio/sfx/step.wav"),
	"tick": preload("res://assets/audio/sfx/tick.wav"),
	"camera": preload("res://assets/audio/sfx/camera.wav"),
}

const ALARM_STREAM: AudioStream = preload("res://assets/audio/sfx/alarm.wav")

var _sfx_players: Array[AudioStreamPlayer] = []
var _sfx_index := 0
var _music_players: Array[AudioStreamPlayer] = []
var _music_slot := 0
var _current_music := ""
var _alarm_player: AudioStreamPlayer
var _alarm_target_db := -60.0
var _toast: Label
var _toast_tween: Tween

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS

	for i in SFX_VOICES:
		var player := AudioStreamPlayer.new()
		add_child(player)
		_sfx_players.append(player)

	for i in 2:
		var music := AudioStreamPlayer.new()
		music.volume_db = -40.0
		add_child(music)
		_music_players.append(music)

	_alarm_player = AudioStreamPlayer.new()
	_alarm_player.volume_db = -60.0
	_alarm_player.stream = _looped(ALARM_STREAM)
	add_child(_alarm_player)

	_make_toast()

func _make_toast() -> void:
	var layer := CanvasLayer.new()
	layer.layer = 100
	add_child(layer)
	_toast = Label.new()
	_toast.add_theme_font_size_override("font_size", 18)
	_toast.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.85))
	_toast.add_theme_constant_override("outline_size", 4)
	_toast.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_toast.position = Vector2(960, 676)
	_toast.size = Vector2(300, 24)
	_toast.modulate.a = 0.0
	layer.add_child(_toast)

func _flash_toast(text: String) -> void:
	if _toast == null:
		return
	_toast.text = text
	if _toast_tween != null and _toast_tween.is_valid():
		_toast_tween.kill()
	_toast.modulate.a = 1.0
	_toast_tween = create_tween()
	_toast_tween.tween_interval(0.8)
	_toast_tween.tween_property(_toast, "modulate:a", 0.0, 0.4)

func play_sfx(sound: String, volume_db := -8.0, pitch := 1.0) -> void:
	if not SFX.has(sound) or _sfx_players.is_empty():
		return
	var player := _sfx_players[_sfx_index]
	_sfx_index = (_sfx_index + 1) % _sfx_players.size()
	player.stream = SFX[sound]
	player.volume_db = volume_db
	player.pitch_scale = pitch
	player.play()

func play_music(track: String) -> void:
	if not MUSIC.has(track):
		return
	if _current_music == track and _music_players[_music_slot].playing:
		return

	var old := _music_players[_music_slot]
	_music_slot = 1 - _music_slot
	var current := _music_players[_music_slot]
	current.stream = _looped(MUSIC[track])
	current.volume_db = -38.0
	current.play()
	_current_music = track

	var tween := create_tween()
	tween.set_parallel(true)
	tween.tween_property(current, "volume_db", MUSIC_DB, MUSIC_FADE)
	if old.playing:
		tween.tween_property(old, "volume_db", -38.0, 0.45)
		tween.chain().tween_callback(func(): old.stop())

func stop_music() -> void:
	_current_music = ""
	var current := _music_players[_music_slot]
	if not current.playing:
		return
	var tween := create_tween()
	tween.tween_property(current, "volume_db", -38.0, 0.8)
	tween.tween_callback(func(): current.stop())

func set_alarm(level: float, active: bool) -> void:
	if not active or level <= 0.5:
		_alarm_target_db = -60.0
		return
	if not _alarm_player.playing:
		_alarm_player.volume_db = -50.0
		_alarm_player.play()
	var amount := clampf(level / 100.0, 0.0, 1.0)
	_alarm_target_db = lerpf(-30.0, -9.0, amount)
	_alarm_player.pitch_scale = lerpf(0.9, 1.2, amount)

func _process(delta: float) -> void:
	if not _alarm_player.playing:
		return
	_alarm_player.volume_db = move_toward(_alarm_player.volume_db, _alarm_target_db, 30.0 * delta)
	if _alarm_player.volume_db <= -59.5 and _alarm_target_db <= -59.5:
		_alarm_player.stop()

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.physical_keycode == KEY_M:
		var muted := not AudioServer.is_bus_mute(0)
		AudioServer.set_bus_mute(0, muted)
		_flash_toast("SILENCIO" if muted else "AUDIO ACTIVADO")

func _looped(stream: AudioStream) -> AudioStream:
	if stream is AudioStreamWAV:
		var wav := stream as AudioStreamWAV
		wav.loop_mode = AudioStreamWAV.LOOP_FORWARD
		wav.loop_begin = 0
		wav.loop_end = int(wav.get_length() * wav.mix_rate)
	return stream
