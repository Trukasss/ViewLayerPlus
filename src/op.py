import bpy
from bpy.types import Operator, Context, Scene, ViewLayer, CompositorNodeRLayers
from bpy.props import BoolProperty


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


class UFRP_OP_SwitchViewLayer(Operator):
    """Switch to active render layer node's view layer"""
    bl_idname = "ufrp.switch_view_layer"
    bl_label = "Switch to active View Layer"
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