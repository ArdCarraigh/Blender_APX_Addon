# -*- coding: utf-8 -*-
# tools/haircard_curve.py

import bpy
import copy
from bpy_extras.object_utils import object_data_add
from statistics import mean
import numpy as np

def haircard_curve(context):
    meshcoll = bpy.context.active_object.users_collection[0]
    bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
    meshScale = copy.deepcopy(bpy.context.active_object.scale)
    meshRot = copy.deepcopy(bpy.context.active_object.rotation_euler)
    meshLoc = copy.deepcopy(bpy.context.active_object.location)
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    bpy.ops.mesh.remove_doubles()
    bpy.ops.object.mode_set(mode='OBJECT')

    #Make a temporary collection for separated hair meshes
    parent_coll = bpy.context.view_layer.active_layer_collection
    coll_temp = bpy.data.collections.new("coll_temp")
    coll_temp_name = coll_temp.name
    parent_coll.collection.children.link(coll_temp)
    bpy.context.view_layer.active_layer_collection = parent_coll.children[coll_temp_name]

    bpy.context.view_layer.active_layer_collection.collection.objects.link(bpy.context.active_object)
    meshcoll.objects.unlink(bpy.context.active_object)
    bpy.ops.mesh.separate(type='LOOSE')
    objects = bpy.context.view_layer.active_layer_collection.collection.objects
    x_all = []
    y_all = []
    z_all = []
    n_obj = 0
    n_point = 0
    for obj in objects:
        n_obj += 1
        bpy.context.view_layer.objects.active = obj
        bpy.context.active_object.select_set(state=True)
        x_obj = []
        y_obj = []
        z_obj = []
        used_vertices = []
        while len(used_vertices) < len(obj.data.vertices):
            UVs_x = []
            UVs_y = []
            vertices_ids = []
            for face in obj.data.polygons:
                for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                    if vert_idx not in used_vertices:
                        uv_coords = obj.data.uv_layers.active.data[loop_idx].uv
                        UVs_x.append(uv_coords.x)
                        UVs_y.append(uv_coords.y)
                        vertices_ids.append(vert_idx)
                    
            top_coords_x = []
            top_coords_y = []
            top_coords_z = []
            if len(UVs_y) > 2:
                top_UVs_index = [UVs_y.index(max(UVs_y))]
                top_UV_y = UVs_y[top_UVs_index[0]]
                for i in range(len(UVs_y)):
                    if UVs_y[i] > (top_UV_y-0.05): #adjust for desired precision
                        if i not in top_UVs_index:
                            top_UVs_index.append(i)
                top_vertices_index = []
                for i in top_UVs_index:
                    if vertices_ids[i] not in top_vertices_index:
                        top_vertices_index.append(vertices_ids[i])
                        used_vertices.append(vertices_ids[i])
                for vert in top_vertices_index:
                    top_coords_x.append(obj.data.vertices[vert].co.x)
                    top_coords_y.append(obj.data.vertices[vert].co.y)
                    top_coords_z.append(obj.data.vertices[vert].co.z)
                    
            else:
                for vert in obj.data.vertices:
                    if vert.index not in used_vertices:
                        top_coords_x.append(vert.co.x)
                        top_coords_y.append(vert.co.y)
                        top_coords_z.append(vert.co.z)
                        used_vertices.append(vert.index)
            
            mean_x = mean(top_coords_x)
            mean_y = mean(top_coords_y)
            mean_z = mean(top_coords_z)
            x_obj.append(mean_x)
            y_obj.append(mean_y)
            z_obj.append(mean_z)
            n_point += 1 
            
        x_all.append(x_obj)
        y_all.append(y_obj)
        z_all.append(z_obj)
        
    n_step = round(n_point/n_obj)
    interp_coords_all = []
    for i in range(len(x_all)):
        xd = np.diff(x_all[i])
        yd = np.diff(y_all[i])
        zd = np.diff(z_all[i])
        dist = np.sqrt(xd**2 + yd**2 + zd**2)
        u = np.cumsum(dist)
        u = np.hstack([[0],u])
        
        t = np.linspace(0,u.max(),n_step)
        xn = np.interp(t, u, x_all[i])
        yn = np.interp(t, u, y_all[i])
        zn = np.interp(t, u, z_all[i])
        interp_coords_obj = []
        for j in range(len(xn)):
            interp_coords_obj.append([xn[j], yn[j], zn[j]])
        interp_coords_all.append(interp_coords_obj)

            
    curve_coll = bpy.data.collections.new("Curves")
    curve_coll_name = curve_coll.name
    parent_coll.collection.children.link(curve_coll)
    bpy.context.view_layer.active_layer_collection = parent_coll.children[curve_coll_name]

    for hair in interp_coords_all:
        # create the Curve Datablock
        curveData = bpy.data.curves.new('myCurve', type='CURVE')
        curveData.dimensions = '3D'
        curveData.resolution_u = 2
        curveData.bevel_depth = 0
            
        # map coords to spline
        polyline = curveData.splines.new('POLY')
        polyline.points.add(len(hair) - 1)
        for j in range(len(hair)):
            polyline.points[j].co = (*hair[j], 1)
            
        # Add the curves to the scene
        object_data_add(context, curveData)
        bpy.context.active_object.scale = meshScale
        bpy.context.active_object.rotation_euler = meshRot
        bpy.context.active_object.location = meshLoc
        
    bpy.data.collections.remove(coll_temp)
    bpy.context.view_layer.active_layer_collection = parent_coll