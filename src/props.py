import bpy
from bpy.types import PropertyGroup, Context
from bpy.props import IntProperty, CollectionProperty, BoolProperty, StringProperty, EnumProperty, PointerProperty


def populate_copy_props(context: Context):
    copy_props = get_copy_props()
    copy_props.clear()
    for rna_prop in context.view_layer.bl_rna.properties:
        if rna_prop.is_readonly and not isinstance(rna_prop, bpy.types.CollectionProperty):
            continue
        if rna_prop.identifier == "name":
            continue # never copy layer name
        copy_props: bpy.types.CollectionProperty
        new_prop = copy_props.add()
        new_prop: UFRP_layer_setting_copy
        new_prop.name = rna_prop.name
        new_prop.identifier = rna_prop.identifier 
        match rna_prop.type:
            case "FLOAT":
                new_prop.icon = "CON_TRANSFORM"
            case "INT":
                new_prop.icon = "CON_TRANSFORM"
            case "BOOLEAN":
                new_prop.icon = "CHECKBOX_HLT"
            case "COLLECTION":
                new_prop.icon = "MOD_ARRAY"
            case "POINTER":
                new_prop.icon = "FILE_3D"
            case "STRING":
                new_prop.icon = "SYNTAX_OFF"
            case _:
                new_prop.icon = "NONE"


class UFRP_layer_setting_copy(PropertyGroup):
    name: StringProperty() # type: ignore
    identifier: StringProperty() # type: ignore
    icon: StringProperty() # type: ignore
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


def get_layer_index():
    return bpy.context.scene.ufrp.index

def set_layer_index(index: int):
    bpy.context.scene.ufrp.index = index

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

def is_copy_passes():
    return bpy.context.scene.ufrp.is_copy_passes

def get_copy_props():
    return bpy.context.scene.ufrp.copy_props