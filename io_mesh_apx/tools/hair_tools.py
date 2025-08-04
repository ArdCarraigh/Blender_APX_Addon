# -*- coding: utf-8 -*-
# tools/hair_tools.py

import bpy
import numpy as np
import re
from bpy_extras.object_utils import object_data_add
from io_mesh_apx.utils import getConnectedVertices, getClosest, MakeKDTree, selectOnly, GetLoopDataPerVertex, RemoveDoubles, GetCollection, GetArmature, ImportTemplates, QuadrangulateActiveMesh
from copy import deepcopy

def add_pin(context, bone, radius, location, use_location, pin_stiffness=0, influence_falloff=0, use_dynamic_pin=False, dolra=False, use_stiffness_pin=False, influence_falloff_curve=[0,0,0,0]):
    collision_coll = GetCollection("Pin Constraints", True)
    pins = collision_coll.objects
    arma = GetArmature()
    bone = arma.data.bones[bone]
    bonePos = np.array(bone.matrix_local.translation)
    boneScale = np.array(arma.scale)
    boneRotation = np.array(arma.rotation_euler)
    boneLocation = np.array(arma.location)
    
    if not use_location:
        location = bonePos
    else:
        location = np.array(location) / boneScale
        
    radius = np.array(radius) / boneScale[0]
    
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=location, segments=24, ring_count=16)
    pin = bpy.context.active_object
    
    num = 1
    pin_temp_name = "pin_" + bone.name + "_"
    while any([re.search(pin_temp_name + str(num), x.name) for x in pins]):
        num += 1
    else:
        pin.name = pin_temp_name + str(num)
        
    pin.data.shade_smooth()     
    pin.display_type = 'WIRE'
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    pin.rotation_euler = boneRotation
    pin.scale = boneScale
    pin.location = boneLocation
    arm_mod = pin.modifiers.new(type='ARMATURE', name = "Armature")
    arm_mod.object = arma
    bone_group = pin.vertex_groups.new(name=bone.name)
    for k in range(len(pin.data.vertices)):
        bone_group.add([k], 1, 'REPLACE')
        
    pin["pinStiffness1"] = pin_stiffness
    pin["influenceFallOff"] = influence_falloff
    pin["useDynamicPin1"] = use_dynamic_pin
    pin["doLra"] = dolra
    pin["useStiffnessPin"] = use_stiffness_pin
    pin["influenceFallOffCurve"] = influence_falloff_curve
    
    if "InfluenceFallOffCurveTemplate" not in bpy.data.node_groups:
        ImportTemplates()
    node_group = bpy.data.node_groups["InfluenceFallOffCurveTemplate"].copy()
    node_group.name = "InfluenceFallOffCurve"
    node_mod = pin.modifiers.new(type='NODES', name = "InfluenceFallOffCurve")
    node_mod.node_group = node_group
    for i, point in enumerate(node_group.nodes["Float Curve"].mapping.curves[0].points):
        point.location[1] = influence_falloff_curve[i]
        
    GetCollection()    
    
    return pin

def remove_pin(context, index):
    pin_coll = GetCollection("Pin Constraints", make_active = False)
    
    if pin_coll:
        if pin_coll.objects:
            bpy.data.objects.remove(pin_coll.objects[index], do_unlink=True)
            
        if not pin_coll.objects:
            bpy.data.collections.remove(pin_coll, do_unlink=True)
    
def shape_hair_interp(context, growthMesh, collection, steps = 0, threshold = 0.001, hair_key = 0, update_material = False):
    context.scene.frame_set(0)
    selectOnly(growthMesh)
    mesh = growthMesh.data
    n_vertices = len(mesh.vertices)
    scale = np.array(growthMesh.scale)
    dist_threshold = (threshold/scale).mean()
    
    # Duplication and quadrangulation
    bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
    QuadrangulateActiveMesh()
    duplicateMesh = bpy.context.active_object
    selectOnly(growthMesh)
    
    # Check curves
    curves = bpy.data.collections[collection].objects
    n_curves = len(curves)
    segmentsCount = len(curves[0].data.splines[0].points)
    display_step = np.array(np.ceil(np.sqrt(segmentsCount)), dtype="byte")
    correctCurves = 0
    for curve in curves:
        if curve.type == 'CURVE' or len(curve.data.splines[0].points) == segmentsCount:
            correctCurves += 1
    assert(correctCurves == n_curves)
    
    mods = growthMesh.modifiers
    if "Hairworks" in mods:
        mods.remove(mods['Hairworks'])
                
    mod = growthMesh.modifiers.new(name="Hairworks", type="PARTICLE_SYSTEM")
    part_sys = mod.particle_system
    settings = part_sys.settings
    settings.type = 'HAIR'
    settings.hair_step = segmentsCount - 1
    settings.display_step = display_step 
    settings.emit_from = 'VERT'
    settings.use_emit_random = False
    settings.count = n_vertices
    growthMesh2 = growthMesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
    bpy.ops.object.mode_set(mode='PARTICLE_EDIT')
    particle_edit = bpy.context.tool_settings.particle_edit
    particle_edit.use_emitter_deflect = False
    particle_edit.display_step = display_step
    bpy.ops.particle.disconnect_hair()
    
    curves_pos = []
    curveBases = []
    curve_pos_array = np.zeros(segmentsCount * 4)
    for curve in curves:
        curve.data.splines[0].points.foreach_get("co", curve_pos_array)
        curves_pos.append(deepcopy(curve_pos_array.reshape(-1,4)))
        curveBases.append(curves_pos[-1][hair_key][:3])
    curves_pos = np.array(curves_pos)[:,:,:3]
    
    #Build the KDTree
    kd = MakeKDTree(curveBases)
    
    for i, vert in enumerate(mesh.vertices):
        part = growthMesh2.particle_systems[-1].particles[i]
        vert_co = np.array(vert.co)
        # No interpolation for close curve
        closestCurveIndex = getClosest(vert_co, kd, threshold)
        if closestCurveIndex is None and not steps:
            closestCurveIndex = getClosest(vert_co, kd)
        if closestCurveIndex is not None:
            closestCurve = curves_pos[closestCurveIndex]
            diffBase = vert_co - closestCurve[0]
            for j, key in enumerate(part.hair_keys):
                key.co_object_set(
                    object = growthMesh2,
                    modifier = growthMesh2.modifiers[-1],
                    particle = part,
                    co = closestCurve[j,:3] + diffBase
                )
            #Hopefully someday usable
            #part.hair_keys.foreach_set("co", np.array(closestCurve[:,:3] + diffBase).flatten())
                
        # Else, Interpolate    
        else:      
            selected_vertices = getConnectedVertices(duplicateMesh, i, steps)
            closestCurveIndices = []
            dist_all = []
            for id in selected_vertices:
                closestCurveIndex = getClosest(mesh.vertices[id].co, kd)
                closestCurveIndices.append(closestCurveIndex)
                dist_all.append(np.linalg.norm(np.array(vert_co) - curves_pos[closestCurveIndex][0]))
            dist_all = np.array(dist_all)
                
            weight_all = dist_all/dist_all.sum()
            interp_co = np.sum(curves_pos[closestCurveIndices] * np.full((3, segmentsCount, len(closestCurveIndices)), weight_all).T, axis=0)
            diffBase = vert_co - interp_co[0]
            for j, key in enumerate(part.hair_keys):
                key.co_object_set(
                    object = growthMesh2,
                    modifier = growthMesh2.modifiers[-1],
                    particle = part,
                    co = interp_co[j] + diffBase
                )
            #Hopefully someday usable
            #part.hair_keys.foreach_set("co", (closestCurve[:,:3] + diffBase).flatten())
                  
    bpy.ops.particle.connect_hair()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.data.objects.remove(duplicateMesh)
    
    if update_material:
        part_sys.use_hair_dynamics = True
        settings.effector_weights.collection = GetCollection(make_active = False)
        settings.child_type = 'INTERPOLATED'
        settings.child_parting_factor = 0.5
        settings.kink = 'WAVE'
        wm = context.window_manager.physx.hair
        for k in growthMesh.keys():
            if hasattr(wm, k):
                setattr(wm, k, growthMesh[k])
    
    return curves_pos
        
def create_curve(context, obj):
    context.scene.frame_set(0)
    # Get the growthmesh
    growthMesh = obj.evaluated_get(context.evaluated_depsgraph_get())
    
    # Make a curve collection
    parent_coll = bpy.context.view_layer.active_layer_collection
    curve_coll = bpy.data.collections.new("Curves")
    curve_coll["Hairworks Curves"] = True
    parent_coll.collection.children.link(curve_coll)
    bpy.context.view_layer.active_layer_collection = parent_coll.children[curve_coll.name]
    
    # Create curves from guides
    hairs = growthMesh.modifiers["Hairworks"].particle_system.particles
    n_keys = len(hairs[0].hair_keys)
    curve_pos_array = np.zeros(n_keys * 3)
    array_ones = np.ones((n_keys,1))
    for hair in hairs:
        # create the Curve Datablock
        curveData = bpy.data.curves.new('myCurve', type='CURVE')
        curveData.dimensions = '3D'
        curveData.resolution_u = 2
        
        # map coords to spline
        hair.hair_keys.foreach_get("co", curve_pos_array)
        polyline = curveData.splines.new('POLY')
        polyline.points.add(len(hair.hair_keys) - 1)
        polyline.points.foreach_set("co", np.hstack([curve_pos_array.reshape(-1,3), array_ones]).flatten())
        
        # Add the curves to the scene
        curve = object_data_add(context, curveData)
        curve.scale = growthMesh.scale
        curve.rotation_euler = growthMesh.rotation_euler
        curve.location = growthMesh.location
    
    # Make the growthmesh active again
    selectOnly(obj)
    
def haircard_curve(context, hair_mesh, uv_orientation = "-Y", tolerance = 0.05):
    obj = bpy.data.objects[hair_mesh]
    selectOnly(obj)
    meshScale = obj.scale
    meshRot = obj.rotation_euler
    meshLoc = obj.location
    meshcoll = obj.users_collection[0]
    
    bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
    obj_dup = bpy.context.active_object
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
    RemoveDoubles()

    #Make a temporary collection for separated hair meshes
    GetCollection()
    parent_coll = bpy.context.view_layer.active_layer_collection
    coll_temp = bpy.data.collections.new("coll_temp")
    parent_coll.collection.children.link(coll_temp)
    bpy.context.view_layer.active_layer_collection = parent_coll.children[coll_temp.name]

    coll_temp.objects.link(obj_dup)
    for coll in obj_dup.users_collection:
        if coll != coll_temp:
            coll.objects.unlink(obj_dup)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.separate(type='LOOSE') # Separate in Edit Mode to avoid messing up normals
    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.object.mode_set(mode='OBJECT')
    objects = coll_temp.objects
    
    coords_all = []
    n_point = 0
    for n_obj, obj in enumerate(objects):
        mesh = obj.data
        n_vertices = len(mesh.vertices)
        vertices = np.zeros(n_vertices*3)
        mesh.attributes["position"].data.foreach_get("vector", vertices)
        vertices = vertices.reshape(-1,3)
        
        UVs = np.array(GetLoopDataPerVertex(mesh, "UV", mesh.uv_layers.active.name))
        if uv_orientation == "-Y":
            sortedUVs = np.array([[x,y,id] for x,y,id in sorted(zip(UVs[:,0], UVs[:,1], np.arange(0, n_vertices)), key = lambda v: v[1], reverse = True)], dtype=object)
            column = 1
        if uv_orientation == "Y":
            sortedUVs = np.array([[x,y,id] for x,y,id in sorted(zip(UVs[:,0], UVs[:,1], np.arange(0, n_vertices)), key = lambda v: v[1])], dtype=object)
            column = 1
        if uv_orientation == "X":
            sortedUVs = np.array([[x,y,id] for x,y,id in sorted(zip(UVs[:,0], UVs[:,1], np.arange(0, n_vertices)), key = lambda v: v[0])], dtype=object)
            column = 0
        if uv_orientation == "-X":
            sortedUVs = np.array([[x,y,id] for x,y,id in sorted(zip(UVs[:,0], UVs[:,1], np.arange(0, n_vertices)), key = lambda v: v[0], reverse = True)], dtype=object)
            column = 0
        
        coords_obj = []
        j = -1
        for i in range(n_vertices):
            if i <= j: continue
            startUV = sortedUVs[i]
            for j in range(i, n_vertices):
                if sortedUVs[j,column] < (startUV[column]-tolerance) or sortedUVs[j,column] > (startUV[column]+tolerance):
                    coords_obj.append(np.mean(vertices[np.array(sortedUVs[i:j,2], dtype=int)], axis = 0))
                    n_point += 1
                    break
                if j == n_vertices - 1:
                    coords_obj.append(np.mean(vertices[np.array(sortedUVs[i:(j+1),2], dtype=int)], axis = 0))
                    n_point += 1

        coords_all.append(np.array(coords_obj))
        
    n_obj += 1
    n_step = round(n_point/n_obj)
    
    curve_coll = bpy.data.collections.new("Curves")
    curve_coll["Hairworks Curves"] = True
    parent_coll.collection.children.link(curve_coll)
    bpy.context.view_layer.active_layer_collection = parent_coll.children[curve_coll.name]
    
    array_ones = np.ones((n_step, 1))
    for coords in coords_all:
        dists = np.hstack([[0], np.cumsum(np.linalg.norm(np.diff(coords, axis = 0), axis = 1))])
        linear_space = np.linspace(0, dists.max(), n_step)
        coords_interp = np.hstack([np.interp(linear_space, dists, coords[:,0]).reshape(-1,1), np.interp(linear_space, dists, coords[:,1]).reshape(-1,1), np.interp(linear_space, dists, coords[:,2]).reshape(-1,1)])

        # create the Curve Datablock
        curveData = bpy.data.curves.new('myCurve', type='CURVE')
        curveData.dimensions = '3D'
        curveData.resolution_u = 2
            
        # map coords to spline
        polyline = curveData.splines.new('POLY')
        polyline.points.add(n_step - 1)
        polyline.points.foreach_set("co", np.hstack([coords_interp, array_ones]).flatten())
            
        # Add the curves to the scene
        curve = object_data_add(context, curveData)
        curve.scale = meshScale
        curve.rotation_euler = meshRot
        curve.location = meshLoc
        
    bpy.data.collections.remove(coll_temp)

def hair_to_haircard(context, obj, cap = False, width = 0.05, width_relative = False):
    bpy.context.scene.collection
    context.scene.frame_set(0)
    # Get the growthmesh
    growthMesh = obj.evaluated_get(context.evaluated_depsgraph_get())