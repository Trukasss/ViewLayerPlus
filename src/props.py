import bpy
from bpy.types import PropertyGroup
from bpy.props import IntProperty, EnumProperty, BoolProperty, StringProperty


class UFRP_properties(PropertyGroup):
    index: IntProperty(name="View Layer Index") # type: ignore
    source: StringProperty(name="View Layer copy source") # type: ignore
    show_switch: BoolProperty(name="Show 'Switch to layer' operator") # type: ignore
    show_use: BoolProperty(name="Show 'Use For Rendering' property") # type: ignore


def get_layer_index():
    return bpy.context.scene.ufrp.index

def set_layer_index(index: int):
    bpy.context.scene.ufrp.index = index

def is_show_switch():
    return bpy.context.scene.ufrp.show_switch

def is_show_use():
    return bpy.context.scene.ufrp.show_use