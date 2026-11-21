@tool
extends EditorScenePostImport

## Z10 post-import: enable vertex-color-as-albedo for the edge-wear red material.
## The GLB carries COLOR_0 (WearEdge) but Godot defaults the material flag to false.

func _post_import(scene: Node) -> Node:
	_apply(scene)
	return scene

func _apply(node: Node) -> void:
	if node is MeshInstance3D and node.mesh != null:
		var mi := node as MeshInstance3D
		for i in range(mi.mesh.get_surface_count()):
			var mat: Material = mi.get_surface_override_material(i)
			if mat == null:
				mat = mi.mesh.surface_get_material(i)
			if mat is BaseMaterial3D and mat.resource_name == "M_Z10_HERO_Sprinkler_Red_WEAR_2K":
				(mat as BaseMaterial3D).vertex_color_use_as_albedo = true
	for child in node.get_children():
		_apply(child)
