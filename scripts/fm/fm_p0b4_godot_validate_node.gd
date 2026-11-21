extends Node3D

## Validación headless del GLB P0b.4 (servicios principales de Z10).
## Comprueba importación, 25 mallas, 18 mallas únicas, nombres y AABB.

const GLB := "res://assets/models/fm/p0b4_z10_services.glb"

const EXPECTED := [
	"P0B4_CONDUIT_CLAMP_01",
	"P0B4_CONDUIT_CLAMP_02",
	"P0B4_CONDUIT_E_DOOR",
	"P0B4_FIREDAMPER_LINK",
	"P0B4_GRILLE_01",
	"P0B4_GRILLE_02",
	"P0B4_GRILLE_03",
	"P0B4_GRILLE_04",
	"P0B4_HVAC_LINK_RUN",
	"P0B4_HVAC_RUN_800x600",
	"P0B4_RISER_PASS_PLATES",
	"P0B4_SLEEVE_HVAC_E",
	"P0B4_SLEEVE_HVAC_W",
	"P0B4_SLEEVE_LINK_E",
	"P0B4_SLEEVE_SPR_E",
	"P0B4_SLEEVE_SPR_W",
	"P0B4_SPRINKLER_HEADS",
	"P0B4_SPRINKLER_RUN_DN80",
	"P0B4_SUPPORTS_HVAC",
	"P0B4_SUPPORTS_LINK",
	"P0B4_SUPPORTS_SPRINKLER",
	"P0B4_SUPPORT_EXTENSIONS",
	"P0B4_TRAY_EAST",
	"P0B4_TRAY_SLEEVES",
	"P0B4_TRAY_WEST",
]


func _aabb_of(root: Node3D) -> AABB:
	var box := AABB()
	var first := true
	var nodes := []
	if root is MeshInstance3D and root.mesh != null:
		nodes.append(root)
	nodes.append_array(root.find_children("*", "MeshInstance3D", true, false))
	for node in nodes:
		var mi := node as MeshInstance3D
		if mi == null or mi.mesh == null:
			continue
		var b: AABB = mi.global_transform * mi.get_aabb()
		if first:
			box = b
			first = false
		else:
			box = box.merge(b)
	return box


func _ready() -> void:
	var ok := true
	print("P0B4_GODOT_VALIDATE_BEGIN")

	var res := load(GLB)
	if res == null:
		print("FAIL load %s" % GLB)
		get_tree().quit(1)
		return
	var scene: Node3D = res.instantiate()
	add_child(scene)
	await get_tree().process_frame

	var meshes := []
	for node in scene.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi != null and mi.mesh != null:
			meshes.append(mi)
	var unique := {}
	for mi in meshes:
		unique[mi.mesh.get_instance_id()] = true
	var box := _aabb_of(scene)

	print("P0B4 meshes=%d unique=%d" % [meshes.size(), unique.size()])
	print("P0B4 aabb_pos=%s aabb_size=%s" % [str(box.position), str(box.size)])

	if meshes.size() != 25:
		print("FAIL expected 25 mesh instances, got %d" % meshes.size())
		ok = false
	if unique.size() != 18:
		print("FAIL expected 18 unique meshes, got %d" % unique.size())
		ok = false

	for n in EXPECTED:
		if scene.find_child(n, true, false) == null:
			print("FAIL missing node %s" % n)
			ok = false

	for mi in meshes:
		var nm := String(mi.name)
		if nm.to_upper().contains("STUDIO") or nm.begins_with("PROP_"):
			print("FAIL stray node %s" % nm)
			ok = false

	# Godot Y-up. Con bandejas: x ~30.16 (39.99..70.154),
	# y 4.19, z ~30.26 (-34.93..-4.67).
	if absf(box.size.x - 30.164) > 0.20:
		print("FAIL aabb x %.4f (expected ~30.164)" % box.size.x)
		ok = false
	if absf(box.size.y - 4.19) > 0.05:
		print("FAIL aabb y %.4f (expected 4.19)" % box.size.y)
		ok = false
	if absf(box.size.z - 30.26) > 0.20:
		print("FAIL aabb z %.4f (expected ~30.26)" % box.size.z)
		ok = false
	if box.position.z > -34.75:
		print("FAIL aabb min z %.4f (expected <= -34.75)" % box.position.z)
		ok = false

	var hvac := scene.find_child("P0B4_HVAC_RUN_800x600", true, false) as MeshInstance3D
	if hvac == null:
		print("FAIL missing HVAC run")
		ok = false
	else:
		var hb := _aabb_of(hvac)
		print("HVAC_RUN aabb_pos=%s aabb_size=%s" % [str(hb.position), str(hb.size)])
		if absf(hb.size.x - 21.628) > 0.05:
			print("FAIL HVAC run length %.4f (expected 21.628)" % hb.size.x)
			ok = false

	var grilles := 0
	for mi in meshes:
		if String(mi.name).begins_with("P0B4_GRILLE_"):
			grilles += 1
	if grilles != 4:
		print("FAIL expected 4 grilles, got %d" % grilles)
		ok = false

	if ok:
		print("P0B4_GODOT_OK")
		get_tree().quit(0)
	else:
		print("P0B4_GODOT_FAIL")
		get_tree().quit(1)
