# -*- coding: utf-8 -*-
# tools/convert_capsule.py

import bpy
import numpy as np
import copy
from math import sqrt
from io_scene_apx.importer import import_hairworks
from io_scene_apx.importer.import_hairworks import JoinThem

def convert_capsule(context):
    parent_coll = bpy.context.view_layer.active_layer_collection
    arma = bpy.context.active_object
    if "Collision Capsules" in parent_coll.collection.children and arma.type=='ARMATURE':
        armaScale = arma.scale
        armaRot = arma.rotation_euler
        armaLoc = arma.location
        capsules = parent_coll.collection.children['Collision Capsules'].objects
        if len(capsules) > 0:
            for capsule in capsules:
                bpy.context.view_layer.objects.active = None
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = capsule
                bpy.context.active_object.select_set(state=True)
                boneName = capsule.name[capsule.name.find("_")+1:capsule.name.rfind("_")]
                bpy.ops.mesh.separate(type='MATERIAL')
                sphereNames = []
                subCapsuleNames = []
                for subCapsule in capsules:
                    if capsule.name in subCapsule.name:
                        subCapsuleNames.append(subCapsule.name)
                        if "Material_Sphere1" in subCapsule.data.materials or "Material_Sphere2" in subCapsule.data.materials:
                            bpy.context.view_layer.objects.active = None
                            bpy.ops.object.select_all(action='DESELECT')
                            bpy.context.view_layer.objects.active = subCapsule
                            bpy.context.active_object.select_set(state=True)
                            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                            subCapsule.scale = [1/x for x in armaScale]
                            subCapsule.rotation_euler = [2*(np.pi)-x for x in armaRot]
                            subCapsule.location = [-1*x for x in armaLoc]
                            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                            bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='MEDIAN')
                            sphereLocation = copy.deepcopy(subCapsule.matrix_world.translation)
                            vert_coord = subCapsule.data.vertices[0].co
                            sphereRadius = sqrt((vert_coord[0])**2 + (vert_coord[1])**2 + (vert_coord[2])**2)
                            bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
                            subCapsule.scale = armaScale
                            subCapsule.rotation_euler = armaRot
                            subCapsule.location = armaLoc
                            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                            
                            bpy.context.view_layer.objects.active = None
                            bpy.ops.object.select_all(action='DESELECT')
                            bpy.context.view_layer.objects.active = arma
                            bpy.context.active_object.select_set(state=True)
                            arma.data.bones.active = arma.data.bones[boneName]
                            bpy.ops.physx.add_collision_sphere(radius = sphereRadius, location = sphereLocation, use_location = True)
                            sphereNames.append(bpy.context.active_object.name)
                            
                JoinThem(subCapsuleNames)
                
                bpy.context.view_layer.objects.active = None
                bpy.ops.object.select_all(action='DESELECT')
                for sphere in sphereNames:
                    bpy.context.view_layer.objects.active = bpy.data.objects[sphere]
                    bpy.context.active_object.select_set(state=True)
                bpy.ops.physx.add_sphere_connection()