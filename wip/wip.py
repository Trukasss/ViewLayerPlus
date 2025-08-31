import bpy

print("==========================")
vl1 = bpy.context.scene.view_layers[0]
vl2 = bpy.context.scene.view_layers[1]
vl1: bpy.types.ViewLayer

rna_names = [rna.identifier for rna in vl1.bl_rna.properties if is_viewlayer_prop_supported(vl1, rna.identifier)]
UFRP_OP_PasteLayer.copy_attrs(vl1, vl2, rna_names)
