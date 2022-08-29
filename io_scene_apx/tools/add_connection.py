# -*- coding: utf-8 -*-
# tools/add_connection.py

import bpy
import math
import copy
import numpy as np
from math import sqrt
from bpy_extras.object_utils import object_data_add
from mathutils import Vector

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
                    bpy.ops.object.select_all(action='DESELECT')
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
                
                pos_2 = objCenter[1]
                pos_1 = objCenter[0]
                R2 = objRadius[1]
                R1 = objRadius[0]
                
                AB = np.linalg.norm(pos_2-pos_1)
                BE = abs(R2-R1)
                AE = (AB**2 - (R2-R1)**2)**.5
                cone_radius_1 = R1 * AE / AB
                cone_radius_2 = R2 * AE / AB
                AG = R1 * BE / AB
                BF = R2 * BE / AB
                
                AB_dir = (pos_2-pos_1)/AB
                if R1 > R2:
                    cone_pos = pos_1 + AB_dir * AG
                else:
                    cone_pos = pos_1 - AB_dir * AG
                
                cone_depth = AB - abs(AG-BF)
                cone_pos = cone_pos + AB_dir * cone_depth * .5 #cone pos is midpoint of centerline
                rotation = Vector([0,0,1]).rotation_difference(Vector(AB_dir)).to_euler("XYZ") ### may need to change
                
                bpy.ops.mesh.primitive_cone_add(
                    vertices=24, 
                    radius1=cone_radius_1, 
                    radius2=cone_radius_2, 
                    depth=cone_depth, 
                    location=cone_pos, 
                    rotation=rotation, 
                    )
                
                bpy.context.active_object.name = connectionName
                bpy.context.active_object.display_type = 'WIRE'
                      
                bpy.context.view_layer.active_layer_collection = parent_coll
            else:
                print("This connection already exists.")
                bpy.context.view_layer.objects.active = None
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.active_layer_collection = parent_coll
        else:
            print("You need to connect two collision spheres.")
            bpy.context.view_layer.objects.active = None
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.active_layer_collection = parent_coll