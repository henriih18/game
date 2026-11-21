extends Node3D

## FRECUENCIA MUERTA — Z10 dark art scene (R8).
## User direction: reception is the only space allowed a bit more light; Z10 and
## the rest must rely on sparse red emergency lights only. No non-diegetic key,
## fill, wash or bounce lights are added here.
##
## The GLB is not modified. Non-emergency punctual lights are hidden at runtime
## and the normal luminaire/work-lamp emissive materials are overridden only in
## this scene, so the room reads as a power-outage emergency-lit space.

const CAM_POS := Vector3(46.0, 2.0, -18.0)
const CAM_TARGET := Vector3(55.47, 2.87, -21.08)
## 24 mm on a 36 mm sensor is 73.7 deg horizontal. 68 deg matches the R6/R7
## framing; keep the same camera as R7 for a clean A/B.
const CAM_FOV := 68.0

## The only imported lights kept visible. These are the red emergency sources
## present in the fiction. Everything else (ceiling practicals, work lights,
## spill) is hidden.
const EMERGENCY_LIGHTS := {
	"LIGHT_Z10_Emergency_E": {"energy": 3.0, "range": 6.0, "shadow": true, "color": Color(1.0, 0.02, 0.01)},
	"LIGHT_L1_Conector_E": {"energy": 0.30, "range": 3.5, "shadow": false, "color": Color(1.0, 0.03, 0.01)},
	"LIGHT_L1_Conector_N": {"energy": 0.30, "range": 3.5, "shadow": false, "color": Color(1.0, 0.03, 0.01)},
}

## Normal fixtures that must not glow during the outage. Their materials are
## duplicated per surface so the shared GLB material is not modified.
const EMISSIVE_OFF_OBJECTS := ["LIGHT_Z10_Luminaire_01", "LIGHT_Z10_Luminaire_02", "LIGHT_Z10_Luminaire_03", "PROP_Z10_WorkLight"]


func _ready() -> void:
	var camera := get_node_or_null("ArtCamera") as Camera3D
	if camera != null:
		camera.fov = CAM_FOV
		camera.look_at_from_position(CAM_POS, CAM_TARGET, Vector3.UP)
		camera.current = true

	var glb := get_node_or_null("Z10Sector")
	if glb != null:
		_configure_emergency_lights(glb)
		_disable_normal_fixture_emission(glb)
		_verify_wear_material(glb)

	print("Z10_ART_R8_READY cam=%s fov=%.1f" % [str(CAM_POS), CAM_FOV])


func _configure_emergency_lights(glb: Node) -> void:
	var kept := 0
	var disabled := 0
	for node in glb.find_children("*", "Light3D", true, false):
		var light := node as Light3D
		var key := String(light.name)
		if not EMERGENCY_LIGHTS.has(key):
			light.visible = false
			disabled += 1
			continue
		var cfg: Dictionary = EMERGENCY_LIGHTS[key]
		light.visible = true
		light.light_energy = float(cfg["energy"])
		light.light_color = cfg["color"] as Color
		light.shadow_enabled = bool(cfg["shadow"])
		if light is OmniLight3D:
			(light as OmniLight3D).omni_range = float(cfg["range"])
		elif light is SpotLight3D:
			(light as SpotLight3D).spot_range = float(cfg["range"])
		kept += 1
	print("Z10_ART_R8_LIGHTS kept=%d disabled=%d" % [kept, disabled])


func _disable_normal_fixture_emission(glb: Node) -> void:
	var overrides := 0
	for node in glb.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi.mesh == null:
			continue
		var nm := String(mi.name)
		if not (EMISSIVE_OFF_OBJECTS.has(nm) or nm.begins_with("LIGHT_Z10_Luminaire_")):
			continue
		for i in range(mi.mesh.get_surface_count()):
			var mat: Material = mi.get_surface_override_material(i)
			if mat == null:
				mat = mi.mesh.surface_get_material(i)
			if mat is BaseMaterial3D:
				var dup := (mat as BaseMaterial3D).duplicate() as BaseMaterial3D
				dup.emission_enabled = false
				mi.set_surface_override_material(i, dup)
				overrides += 1
	print("Z10_ART_R8_EMISSION_OFF overrides=%d" % overrides)


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
				print("Z10_ART_R8_WEAR vc=%s node=%s" % [str(vc), str(mi.name)])
				return
	print("Z10_ART_R8_WEAR vc=not_found")
