# -*- coding: utf-8 -*-
# tools/hair_tools.py

import bpy
import numpy as np
from bpy_extras.object_utils import object_data_add
from io_mesh_apx.utils import getConnectedVertices, getClosest, MakeKDTree, selectOnly, GetLoopDataPerVertex, RemoveDoubles
from copy import deepcopy

def add_pin(context, radius, location, use_location):
    parent_coll = bpy.context.view_layer.active_layer_collection
    if "Pin Constraints" in parent_coll.collection.children:
        bpy.context.view_layer.active_layer_collection = parent_coll.children["Pin Constraints"]
    else:
        pin_coll = bpy.data.collections.new("Pin Constraints")
        parent_coll.collection.children.link(pin_coll)
        bpy.context.view_layer.active_layer_collection = parent_coll.children[pin_coll.name]
    
    arma = bpy.context.active_object
    bone = bpy.context.active_bone
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
    while pin_temp_name + str(num) in bpy.context.view_layer.active_layer_collection.collection.objects:
        num += 1
    else:
        pin.name = pin_temp_name + str(num)
        
    pin.display_type = 'WIRE'
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    pin.rotation_euler = boneRotation
    pin.scale = boneScale
    pin.location = boneLocation
    bpy.context.view_layer.active_layer_collection = parent_coll
    
    return pin
    
def shape_hair_interp(context, steps = 0, threshold = 0.001, hair_key = 0):
    growthMesh = bpy.context.active_object
    mesh = growthMesh.data
    n_vertices = len(mesh.vertices)
    scale = np.array(growthMesh.scale)
    dist_threshold = (threshold/scale).mean()
    
    # Duplication and quadrangulation
    bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.tris_convert_to_quads()
    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.object.mode_set(mode='OBJECT')
    duplicateMesh = bpy.context.active_object
    selectOnly(growthMesh)
    
    # Check curves
    curves = bpy.context.view_layer.active_layer_collection.collection.objects
    n_curves = len(curves)
    segmentsCount = len(curves[0].data.splines[0].points)
    display_step = np.array(np.ceil(np.sqrt(segmentsCount)), dtype="byte")
    correctCurves = 0
    for curve in curves:
        if curve.type == 'CURVE' or len(curve.data.splines[0].points) == segmentsCount:
            correctCurves += 1
    assert(correctCurves == n_curves)
                
    bpy.ops.object.particle_system_add()
    part_sys = growthMesh.particle_systems[-1]
    part_sys.settings.type = 'HAIR'
    part_sys.settings.hair_step = segmentsCount - 1
    part_sys.settings.display_step = display_step 
    part_sys.settings.emit_from = 'VERT'
    part_sys.settings.use_emit_random = False
    part_sys.settings.count = n_vertices
    growthMesh2 = growthMesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
    bpy.ops.object.mode_set(mode='PARTICLE_EDIT')
    bpy.context.tool_settings.particle_edit.use_emitter_deflect = False
    bpy.context.tool_settings.particle_edit.display_step = display_step
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
            #growthMesh2.particle_systems[-1].particles[i].hair_keys.foreach_set("co", np.array(closestCurve[:,:3] + diffBase).flatten())
                
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
            #growthMesh2.particle_systems[-1].particles[i].hair_keys.foreach_set("co", (closestCurve[:,:3] + diffBase).flatten())
                  
    bpy.ops.particle.connect_hair()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.data.objects.remove(duplicateMesh)
    
    return curves_pos
        
def create_curve(context):
    # Get the growthmesh
    obj = bpy.context.active_object
    growthMesh = obj.evaluated_get(context.evaluated_depsgraph_get())
    
    # Make a curve collection
    parent_coll = bpy.context.view_layer.active_layer_collection
    curve_coll = bpy.data.collections.new("Curves")
    parent_coll.collection.children.link(curve_coll)
    bpy.context.view_layer.active_layer_collection = parent_coll.children[curve_coll.name]
    
    # Create curves from guides
    hairs = growthMesh.particle_systems[0].particles
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
    
def haircard_curve(context, uv_orientation = "-Y", tolerance = 0.05):
    obj = bpy.context.active_object
    meshScale = obj.scale
    meshRot = obj.rotation_euler
    meshLoc = obj.location
    meshcoll = obj.users_collection[0]
    
    bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
    obj_dup = bpy.context.active_object
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
    RemoveDoubles()

    #Make a temporary collection for separated hair meshes
    parent_coll = bpy.context.view_layer.active_layer_collection
    coll_temp = bpy.data.collections.new("coll_temp")
    parent_coll.collection.children.link(coll_temp)
    bpy.context.view_layer.active_layer_collection = parent_coll.children[coll_temp.name]

    coll_temp.objects.link(obj_dup)
    meshcoll.objects.unlink(obj_dup)
    bpy.ops.mesh.separate(type='LOOSE')
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