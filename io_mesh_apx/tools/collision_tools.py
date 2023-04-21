# -*- coding: utf-8 -*-
# tools/collision_tools.py

import bpy
import numpy as np
from bpy_extras.object_utils import object_data_add
from mathutils import Vector
from copy import deepcopy
from io_mesh_apx.utils import JoinThem, applyTransforms, selectOnly

def add_sphere(context, radius, location, use_location):
    parent_coll = bpy.context.view_layer.active_layer_collection
    if "Collision Spheres" in parent_coll.collection.children:
        bpy.context.view_layer.active_layer_collection = parent_coll.children["Collision Spheres"]
    else:
        sphere_coll = bpy.data.collections.new("Collision Spheres")
        parent_coll.collection.children.link(sphere_coll)
        bpy.context.view_layer.active_layer_collection = parent_coll.children[sphere_coll.name]
        
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
    sphere = bpy.context.active_object
    
    num = 1
    sphere_temp_name = "sphere_" + bone.name + "_"
    while sphere_temp_name + str(num) in bpy.context.view_layer.active_layer_collection.collection.objects:
        num += 1
    else:
        sphere.name = sphere_temp_name + str(num)
        
    sphere.display_type = 'WIRE'
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    sphere.rotation_euler = boneRotation
    sphere.scale = boneScale
    sphere.location = boneLocation
    bpy.context.view_layer.active_layer_collection = parent_coll
    
    return sphere
    
def add_connection(context):
    parent_coll = bpy.context.view_layer.active_layer_collection
    if "Collision Spheres Connections" in parent_coll.collection.children:
        bpy.context.view_layer.active_layer_collection = parent_coll.children["Collision Spheres Connections"]
    else:
        sphere_connec_coll = bpy.data.collections.new("Collision Spheres Connections")
        parent_coll.collection.children.link(sphere_connec_coll)
        bpy.context.view_layer.active_layer_collection = parent_coll.children[sphere_connec_coll.name]
        
    objects = bpy.context.selected_objects
    objCenter = []
    objRadius = []
    objName = []
    assert(len(objects) == 2)
    
    correctNames = 0
    for obj in objects:
        objName.append(obj.name)
        if obj.name.startswith("sphere_") == True and "_to_" not in obj.name:
            correctNames += 1
    assert(correctNames == 2)
    
    connectionName = objName[0] + "_to_" + objName[1]
    assert(connectionName not in bpy.context.view_layer.active_layer_collection.collection.objects)
    for obj in objects:
        selectOnly(obj)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='MEDIAN')
        objCenter.append(deepcopy(obj.matrix_world.translation))
        objRadius.append(np.linalg.norm(obj.data.vertices[0].co))
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    
    pos_2 = objCenter[1]
    pos_1 = objCenter[0]
    R2 = objRadius[1]
    R1 = objRadius[0]
    
    AB = np.linalg.norm(pos_2-pos_1)
    BE = abs(R2-R1)
    AE = (AB**2 - (BE)**2)**.5
    AE_AB = AE/AB
    BE_AB = BE/AB
    cone_radius_1 = R1 * AE_AB
    cone_radius_2 = R2 * AE_AB
    AG = R1 * BE_AB
    BF = R2 * BE_AB
    
    AB_dir = (pos_2-pos_1)/AB
    if R1 > R2:
        cone_pos = pos_1 + AB_dir * AG
    else:
        cone_pos = pos_1 - AB_dir * AG
    
    cone_depth = AB - abs(AG-BF)
    cone_pos = cone_pos + AB_dir * cone_depth * 0.5 #cone pos is midpoint of centerline
    rotation = Vector([0,0,1]).rotation_difference(Vector(AB_dir)).to_euler("XYZ") ### may need to change
    
    bpy.ops.mesh.primitive_cone_add(
        vertices=24, 
        radius1=cone_radius_1, 
        radius2=cone_radius_2, 
        depth=cone_depth, 
        location=cone_pos, 
        rotation=rotation, 
        )
    
    connection = bpy.context.active_object
    connection.name = connectionName
    connection.display_type = 'WIRE'
            
    bpy.context.view_layer.active_layer_collection = parent_coll
    
    return connection
    
def add_capsule(context, radius, height, location, rotation, use_location):
    parent_coll = bpy.context.view_layer.active_layer_collection
    if "Collision Capsules" in parent_coll.collection.children:
        bpy.context.view_layer.active_layer_collection = parent_coll.children["Collision Capsules"]
    else:
        capsule_coll = bpy.data.collections.new("Collision Capsules")
        parent_coll.collection.children.link(capsule_coll)
        bpy.context.view_layer.active_layer_collection = parent_coll.children[capsule_coll.name]
    
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
    height = np.array(height) / boneScale[1]
        
    if "Material_Sphere1" not in bpy.data.materials:
        sphere1_mat = bpy.data.materials.new("Material_Sphere1")
    if "Material_Sphere2" not in bpy.data.materials:
        sphere2_mat = bpy.data.materials.new("Material_Sphere2")
    if "Material_Cylinder" not in bpy.data.materials:
        cylinder_mat = bpy.data.materials.new("Material_Cylinder")
    
    meshes = []
    half_height = height/2
    rot90 = (-np.pi/2,0,0)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=(0,half_height,0), segments=24, ring_count=16, rotation = rot90)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.context.active_object.data.materials.append(bpy.data.materials["Material_Sphere1"])
    meshes.append(bpy.context.active_object)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=(0,-half_height,0), segments=24, ring_count=16, rotation = rot90)
    bpy.context.active_object.data.materials.append(bpy.data.materials["Material_Sphere2"])
    meshes.append(bpy.context.active_object)
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=radius, radius2=radius, depth=height, rotation = rot90)
    bpy.context.active_object.data.materials.append(bpy.data.materials["Material_Cylinder"])
    meshes.append(bpy.context.active_object)
    JoinThem(meshes)
    capsule = bpy.context.active_object
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    bpy.ops.mesh.remove_doubles()
    bpy.ops.transform.translate(value=location)
    bpy.ops.transform.rotate(value = rotation[0], orient_axis='X', constraint_axis=(True, False, False))
    bpy.ops.transform.rotate(value = rotation[1], orient_axis='Y', constraint_axis=(False, True, False))
    bpy.ops.transform.rotate(value = rotation[2], orient_axis='Z', constraint_axis=(False, False, True))
    bpy.ops.object.mode_set(mode='OBJECT')
    
    num = 1
    capsule_temp_name = "capsule_" + bone.name + "_"
    while capsule_temp_name + str(num) in bpy.context.view_layer.active_layer_collection.collection.objects:
        num += 1
    else:
        capsule.name = capsule_temp_name + str(num)
        
    capsule.display_type = 'WIRE'
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    capsule.rotation_euler = boneRotation
    capsule.scale = boneScale
    capsule.location = boneLocation
    bpy.context.view_layer.active_layer_collection = parent_coll
    
    return capsule
    
def convert_capsule(context):
    parent_coll = bpy.context.view_layer.active_layer_collection
    arma = bpy.context.active_object
    if "Collision Capsules" in parent_coll.collection.children and arma.type=='ARMATURE':
        armaScale = np.array(arma.scale)
        armaRot = np.array(arma.rotation_euler)
        armaLoc = np.array(arma.location)
        capsules = parent_coll.collection.children['Collision Capsules'].objects
        if capsules:
            for capsule in capsules:
                capsule_name = capsule.name
                boneName = capsule_name[capsule_name.find("_")+1:capsule_name.rfind("_")]
                selectOnly(capsule)
                bpy.ops.mesh.separate(type='MATERIAL')
                spheres = []
                subCapsules = []
                for subCapsule in capsules:
                    if capsule_name in subCapsule.name:
                        subCapsules.append(subCapsule)
                        if "Material_Sphere1" in subCapsule.data.materials or "Material_Sphere2" in subCapsule.data.materials:
                            sphereLocation, sphereRadius = applyTransforms(subCapsule, armaScale, armaRot, armaLoc, True)
                            bpy.context.view_layer.objects.active = None
                            bpy.ops.object.select_all(action='DESELECT')
                            bpy.context.view_layer.objects.active = arma
                            arma.select_set(state=True)
                            arma.data.bones.active = arma.data.bones[boneName]
                            spheres.append(add_sphere(bpy.context, sphereRadius, sphereLocation, True))
                            
                JoinThem(subCapsules)
                
                bpy.context.view_layer.objects.active = None
                bpy.ops.object.select_all(action='DESELECT')
                for sphere in spheres:
                    bpy.context.view_layer.objects.active = sphere
                    sphere.select_set(state=True)
                add_connection(context = bpy.context)