extends Node3D

## FRECUENCIA MUERTA — Recepción art scene (R9).
## User direction: reception is the only area allowed a bit more light; Z10 and
## the rest stay emergency-only. This scene loads the geometry-only reception GLB
## and uses ONLY diegetic practical/emergency fixtures already present in the
## room. No key/fill/bounce or other non-diegetic lights are added.
##
## The GLB is not modified. Collision helper meshes ending in "-col" are hidden.

const CAM_POS := Vector3(-106.0, 1.7, 36.0)
const CAM_TARGET := Vector3(-99.54, 1.66, 28.37)
## ARCH_CAM_Reception is 24 mm on a 36 mm sensor -> 73.7 deg horizontal.
const CAM_FOV := 73.7

const EXPECTED_SCENE_LIGHTS := 12


func _ready() -> void:
	var camera := get_node_or_null("ArtCamera") as Camera3D
	if camera != null:
		camera.fov = CAM_FOV
		camera.look_at_from_position(CAM_POS, CAM_TARGET, Vector3.UP)
		camera.current = true

	var glb := get_node_or_null("ReceptionSector")
	if glb != null:
		_hide_collision_helpers(glb)
		var glb_lights := glb.find_children("*", "Light3D", true, false).size()
		print("RECEPTION_ART_R9_GLB_LIGHTS %d" % glb_lights)

	var scene_lights := find_children("*", "Light3D", true, false)
	var omni := 0
	var spot := 0
	var directional := 0
	for node in scene_lights:
		if node is OmniLight3D:
			omni += 1
		elif node is SpotLight3D:
			spot += 1
		elif node is DirectionalLight3D:
			directional += 1
	print("RECEPTION_ART_R9_LIGHTS total=%d expected=%d omni=%d spot=%d directional=%d" % [
		scene_lights.size(), EXPECTED_SCENE_LIGHTS, omni, spot, directional,
	])
	print("RECEPTION_ART_R9_READY cam=%s fov=%.1f" % [str(CAM_POS), CAM_FOV])


func _hide_collision_helpers(glb: Node) -> void:
	var hidden := 0
	for node in glb.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi != null and String(mi.name).ends_with("-col"):
			mi.visible = false
			hidden += 1
	print("RECEPTION_ART_R9_COLLISION_HELPERS_HIDDEN %d" % hidden)
