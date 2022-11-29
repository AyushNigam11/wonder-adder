bl_info = {
    "name": "Anime By Me",
    "author": "AnimeByMe",
    "blender": (2, 80, 3),
    "location": "Menu > Submenus",
    "description": "An add-on to import models",
    "warning": "",
    "wiki_url": "",
    "category": "UI"
}

import os
from functools import partial
import bpy
from bpy.utils import previews
from bpy_extras.io_utils import ImportHelper

from bpy.props import (BoolProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       CollectionProperty
                       )


imageloader = None


class ImageLoader():
    """ImageLoader to wrap previews into a singleton.
    Heavily inspired by Embark tools - thanks!
    """

    def __init__(self):
        self.preview_handler = previews.new()

    def blender_icon(self, icon="NONE"):
        if icon.lower().endswith(".png"):
            icon = self.load_icon(icon)
        return self.preview_handler[icon].icon_id

    def load_icon(self, filename="image.png"):
        script_dir = os.path.dirname(__file__)
        icon_dir = os.path.join(script_dir, "icons")
        filepath = os.path.join(icon_dir, filename)
        name = os.path.splitext(filename)[0]
        self.preview_handler.load(name, filepath, 'IMAGE')
        return name

    def unregister(self):
        previews.remove(self.preview_handler)
        self.preview_handler = None


def add_menu(name, icon_value=0, parent_name="TOPBAR_MT_editor_menus"):
    """Adds a menu class and adds it to any menu.

    Args:
        name (str): Name of the menu
        parent_name (str, optional): What Blender menu should this be added into. Defaults to "TOPBAR_MT_editor_menus".
    """

    def draw(self, context):
        pass

    def menu_draw(self, context):
        self.layout.menu(my_menu_class.bl_idname, icon_value=icon_value)

    bl_idname = "MENU_MT_{0}".format(name.replace(" ", ""))
    full_parent_name = "bpy.types.{0}".format(parent_name)

    parent = eval(full_parent_name)

    my_menu_class = type(
        "DynamicMenu{0}".format(name),
        (bpy.types.Menu,),
        {
            "bl_idname": bl_idname,
            "bl_label": name,
            "draw": draw
        })

    bpy.utils.register_class(my_menu_class)
    parent.append(menu_draw)

    return bl_idname


def add_operator(name, callback, icon_value=0, tooltip='Dynamic Operator', parent_name="TOPBAR_MT_editor_menus"):
    """Adds a dummy operator to be able to add your callback into any menu.

    Args:
        name (str): Name of the menu entry
        callback (function): What method do you want to callback to from here
        parent_name (str, optional): What Blender menu should this be added into. Defaults to "TOPBAR_MT_editor_menus".
    """

    def execute(self, context):
        my_operator_class.func()
        return {"FINISHED"}

    def operatator_draw(self, context):
        self.layout.operator(my_operator_class.bl_idname, icon_value=icon_value)

    bl_idname = "menuentry.{0}".format(name.replace(" ", "").lower())
    full_parent_name = "bpy.types.{0}".format(parent_name)
    parent = eval(full_parent_name)
    my_operator_class = type(
        "DynamicOperator{0}".format(name),
        (bpy.types.Operator,),
        {
            "bl_idname": bl_idname,
            "bl_label": name,
            "func": callback,
            "execute": execute,
            "__doc__": tooltip
        })
    bpy.utils.register_class(my_operator_class)
    parent.append(operatator_draw)

    return bl_idname


def add_separator(parent_name="TOPBAR_MT_editor_menus"):
    """Adds a separator to the menu identified in parent_name

    Args:
        parent_name (str, optional): What Blender menu should this be added into. Defaults to "TOPBAR_MT_editor_menus".
    """

    def draw_separator(self, context):
        self.layout.row().separator()

    full_parent_name = "bpy.types.{0}".format(parent_name)
    parent = eval(full_parent_name)
    parent.append(draw_separator)


def build_menus(menu_dict, parent_name="TOPBAR_MT_editor_menus"):
    """A simple recursive menu builder without too much logic or extra data.

    Args:
        menu_dict (dict): A dictionary with entries for submenus and operators.
        parent_name (str, optional): What Blender menu should this be nested into. Defaults to "TOPBAR_MT_editor_menus".
    """

    for key in menu_dict:
        if key.count("-") == len(key):
            add_separator(parent_name)
        entry = menu_dict[key]
        icon = 0
        tooltip = ""
        if "icon" in entry:
            icon = imageloader.blender_icon(entry["icon"])
        if "tooltip" in entry:
            tooltip = entry["tooltip"]
        if "menu" in entry:
            bl_idname = add_menu(
                name=key,
                icon_value=icon,
                parent_name=parent_name)
            build_menus(entry["menu"], bl_idname)
        elif "operator" in entry:
            add_operator(
                name=key,
                callback=entry["operator"],
                icon_value=icon,
                tooltip=tooltip,
                parent_name=parent_name)


def an_example():
    """A simple example method to call in our example menu.
    """

    print("An Example!")


def an_example_with(parameter):
    """A simple example method with a parameter to showcase
    how to add it in our menu.

    Args:
        parameter (str, int, float): We will call print() on this.
    """

    print(parameter)


menu_hierarchy = {
    "Anime By Me": {
        "icon": "heart.png",
        "menu": {
            "Import Local Models": {
                "icon": "arrow.png",
                "tooltip": "Import and Use your local models from here",
                "operator": an_example},
            "Upload Models": {
                "icon": "arrowBlue.png",
                "tooltip": "Showcase your 3D skills : Upload your work here",
                "operator": partial(an_example_with, "This works!")},
            "----": {},
            "Our Models": {
            "tooltip": "Just a glance, Find our cool models at slide navigation",
                "menu": {
                     "Vehicles": {
                        "operator": partial(an_example_with, "This works too!"),
                        "tooltip": "Import cool cars and more from here"},
                     "Architecture": {
                        "operator": partial(an_example_with, "This works too!"),
                        "tooltip": "Cool skyscrapers thats all you need"},
                     "Character": {
                        "operator": partial(an_example_with, "This works too!"),
                        "tooltip": "Import your Avatar from here"},
                      "Aircraft": {
                        "operator": partial(an_example_with, "This works too!"),
                        "tooltip": "Aviation lovers we have something for you"},
                      "Furniture": {
                        "operator": partial(an_example_with, "This works too!"),
                        "tooltip": "Home and Decor, Thats how life is balance. Right!"},
                      "Electronic": {
                        "operator": partial(an_example_with, "This works too!"),
                        "tooltip": "Iphone - Samsung, We have all for you"},
                       "Plants": {
                        "operator": partial(an_example_with, "This works too!"),
                        "tooltip": "Far from toxicity, celebrate nature with our models"}
                        }
                     
                    },
            "Help": {
                "menu": {
                     "Related to Models": {
                        "operator": partial(an_example_with, "This works too!"),
                        "tooltip": "We would love to hear from you"},
                     "Request New Models": {
                        "operator": partial(an_example_with, "This works too!"),
                        "tooltip": "Let us know about your model needs"}
                        }
                     
                    },
                   
             
                     
                    }
                }
            }

class ImportMultipleObjs(bpy.types.Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "import_scene.multiple_objs"
    bl_label = "Import multiple OBJ's"
    bl_options = {'PRESET', 'UNDO'}

    # ImportHelper mixin class uses this
    filename_ext = ".obj"

    filter_glob: StringProperty(
        default="*.obj",
        options={'HIDDEN'},
    )

    # Selected files
    files: CollectionProperty(type=bpy.types.PropertyGroup)

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    edges_setting: BoolProperty(
        name="Lines",
        description="Import lines and faces with 2 verts as edge",
        default=True,
    )
    smooth_groups_setting: BoolProperty(
        name="Smooth Groups",
        description="Surround smooth groups by sharp edges",
        default=True,
    )

    split_objects_setting: BoolProperty(
        name="Object",
        description="Import OBJ Objects into Blender Objects",
        default=True,
    )
    split_groups_setting: BoolProperty(
        name="Group",
        description="Import OBJ Groups into Blender Objects",
        default=True,
    )

    groups_as_vgroups_setting: BoolProperty(
        name="Poly Groups",
        description="Import OBJ groups as vertex groups",
        default=False,
    )

    image_search_setting: BoolProperty(
        name="Image Search",
        description="Search subdirs for any associated images "
                    "(Warning, may be slow)",
        default=False
    )

    split_mode_setting: EnumProperty(
        name="Split",
        items=(('ON', "Split", "Split geometry, omits unused verts"),
               ('OFF', "Keep Vert Order", "Keep vertex order from file"),),
    )

    clamp_size_setting: FloatProperty(
        name="Clamp Size",
        description="Clamp bounds under this value (zero to disable)",
        min=0.0, max=1000.0,
        soft_min=0.0, soft_max=1000.0,
        default=0.0,
    )

    axis_forward_setting: EnumProperty(
        name="Forward",
        items=(('X', "X Forward", ""),
               ('Y', "Y Forward", ""),
               ('Z', "Z Forward", ""),
               ('-X', "-X Forward", ""),
               ('-Y', "-Y Forward", ""),
               ('-Z', "-Z Forward", ""),
               ),
        default='-Z',
    )

    axis_up_setting: EnumProperty(
        name="Up",
        items=(('X', "X Up", ""),
               ('Y', "Y Up", ""),
               ('Z', "Z Up", ""),
               ('-X', "-X Up", ""),
               ('-Y', "-Y Up", ""),
               ('-Z', "-Z Up", ""),
               ),
        default='Y',
    )

    scale_setting: FloatProperty(
        name="Size",
        description="Scale objects",
        min=0.0, max=1000.0,
        soft_min=0.0, soft_max=1000.0,
        default=1,
    )

    center_origin: BoolProperty(
        name="Center Origin",
        default=True
    )

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.prop(self, "smooth_groups_setting")
        row.prop(self, "edges_setting")

        box = layout.box()
        row = box.row()
        row.prop(self, "split_mode_setting", expand=True)

        row = box.row()
        if self.split_mode_setting == 'ON':
            row.label(text="Split by:")
            row.prop(self, "split_objects_setting")
            row.prop(self, "split_groups_setting")
        else:
            row.prop(self, "groups_as_vgroups_setting")

        row = layout.split()
        row.prop(self, "clamp_size_setting")
        layout.prop(self, "axis_forward_setting")
        layout.prop(self, "axis_up_setting")

        layout.prop(self, "image_search_setting")

        row = layout.split()
        row.prop(self, "scale_setting")
        row.prop(self, "center_origin")

    def execute(self, context):

        # get the folder
        folder = (os.path.dirname(self.filepath))

        # iterate through the selected files
        for j, i in enumerate(self.files):

            # generate full path to file
            path_to_file = (os.path.join(folder, i.name))

            # call obj operator and assign ui values
            bpy.ops.import_scene.obj(filepath=path_to_file,
                                     axis_forward=self.axis_forward_setting,
                                     axis_up=self.axis_up_setting,
                                     use_edges=self.edges_setting,
                                     use_smooth_groups=self.smooth_groups_setting,
                                     use_split_objects=self.split_objects_setting,
                                     use_split_groups=self.split_groups_setting,
                                     use_groups_as_vgroups=self.groups_as_vgroups_setting,
                                     use_image_search=self.image_search_setting,
                                     split_mode=self.split_mode_setting,
                                     global_clight_size=self.clamp_size_setting)

            if self.center_origin:
                bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
            bpy.ops.transform.resize(value=(self.scale_setting, self.scale_setting, self.scale_setting), constraint_axis=(False, False, False))
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        return {'FINISHED'}
   
def menu_func_import(self, context):
    self.layout.operator(ImportMultipleObjs.bl_idname, text="Import our models")


class MainPanel(bpy.types.Panel):
    bl_label = "Object Adder"
    bl_idname = "PT_MainPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Object Adder'
   
    def draw(self, context):
        layout = self.layout
        layout.scale_y = 1.2
       
        row = layout.row()
        row.label(text= "Add an object", icon= 'OBJECT_ORIGIN')
        row = layout.row()
        row.operator("mesh.primitive_cube_add", icon= 'CUBE', text= "Cube")
        row.operator("mesh.primitive_uv_sphere_add", icon= 'SPHERE', text= "Sphere")
        row.operator("mesh.primitive_monkey_add", icon= 'MESH_MONKEY', text= "Suzanne")
        row = layout.row()
        row.operator("curve.primitive_bezier_curve_add", icon= 'CURVE_BEZCURVE', text= "Bezier Curve")
        row.operator("curve.primitive_bezier_circle_add", icon= 'CURVE_BEZCIRCLE', text= "Bezier Circle")
       
       
        row = layout.row()
        row.operator("object.text_add", icon= 'FILE_FONT', text= "Add Font")
        row = layout.row()
 
 
    #This is Panel A - The Scale Sub Panel (Child of MainPanel)
class PanelA(bpy.types.Panel):
    bl_label = "Scale"
    bl_idname = "PT_PanelA"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Object Adder'
    bl_parent_id = 'PT_MainPanel'
    bl_options = {'DEFAULT_CLOSED'}
   
    def draw(self, context):
        layout = self.layout
        obj = context.object
       
        row = layout.row()
        row.label(text= "Select an option to scale your", icon= 'FONT_DATA')
        row = layout.row()
        row.label(text= "      object.")
        row = layout.row()
        row.operator("transform.resize")
        row = layout.row()
        layout.scale_y = 1.2
       
        col = layout.column()
        col.prop(obj, "scale")
             
 
    #This is Panel B - The Specials Sub Panel (Child of MainPanel)
class PanelB(bpy.types.Panel):
    bl_label = "Specials"
    bl_idname = "PT_PanelB"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Object Adder'
    bl_parent_id = 'PT_MainPanel'
    bl_options = {'DEFAULT_CLOSED'}
   
    def draw(self, context):
        layout = self.layout
       
        row = layout.row()
        row.label(text= "Select a Special Option", icon= 'COLOR_BLUE')
        row = layout.row()
        row.operator("object.shade_smooth", icon= 'MOD_SMOOTH', text= "Set Smooth Shading")
        row.operator("object.subdivision_set", icon= 'MOD_SUBSURF', text= "Add Subsurf")
        row = layout.row()
        row.operator("object.modifier_add", icon= 'MODIFIER')





def register():
    global imageloader
    if imageloader is None:
        imageloader = ImageLoader()
    build_menus(menu_hierarchy)
    bpy.utils.register_class(ImportMultipleObjs)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.utils.register_class(MainPanel)
    bpy.utils.register_class(PanelA)
    bpy.utils.register_class(PanelB)

def unregister():
    global imageloader
    if imageloader is not None:
        imageloader.unregister()
        imageloader = None
    bpy.utils.unregister_class(ImportMultipleObjs)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.utils.unregister_class(MainPanel)
    bpy.utils.unregister_class(PanelA)
    bpy.utils.unregister_class(PanelB)

if __name__ == "__main__":
    register()