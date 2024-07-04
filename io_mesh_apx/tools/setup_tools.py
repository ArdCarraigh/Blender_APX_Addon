# -*- coding: utf-8 -*-
# tools/setup_tools.py

import bpy
import random, colorsys
import re
import numpy as np
from copy import deepcopy
from io_mesh_apx.utils import ImportTemplates, SetAttributes, GetWind, GetDrag, GetArmature, selectOnly, GetCollection, RemoveDoubles
from io_mesh_apx.templates.template_clothing_setup import *
from io_mesh_apx.templates.template_hairworks_setup import *
from io_mesh_apx.tools.paint_tools import cleanUpDriveLatchGroups
from io_mesh_apx.tools.hair_tools import create_curve, shape_hair_interp

def setup_hairworks(context, obj):
    assert(obj.type == 'MESH')
    selectOnly(obj)
    RemoveDoubles()
    mesh = obj.data

    # Deal with Collections
    parent_coll = bpy.context.view_layer.active_layer_collection
    main_colls = obj.users_collection
    if "PhysXAssetType" not in main_colls[0]:
        apx_coll = bpy.data.collections.new("APX Asset")
        apx_coll["PhysXAssetType"] = "Hairworks"
        parent_coll.collection.children.link(apx_coll)
        bpy.context.view_layer.active_layer_collection = parent_coll.children[apx_coll.name]
        arma = obj.parent
        if arma and arma.type == 'ARMATURE':
            apx_coll.objects.link(arma)
            for coll in main_colls:
                coll.objects.unlink(arma)
        apx_coll.objects.link(obj)
        for coll in main_colls:
            coll.objects.unlink(obj)
    else:
        apx_coll = main_colls[0]
        apx_coll["PhysXAssetType"] = "Hairworks"
        
    # Check Armature
    GetArmature()
    assert(obj.parent.type == 'ARMATURE')
    # Check Wind
    GetWind()
    
    # Check Material 
    if not mesh.materials:
        temp_mat = bpy.data.materials.new(name="Material")
        mesh.materials.append(temp_mat)
        temp_mat.diffuse_color = (*colorsys.hsv_to_rgb(random.random(), .7, .9), 1)
        
    # Refresh the Hair Simulation Modifier
    if 'Hairworks' in obj.modifiers:
        create_curve(context, obj)
        curve_coll_temp = bpy.context.view_layer.active_layer_collection.collection
        # Remove particle
        while obj.particle_systems:
            bpy.ops.object.particle_system_remove()
        shape_hair_interp(bpy.context, obj, curve_coll_temp.name)
        GetCollection()
        bpy.data.collections.remove(curve_coll_temp)
    else:
        # Remove particle
        while obj.particle_systems:
            bpy.ops.object.particle_system_remove()
        
    # Remove Cloth and Curves Modifiers
    for mod in obj.modifiers:
        if mod.name in ["ClothSimulation", "SimulationCurves"]:
            obj.modifiers.remove(mod)
        
    # SetUp Hair Material/Simulation
    sim = deepcopy(templateHairMat)
    for key in obj.keys():
        if key in templateHairMat:
            sim[key] = obj[key]
    SetUpHairworksMaterial(obj, apx_coll, sim)
                   
def SetUpHairworksMaterial(obj, parent_coll, material):
    wm = bpy.context.window_manager.physx
    wm.PhysXSubPanel = 'collision'
    selectOnly(obj)
    if 'Hairworks' not in obj.modifiers:
        mod = obj.modifiers.new(name="Hairworks", type="PARTICLE_SYSTEM")
        part_sys = mod.particle_system
        settings = part_sys.settings
        settings.type = 'HAIR'
        settings.hair_step = 5
        settings.display_step = 3
        settings.emit_from = 'VERT'
        settings.use_emit_random = False
        settings.count = len(obj.data.vertices)
        settings.hair_length = 0.1
        bpy.ops.object.mode_set(mode='PARTICLE_EDIT')
        particle_edit = bpy.context.tool_settings.particle_edit
        particle_edit.use_emitter_deflect = False
        particle_edit.display_step = 3
        bpy.ops.object.mode_set(mode='OBJECT')
    else:
        part_sys = obj.modifiers['Hairworks'].particle_system
        settings = part_sys.settings
    
    part_sys.use_hair_dynamics = True
    settings.effector_weights.collection = parent_coll
    settings.child_type = 'INTERPOLATED'
    settings.child_parting_factor = 0.5
    settings.kink = 'WAVE'
    
    bpy.context.scene.render.hair_type = 'STRIP'
    
    if "SimulationCurves" not in obj.modifiers:
        if "SimulationCurvesTemplate" not in bpy.data.node_groups:
            ImportTemplates()
        node_group = bpy.data.node_groups["SimulationCurvesTemplate"].copy()
        node_group.name = "SimulationCurves"
        node_mod = obj.modifiers.new(type='NODES', name = "SimulationCurves")
        node_mod.node_group = node_group
    
    SetAttributes(wm.hair, material)
                
def setup_clothing(context, obj):
    assert(obj.type == 'MESH')
    mesh = obj.data
    
    # Deal with Collections
    parent_coll = bpy.context.view_layer.active_layer_collection
    main_colls = obj.users_collection
    if "PhysXAssetType" not in main_colls[0]:
        apx_coll = bpy.data.collections.new("APX Asset")
        apx_coll["PhysXAssetType"] = "Clothing"
        parent_coll.collection.children.link(apx_coll)
        bpy.context.view_layer.active_layer_collection = parent_coll.children[apx_coll.name]
        arma = obj.parent
        if arma and arma.type == 'ARMATURE':
            apx_coll.objects.link(arma)
            for coll in main_colls:
                coll.objects.unlink(arma)
        apx_coll.objects.link(obj)
        for coll in main_colls:
            coll.objects.unlink(obj)
    else:
        apx_coll = main_colls[0]
        apx_coll["PhysXAssetType"] = "Clothing"
        
    # Check Collision Collections
    sphere_coll = GetCollection("Collision Spheres", make_active=False)
    connection_coll = GetCollection("Collision Connections", make_active=False)
    capsule_coll = GetCollection("Collision Capsules", make_active=False)
        
    # Check Armature
    arma = GetArmature()
    assert(obj.parent.type == 'ARMATURE')
    
    for ob in arma.children:
        # Set Up Paints
        for layer in ["PhysXMaximumDistance", "PhysXBackstopRadius", "PhysXBackstopDistance", "PhysXDrive1", "PhysXLatch1"]:
            if layer not in ob.vertex_groups:
                ob.vertex_groups.new(name=layer)
                if layer == "PhysXDrive1":
                    drive_group = ob.vertex_groups["PhysXDrive1"]
                    for k in range(len(mesh.vertices)):
                        drive_group.add([k], 1, 'REPLACE')
        cleanUpDriveLatchGroups(ob)
               
        # Check Material 
        if not mesh.materials:
            temp_mat = bpy.data.materials.new(name="Material")
            mesh.materials.append(temp_mat)
            temp_mat.diffuse_color = (*colorsys.hsv_to_rgb(random.random(), .7, .9), 1)
            
        # Remove particle systems/Hairworks
        while ob.particle_systems:
            bpy.ops.object.particle_system_remove()
            
        # Setup Cloth Material
        if "ClothSimulation" in ob.modifiers:
            ob.modifiers.remove(ob.modifiers["ClothSimulation"])
        
        cloth = deepcopy(templateClothMat)       
        for key in ob.keys():
            if key in templateClothMat:
                cloth[key] = ob[key]
        
        SetUpClothMaterial(ob, apx_coll, cloth)
        
        # Setup Cloth Simulation
        sim = deepcopy(templateClothSim)
        for key in apx_coll.keys():
            if key in templateClothSim:
                sim[key] = apx_coll[key]
        SetAttributes(bpy.context.window_manager.physx.cloth, sim)
    
        # Setup Simulation Collision
        if sphere_coll:
            ob.modifiers['ClothSimulation']['Input_14'] = sphere_coll
        if connection_coll:
            ob.modifiers['ClothSimulation']['Socket_2'] = connection_coll
        if capsule_coll:
            ob.modifiers['ClothSimulation']['Socket_3'] = capsule_coll
            
def SetUpClothMaterial(obj, parent_coll, sim):
    wm = bpy.context.window_manager.physx
    wm.PhysXSubPanel = 'collision'
    selectOnly(obj)
    if "ClothSimulationTemplate" not in bpy.data.node_groups:
        ImportTemplates()
    
    node_group = bpy.data.node_groups["ClothSimulationTemplate"].copy()
    node_group.name = "ClothSimulation"
    node_mod = obj.modifiers.new(type='NODES', name = "ClothSimulation")
    node_mod.node_group = node_group
    
    SetAttributes(wm.cloth, sim)