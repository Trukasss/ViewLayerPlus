import bpy.utils.previews
from pathlib import Path


_icons = {}


def register():
    global _icons
    _icons = bpy.utils.previews.new()
    icons_dir = Path(__file__).parent / "images"
    _icons.load(
        "addon", 
        str(icons_dir / "icon_addon.png"), 
        "IMAGE")
    _icons.load(
        "checked", 
        str(icons_dir / "icon_checked.png"), 
        "IMAGE")
    _icons.load(
        "unchecked", 
        str(icons_dir / "icon_unchecked.png"), 
        "IMAGE")
    _icons.load(
        "selected", 
        str(icons_dir / "icon_selected.png"), 
        "IMAGE")
    _icons.load(
        "switch", 
        str(icons_dir / "icon_switch.png"), 
        "IMAGE")
    _icons.load(
        "unmuted", 
        str(icons_dir / "icon_unmuted.png"), 
        "IMAGE")


def unregister():
    bpy.utils.previews.remove(_icons)


def get_addon_id():
    return _icons["addon"].icon_id


def get_checked_id():
    return _icons["checked"].icon_id


def get_unchecked_id():
    return _icons["unchecked"].icon_id


def get_selected_id():
    return _icons["selected"].icon_id


def get_switch_id():
    return _icons["switch"].icon_id


def get_unmuted_id():
    return _icons["unmuted"].icon_id