class_name FMHorrorAudio
extends Node3D

## Capa de audio de terror de FRECUENCIA MUERTA — Nivel 1 V06.
##
## No sustituye al autoload `Audio` ni a los SFX del vertical slice: añade dos
## lechos ambientales no posicionales (zumbido industrial existente + drone
## grave) y eventos esporádicos posicionales 3D (golpe metálico, pasos lejanos,
## susurro/estática, interferencia de radio, goteo y crujido).
##
## Diseño:
##   - Los lechos suenan muy bajos para que el silencio siga existiendo.
##   - Los eventos aparecen cada 13–26 s, nunca encadenados, y se eligen cerca
##     del jugador (6–26 m) para que el audio 3D tenga dirección creíble.
##   - No hay música, tambores heroicos ni melodías: solo textura y presencia.
##   - Los WAV son síntesis propia del proyecto (ver assets/audio/fm/LICENSE.txt).

const AMBIENCE: AudioStream = preload("res://assets/audio/ambience/ambience.wav")
const DRONE: AudioStream = preload("res://assets/audio/fm/amb_drone_loop.wav")
const EVENT_METAL: AudioStream = preload("res://assets/audio/fm/event_metal_hit.wav")
const EVENT_STEPS: AudioStream = preload("res://assets/audio/fm/event_distant_steps.wav")
const EVENT_WHISPER: AudioStream = preload("res://assets/audio/fm/event_whisper_static.wav")
const EVENT_RADIO: AudioStream = preload("res://assets/audio/fm/event_radio_interference.wav")
const EVENT_DRIP: AudioStream = preload("res://assets/audio/fm/event_drip.wav")
const EVENT_CREAK: AudioStream = preload("res://assets/audio/fm/event_creak.wav")

## Volumen de los lechos. El zumbido industrial ya existe en el proyecto; el
## drone es la capa nueva de terror. Ambos quedan por debajo de los SFX.
const AMBIENCE_DB := -19.0
const DRONE_DB := -25.0

## Un evento cada 13–26 s. El primero tarda un poco más: el nivel necesita
## unos segundos de silencio antes de empezar a "respirar".
const FIRST_EVENT_MIN_S := 9.0
const FIRST_EVENT_MAX_S := 17.0
const EVENT_GAP_MIN_S := 13.0
const EVENT_GAP_MAX_S := 26.0
const EVENT_MIN_DISTANCE := 6.0
const EVENT_MAX_DISTANCE := 26.0
const VOICE_COUNT := 4

const EVENTS: Array[Dictionary] = [
	{"stream": EVENT_METAL, "db": -13.0, "label": "metal"},
	{"stream": EVENT_STEPS, "db": -16.0, "label": "pasos"},
	{"stream": EVENT_WHISPER, "db": -18.0, "label": "susurro"},
	{"stream": EVENT_RADIO, "db": -16.0, "label": "radio"},
	{"stream": EVENT_DRIP, "db": -20.0, "label": "goteo"},
	{"stream": EVENT_CREAK, "db": -17.0, "label": "crujido"},
]

## Anclas dentro de los volúmenes jugables de los cinco sectores. No son
## puntos de spawn de criaturas: solo posiciones donde un sonido diegético
## tiene sentido (pasillos, salas técnicas, esquinas y zonas de paso).
const EVENT_ANCHORS: Array[Vector3] = [
	Vector3(46.5, 1.2, -30.0), Vector3(60.0, 1.2, -28.0),
	Vector3(66.0, 1.2, -10.0), Vector3(44.0, 1.2, -6.0),
	Vector3(-101.0, 1.2, 10.0), Vector3(-84.0, 1.2, 29.0),
	Vector3(-104.0, 1.2, 34.0), Vector3(-94.0, 1.2, 20.0),
	Vector3(-99.0, 1.2, -31.0), Vector3(-77.0, 1.2, -27.0),
	Vector3(-90.0, 1.2, -12.0),
	Vector3(-90.0, 1.2, 1.5), Vector3(-50.0, 1.2, -1.5),
	Vector3(-12.0, 1.2, 1.5), Vector3(31.0, 1.2, -1.5),
	Vector3(61.0, 1.2, 1.5),
	Vector3(-60.0, 1.2, -10.7), Vector3(-43.0, 1.2, -10.7),
]

var _beds: Array[AudioStreamPlayer] = []
var _voices: Array[AudioStreamPlayer3D] = []
var _timer: Timer
var _player: Node3D
var _rng := RandomNumberGenerator.new()
var _last_event_index := -1
var _events_played := 0
var _last_event_label := ""
var _active := false


func setup(player: Node3D) -> void:
	if player == null or not is_instance_valid(player):
		push_error("FMHorrorAudio: falta el jugador para posicionar los eventos")
		return
	_player = player
	_rng.randomize()
	_build_beds()
	_build_voices()
	_timer = Timer.new()
	_timer.name = "EventTimer"
	_timer.one_shot = true
	_timer.timeout.connect(_on_event_timer_timeout)
	add_child(_timer)
	_active = true
	_timer.start(_rng.randf_range(FIRST_EVENT_MIN_S, FIRST_EVENT_MAX_S))
	print("FMH_AUDIO_READY beds=%d voices=%d events=%d ambience_db=%.1f drone_db=%.1f first=%.1f..%.1f gap=%.1f..%.1f anchors=%d" % [
		_beds.size(), _voices.size(), EVENTS.size(), AMBIENCE_DB, DRONE_DB,
		FIRST_EVENT_MIN_S, FIRST_EVENT_MAX_S, EVENT_GAP_MIN_S, EVENT_GAP_MAX_S,
		EVENT_ANCHORS.size(),
	])


func _build_beds() -> void:
	_add_bed("IndustrialBed", AMBIENCE, AMBIENCE_DB)
	_add_bed("TerrorDrone", DRONE, DRONE_DB)


func _add_bed(bed_name: String, stream: AudioStream, volume_db: float) -> void:
	var player := AudioStreamPlayer.new()
	player.name = bed_name
	player.stream = _looped(stream)
	player.volume_db = volume_db
	add_child(player)
	player.play()
	_beds.append(player)


func _build_voices() -> void:
	for index in VOICE_COUNT:
		var voice := AudioStreamPlayer3D.new()
		voice.name = "EventVoice%d" % index
		voice.unit_size = 8.0
		voice.max_distance = 45.0
		voice.attenuation_model = AudioStreamPlayer3D.ATTENUATION_INVERSE_DISTANCE
		voice.panning_strength = 1.0
		voice.volume_db = -80.0
		add_child(voice)
		_voices.append(voice)


func _on_event_timer_timeout() -> void:
	if not _active:
		return
	_fire_event()
	_timer.start(_rng.randf_range(EVENT_GAP_MIN_S, EVENT_GAP_MAX_S))


func _fire_event() -> void:
	if _player == null or not is_instance_valid(_player):
		return
	var voice := _free_voice()
	if voice == null:
		return
	var index := _rng.randi_range(0, EVENTS.size() - 1)
	if index == _last_event_index and EVENTS.size() > 1:
		index = (index + 1) % EVENTS.size()
	_last_event_index = index
	var event: Dictionary = EVENTS[index]
	voice.stream = event["stream"] as AudioStream
	voice.global_position = _pick_anchor()
	voice.volume_db = float(event["db"]) + _rng.randf_range(-1.5, 1.5)
	voice.pitch_scale = _rng.randf_range(0.94, 1.06)
	voice.play()
	_events_played += 1
	_last_event_label = String(event["label"])


func _free_voice() -> AudioStreamPlayer3D:
	for voice in _voices:
		if voice != null and is_instance_valid(voice) and not voice.playing:
			return voice
	return null


func _pick_anchor() -> Vector3:
	var origin := _player.global_position
	var candidates: Array[Vector3] = []
	var nearest := EVENT_ANCHORS[0]
	var nearest_distance := INF
	for anchor in EVENT_ANCHORS:
		var distance := origin.distance_to(anchor)
		if distance < nearest_distance:
			nearest = anchor
			nearest_distance = distance
		if distance >= EVENT_MIN_DISTANCE and distance <= EVENT_MAX_DISTANCE:
			candidates.append(anchor)
	if candidates.is_empty():
		return nearest
	return candidates[_rng.randi_range(0, candidates.size() - 1)]


func stop_all() -> void:
	_active = false
	if _timer != null and is_instance_valid(_timer):
		_timer.stop()
	for bed in _beds:
		if bed != null and is_instance_valid(bed):
			bed.stop()
	for voice in _voices:
		if voice != null and is_instance_valid(voice):
			voice.stop()


func _looped(source: AudioStream) -> AudioStream:
	var wav := source as AudioStreamWAV
	if wav == null:
		return source
	var copy := wav.duplicate() as AudioStreamWAV
	copy.loop_mode = AudioStreamWAV.LOOP_FORWARD
	copy.loop_begin = 0
	copy.loop_end = int(copy.get_length() * copy.mix_rate) - 1
	return copy


# ---------------------------------------------------------------------------
# Consultas de diagnóstico (no las consume el gameplay)
# ---------------------------------------------------------------------------

func get_bed_count() -> int:
	return _beds.size()


func get_voice_count() -> int:
	return _voices.size()


func get_events_played() -> int:
	return _events_played


func get_last_event_label() -> String:
	return _last_event_label


func is_active() -> bool:
	return _active
