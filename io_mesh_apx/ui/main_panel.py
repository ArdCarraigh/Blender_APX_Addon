# -*- coding: utf-8 -*-
# ui/main_panel.py

import bpy
from bpy.props import EnumProperty, IntProperty, BoolProperty
from bpy.types import Operator
from io_mesh_apx.tools.setup_tools import setup_hairworks, setup_clothing
from io_mesh_apx.utils import GetCollection, MakeKDTree, getClosest, GetArmature
from bpy_extras import view3d_utils
import numpy as np 
    
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
    
class PhysXModalGrab(Operator):
    bl_idname = "physx.modal_grab"
    bl_label = "Modal Grab"
    
    active = False
    vert_id = 0
    vert_pos = [0,0,0]
    depth = [0,0,0]
        
    def execute(self, context):
        mod = context.active_object.modifiers['ClothSimulation']
        mod['Socket_12'] = self.active
        mod['Socket_13'] = self.vert_id
        mod['Socket_14'] = np.array(self.vert_pos, dtype=float)
        mod.node_group.interface_update(context)
        return {'FINISHED'}

    def modal(self, context, event):
        ob = context.active_object
        rotation_and_scale = ob.matrix_world.to_3x3().transposed()
        offset = ob.matrix_world.translation
        mouse_pos = [event.mouse_region_x, event.mouse_region_y]
        region = bpy.context.region
        region3D = bpy.context.space_data.region_3d
        
        if event.type in ['MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE']: # Allow Camera Movement
            return {'PASS_THROUGH'}
        
        if event.type == 'MOUSEMOVE':  # Apply
            if self.active:
                pos = view3d_utils.region_2d_to_location_3d(region, region3D, mouse_pos, self.depth)
                pos -= offset
                pos = np.matmul(pos, rotation_and_scale.inverted())
                self.vert_pos = pos
                self.execute(context)
                
        elif event.type == 'LEFTMOUSE':  # Select Vertex
            if event.value == 'RELEASE' and self.active:
                self.active = False
                self.vert_id = 0
                self.vert_pos = [0,0,0]
                self.depth = [0,0,0]
                self.execute(context)
            elif event.value == 'PRESS' and not event.is_repeat:
                self.active = True
                obj = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
                vert_poses_3D = np.zeros(len(obj.data.vertices) * 3)
                obj.data.attributes['position'].data.foreach_get("vector", vert_poses_3D)
                vert_poses_3D = vert_poses_3D.reshape(-1,3)
                vert_poses_3D_global = np.matmul(vert_poses_3D, rotation_and_scale)
                vert_poses_3D_global += offset
                vert_poses_2D = [[*view3d_utils.location_3d_to_region_2d(region, region3D, x), 0] for x in vert_poses_3D_global]
                tree = MakeKDTree(vert_poses_2D)
                self.vert_id = getClosest([*mouse_pos, 0], tree, 10)
                self.vert_pos = vert_poses_3D[self.vert_id]
                self.depth = vert_poses_3D_global[self.vert_id]
                self.execute(context)
                
        elif event.type in ['RIGHTMOUSE', 'ESC', 'SPACE']:  # Cancel
            self.active = False
            self.vert_id = 0
            self.vert_pos = [0,0,0]
            self.depth = [0,0,0]
            context.window_manager.physx.PhysXGrabMode = False
            self.execute(context)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self.active = False
        self.vert_id = 0
        self.vert_pos = [0,0,0]
        self.depth = [0,0,0]
        context.window_manager.physx.PhysXGrabMode = True
        self.execute(context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
class PhysXBakeSimulation(Operator):
    """Bake PhysX Simulation"""
    bl_idname = "physx.bake_simulation"
    bl_label = "Bake PhysX Simulation"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        context.scene.frame_set(0)
        bpy.ops.object.geometry_node_bake_single(session_uid=context.active_object.id_data.session_uid, modifier_name="ClothSimulation", bake_id=231501695)
        return {'FINISHED'}
    
class PhysXDeleteBakedData(Operator):
    """Delete Baked PhysX Data"""
    bl_idname = "physx.delete_bake_data"
    bl_label = "Delete Baked PhysX Data"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        context.scene.frame_set(0)
        bpy.ops.object.geometry_node_bake_delete_single(session_uid=context.active_object.id_data.session_uid, modifier_name="ClothSimulation", bake_id=231501695)
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
            if main_coll["PhysXAssetType"] == "Clothing":
                arma = GetArmature()
                obj = context.active_object
                
                row = layout.row()
                box = row.box()
                box.label(text = "Simulation", icon='SETTINGS')
                box_row = box.row()
                box_row.prop(wm, "PhysXSimFPS", text="Frames per second")
                
                check_mesh =  (main_coll is not None and obj is not None and obj in arma.children and obj.type == 'MESH')
                box_row = box.row()
                box_row.enabled = check_mesh and bpy.context.mode != 'PAINT_WEIGHT'
                split = box_row.split(factor = 0.85, align = True)
                split.operator(PhysXBakeSimulation.bl_idname, text = "Bake Simulation")
                split.operator(PhysXDeleteBakedData.bl_idname, text = "", icon='TRASH')
                
                box_row = box.row()
                box_row.enabled = check_mesh and bpy.context.screen.is_animation_playing
                box_row.alert = wm.PhysXGrabMode
                if wm.PhysXGrabMode:
                    icon = 'PAUSE'
                    txt = 'Ongoing'
                else:
                    icon = "PLAY"
                    txt = 'Enable Grab Mode'
                box_row.operator(PhysXModalGrab.bl_idname, text = txt, icon = icon)
                if not bpy.context.screen.is_animation_playing:
                    wm.PhysXGrabMode = False
                        
                layout.separator()
                    
            row = layout.row(align = True)
            row.alignment = "CENTER"
            row.scale_x = 1.44
            row.scale_y = 1.4
            if main_coll["PhysXAssetType"] != "Destruction":
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
    
def updatePhysXSimFPS(self, context):
    context.scene.render.fps = self.PhysXSimFPS
    for obj in bpy.data.objects:
        if 'ClothSimulation' in obj.modifiers:
            mod = obj.modifiers['ClothSimulation']
            mod['Socket_15'] = self.PhysXSimFPS
            mod.node_group.interface_update(context)
            
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
    )),
('PhysXSimFPS', IntProperty(
        name="PhysX Simulation FPS",
        description="Set the number of frames per second for the PhysX simulation",
        default=24,
        min=1,
        update=updatePhysXSimFPS
    )),
('PhysXGrabMode', BoolProperty(
        name="PhysX Grab Mode",
        description="Enable grabbing during simulation",
        default=False
    ))
]

CLASSES_Main_Panel = [SetupHairworks, SetupClothing, PhysXModalGrab, PhysXBakeSimulation, PhysXDeleteBakedData, PhysXMainPanel]