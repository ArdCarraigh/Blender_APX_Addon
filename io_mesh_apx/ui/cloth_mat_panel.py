# -*- coding: utf-8 -*-
#ui/cloth_mat_panel.py

import bpy
import numpy as np
from bpy.props import BoolProperty, FloatProperty, IntProperty
from io_mesh_apx.utils import GetCollection, GetArmature
    
class PhysXClothMaterialPanel(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_PhysX_cloth_mat_panel'
    bl_parent_id = 'VIEW3D_PT_PhysX_panel'
    bl_label = 'PhysX Cloth Material'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'PhysX'
    bl_options = {'HIDE_HEADER'}
    
    def draw(self, context):
        layout = self.layout
        physx = context.window_manager.physx
        wm = physx.cloth
        if physx.PhysXSubPanel == 'cloth_mat':
            main_coll = GetCollection(make_active=False)
            arma = GetArmature()
            obj = context.active_object
            if main_coll and obj and obj in arma.children and obj.type == 'MESH':
                
                row = layout.row()
                box = row.box()
                box.label(text="Stiffness")
                box_row = box.row()
                box_row.prop(wm, "verticalStretchingStiffness", text = "Vertical Stretching Stiffness")
                if wm.verticalStretchingStiffness != obj["verticalStretchingStiffness"]:
                    wm.verticalStretchingStiffness = obj["verticalStretchingStiffness"]
                box_row = box.row()
                box_row.prop(wm, "horizontalStretchingStiffness", text = "Horizontal Stretching Stiffness")
                if wm.horizontalStretchingStiffness != obj["horizontalStretchingStiffness"]:
                    wm.horizontalStretchingStiffness = obj["horizontalStretchingStiffness"]
                box_row = box.row()
                box_row.prop(wm, "shearingStiffness", text = "Shearing Stiffness")
                if wm.shearingStiffness != obj["shearingStiffness"]:
                    wm.shearingStiffness = obj["shearingStiffness"]
                box_row = box.row()
                box_row.prop(wm, "bendingStiffness", text = "Bending Stiffness")
                if wm.bendingStiffness != obj["bendingStiffness"]:
                    wm.bendingStiffness = obj["bendingStiffness"]
                box_row = box.row()
                box_row.prop(wm, "tetherStiffness", text = "Tether Stiffness")
                if wm.tetherStiffness != obj["tetherStiffness"]:
                    wm.tetherStiffness = obj["tetherStiffness"]
                box_row = box.row()
                box_row.prop(wm, "tetherLimit", text = "Stretch Limit")
                if wm.tetherLimit != obj["tetherLimit"]:
                    wm.tetherLimit = obj["tetherLimit"]
                
                layout.separator()
                row = layout.row()
                box = row.box()
                box.label(text="Fiber Limits")
                box_row = box.row()
                box_row.label(text="Vertical")
                box_row = box.row()
                box_row.prop(wm, "verticalStiffnessScaling_compressionRange", text = "Compression Range")
                if wm.verticalStiffnessScaling_compressionRange != obj["verticalStiffnessScaling_compressionRange"]:
                    wm.verticalStiffnessScaling_compressionRange = obj["verticalStiffnessScaling_compressionRange"]
                box_row = box.row()
                box_row.prop(wm, "verticalStiffnessScaling_stretchRange", text = "Expansion Range")
                if wm.verticalStiffnessScaling_stretchRange != obj["verticalStiffnessScaling_stretchRange"]:
                    wm.verticalStiffnessScaling_stretchRange = obj["verticalStiffnessScaling_stretchRange"]
                box_row = box.row()
                box_row.prop(wm, "verticalStiffnessScaling_scale", text = "Scale")
                if wm.verticalStiffnessScaling_scale != obj["verticalStiffnessScaling_scale"]:
                    wm.verticalStiffnessScaling_scale = obj["verticalStiffnessScaling_scale"]
                box_row = box.row()
                box_row.label(text="Horizontal")
                box_row = box.row()
                box_row.prop(wm, "horizontalStiffnessScaling_compressionRange", text = "Compression Range")
                if wm.horizontalStiffnessScaling_compressionRange != obj["horizontalStiffnessScaling_compressionRange"]:
                    wm.horizontalStiffnessScaling_compressionRange = obj["horizontalStiffnessScaling_compressionRange"]
                box_row = box.row()
                box_row.prop(wm, "horizontalStiffnessScaling_stretchRange", text = "Expansion Range")
                if wm.horizontalStiffnessScaling_stretchRange != obj["horizontalStiffnessScaling_stretchRange"]:
                    wm.horizontalStiffnessScaling_stretchRange = obj["horizontalStiffnessScaling_stretchRange"]
                box_row = box.row()
                box_row.prop(wm, "horizontalStiffnessScaling_scale", text = "Scale")
                if wm.horizontalStiffnessScaling_scale != obj["horizontalStiffnessScaling_scale"]:
                    wm.horizontalStiffnessScaling_scale = obj["horizontalStiffnessScaling_scale"]
                box_row = box.row()
                box_row.label(text="Bending")
                box_row = box.row()
                box_row.prop(wm, "bendingStiffnessScaling_compressionRange", text = "Compression Range")
                if wm.bendingStiffnessScaling_compressionRange != obj["bendingStiffnessScaling_compressionRange"]:
                    wm.bendingStiffnessScaling_compressionRange = obj["bendingStiffnessScaling_compressionRange"]
                box_row = box.row()
                box_row.prop(wm, "bendingStiffnessScaling_stretchRange", text = "Expansion Range")
                if wm.bendingStiffnessScaling_stretchRange != obj["bendingStiffnessScaling_stretchRange"]:
                    wm.bendingStiffnessScaling_stretchRange = obj["bendingStiffnessScaling_stretchRange"]
                box_row = box.row()
                box_row.prop(wm, "bendingStiffnessScaling_scale", text = "Scale")
                if wm.bendingStiffnessScaling_scale != obj["bendingStiffnessScaling_scale"]:
                    wm.bendingStiffnessScaling_scale = obj["bendingStiffnessScaling_scale"]
                box_row = box.row()
                box_row.label(text="Shearing")
                box_row = box.row()
                box_row.prop(wm, "shearingStiffnessScaling_compressionRange", text = "Compression Range")
                if wm.shearingStiffnessScaling_compressionRange != obj["shearingStiffnessScaling_compressionRange"]:
                    wm.shearingStiffnessScaling_compressionRange = obj["shearingStiffnessScaling_compressionRange"]
                box_row = box.row()
                box_row.prop(wm, "shearingStiffnessScaling_stretchRange", text = "Expansion Range")
                if wm.shearingStiffnessScaling_stretchRange != obj["shearingStiffnessScaling_stretchRange"]:
                    wm.shearingStiffnessScaling_stretchRange = obj["shearingStiffnessScaling_stretchRange"]
                box_row = box.row()
                box_row.prop(wm, "shearingStiffnessScaling_scale", text = "Scale")
                if wm.shearingStiffnessScaling_scale != obj["shearingStiffnessScaling_scale"]:
                    wm.shearingStiffnessScaling_scale = obj["shearingStiffnessScaling_scale"]
                
                layout.separator()
                row = layout.row()
                box = row.box()
                box.label(text="Inertia")
                box_row = box.row()
                box_row.prop(wm, "damping", text = "Damping")
                if wm.damping != obj["damping"]:
                    wm.damping = obj["damping"]
                box_row = box.row()
                box_row.prop(wm, "stiffnessFrequency", text = "Stiffness Frequency")
                if wm.stiffnessFrequency != obj["stiffnessFrequency"]:
                    wm.stiffnessFrequency = obj["stiffnessFrequency"]
                box_row = box.row()
                box_row.prop(wm, "drag", text = "Drag")
                if wm.drag != obj["drag"]:
                    wm.drag = obj["drag"]
                box_row = box.row()
                box_row.prop(wm, "comDamping", text = "Center Of Mass Damping")
                if wm.comDamping != obj["comDamping"]:
                    wm.comDamping = obj["comDamping"]
                box_row = box.row()
                box_row.prop(wm, "friction", text = "Friction")
                if wm.friction != obj["friction"]:
                    wm.friction = obj["friction"]
                box_row = box.row()
                box_row.prop(wm, "massScale", text = "Motion Adaptation")
                if wm.massScale != obj["massScale"]:
                    wm.massScale = obj["massScale"]
                box_row = box.row()
                box_row.prop(wm, "inertiaScale", text = "Inertia Blend")
                if wm.inertiaScale != obj["inertiaScale"]:
                    wm.inertiaScale = obj["inertiaScale"]
                
                layout.separator()
                row = layout.row()
                box = row.box()
                box.label(text="Self Collision")
                box_row = box.row()
                box_row.prop(wm, "selfcollisionThickness", text = "Self Collision Thickness")
                if wm.selfcollisionThickness != obj["selfcollisionThickness"]:
                    wm.selfcollisionThickness = obj["selfcollisionThickness"]
                box_row = box.row()
                box_row.prop(wm, "selfcollisionStiffness", text = "Self Collision Stiffness")
                if wm.selfcollisionStiffness != obj["selfcollisionStiffness"]:
                    wm.selfcollisionStiffness = obj["selfcollisionStiffness"]
                box_row = box.row()
                box_row.prop(wm, "selfcollisionSquashScale", text = "Self Collision Squash Scale")
                if wm.selfcollisionSquashScale != obj["selfcollisionSquashScale"]:
                    wm.selfcollisionSquashScale = obj["selfcollisionSquashScale"]
                
                layout.separator()
                row = layout.row()
                box = row.box()
                box.label(text="Solver")
                box_row = box.row()
                box_row.prop(wm, "solverIterations", text = "Solver Iterations")
                if wm.solverIterations != obj["solverIterations"]:
                    wm.solverIterations = obj["solverIterations"]
                box_row = box.row()
                box_row.prop(wm, "solverFrequency", text = "Solver Frequency")
                if wm.solverFrequency != obj["solverFrequency"]:
                    wm.solverFrequency = obj["solverFrequency"]
                box_row = box.row()
                box_row.prop(wm, "hierarchicalSolverIterations", text = "Hierarchical Solver Iterations")
                if wm.hierarchicalSolverIterations != obj["hierarchicalSolverIterations"]:
                    wm.hierarchicalSolverIterations = obj["hierarchicalSolverIterations"]
                
                layout.separator()
                row = layout.row()
                box = row.box()
                box.label(text="Miscellaneous")
                box_row = box.row()
                box_row.prop(wm, "orthoBending", text = "Orthogonal Bending Resistance")
                if wm.orthoBending != obj["orthoBending"]:
                    wm.orthoBending = obj["orthoBending"]
                box_row = box.row()
                box_row.prop(wm, "gravityScale", text = "Gravity Multiplier")
                if wm.gravityScale != obj["gravityScale"]:
                    wm.gravityScale = obj["gravityScale"]
                box_row = box.row()
                box_row.prop(wm, "hardStretchLimitation", text = "Hard Stretch Limitation")
                if wm.hardStretchLimitation != obj["hardStretchLimitation"]:
                    wm.hardStretchLimitation = obj["hardStretchLimitation"]
                box_row = box.row()
                box_row.prop(wm, "maxDistanceBias", text = "Max Distance Bias")
                if wm.maxDistanceBias != obj["maxDistanceBias"]:
                    wm.maxDistanceBias = obj["maxDistanceBias"]    
                    
        return
    
def updateStiffness(self, context, obj):
    settings = obj.modifiers["ClothSimulation"].settings
    stiffness = np.mean([self.verticalStretchingStiffness, self.horizontalStretchingStiffness])
    settings.tension_stiffness = stiffness * 15
    settings.compression_stiffness = stiffness * 15
    
def updateSelfCollision(self, context, obj):
    settings = obj.modifiers["ClothSimulation"].collision_settings
    settings.self_distance_min = self.selfcollisionThickness * 0.125
    settings.self_friction = self.selfcollisionStiffness * 80
    if self.selfcollisionStiffness and self.selfcollisionThickness:
        settings.use_self_collision = True
    else:
        settings.use_self_collision = False
        
def updateVerticalStretchingStiffness(self, context):
    obj = context.active_object
    obj["verticalStretchingStiffness"] = self.verticalStretchingStiffness
    updateStiffness(self, context, obj)
    
def updateHorizontalStretchingStiffness(self, context):
    obj = context.active_object
    obj["horizontalStretchingStiffness"] = self.horizontalStretchingStiffness
    updateStiffness(self, context, obj)
    
def updateBendingStiffness(self, context):
    obj = context.active_object
    obj["bendingStiffness"] = self.bendingStiffness
    obj.modifiers["ClothSimulation"].settings.bending_stiffness = self.bendingStiffness * 15
    
def updateShearingStiffness(self, context):
    obj = context.active_object
    obj["shearingStiffness"] = self.shearingStiffness
    obj.modifiers["ClothSimulation"].settings.shear_stiffness = self.shearingStiffness * 15
    
def updateTetherStiffness(self, context):
    context.active_object["tetherStiffness"] = self.tetherStiffness
    
def updateTetherLimit(self, context):
    context.active_object["tetherLimit"] = self.tetherLimit
    
def updateOrthoBending(self, context):
    context.active_object["orthoBending"] = self.orthoBending
    
def updateVerticalStiffnessScaling_compressionRange(self, context):
    context.active_object["verticalStiffnessScaling_compressionRange"] = self.verticalStiffnessScaling_compressionRange
    
def updateVerticalStiffnessScaling_stretchRange(self, context):
    context.active_object["verticalStiffnessScaling_stretchRange"] = self.verticalStiffnessScaling_stretchRange
    
def updateVerticalStiffnessScaling_scale(self, context):
    context.active_object["verticalStiffnessScaling_scale"] = self.verticalStiffnessScaling_scale
    
def updateHorizontalStiffnessScaling_compressionRange(self, context):
    context.active_object["horizontalStiffnessScaling_compressionRange"] = self.horizontalStiffnessScaling_compressionRange
    
def updateHorizontalStiffnessScaling_stretchRange(self, context):
    context.active_object["horizontalStiffnessScaling_stretchRange"] = self.horizontalStiffnessScaling_stretchRange
    
def updateHorizontalStiffnessScaling_scale(self, context):
    context.active_object["horizontalStiffnessScaling_scale"] = self.horizontalStiffnessScaling_scale
    
def updateBendingStiffnessScaling_compressionRange(self, context):
    context.active_object["bendingStiffnessScaling_compressionRange"] = self.bendingStiffnessScaling_compressionRange
    
def updateBendingStiffnessScaling_stretchRange(self, context):
    context.active_object["bendingStiffnessScaling_stretchRange"] = self.bendingStiffnessScaling_stretchRange
    
def updateBendingStiffnessScaling_scale(self, context):
    context.active_object["bendingStiffnessScaling_scale"] = self.bendingStiffnessScaling_scale
    
def updateShearingStiffnessScaling_compressionRange(self, context):
    context.active_object["shearingStiffnessScaling_compressionRange"] = self.shearingStiffnessScaling_compressionRange
    
def updateShearingStiffnessScaling_stretchRange(self, context):
    context.active_object["shearingStiffnessScaling_stretchRange"] = self.shearingStiffnessScaling_stretchRange
    
def updateShearingStiffnessScaling_scale(self, context):
    context.active_object["shearingStiffnessScaling_scale"] = self.shearingStiffnessScaling_scale
    
def updateDamping(self, context):
    obj = context.active_object
    settings = obj.modifiers["ClothSimulation"].settings
    obj["damping"] = self.damping
    settings.tension_damping = self.damping
    settings.compression_damping = self.damping
    if "drag" in obj and obj["drag"] > obj["damping"]:
        obj["drag"] = obj["damping"]
    
def updateStiffnessFrequency(self, context):
    context.active_object["stiffnessFrequency"] = self.stiffnessFrequency
    
def updateDrag(self, context):
    obj = context.active_object
    obj["drag"] = self.drag
    if obj["drag"] > obj["damping"]:
        obj["drag"] = obj["damping"]
    obj.modifiers["ClothSimulation"].settings.effector_weights.drag = obj["drag"]
    
def updateComDamping(self, context):
    context.active_object["comDamping"] = self.comDamping
    
def updateFriction(self, context):
    context.active_object["friction"] = self.friction
    sphere_coll = GetCollection("Collision Spheres", make_active=False) 
    connection_coll = GetCollection("Collision Connections", make_active=False) 
    capsule_coll = GetCollection("Collision Capsules", make_active=False)
    
    objects = []
    if sphere_coll:
        objects.extend(sphere_coll.objects)
    if connection_coll:
        objects.extend(connection_coll.objects)
    if capsule_coll:
        objects.extend(capsule_coll.objects)
    
    for obj in objects:
        obj.modifiers['Collision'].settings.cloth_friction = self.friction * 80
    
def updateMassScale(self, context):
    context.active_object["massScale"] = self.massScale
    
def updateSolverIterations(self, context):
    obj = context.active_object
    obj["solverIterations"] = self.solverIterations
    obj.modifiers["ClothSimulation"].settings.quality = self.solverIterations
    
def updateSolverFrequency(self, context):
    context.active_object["solverFrequency"] = self.solverFrequency
    
def updateGravityScale(self, context):
    obj = context.active_object
    obj["gravityScale"] = self.gravityScale
    obj.modifiers["ClothSimulation"].settings.effector_weights.gravity = self.gravityScale * -self.gravityDirection[2]
    
def updateInertiaScale(self, context):
    obj = context.active_object
    obj["inertiaScale"] = self.inertiaScale
    inertia = self.inertiaScale
    if inertia < 0.1:
        inertia = 0.1
    obj.modifiers["ClothSimulation"].settings.air_damping = 1 / inertia
    
def updateHardStretchLimitation(self, context):
    context.active_object["hardStretchLimitation"] = self.hardStretchLimitation
    
def updateMaxDistanceBias(self, context):
    context.active_object["maxDistanceBias"] = self.maxDistanceBias
    
def updateHierarchicalSolverIterations(self, context):
    context.active_object["hierarchicalSolverIterations"] = self.hierarchicalSolverIterations

def updateSelfCollisionThickness(self, context):
    obj = context.active_object
    obj["selfcollisionThickness"] = self.selfcollisionThickness
    updateSelfCollision(self, context, obj)

def updateSelfCollisionSquashScale(self, context):
    context.active_object["selfcollisionSquashScale"] = self.selfcollisionSquashScale

def updateSelfCollisionStiffness(self, context):
    obj = context.active_object
    obj["selfcollisionStiffness"] = self.selfcollisionStiffness
    updateSelfCollision(self, context, obj)
        
PROPS_ClothMaterial_Panel = [
('verticalStretchingStiffness', FloatProperty(
        name="Vertical Stretching Stiffness",
        description="Vertical stretching stiffness of the cloth in the range [0, 1]. This parameter is ignored by the PhysX 2.8.4 solver. Should be set to 1 because cloth doesn't stretch under gravity",
        default=1,
        min=0,
        max=1,
        update=updateVerticalStretchingStiffness
    )),
('horizontalStretchingStiffness', FloatProperty(
        name="Horizontal Stretching Stiffness",
        description="Horizontal Stretching stiffness of the cloth in the range (0, 1]",
        default=1,
        min=0,
        max=1,
        update=updateHorizontalStretchingStiffness
    )),
('bendingStiffness', FloatProperty(
        name="Bending Stiffness",
        description="Bending stiffness of the cloth in the range [0, 1]. Can be set pretty high because these forces are pretty soft",
        default=0.5,
        min=0,
        max=1,
        update=updateBendingStiffness
    )),
('shearingStiffness', FloatProperty(
        name="Shearing Stiffness",
        description="Shearing stiffness of the cloth in the range [0, 1]. Can be set pretty high because these forces are pretty soft. If horizontal stretching is desired, high shear resistance should be avoided",
        default=0.5,
        min=0,
        max=1,
        update=updateShearingStiffness
    )),
('tetherStiffness', FloatProperty(
        name="Tether Stiffness",
        description="Range [0, 1], but should be 1. The lower this value, the more the piece of clothing is allowed to stretch",
        default=1,
        min=0,
        max=1,
        update=updateTetherStiffness
    )),
('tetherLimit', FloatProperty(
        name="Tether Limit",
        description="Range [1, 4], but should be 1. This scales the restlength of the tether constraints. The higher this value, the more the piece of clothing is allowed to stretch",
        default=1,
        min=1,
        max=4,
        update=updateTetherLimit
    )),
('orthoBending', BoolProperty(
        name="Ortho Bending",
        description="Enable/disable orthogonal bending resistance. Bending is modeled via an angular spring between adjacent triangles. This mode is slower but independent of stretching resistance. It is a mathematically more correct version of bending but it comes at some performance cost and rarely with a gain in quality",
        default=False,
        update=updateOrthoBending
    )),
('verticalStiffnessScaling_compressionRange', FloatProperty(
        name="Vertical Stiffness Scaling Compression Range",
        description="Multiplier relative to rest length that defines where the stiffness is scaled down to allow compression. For any edge where the simulated length is within the range [restlength, compressionRange*restlength], the scale will be multiplied on top of the regular stiffness. This is can be used to allow the cloth to compress more easily up to a certain limit",
        default=1,
        min=0,
        max=1,
        update=updateVerticalStiffnessScaling_compressionRange
    )),
('verticalStiffnessScaling_stretchRange', FloatProperty(
        name="Vertical Stiffness Scaling Stretch Range",
        description="Multiplier relative to rest length that defines the range where the stiffness is scaled down to allow stretching. For any edge where the simulated length is within the range [restlength, stretchRange*restlength], the scale will be multiplied on top of the regular stiffness. This is can be used to allow the cloth to stretch more easily up to a certain limit",
        default=1,
        min=1,
        max=3,
        update=updateVerticalStiffnessScaling_stretchRange
    )),
('verticalStiffnessScaling_scale', FloatProperty(
        name="Vertical Stiffness Scaling Scale",
        description="Stiffness scale [0, 1] applied when inside the scaling range",
        default=0.5,
        min=0,
        max=1,
        update=updateVerticalStiffnessScaling_scale
    )),
('horizontalStiffnessScaling_compressionRange', FloatProperty(
        name="Horizontal Stiffness Scaling Compression Range",
        description="Multiplier relative to rest length that defines where the stiffness is scaled down to allow compression. For any edge where the simulated length is within the range [restlength, compressionRange*restlength], the scale will be multiplied on top of the regular stiffness. This is can be used to allow the cloth to compress more easily up to a certain limit",
        default=1,
        min=0,
        max=1,
        update=updateHorizontalStiffnessScaling_compressionRange
    )),
('horizontalStiffnessScaling_stretchRange', FloatProperty(
        name="Horizontal Stiffness Scaling Stretch Range",
        description="Multiplier relative to rest length that defines the range where the stiffness is scaled down to allow stretching. For any edge where the simulated length is within the range [restlength, stretchRange*restlength], the scale will be multiplied on top of the regular stiffness. This is can be used to allow the cloth to stretch more easily up to a certain limit",
        default=1,
        min=1,
        max=3,
        update=updateHorizontalStiffnessScaling_stretchRange
    )),
('horizontalStiffnessScaling_scale', FloatProperty(
        name="Horizontal Stiffness Scaling Scale",
        description="Stiffness scale [0, 1] applied when inside the scaling range",
        default=0.5,
        min=0,
        max=1,
        update=updateHorizontalStiffnessScaling_scale
    )),
('bendingStiffnessScaling_compressionRange', FloatProperty(
        name="Bending Stiffness Scaling Compression Range",
        description="Multiplier relative to rest length that defines where the stiffness is scaled down to allow compression. For any edge where the simulated length is within the range [restlength, compressionRange*restlength], the scale will be multiplied on top of the regular stiffness. This is can be used to allow the cloth to compress more easily up to a certain limit",
        default=1,
        min=0,
        max=1,
        update=updateBendingStiffnessScaling_compressionRange
    )),
('bendingStiffnessScaling_stretchRange', FloatProperty(
        name="Bending Stiffness Scaling Stretch Range",
        description="Multiplier relative to rest length that defines the range where the stiffness is scaled down to allow stretching. For any edge where the simulated length is within the range [restlength, stretchRange*restlength], the scale will be multiplied on top of the regular stiffness. This is can be used to allow the cloth to stretch more easily up to a certain limit",
        default=1,
        min=1,
        max=3,
        update=updateBendingStiffnessScaling_stretchRange
    )),
('bendingStiffnessScaling_scale', FloatProperty(
        name="Bending Stiffness Scaling Scale",
        description="Stiffness scale [0, 1] applied when inside the scaling range",
        default=0.5,
        min=0,
        max=1,
        update=updateBendingStiffnessScaling_scale
    )),
('shearingStiffnessScaling_compressionRange', FloatProperty(
        name="Shearing Stiffness Scaling Compression Range",
        description="Multiplier relative to rest length that defines where the stiffness is scaled down to allow compression. For any edge where the simulated length is within the range [restlength, compressionRange*restlength], the scale will be multiplied on top of the regular stiffness. This is can be used to allow the cloth to compress more easily up to a certain limit",
        default=1,
        min=0,
        max=1,
        update=updateShearingStiffnessScaling_compressionRange
    )),
('shearingStiffnessScaling_stretchRange', FloatProperty(
        name="Shearing Stiffness Scaling Stretch Range",
        description="Multiplier relative to rest length that defines the range where the stiffness is scaled down to allow stretching. For any edge where the simulated length is within the range [restlength, stretchRange*restlength], the scale will be multiplied on top of the regular stiffness. This is can be used to allow the cloth to stretch more easily up to a certain limit",
        default=1,
        min=1,
        max=3,
        update=updateShearingStiffnessScaling_stretchRange
    )),
('shearingStiffnessScaling_scale', FloatProperty(
        name="Shearing Stiffness Scaling Scale",
        description="Stiffness scale [0, 1] applied when inside the scaling range",
        default=0.5,
        min=0,
        max=1,
        update=updateShearingStiffnessScaling_scale
    )),
('damping', FloatProperty(
        name="Damping",
        description="Spring damping of the cloth in the range [0, 1]. Damps particle velocity relative to the simulation space (differs for global and local space simulation). This does not damp absolute velocity, only oscillations in edges",
        default=0.1,
        min=0,
        max=1,
        update=updateDamping
    )),
('stiffnessFrequency', FloatProperty(
        name="Stiffness Frequency",
        description="Scales linearity of behavior for the various stiffness values in the interval [0, 1]",
        default=100,
        min=10,
        max=500,
        update=updateStiffnessFrequency
    )),
('drag', FloatProperty(
        name="Drag",
        description="Drag coefficient in the range [0, 1]. Adds a drag force to the simulation space. Must not be bigger than the damping value! The drag coefficient is the portion of local frame velocity that is applied to each particle",
        default=0,
        min=0,
        max=1,
        update=updateDrag
    )),
('comDamping', BoolProperty(
        name="Center of Mass Damping",
        description="Enable/disable damping of internal velocities relative to the center of mass of the mesh. If set, the global rigid body modes (translation and rotation) are extracted from damping. This way, the cloth can freely move and rotate even under high damping. Behaves a bit like a metal plate, but does not work very well on characters",
        default=False,
        update=updateComDamping
    )),
('friction', FloatProperty(
        name="Friction",
        description="Friction coefficient in the range [0, 1]. Friction with collision volumes or the amount of velocity that is removed when sliding over a surface. Currently only spheres and capsules impose friction on the colliding particles",
        default=0.25,
        min=0,
        max=1,
        update=updateFriction
    )),
('massScale', FloatProperty(
        name="Mass Scale",
        description="Controls the amount of mass scaling during collision [0, 100]. Temporarily increases mass of colliding particles. Can enhance collision behavior",
        default=25,
        min=0,
        max=100,
        update=updateMassScale
    )),
('solverIterations', IntProperty(
        name="Solver Iterations",
        description="Number of solver iterations. For 2.x cloth. Small numbers make the simulation faster while the cloth gets less stiff. Higher number can reduce some stretching, but scales very linear with performance. A value of 5 is a good start, but if it also works with lower version, performance will be better",
        default=5,
        min=0,
        update=updateSolverIterations
    )),
('solverFrequency', FloatProperty(
        name="Solver Frequency",
        description="Number of solver iterations per second. For 3.x cloth. Small numbers make the simulation faster while the cloth gets less stiff",
        default=250,
        min=1,
        max = 1000,
        update=updateSolverFrequency
    )),
('gravityScale', FloatProperty(
        name="Gravity Scale",
        description="Amount of gravity that is applied to the cloth. A value of 0 will make the cloth ignore gravity, a value of 10 will apply 10 times the gravity",
        default=1,
        min=0,
        max=100,
        update=updateGravityScale
    )),
('inertiaScale', FloatProperty(
        name="Inertia Scale",
        description="Amount of inertia that is kept when using local space simulation. Amount of inertia that is trasnfered from an accelerated simulation space to the particle velocities. A value of 0 will make the cloth move in global space without inertia, a value of 1 will keep all inertia",
        default=1,
        min=0,
        max=1,
        update=updateInertiaScale
    )),
('hardStretchLimitation', FloatProperty(
        name="Hard Stretch Limitation",
        description="Make cloth simulation less stretchy. A value smaller than 1 will turn it off. Good values are usually between 1 and 1.1. Any value >= 1 will guarantee that a certain set of edges is not longer than that value times the initial rest length",
        default=0,
        min=0,
        max=2,
        update=updateHardStretchLimitation
    )),
('maxDistanceBias', FloatProperty(
        name="Max Distance Bias",
        description="Deform the max distance sphere into a capsule or a disc. A value smaller than 0 will turn the sphere into a capsule and eventually a line (at value -1) along the normal of the vertex. A value bigger than 0 will turn the sphere into a disc and becomes a flat circle in the tangential plane at 1",
        default=0,
        min=-1,
        max=1,
        update=updateMaxDistanceBias
    )),
('hierarchicalSolverIterations', IntProperty(
        name="Hierarchical Solver Iterations",
        description="Number of iterations of the hierarchical cloth solver. Amount of iterations done on the hierarchical mesh. This is a workaround for fixing high stretching. Must not be used in conjunction with the hard stretch limitation",
        default=0,
        min=0,
        update=updateHierarchicalSolverIterations
    )),
('selfcollisionThickness', FloatProperty(
        name="Self Collision Thickness",
        description="Minimal amount of distance particles will keep of each other. This feature prevents meshes from self-intersecting. Only works properly when configured properly. As usual the rule is: keep them as small as possible, but as big as needed",
        default=0,
        min=0,
        max=0.8,
        update=updateSelfCollisionThickness
    )),
('selfcollisionSquashScale', FloatProperty(
        name="Self Collision Squash Scale",
        description="Amount of thickness scaling along surface normal. This feature prevents self collision thickness becoming too high for low resolution cloth",
        default=0,
        update=updateSelfCollisionSquashScale
    )),
('selfcollisionStiffness', FloatProperty(
        name="Self Collision Stiffness",
        description="Stiffness of self collision solver. This feature prevents meshes from self-intersecting. Only works properly when configured properly",
        default=0,
        min=0,
        max=1,
        update=updateSelfCollisionStiffness
    ))
]

CLASSES_ClothMaterial_Panel = [PhysXClothMaterialPanel]