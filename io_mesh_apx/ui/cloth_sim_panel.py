# -*- coding: utf-8 -*-
#ui/cloth_sim_panel.py

import bpy
import numpy as np
from bpy.props import BoolProperty, FloatProperty, IntProperty, IntVectorProperty
from io_mesh_apx.utils import GetCollection, GetWind, GetArmature
    
class PhysXClothSimulationPanel(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_PhysX_cloth_sim_panel'
    bl_parent_id = 'VIEW3D_PT_PhysX_panel'
    bl_label = 'PhysX Cloth Simulation'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'PhysX'
    bl_options = {'HIDE_HEADER'}
    
    def draw(self, context):
        layout = self.layout
        physx = context.window_manager.physx
        wm = physx.cloth
        if physx.PhysXSubPanel == 'cloth_sim':
            main_coll = GetCollection(make_active=False)
            if main_coll:
                
                row = layout.row()
                box = row.box()
                box.label(text="Simulation", icon="WORLD")
                box_row = box.row()
                box_row.prop(wm, "disableCCD", text = "Disable CCD")
                if wm.disableCCD != main_coll["disableCCD"]:
                    wm.disableCCD = main_coll["disableCCD"]
                box_row = box.row()
                box_row.prop(wm, "untangling", text = "Untangling")
                if wm.untangling != main_coll["untangling"]:
                    wm.untangling = main_coll["untangling"]
                box_row = box.row()
                box_row.prop(wm, "twowayInteraction", text = "Two Way Interaction")
                if wm.twowayInteraction != main_coll["twowayInteraction"]:
                    wm.twowayInteraction = main_coll["twowayInteraction"]
                box_row = box.row()
                box_row.label(text="Gravity Direction")
                box_row = box.row()
                box_row.prop(wm, "gravityDirection", text="")
                if not all(np.array(wm.gravityDirection) == np.array(main_coll["gravityDirection"])):
                    wm.gravityDirection = main_coll["gravityDirection"]
                box_row = box.row()
                box_row.prop(wm, "thickness", text = "Simulation Thickness")
                if wm.thickness != main_coll["thickness"]:
                    wm.thickness = main_coll["thickness"]
                box_row = box.row()
                box_row.prop(wm, "virtualParticleDensity", text = "Virtual Particle Density")
                if wm.virtualParticleDensity != main_coll["virtualParticleDensity"]:
                    wm.virtualParticleDensity = main_coll["virtualParticleDensity"]
                box_row = box.row()
                box_row.prop(wm, "hierarchicalLevels", text = "Hierarchical Levels")
                if wm.hierarchicalLevels != main_coll["hierarchicalLevels"]:
                    wm.hierarchicalLevels = main_coll["hierarchicalLevels"]
                box_row = box.row()
                box_row.prop(wm, "sleepLinearVelocity", text = "Sleep Linear Velocity")
                if wm.sleepLinearVelocity != main_coll["sleepLinearVelocity"]:
                    wm.sleepLinearVelocity = main_coll["sleepLinearVelocity"]
                box_row = box.row()
                box_row.prop(wm, "restLengthScale", text = "Rest Length Scale")
                if wm.restLengthScale != main_coll["restLengthScale"]:
                    wm.restLengthScale = main_coll["restLengthScale"]
                
                row = layout.row()
                box = row.box()
                box.label(text="Wind", icon="FORCE_WIND")
                box_row = box.row()
                box_row.prop(wm, "windVelocity", text = "Velocity")
                box_row = box.row()
                box_row.prop(wm, "windNoise", text = "Noise")
                box_row = box.row()
                box_row.prop(wm, "windDirection", text = "Direction")
                box_row = box.row()
                box_row.prop(wm, "windElevation", text = "Elevation")
                    
        return
    
def updateHierarchicalLevels(self, context):
    main_coll = GetCollection(make_active=False) 
    main_coll["hierarchicalLevels"] = self.hierarchicalLevels
    
def updateThickness(self, context):
    main_coll = GetCollection(make_active=False) 
    main_coll["thickness"] = self.thickness
    arma = GetArmature()
    for obj in arma.children:
        mod = obj.modifiers['ClothSimulation']
        mod["Input_17"] = self.thickness
        mod.node_group.interface_update(context)
        
def updateVirtualParticleDensity(self, context):
    main_coll = GetCollection(make_active=False) 
    main_coll["virtualParticleDensity"] = self.virtualParticleDensity
    
def updateGravityDirection(self, context):
    main_coll = GetCollection(make_active=False) 
    main_coll["gravityDirection"] = self.gravityDirection
    arma = GetArmature()
    for obj in arma.children:
        mod = obj.modifiers['ClothSimulation']
        mod["Input_15"] = np.array(self.gravityDirection, dtype=float)
        mod.node_group.interface_update(context)
    
def updateSleepLinearVelocity(self, context):
    main_coll = GetCollection(make_active=False) 
    main_coll["sleepLinearVelocity"] = self.sleepLinearVelocity
    
def updateDisableCCD(self, context):
    main_coll = GetCollection(make_active=False) 
    main_coll["disableCCD"] = self.disableCCD
    
def updateUntangling(self, context):
    main_coll = GetCollection(make_active=False) 
    main_coll["untangling"] = self.untangling

def updateTwoWayInteraction(self, context):
    main_coll = GetCollection(make_active=False) 
    main_coll["twowayInteraction"] = self.twowayInteraction
    
def updateRestLengthScale(self, context):
    main_coll = GetCollection(make_active=False) 
    main_coll["restLengthScale"] = self.restLengthScale
    arma = GetArmature()
    for obj in arma.children:
        mod = obj.modifiers['ClothSimulation']
        mod["Socket_4"] = self.restLengthScale
        mod.node_group.interface_update(context)

def updateWindVelocity(self, context):
    arma = GetArmature()
    for obj in arma.children:
        mod = obj.modifiers['ClothSimulation']
        mod["Socket_5"] = self.windVelocity
        mod.node_group.interface_update(context)
    
def updateWindNoise(self, context):
    arma = GetArmature()
    for obj in arma.children:
        mod = obj.modifiers['ClothSimulation']
        mod["Socket_10"] = self.windNoise
        mod.node_group.interface_update(context)
    
def updateWindDirection(self, context):
    arma = GetArmature()
    for obj in arma.children:
        mod = obj.modifiers['ClothSimulation']
        mod["Socket_7"] = self.windDirection
        mod.node_group.interface_update(context) 
    
def updateWindElevation(self, context):
    arma = GetArmature()
    for obj in arma.children:
        mod = obj.modifiers['ClothSimulation']
        mod["Socket_8"] = self.windElevation
        mod.node_group.interface_update(context) 
    
PROPS_ClothSimulation_Panel = [
('hierarchicalLevels', IntProperty(
        name="Hierarchical Levels",
        description="The number of cloth hierarhies. Only used to prevent stretching. Corresponds to NxClothMeshDesc::numHierarchyLevels. This is orthogonal to the Hard Stretch Limitation in the Clothing Material. This is only applicable if the number of hierarchical solver iterations in the Clothing Material is set to larger than 0. Use with care. This will increase the cooking time significantly, use more memory and more CPU at run time. Hard Stretch Limitation might be a better alternative to try first",
        default=0,
        min=0,
        update=updateHierarchicalLevels
    )),
('thickness', FloatProperty(
        name="Thickness",
        description="Minimal amount of separation between cloth particles and collision volumes. Each cloth particle will minimaly have as much distance to any collision volume. Most stable when this value corresponds roughly to half the average edge length. Can be increased to prevent penetration artifacts",
        default=0.06,
        min=0.0001,
        update=updateThickness
    )),
('virtualParticleDensity', FloatProperty(
        name="Virtual Particle Density",
        description="Select the amount of virtual particles generated for each triangle. 0 will create no virtual particles. 1 will create 3 virtual particles for every triangle. Everything else is in between",
        default=0,
        min=0,
        max=1,
        update=updateVirtualParticleDensity
    )),
('gravityDirection', IntVectorProperty(
        name="Gravity Direction",
        description="Direction of gravity for this asset",
        default=(0,0,-1),
        min=-1,
        max=1,
        update=updateGravityDirection
    )),
('sleepLinearVelocity', FloatProperty(
        name="Sleep Linear Velocity",
        description="Clothing will fall asleep if every vertex is slower than this velocity. Most clothing doesn't need it, but it might be useful for smaller assets like flags and the like",
        default=0,
        min=0,
        update=updateSleepLinearVelocity
    )),
('disableCCD', BoolProperty(
        name="Disable Continuous Collision Detection",
        description="Turn off CCD when colliding cloth particles with collision volumes. When turning off CCD, cloth particles can tunnel through fast moving collision volumes. But sometimes ill turning collision volumes can excert large velocities on particles. This can help prevent it. Setting this is not recommended. The ClothingActor will take care when to use and not use this flag upon teleportation or similar situations where continuous collision is not desired",
        default=False,
        update=updateDisableCCD
    )),
('untangling', BoolProperty(
        name="Untangling",
        description="EXPERIMENTAL: Untangle Cloth when it's entangled. This feature is highly experimental and still rather slow. Only use when self-collision could not help adequately. This comes with big performance implications, use with absolute care!",
        default=False,
        update=updateUntangling
    )),
('twowayInteraction', BoolProperty(
        name="Two Way Interaction",
        description="Make use of twoway interaction. For clothing this is normally not needed, as clothing should only follow the kinematic shapes. Needed when interacting with dynamic rigid bodies that need to be influenced by clothing. This is usually not necessary since regular clothing has very limited influence on most dynamic objects",
        default=False,
        update=updateTwoWayInteraction
    )),
('restLengthScale', FloatProperty(
        name="Rest Length Scale",
        description="Scale for cloth rest lengths",
        default=1,
        min=0.01,
        max=2,
        update=updateRestLengthScale
    )),
('windVelocity', FloatProperty(
        name="Wind Velocity",
        description="Strength of the wind effect",
        default=0,
        min=0,
        max=99,
        update=updateWindVelocity
    )),
('windNoise', FloatProperty(
        name="Wind Noise",
        description="Noise of the wind effect",
        default=0,
        min=0,
        max=10,
        update=updateWindNoise
    )),
('windDirection', FloatProperty(
        name="Wind Direction",
        description="Direction of the wind effect",
        default=1.5708,
        min=0,
        max=6.26573,
        subtype='ANGLE',
        update=updateWindDirection
    )),
('windElevation', FloatProperty(
        name="Wind Elevation",
        description="Elevation of the wind effect",
        default=1.5708,
        min=0,
        max=3.14159,
        subtype='ANGLE',
        update=updateWindElevation
    ))
]

CLASSES_ClothSimulation_Panel = [PhysXClothSimulationPanel]