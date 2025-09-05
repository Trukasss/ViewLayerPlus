import bpy
from bpy.types import Context, Panel, Menu, UIList
from bl_ui.space_node import NODE_MT_context_menu
from bl_ui.space_topbar import TOPBAR_HT_upper_bar
from . import props
from .op import (
    UFRP_OP_batch, 
    UFRP_OP_OnlyUnmuted,
    UFRP_OP_OnlySelected,
    UFRP_OP_RenderLayerSwitch,
    UFRP_OP_AllCopyProps,
    UFRP_OP_ReloadPasses,
    UFRP_OP_CopyLayer,
    UFRP_OP_PasteLayer,
    UFRP_OP_ViewLayerAdd,
    UFRP_OP_ViewLayerRemove,
    UFRP_OP_ViewLayerSwitch,
    UFRP_OP_MoveLayer,
    UFRP_OP_SortLayers,
)
from . import icons


class UFRP_PT_layer_filter(Panel):
    """Show View Layer manager list options"""
    bl_label = "ViewLayerPlus Manager filter"
    bl_idname = "UFRP_PT_layer_filter"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "view_layer"
    bl_options = {"INSTANCED"}

    def draw(self, context: Context):
        lay = self.layout
        lay.label(text="Filter manager options")
        row = lay.row(align=True)
        row.prop(context.scene.ufrp, "show_use", text="", icon="CHECKBOX_HLT", toggle=True)


class UFRP_PT_passes_filter(Panel):
    """Choose which View Layer's passes to copy"""
    bl_label = "ViewLayerPlus copy passes filter"
    bl_idname = "UFRP_PT_passes_filter"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "view_layer"
    bl_options = {"INSTANCED"}

    def draw_options_row(self, layout):
        row = layout.row(align=True)
        row.operator(UFRP_OP_AllCopyProps.bl_idname, text="", icon="RESTRICT_SELECT_OFF").action = "ON"
        row.operator(UFRP_OP_AllCopyProps.bl_idname, text="", icon="RESTRICT_SELECT_ON").action = "OFF"
        row.operator(UFRP_OP_AllCopyProps.bl_idname, text="", icon="UV_SYNC_SELECT").action = "TOGGLE"
        row.separator()
        row.operator(UFRP_OP_ReloadPasses.bl_idname, text="", icon="FILE_REFRESH")

    def draw(self, context: Context):
        lay = self.layout
        passes = props.get_passes()
        if not passes:
            lay.operator(UFRP_OP_ReloadPasses.bl_idname, icon="FILE_REFRESH")  
            return
        self.draw_options_row(lay)
        col = lay.column(align=True)
        props_sorted = sorted(passes, key=lambda p: f"{p.sub_type}_{p.type}") #TODO sort when creating ?
        last_type = passes[0].type
        last_sub_type = passes[0].sub_type
        for p in props_sorted:
            p: props.UFRP_property_passe
            if p.type != last_type or p.sub_type != last_sub_type:
                last_type = p.type
                last_sub_type = p.sub_type
                col.separator()
                col.label(text=p.sub_type)
            match p.type:
                case "FLOAT":
                    icon = "CON_TRANSFORM"
                case "INT":
                    icon = "CON_TRANSFORM"
                case "BOOLEAN":
                    icon = "CHECKBOX_HLT"
                case "COLLECTION":
                    icon = "MOD_ARRAY"
                case "POINTER":
                    icon = "FILE_3D"
                case "STRING":
                    icon = "SYNTAX_OFF"
                case _:
                    icon = "NONE"
            col.prop(p, "is_copy", text=p.name, icon=icon, toggle=True)
        self.draw_options_row(lay)


class UFRP_UL_layers(UIList):
    bl_idname = "UFRP_UL_layers"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        scene = data
        row = layout.row(align=True)
        if item == context.view_layer:
            # row.label(text="")
            row.prop(item, "name", text="", emboss=False, icon_value=icon)
        else:
            row.operator(UFRP_OP_ViewLayerSwitch.bl_idname, text="", icon_value=icons.get_switch_id()).layer_name = item.name
            row.prop(item, "name", text="", emboss=False, icon="BLANK1")
        row = row.row(align=True)
        if props.is_show_use():
            row.prop(item, "use", text="")#, toggle=True)


class UFRP_MT_manager_context_menu(Menu):
    bl_label = "ViewLayerPlus manager specials"
    def draw(self, context: Context):
        lay = self.layout
        lay.operator(UFRP_OP_MoveLayer.bl_idname, icon="TRIA_UP_BAR", text="Move to Top").direction = "TOP"
        lay.operator(UFRP_OP_MoveLayer.bl_idname, icon="TRIA_DOWN_BAR", text="Move to Bottom").direction = "BOTTOM"
        lay.separator()
        lay.operator(UFRP_OP_SortLayers.bl_idname, icon="SORT_ASC", text="Sort by Name",).is_reverse = False
        lay.operator(UFRP_OP_SortLayers.bl_idname, icon="SORT_DESC", text="Sort reverse").is_reverse = True
        lay.separator()
        lay.operator(UFRP_OP_batch.bl_idname, text="Enable all", icon_value = icons.get_checked_id()).state = True
        lay.operator(UFRP_OP_batch.bl_idname, text="Disable all", icon_value = icons.get_unchecked_id()).state = False


class UFRP_PT_manager(Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "ViewLayerPlus Manager"
    bl_region_type = "WINDOW"

    def draw(self, context):
        lay = self.layout
        row = lay.row()
        col1 = row.column()
        col2 = row.column(align=True)
        # col1 (main)
        col1.template_list(UFRP_UL_layers.bl_idname, "", context.scene, "view_layers", context.scene.ufrp, "index")
        col1.label(text="Copy/Paste View Layers properties")
        row = col1.row(align=True)
        row.prop(context.scene.ufrp, "is_copy_exclude", text="", icon="CHECKBOX_HLT", toggle=True)
        row.prop(context.scene.ufrp, "is_copy_hide_viewport", text="", icon="HIDE_OFF", toggle=True)
        row.prop(context.scene.ufrp, "is_copy_holdout", text="", icon="HOLDOUT_ON", toggle=True)
        row.prop(context.scene.ufrp, "is_copy_indirect_only", text="", icon="INDIRECT_ONLY_ON", toggle=True)
        row.separator()
        row.prop(context.scene.ufrp, "is_copy_passes", text="Passes", toggle=True)
        row.popover(panel=UFRP_PT_passes_filter.bl_idname, text="", icon="FILTER")
        row.separator()
        row.prop(context.scene.ufrp, "is_copy_aovs", text="AOVs", toggle=True)
        row.separator()
        row.operator(UFRP_OP_CopyLayer.bl_idname, text="", icon="COPYDOWN")
        row.operator(UFRP_OP_PasteLayer.bl_idname, text="", icon="PASTEDOWN")
        # col2 (sidebar)
        col2.operator(UFRP_OP_ViewLayerAdd.bl_idname, icon="ADD", text="")
        col2.operator(UFRP_OP_ViewLayerRemove.bl_idname, icon="REMOVE", text="")
        col2.separator()
        col2.popover(panel=UFRP_PT_layer_filter.bl_idname, text="", icon="FILTER")
        col2.menu("UFRP_MT_manager_context_menu", icon="DOWNARROW_HLT", text="")
        col2.separator()
        col2.operator(UFRP_OP_MoveLayer.bl_idname, icon="TRIA_UP", text="").direction = "UP"
        col2.operator(UFRP_OP_MoveLayer.bl_idname, icon="TRIA_DOWN", text="").direction = "DOWN"


class UFRP_PT_manager_topbar(UFRP_PT_manager):
    bl_idname = "UFRP_PT_UFRP_PT_manager_topbarlayer_manager"
    bl_space_type = "TOPBAR"
    bl_options = {"INSTANCED"}
    bl_ui_units_x = 20


class UFRP_PT_manager_properties(UFRP_PT_manager):
    bl_idname = "UFRP_PT_manager_properties"
    bl_space_type = "PROPERTIES"
    bl_context = "view_layer"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "VIEWLAYER_PT_layer"


class UFRP_MT_menu(Menu):
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


def draw_comp_menu(self: NODE_MT_context_menu, context: Context):
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


def draw_manager_topbar(self: TOPBAR_HT_upper_bar, context: Context):
    if context.region.alignment == "RIGHT":
        lay = self.layout
        lay.popover(panel=UFRP_PT_manager_topbar.bl_idname, text="", icon_value=icons.get_addon_id())