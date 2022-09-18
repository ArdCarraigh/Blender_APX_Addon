# -*- coding: utf-8 -*-
# tools/shape_hair_interp.py

import bpy
import math
import copy
import numpy as np
from math import sqrt
from bpy_extras.object_utils import object_data_add
from mathutils import Vector

def whichClosestCoords(vert_coord, array2D):
    list2 = []
    for i in range(len(array2D)):
        list2.append(sqrt((array2D[i][0] - vert_coord[0])**2 + (array2D[i][1] - vert_coord[1])**2 + (array2D[i][2] - vert_coord[2])**2))
    closestIndex = list2.index(min(list2))
    return(closestIndex)

def getConnectedVertices(obj, vertex, steps):
    interest_verts = [vertex.index]
    for i in range(steps):
        connec_verts = []
        for edge in obj.data.edges:
            edge_verts = list(edge.vertices)
            check = any(item in interest_verts for item in edge_verts)
            if check is True:
                connec_verts.extend(edge_verts)
        interest_verts = list(set(connec_verts))
        interest_verts = list(filter(lambda v: v!=vertex.index, interest_verts))
        connected_vertices = interest_verts
    return(connected_vertices)

def shape_hair_interp(context, steps):
    growthMesh = bpy.context.active_object
    scale = np.array(copy.deepcopy(growthMesh.scale))
    threshold = np.array((0.01,0.01,0.01)) / scale # 1cm, adjustable
    dist_threshold = sqrt(threshold[0]**2 + threshold[1]**2 + threshold[2]**2)
    # Duplication and quadrangulation
    bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.tris_convert_to_quads()
    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.object.mode_set(mode='OBJECT')
    duplicateMesh = bpy.context.active_object
    bpy.context.view_layer.objects.active = None
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = growthMesh
    bpy.context.active_object.select_set(state=True)
    # Check curves
    curves = bpy.context.view_layer.active_layer_collection.collection.objects
    segmentsCount = len(curves[0].data.splines[0].points)
    correctCurves = 0
    for curve in curves:
        if curve.type == 'CURVE' or len(curve.data.splines[0].points) == segmentsCount:
            correctCurves += 1
        else:
            print("Something is wrong with your curve collection.")
            break
                
    if correctCurves == len(curves):
        bpy.ops.object.particle_system_add()
        growthMesh.particle_systems[0].settings.type = 'HAIR'
        growthMesh.particle_systems[0].settings.hair_step = segmentsCount - 1
        growthMesh.particle_systems[0].settings.display_step = int(round(sqrt(segmentsCount),0)) + 1 
        growthMesh.particle_systems[0].settings.emit_from = 'VERT'
        growthMesh.particle_systems[0].settings.use_emit_random = False
        growthMesh.particle_systems[0].settings.count = len(growthMesh.data.vertices)
        growthMesh2 = growthMesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
        bpy.ops.object.mode_set(mode='PARTICLE_EDIT')
        bpy.context.tool_settings.particle_edit.use_emitter_deflect = False
        bpy.context.tool_settings.particle_edit.display_step = int(round(sqrt(segmentsCount),0)) + 1 
        bpy.ops.particle.disconnect_hair()
        
        curveBases = np.zeros(shape=(len(curves), 3))
        for i in range(len(curves)):
            curveBases[i] = curves[i].data.splines[0].points[0].co[0:3] 
        if steps != 0:  
            curve_1st_verts = np.zeros(shape=(len(curves), 3))
            for i in range(len(curves)):
                curve_1st_verts[i] = curves[i].data.splines[0].points[1].co[0:3] 
        
        for i in range(len(growthMesh.data.vertices)):
            closestCurveIndex = whichClosestCoords(growthMesh.data.vertices[i].co[0:3], curveBases)
            
            # No interpolation for close curve 
            diffBase = growthMesh.data.vertices[i].co - Vector((curves[closestCurveIndex].data.splines[0].points[0].co[0:3]))
            distBase = sqrt(diffBase[0]**2 + diffBase[1]**2 + diffBase[2]**2)
            if distBase <= dist_threshold or steps == 0:
                for j in range(0,len(curves[closestCurveIndex].data.splines[0].points)):
                    growthMesh2.particle_systems[0].particles[i].hair_keys[j].co_object_set(
                        object = growthMesh2,
                        modifier = growthMesh2.modifiers[-1],
                        particle = growthMesh2.particle_systems[0].particles[i],
                        co = Vector((curves[closestCurveIndex].data.splines[0].points[j].co[0:3])) + diffBase
                    )
                    
            # Interpolation      
            else:      
                interest_vert = duplicateMesh.data.vertices[i]
                selected_vertices = getConnectedVertices(duplicateMesh, interest_vert, steps)
                
                closestCurveIndexes = []
                for id in selected_vertices:
                    closestCurveIndexBase = whichClosestCoords(duplicateMesh.data.vertices[id].co[0:3], curveBases)
                    closestCurveIndex1stVert = whichClosestCoords(duplicateMesh.data.vertices[id].co[0:3], curve_1st_verts)
                    #if closestCurveIndexBase == closestCurveIndex1stVert:
                    closestCurveIndexes.append(closestCurveIndexBase)
                    #else:
                    #    closestCurveIndexes.append(closestCurveIndex1stVert)    
                
                dist_all = []
                for id in closestCurveIndexes:
                    mesh_vert = growthMesh.data.vertices[i].co[0:3]
                    curve_vert = curves[id].data.splines[0].points[0].co[0:3]
                    dist_all.append(((mesh_vert[0] - curve_vert[0])**2 + (mesh_vert[1] - curve_vert[1])**2 + (mesh_vert[2] - curve_vert[2])**2))
                    
                sum_dist = sum(dist_all)
                weight_all = [(sum_dist-x)/(sum_dist) for x in dist_all]
                sum_weight = sum(weight_all)
                
                x_interp = []
                y_interp = []
                z_interp = []
                for j in range(segmentsCount):
                    all_x = []
                    all_y = []
                    all_z = []
                    for id in closestCurveIndexes:
                        all_x.append(curves[id].data.splines[0].points[j].co[0])
                        all_y.append(curves[id].data.splines[0].points[j].co[1])
                        all_z.append(curves[id].data.splines[0].points[j].co[2])
                    
                    mean_x = 0
                    mean_y = 0
                    mean_z = 0
                    for k in range(len(all_x)):
                        mean_x += all_x[k] * weight_all[k]
                        mean_y += all_y[k] * weight_all[k]
                        mean_z += all_z[k] * weight_all[k]
                    if sum_weight > 0:
                        mean_x = mean_x/sum_weight
                        mean_y = mean_y/sum_weight
                        mean_z = mean_z/sum_weight
                        
                    x_interp.append(mean_x)
                    y_interp.append(mean_y)
                    z_interp.append(mean_z)
                    
                    diffBase2 = Vector((growthMesh.data.vertices[i].co[0:3])) - Vector((x_interp[0],y_interp[0],z_interp[0]))
                    
                    growthMesh2.particle_systems[0].particles[i].hair_keys[j].co_object_set(
                        object = growthMesh2,
                        modifier = growthMesh2.modifiers[-1],
                        particle = growthMesh2.particle_systems[0].particles[i],
                        co = Vector((mean_x,mean_y,mean_z)) + diffBase2
                    )
                      
        bpy.ops.particle.connect_hair()
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.view_layer.objects.active = None
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = duplicateMesh
        bpy.context.active_object.select_set(state=True)
        bpy.ops.object.delete(use_global=False, confirm=False)
        bpy.context.view_layer.objects.active = growthMesh