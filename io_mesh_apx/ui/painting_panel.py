# -*- coding: utf-8 -*-
#ui/painting_panel.py

import bpy
import re
import numpy as np
from bpy.props import EnumProperty, BoolProperty, FloatProperty, IntProperty
from bpy.types import Operator, SpaceView3D
from io_mesh_apx.utils import GetCollection, GetArmature, ConvertMode, draw_paint_vectors, draw_paint_spheres, vertices_global_co_normal, setCustomWeightPalette
from io_mesh_apx.tools.paint_tools import add_drive_latch_group, applyDriveLatch, floodAllVertices, smoothAllVertices, copyMaxDistance

class SmoothAll(Operator):
    """Smooth All"""
    bl_idname = "physx.smooth_all"
    bl_label = "Smooth All"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        obj = context.active_object
        vgroups = obj.vertex_groups
        group_name = vgroups[vgroups.active_index].name
        smoothAllVertices(context, obj, group_name)
        return {'FINISHED'}

class FloodAll(Operator):
    """Flood All"""
    bl_idname = "physx.flood_all"
    bl_label = "Flood All"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        obj = context.active_object
        vgroups = obj.vertex_groups
        group_name = vgroups[vgroups.active_index].name
        wm = context.window_manager.physx.cloth
        if wm.paintLayer != 'PhysXBackstopDistance':
            floodAllVertices(context, obj, group_name, wm.paintValue)
        else:
            floodAllVertices(context, obj, group_name, wm.paintValueBackstopDistance * 0.5 + 0.5)
        return {'FINISHED'}
    
class CopyMaxDistance(Operator):
    """Copy Maximum Distance Paint"""
    bl_idname = "physx.copy_max_dist"
    bl_label = "Copy Maximum Distance Paint"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        obj = context.active_object
        copyMaxDistance(context, obj)
        return {'FINISHED'}
    
class PhysXDisplayPaint(Operator):
    bl_idname = "physx.display_paint_vectors"
    bl_label = "Display Paint Vectors"
    bl_description = "Control for enabling or disabling the display of paint vectors in the viewport"

    _handle = None  # keep function handler

    @staticmethod
    def handle_add(self, context):
        if PhysXDisplayPaint._handle is None:
            obj = context.active_object
            coords, normals = vertices_global_co_normal(obj)
            rots = np.arange(0,2*np.pi, 0.39269908169872414)
            dirs = np.stack([np.cos(rots), np.sin(rots), np.zeros_like(rots)], axis=1)
            PhysXDisplayPaint._handle = SpaceView3D.draw_handler_add(draw_callback_px, (self, context, obj, context.window_manager.physx.cloth.viewPaintMode, coords, normals, dirs), 'WINDOW', 'POST_VIEW')

    @staticmethod
    def handle_remove(self, context):
        if PhysXDisplayPaint._handle is not None:
            SpaceView3D.draw_handler_remove(PhysXDisplayPaint._handle, 'WINDOW')
        PhysXDisplayPaint._handle = None

    def execute(self, context):
        if context.area.type == 'VIEW_3D':
            wm = context.window_manager.physx.cloth
            if wm.viewPaintMode != "OFF" and wm.clothPaintingMode:
                self.handle_add(self, context)
                context.area.tag_redraw()
            else:
                self.handle_remove(self, context)
                context.area.tag_redraw()

            return {'FINISHED'}
        else:
            self.report({'WARNING'},
                        "View3D not found, cannot run operator")

        return {'CANCELLED'}
    
def draw_callback_px(self, context, obj, mode, coords, normals, dirs):
    if mode  == 'VECTOR':
        draw_paint_vectors(obj, context.window_manager.physx.cloth.paintLayer, coords, normals)
    elif mode  == 'SPHERE':
        draw_paint_spheres(obj, context.window_manager.physx.cloth.paintLayer, coords, normals, dirs)
    
class PhysXPaintingPanel(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_PhysX_painting_panel'
    bl_parent_id = 'VIEW3D_PT_PhysX_panel'
    bl_label = 'PhysX Painting'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'PhysX'
    bl_options = {'HIDE_HEADER'}
    
    def draw(self, context):
        layout = self.layout
        physx = context.window_manager.physx
        wm = physx.cloth
        paint_settings = context.scene.tool_settings.weight_paint.unified_paint_settings
        if physx.PhysXSubPanel == 'painting':
            main_coll = GetCollection(make_active=False)
            arma = GetArmature()
            obj = context.active_object
            if main_coll and obj and obj in arma.children and obj.type == 'MESH':
                
                row = layout.row()
                row.prop(wm, "maximumMaxDistance", text = "Maximum Max Distance")
                if wm.maximumMaxDistance != obj["maximumMaxDistance"]:
                    wm.maximumMaxDistance = obj["maximumMaxDistance"]
                
                vgroups = obj.vertex_groups
                active_name = vgroups[vgroups.active_index].name
                row = layout.row()
                if wm.clothPaintingMode:
                    icon = 'PAUSE'
                    txt = 'Disable Painting Mode'
                else:
                    icon = "PLAY"
                    txt = 'Enable Painting Mode'
                row.prop(wm, "clothPaintingMode", text = txt, toggle=True, icon = icon)
                if wm.clothPaintingMode and (context.scene.frame_current or bpy.context.mode != 'PAINT_WEIGHT' or not context.preferences.view.use_weight_color_range or not obj.show_wire or not re.search(r"PhysX", active_name)):
                    wm.clothPaintingMode = False
                    
                row = layout.row(align = True)
                row.enabled = wm.clothPaintingMode
                     
                if wm.paintLayer != 'Drive/Latch':
                    split = row.split(align = True)
                    split.scale_x = 0.825
                    split.prop(wm, "paintLayer", text = "Layer")
                    split = row.split(align = True)
                    split.alert = (wm.viewPaintMode != "OFF")
                    split.prop(wm, "viewPaintMode", text = "")
                    
                    row = layout.row(align=True)
                    row.label(text="Operation:")
                    row.enabled = wm.clothPaintingMode
                    row.prop_enum(wm, "paintMode", 'Draw')
                    row.prop_enum(wm, "paintMode", 'Smooth')
                    brush_type = bpy.context.tool_settings.weight_paint.brush.weight_brush_type
                    if brush_type == 'DRAW' and wm.paintMode != 'Draw':
                        wm.paintMode = 'Draw'
                    elif brush_type == 'BLUR' and wm.paintMode != 'Smooth':
                        wm.paintMode = 'Smooth'
                             
                    if wm.paintMode != 'Smooth':
                        row = layout.row()
                        row.enabled = wm.clothPaintingMode
                        if wm.paintLayer != 'PhysXBackstopDistance':
                            row.prop(wm, "paintValue", text = "Value")
                            if wm.paintValue != paint_settings.weight:
                                wm.paintValue = paint_settings.weight
                        else:
                            row.prop(wm, "paintValueBackstopDistance", text = "Value")
                            if wm.paintValueBackstopDistance != (paint_settings.weight - 0.5) * 2:
                                wm.paintValueBackstopDistance = (paint_settings.weight - 0.5) * 2
                        
                else:
                    row.prop(wm, "paintLayer", text = "Layer")
                    row = layout.row()
                    row.enabled = wm.clothPaintingMode
                    row.prop(wm, "driveLatchGroup", text = "Group") 
                    row = layout.row()
                    row.label(text="Mode")
                    row.enabled = wm.clothPaintingMode
                    row.prop_enum(wm, "driveLatchMode", 'Drive')
                    row.prop_enum(wm, "driveLatchMode", 'Latch')
                    active_index = vgroups.active_index
                    if vgroups["PhysX" + wm.driveLatchMode + wm.driveLatchGroup[5:]].index != active_index:
                        active_group_name = vgroups[active_index].name
                        wm.driveLatchGroup = "Group" + active_group_name[10:]
                        wm.driveLatchMode = active_group_name[5:10]
                         
                    row = layout.row()
                    row.label(text="Operation")
                    row.enabled = wm.clothPaintingMode
                    row.prop_enum(wm, "paintModeDriveLatch", 'Add')
                    row.prop_enum(wm, "paintModeDriveLatch", 'Remove')
                    if wm.paintModeDriveLatch == 'Add' and paint_settings.weight < 1:
                        wm.paintModeDriveLatch = 'Remove'
                    elif wm.paintModeDriveLatch == 'Remove' and paint_settings.weight > 0:
                        wm.paintModeDriveLatch = 'Add'
                        
                if active_name in ['PhysXMaximumDistance', 'PhysXBackstopRadius', 'PhysXBackstopDistance'] and wm.paintLayer != active_name:
                    wm.paintLayer = active_name
                elif re.search(r"PhysX(Drive|Latch)[0-9]+", active_name) and wm.paintLayer != 'Drive/Latch':
                    wm.paintLayer = 'Drive/Latch'
                        
                row = layout.row()
                row.enabled = wm.clothPaintingMode
                row.prop(wm, "paintRadius", text = "Radius")
                if wm.paintRadius != paint_settings.size:
                    wm.paintRadius = paint_settings.size
                    
                if wm.paintLayer != 'Drive/Latch':
                    row = layout.row()
                    row.enabled = wm.clothPaintingMode
                    row.operator(SmoothAll.bl_idname, text="Smooth All", icon='SMOOTHCURVE')
                
                if wm.paintLayer == 'Drive/Latch' or wm.paintMode != 'Smooth':
                    row = layout.row()
                    row.enabled = wm.clothPaintingMode
                    row.operator(FloodAll.bl_idname, text="Flood All", icon='IMAGE')
                
                if wm.paintLayer == 'PhysXBackstopDistance' and wm.paintMode == 'Draw':
                    row = layout.row()
                    row.enabled = wm.clothPaintingMode
                    row.operator(CopyMaxDistance.bl_idname, text="Copy Maximum Distance", icon='DRIVER_DISTANCE')
        return
    
def updateMaximumMaxDistance(self, context):
    obj = context.active_object
    obj["maximumMaxDistance"] = self.maximumMaxDistance
    mod = obj.modifiers['ClothSimulation']
    mod["Socket_11"] = self.maximumMaxDistance
    mod.node_group.interface_update(context)
    
def updateClothPaintingMode(self, context):
    obj = context.active_object
    vgroups = applyDriveLatch(obj)
    mode = context.mode
    view_prefs = context.preferences.view
    if self.clothPaintingMode:
        if context.screen.is_animation_playing:
            bpy.ops.screen.animation_cancel(restore_frame=False)
        context.scene.frame_set(0)
        bpy.ops.physx.delete_bake_data()
        self.previousMode = mode
        bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
        view_prefs.use_weight_color_range = True
        view_prefs.weight_color_range.color_mode = 'RGB'
        view_prefs.weight_color_range.interpolation = 'LINEAR'
        obj.show_wire = True
        
        if self.paintLayer != 'Drive/Latch':
            vgroups.active_index = vgroups[self.paintLayer].index
            if self.paintMode == 'Draw':
                bpy.ops.brush.asset_activate(asset_library_type='ESSENTIALS', asset_library_identifier="", relative_asset_identifier="brushes\\essentials_brushes-mesh_weight.blend\\Brush\\Paint")
                w_brush = context.tool_settings.weight_paint.brush
                w_brush.weight_brush_type = 'DRAW'
                w_brush.curve_distance_falloff_preset = 'CONSTANT'
                w_brush.blend = 'MIX'
                context.scene.tool_settings.weight_paint.unified_paint_settings.weight = self.paintValue
            else:
                bpy.ops.brush.asset_activate(asset_library_type='ESSENTIALS', asset_library_identifier="", relative_asset_identifier="brushes\\essentials_brushes-mesh_weight.blend\\Brush\\Blur")
                w_brush = context.tool_settings.weight_paint.brush
                w_brush.weight_brush_type = 'BLUR'
                w_brush.curve_distance_falloff_preset = 'CONSTANT'
                bpy.data.brushes['Blur'].strength = 1
            context.scene.tool_settings.weight_paint.unified_paint_settings.size = self.paintRadius
            if self.viewPaintMode != "OFF":
                PhysXDisplayPaint.handle_add(PhysXDisplayPaint, context)
            if self.paintLayer != 'PhysXBackstopDistance':
                setCustomWeightPalette('DEFAULT')
            else:
                setCustomWeightPalette('BACKSTOP_DISTANCE')
                if self.paintMode == 'Draw':
                    context.scene.tool_settings.weight_paint.unified_paint_settings.weight = self.paintValueBackstopDistance * 0.5 + 0.5
            
        else:
            setCustomWeightPalette('DRIVE/LATCH')
            PhysXDisplayPaint.handle_remove(PhysXDisplayPaint, context)
            if self.driveLatchMode == 'Drive':
                vgroups.active_index = vgroups["PhysXDrive"+self.driveLatchGroup[5:]].index
            else:
                vgroups.active_index = vgroups["PhysXLatch"+self.driveLatchGroup[5:]].index
            updatePaintModeDriveLatch(self, context)
            
    else:
        PhysXDisplayPaint.handle_remove(PhysXDisplayPaint, context)
        view_prefs.use_weight_color_range = False
        obj.show_wire = False
        if mode == 'PAINT_WEIGHT': 
            bpy.ops.object.mode_set(mode=ConvertMode(self.previousMode))
    bpy.ops.wm.save_userpref()
        
def updatePaintLayer(self, context):
    vgroups = applyDriveLatch(context.active_object)
    if self.paintLayer != 'Drive/Latch':
        if self.paintLayer != 'PhysXBackstopDistance':
            setCustomWeightPalette('DEFAULT')
        else:
            setCustomWeightPalette('BACKSTOP_DISTANCE')
        vgroups.active_index = vgroups[self.paintLayer].index
        if self.viewPaintMode != "OFF":
            PhysXDisplayPaint.handle_add(PhysXDisplayPaint, context)
    else:
        setCustomWeightPalette('DRIVE/LATCH')
        PhysXDisplayPaint.handle_remove(PhysXDisplayPaint, context)
        vgroups.active_index = vgroups["PhysX" + self.driveLatchMode + self.driveLatchGroup[5:]].index
        updatePaintModeDriveLatch(self, context)
        
def updateViewPaintMode(self, context):
    PhysXDisplayPaint.handle_remove(PhysXDisplayPaint, context)
    PhysXDisplayPaint.execute(PhysXDisplayPaint, context)
    
def updatePaintMode(self, context):
    if self.paintMode == 'Draw':
        bpy.ops.brush.asset_activate(asset_library_type='ESSENTIALS', asset_library_identifier="", relative_asset_identifier="brushes\\essentials_brushes-mesh_weight.blend\\Brush\\Paint")
        w_brush = context.tool_settings.weight_paint.brush
        w_brush.weight_brush_type = 'DRAW'
        w_brush.curve_distance_falloff_preset = 'CONSTANT'
        w_brush.blend = 'MIX'
        if self.paintLayer != 'PhysXBackstopDistance':
            context.scene.tool_settings.weight_paint.unified_paint_settings.weight = self.paintValue
        else:
            context.scene.tool_settings.weight_paint.unified_paint_settings.weight = self.paintValueBackstopDistance * 0.5 + 0.5
    else:
        bpy.ops.brush.asset_activate(asset_library_type='ESSENTIALS', asset_library_identifier="", relative_asset_identifier="brushes\\essentials_brushes-mesh_weight.blend\\Brush\\Blur")
        w_brush = context.tool_settings.weight_paint.brush
        w_brush.weight_brush_type = 'BLUR'
        w_brush.curve_distance_falloff_preset = 'CONSTANT'
        bpy.data.brushes['Blur'].strength = 1
        
def updatePaintValue(self, context):
    context.scene.tool_settings.weight_paint.unified_paint_settings.weight = self.paintValue
    
def updatePaintValueBackstopDistance(self, context):
    context.scene.tool_settings.weight_paint.unified_paint_settings.weight = self.paintValueBackstopDistance * 0.5 + 0.5
    
def updatePaintRadius(self, context):
    context.scene.tool_settings.weight_paint.unified_paint_settings.size = self.paintRadius
    
def getDriveLatchGroups(self, context):
    groups = []
    drive_groups = []
    latch_groups = [] 
    obj = context.active_object
    vgroups = obj.vertex_groups     
    for vg in vgroups:
        if re.search("PhysXDrive[0-9]+", vg.name):
            drive_groups.append(vg)
        if re.search("PhysXLatch[0-9]+", vg.name):
            latch_groups.append(vg)
    if drive_groups:        
        while len(latch_groups) != len(drive_groups):
            if len(latch_groups) > len(drive_groups):
                latch_groups.remove(latch_groups[-1])
                vgroups.remove(latch_groups[-1])
            if len(latch_groups) < len(drive_groups):
                drive_groups.remove(drive_groups[-1])
                vgroups.remove(drive_groups[-1])
    if drive_groups:   
        for i, [d_vg, l_vg] in enumerate(zip(drive_groups, latch_groups)):
            idx = str(i + 1)
            groups.append(('Group'+idx, "Group "+idx, "", 'DOT', i))
    groups.extend([None, ('NewGroup', "New Group", "", 'ADD', i+1)])
    return groups

def updateDriveLatchGroup(self, context):
    obj = context.active_object
    vgroups = applyDriveLatch(obj)
        
    if self.driveLatchGroup == 'NewGroup':
        add_drive_latch_group(obj)
        self.driveLatchGroup = "Group" + self.driveLatchGroup[5:]
        mod = obj.modifiers['ClothSimulation']
        mod["Socket_0"] += 1
        mod.node_group.interface_update(context)
        
    vgroups.active_index = vgroups["PhysX" + self.driveLatchMode + self.driveLatchGroup[5:]].index
        
def updatePaintModeDriveLatch(self, context):
    bpy.ops.brush.asset_activate(asset_library_type='ESSENTIALS', asset_library_identifier="", relative_asset_identifier="brushes\\essentials_brushes-mesh_weight.blend\\Brush\\Paint")
    w_brush = context.tool_settings.weight_paint.brush
    w_brush.weight_brush_type = 'DRAW'
    w_brush.curve_distance_falloff_preset = 'CONSTANT'
    w_brush.blend = 'MIX'
    if self.paintModeDriveLatch == 'Add':
        context.scene.tool_settings.weight_paint.unified_paint_settings.weight = 1
    else: 
        context.scene.tool_settings.weight_paint.unified_paint_settings.weight = 0
        
PROPS_Painting_Panel = [
('maximumMaxDistance', FloatProperty(
        name="Set Maximum Value of Maximum Distance Paint",
        default=1,
        min=0,
        update=updateMaximumMaxDistance
    )),
('clothPaintingMode', BoolProperty(
        name="Cloth Painting Mode",
        description="Enter or Exit Cloth Painting Mode",
        default=False,
        update=updateClothPaintingMode
    )),
('paintLayer', EnumProperty(
        name="Active Paint Layer",
        description="Set the Active Paint Layer",
        default='PhysXMaximumDistance',
        items=(
        ('PhysXMaximumDistance', "Maximum Distance", ""),
        ('PhysXBackstopRadius', "Backstop Radius", ""),
        ('PhysXBackstopDistance', "Backstop Distance", ""),
        ('Drive/Latch', "Drive/Latch", "")
        ),
        update=updatePaintLayer
    )),
('viewPaintMode', EnumProperty(
        name="Visualize Paint",
        description="Set the Paint Visualization Mode",
        default='OFF',
        items=(
        ('OFF', "", "Disable Paint Visualization",  "HIDE_ON", 0),
        ('VECTOR', "", "Enable Paint Visualization with Vectors", "IPO_LINEAR", 1),
        ('SPHERE', "", "Enable Paint Visualization with Spheres",  "MESH_CIRCLE", 2)
        ),
        update=updateViewPaintMode
    )),
('paintMode', EnumProperty(
        name="Active Paint Mode",
        description="Set the Active Paint Mode",
        default='Draw',
        items=(
        ('Draw', "Replace", ""),
        ('Smooth', "Smooth", "")
        ),
        update=updatePaintMode
    )),
('paintValue', FloatProperty(
        name="Paint Value",
        description="Set the Paint Value",
        default=1,
        min=0,
        max=1,
        precision=6,
        update=updatePaintValue
    )),
('paintValueBackstopDistance', FloatProperty(
    name="Paint Backstop Distance Value",
    description="Set the Backstop Distance Paint Value",
    default=0,
    min=-1,
    max=1,
    precision=6,
    update=updatePaintValueBackstopDistance
)),
('paintRadius', IntProperty(
        name="Radius Value",
        description="Set the Radius of the Brush",
        default=50,
        min=1,
        max=500,
        subtype="PIXEL",
        update=updatePaintRadius
    )),
('driveLatchGroup', EnumProperty(
        name="Drive/Latch Group",
        description="Set the Drive or Latch Group",
        items=getDriveLatchGroups,
        update=updateDriveLatchGroup
    )),
('driveLatchMode', EnumProperty(
        name="Drive or Latch Mode",
        description="Set the Drive or Latch Mode",
        default='Drive',
        items=(
        ('Drive', "Drive", ""),
        ('Latch', "Latch", "")
        ),
        update=updateDriveLatchGroup
    )),
('paintModeDriveLatch', EnumProperty(
        name="Active Paint Mode",
        description="Set the Active Paint Mode",
        default='Add',
        items=(
        ('Add', "Add", ""),
        ('Remove', "Remove", "")
        ),
        update=updatePaintModeDriveLatch
    )),
('previousMode', EnumProperty(
        name="Previous Mode",
        items=(
        ('OBJECT', "OBJECT", ""),
        ('EDIT_MESH', "EDIT_MESH", ""),
        ('SCULPT', "SCULPT", ""),
        ('PAINT_VERTEX', "PAINT_VERTEX", ""),
        ('PAINT_WEIGHT', "PAINT_WEIGHT", ""),
        ('PAINT_TEXTURE', "PAINT_TEXTURE", ""),
        ('PARTICLE', "PARTICLE", ""),
        ),
    ))
]

CLASSES_Painting_Panel = [SmoothAll, FloodAll, CopyMaxDistance, PhysXDisplayPaint, PhysXPaintingPanel]