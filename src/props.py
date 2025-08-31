import bpy
from bpy.types import PropertyGroup, Context
from bpy.props import IntProperty, CollectionProperty, BoolProperty, StringProperty, EnumProperty, PointerProperty
from cycles.properties import CyclesRenderLayerSettings


# # TODO (wip) add all proprety support (ex: eevee, aovs)
# def is_viewlayer_prop_supported(view_layer: bpy.types.ViewLayer, attr_name: str):
#     if attr_name == "name": # do not copy view layer name
#         return False
#     rna = view_layer.bl_rna.properties[attr_name]
#     attr = getattr(view_layer, attr_name)
#     # Support simple writable properties
#     if isinstance(rna, (
#         bpy.types.IntProperty,
#         bpy.types.FloatProperty,
#         bpy.types.BoolProperty,
#         bpy.types.StringProperty,
#         bpy.types.EnumProperty, #TODO needs testing, but should work
#         )) and not rna.is_readonly:
#         return True
#     # Support writable pointer properties & eevee & cycles
#     if isinstance(rna, bpy.types.PointerProperty):
#         if not rna.is_readonly:
#             return True
#         if isinstance(rna.fixed_type, (
#             bpy.types.ViewLayerEEVEE,
#             CyclesRenderLayerSettings,)):
#             return True
#         return False
#     # Support collection properties with add/remove functions
#     if (
#         isinstance(rna, bpy.types.CollectionProperty)
#         and hasattr(attr, "add")
#         and hasattr(attr, "remove")
#         ):
#         return True
#     return False


def populate_copy_props(context: Context):
    copy_props = get_copy_props()
    copy_props.clear()
    for rna_prop in context.view_layer.bl_rna.properties:
        # if not is_viewlayer_prop_supported(context.view_layer, rna_prop.identifier):
        if not rna_prop.identifier.startswith("use_pass_"):
            continue
        new_prop = copy_props.add()
        new_prop: UFRP_layer_setting_copy
        new_prop.name = rna_prop.name
        new_prop.identifier = rna_prop.identifier 
        new_prop.type = rna_prop.type


class UFRP_layer_setting_copy(PropertyGroup):
    name: StringProperty() # type: ignore
    identifier: StringProperty() # type: ignore
    type: StringProperty() # type: ignore
    is_copy: BoolProperty(default=True) # type: ignore


class UFRP_properties(PropertyGroup):
    index: IntProperty(name="View Layer Index") # type: ignore
    source: StringProperty(name="View Layer copy source") # type: ignore
    show_use: BoolProperty(name="Show 'Use For Rendering' property", default=True) # type: ignore
    is_copy_exclude: BoolProperty(name="Copy/Paste 'exclude' setting", default=True) # type: ignore
    is_copy_holdout: BoolProperty(name="Copy/Paste 'holdout' setting", default=True) # type: ignore
    is_copy_indirect_only: BoolProperty(name="Copy/Paste 'indirect_only' setting", default=True) # type: ignore
    is_copy_hide_viewport: BoolProperty(name="Copy/Paste 'hide_viewport' setting", default=True) # type: ignore
    is_copy_passes: BoolProperty(name="Copy/Paste View Layer passes setting", default=True) # type: ignore
    copy_props: CollectionProperty(type=UFRP_layer_setting_copy, name="View Layer properties to copy") # type: ignore


def get_layer_index() -> bpy.types.IntProperty:
    return bpy.context.scene.ufrp.index

def set_layer_index(index: int):
    bpy.context.scene.ufrp.index = index

def is_show_use() -> bpy.types.BoolProperty:
    return bpy.context.scene.ufrp.show_use

def get_layer_source() -> bpy.types.StringProperty:
    return bpy.context.scene.ufrp.source

def set_layer_source(layer_name: str):
    bpy.context.scene.ufrp.source = layer_name

def is_copy_exclude() -> bpy.types.BoolProperty:
    return bpy.context.scene.ufrp.is_copy_exclude

def is_copy_holdout() -> bpy.types.BoolProperty:
    return bpy.context.scene.ufrp.is_copy_holdout

def is_copy_indirect_only() -> bpy.types.BoolProperty:
    return bpy.context.scene.ufrp.is_copy_indirect_only

def is_copy_hide_viewport() -> bpy.types.BoolProperty:
    return bpy.context.scene.ufrp.is_copy_hide_viewport

def is_copy_passes() -> bpy.types.BoolProperty:
    return bpy.context.scene.ufrp.is_copy_passes

def get_copy_props() -> UFRP_layer_setting_copy:
    return bpy.context.scene.ufrp.copy_props