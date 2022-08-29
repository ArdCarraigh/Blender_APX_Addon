# -*- coding: utf-8 -*-
# tools/add_pin.py

import bpy
from bpy_extras.object_utils import object_data_add

def add_pin(context, radius, location):
    parent_coll = bpy.context.view_layer.active_layer_collection
    sphere_coll = bpy.data.collections.new("Pin Constraints")
    sphere_coll_name = sphere_coll.name
    if "Pin Constraints" in parent_coll.collection.children:
        bpy.context.view_layer.active_layer_collection = parent_coll.children["Pin Constraints"]
    else:
        parent_coll.collection.children.link(sphere_coll)
        bpy.context.view_layer.active_layer_collection = parent_coll.children[sphere_coll_name]
        
    
    bonePos = bpy.context.active_bone.matrix_local.translation
    boneName = bpy.context.active_bone.name
    boneScale = bpy.context.active_object.scale
    boneRotation = bpy.context.active_object.rotation_euler
    boneLocation = bpy.context.active_object.location
    
    if location == (0,0,0):
        location = bonePos
    
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=location, segments=24, ring_count=16)
    
    num = 1
    while "pin_" + boneName + "_" + str(num) in bpy.context.view_layer.active_layer_collection.collection.objects:
        num += 1
    else:
        bpy.context.active_object.name = "pin_" + boneName + "_" + str(num)
        
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