bl_info = {
    "name": "View Layer Plus",
    "description": "Seamlessly extend View Layers management",
    "author": "Lukas Sabaliauskas <lukas_sabaliauskas@hotmail.com>",
    "version": (1, 1, 5),
    "blender": (4, 0, 0),
    "doc_url": "https://extensions.blender.org/add-ons/use-for-rendering-plus/",
    "tracker_url": "https://github.com/Trukasss/ViewLayerPlus",
}


is_reloading = "bpy" in locals()

import bpy
from bpy.props import PointerProperty
from . import icons
from . import props
from . import op
from . import ui

if is_reloading:
    import importlib
    importlib.reload(icons)
    importlib.reload(props)
    importlib.reload(op)
    importlib.reload(ui)


def register():
    icons.register()
    bpy.utils.register_class(props.UFRP_property_select)
    bpy.utils.register_class(props.UFRP_property_passe)
    bpy.utils.register_class(props.UFRP_properties)
    bpy.utils.register_class(op.UFRP_OP_toggle)
    bpy.utils.register_class(op.UFRP_OP_batch)
    bpy.utils.register_class(op.UFRP_OP_OnlyUnmuted)
    bpy.utils.register_class(op.UFRP_OP_OnlySelected)
    bpy.utils.register_class(op.UFRP_OP_RenderLayerSwitch)
    bpy.utils.register_class(op.UFRP_OP_ViewLayerAdd)
    bpy.utils.register_class(op.UFRP_OP_ViewLayerRemove)
    bpy.utils.register_class(op.UFRP_OP_ViewLayerSwitch)
    bpy.utils.register_class(op.UFRP_OP_AllCopyProps)
    bpy.utils.register_class(op.UFRP_OP_ReloadPasses)
    bpy.utils.register_class(op.UFRP_OP_CopyLayer)
    bpy.utils.register_class(op.UFRP_OP_PasteLayer)
    bpy.utils.register_class(op.UFRP_OT_CopyToSelected)
    bpy.utils.register_class(op.UFRP_OP_MoveLayer)
    bpy.utils.register_class(op.UFRP_OP_SortLayers)
    bpy.utils.register_class(ui.UFRP_PT_layer_filter)
    bpy.utils.register_class(ui.UFRP_PT_passes_filter)
    bpy.utils.register_class(ui.UFRP_MT_menu)
    bpy.utils.register_class(ui.UFRP_UL_layers)
    bpy.utils.register_class(ui.UFRP_MT_manager_context_menu)
    bpy.utils.register_class(ui.UFRP_PT_manager_topbar)
    bpy.utils.register_class(ui.UFRP_PT_manager_properties)
    bpy.types.NODE_MT_editor_menus.append(ui.draw_comp_menu)
    bpy.types.NODE_MT_context_menu.append(ui.draw_context_menu)
    bpy.types.TOPBAR_HT_upper_bar.append(ui.draw_manager_topbar)
    bpy.types.OUTLINER_MT_collection.append(ui.draw_context_outliner)
    bpy.types.Scene.ufrp = PointerProperty(type=props.UFRP_properties)


def unregister():
    del bpy.types.Scene.ufrp
    bpy.types.OUTLINER_MT_collection.remove(ui.draw_context_outliner)
    bpy.types.TOPBAR_HT_upper_bar.remove(ui.draw_manager_topbar)
    bpy.types.NODE_MT_context_menu.remove(ui.draw_context_menu)
    bpy.types.NODE_MT_editor_menus.remove(ui.draw_comp_menu)
    bpy.utils.unregister_class(ui.UFRP_PT_manager_properties)
    bpy.utils.unregister_class(ui.UFRP_PT_manager_topbar)
    bpy.utils.unregister_class(ui.UFRP_MT_manager_context_menu)
    bpy.utils.unregister_class(ui.UFRP_UL_layers)
    bpy.utils.unregister_class(ui.UFRP_MT_menu)
    bpy.utils.unregister_class(ui.UFRP_PT_passes_filter)
    bpy.utils.unregister_class(ui.UFRP_PT_layer_filter)
    bpy.utils.unregister_class(op.UFRP_OP_SortLayers)
    bpy.utils.unregister_class(op.UFRP_OP_MoveLayer)
    bpy.utils.unregister_class(op.UFRP_OT_CopyToSelected)
    bpy.utils.unregister_class(op.UFRP_OP_PasteLayer)
    bpy.utils.unregister_class(op.UFRP_OP_CopyLayer)
    bpy.utils.unregister_class(op.UFRP_OP_ReloadPasses)
    bpy.utils.unregister_class(op.UFRP_OP_AllCopyProps)
    bpy.utils.unregister_class(op.UFRP_OP_ViewLayerSwitch)
    bpy.utils.unregister_class(op.UFRP_OP_ViewLayerRemove)
    bpy.utils.unregister_class(op.UFRP_OP_ViewLayerAdd)
    bpy.utils.unregister_class(op.UFRP_OP_RenderLayerSwitch)
    bpy.utils.unregister_class(op.UFRP_OP_OnlySelected)
    bpy.utils.unregister_class(op.UFRP_OP_OnlyUnmuted)
    bpy.utils.unregister_class(op.UFRP_OP_batch)
    bpy.utils.unregister_class(op.UFRP_OP_toggle)
    bpy.utils.unregister_class(props.UFRP_properties)
    bpy.utils.unregister_class(props.UFRP_property_passe)
    bpy.utils.unregister_class(props.UFRP_property_select)
    icons.unregister()