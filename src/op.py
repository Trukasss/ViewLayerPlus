import bpy
from bpy.types import Operator, Context, Scene, ViewLayer, CompositorNodeRLayers, Collection, CollectionProperty, LayerCollection, bpy_struct, bpy_prop_collection, ViewLayerEEVEE
from bpy.props import BoolProperty
import re
from . import props

############## COMPOSITING ##############
def get_render_node_scene_layer(node: CompositorNodeRLayers) -> tuple[Scene, ViewLayer]:
    if node.type != "R_LAYERS":
        raise ValueError("Active node must be of Render Layer type")
    if node.scene is None:
        return (None, None)
    layer = node.scene.view_layers.get(node.layer, None)
    if layer is None:
        return (node.scene, None)
    return (node.scene, layer)


def get_render_nodes(unmuted_only=False, selected_only=False):
    node_tree =  bpy.context.scene.node_tree
    if not node_tree:
        return []
    return [
        n for n in node_tree.nodes
        if n.type == "R_LAYERS"
        and (not unmuted_only or not n.mute)
        and (not selected_only or n.select)
    ]


def set_all_view_layers(layers: list[ViewLayer], include=True):
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


class UFRP_OP_toggle(Operator):
    """Set selected View Layers 'Use for rendering' property"""
    bl_idname = "ufrp.toggle"
    bl_label = "Use for rendering selected"
    bl_options = {"REGISTER", "UNDO"}
    state: BoolProperty(
        name="UseForRenderingState", 
        description="Check or uncheck selected View Layers 'Use for rendering' property"
        ) # type: ignore

    @classmethod
    def poll(cls, context: Context):
        cls.poll_message_set("Must select Render Layer nodes")
        return get_render_nodes(selected_only=True)

    def execute(self, context: Context):
        render_nodes = get_render_nodes(selected_only=True)
        bpy.context.scene.render.use_single_layer = False
        for node in render_nodes:
            node.mute = not self.state
            scene, layer = get_render_node_scene_layer(node)
            if not layer:
                continue
            layer.use = self.state
        if self.state == True:
            self.report({"INFO"}, f"Enabled selected {len(render_nodes)} View Layers for rendering")
        else:
            self.report({"INFO"}, f"Disabled selected {len(render_nodes)} View Layers from rendering")
        return {"FINISHED"}


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
            nb = set_all_view_layers([], include=False)
        else:
            nb = set_all_view_layers([], include=True)
        # update render nodes mute state
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
        set_all_view_layers(layers_to_use, include=True)
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
        return get_render_nodes(selected_only=True)
    
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
        set_all_view_layers(layers_to_use, include=True)
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
        if context.window.scene == scene and context.window.view_layer == layer:
            self.report({"INFO"}, f"Already on '{layer.name}' View Layer")
            return {"CANCELLED"}
        context.window.scene = scene
        context.window.view_layer = layer
        self.report({"INFO"}, f"Switched to '{layer.name}' View Layer")
        return {"FINISHED"}


############## LAYER MANAGER ##############
class UFRP_OP_ViewLayerAdd(Operator):
    """Add a new View Layer from highlighted, similar as 'NEW'"""
    bl_idname = "ufrp.view_layer_add"
    bl_label = "Add View Layer"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: Context):
        layer_index = props.get_layer_index()
        #TODO check si index correct, peut-etre interdir en dehors du nombre de View Layer dans la proprietee directement
        highlighted_layer = context.scene.view_layers[layer_index]
        context.scene.view_layers.new(highlighted_layer.name)
        props.set_layer_index(len(context.scene.view_layers) - 1)
        return {"FINISHED"}


class UFRP_OP_ViewLayerRemove(Operator):
    """Remove highlighted View Layer"""
    bl_idname = "ufrp.view_layer_remove"
    bl_label = "Remove View Layer"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: Context):
        cls.poll_message_set("Cannot remove last View Layer")
        return len(context.scene.view_layers) > 1

    def execute(self, context):
        layer_index = props.get_layer_index()
        highlighted_layer = context.scene.view_layers[layer_index]
        context.scene.view_layers.remove(highlighted_layer)
        props.set_layer_index(layer_index - 1)
        return {"FINISHED"}


class UFRP_OP_ViewLayerSwitch(Operator):
    """Switch to hightlighted View Layer"""
    bl_idname = "ufrp.switch_view_layer"
    bl_label = "Switch to View Layer"
    bl_options = {"REGISTER"}
    layer_name: bpy.props.StringProperty("View Layer name") # type: ignore

    def execute(self, context: Context):
        highlighted_layer = context.scene.view_layers.get(self.layer_name)
        context.window.view_layer = highlighted_layer
        switched_index = context.scene.view_layers.keys().index(self.layer_name)
        props.set_layer_index(switched_index)
        self.report({"INFO"}, f"Switched to '{self.layer_name}'")
        return {"FINISHED"}


class UFRP_OP_AllCopyProps(Operator):
    """Check/Uncheck all View Layers properties for copy"""
    bl_idname = "ufrp.all_passes"
    bl_label = "Check/Uncheck all"
    bl_options = {"REGISTER", "UNDO"}
    action: bpy.props.StringProperty(name="Action for all props") # type: ignore

    def execute(self, context: Context):
        passes = props.get_passes()
        for p in passes:
            match self.action:
                case "ON":
                    p.is_copy = True
                case "OFF":
                    p.is_copy = False
                case "TOGGLE":
                    p.is_copy = not p.is_copy
        return {"FINISHED"}


class UFRP_OP_ReloadPasses(Operator):
    """Reload View Layers copiable passes"""
    bl_idname = "ufrp.reload_passes"
    bl_label = "Reload passes to copy"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: Context):
        props.populate_prop_passes(context)
        return {"FINISHED"}


class UFRP_OP_CopyLayer(Operator):
    """Set highlighted View Layer's as copy source"""
    bl_idname = "ufrp.copy_layer_props"
    bl_label = "Copy properties and render settings"
    bl_options = {"REGISTER"}

    def execute(self, context: Context):
        layer_index = props.get_layer_index()
        highlighted_layer = context.scene.view_layers[layer_index]
        props.set_layer_source(highlighted_layer.name)
        self.report({"INFO"}, f"Set '{highlighted_layer.name}' as copy source")
        return {"FINISHED"}


class UFRP_OP_PasteLayer(Operator):
    """Paste View Layer's Layer properties and its Collection render settings from source"""
    bl_idname = "ufrp.paste_layer_props"
    bl_label = "Paste properties and render settings"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: Context):
        cls.poll_message_set("No properties to Copy/Paste, please check at least one option")
        if (    not props.is_copy_exclude() 
            and not props.is_copy_holdout() 
            and not props.is_copy_indirect_only() 
            and not props.is_copy_hide_viewport()
            and not props.is_copy_aovs()
            and not props.is_copy_passes()
            ): return False
        return True

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
    def copy_collection_prop(obj_src, obj_trg, prop_name: str):
        assert type(obj_src) == type(obj_trg)
        assert obj_src != obj_trg
        prop_src = getattr(obj_src, prop_name)
        prop_trg = getattr(obj_trg, prop_name)
        for coll_prop in prop_trg:
            prop_trg.remove(coll_prop)
        for coll_prop in prop_src:
            new_prop = prop_trg.add()
            filter = [p.identifier for p in new_prop.bl_rna.properties if props.is_prop_copyable(p)]
            __class__.copy_attrs(coll_prop, new_prop, filter)

    @staticmethod
    def copy_attrs(obj_src, obj_trg, filter=None):
        for attr_name in dir(obj_src):
            if filter is not None and attr_name not in filter:
                continue
            value = getattr(obj_src, attr_name)
            setattr(obj_trg, attr_name, value)

    def execute(self, context: Context):
        # assure passes prop
        passes = props.get_passes()
        if not passes:
            props.populate_prop_passes(context)
            passes = props.get_passes()
        passes_to_copy = [p.identifier for p in passes if p.is_copy]
        # checks
        if (not self.poll(context)
            or (props.is_copy_passes() and not passes_to_copy)):
            self.report({"WARNING"}, f"No properties to Copy/Paste, please check at least one option")
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
        if source_vl == target_vl:
            self.report({"WARNING"}, f"Target View Layer '{target_vl.name}' is already the source")
            return {"CANCELLED"}
        # copy/paste
        self.copy_layercollection_settings(source_vl.layer_collection, target_vl.layer_collection)
        if props.is_copy_passes() and passes_to_copy:
            self.copy_attrs(source_vl, target_vl, passes_to_copy)
            self.copy_attrs(source_vl.cycles, target_vl.cycles, passes_to_copy)
            self.copy_attrs(source_vl.eevee, target_vl.eevee, passes_to_copy)
        if props.is_copy_aovs():
            self.copy_collection_prop(source_vl, target_vl, "aovs")
        self.report({"INFO"}, f"Pasted properties from '{source_vl.name}' to '{target_vl.name}'")
        return {"FINISHED"}


class UFRP_OT_CopyToSelected(Operator):
    """Copy selected collection's render settings to all View Layers"""
    bl_idname = "ufrp.copy_to_selected"
    bl_label = "Copy to selected"
    bl_options = {"REGISTER", "UNDO"}

    def copy_layercollection_settings(self, source_lc: LayerCollection, target_lc: LayerCollection):
        """Recursively copy View Layer's Layer Collections settings"""
        if target_lc.collection in self.selected:
            target_lc.exclude = source_lc.exclude
            target_lc.holdout = source_lc.holdout
            target_lc.indirect_only = source_lc.indirect_only
            target_lc.hide_viewport = source_lc.hide_viewport
        for src_child, dst_child in zip(source_lc.children, target_lc.children):
            self.copy_layercollection_settings(src_child, dst_child)

    def execute(self, context: Context):
        self.selected = [c for c in context.selected_ids if c.id_type=="COLLECTION"]
        current_vl = context.view_layer
        vls = context.scene.view_layers
        for vl in vls:
            if current_vl == vl:
                continue
            self.copy_layercollection_settings(current_vl.layer_collection, vl.layer_collection)
        self.report({"INFO"}, f"Copied {len(self.selected)} Layer Collections settings to {len(vls)-1} View Layers")
        return {"FINISHED"}


def backup_comp_layers(context: Context):
    if not context.scene.node_tree:
        return None
    nodes = context.scene.node_tree.nodes
    old_nodes = [n for n in nodes if n.type=="R_LAYERS"]
    old_layers = [n.layer for n in old_nodes]
    return old_nodes, old_layers

def correct_comp_layers(backup: tuple[list, list]):
    if backup is None:
        return
    old_nodes, old_layers = backup
    for node, layer in zip(old_nodes, old_layers):
        node.layer = layer

class UFRP_OP_MoveLayer(Operator):
    """Move highlighted View Layer up/down"""
    bl_idname = "ufrp.move_layer"
    bl_label = "Move View Layer"
    bl_options = {"REGISTER", "UNDO"}
    direction: bpy.props.StringProperty() #type: ignore

    @classmethod
    def poll(cls, context: Context):
        cls.poll_message_set("Must have at least two View Layers")
        return len(context.scene.view_layers) > 1

    def execute(self, context: Context):
        backup = backup_comp_layers(context)
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
        correct_comp_layers(backup)
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
        #TODO update index to keep highlighted view layer
        backup = backup_comp_layers(context)
        layers = context.scene.view_layers
        sorted_layers = sorted(layers, key=lambda vl: self.natural_sort_key(vl.name))
        if self.is_reverse:
            sorted_layers.reverse()
        layer_index = props.get_layer_index()
        current_layer = layers[layer_index]
        for to_i, layer in enumerate(sorted_layers):
            current_i = [l for l in layers].index(layer)
            layers.move(current_i, to_i)
            if layer == current_layer:
                props.set_layer_index(to_i)
        correct_comp_layers(backup)
        return {"FINISHED"}