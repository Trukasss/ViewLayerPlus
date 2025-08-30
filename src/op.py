import bpy
from bpy.types import Operator, Context, Scene, ViewLayer, CompositorNodeRLayers, Collection, CollectionProperty, LayerCollection, bpy_struct, bpy_prop_collection
from bpy.props import BoolProperty
import json
import re
from . import props

############## COMPOSITING ##############
def get_render_node_scene_layer(node: CompositorNodeRLayers):
    if node.type != "R_LAYERS":
        raise ValueError("Active node must be of Render Layer type")
    if node.scene is None:
        return (None, None)
    layer = node.scene.view_layers.get(node.layer, None)
    if layer is None:
        return (node.scene, None)
    return (node.scene, layer)


def get_render_nodes(unmuted_only=False):
    node_tree =  bpy.context.scene.node_tree
    if not node_tree:
        return []
    if unmuted_only:
        return [node for node in node_tree.nodes if node.type == "R_LAYERS" and not node.mute]
    return [node for node in node_tree.nodes if node.type == "R_LAYERS"]


def use_view_layers(layers: list[ViewLayer], include=True):
    #TODO not really readable
    bpy.context.scene.render.use_single_layer = False
    nb_view_layers = 0
    for scene in bpy.data.scenes:
        scene: Scene
        for vl in scene.view_layers:
            if vl in layers:
                if include:
                    vl.use = True
                    nb_view_layers += 1
                else:
                    vl.use = False
            else:
                if include:
                    vl.use = False
                else:
                    vl.use = True
                    nb_view_layers += 1
    return nb_view_layers


class UFRP_OP_batch(Operator):
    """Set all View Layers 'Use for rendering' property"""
    bl_idname = "ufrp.batch"
    bl_label = "Use for rendering batch"
    bl_options = {"REGISTER", "UNDO"}
    state: BoolProperty(
        name="UseForRenderingState", 
        description="Check or uncheck all View Layers 'Use for rendering' property"
        ) # type: ignore

    def execute(self, context: Context):
        if self.state == True:
            nb = use_view_layers([], include=False)
        else:
            nb = use_view_layers([], include=True)
        render_nodes = get_render_nodes()
        for node in render_nodes:
            node: CompositorNodeRLayers
            node.mute = not self.state
        if self.state == True:
            self.report({"INFO"}, f"Enabled all {nb} View Layers for rendering")
        else:
            self.report({"INFO"}, f"Disabled all {nb} View Layers from rendering")
        return {"FINISHED"}


class UFRP_OP_OnlyUnmuted(Operator):
    """Only 'use for rendering' unmuted render layer nodes"""
    bl_idname = "ufrp.only_active"
    bl_label = "Enable unmuted only"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context: Context):
        # get layers to use
        render_nodes = get_render_nodes(unmuted_only=True)
        layers_to_use = []
        for node in render_nodes:
            scene, layer = get_render_node_scene_layer(node)
            if not layer:
                continue
            layers_to_use.append(layer)
        # only activate layers to use
        use_view_layers(layers_to_use, include=True)
        self.report({"INFO"}, f"Enable only {len(layers_to_use)} active View Layers for rendering")
        return {"FINISHED"}


class UFRP_OP_OnlySelected(Operator):
    """Only 'use for rendering' selected render layer nodes"""
    bl_idname = "ufrp.only_selected"
    bl_label = "Enable selected only"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: Context):
        cls.poll_message_set("Must select Render Layer nodes")
        render_layer_nodes = [node for node in context.selected_nodes if node.type == "R_LAYERS"]
        return len(render_layer_nodes) > 0
    
    def execute(self, context: Context):
        render_nodes = get_render_nodes()
        selected_nodes = [node for node in context.selected_nodes if node.type == "R_LAYERS"]
        if not selected_nodes:
            self.report({"ERROR"}, "Must select at least one render layer node")
            return {"CANCELLED"}
        layers_to_use = []
        for node in render_nodes:
            if node not in selected_nodes:
                node.mute = True
                continue
            node.mute = False
            scene, layer = get_render_node_scene_layer(node)
            if not layer:
                continue
            layers_to_use.append(layer)
        use_view_layers(layers_to_use, include=True)
        self.report({"INFO"}, f"Enable only {len(layers_to_use)} selected View Layers for rendering")
        return {"FINISHED"}


class UFRP_OP_RenderLayerSwitch(Operator):
    """Switch to active render layer node's View Layer"""
    bl_idname = "ufrp.switch_render_layer"
    bl_label = "Switch to active Render Layer Node"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: Context):
        cls.poll_message_set("Must select a Render Layer Node")
        return (
            context.selected_nodes
            and context.active_node
            and context.active_node.type == "R_LAYERS")
    
    def execute(self, context: Context):
        node = context.active_node
        if node.type != "R_LAYERS":
            self.report({"ERROR"}, "Active node must be of Render Layer type")
            return {"CANCELLED"}
        scene, layer = get_render_node_scene_layer(node)
        if not scene or not layer:
            self.report({"ERROR"}, f"Could not find scene '{scene}' and View Layer '{layer}'")
            return {"CANCELLED"}
        context.window.scene = scene
        context.window.view_layer = layer
        self.report({"INFO"}, f"Switched to '{layer.name}' View Layer")
        return {"FINISHED"}


############## LAYER MANAGER ##############
class UFRP_OP_ViewLayerAdd(Operator):
    """Add a new View Layer from selected"""
    bl_idname = "ufrp.view_layer_add"
    bl_label = "Add a new View Layer"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: Context):
        layer_index = props.get_layer_index()
        #TODO check si index correct, peut-etre interdir en dehors du nombre de View Layer dans la proprietee directement
        selected_layer = context.scene.view_layers[layer_index]
        context.scene.view_layers.new(selected_layer.name)
        props.set_layer_index(layer_index + 1)
        return {"FINISHED"}


class UFRP_OP_ViewLayerRemove(Operator):
    """Remove selected View Layer"""
    bl_idname = "ufrp.view_layer_remove"
    bl_label = "Remove the View Layer"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: Context):
        cls.poll_message_set("Cannot remove last View Layer")
        return len(context.scene.view_layers) > 1

    def execute(self, context):
        layer_index = props.get_layer_index()
        selected_layer = context.scene.view_layers[layer_index]
        context.scene.view_layers.remove(selected_layer)
        props.set_layer_index(layer_index - 1)
        return {"FINISHED"}


class UFRP_OP_ViewLayerSwitch(Operator):
    """Switch to manager's View Layer"""
    bl_idname = "ufrp.switch_view_layer"
    bl_label = "Switch to View Layer"
    bl_options = {"REGISTER", "UNDO"}
    layer_name: bpy.props.StringProperty("View Layer name") # type: ignore

    def execute(self, context: Context):
        selected_layer = context.scene.view_layers.get(self.layer_name)
        context.window.view_layer = selected_layer
        switched_index = context.scene.view_layers.keys().index(self.layer_name)
        props.set_layer_index(switched_index)
        return {"FINISHED"}


class UFRP_OP_CopyLayerSettings(Operator):
    """Set selected View Layer's as copy source"""
    bl_idname = "ufrp.copy_layer_settings"
    bl_label = "Copy settings"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: Context):
        layer_index = props.get_layer_index()
        selected_layer = context.scene.view_layers[layer_index]
        props.set_layer_source(selected_layer.name)
        self.report({"INFO"}, f"Set '{selected_layer.name}' as copy source")
        return {"FINISHED"}


class UFRP_OP_PasteLayerSettings(Operator):
    """Paste View Layer's Layer Collections settings from source"""
    bl_idname = "ufrp.paste_layer_settings"
    bl_label = "Paste settings"
    bl_options = {"REGISTER", "UNDO"}

    @staticmethod
    def copy_layercollection_settings(source_lc: LayerCollection, target_lc: LayerCollection):
        """Recursively copy View Layer's Layer Collections settings"""
        s = source_lc
        t = target_lc
        if props.is_copy_exclude():
            t.exclude = s.exclude
        if props.is_copy_holdout():
            t.holdout = s.holdout
        if props.is_copy_indirect_only():
            t.indirect_only = s.indirect_only
        if props.is_copy_hide_viewport():
            t.hide_viewport = s.hide_viewport
        for src_child, dst_child in zip(s.children, t.children):
            __class__.copy_layercollection_settings(src_child, dst_child)

    @staticmethod
    def copy_attrs(object_source, object_target, passes_only=True):
        """Recursively copy blender's attributes"""
        for attr_name in dir(object_source):
            if passes_only and not attr_name.startswith("use_"):
                continue
            # ingore unsettable attrs
            if isinstance(object_source, ViewLayer) and attr_name == "name":
                continue # don't change View Layer's names
            if attr_name.startswith("_"):
                continue
            attr_src = getattr(object_source, attr_name)
            if callable(attr_src):
                continue
            # collection props
            if isinstance(attr_src, bpy_prop_collection):
                if not getattr(attr_src, "add", False):
                    continue
                if not getattr(attr_src, "remove", False):
                    continue
                attr_trg = getattr(object_target, attr_name)
                for prop_trg in attr_trg:
                    attr_trg.remove(prop_trg)
                for prop in attr_src:
                    new_prop = attr_trg.add()
                    __class__.copy_attrs(prop, new_prop, passes_only)
                continue
            # simple props/variables
            try:
                setattr(object_target, attr_name, attr_src)
            except AttributeError as e:
                if "read-only" in str(e):
                    continue
                print(f"Could not set attr '{attr_name}': {e}")


    def execute(self, context: Context):
        if (not props.is_copy_exclude() 
            and not props.is_copy_holdout() 
            and not props.is_copy_indirect_only() 
            and not props.is_copy_hide_viewport()
            and not props.is_copy_passes()):
            self.report({"WARNING"}, f"No settings to Copy/Paste, please check at least one option")
            return {"CANCELLED"}
        source_vl_name = props.get_layer_source()
        if not source_vl_name:
            self.report({"WARNING"}, f"Please first copy a View Layer")
            return {"CANCELLED"}
        source_vl = context.scene.view_layers.get(source_vl_name, None)
        if not source_vl:
            self.report({"WARNING"}, f"Source '{source_vl_name}' View Layer is missing, please new View Layer")
            return {"CANCELLED"}
        layer_index = props.get_layer_index()
        target_vl = context.scene.view_layers[layer_index]
        self.copy_layercollection_settings(source_vl.layer_collection, target_vl.layer_collection)
        if props.is_copy_passes():
            print("=======================") #TODO DEBUG
            self.copy_attrs(source_vl, target_vl, True)
        self.report({"INFO"}, f"Pasted settings from '{source_vl.name}' to '{target_vl.name}'")
        return {"FINISHED"}


class UFRP_OP_MoveLayer(Operator):
    """Move selected View Layer up or down"""
    bl_idname = "ufrp.move_layer"
    bl_label = "Move up/down"
    bl_options = {"REGISTER", "UNDO"}
    direction: bpy.props.StringProperty() #type: ignore

    @classmethod
    def poll(cls, context: Context):
        cls.poll_message_set("Must have at least two View Layers")
        return len(context.scene.view_layers) > 1

    def execute(self, context: Context):
        layer_index = props.get_layer_index()
        if self.direction == "UP":
            index_to = layer_index - 1
            if index_to < 0:
                index_to = len(context.scene.view_layers) - 1
        elif self.direction == "DOWN":
            index_to = layer_index + 1
            if index_to > len(context.scene.view_layers) - 1:
                index_to = 0
        elif self.direction == "TOP":
            index_to = 0
        elif self.direction == "BOTTOM":
            index_to = len(context.scene.view_layers) - 1
        else:
            self.report({"ERROR"}, f"Operator property 'direction' should be in 'UP', 'DOWN', 'TOP' or 'BOTTOM', got '{self.direction}'")
            return {"CANCELLED"}
        context.scene.view_layers.move(layer_index, index_to)
        props.set_layer_index(index_to)

        return {"FINISHED"}


class UFRP_OP_SortLayers(Operator):
    """Sort View Layers by name"""
    bl_idname = "ufrp.sort_layers"
    bl_label = "Sort layers"
    bl_options = {"REGISTER", "UNDO"}
    is_reverse: bpy.props.BoolProperty(default=False) #type: ignore

    @classmethod
    def poll(cls, context: Context):
        cls.poll_message_set("Must have at least two View Layers")
        return len(context.scene.view_layers) > 1
    
    @staticmethod
    def natural_sort_key(s, _nsre=re.compile("([0-9]+)")):
        """Sort a string in a natural way
        https://stackoverflow.com/a/16090640"""
        return [int(text) if text.isdigit() else text.lower() for text in _nsre.split(s)]

    def execute(self, context: Context):
        layers = context.scene.view_layers
        sorted_layers = sorted(layers, key=lambda vl: self.natural_sort_key(vl.name))
        if self.is_reverse:
            sorted_layers.reverse()
        for to_i, l in enumerate(sorted_layers):
            current_i = [l.name for l in context.scene.view_layers].index(l.name)
            context.scene.view_layers.move(current_i, to_i)
        return {"FINISHED"}