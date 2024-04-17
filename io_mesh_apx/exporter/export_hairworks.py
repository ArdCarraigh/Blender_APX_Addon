# -*- coding: utf-8 -*-
# exporter/export_hairworks.py

import bpy
from mathutils import Matrix
import numpy as np
from bpy_extras.object_utils import object_data_add
from io_mesh_apx.exporter.template_hairworks import template_hairworks
from io_mesh_apx.utils import applyTransforms, TriangulateActiveMesh, selectOnly, GetCollection, GetArmature
from io_mesh_apx.tools.hair_tools import shape_hair_interp, create_curve

def write_hairworks(context, filepath, resample_value):
    kwargs = {}
    main_coll = GetCollection()
    assert(main_coll is not None)
    
    # Get transforms of the armature
    arma = GetArmature()
    armaScale = np.array(arma.scale)
    armaRot = np.array(arma.rotation_euler)
    armaLoc = np.array(arma.location)
    assert(arma.children is not None)
    
    # Make the main mesh active
    main_mesh = arma.children[0]
    selectOnly(main_mesh)
    
    # Use a duplicate growthmesh for resampling
    bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
    bpy.ops.object.mode_set(mode='PARTICLE_EDIT')
    bpy.ops.particle.select_all(action='SELECT')
    bpy.ops.particle.rekey(keys_number=resample_value)
    bpy.ops.particle.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    duplicate_GrowthMesh = bpy.context.active_object
    
    # Create temporary curves and get all hair verts
    create_curve(bpy.context, duplicate_GrowthMesh)
    curve_coll_temp = bpy.context.view_layer.active_layer_collection.collection
    
    # Apply transforms
    applyTransforms(duplicate_GrowthMesh, armaScale, armaRot, armaLoc)
        
    # Triangulate faces
    TriangulateActiveMesh()
    # Reapply hair after triangulation as it messes with the hair,
    # and get all hair coordinates at the same time
    hair_verts = shape_hair_interp(bpy.context, duplicate_GrowthMesh, curve_coll_temp.name)
    
    #Back to the state before corrections
    GetCollection()
    
    #%% numHairs totalVerts
    hairs = duplicate_GrowthMesh.particle_systems[-1].particles
    n_hairs = len(hairs)
    n_vertices = n_hairs * resample_value
    kwargs['numHairs'] = n_hairs
    kwargs['totalVerts'] = n_vertices
    
    #%% hair_verts
    kwargs['hair_verts'] = ', '.join([' '.join(map(str, vert)) for vert in hair_verts.reshape(-1,3)])
    
    #%% endIndices #list of vertex indices of hair tips
    kwargs['endIndices'] = ' '.join(map(str, np.arange(resample_value-1, n_vertices, resample_value)))
    
    #%% numFaces n_faceIndices faceIndices
    growth_mesh = duplicate_GrowthMesh.data
    n_faces = len(growth_mesh.polygons)
    n_face_indices = n_faces * 3
    face_array = np.zeros(n_face_indices, dtype=int)
    growth_mesh.attributes[".corner_vert"].data.foreach_get("value", face_array)
    kwargs['numFaces'] = n_faces
    kwargs['n_faceIndices'] = n_face_indices
    kwargs['faceIndices'] = ' '.join(map(str, face_array))
    
    #%% UVs
    uv_name = growth_mesh.uv_layers.active.name
    uv_array = np.zeros(n_face_indices*2)
    growth_mesh.attributes[uv_name].data.foreach_get("vector", uv_array)
    uv_array[1::2] = 1-uv_array[1::2]
    kwargs['UVs'] = ', '.join(' '.join(map(str, uv)) for uv in uv_array.reshape(-1,2))
    
    #%% numBones boneNamesSize boneNames boneNameList 
    boneIndex = {}
    boneNames = []
    bones = duplicate_GrowthMesh.parent.data.bones
    for i, bone in enumerate(bones):
        bone_name = bone.name
        boneIndex[bone_name] = i
        for j in bone_name:
            boneNames.append(str(ord(j)))
        boneNames.append("0")
    n_bones = i + 1
    kwargs['numBones'] = n_bones
    kwargs['boneNamesSize'] = len(boneNames)
    kwargs['boneNames'] = ' '.join(boneNames)
    kwargs['boneNameList'] = '\n            '.join('<value type="String">{}</value>'.format(bone) for bone in boneIndex)
    
    #%% boneParents bindPoses
    boneParents = []
    poses = np.zeros(n_bones*16)
    bones.foreach_get("matrix_local", poses)
    poses = poses.reshape(-1,4,4)
    for i, bone in enumerate(bones):
        bone_parent = bone.parent
        if bone_parent:
            boneParents.append(boneIndex[bone_parent.name])
            if bone.use_relative_parent:
                poses[i] = np.array(duplicate_GrowthMesh.matrix_parent_inverse.inverted() * bone.parent.matrix_local * (bone_parent.matrix_local.inverted_safe() @ Matrix(poses[i])))
        else:
            boneParents.append(-1)
    kwargs['boneParents'] = ' '.join(map(str, boneParents))
    kwargs['bindPoses'] = ', '.join(' '.join(map(str, matrix.flat)) for matrix in poses)
    
    #%% boneIndices boneWeights
    boneIndices = []
    boneWeights = []
    vertex_groups = duplicate_GrowthMesh.vertex_groups
    for vertex in growth_mesh.vertices:
        boneIndices.append(np.zeros(4, dtype=int))
        boneWeights.append(np.zeros(4, dtype=float))
        i = 0
        for g in vertex.groups:
            g_weight = g.weight
            if i < 4 and g_weight and vertex_groups[g.group].name in boneIndex:
                boneIndices[-1][i] = boneIndex[vertex_groups[g.group].name]
                boneWeights[-1][i] = g_weight
                i += 1
    boneWeights = [x/x.sum() for x in boneWeights]
    kwargs['boneIndices'] = ', '.join(' '.join(map(str, x)) for x in boneIndices)
    kwargs['boneWeights'] = ', '.join(' '.join(map(str, x)) for x in boneWeights)
    
    # boneSpheres
    kwargs['numBonesSpheres'] = "0"
    kwargs['boneSpheres'] = ""
    sphereIndex = {}
    sphereAll = []
    sphere_coll = GetCollection("Collision Spheres", make_active=False)
    if sphere_coll:
        spheres = sphere_coll.objects
        if spheres:
            for i, sphere in enumerate(spheres):
                sphere_name = sphere.name
                sphereIndex[sphere_name] = i
                sphereBoneName = sphere_name[sphere_name.find("_")+1:sphere_name.rfind("_")]
                sphereLocation, sphereRadius = applyTransforms(sphere, armaScale, armaRot, armaLoc, True, True, bones[sphereBoneName])
                sphereAll.append([boneIndex[sphereBoneName], sphereRadius, *sphereLocation])
            kwargs['numBonesSpheres'] = len(spheres)
            kwargs['boneSpheres'] = ','.join(' '.join(map(str, x)) for x in sphereAll)
        
    # boneCapsuleIndices
    kwargs['numBoneCapsules'] = "0"
    kwargs['numBoneCapsuleIndices'] = "0"
    kwargs['boneCapsuleIndices'] = ""
    boneCapsules = []
    connection_coll = GetCollection("Collision Connections", make_active=False)
    if sphere_coll and connection_coll:
        connections = connection_coll.objects
        if connections:
            for connection in connections:
                connection_name = connection.name
                sphereName1 = connection_name[:connection_name.find("_to_")]
                sphereName2 = connection_name[connection_name.find("_to_")+4:]
                boneCapsules.append([sphereIndex[sphereName1], sphereIndex[sphereName2]])
            kwargs['numBoneCapsules'] = len(connections)
            kwargs['numBoneCapsuleIndices'] = len(connections) * 2
            kwargs['boneCapsuleIndices'] = ' '.join(' '.join(map(str,x)) for x in boneCapsules)
            
        
    # pinConstraints
    kwargs['numPinConstraints'] = "0"
    kwargs['pinConstraints'] = ""
    pinAll = []
    pin_coll = GetCollection("Pin Constraints", make_active=False)
    if pin_coll:
        pins = pin_coll.objects
        if pins:
            for pin in pins:
                pin_name = pin.name
                pinBoneName = pin_name[pin_name.find("_")+1:pin_name.rfind("_")]
                pinLocation, pinRadius = applyTransforms(pin, armaScale, armaRot, armaLoc, True, True, bones[pinBoneName])
                pinAll.append([boneIndex[pinBoneName], pinRadius, *pinLocation, pin["pinStiffness1"], pin["influenceFallOff"], str(pin["useDynamicPin1"]).lower(), str(pin["doLra"]).lower(), str(pin["useStiffnessPin"]).lower(), *pin["influenceFallOffCurve"]])
            kwargs['numPinConstraints'] = len(pins)
            kwargs['pinConstraints'] = ','.join(' '.join(map(str, x)) for x in pinAll) 
    
    # Delete the duplicate growthmesh used for resampling as well as the temporary curve collection
    bpy.data.objects.remove(duplicate_GrowthMesh)
    bpy.data.collections.remove(curve_coll_temp)
    
    # Write Simulation Material
    for key in main_mesh.keys():
        kwargs[key] = main_mesh[key]
        if type(kwargs[key]) == bool:
            kwargs[key] = str(kwargs[key]).lower()
        elif hasattr(kwargs[key], '__len__') and not isinstance(kwargs[key], str):
            kwargs[key] = ' '.join(map(str, list(kwargs[key])))
            
    # Add path to textures
    if main_mesh["textureDirName"]:
        for key in ["densityTexture", "rootColorTexture", "tipColorTexture", "widthTexture", "rootWidthTexture",
        "tipWidthTexture", "stiffnessTexture","rootStiffnessTexture", "clumpScaleTexture", "clumpRoundnessTexture",
        "clumpNoiseTexture", "waveScaletexture", "waveFreqTexture", "strandTexture", "lengthTexture", "specularTexture"]:
            if kwargs[key]:
                kwargs[key] = main_mesh["textureDirName"] + "\\" + kwargs[key]
    
    #%% write the template with generated values
    with open(filepath, 'w', encoding = 'utf-8') as f:
        f.write(template_hairworks.format(**kwargs))