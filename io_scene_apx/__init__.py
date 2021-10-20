# -*- coding: utf-8 -*-
# __init__.py

bl_info = {
    "name": "APX Importer/Exporter (.apx)",
    "author": "Ard Carraigh & Aaron Thompson",
    "version": (1, 0),
    "blender": (2, 92, 0),
    "location": "File > Import-Export",
    "description": "Import and export .apx meshes",
    "wiki_url": "https://github.com/ArdCarraigh/Blender_APX_Importer",
    "tracker_url": "https://github.com/ArdCarraigh/Blender_APX_Importer/issues",
    "support": "COMMUNITY",
    "category": "Import-Export",
}

import bpy
from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy_extras.object_utils import AddObjectHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatProperty, FloatVectorProperty, IntProperty
from bpy.types import Operator
from io_scene_apx.importer import import_clothing
from io_scene_apx.importer import import_hairworks
from io_scene_apx.importer.import_clothing import read_clothing
from io_scene_apx.importer.import_hairworks import read_hairworks
from io_scene_apx.exporter import export_hairworks
from io_scene_apx.exporter.export_hairworks import write_hairworks
from io_scene_apx.tools import add_sphere
from io_scene_apx.tools.add_sphere import add_sphere
from io_scene_apx.tools import add_connection
from io_scene_apx.tools.add_connection import add_connection
from io_scene_apx.tools import add_pin
from io_scene_apx.tools.add_pin import add_pin
from io_scene_apx.tools import shape_hair
from io_scene_apx.tools.shape_hair import shape_hair


def read_apx(context, filepath, rm_db, use_mat, rotate_180, scale_down, minimal_armature, rm_ph_me):
    print("running read_apx...")
    
    # Should work from all modes
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
    bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
    with open(filepath, 'r', encoding='utf-8') as file:

        # Get the type of .apx we have
        for line in file:
            if 'className=' in line:
                if 'ClothingAssetParameters' in line:
                    type = 'cloth'
                if 'HairWorksInfo' in line:
                    type = 'hair'
                break

    # If PhysX Clothing type
    if type == 'cloth':
        read_clothing(context, filepath, rm_db, use_mat, rotate_180, minimal_armature, rm_ph_me)

    # If Hairworks type
    if type == 'hair':
        read_hairworks(context, filepath, rotate_180, scale_down, minimal_armature)

    # Unselect everything
    bpy.context.view_layer.objects.active = None
    bpy.ops.object.select_all(False)

    return {'FINISHED'}

class ImportApx(Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "import.apx"  # important since its how bpy.ops.import.apx is constructed
    bl_label = "Import APX"

    # ImportHelper mixin class uses this
    filename_ext = ".apx"

    filter_glob: StringProperty(
        default="*.apx",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    
    rm_db: BoolProperty(
        name="Remove Doubles",
        description="Remove double vertices of the imported meshes",
        default=True,
    )
    
    use_mat: BoolProperty(
        name="Prevent Material Duplication",
        description="Use existing materials from the scene if their name is identical to the ones of your mesh",
        default=True,
    )
    
    rotate_180: BoolProperty(
        name="Rotate 180°",
        description="Rotate both the mesh and the armature on the Z-axis by 180°",
        default=True
    )
    
    scale_down: BoolProperty(
        name="Scale Down x100",
        description="Scale both the mesh and the armature by 0.01",
        default=True
    )
    
    minimal_armature: BoolProperty(
        name="Minimal Armature",
        description="Limit the bone importation to those used to weight the meshes",
        default=False
    )
    
    rm_ph_me: BoolProperty(
        name="Remove Physical Meshes",
        description="Remove the physical meshes after transfer of vertex colors to graphical meshes",
        default=True
    )

    def draw(self, context):
        layout = self.layout
        
        sections = ["General", "Clothing", "Hairworks"]
        
        section_options = {
            "General" : ["rotate_180", "minimal_armature"], 
            "Clothing" : ["rm_db", "use_mat", "rm_ph_me"], 
            "Hairworks" : ["scale_down"]
        }
        
        section_icons = {
            "General" : "WORLD", "Clothing" : "MATCLOTH", "Hairworks" : "HAIR_DATA"
        }
        
        for section in sections:
            row = layout.row()
            box = row.box()
            box.label(text=section, icon=section_icons[section])
            for prop in section_options[section]:
                box.prop(self, prop)
                
    def execute(self, context):
        return read_apx(context, self.filepath, self.rm_db, self.use_mat, self.rotate_180, self.scale_down, self.minimal_armature, self.rm_ph_me)


def write_apx(context, filepath, type, resample_value, spline):
    print("running read_apx...")
    
    # Should work from all modes
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
    bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
    
    if type == 'Hairworks':
        write_hairworks(context, filepath, resample_value, spline)
    
    return {'FINISHED'}

class ExportApx(Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "export.apx"  # important since its how bpy.ops.export.apx is constructed
    bl_label = "Export APX"

    # ExportHelper mixin class uses this
    filename_ext = ".apx"

    filter_glob: StringProperty(
        default="*.apx",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.

    type: EnumProperty(
        name="APX Type",
        description="Choose between Clothing and Hairworks",
        items=(
            ('Hairworks', "Hairworks", "Write a hairworks .apx"),
            ('Clothing', "Clothing", "Write a clothing .apx"),
        ),
        default='Hairworks',
    )
    
    resample_value: IntProperty(
        name = "Resample",
        default = 4,
        description = "Set the number of vertices used to resample. Root and tip vertices are included",
        max = 99,
        min = 2,
    )
    
    spline: IntProperty(
        name = "Spline Multiplier",
        default = 4,
        description = "Set the spline multiplier of the hairworks asset",
        max = 4,
        min = 1,
    )

    def draw(self, context):
        layout = self.layout

        sections = ["General", "Hairworks"]

        section_options = {
            "General": ["type"],
            "Hairworks": ["resample_value", "spline"]
        }

        section_icons = {
            "General": "WORLD", "Hairworks": "HAIR_DATA"
        }

        for section in sections:
            row = layout.row()
            box = row.box()
            box.label(text=section, icon=section_icons[section])
            for prop in section_options[section]:
                box.prop(self, prop)

    def execute(self, context):
        return write_apx(context, self.filepath, self.type, self.resample_value, self.spline)
    
      
class AddCollisionSphere(Operator, AddObjectHelper):
    """Create a new Collision Sphere"""
    bl_idname = "physx.add_collision_sphere"
    bl_label = "Add Collision Sphere"
    bl_options = {'REGISTER', 'UNDO'}

    radius: FloatProperty(
        name="Radius",
        default = 0.15,
        description="Set the radius of the sphere",
    )

    def execute(self, context):
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
        add_sphere(context, self.radius)
        return {'FINISHED'}
    
class AddSphereConnection(Operator):
    """Create a new Connection"""
    bl_idname = "physx.add_sphere_connection"
    bl_label = "Add Sphere Connection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
        add_connection(context)
        return {'FINISHED'}
    
class AddPinSphere(Operator, AddObjectHelper):
    """Create a new Pin Sphere"""
    bl_idname = "physx.add_pin_sphere"
    bl_label = "Add Pin Sphere"
    bl_options = {'REGISTER', 'UNDO'}

    radius: FloatProperty(
        name="Radius",
        default = 0.15,
        description="Set the radius of the sphere",
    )

    def execute(self, context):
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
        add_pin(context, self.radius)
        return {'FINISHED'}
    
class ShapeHair(Operator):
    """Shape Hair from Curves"""
    bl_idname = "physx.shape_hair"
    bl_label = "Shape Hair from Curves"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
        shape_hair(context)
        return {'FINISHED'}

    
class PhysXMenu(bpy.types.Menu):
    bl_label = "PhysX"
    bl_idname = "VIEW3D_MT_object_PhysX_menu"

    def draw(self, context):
        layout = self.layout

        layout.operator("add_sphere_button", text = "Add Collision Capsule (Clothing)", icon='MESH_CAPSULE')
        layout.operator(AddCollisionSphere.bl_idname, text = "Add Collision Sphere", icon='MESH_UVSPHERE')
        layout.operator(AddSphereConnection.bl_idname, text = "Add Sphere Connection", icon='MESH_CAPSULE')
        layout.operator(AddPinSphere.bl_idname, text = "Add Pin Sphere (Hairworks)", icon='MESH_UVSPHERE')
        layout.operator(ShapeHair.bl_idname, text = "Shape Hair from Curves (Hairworks)", icon='HAIR')


# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(ImportApx.bl_idname, text="APX (.apx)")

def menu_func_export(self, context):
    self.layout.operator(ExportApx.bl_idname, text="APX (.apx)")
    
def draw_item(self, context):
    layout = self.layout
    layout.separator()
    layout.menu(PhysXMenu.bl_idname)

def register():
    bpy.utils.register_class(ImportApx)
    bpy.utils.register_class(ExportApx)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
    
    bpy.utils.register_class(AddCollisionSphere)
    bpy.utils.register_class(AddSphereConnection)
    bpy.utils.register_class(AddPinSphere)
    bpy.utils.register_class(ShapeHair)
    
    bpy.utils.register_class(PhysXMenu)
    bpy.types.VIEW3D_MT_object.append(draw_item)

def unregister():
    bpy.utils.unregister_class(ImportApx)
    bpy.utils.unregister_class(ExportApx)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    
    bpy.utils.unregister_class(AddCollisionSphere)
    bpy.utils.unregister_class(AddSphereConnection)
    bpy.utils.unregister_class(AddPinSphere)
    bpy.utils.unregister_class(ShapeHair)
    
    bpy.utils.unregister_class(PhysXMenu)
    bpy.types.VIEW3D_MT_object.remove(draw_item)


if __name__ == "__main__":
    register()
    
    # test call
    bpy.ops.import_test.apx('INVOKE_DEFAULT')
