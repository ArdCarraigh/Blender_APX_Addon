# -*- coding: utf-8 -*-
#ui/hair_tools_panel.py

import bpy
import re
from bpy.props import EnumProperty, FloatProperty, IntProperty, BoolProperty
from bpy.types import Operator
from io_mesh_apx.utils import GetCollection, GetArmature, getCurvesCollections, getObjects
from io_mesh_apx.tools.hair_tools import shape_hair_interp, create_curve, haircard_curve, hair_to_haircard

class ShapeHairInterp(Operator):
    """Shape Hair from Curves"""
    bl_idname = "physx.shape_hair_interp"
    bl_label = "Shape Hair from Curves"
    bl_options = {'REGISTER', 'UNDO'}
    bl_property = "collection"
    
    steps: IntProperty(
        name="Interpolation Steps",
        default = 0,
        min = 0,
        description="Number of steps taken around each vertex for interpolation. Interpolation occurs when superior to 0"
    )
    threshold: FloatProperty(
        name="Proximity Threshold",
        default = 0.001,
        min = 0,
        description="Proximity threshold over which interpolation occurs"
    )
    hair_key: IntProperty(
        name="Hair Key",
        default = 0,
        min = 0,
        description="Index of the vertex along the curve used to compute proximity"
    )
    collection: EnumProperty(
        options={'HIDDEN'},
        name="Curves Collections",
        items=getCurvesCollections
    )

    def execute(self, context):
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
        shape_hair_interp(context, GetArmature().children[0], self.collection, self.steps, self.threshold, self.hair_key, True)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'RUNNING_MODAL'}
    
class CreateCurve(Operator):
    """Create Curves from Hair"""
    bl_idname = "physx.create_curve"
    bl_label = "Create Curves from Hair"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
        create_curve(context, GetArmature().children[0])
        return {'FINISHED'}
    
class HaircardCurve(Operator):
    """Create Curves from Haircard Mesh"""
    bl_idname = "physx.haircard_curve"
    bl_label = "Create Curves from Haircard Mesh"
    bl_options = {'REGISTER', 'UNDO'}
    bl_property = "hair_mesh"
    
    uv_orientation: EnumProperty(
        name="UV Orientation",
        description="Inform the orientation of your hair cards on the UV map",
        items=(
            ('-Y', "-Y", "From top to bottom"),
            ('Y', "Y", "From bottom to top"),
            ('X', "X", "From left to right"),
            ('-X', "-X", "From right to left")
        ),
        default='-Y',
    )
    
    tolerance: FloatProperty(
        name="Tolerance threshold",
        default = 0.05,
        min = 0,
        description="Tolerance threshold of UV coordinates difference used to assess which vertices to gather"
    )
    
    hair_mesh: EnumProperty(
        options={'HIDDEN'},
        name="Hair Mesh",
        items=getObjects
    )

    def execute(self, context):
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
        haircard_curve(context, self.hair_mesh, self.uv_orientation, self.tolerance)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'RUNNING_MODAL'}
    
class HairToHaircard(Operator):
    """Create Haircard Mesh from Hair"""
    bl_idname = "physx.hair_to_haircard"
    bl_label = "Create Haircard Mesh from Hair"
    bl_options = {'REGISTER', 'UNDO'}
    
    cap: BoolProperty(
        name="Enable/Disable Cap",
        default = False,
        description="Make a cap as base for the haircard mesh"
    )
    width: FloatProperty(
        name="Hair Card Width",
        default = 0.05,
        min = 0,
        description="Set the maximum width of the haircard"
    )
    width_relative: BoolProperty(
        name="Enable/Disable Relative Width",
        default=False,
        description="Make the width relative to the length of the hair"
    )

    def execute(self, context):
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
        hair_to_haircard(context, GetArmature().children[0], self.cap, self.width, self.width_relative)
        return {'FINISHED'}
    
class PhysXHairToolsPanel(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_PhysX_hair_tools_panel'
    bl_parent_id = 'VIEW3D_PT_PhysX_panel'
    bl_label = 'Hairworks Tools'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'PhysX'
    bl_options = {'HIDE_HEADER'}
    
    def draw(self, context):
        layout = self.layout
        physx = context.window_manager.physx
        wm = physx.hair
        if physx.PhysXSubPanel == 'hair_tools':
            main_coll = GetCollection(make_active=False)
            obj = GetArmature().children[0]
            if main_coll and obj and obj.type == 'MESH':
                row = layout.row()
                row.enabled = "Hairworks" in obj.modifiers
                row.operator(CreateCurve.bl_idname, text = "Convert Hair to Curves")
                
                row = layout.row()
                row.operator(ShapeHairInterp.bl_idname, text = "Convert Curves to Hair")
                
                row = layout.row()
                row.operator(HaircardCurve.bl_idname, text = "Convert Hair Cards to Curves")
                
                #row = layout.row()
                #row.operator(HairToHaircard.bl_idname, text = "Convert Hair to Hair Cards")
            
        return
        
PROPS_HairTools_Panel = [

]

CLASSES_HairTools_Panel = [ShapeHairInterp, CreateCurve, HaircardCurve, HairToHaircard, PhysXHairToolsPanel]