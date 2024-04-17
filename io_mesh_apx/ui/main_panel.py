# -*- coding: utf-8 -*-
# ui/main_panel.py

import bpy
from bpy.props import EnumProperty
from bpy.types import Operator
from io_mesh_apx.tools.setup_tools import setup_hairworks, setup_clothing
from io_mesh_apx.utils import GetCollection
    
class SetupHairworks(Operator):
    """Set Up a Hairworks Asset"""
    bl_idname = "physx.setup_hairworks"
    bl_label = "Set Up a Hairworks Asset"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        obj = bpy.context.active_object
        assert(obj is not None)
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
        setup_hairworks(context, obj)
        return {'FINISHED'}
    
class SetupClothing(Operator):
    """Set Up a Clothing Asset"""
    bl_idname = "physx.setup_clothing"
    bl_label = "Set Up a Clothing Asset"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        obj = bpy.context.active_object
        assert(obj is not None)
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
        setup_clothing(context, obj)
        return {'FINISHED'}

class PhysXMainPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'PhysX'
    bl_idname = 'VIEW3D_PT_PhysX_panel'
    bl_label = 'PhysX'
    
    def draw(self, context):
        wm = context.window_manager.physx
        layout = self.layout
        row = layout.row()
        box = row.box()
        box.label(text = "Setup", icon='ASSET_MANAGER')
        box_row = box.row(align = True)
        box_row.operator(SetupClothing.bl_idname, text = "Clothing", icon = "MATCLOTH")
        box_row.operator(SetupHairworks.bl_idname, text = "Hairworks", icon = "OUTLINER_DATA_CURVES")
        layout.separator()
        
        main_coll = GetCollection(make_active=False)
        if main_coll:
            row = layout.row(align = True)
            row.alignment = "CENTER"
            row.scale_x = 1.44
            row.scale_y = 1.4
            row.prop_enum(wm, "PhysXSubPanel", 'collision', text = "")
            
            if main_coll["PhysXAssetType"] == "Clothing":
                row.prop_enum(wm, "PhysXSubPanel", 'painting', text = "")
                row.prop_enum(wm, "PhysXSubPanel", 'cloth_sim', text = "")
                row.prop_enum(wm, "PhysXSubPanel", 'cloth_mat', text = "")
                
            elif main_coll["PhysXAssetType"] == "Hairworks":
                row.prop_enum(wm, "PhysXSubPanel", 'hair_pin', text = "")
                row.prop_enum(wm, "PhysXSubPanel", 'hair_tools', text = "")
                row.prop_enum(wm, "PhysXSubPanel", 'hair_mat', text = "")
        
        return 
            
PROPS_Main_Panel = [
('PhysXSubPanel', EnumProperty(
        name="PhysX SubPanel",
        description="Set the active PhysX subpanel",
        items=(
            ('collision', "collision", "Show the collision PhysX subpanel", 'OUTLINER_OB_ARMATURE', 0),
            ('painting', "painting", "Show the painting PhysX subpanel", 'BRUSH_DATA', 1),
            ('cloth_sim', "cloth_sim", "Show the cloth simulation PhysX subpanel", 'TOOL_SETTINGS', 2),
            ('cloth_mat', "cloth_mat", "Show the cloth material PhysX subpanel", 'MATCLOTH', 3),
            ('hair_pin', "hair_pin", "Show the Hairworks pin subpanel", 'PINNED', 4),
            ('hair_tools', "hair_tools", "Show the Hairworks tools subpanel", 'TOOL_SETTINGS', 5),
            ('hair_mat', "hair_mat", "Show the Hairworks Material subpanel", 'MATERIAL', 6)
        ),
        default='collision'
    ))
]

CLASSES_Main_Panel = [SetupHairworks, SetupClothing, PhysXMainPanel]