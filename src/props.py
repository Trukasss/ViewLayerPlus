import bpy
from bpy.types import PropertyGroup, Context
from bpy.props import IntProperty, CollectionProperty, BoolProperty, StringProperty, EnumProperty, PointerProperty


def is_prop_copyable(rna_prop):
    if isinstance(rna_prop, (
        bpy.types.IntProperty,
        bpy.types.FloatProperty,
        bpy.types.BoolProperty,
        bpy.types.StringProperty,
        bpy.types.EnumProperty, #TODO needs testing, but should work
        )) and not rna_prop.is_readonly:
        return True
    return False

def populate_prop_passes(context: Context):
    def new(name, identifier, type, sub_type=""):
        if identifier == "name": # do not copy view layer name
            return
        if rna_prop.is_readonly:
            return
        if not identifier.startswith("use_"):
            return
        new_prop: UFRP_property_passe = passes.add()
        new_prop.name = name
        new_prop.identifier = identifier
        new_prop.type = type
        new_prop.sub_type = sub_type
    
    passes = get_passes()
    passes.clear()
    for rna_prop in context.view_layer.bl_rna.properties:
        key = rna_prop.identifier
        if key in ["eevee", "cycles"]:
            for rna_prop in  getattr(context.view_layer, key).bl_rna.properties:
                new(rna_prop.name, rna_prop.identifier, rna_prop.type, key)
            continue
        new(rna_prop.name, rna_prop.identifier , rna_prop.type, "View Layer")

class UFRP_property_passe(PropertyGroup):
    name: StringProperty() # type: ignore
    identifier: StringProperty() # type: ignore
    type: StringProperty() # type: ignore
    sub_type: StringProperty() #type: ignore
    is_copy: BoolProperty(default=True) # type: ignore


class UFRP_properties(PropertyGroup):
    index: IntProperty(name="Highlighted View Layer") # type: ignore
    source: StringProperty(name="View Layer copy source") # type: ignore
    show_use: BoolProperty(name="Show use", description="Show 'Use For Rendering' property", default=True) # type: ignore
    is_copy_exclude: BoolProperty(name="Copy Exclude from View Layer", description="Copy/Paste 'exclude' setting", default=True) # type: ignore
    is_copy_hide_viewport: BoolProperty(name="Copy Hide in Viewport", description="Copy/Paste 'hide_viewport' setting", default=True) # type: ignore
    is_copy_holdout: BoolProperty(name="Copy Holdout", description="Copy/Paste 'holdout' setting", default=True) # type: ignore
    is_copy_indirect_only: BoolProperty(name="Copy Indirect Only", description="Copy/Paste 'indirect_only' setting", default=True) # type: ignore
    is_copy_passes: BoolProperty(name="Copy Render Passes", description="Copy/Paste View Layer render passes properties", default=True) # type: ignore
    passes: CollectionProperty(type=UFRP_property_passe, name="View Layer properties to copy") # type: ignore
    is_copy_aovs: BoolProperty(name="Copy AOVs", description="Copy/Paste View Layer AOVs", default=True) # type: ignore


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

def get_passes() -> UFRP_property_passe:
    return bpy.context.scene.ufrp.passes

def is_copy_aovs() -> bpy.types.BoolProperty:
    return bpy.context.scene.ufrp.is_copy_aovs