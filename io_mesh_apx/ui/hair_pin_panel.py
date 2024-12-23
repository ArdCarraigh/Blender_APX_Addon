# -*- coding: utf-8 -*-
# ui/hair_pin_panel.py

import bpy
import numpy as np
from copy import deepcopy
from mathutils import Vector
from bpy.props import FloatProperty, FloatVectorProperty, IntProperty, BoolProperty, EnumProperty
from bpy.types import Operator
from io_mesh_apx.tools.hair_tools import add_pin, remove_pin
from io_mesh_apx.utils import GetCollection, selectOnly, GetArmature, getBones

class AddPinSphere(Operator):
    """Create a new Pin Sphere"""
    bl_idname = "physx.add_pin_sphere"
    bl_label = "Add Pin Sphere"
    bl_options = {'REGISTER', 'UNDO'}
    bl_property = "bone"

    radius: FloatProperty(
        name="Radius",
        default = 0.15,
        min = 0,
        description="Set the radius of the sphere",
    )
    location: FloatVectorProperty(
        name="Location",
        default=(0, 0, 0),
        description="Set the location of the sphere",
        subtype = 'COORDINATES'
    )
    use_location: BoolProperty(
        name="Use Location",
        default=False,
        description="Use custom location, or bone location"
    )
    bone: EnumProperty(
        options={'HIDDEN'},
        name="Bone",
        items=getBones
    )
    
    def execute(self, context):
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
        add_pin(context, self.bone, self.radius, self.location, self.use_location)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'RUNNING_MODAL'}
    
class RemovePinSphere(Operator):
    """Remove a Pin Sphere"""
    bl_idname = "physx.remove_pin_sphere"
    bl_label = "Remove Pin Sphere"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
        wm = bpy.context.window_manager.physx.hair
        index = wm.PhysXPinSpheresIndex
        remove_pin(context, index)
        if not index:
            wm.PhysXPinSpheresIndex = 0
        elif index > 0:
            wm.PhysXPinSpheresIndex = index - 1    
        return {'FINISHED'}
                                    
class PHYSX_UL_pins(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        coll = data
        ob = item
            
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if ob:
                layout.prop(ob, "name", text="", emboss=False)
            else:
                layout.label(text="", translate=False)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="")
                                        
class PhysXHairPinPanel(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_PhysX_hair_pin_panel'
    bl_parent_id = 'VIEW3D_PT_PhysX_panel'
    bl_label = 'Hairworks Pins'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'PhysX'
    bl_options = {'HIDE_HEADER'}
    
    def draw(self, context):
        layout = self.layout
        physx = context.window_manager.physx
        wm = physx.hair
        if physx.PhysXSubPanel == 'hair_pin':
            main_coll = GetCollection(make_active=False)
            if main_coll:
                    
                pin_coll = GetCollection("Pin Constraints", make_active=False)
                
                row = layout.row()
                col = row.column()
                col.operator(AddPinSphere.bl_idname, text="Add")
                col = row.column()
                col.enabled = wm.PhysXPinSpheresIndex != -1
                col.operator(RemovePinSphere.bl_idname, text = "Remove")    
                row = layout.row()
                if pin_coll:
                    row.template_list("PHYSX_UL_pins", "", pin_coll, "objects", wm, "PhysXPinSpheresIndex", rows=3)
                    index_sphere = np.where(np.array(pin_coll.objects) == bpy.context.active_object)[0]
                    if index_sphere.size:
                        if wm.PhysXPinSpheresIndex != index_sphere[0]:
                            wm.PhysXPinSpheresIndex = index_sphere[0]
                    else:
                        wm.PhysXPinSpheresIndex = -1
                        
                    row = layout.row()
                    row.enabled = wm.PhysXPinSpheresIndex != -1
                    row.prop(wm, "pinRadius", text = "Radius")
                
                    obj = pin_coll.objects[wm.PhysXPinSpheresIndex]
                    row = layout.row()
                    row.enabled = wm.PhysXPinSpheresIndex != -1
                    row.prop(wm, "doLra", text = "doLra")
                    if wm.doLra != obj["doLra"]:
                        wm.doLra = obj["doLra"]
                    
                    row = layout.row()
                    row.enabled = wm.PhysXPinSpheresIndex != -1
                    row.prop(wm, "useDynamicPin1", text = "Dynamic Pin")
                    if wm.useDynamicPin1 != obj["useDynamicPin1"]:
                        wm.useDynamicPin1 = obj["useDynamicPin1"]
                    
                    row = layout.row()
                    row.enabled = wm.PhysXPinSpheresIndex != -1
                    row.prop(wm, "useStiffnessPin", text = "Tether Pin")
                    if wm.useStiffnessPin != obj["useStiffnessPin"]:
                        wm.useStiffnessPin = obj["useStiffnessPin"]
                        
                    row = layout.row()
                    row.enabled = wm.PhysXPinSpheresIndex != -1
                    row.prop(wm, "pinStiffness1", text = "Stiffness")
                    if wm.pinStiffness1 != obj["pinStiffness1"]:
                        wm.pinStiffness1 = obj["pinStiffness1"]
                        
                    row = layout.row()
                    row.enabled = wm.PhysXPinSpheresIndex != -1
                    split = row.split(factor = 0.85, align = True)
                    split.prop(wm, "influenceFallOff", text = "Influence Fall Off")
                    if wm.influenceFallOff != obj["influenceFallOff"]:
                        wm.influenceFallOff = obj["influenceFallOff"]
                    split.prop(wm, "influenceFallOffCurveToggle", text = "", toggle = True, icon = "FCURVE")
                    if wm.influenceFallOffCurveToggle:
                        row = layout.row()
                        row.enabled = wm.PhysXPinSpheresIndex != -1
                        row.prop(wm, "influenceFallOffCurve", text = "")
                        if not all(np.array(wm.influenceFallOffCurve) == np.array(obj["influenceFallOffCurve"])):
                            wm.influenceFallOffCurve = obj["influenceFallOffCurve"]
                        col = layout.column()
                        col.enabled = False
                        col.template_curve_mapping(obj.modifiers["InfluenceFallOffCurve"].node_group.nodes["Float Curve"], "mapping")
            
        return
            
def updatePhysXPinSpheresIndex(self, context):
    pin_coll = GetCollection("Pin Constraints", make_active=False)      
    if pin_coll:
        if pin_coll.objects and self.PhysXPinSpheresIndex != -1:
            selectOnly(pin_coll.objects[self.PhysXPinSpheresIndex])
            
def updatedoLra(self, context):
    context.active_object["doLra"] = self.doLra
    
def updateUseDynamicPin1(self, context):
    context.active_object["useDynamicPin1"] = self.useDynamicPin1
    
def updateUseStiffnessPin(self, context):
    context.active_object["useStiffnessPin"] = self.useStiffnessPin
    
def updatePinStiffness1(self, context):
    context.active_object["pinStiffness1"] = self.pinStiffness1
    
def updateInfluenceFallOff(self, context):
    context.active_object["influenceFallOff"] = self.influenceFallOff
    
def updateInfluenceFallOffCurve(self, context):
    obj = context.active_object
    obj["influenceFallOffCurve"] = self.influenceFallOffCurve
    mapping = obj.modifiers["InfluenceFallOffCurve"].node_group.nodes["Float Curve"].mapping
    for i, point in enumerate(mapping.curves[0].points):
        point.location[1] = self.influenceFallOffCurve[i]
    mapping.update()
    
def updatePinRadius(self, context):
    pin = context.active_object
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='MEDIAN')
    Radius = np.linalg.norm(pin.data.vertices[0].co)
    pin.scale = [self.pinRadius / Radius] * 3
    
PROPS_HairPin_Panel = [
("PhysXPinSpheresIndex", IntProperty(
        name = "Index of the Hairworks Pin",
        update = updatePhysXPinSpheresIndex,
        default = -1
    )),
("doLra", BoolProperty(
        name = "doLra?",
        update = updatedoLra,
        default = False
    )),
("useDynamicPin1", BoolProperty(
        name = "Use Dynamic Pin",
        description = "This setting causes the hair to have dynamic movement based on the collective simulation of hair cv’s clumped together in it’s volume",
        update = updateUseDynamicPin1,
        default = False
    )),
("useStiffnessPin", BoolProperty(
        name = "Use Stiffness Pin",
        description = "When dynamic hair pin is enabled, this eliminates any stretching of the pin by using a constraint between the hair pin and the bone it is attached to",
        update = updateUseStiffnessPin,
        default = False
    )),
("pinStiffness1", FloatProperty(
        name = "Pin Stiffness",
        description = "This refers to the strength pin constraint. The center of the pin volume will have strength equal to the Pin Stiffness value, but will falloff in strength to the outer edge of the volume",
        update = updatePinStiffness1,
        default = 0,
        min = 0,
        max = 1
    )),
("influenceFallOff", FloatProperty(
        name = "Influence FallOff",
        description = "The strength falloff of the stiffness value from the center to the edge of the hair pin sphere",
        update = updateInfluenceFallOff,
        default = 0,
        min = 0,
        max = 1
    )),
("influenceFallOffCurveToggle", BoolProperty(
        name = "Influence FallOff Curve Toggle",
        default = False
    )),
("influenceFallOffCurve", FloatVectorProperty(
        name = "Influence FallOff Curve",
        update = updateInfluenceFallOffCurve,
        size = 4,
        default = (0,0,0,0),
        min = -0.2,
        max = 1.2
    )),
("pinRadius", FloatProperty(
        name = "Hair Pin Radius",
        update = updatePinRadius,
        min = 0.01
    ))
]

CLASSES_HairPin_Panel = [AddPinSphere, RemovePinSphere, PHYSX_UL_pins, PhysXHairPinPanel]