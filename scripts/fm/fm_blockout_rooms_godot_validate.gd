extends SceneTree

## FRECUENCIA MUERTA - validates the nine blockout room GLBs in Godot 4.7.
##
## For each room it loads the GLB, checks identity/mesh set against the
## Blender report, rejects lights, cameras and forbidden nodes, verifies the
## room AABB in Godot coordinates and checks that every floor piece has its
## top at Y = 0.
##
## Run:
##   godot --headless --path . --script \
##       scripts/fm/fm_blockout_rooms_godot_validate.gd

const TOL := 0.02
const FORBIDDEN := [
	"ANNOT_", "LIGHT_", "CAM_", "STUDIO", "LIB_", "RETIRED",
	"LOD1", "LOD2", "P0_TEST", "PLAYER", "VAL_", "FM_LIBRARY",
]

const ROOMS := [
	{
		"id": "control",
		"glb": "res://assets/models/fm/blockout_control.glb",
		"root": "FM_L1_BLOCKOUT_CONTROL",
		"report": "res://docs/fm_blockout_control_export.json",
	},
	{
		"id": "lockers",
		"glb": "res://assets/models/fm/blockout_lockers.glb",
		"root": "FM_L1_BLOCKOUT_LOCKERS",
		"report": "res://docs/fm_blockout_lockers_export.json",
	},
	{
		"id": "warehouse",
		"glb": "res://assets/models/fm/blockout_warehouse.glb",
		"root": "FM_L1_BLOCKOUT_WAREHOUSE",
		"report": "res://docs/fm_blockout_warehouse_export.json",
	},
	{
		"id": "maintenance",
		"glb": "res://assets/models/fm/blockout_maintenance.glb",
		"root": "FM_L1_BLOCKOUT_MAINTENANCE",
		"report": "res://docs/fm_blockout_maintenance_export.json",
	},
	{
		"id": "offices",
		"glb": "res://assets/models/fm/blockout_offices.glb",
		"root": "FM_L1_BLOCKOUT_OFFICES",
		"report": "res://docs/fm_blockout_offices_export.json",
	},
	{
		"id": "restroom",
		"glb": "res://assets/models/fm/blockout_restroom.glb",
		"root": "FM_L1_BLOCKOUT_RESTROOM",
		"report": "res://docs/fm_blockout_restroom_export.json",
	},
	{
		"id": "stairs_main",
		"glb": "res://assets/models/fm/blockout_stairs_main.glb",
		"root": "FM_L1_BLOCKOUT_STAIRS_MAIN",
		"report": "res://docs/fm_blockout_stairs_main_export.json",
	},
	{
		"id": "stairs_e1",
		"glb": "res://assets/models/fm/blockout_stairs_e1.glb",
		"root": "FM_L1_BLOCKOUT_STAIRS_E1",
		"report": "res://docs/fm_blockout_stairs_e1_export.json",
	},
	{
		"id": "stairs_e2",
		"glb": "res://assets/models/fm/blockout_stairs_e2.glb",
		"root": "FM_L1_BLOCKOUT_STAIRS_E2",
		"report": "res://docs/fm_blockout_stairs_e2_export.json",
	},
]

var failures := 0
var checks := 0


func _init() -> void:
	_run.call_deferred()


func check(condition: bool, label: String) -> void:
	checks += 1
	if not condition:
		failures += 1
		push_error("BLOCKOUT_FAIL: " + label)
		print("FAIL: ", label)


func _run() -> void:
	for room in ROOMS:
		await _validate_room(room)
	print("BLOCKOUT_ROOMS_GODOT checks=%d failures=%d" % [checks, failures])
	print("BLOCKOUT_ROOMS_GODOT_%s" % ("OK" if failures == 0 else "FAIL"))
	quit(0 if failures == 0 else 1)


func _validate_room(room: Dictionary) -> void:
	var rid: String = room["id"]
	print("--- ", rid)
	var packed: PackedScene = load(room["glb"])
	if packed == null:
		check(false, "%s: cannot load %s" % [rid, room["glb"]])
		return
	var instance := packed.instantiate()
	root.add_child(instance)
	await process_frame

	var report_text := FileAccess.get_file_as_string(room["report"])
	var report: Variant = JSON.parse_string(report_text)
	if typeof(report) != TYPE_DICTIONARY:
		check(false, "%s: missing/invalid report %s" % [rid, room["report"]])
		instance.queue_free()
		return

	var meshes: Array[MeshInstance3D] = []
	for n in instance.find_children("*", "MeshInstance3D", true, false):
		meshes.append(n as MeshInstance3D)

	var names: Array[String] = []
	var strays: Array[String] = []
	for mi in meshes:
		names.append(String(mi.name))
		for token in FORBIDDEN:
			if String(mi.name).to_upper().contains(token.to_upper()):
				strays.append(String(mi.name))
				break
	names.sort()
	var expected: Array = report["names"].duplicate()
	expected.sort()

	check(int(report["objects"]) == meshes.size(),
		"%s: meshes=%d expected=%d" % [rid, meshes.size(), int(report["objects"])])
	check(names == expected, "%s: mesh name set differs from Blender report" % rid)
	check(strays.is_empty(), "%s: forbidden node names %s" % [rid, str(strays)])
	check(instance.find_child(String(room["root"]), true, false) != null,
		"%s: missing root %s" % [rid, room["root"]])

	var lights := instance.find_children("*", "Light3D", true, false)
	var cameras := instance.find_children("*", "Camera3D", true, false)
	check(lights.is_empty(), "%s: lights=%d" % [rid, lights.size()])
	check(cameras.is_empty(), "%s: cameras=%d" % [rid, cameras.size()])

	var box := AABB()
	var first := true
	for mi in meshes:
		check(mi.mesh != null, "%s: %s has no mesh" % [rid, mi.name])
		if mi.mesh == null:
			continue
		var b: AABB = mi.global_transform * mi.mesh.get_aabb()
		check(b.position.is_finite() and b.size.is_finite(),
			"%s: non-finite AABB on %s" % [rid, mi.name])
		if first:
			box = b
			first = false
		else:
			box = box.merge(b)
		if String(mi.name).contains("Floor"):
			check(absf(b.end.y) <= TOL,
				"%s: floor top Y=%f on %s" % [rid, b.end.y, mi.name])

	var expected_pos: Array = report["aabb_godot_position"]
	var expected_size: Array = report["aabb_godot_size"]
	var want_pos := Vector3(expected_pos[0], expected_pos[1], expected_pos[2])
	var want_size := Vector3(expected_size[0], expected_size[1], expected_size[2])
	check(box.position.distance_to(want_pos) <= TOL,
		"%s: aabb pos %s expected %s" % [rid, box.position, want_pos])
	check(box.size.distance_to(want_size) <= TOL,
		"%s: aabb size %s expected %s" % [rid, box.size, want_size])
	check(box.get_volume() > 0.0, "%s: empty AABB" % rid)

	print("    %s meshes=%d aabb_pos=%s size=%s root_ok=true"
		% [rid, meshes.size(),
		str(box.position.snapped(Vector3.ONE * 0.001)),
		str(box.size.snapped(Vector3.ONE * 0.001))])

	instance.queue_free()
	await process_frame
