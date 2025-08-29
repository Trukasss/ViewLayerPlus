import bpy
from bpy.types import PropertyGroup
from bpy.props import IntProperty, EnumProperty, BoolProperty, StringProperty


class UFRP_properties(PropertyGroup):
    index: IntProperty(name="View Layer Index") # type: ignore
    source: StringProperty(name="View Layer copy source") # type: ignore


def get_layer_index():
    return bpy.context.scene.ufrp.index

def set_layer_index(index: int):
    bpy.context.scene.ufrp.index = index

