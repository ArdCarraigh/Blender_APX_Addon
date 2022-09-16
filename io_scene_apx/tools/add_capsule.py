# -*- coding: utf-8 -*-
# tools/add_capsule.py

import bpy
import numpy as np
from bpy_extras.object_utils import object_data_add
from io_scene_apx.importer import import_hairworks
from io_scene_apx.importer.import_hairworks import JoinThem

def add_capsule(context, radius, height, location, rotation, use_location):
    parent_coll = bpy.context.view_layer.active_layer_collection
    if "Collision Capsules" in parent_coll.collection.children:
        bpy.context.view_layer.active_layer_collection = parent_coll.children["Collision Capsules"]
    else:
        capsule_coll = bpy.data.collections.new("Collision Capsules")
        capsule_coll_name = capsule_coll.name
        parent_coll.collection.children.link(capsule_coll)
        bpy.context.view_layer.active_layer_collection = parent_coll.children[capsule_coll_name]
        
    bonePos = bpy.context.active_bone.matrix_local.translation
    boneName = bpy.context.active_bone.name
    boneScale = bpy.context.active_object.scale
    boneRotation = bpy.context.active_object.rotation_euler
    boneLocation = bpy.context.active_object.location
    
    if not use_location:
        location = bonePos
        
    if "Material_Sphere1" not in bpy.data.materials:
        sphere1_mat = bpy.data.materials.new("Material_Sphere1")
    if "Material_Sphere2" not in bpy.data.materials:
        sphere2_mat = bpy.data.materials.new("Material_Sphere2")
    if "Material_Cylinder" not in bpy.data.materials:
        cylinder_mat = bpy.data.materials.new("Material_Cylinder")
    
    meshNames = []
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=(0,height/2,0), segments=24, ring_count=16)
    bpy.context.active_object.data.materials.append(bpy.data.materials["Material_Sphere1"])
    meshNames.append(bpy.context.active_object.name)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=(0,-height/2,0), segments=24, ring_count=16)
    bpy.context.active_object.data.materials.append(bpy.data.materials["Material_Sphere2"])
    meshNames.append(bpy.context.active_object.name)
    bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=radius, radius2=radius, depth=height, rotation=(-np.pi/2,0,0))
    bpy.context.active_object.data.materials.append(bpy.data.materials["Material_Cylinder"])
    meshNames.append(bpy.context.active_object.name)
    JoinThem(meshNames)
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    bpy.ops.mesh.remove_doubles()
    #bpy.ops.transform.translate(value=location)
    #bpy.ops.transform.rotate(value = rotation[0], orient_axis='X', constraint_axis=(True, False, False))
    #bpy.ops.transform.rotate(value = rotation[1], orient_axis='Y', constraint_axis=(False, True, False))
    #bpy.ops.transform.rotate(value = rotation[2], orient_axis='Z', constraint_axis=(False, False, True))
    bpy.ops.object.mode_set(mode='OBJECT')
    
    num = 1
    while "capsule_" + boneName + "_" + str(num) in bpy.context.view_layer.active_layer_collection.collection.objects:
        num += 1
    else:
        bpy.context.active_object.name = "capsule_" + boneName + "_" + str(num)
        
    bpy.context.active_object.display_type = 'WIRE'
    
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    bpy.context.active_object.rotation_euler = boneRotation
    bpy.context.active_object.scale = boneScale
    bpy.context.active_object.location = list(x for x in list(map(sum, zip(boneLocation,location))))
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.transform.resize(value = (1/boneScale[0], 1/boneScale[1], 1/boneScale[2]))
    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='MEDIAN')
    bpy.context.active_object.rotation_euler = rotation
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    bpy.context.active_object.rotation_euler = list(x for x in list(map(sum, zip(rotation,boneRotation))))
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='MEDIAN')
    bpy.context.view_layer.active_layer_collection = parent_coll