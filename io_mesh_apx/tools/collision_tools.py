# -*- coding: utf-8 -*-
# tools/collision_tools.py

import bpy
import re
import numpy as np
from bpy_extras.object_utils import object_data_add
from mathutils import Vector
from copy import deepcopy
from io_mesh_apx.utils import JoinThem, applyTransforms, selectOnly, GetCollection, ImportTemplates, GetArmature, getWeightArray

def add_sphere(context, bone, radius, location, use_location, set_sim = False):
    collision_coll = GetCollection("Collision Spheres", True)
    spheres = collision_coll.objects
    main_coll = GetCollection(make_active=False)
    arma = GetArmature()   
    if main_coll["PhysXAssetType"] == "Clothing":
        if set_sim:
            for obj in arma.children:
                obj.modifiers['ClothSimulation']['Input_14'] = collision_coll
        capsule_coll = GetCollection("Collision Capsules", make_active=False)
        n_spheres = 0
        if collision_coll:
            n_spheres += len(collision_coll.objects)
        if capsule_coll:
            n_spheres += len(capsule_coll.objects)*2
        assert(n_spheres < 32)
           
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
    sphere = bpy.context.active_object
    
    num = 1
    sphere_temp_name = "sphere_" + bone.name + "_"
    while any([re.search(sphere_temp_name + str(num), x.name) for x in spheres]):
        num += 1
    else:
        sphere.name = sphere_temp_name + str(num)
    
    sphere.data.shade_smooth()    
    sphere.display_type = 'WIRE'
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    sphere.rotation_euler = boneRotation
    sphere.scale = boneScale
    sphere.location = boneLocation
    arm_mod = sphere.modifiers.new(type='ARMATURE', name = "Armature")
    arm_mod.object = arma
    bone_group = sphere.vertex_groups.new(name=bone.name)
    for k in range(len(sphere.data.vertices)):
        bone_group.add([k], 1, 'REPLACE')
    sphere.modifiers.new(type='COLLISION', name = "Collision")
    sphere.collision.thickness_outer = 0.001
    
    GetCollection()
    
    return sphere

def remove_sphere(context, index):
    collision_coll = GetCollection("Collision Spheres", make_active = False)
    connection_coll = GetCollection("Collision Connections", make_active = False)
    
    if collision_coll:
        if collision_coll.objects:
            
            if connection_coll:
                for obj in connection_coll.objects:
                    mod = obj.modifiers[0]
                    if mod["Input_2"] == collision_coll.objects[index] or mod["Input_3"] == collision_coll.objects[index]:
                        bpy.data.objects.remove(obj, do_unlink=True)
                        
                if not connection_coll.objects:
                    bpy.data.collections.remove(connection_coll, do_unlink=True)
                    
            bpy.data.objects.remove(collision_coll.objects[index], do_unlink=True)
            
        if not collision_coll.objects:
            bpy.data.collections.remove(collision_coll, do_unlink=True)
    
def add_connection(context, objects, set_sim = False):
    collision_coll = GetCollection("Collision Connections", True)
    main_coll = GetCollection(make_active=False)
    arma = GetArmature()
    if main_coll["PhysXAssetType"] == "Clothing" and set_sim:
        for obj in arma.children:
            obj.modifiers['ClothSimulation']['Socket_2'] = collision_coll
        
    #objCenter = []
    #objRadius = []
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
    
    bpy.ops.mesh.primitive_uv_sphere_add()
    
    connection = bpy.context.active_object
    connection.name = connectionName
    connection.display_type = 'WIRE'
    if "SphereConnectionTemplate" not in bpy.data.node_groups:
        ImportTemplates()
    node_group = bpy.data.node_groups["SphereConnectionTemplate"].copy()
    node_group.name = "SphereConnection"
    node_mod = connection.modifiers.new(type='NODES', name = "SphereConnection")
    node_mod.node_group = node_group
    node_mod["Input_2"] = objects[0]
    node_mod["Input_3"] = objects[1]
    connection.modifiers.new(type='COLLISION', name = "Collision")
    connection.collision.thickness_outer = 0.001
    
    GetCollection()
    
    return connection

def remove_connection(context, index):
    collision_coll = GetCollection("Collision Connections", make_active = False)
    
    if collision_coll:
        if collision_coll.objects:
            bpy.data.objects.remove(collision_coll.objects[index], do_unlink=True)
            
        if not collision_coll.objects:
            bpy.data.collections.remove(collision_coll, do_unlink=True)
    
def add_capsule(context, bone, radius, height, location, rotation, use_location, set_sim = False):
    collision_coll = GetCollection("Collision Capsules", True)
    arma = GetArmature()
    if set_sim:
        for obj in arma.children:
            obj.modifiers['ClothSimulation']['Socket_3'] = collision_coll
    capsules = collision_coll.objects
    sphere_coll = GetCollection("Collision Spheres", make_active=False)
    n_spheres = 0
    if sphere_coll:
        n_spheres += len(sphere_coll.objects)
    if collision_coll:
        n_spheres += len(collision_coll.objects)*2
    assert(n_spheres < 31)
    
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
    while any([re.search(capsule_temp_name + str(num), x.name) for x in capsules]):
        num += 1
    else:
        capsule.name = capsule_temp_name + str(num)
        
    capsule.data.shade_smooth()
    capsule.display_type = 'WIRE'
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    capsule.rotation_euler = boneRotation
    capsule.scale = boneScale
    capsule.location = boneLocation
    arm_mod = capsule.modifiers.new(type='ARMATURE', name = "Armature")
    arm_mod.object = arma
    bone_group = capsule.vertex_groups.new(name=bone.name)
    for k in range(len(capsule.data.vertices)):
        bone_group.add([k], 1, 'REPLACE')
    capsule.modifiers.new(type='COLLISION', name = "Collision")
    capsule.collision.thickness_outer = 0.001
    
    GetCollection()
    
    return capsule

def remove_capsule(context, index):
    collision_coll = GetCollection("Collision Capsules", make_active = False)
    
    if collision_coll:
        if collision_coll.objects:
            bpy.data.objects.remove(collision_coll.objects[index], do_unlink=True)
            
        if not collision_coll.objects:
            bpy.data.collections.remove(collision_coll, do_unlink=True)
    
def convert_capsule(context):
    collision_coll = GetCollection("Collision Capsules", False)
    arma = GetArmature()
    if collision_coll:
        armaScale = np.array(arma.scale)
        armaRot = np.array(arma.rotation_euler)
        armaLoc = np.array(arma.location)
        capsules = collision_coll.objects
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
                            spheres.append(add_sphere(bpy.context, boneName, sphereRadius, sphereLocation, True))
                            
                JoinThem(subCapsules)         
                add_connection(bpy.context, spheres)
        
        bpy.data.collections.remove(collision_coll, do_unlink=True)
        
def generateRagdoll(context, object):
    object = bpy.data.objects[object]
    mesh = object.data
    sphere_coll = GetCollection("Collision Spheres", True, False)
    connection_coll = GetCollection("Collision Connections", True, False)
    capsule_coll = GetCollection("Collision Capsules", True, False)
    while sphere_coll.objects:
        bpy.data.objects.remove(sphere_coll.objects[-1], do_unlink=True)
    bpy.data.collections.remove(connection_coll, do_unlink=True)
    bpy.data.collections.remove(capsule_coll, do_unlink=True)
    arma_main = GetArmature()
    bones_main = arma_main.data.bones
    
    arma = object.parent
    armaScale = np.array(arma.scale)
    armaRotation = np.array(arma.rotation_euler)
    armaLocation = np.array(arma.location)
    bones = arma.data.bones
    verts = mesh.vertices
    pos_array = np.zeros(len(verts) * 3)
    mesh.attributes['position'].data.foreach_get("vector", pos_array)
    pos_array = pos_array.reshape(-1, 3)
    vertex_groups = object.vertex_groups
    
    if len(bones) > 1:
        connection_coll = GetCollection("Collision Connections", True, False)
    
    spheres = []
    for bone in bones:
        bone_name = bone.name
        if bone_name in vertex_groups and bone_name in bones_main:
            vg = vertex_groups[bone.name]
            if any([vg.index in [g.group for g in v.groups] for v in verts]):
                bool_array = [vg.index in [g.group for g in v.groups] for v in verts]
                weight_array = getWeightArray(verts, vg)[bool_array]
                weighting_array = weight_array/weight_array.sum()
                bone_pos_array = pos_array[bool_array]
                location = np.sum(bone_pos_array * weighting_array.reshape(-1,1), axis = 0)
                dist_array = np.linalg.norm(bone_pos_array - location, axis = 1)
                radius = np.sum(dist_array * weighting_array)
                spheres.append(add_sphere(bpy.context, bone_name, radius, location, True))
                sphere = bpy.context.active_object
                sphere.rotation_euler = armaRotation
                sphere.scale = armaScale
                sphere.location = armaLocation
                
                parent = bone.parent
                if parent:
                    parent_object = re.findall(r"sphere_" + parent.name + "_\d+\.?\d*" , str([x.name for x in spheres]))
                    if parent_object:
                        add_connection(bpy.context, [spheres[-1], bpy.data.objects[parent_object[0]]])
                        
def mirrorRagdoll(context, pattern, replacement, axis):
    sphere_coll = GetCollection("Collision Spheres", False, False)
    connection_coll = GetCollection("Collision Connections", False, False)
    capsule_coll = GetCollection("Collision Capsules", False, False)
    arma = GetArmature()
    
    if sphere_coll:
        spheres = sphere_coll.objects
        num_spheres = len(spheres)
        sphere_names = [x.name[x.name.find("_")+1:x.name.rfind("_")] for x in spheres]
        for i in range(num_spheres):
            bone_name = sphere_names[i]
            if re.search(pattern, bone_name):
                new_name = re.sub(pattern, replacement, bone_name)
                sphere = spheres[i]
                new_sphere_name = re.sub(pattern, replacement, sphere.name)
                if not any([re.search(new_sphere_name, x.name) for x in spheres]):
                    sphereLocation, sphereRadius = applyTransforms(sphere, np.array(arma.scale), np.array(arma.rotation_euler), np.array(arma.location), True)
                    match axis:
                        case 'X':
                            sphereLocation[0] = -sphereLocation[0]
                        case 'Y':
                            sphereLocation[1] = -sphereLocation[1]
                        case 'Z':
                            sphereLocation[2] = -sphereLocation[2]
                    add_sphere(context, new_name, sphereRadius, sphereLocation, True)
                
    if connection_coll:
        connections = connection_coll.objects
        num_connections = len(connections)
        for i in range(num_connections):
            connection_name = connections[i].name
            new_connection_name = re.sub(pattern, replacement, connection_name)
            if not any([re.search(new_connection_name, x.name) for x in connections]):
                sphereName1 = connection_name[:connection_name.find("_to_")]
                sphereName2 = connection_name[connection_name.find("_to_")+4:]
                if re.search(pattern, sphereName1) or re.search(pattern, sphereName2):
                    add_connection(bpy.context, [bpy.data.objects[re.sub(pattern, replacement, sphereName1)], bpy.data.objects[re.sub(pattern, replacement, sphereName2)]])
                 
    if capsule_coll:
        capsules = capsule_coll.objects
        num_capsules = len(capsules)
        capsule_names = [x.name[x.name.find("_")+1:x.name.rfind("_")] for x in capsules]
        for i in range(num_capsules):
            bone_name = capsule_names[i]
            if re.search(pattern, bone_name):
                new_name = re.sub(pattern, replacement, bone_name)
                capsule = capsules[i]
                new_capsule_name = re.sub(pattern, replacement, capsule.name)
                if not any([re.search(new_capsule_name, x.name) for x in capsules]):
                    selectOnly(capsule)
                    bpy.ops.mesh.separate(type='MATERIAL')
                    spherePositions = []
                    subCapsules = []
                    for subCapsule in capsules:
                        if capsule.name in subCapsule.name:
                            subCapsules.append(subCapsule)
                            if "Material_Sphere1" in subCapsule.data.materials or "Material_Sphere2" in subCapsule.data.materials:
                                sphereLocation, sphereRadius = applyTransforms(subCapsule, np.array(arma.scale), np.array(arma.rotation_euler), np.array(arma.location), True)
                                spherePositions.append(sphereLocation)    
                    JoinThem(subCapsules)
                    capsuleDir = spherePositions[0] - spherePositions[1]
                    capsuleHeight = np.linalg.norm(capsuleDir)
                    capsulePosition = np.mean(spherePositions, axis = 0)
                    capsuleRotation = Vector((0,-capsuleHeight,0)).rotation_difference(capsuleDir).to_euler()
                    match axis:
                        case 'X':
                            capsulePosition[0] = -capsulePosition[0]
                            capsuleRotation[2] = capsuleRotation[2] + 2 * (2 * np.pi - capsuleRotation[2])
                            capsuleRotation[1] = capsuleRotation[1] + 2 * (2 * np.pi - capsuleRotation[1])
                        case 'Y':
                            capsulePosition[1] = -capsulePosition[1]
                            capsuleRotation[2] = capsuleRotation[2] + 2 * (2 * np.pi - capsuleRotation[2])
                            capsuleRotation[0] = capsuleRotation[0] + 2 * (2 * np.pi - capsuleRotation[0])
                        case 'Z':
                            capsulePosition[2] = -capsulePosition[2]
                            capsuleRotation[1] = capsuleRotation[1] + 2 * (2 * np.pi - capsuleRotation[1])
                            capsuleRotation[0] = capsuleRotation[0] + 2 * (2 * np.pi - capsuleRotation[0])
                    add_capsule(context, new_name, sphereRadius, capsuleHeight, capsulePosition, capsuleRotation, True)
                    
def lexarRagdoll(context, collection):
    main_coll = GetCollection(make_active = False)
    bones = GetArmature().data.bones
    asset = bpy.data.collections[collection]
    check_sphere = False
    if asset.children:
        for coll in asset.children:
            if "Collision Spheres" in coll.name and coll.objects:
                check_sphere = True
                sphere_coll = GetCollection("Collision Spheres", True, False)
                spheres = coll.objects
                sphere_bone_names = [x.name[x.name.find("_")+1:x.name.rfind("_")] for x in spheres]
                old_spheres = {}
                new_spheres = {}
                for i, obj in enumerate(spheres):
                    old_spheres[obj.name] = i
                    if sphere_bone_names[i] in bones:
                        selectOnly(obj)
                        bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
                        obj_dup = bpy.context.active_object
                        new_spheres[i] = obj_dup
                        sphere_coll.objects.link(obj_dup)
                        for col in obj_dup.users_collection:
                            if col != sphere_coll:
                                col.objects.unlink(obj_dup)
                        
            if "Collision Connections" in coll.name and coll.objects and check_sphere:
                connection_coll = GetCollection("Collision Connections", True, False)
                for obj in coll.objects:
                    x = obj.name
                    sphereName1 = x[:x.find("_to_")]
                    boneName1 = sphereName1[sphereName1.find("_")+1:sphereName1.rfind("_")]
                    sphereName2 = x[x.find("_to_")+4:]
                    boneName2 = sphereName2[sphereName2.find("_")+1:sphereName2.rfind("_")]
                    if boneName1 in bones and boneName2 in bones:
                        add_connection(context, [new_spheres[old_spheres[sphereName1]], new_spheres[old_spheres[sphereName2]]], False)
                                
            if "PhysXAssetType" in main_coll and main_coll['PhysXAssetType'] == 'Clothing':         
                if "Collision Capsules" in coll.name and coll.objects:
                    capsule_coll = GetCollection("Collision Capsules", True, False)
                    capsules = coll.objects
                    capsule_bone_names = [x.name[x.name.find("_")+1:x.name.rfind("_")] for x in capsules]
                    for i, obj in enumerate(capsules):
                        if capsule_bone_names[i] in bones:
                            selectOnly(obj)
                            bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
                            obj_dup = bpy.context.active_object
                            capsule_coll.objects.link(obj_dup)
                            for col in obj_dup.users_collection:
                                if col != capsule_coll:
                                    col.objects.unlink(obj_dup)
    
    