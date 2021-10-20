# -*- coding: utf-8 -*-
# tools/add_sphere.py

import bpy
import math
import random
from bpy_extras.object_utils import object_data_add
from mathutils import Vector, Matrix

def add_sphere(context, radius):
    parent_coll = bpy.context.view_layer.active_layer_collection
    sphere_coll = bpy.data.collections.new("Collision Spheres")
    sphere_coll_name = sphere_coll.name
    if "Collision Spheres" in parent_coll.collection.children:
        bpy.context.view_layer.active_layer_collection = parent_coll.children["Collision Spheres"]
    else:
        parent_coll.collection.children.link(sphere_coll)
        bpy.context.view_layer.active_layer_collection = parent_coll.children[sphere_coll_name]
        
    
    bonePos = bpy.context.active_bone.matrix_local.translation
    boneName = bpy.context.active_bone.name
    boneScale = bpy.context.active_object.scale
    boneRotation = bpy.context.active_object.rotation_euler
    boneLocation = bpy.context.active_object.location
    
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=bonePos, segments=24, ring_count=16)
    
    num = 1
    while "sphere_" + boneName + "_" + str(num) in bpy.context.view_layer.active_layer_collection.collection.objects:
        num += 1
    else:
        bpy.context.active_object.name = "sphere_" + boneName + "_" + str(num)
        
    bpy.context.active_object.display_type = 'WIRE'
    
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    bpy.context.active_object.rotation_euler = boneRotation
    bpy.context.active_object.scale = boneScale
    bpy.context.active_object.location = boneLocation
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.transform.resize(value = (1/boneScale[0], 1/boneScale[1], 1/boneScale[2]))
    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.context.view_layer.active_layer_collection = parent_coll