# -*- coding: utf-8 -*-
# tools/add_connection.py

import bpy
import math
import random
import copy
from math import sqrt
from bpy_extras.object_utils import object_data_add
from mathutils import Vector, Matrix

def add_connection(context):
    parent_coll = bpy.context.view_layer.active_layer_collection
    sphere_connec_coll = bpy.data.collections.new("Collision Spheres Connections")
    sphere_connec_coll_name = sphere_connec_coll.name
    if "Collision Spheres Connections" in parent_coll.collection.children:
        bpy.context.view_layer.active_layer_collection = parent_coll.children["Collision Spheres Connections"]
    else:
        parent_coll.collection.children.link(sphere_connec_coll)
        bpy.context.view_layer.active_layer_collection = parent_coll.children[sphere_connec_coll_name]
        
    objects = bpy.context.selected_objects
    objCenter = []
    objRadius = []
    objName = []
    if len(objects) != 2:
        print("You need to select two spheres.")
        bpy.context.view_layer.active_layer_collection = parent_coll
    else:
        correctNames = 0
        for obj in objects:
            bpy.context.view_layer.objects.active = None
            bpy.ops.object.select_all(False)
            bpy.context.view_layer.objects.active = obj
            bpy.context.active_object.select_set(state=True)
            objName.append(obj.name)
            if obj.name.startswith("sphere_") == True and "_to_" not in obj.name:
                correctNames += 1
            else:
                print("You need to connect two collision spheres.")
                break
        if correctNames == 2:
            connectionName = objName[0] + "_to_" + objName[1]
            if connectionName not in bpy.context.view_layer.active_layer_collection.collection.objects:
                for obj in objects:
                    bpy.context.view_layer.objects.active = None
                    bpy.ops.object.select_all(False)
                    bpy.context.view_layer.objects.active = obj
                    bpy.context.active_object.select_set(state=True)
                    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='MEDIAN')
                    objCenter.append(copy.deepcopy(obj.matrix_world.translation))
                    center = obj.matrix_world.translation
                    vert = obj.data.vertices[0].co
                    radius = sqrt((vert[0])**2 + (vert[1])**2 + (vert[2])**2)
                    objRadius.append(copy.deepcopy(radius))
                    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
            
                # create the Curve Datablock
                curveData = bpy.data.curves.new(connectionName, type='CURVE')
                curveData.dimensions = '3D'
                curveData.resolution_u = 2
                curveData.bevel_depth = 1.0
                curveData.bevel_resolution = 10
                edge_vertices = 4 + (10*2)
                
                # map coords to spline
                polyline = curveData.splines.new('POLY')
                polyline.points.add(len(objCenter)-1)
                for j, coord in enumerate(objCenter):
                    x,y,z = coord
                    polyline.points[j].co = (x, y, z, 1)
                    
                # Add the curves to the scene
                object_data_add(context, curveData)
                
                # Scale the edge loops to the spheres' radius
                bpy.ops.object.convert(target = 'MESH')
                mesh = bpy.context.active_object
                for j in range(edge_vertices):
                    mesh.data.vertices[j].select = True
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.transform.resize(value = (objRadius[0], objRadius[0], objRadius[0]))
                bpy.ops.mesh.select_all(action="DESELECT")
                bpy.ops.object.mode_set(mode='OBJECT')
                for j in range(edge_vertices, edge_vertices * 2):
                    mesh.data.vertices[j].select = True
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.transform.resize(value = (objRadius[1], objRadius[1], objRadius[1]))   
                bpy.ops.mesh.select_all(action="DESELECT")
                bpy.ops.object.mode_set(mode='OBJECT')
                
                bpy.context.active_object.display_type = 'WIRE'
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
                      
                bpy.context.view_layer.active_layer_collection = parent_coll
            else:
                print("This connection exists already.")
                bpy.context.view_layer.objects.active = None
                bpy.ops.object.select_all(False)
                bpy.context.view_layer.active_layer_collection = parent_coll
        else:
            print("You need to connect two collision spheres.")
            bpy.context.view_layer.objects.active = None
            bpy.ops.object.select_all(False)
            bpy.context.view_layer.active_layer_collection = parent_coll