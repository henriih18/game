extends Node3D

## Validación headless del GLB P0b.1 (columna de servicios del corredor).
## Comprueba importación, mallas, AABB y ausencia de strays.

const GLB := "res://assets/models/fm/p0b_corridor_services.glb"

const EXPECTED := [
	"P0B_BLIND_E",
	"P0B_BLIND_W",
	"P0B_END_FLANGE_E",
	"P0B_END_FLANGE_W",
	"P0B_HVAC_BRANCH_Z10",
	"P0B_HVAC_RUN_800x600",
	"P0B_LABELS",
	"P0B_SLEEVE_CORR",
	"P0B_SLEEVE_Z10",
	"P0B_SPRINKLER_HEADS",
	"P0B_SPRINKLER_RUN_DN80",
	"P0B_SUPPORTS_HVAC",
	"P0B_SUPPORTS_SPRINKLER",
	"P0B_SUPPORTS_TRAY",
	"P0B_TEE_MAIN",
	"P0B_TEE_Z10",
	"P0B_TRAY_RUN_400",
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


func _mesh_instances(root: Node) -> Array:
	var out := []
	for node in root.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi != null and mi.mesh != null:
			out.append(mi)
	return out


func _ready() -> void:
	var ok := true
	print("P0B_GODOT_VALIDATE_BEGIN")

	var res := load(GLB)
	if res == null:
		print("FAIL load %s" % GLB)
		get_tree().quit(1)
		return
	var scene: Node3D = res.instantiate()
	add_child(scene)
	await get_tree().process_frame

	var meshes := _mesh_instances(scene)
	var box := _aabb_of(scene)
	var names := []
	var unique_meshes := {}
	for mi in meshes:
		names.append(mi.name)
		unique_meshes[mi.mesh.get_instance_id()] = true

	print("P0B meshes=%d unique=%d" % [meshes.size(), unique_meshes.size()])
	print("P0B aabb_pos=%s aabb_size=%s" % [str(box.position), str(box.size)])
	print("P0B names=%s" % str(names))

	if meshes.size() != 17:
		print("FAIL expected 17 mesh instances, got %d" % meshes.size())
		ok = false
	if unique_meshes.size() != 16:
		print("FAIL expected 16 unique meshes, got %d" % unique_meshes.size())
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

	# Godot importa el GLB con Y arriba: X=corredor, Y=alto, Z=-profundidad Blender.
	if absf(box.size.x - 172.906) > 0.05:
		print("FAIL aabb x %.3f (expected 172.906)" % box.size.x)
		ok = false
	if absf(box.size.y - 0.89) > 0.05:
		print("FAIL aabb y %.3f (expected 0.89)" % box.size.y)
		ok = false
	if absf(box.size.z - 22.11) > 0.05:
		print("FAIL aabb z %.3f (expected 22.11)" % box.size.z)
		ok = false
	if box.position.z > -19.5:
		print("FAIL aabb min z %.3f (expected <= -19.5, ramal Z10)" % box.position.z)
		ok = false

	var hvac := scene.find_child("P0B_HVAC_RUN_800x600", true, false) as MeshInstance3D
	if hvac == null:
		print("FAIL missing HVAC run")
		ok = false
	else:
		print("HVAC_RUN aabb_size=%s" % str(_aabb_of(hvac).size))

	if ok:
		print("P0B_GODOT_OK")
		get_tree().quit(0)
	else:
		print("P0B_GODOT_FAIL")
		get_tree().quit(1)
