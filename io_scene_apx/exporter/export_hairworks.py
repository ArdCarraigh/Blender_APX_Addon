# -*- coding: utf-8 -*-
# exporter/export_clothing.py

import bpy
from math import sqrt
from mathutils import Matrix
from io_scene_apx.exporter import template_hairworks
from io_scene_apx.exporter.template_hairworks import template_hairworks
import numpy as np
import copy
from bpy_extras.object_utils import object_data_add


def getClosest(vec, vecList):
    vec = np.asarray(vec)
    vecList = np.asarray(vecList)
    diff = vecList - vec
    distance = np.linalg.norm(diff, axis=-1)
    return np.argmin(distance)


def write_hairworks(context, filepath, resample_value, spline):
    kwargs = {}
    
    # Get transforms of the armature
    if bpy.context.active_object.parent.type == "ARMATURE":
        armaScale = copy.deepcopy(bpy.context.active_object.parent.scale)
        armaRot = copy.deepcopy(bpy.context.active_object.parent.rotation_euler)
        armaLoc = copy.deepcopy(bpy.context.active_object.parent.location)
    
    # Use a duplicate growthmesh for resampling
    bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
    bpy.ops.object.mode_set(mode='PARTICLE_EDIT')
    bpy.ops.particle.select_all(action='SELECT')
    bpy.ops.particle.rekey(keys_number=resample_value)
    bpy.ops.particle.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Evaluate our duplicate and get its transforms
    duplicate_GrowthMesh = bpy.context.active_object
    ctxt_object_temp = bpy.context.active_object.evaluated_get(context.evaluated_depsgraph_get())
    meshScale = copy.deepcopy(duplicate_GrowthMesh.scale)
    meshRot = copy.deepcopy(duplicate_GrowthMesh.rotation_euler)
    meshLoc = copy.deepcopy(duplicate_GrowthMesh.location)
    
    # Make a temporary curve collection
    parent_coll = bpy.context.view_layer.active_layer_collection
    curve_coll_temp = bpy.data.collections.new("Curves_temp")
    curve_coll_temp_name = curve_coll_temp.name
    parent_coll.collection.children.link(curve_coll_temp)
    bpy.context.view_layer.active_layer_collection = parent_coll.children[curve_coll_temp_name]
    
    # Create curves from guides
    hairs_temp = ctxt_object_temp.particle_systems[0].particles
    for hair in hairs_temp:
        # create the Curve Datablock
        curveData = bpy.data.curves.new('myCurve_temp', type='CURVE')
        curveData.dimensions = '3D'
        curveData.resolution_u = 2
        curveData.bevel_depth = 0
        
        # map coords to spline
        polyline = curveData.splines.new('POLY')
        polyline.points.add(len(hair.hair_keys) - 1)
        for j in range(len(hair.hair_keys)):
            polyline.points[j].co = (*hair.hair_keys[j].co, 1)
        
        # Add the curves to the scene
        object_data_add(context, curveData)
        bpy.context.active_object.scale = meshScale
        bpy.context.active_object.rotation_euler = meshRot
        bpy.context.active_object.location = meshLoc
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.context.active_object.scale = [1/x for x in armaScale]
        bpy.context.active_object.rotation_euler = [2*(np.pi)-x for x in armaRot]
        bpy.context.active_object.location = [-1*x for x in armaLoc] 
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        
    # Delete particle system to allow applying transforms and triangulation of faces without messing up the hair
    bpy.context.view_layer.objects.active = None
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = duplicate_GrowthMesh
    bpy.context.active_object.select_set(state=True)
    bpy.ops.object.particle_system_remove()
    # Apply transforms
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.context.active_object.scale = [1/x for x in armaScale]
    bpy.context.active_object.rotation_euler = [2*(np.pi)-x for x in armaRot]
    bpy.context.active_object.location = [-1*x for x in armaLoc] 
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    # Triangulate faces
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.quads_convert_to_tris(quad_method='SHORTEST_DIAGONAL', ngon_method='BEAUTY')
    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.object.mode_set(mode='OBJECT')
    # Reapply hair after corrections
    bpy.ops.physx.shape_hair_interp(steps = 0)
    
    #Back to the state before corrections
    bpy.context.view_layer.active_layer_collection = parent_coll
    
    # Spline Multiplier
    kwargs['splines'] = spline
    
    #%% numHairs totalVerts
    ctxt_object = bpy.context.active_object.evaluated_get(context.evaluated_depsgraph_get())
    hairs = ctxt_object.particle_systems[0].particles
    kwargs['numHairs'] = len(hairs)
    kwargs['totalVerts'] = sum([len(p.hair_keys) for p in hairs])
    
    #%% hair_verts
    hair_verts = [] #list of vertices of all hairs
    meshCoords = [] #root vertex of each guide hair
    for hair in hairs:
        meshCoords.append(hair.hair_keys[0].co)
        for key in hair.hair_keys:
            hair_verts.append([key.co.x, key.co.y, key.co.z])
    kwargs['hair_verts'] = ', '.join([' '.join(map(str, vert)) for vert in hair_verts])
    
    #%% endIndices
    i = -1
    end_indices = [] #list of vertex indices of hair tips
    for hair in hairs:
        i += len(hair.hair_keys)
        end_indices.append(i)
    kwargs['endIndices'] = ' '.join(map(str, end_indices))
    
    #%% numFaces n_faceIndices faceIndices
    growth_mesh = ctxt_object.data
    face_indices = [] #list of indices into meshCoords for each vertex of each face
                      #  assuming {growth_mesh.vertices} == {meshCoords}
    for face in growth_mesh.polygons:
        for vertex in face.vertices:
            face_indices.append(getClosest(growth_mesh.vertices[vertex].co, meshCoords)) #maybe handle quads and tris?
    kwargs['numFaces'] = len(growth_mesh.polygons)
    kwargs['n_faceIndices'] = len(face_indices)
    kwargs['faceIndices'] = ' '.join(map(str, face_indices))
    
    #%% n_UVs UVs
    UVs = []
    uv_act = growth_mesh.uv_layers.active
    uv_layer = uv_act.data if uv_act is not None else [0.0, 0.0]
    for face in growth_mesh.polygons:
        for li in face.loop_indices:
            UVs.append(uv_layer[li].uv) 
    kwargs['n_UVs'] = len(UVs)
    kwargs['UVs'] = ', '.join(' '.join(map(str, [uv.x, 1-uv.y])) for uv in UVs)  # Not sure about this one, (1-uv.y)
                                                                                    # but it seems Maya exporter does something like that
                                                                                    # since I had to perform operations on its exported UV
                                                                                    # to get the original uv back 
    
    #%% numBones 
    bones = []
    poseBones = []
    usedBones = []
    boneIndex = {}
    boneIndex_value = 0
    if ctxt_object.parent.type == "ARMATURE":
        bones = ctxt_object.parent.data.bones
        poseBones = ctxt_object.parent.pose.bones
        for bone in bones:
            usedBones.append(bone)
            boneIndex[bone.name] = boneIndex_value
            boneIndex_value += 1
    kwargs['numBones'] = len(usedBones)
    
    #%% boneIndices boneWeights
    boneIndices = []
    boneWeights = []
    for vertex in growth_mesh.vertices:
        boneIndices.append(np.zeros(4, dtype=int))
        boneWeights.append(np.zeros(4, dtype=float))
        i = 0
        for g in vertex.groups:
            if i < 4 and g.weight > 0:
                boneIndices[-1][i] = boneIndex[ctxt_object.vertex_groups[g.group].name]
                boneWeights[-1][i] = g.weight
                i += 1
    kwargs['boneIndices'] = ', '.join(' '.join(map(str, x)) for x in boneIndices)
    kwargs['boneWeights'] = ', '.join(' '.join(map(str, x)) for x in boneWeights)
    
    # boneNames
    boneNames = []
    for bone in usedBones:
        for i in range(len(bone.name)):
            boneNames.append(str(ord(bone.name[i])))
        boneNames.append("0")
    
    kwargs['boneNamesSize'] = len(boneNames)
    kwargs['boneNames'] = ' '.join(boneNames)
        
    
    #%% boneNameList
    kwargs['boneNameList'] = '\n            '.join('<value type="String">{}</value>'.format(bone.name) for bone in usedBones)


    #%% bindPoses
    poses = []
    for bone in usedBones:
        for index, pose in enumerate(poseBones):
            if bone.name == pose.name:
                par_mat_inv = bones[bone.name].parent.matrix_local.inverted_safe() if bones[bone.name].parent and bones[bone.name].use_relative_parent else Matrix()
                matrix = par_mat_inv @ bones[bone.name].matrix_local
                if bones[bone.name].parent is not None and bones[bone.name].use_relative_parent:
                    matrix = ctxt_object.matrix_parent_inverse.inverted() * bones[bone.name].parent.matrix_local * matrix
                matrix.transpose()
                poses.append(matrix)
    kwargs['bindPoses'] = ', '.join(' '.join(map(str, np.array(matrix).flat)) for matrix in poses)
    
    #%% num_boneParents boneParents
    boneParents = []
    for pose in poseBones:
        if pose.parent is not None:
            for index, bone in enumerate(usedBones):
                if pose.parent.name == bone.name:
                    boneParents.append(ctxt_object.vertex_groups[bone.name].index)
        else:
            boneParents.append (-1)
    kwargs['num_boneParents'] = len(boneParents)
    kwargs['boneParents'] = ' '.join(map(str, boneParents))
    
    # boneSpheres
    kwargs['numBonesSpheres'] = "0"
    kwargs['boneSpheres'] = ""
    sphereIndex = {}
    sphereIndex_value = 0
    sphereBoneIndex = []
    sphereRadius = []
    sphereVec3 = []
    sphereAll = []
    if "Collision Spheres" in bpy.context.view_layer.active_layer_collection.collection.children:
        spheres = bpy.context.view_layer.active_layer_collection.collection.children['Collision Spheres'].objects
        if len(spheres) > 0:
            for sphere in spheres:
                bpy.context.view_layer.objects.active = None
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = sphere
                bpy.context.active_object.select_set(state=True)
                sphereIndex[sphere.name] = sphereIndex_value
                sphereIndex_value += 1
                sphereBoneName = sphere.name[sphere.name.find("_")+1:sphere.name.rfind("_")]
                sphereBoneIndex.append(boneIndex[sphereBoneName])
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                sphere.scale = [1/x for x in armaScale]
                sphere.rotation_euler = [2*(np.pi)-x for x in armaRot]
                sphere.location = [-1*x for x in armaLoc]
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='MEDIAN')
                vert_coord = sphere.data.vertices[0].co
                sphereRadius.append(sqrt((vert_coord[0])**2 + (vert_coord[1])**2 + (vert_coord[2])**2))
                sphereWorldVec = sphere.matrix_world.translation
                boneMatrix = bones[sphereBoneName].matrix_local
                sphereVec3.append(boneMatrix.inverted() @ sphereWorldVec)
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
                sphere.scale = armaScale
                sphere.rotation_euler = armaRot
                sphere.location = armaLoc
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                
            for i in range(len(sphereBoneIndex)):
                sphereAll.append([sphereBoneIndex[i], sphereRadius[i], sphereVec3[i][0], sphereVec3[i][1], sphereVec3[i][2]])
            
            kwargs['numBonesSpheres'] = len(spheres)
            kwargs['boneSpheres'] = ','.join(' '.join(map(str, x)) for x in sphereAll)
        
    # boneCapsuleIndices
    kwargs['numBoneCapsules'] = "0"
    kwargs['numBoneCapsuleIndices'] = "0"
    kwargs['boneCapsuleIndices'] = ""
    boneCapsules = []
    if "Collision Spheres Connections" and "Collision Spheres" in bpy.context.view_layer.active_layer_collection.collection.children:
        connections = bpy.context.view_layer.active_layer_collection.collection.children['Collision Spheres Connections'].objects
        if len(connections) > 0:
            for connection in connections:
                sphereName1 = connection.name[:connection.name.find("_to_")]
                sphereName2 = connection.name[connection.name.find("_to_")+4:]
                boneCapsules.append([sphereIndex[sphereName1], sphereIndex[sphereName2]])
                
            kwargs['numBoneCapsules'] = len(connections)
            kwargs['numBoneCapsuleIndices'] = len(connections) * 2
            kwargs['boneCapsuleIndices'] = ' '.join(' '.join(map(str,x)) for x in boneCapsules)
            
        
    # pinConstraints
    kwargs['numPinConstraints'] = "0"
    kwargs['pinConstraints'] = ""
    pinBoneIndex = []
    pinRadius = []
    pinVec3 = []
    pinAll = []
    if "Pin Constraints" in bpy.context.view_layer.active_layer_collection.collection.children:
        pins = bpy.context.view_layer.active_layer_collection.collection.children['Pin Constraints'].objects
        if len(pins) > 0:
            for pin in pins:
                bpy.context.view_layer.objects.active = None
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = pin
                bpy.context.active_object.select_set(state=True)
                pinBoneName = pin.name[pin.name.find("_")+1:pin.name.rfind("_")]
                pinBoneIndex.append(boneIndex[pinBoneName])
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                pin.scale = [1/x for x in armaScale]
                pin.rotation_euler = [2*(np.pi)-x for x in armaRot]
                pin.location = [-1*x for x in armaLoc]
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='MEDIAN')
                vert_coord = pin.data.vertices[0].co
                pinRadius.append(sqrt((vert_coord[0])**2 + (vert_coord[1])**2 + (vert_coord[2])**2))
                pinWorldVec = pin.matrix_world.translation
                boneMatrix = bones[pinBoneName].matrix_local
                pinVec3.append(boneMatrix.inverted() @ pinWorldVec)
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
                pin.scale = armaScale
                pin.rotation_euler = armaRot
                pin.location = armaLoc
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                
            for i in range(len(pinBoneIndex)):
                pinAll.append([pinBoneIndex[i], pinRadius[i], pinVec3[i][0], pinVec3[i][1], pinVec3[i][2],0,0,"false","false","fasle",0,0,0,0])
            
            kwargs['numPinConstraints'] = len(pins)
            kwargs['pinConstraints'] = ','.join(' '.join(map(str, x)) for x in pinAll) 
    
    # Delete the duplicate growthmesh used for resampling as well as the temporary curve collection
    bpy.context.view_layer.objects.active = None
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = duplicate_GrowthMesh
    bpy.context.active_object.select_set(state=True)
    bpy.ops.object.delete(use_global=False, confirm=False)
    bpy.data.collections.remove(curve_coll_temp)
    
    
    #%% write the template with generated values
    with open(filepath, 'w', encoding = 'utf-8') as f:
        f.write(template_hairworks.format(**kwargs))