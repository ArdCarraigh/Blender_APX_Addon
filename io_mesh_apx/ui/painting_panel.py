# -*- coding: utf-8 -*-
#ui/painting_panel.py

import bpy
import re
from bpy.props import EnumProperty, BoolProperty, FloatProperty, IntProperty
from bpy.types import Operator, SpaceView3D
from io_mesh_apx.utils import GetCollection, GetArmature, set_active_tool, ConvertMode, draw_max_dist_vectors, vertices_global_co_normal, setCustomWeightPalette
from io_mesh_apx.tools.paint_tools import add_drive_latch_group, applyDriveLatch, floodAllVertices, smoothAllVertices

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
        floodAllVertices(context, obj, group_name, context.scene.tool_settings.unified_paint_settings.weight)
        return {'FINISHED'}
    
class PhysXDisplayPaintVectors(Operator):
    bl_idname = "physx.display_paint_vectors"
    bl_label = "Display Paint Vectors"
    bl_description = "Control for enabling or disabling the display of paint vectors in the viewport"

    _handle = None  # keep function handler

    @staticmethod
    def handle_add(self, context):
        if PhysXDisplayPaintVectors._handle is None:
            coords, normals = vertices_global_co_normal(bpy.context.active_object)
            PhysXDisplayPaintVectors._handle = SpaceView3D.draw_handler_add(draw_callback_px, (self, context, coords, normals), 'WINDOW', 'POST_VIEW')

    @staticmethod
    def handle_remove(self, context):
        if PhysXDisplayPaintVectors._handle is not None:
            SpaceView3D.draw_handler_remove(PhysXDisplayPaintVectors._handle, 'WINDOW')
        PhysXDisplayPaintVectors._handle = None

    def execute(self, context):
        if context.area.type == 'VIEW_3D':
            wm = context.window_manager.physx.cloth
            if wm.viewPaintVectors and wm.clothPaintingMode:
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
    
def draw_callback_px(self, context, coords, normals):
    wm = context.window_manager.physx.cloth
    obj = context.active_object
    draw_max_dist_vectors(obj, obj.vertex_groups[wm.paintLayer], wm.maximumMaxDistance, coords, normals)
    
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
        paint_settings = context.scene.tool_settings.unified_paint_settings
        if physx.PhysXSubPanel == 'painting':
            main_coll = GetCollection(make_active=False)
            arma = GetArmature()
            obj = context.active_object
            if main_coll and obj and obj in arma.children and obj.type == 'MESH':
                
                row = layout.row()
                row.prop(wm, "maximumMaxDistance", text = "Maximum Max Distance")
                max_dist = obj.modifiers["PinGroup"].node_group.nodes["Maximum Max Distance"].inputs[1].default_value
                if wm.maximumMaxDistance != max_dist:
                    wm.maximumMaxDistance = max_dist
                
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
                    
                row = layout.row()
                row.enabled = wm.clothPaintingMode
                row.prop(wm, "paintLayer", text = "Layer")
                layers = ['PhysXMaximumDistance', 'PhysXBackstopRadius', 'PhysXBackstopDistance']
                if active_name in layers and wm.paintLayer != active_name:
                    wm.paintLayer = active_name
                elif re.search(r"PhysX(Drive|Latch)[0-9]+", active_name) and wm.paintLayer != 'Drive/Latch':
                    wm.paintLayer = 'Drive/Latch'
                     
                if wm.paintLayer != 'Drive/Latch':
                    split = row.split(factor = 1.3, align = False)
                    split.enabled = wm.clothPaintingMode
                    if wm.viewPaintVectors:
                        icon = 'HIDE_OFF'
                    else:
                        icon = "HIDE_ON"
                    split.prop(wm, "viewPaintVectors", text = "", toggle = True, icon = icon)
                    
                    row = layout.row(align=True)
                    row.label(text="Operation:")
                    row.enabled = wm.clothPaintingMode
                    row.prop_enum(wm, "paintMode", 'Draw')
                    row.prop_enum(wm, "paintMode", 'Smooth')
                    brush_name = context.tool_settings.weight_paint.brush.name
                    if brush_name in ['Draw', 'Blur']:
                        if brush_name == 'Draw' and wm.paintMode != brush_name:
                            wm.paintMode = 'Draw'
                        elif brush_name == 'Blur' and wm.paintMode != 'Smooth':
                            wm.paintMode = 'Smooth'
                             
                    if wm.paintMode != 'Smooth':
                        row = layout.row()
                        row.enabled = wm.clothPaintingMode
                        row.prop(wm, "paintValue", text = "Value")
                        if wm.paintValue != paint_settings.weight:
                            wm.paintValue = paint_settings.weight
                        
                
                else:
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
                        
                row = layout.row()
                row.enabled = wm.clothPaintingMode
                row.prop(wm, "paintRadius", text = "Radius")
                if wm.paintRadius != paint_settings.size:
                    wm.paintRadius = paint_settings.size
                    
                if wm.paintLayer != 'Drive/Latch':
                    row = layout.row()
                    row.enabled = wm.clothPaintingMode
                    row.operator(SmoothAll.bl_idname, text="Smooth All", icon='SMOOTHCURVE')
                    
                row = layout.row()
                row.enabled = wm.clothPaintingMode
                row.operator(FloodAll.bl_idname, text="Flood All", icon='IMAGE')
        return
    
def updateMaximumMaxDistance(self, context):
    obj = context.active_object
    obj.modifiers["PinGroup"].node_group.nodes["Maximum Max Distance"].inputs[1].default_value = self.maximumMaxDistance
    
def updateClothPaintingMode(self, context):
    obj = context.active_object
    vgroups = applyDriveLatch(obj)
    mode = context.mode
    view_prefs = context.preferences.view
    context.scene.frame_set(0)
    if self.clothPaintingMode:
        self.previousMode = mode
        context.scene.frame_set(0)
        bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
        view_prefs.use_weight_color_range = True
        view_prefs.weight_color_range.color_mode = 'RGB'
        view_prefs.weight_color_range.interpolation = 'LINEAR'
        obj.show_wire = True
        
        if self.paintLayer != 'Drive/Latch':
            setCustomWeightPalette('DEFAULT')
            vgroups.active_index = vgroups[self.paintLayer].index
            if self.paintMode == 'Draw':
                set_active_tool('builtin_brush.Draw')
                context.tool_settings.weight_paint.brush = bpy.data.brushes['Draw']
                context.scene.tool_settings.unified_paint_settings.weight = self.paintValue
            else:
                set_active_tool('builtin_brush.Blur')
                context.tool_settings.weight_paint.brush = bpy.data.brushes['Blur']
                bpy.data.brushes['Blur'].strength = 1
            context.scene.tool_settings.unified_paint_settings.size = self.paintRadius
            if self.viewPaintVectors:
                PhysXDisplayPaintVectors.handle_add(PhysXDisplayPaintVectors, context)
            
        else:
            setCustomWeightPalette('DRIVE/LATCH')
            PhysXDisplayPaintVectors.handle_remove(PhysXDisplayPaintVectors, context)
            if self.driveLatchMode == 'Drive':
                vgroups.active_index = vgroups["PhysXDrive"+self.driveLatchGroup[5:]].index
            else:
                vgroups.active_index = vgroups["PhysXLatch"+self.driveLatchGroup[5:]].index
            updatePaintModeDriveLatch(self, context)
            
    else:
        PhysXDisplayPaintVectors.handle_remove(PhysXDisplayPaintVectors, context)
        view_prefs.use_weight_color_range = False
        obj.show_wire = False
        if mode == 'PAINT_WEIGHT': 
            bpy.ops.object.mode_set(mode=ConvertMode(self.previousMode))
    bpy.ops.wm.save_userpref()
        
def updatePaintLayer(self, context):
    vgroups = applyDriveLatch(context.active_object)
    if self.paintLayer != 'Drive/Latch':
        setCustomWeightPalette('DEFAULT')
        vgroups.active_index = vgroups[self.paintLayer].index
        if self.viewPaintVectors:
            PhysXDisplayPaintVectors.handle_add(PhysXDisplayPaintVectors, context)
    else:
        setCustomWeightPalette('DRIVE/LATCH')
        PhysXDisplayPaintVectors.handle_remove(PhysXDisplayPaintVectors, context)
        vgroups.active_index = vgroups["PhysX" + self.driveLatchMode + self.driveLatchGroup[5:]].index
        updatePaintModeDriveLatch(self, context)
        
def updateViewPaintVectors(self, context):
    PhysXDisplayPaintVectors.execute(PhysXDisplayPaintVectors, context)
    
def updatePaintMode(self, context):
    if self.paintMode == 'Draw':
        set_active_tool('builtin_brush.Draw')
        context.tool_settings.weight_paint.brush = bpy.data.brushes['Draw']
    else:
        set_active_tool('builtin_brush.Blur')
        context.tool_settings.weight_paint.brush = bpy.data.brushes['Blur']
        bpy.data.brushes['Blur'].strength = 1
        
def updatePaintValue(self, context):
    context.scene.tool_settings.unified_paint_settings.weight = self.paintValue
    
def updatePaintRadius(self, context):
    context.scene.tool_settings.unified_paint_settings.size = self.paintRadius
    
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
        
    vgroups.active_index = vgroups["PhysX" + self.driveLatchMode + self.driveLatchGroup[5:]].index
        
def updatePaintModeDriveLatch(self, context):
    set_active_tool('builtin_brush.Draw')
    w_paint = context.tool_settings.weight_paint
    w_paint.brush = bpy.data.brushes['Draw']
    w_paint.brush.curve_preset = 'CONSTANT'
    if self.paintModeDriveLatch == 'Add':
        context.scene.tool_settings.unified_paint_settings.weight = 1
    else: 
        context.scene.tool_settings.unified_paint_settings.weight = 0
        
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
('viewPaintVectors', BoolProperty(
        name="Visualize Paint Vectors",
        default = False,
        update = updateViewPaintVectors
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

CLASSES_Painting_Panel = [SmoothAll, FloodAll, PhysXDisplayPaintVectors, PhysXPaintingPanel]