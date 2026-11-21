extends Node3D

## FRECUENCIA MUERTA — Z10 art parity scene (R7).
## Loads the final R6 GLB and configures the imported punctual lights for a
## Forward+ / AgX / volumetric-fog beauty frame. The GLB itself is not modified.
##
## The Blender beauty (docs/fm_z10_hero_beauty_r6.png) used Cycles area lights,
## GI and a volume that do not travel in glTF. This scene reproduces the intent
## with a controlled environment, scaled GLB lights and a small set of
## documented bounce/wash lights.

const CAM_POS := Vector3(46.0, 2.0, -18.0)
const CAM_TARGET := Vector3(55.47, 2.87, -21.08)
## 24 mm on a 36 mm sensor is 73.7 deg horizontal. 68 deg matches the R6
## beauty framing better after A/B; set 73.7 for strict 24 mm lens parity.
const CAM_FOV := 68.0

## Energy/range/color/shadow overrides for the lights embedded in the GLB.
## The raw glTF values are huge (range 4096, energy up to 14k) and overexpose
## the frame without an environment.
const GLB_LIGHTS := {
	"LIGHT_Z10_Point_01": {"energy": 1.2, "range": 8.5, "shadow": true, "color": Color(0.84, 0.88, 1.0)},
	"LIGHT_Z10_Point_02": {"energy": 1.2, "range": 8.5, "shadow": true, "color": Color(0.84, 0.88, 1.0)},
	"LIGHT_Z10_Point_03": {"energy": 1.2, "range": 8.5, "shadow": true, "color": Color(0.84, 0.88, 1.0)},
	"LIGHT_Z10_SouthSpill": {"energy": 0.8, "range": 7.0, "shadow": false, "color": Color(0.35, 0.55, 1.0)},
	"LIGHT_Z10_WorkFill": {"energy": 1.5, "range": 7.0, "shadow": false, "color": Color(1.0, 0.72, 0.42)},
	"LIGHT_Z10_WorkSpot": {"energy": 2.0, "range": 10.0, "angle": 45.0, "shadow": false, "color": Color(1.0, 0.78, 0.55)},
	"LIGHT_Z10_Emergency_E": {"energy": 1.6, "range": 5.5, "shadow": true, "color": Color(1.0, 0.02, 0.01)},
	"LIGHT_L1_Conector_E": {"energy": 0.1, "range": 4.5, "shadow": false, "color": Color(1.0, 0.05, 0.02)},
	"LIGHT_L1_Conector_N": {"energy": 0.1, "range": 4.5, "shadow": false, "color": Color(1.0, 0.05, 0.02)},
}


func _ready() -> void:
	var camera := get_node_or_null("ArtCamera") as Camera3D
	if camera != null:
		camera.fov = CAM_FOV
		camera.look_at_from_position(CAM_POS, CAM_TARGET, Vector3.UP)
		camera.current = true

	var glb := get_node_or_null("Z10Sector")
	if glb != null:
		_configure_glb_lights(glb)
		_verify_wear_material(glb)

	print("Z10_ART_R7_READY cam=%s fov=%.1f" % [str(CAM_POS), CAM_FOV])


func _configure_glb_lights(glb: Node) -> void:
	for node in glb.find_children("*", "Light3D", true, false):
		var light := node as Light3D
		var key := String(light.name)
		if not GLB_LIGHTS.has(key):
			continue
		var cfg: Dictionary = GLB_LIGHTS[key]
		light.light_energy = float(cfg["energy"])
		light.light_color = cfg["color"] as Color
		light.shadow_enabled = bool(cfg["shadow"])
		if light is OmniLight3D:
			(light as OmniLight3D).omni_range = float(cfg["range"])
		elif light is SpotLight3D:
			(light as SpotLight3D).spot_range = float(cfg["range"])
			if cfg.has("angle"):
				(light as SpotLight3D).spot_angle = float(cfg["angle"])


func _verify_wear_material(glb: Node) -> void:
	for node in glb.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi.mesh == null:
			continue
		for i in range(mi.mesh.get_surface_count()):
			var mat: Material = mi.get_surface_override_material(i)
			if mat == null:
				mat = mi.mesh.surface_get_material(i)
			if mat is BaseMaterial3D and mat.resource_name == "M_Z10_HERO_Sprinkler_Red_WEAR_2K":
				var vc := (mat as BaseMaterial3D).vertex_color_use_as_albedo
				print("Z10_ART_R7_WEAR vc=%s node=%s" % [str(vc), str(mi.name)])
				return
	print("Z10_ART_R7_WEAR vc=not_found")
