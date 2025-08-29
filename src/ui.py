import bpy
from bpy.types import Context, Panel, Menu
from bl_ui.space_node import NODE_MT_context_menu

from .op import (
    UFRP_OP_batch, 
    UFRP_OP_OnlyUnmuted,
    UFRP_OP_OnlySelected,
    UFRP_OP_RenderLayerSwitch,
    UFRP_OP_ViewLayerAdd,
    UFRP_OP_ViewLayerRemove,
    UFRP_OP_ViewLayerSwitch,
    UFRP_OP_MoveLayer,
    UFRP_OP_SortLayers,
)
from . import icons


class UFRP_UL_layers(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        scene = data
        current_view_layer = item
        row = layout.row()
        row.prop(item, "name", text="", emboss=False, icon_value=icon)
        row.prop(item, "use", text="")
        op_switch = row.operator(UFRP_OP_ViewLayerSwitch.bl_idname, icon_value=icons.get_switch_id(), text="")
        op_switch.layer_name = current_view_layer.name


class UFRP_MT_manager_context_menu(Menu):
    bl_label = "ViewLayerPlus manager specials"
    def draw(self, context: Context):
        lay = self.layout
        lay.operator(UFRP_OP_MoveLayer.bl_idname, icon='TRIA_UP_BAR', text="Move to Top").direction = 'TOP'
        lay.operator(UFRP_OP_MoveLayer.bl_idname, icon='TRIA_DOWN_BAR', text="Move to Bottom").direction = 'BOTTOM'
        lay.separator()
        lay.operator(UFRP_OP_SortLayers.bl_idname, icon='SORTALPHA', text="Sort by Name",).is_reverse = False
        lay.operator(UFRP_OP_SortLayers.bl_idname, icon="ARROW_LEFTRIGHT", text="Sort reverse").is_reverse = True


class UFRP_PT_layer_manager(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "ViewLayerPlus Manager"
    bl_idname = "UFRP_PT_layer_manager"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "view_layer"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.template_list("UFRP_UL_layers", "", context.scene, "view_layers", context.scene.ufrp, "index")
        col = row.column(align=True)
        col.operator(UFRP_OP_ViewLayerAdd.bl_idname, icon='ADD', text="")
        col.operator(UFRP_OP_ViewLayerRemove.bl_idname, icon='REMOVE', text="")
        col.separator()
        col.menu("UFRP_MT_manager_context_menu", icon='DOWNARROW_HLT', text="")
        col.separator()
        sub = col.column(align=True)
        sub.operator(UFRP_OP_MoveLayer.bl_idname, icon='TRIA_UP', text="").direction = "UP"
        sub.operator(UFRP_OP_MoveLayer.bl_idname, icon='TRIA_DOWN', text="").direction = "DOWN"


class UFRP_MT_menu(bpy.types.Menu):
    bl_label = "View Layers"
    bl_idname = "UFRP_MT_menu"

    def draw(self, context: Context):
        layout = self.layout
        op_on = layout.operator(
            UFRP_OP_batch.bl_idname, 
            text="Enable all",
            icon_value = icons.get_checked_id())
        op_on.state = True
        op_off = layout.operator(
            UFRP_OP_batch.bl_idname, 
            text="Disable all",
            icon_value = icons.get_unchecked_id())
        op_off.state = False
        layout.operator(
            UFRP_OP_OnlyUnmuted.bl_idname,
            icon_value = icons.get_unmuted_id())
        layout.operator(
            UFRP_OP_OnlySelected.bl_idname,
            icon_value = icons.get_selected_id())
        layout.operator(
            UFRP_OP_RenderLayerSwitch.bl_idname,
            icon_value = icons.get_switch_id())


def draw_batch_operators(self: Panel, context: Context):
    layout = self.layout
    op_on = layout.operator(
        UFRP_OP_batch.bl_idname, 
        text="Enable all", 
        icon_value = icons.get_checked_id())
    op_on.state = True
    op_off = layout.operator(
        UFRP_OP_batch.bl_idname, 
        text="Disable all", 
        icon_value = icons.get_unchecked_id())
    op_off.state = False


def draw_comp_menu(self: Panel, context: Context):
    space = context.space_data
    if space.type == "NODE_EDITOR" and space.tree_type == "CompositorNodeTree":
        layout = self.layout
        layout.menu(UFRP_MT_menu.bl_idname)


def draw_node_menu(self: NODE_MT_context_menu, context: Context):
    if (context.space_data.tree_type == "CompositorNodeTree"
        and context.active_node):
        layout = self.layout
        layout.separator()
        layout.operator(
            UFRP_OP_RenderLayerSwitch.bl_idname, 
            icon_value = icons.get_switch_id())
        layout.operator(
            UFRP_OP_OnlySelected.bl_idname, 
            icon_value = icons.get_selected_id())