import bpy
from bpy.types import Operator, Context, Scene, ViewLayer, CompositorNodeRLayers, Collection, CollectionProperty, LayerCollection
from bpy.props import BoolProperty
import json
import re
from . import props


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
    """Set all view layers 'Use for rendering' property"""
    bl_idname = "ufrp.batch"
    bl_label = "Use for rendering batch"
    bl_options = {"REGISTER", "UNDO"}
    state: BoolProperty(
        name="UseForRenderingState", 
        description="Check or uncheck all view layers 'Use for rendering' property"
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
            self.report({"INFO"}, f"Enabled all {nb} view layers for rendering")
        else:
            self.report({"INFO"}, f"Disabled all {nb} view layers from rendering")
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
        self.report({"INFO"}, f"Enable only {len(layers_to_use)} active view layers for rendering")
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
        self.report({"INFO"}, f"Enable only {len(layers_to_use)} selected view layers for rendering")
        return {"FINISHED"}


class UFRP_OP_RenderLayerSwitch(Operator):
    """Switch to active render layer node's view layer"""
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
            self.report({"ERROR"}, f"Could not find scene '{scene}' and view layer '{layer}'")
            return {"CANCELLED"}
        context.window.scene = scene
        context.window.view_layer = layer
        self.report({"INFO"}, f"Switched to '{layer.name}' view layer")
        return {"FINISHED"}


############## LAYER MANAGER ##############

class UFRP_OP_ViewLayerAdd(Operator):
    """Add a new View Layer from selected"""
    bl_idname = "ufrp.view_layer_add"
    bl_label = "Add a new View Layer"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        layer_index = props.get_layer_index()
        #TODO check si index correct, peut-etre interdir en dehors du nombre de view layer dans la proprietee directement
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
    """Switch to manager selected View Layer"""
    bl_idname = "ufrp.switch_view_layer"
    bl_label = "Switch to selected View Layer"
    bl_options = {"REGISTER", "UNDO"}
    layer_name: bpy.props.StringProperty("View Layer name") # type: ignore

    def execute(self, context):
        selected_layer = context.scene.view_layers.get(self.layer_name)
        context.window.view_layer = selected_layer
        switched_index = context.scene.view_layers.keys().index(self.layer_name)
        props.set_layer_index(switched_index)
        return {"FINISHED"}


def recursive_layer_collection_search(collection: Collection, layer_collections: CollectionProperty):
    pass #TODO recursivly store/copy view layer settings

    # for lc in layer_collections:
    #     lc: LayerCollection
    #     if lc.collection == collection:
    #         return lc
    # for lc in layer_collections:
    #     found = recursive_layer_collection_search(collection, lc.children)
    #     if found:
    #         return lc
    # return None


class UFRP_OP_CopyLayerSettings(Operator):
    """Copy selected View Layer's settings"""
    bl_idname = "ufrp.copy_layer_settings"
    bl_label = "Copy settings"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        layer_index = props.get_layer_index()
        selected_layer = context.scene.view_layers[layer_index]
        context.scene.view_layer_source = selected_layer.name
        return {"FINISHED"}


class UFRP_OP_PasteLayerSettings(Operator):
    """Paste copied source settings to selected View Layer"""
    bl_idname = "ufrp.paste_layer_settings"
    bl_label = "Paste settings"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        source_layer = context.scene.view_layer_source
        layer_index = props.get_layer_index()
        selected_layer = context.scene.view_layers[layer_index]
        recursive_layer_collection_search() #TODO:
        return {"FINISHED"}


class UFRP_OP_MoveLayer(Operator):
    """Move selected View layer up or down"""
    bl_idname = "ufrp.move_layer"
    bl_label = "Move up/down"
    bl_options = {"REGISTER", "UNDO"}
    direction: bpy.props.StringProperty() #type: ignore

    @classmethod
    def poll(cls, context: Context):
        cls.poll_message_set("Must have at least two view layers")
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
    """Sort View layers by name"""
    bl_idname = "ufrp.sort_layers"
    bl_label = "Sort layers"
    bl_options = {"REGISTER", "UNDO"}
    is_reverse: bpy.props.BoolProperty(default=False) #type: ignore

    @classmethod
    def poll(cls, context: Context):
        cls.poll_message_set("Must have at least two view layers")
        return len(context.scene.view_layers) > 1
    
    @staticmethod
    def natural_sort_key(s, _nsre=re.compile('([0-9]+)')):
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