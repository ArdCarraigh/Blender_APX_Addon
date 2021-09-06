# -*- coding: utf-8 -*-
# __init__.py

bl_info = {
    "name": "APX Importer (.apx)",
    "author": "Ard Carraigh",
    "version": (1, 0),
    "blender": (2, 92, 0),
    "location": "File > Import > APX (.apx)",
    "description": "Import an .apx mesh",
    "wiki_url": "https://github.com/ArdCarraigh/Blender_APX_Importer",
    "tracker_url": "https://github.com/ArdCarraigh/Blender_APX_Importer/issues",
    "support": "COMMUNITY",
    "category": "Import-Export",
}

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
from io_import_apx import clothing
from io_import_apx import hairworks
from io_import_apx.clothing import read_clothing
from io_import_apx.hairworks import read_hairworks


def read_apx(context, filepath, rm_db, use_mat, rotate_180, scale_down, minimal_armature):
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
        read_clothing(context, filepath, rm_db, use_mat, rotate_180, minimal_armature)

    # If Hairworks type
    if type == 'hair':
        read_hairworks(context, filepath, rotate_180, scale_down, minimal_armature)

    # Unselect everything
    bpy.context.view_layer.objects.active = None
    bpy.ops.object.select_all(False)

    return {'FINISHED'}

class ImportApx(Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "import_test.apx"  # important since its how bpy.ops.import_test.some_data is constructed
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
        description="Remove doubles of the imported meshes",
        default=True,
    )
    
    use_mat: BoolProperty(
        name="Prevent Material Duplication",
        description="Use existing materials from the scene if their name is identical to the one of your mesh",
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

    def draw(self, context):
        layout = self.layout
        
        sections = ["General", "Clothing", "Hairworks"]
        
        section_options = {
            "General" : ["rotate_180", "minimal_armature"], 
            "Clothing" : ["rm_db", "use_mat"], 
            "Hairworks" : ["scale_down"]
        }
        
        section_icons = {
            "General" : "WORLD", "Clothing" : "MESH_DATA", "Hairworks" : "MESH_DATA"
        }
        
        for section in sections:
            row = layout.row()
            box = row.box()
            box.label(text=section, icon=section_icons[section])
            for prop in section_options[section]:
                box.prop(self, prop)
                
    def execute(self, context):
        return read_apx(context, self.filepath, self.rm_db, self.use_mat, self.rotate_180, self.scale_down, self.minimal_armature)


# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(ImportApx.bl_idname, text="APX (.apx)")


def register():
    bpy.utils.register_class(ImportApx)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportApx)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()
    
    # test call
    bpy.ops.import_test.apx('INVOKE_DEFAULT')
