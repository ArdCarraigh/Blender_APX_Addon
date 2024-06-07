# -*- coding: utf-8 -*-
# __init__.py

bl_info = {
    "name": "APX Importer/Exporter (.apx/.apb)",
    "author": "Ard Carraigh & Aaron Thompson",
    "version": (5, 4),
    "blender": (4, 1, 1),
    "location": "File > Import-Export",
    "description": "Import and export .apx meshes",
    "doc_url": "https://github.com/ArdCarraigh/Blender_APX_Addon",
    "tracker_url": "https://github.com/ArdCarraigh/Blender_APX_Addon/issues",
    "support": "COMMUNITY",
    "category": "Import-Export",
}

import bpy
import os.path
from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, PointerProperty, IntProperty
from bpy.types import Operator, PropertyGroup, AddonPreferences
from io_mesh_apx.importer.import_clothing import read_clothing
from io_mesh_apx.importer.import_hairworks import read_hairworks
from io_mesh_apx.importer.import_destruction import read_destruction
from io_mesh_apx.exporter.export_hairworks import write_hairworks
from io_mesh_apx.exporter.export_clothing import write_clothing
from io_mesh_apx.ui.main_panel import PROPS_Main_Panel, CLASSES_Main_Panel
from io_mesh_apx.ui.collision_panel import PROPS_Collision_Panel, CLASSES_Collision_Panel
from io_mesh_apx.ui.painting_panel import PROPS_Painting_Panel, CLASSES_Painting_Panel
from io_mesh_apx.ui.cloth_mat_panel import PROPS_ClothMaterial_Panel, CLASSES_ClothMaterial_Panel
from io_mesh_apx.ui.cloth_sim_panel import PROPS_ClothSimulation_Panel, CLASSES_ClothSimulation_Panel
from io_mesh_apx.ui.hair_pin_panel import PROPS_HairPin_Panel, CLASSES_HairPin_Panel
from io_mesh_apx.ui.hair_tools_panel import PROPS_HairTools_Panel, CLASSES_HairTools_Panel
from io_mesh_apx.ui.hair_mat_panel import PROPS_HairMaterial_Panel, CLASSES_HairMaterial_Panel
from io_mesh_apx.utils import getNumberHairVerts, GetCollection

class APXAddonPreferences(AddonPreferences):
    bl_idname = __package__

    apex_sdk_cli: StringProperty(
        name="Apex SDK 1.3.0 CLI",
        subtype='DIR_PATH',
        default="D:/Witcher3Modding/ApexCloth/1.3.1/bin/vc10win32-PhysX_3.3/ParamToolPROFILE.exe",
        description="Path to the Apex SDK Command-Line Interface .exe"
    )

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "apex_sdk_cli")

class ImportApx(Operator, ImportHelper):
    """Load a APX file"""
    bl_idname = "import.apx"  # important since its how bpy.ops.import.apx is constructed
    bl_label = "Import APX"

    # ImportHelper mixin class uses this
    filename_ext = ".apx"

    filter_glob: StringProperty(
        default="*.apx;*.apb",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    
    rotate_180: BoolProperty(
        name="Rotate 180°",
        description="Rotate both the mesh and the armature on the Z-axis by 180°",
        default=True
    )
    
    rm_ph_me: BoolProperty(
        name="Remove Physical Meshes",
        description="Remove the physical meshes after transfer of vertex colors to graphical meshes",
        default=True
    )

    def draw(self, context):
        layout = self.layout
        
        sections = ["General", "Clothing"]
        
        section_options = {
            "General" : ["rotate_180"], 
            "Clothing" : ["rm_ph_me"], 
        }
        
        section_icons = {
            "General" : "WORLD", "Clothing" : "MATCLOTH"
        }
        
        for section in sections:
            row = layout.row()
            box = row.box()
            box.label(text=section, icon=section_icons[section])
            for prop in section_options[section]:
                box.prop(self, prop)
                
    def execute(self, context):
        # Should work from all modes
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
        
        # Convert to .apx if necessary
        if os.path.splitext(os.path.basename(self.filepath))[1] == ".apb":
            apex_path = bpy.context.preferences.addons[__package__].preferences.apex_sdk_cli
            if os.path.exists(apex_path):
                import subprocess
                command = [apex_path, "-s", "apx", self.filepath]
                subprocess.run(command)
                self.filepath = self.filepath[:-1] + "x"
            else:
                log.critical('Apex SDK CLI .exe not found.')
                return
        
        with open(self.filepath, 'r', encoding='utf-8') as file:

            # Get the type of .apx we have
            for line in file:
                if 'className=' in line:
                    if 'ClothingAssetParameters' in line:
                        read_clothing(context, self.filepath, self.rotate_180, self.rm_ph_me)
                    elif 'HairWorksInfo' in line:
                        read_hairworks(context, self.filepath, self.rotate_180)
                    elif 'DestructibleAssetParameters' in line:
                        read_destruction(context, self.filepath, self.rotate_180)
                    break
                
        # Unselect everything
        bpy.context.view_layer.objects.active = None
        bpy.ops.object.select_all(False)

        return {'FINISHED'}

class ExportApx(Operator, ExportHelper):
    """Write a APX file"""
    bl_idname = "export.apx"  # important since its how bpy.ops.export.apx is constructed
    bl_label = "Export APX"

    # ExportHelper mixin class uses this
    filename_ext = ".apx"

    filter_glob: StringProperty(
        default="*.apx",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )
     
    resample_value: IntProperty(
        name = "Resample",
        default = 4,
        description = "Set the number of vertices used to resample. Root and tip vertices are included",
        max = 99,
        min = 2,
    )
    
    n_verts_check = False

    def draw(self, context):
        layout = self.layout
        main_coll = GetCollection(make_active=False)
        if "PhysXAssetType" in main_coll and main_coll["PhysXAssetType"] == 'Hairworks':
            nverts = getNumberHairVerts()
            row = layout.row()
            box = row.box()
            box.label(text="Hairworks", icon='PARTICLE_POINT')
            box_row = box.row()
            box_row.prop(self, "resample_value")
            if self.resample_value != nverts and not self.n_verts_check:
                self.resample_value = nverts
                self.n_verts_check = True

    def execute(self, context):
        context.scene.frame_set(0)
        # Should work from all modes
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
        main_coll = GetCollection(make_active=False)
        
        if "PhysXAssetType" in main_coll:
            if main_coll["PhysXAssetType"] == 'Hairworks':
                write_hairworks(context, self.filepath, self.resample_value)
                self.n_verts_check = False
            elif main_coll["PhysXAssetType"] == 'Clothing':
                write_clothing(context, self.filepath)
                
        return {'FINISHED'}
    
class PhysXProperties(PropertyGroup):
    placeholder: IntProperty(name="Placeholder")
    
class ClothProperties(PropertyGroup):
    placeholder: IntProperty(name="Placeholder")
    
class HairProperties(PropertyGroup):
    placeholder: IntProperty(name="Placeholder")
        
PROPS = [*PROPS_Main_Panel, *PROPS_Collision_Panel]
PROPS_CLOTH = [* PROPS_ClothMaterial_Panel, *PROPS_ClothSimulation_Panel, *PROPS_Painting_Panel] 
PROPS_HAIR = [*PROPS_HairPin_Panel, *PROPS_HairTools_Panel, *PROPS_HairMaterial_Panel]
CLASSES = [APXAddonPreferences, ImportApx, ExportApx, PhysXProperties, ClothProperties, HairProperties, *CLASSES_Main_Panel, *CLASSES_Collision_Panel, *CLASSES_Painting_Panel, *CLASSES_ClothMaterial_Panel, *CLASSES_ClothSimulation_Panel, *CLASSES_HairPin_Panel, *CLASSES_HairTools_Panel, *CLASSES_HairMaterial_Panel]

# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(ImportApx.bl_idname, text="APX (.apx/.apb)")

def menu_func_export(self, context):
    self.layout.operator(ExportApx.bl_idname, text="APX (.apx)")

def register():
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
    
    for klass in CLASSES:
        bpy.utils.register_class(klass)
    setattr(bpy.types.WindowManager, "physx", PhysXProperties)
    for (prop_name, prop_value) in PROPS:
        setattr(bpy.types.WindowManager.physx, prop_name, prop_value)
    setattr(bpy.types.WindowManager.physx, "cloth", ClothProperties)
    for (prop_name, prop_value) in PROPS_CLOTH:
        setattr(bpy.types.WindowManager.physx.cloth, prop_name, prop_value)
    setattr(bpy.types.WindowManager.physx, "hair", HairProperties)
    for (prop_name, prop_value) in PROPS_HAIR:
        setattr(bpy.types.WindowManager.physx.hair, prop_name, prop_value)
    bpy.types.WindowManager.physx.cloth = PointerProperty(type=ClothProperties)
    bpy.types.WindowManager.physx.hair = PointerProperty(type=HairProperties)
    bpy.types.WindowManager.physx = PointerProperty(type=PhysXProperties)

    bpy.context.window_manager.keyconfigs.active.keymaps['Object Mode'].keymap_items.new("physx.add_sphere_connection_key", 'C', 'PRESS', shift=1, ctrl=1)
        
def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    
    CLASSES_Painting_Panel[2].handle_remove(CLASSES_Painting_Panel[2], bpy.context)
    #keys = bpy.context.window_manager.keyconfigs.active.keymaps['Object Mode'].keymap_items 
    #keys.remove(keys.find_from_operator("physx.add_sphere_connection_key"))
    
    for klass in CLASSES:
        bpy.utils.unregister_class(klass)
        
    delattr(bpy.types.WindowManager, "physx")