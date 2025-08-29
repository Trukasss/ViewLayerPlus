import bpy
from bpy.types import PropertyGroup
from bpy.props import IntProperty, EnumProperty, BoolProperty, StringProperty


class UFRP_properties(PropertyGroup):
    index: IntProperty(name="View Layer Index") # type: ignore
    source: StringProperty(name="View Layer copy source") # type: ignore
    show_switch: BoolProperty(name="Show 'Switch to layer' operator", default=True) # type: ignore
    show_use: BoolProperty(name="Show 'Use For Rendering' property", default=True) # type: ignore
    is_copy_exclude: BoolProperty(name="Copy/Paste 'exclude' setting", default=True) # type: ignore
    is_copy_holdout: BoolProperty(name="Copy/Paste 'holdout' setting", default=True) # type: ignore
    is_copy_indirect_only: BoolProperty(name="Copy/Paste 'indirect_only' setting", default=True) # type: ignore
    is_copy_hide_viewport: BoolProperty(name="Copy/Paste 'hide_viewport' setting", default=True) # type: ignore


def get_layer_index():
    return bpy.context.scene.ufrp.index

def set_layer_index(index: int):
    bpy.context.scene.ufrp.index = index

def is_show_switch():
    return bpy.context.scene.ufrp.show_switch

def is_show_use():
    return bpy.context.scene.ufrp.show_use

def get_layer_source():
    return bpy.context.scene.ufrp.source

def set_layer_source(layer_name: str):
    bpy.context.scene.ufrp.source = layer_name

def is_copy_exclude():
    return bpy.context.scene.ufrp.is_copy_exclude

def is_copy_holdout():
    return bpy.context.scene.ufrp.is_copy_holdout

def is_copy_indirect_only():
    return bpy.context.scene.ufrp.is_copy_indirect_only

def is_copy_hide_viewport():
    return bpy.context.scene.ufrp.is_copy_hide_viewport