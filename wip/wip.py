import bpy

# -------------------------------------------------
# Store one index
# -------------------------------------------------
class MySelectedIndex(bpy.types.PropertyGroup):
    index: bpy.props.IntProperty()


# -------------------------------------------------
# Utility functions
# -------------------------------------------------
def get_selected_indices(scene):
    return {sel.index for sel in scene.my_items_selected}

def set_selected_indices(scene, indices):
    scene.my_items_selected.clear()
    for i in indices:
        sel = scene.my_items_selected.add()
        sel.index = i


# -------------------------------------------------
# Custom item
# -------------------------------------------------
class MyItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()


# -------------------------------------------------
# Operator
# -------------------------------------------------
class MYLIST_OT_select(bpy.types.Operator):
    """Select item in UIList (supports shift/ctrl)"""
    bl_idname = "mylist.select"
    bl_label = "Select Item"

    index: bpy.props.IntProperty()

    def invoke(self, context, event):
        scene = context.scene
        items = scene.my_items
        selected = get_selected_indices(scene)

        if event.shift and selected:
            # Range select
            last = scene.my_last_index if scene.my_last_index >= 0 else self.index
            low, high = sorted((last, self.index))
            new_sel = set(range(low, high + 1))
            set_selected_indices(scene, new_sel)
        elif event.ctrl:
            # Toggle selection
            if self.index in selected:
                selected.remove(self.index)
            else:
                selected.add(self.index)
            set_selected_indices(scene, selected)
        else:
            # Single select
            set_selected_indices(scene, {self.index})

        scene.my_last_index = self.index
        return {"FINISHED"}


# -------------------------------------------------
# Custom UIList
# -------------------------------------------------
class MY_UL_List(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        scene = context.scene
        selected = get_selected_indices(scene)
        row = layout.row()
        op = row.operator("mylist.select", text=item.name, depress=index in selected)
        op.index = index


# -------------------------------------------------
# Panel
# -------------------------------------------------
class MY_PT_Panel(bpy.types.Panel):
    bl_label = "Multi-Select UIList Demo"
    bl_idname = "MY_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Demo"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.template_list("MY_UL_List", "", scene, "my_items", scene, "my_items_index")
        layout.label(text=f"Selected: {sorted(get_selected_indices(scene))}")


# -------------------------------------------------
# Register
# -------------------------------------------------
classes = (
    MySelectedIndex,
    MyItem,
    MYLIST_OT_select,
    MY_UL_List,
    MY_PT_Panel,
)

def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.Scene.my_items = bpy.props.CollectionProperty(type=MyItem)
    bpy.types.Scene.my_items_index = bpy.props.IntProperty()
    bpy.types.Scene.my_items_selected = bpy.props.CollectionProperty(type=MySelectedIndex)
    bpy.types.Scene.my_last_index = bpy.props.IntProperty(default=-1)

    # Add demo items
    if not bpy.context.scene.my_items:
        for i in range(10):
            it = bpy.context.scene.my_items.add()
            it.name = f"Item {i}"


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
    del bpy.types.Scene.my_items
    del bpy.types.Scene.my_items_index
    del bpy.types.Scene.my_items_selected
    del bpy.types.Scene.my_last_index


if __name__ == "__main__":
    register()
