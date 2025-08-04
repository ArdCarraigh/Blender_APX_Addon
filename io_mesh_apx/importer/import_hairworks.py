# -*- coding: utf-8 -*-
# importer/import_hairworks.py

import xml.etree.ElementTree as ET
import numpy as np
import random, colorsys
import bpy
import os.path
from bpy_extras.object_utils import object_data_add
from mathutils import Matrix, Vector
from io_mesh_apx.tools.collision_tools import add_sphere, add_connection
from io_mesh_apx.tools.hair_tools import add_pin, shape_hair_interp
from io_mesh_apx.utils import find_elem, to_array, selectOnly, str2bool, simValueType, str2floatvec, SetUpWind
from io_mesh_apx.tools.setup_tools import SetUpHairworksMaterial

def read_hairworks(context, filepath, rotate_180):
    
    # Create Main Collection #
    file_name = os.path.splitext(os.path.basename(filepath))[0]
    parent_coll = bpy.context.view_layer.active_layer_collection
    main_coll = bpy.data.collections.new(file_name)
    main_coll["PhysXAssetType"] = "Hairworks"
    parent_coll.collection.children.link(main_coll)
    bpy.context.view_layer.active_layer_collection = parent_coll.children[main_coll.name]
    
    # Set Up Wind
    SetUpWind()
    
    # Parse File
    root = ET.parse(filepath).getroot() #NvParameters element
    HairAssetDescriptor = find_elem(root, "value", "className", "HairAssetDescriptor")[0] #extra [0] to index into <struct>

    #%% Armature and bones creation
    numBones = int(find_elem(HairAssetDescriptor, "value", "name", "numBones").text)
    
    boneNames_text = find_elem(HairAssetDescriptor, "array", "name", "boneNames").text
    boneNames = ''.join(map(lambda c: chr(int(c)), boneNames_text.replace(',', ' ').split())).replace('\x00', ' ').split()
    if not boneNames:
        boneNames_text = find_elem(HairAssetDescriptor, "array", "name", "boneNameList").text.split('\n')
        boneNames = to_array(boneParents_text, str, [-1])
        [x[x.find(">")+1:x.rfind("<")] for x in boneNames]
    assert(len(boneNames) == numBones)
    
    bindPoses_text = find_elem(HairAssetDescriptor, "array", "name", "bindPoses").text
    bindPoses = to_array(bindPoses_text, float, [-1, 4, 4])
    assert(len(bindPoses) == numBones)
    
    boneParents_text = find_elem(HairAssetDescriptor, "array", "name", "boneParents").text
    boneParents = to_array(boneParents_text, int, [-1])
    assert(len(boneParents) == numBones)
    
    # Create Armature
    skeleton = bpy.data.armatures.new(name="Armature")
    arma = object_data_add(context, skeleton)
    # Edit mode required to add bones to the armature
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    for i in range(len(boneNames)):
        b = skeleton.edit_bones.new(boneNames[i])
        b.head = (0,0,0)
        b.tail = (0,1,0)
        b.matrix = Matrix(bindPoses[i].T)
    # Parenting Bones
    for i, bone in enumerate(skeleton.edit_bones):
        if boneParents[i] != -1:
            bone.parent = skeleton.edit_bones[boneNames[boneParents[i]]]
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # scene options
    # Rotation of the armature if requested
    if rotate_180:
        arma.rotation_euler[2] = np.pi

    #%% guides
    # read from file
    numGuideHairs = int(find_elem(HairAssetDescriptor, "value", "name", "numGuideHairs").text)
    
    numVertices = int(find_elem(HairAssetDescriptor, "value", "name", "numVertices").text)
    
    vertices_text = find_elem(HairAssetDescriptor, "array", "name", "vertices").text
    vertices = to_array(vertices_text, float, [-1,3])
    assert(len(vertices) == numVertices)
    
    endIndices_text = find_elem(HairAssetDescriptor, "array", "name", "endIndices").text
    endIndices = to_array(endIndices_text, int, [-1])
    assert(len(endIndices) == numGuideHairs)
    
    #%% guide curves
    # Create a new collection to store curves
    parent_coll = bpy.context.view_layer.active_layer_collection
    curve_coll = bpy.data.collections.new("Curves")
    curve_coll["Hairworks Curves"] = True
    curve_coll_name = curve_coll.name
    parent_coll.collection.children.link(curve_coll)
    bpy.context.view_layer.active_layer_collection = parent_coll.children[curve_coll_name]
    
    # Create curves from guides and compute vertices
    growth_verts = [vertices[0]]
    start_idx = 0
    endIndex = endIndices[-1] + 1
    vertices_1 = np.hstack([vertices, np.ones((numVertices,1))])
    for end_idx in endIndices + 1: #endIndices + 1 because of inclusive indexing
        
        #(first vert from each hair)
        if end_idx != endIndex:
            growth_verts.append(vertices[end_idx])
            
        # create the Curve Datablock
        curveData = bpy.data.curves.new('myCurve', type='CURVE')
        curveData.dimensions = '3D'
        curveData.resolution_u = 2
        
        # map coords to spline
        polyline = curveData.splines.new('POLY')
        polyline.points.add(end_idx - start_idx - 1)
        polyline.points.foreach_set("co", vertices_1[start_idx:end_idx].flatten())
        
        # Add the curves to the scene
        obj = object_data_add(context, curveData)
        
        # Rotation of the curves if requested
        if rotate_180:
            obj.rotation_euler[2] = np.pi
        
        start_idx = end_idx
        
    bpy.context.view_layer.active_layer_collection = parent_coll

    #%% growth mesh
    # read from file
    numFaces = int(find_elem(HairAssetDescriptor, "value", "name", "numFaces").text)
    
    faceIndices_text = find_elem(HairAssetDescriptor, "array", "name", "faceIndices").text
    faceIndices = to_array(faceIndices_text, int, [-1, 3])
    assert(len(faceIndices) == numFaces)
    
    faceUVs_text = find_elem(HairAssetDescriptor, "array", "name", "faceUVs").text
    faceUVs = to_array(faceUVs_text, float, -1)
    assert(len(faceUVs) == numFaces * 6)  
    
    # Add the growthmesh to the scene
    growth_mesh = bpy.data.meshes.new(name="GrowthMesh")
    growth_mesh.from_pydata(growth_verts, [], list(faceIndices))
    obj = object_data_add(context, growth_mesh)
    growth_mesh.shade_smooth()

    # scene options
    # Rotation of the growthmesh if requested
    if rotate_180:
        obj.rotation_euler[2] = np.pi

    # UVmap creation
    uv_map = growth_mesh.attributes.new("DiffuseUV", 'FLOAT2', 'CORNER')
    faceUVs[1::2] = 1-faceUVs[1::2]
    uv_map.data.foreach_set("vector", faceUVs)
    
    # Bone Indices
    boneIndices_text = find_elem(HairAssetDescriptor, "array", "name", "boneIndices").text
    numBonesPerVertex = np.array([int(x) for x in boneIndices_text[:boneIndices_text.find(",")].split()]).size
    boneIndices = to_array(boneIndices_text, int, [-1, numBonesPerVertex])
    assert(len(boneIndices) == numGuideHairs)
    
    # Bone Weights
    boneWeights_text = find_elem(HairAssetDescriptor, "array", "name", "boneWeights").text
    boneWeights = to_array(boneWeights_text, float, [-1, numBonesPerVertex])
    assert(len(boneWeights) == numGuideHairs)
    
    # Parenting
    obj.select_set(state=True)
    bpy.context.view_layer.objects.active = arma
    bpy.ops.object.parent_set(type="ARMATURE_NAME", xmirror=False, keep_transform=False)
    bpy.context.view_layer.objects.active = None
    bpy.ops.object.select_all(action='DESELECT')

    # Bone Weighting
    for j, (indices, weights) in enumerate(zip(boneIndices, boneWeights)):
        for i in range(numBonesPerVertex):
            weight = weights[i]
            if weight:
                obj.vertex_groups[boneNames[indices[i]]].add([j], weight, 'REPLACE')
        
    # Apply curves as hair particle system
    shape_hair_interp(bpy.context, obj, curve_coll_name)
    
    #%% bone spheres
    numBoneSpheres = int(find_elem(HairAssetDescriptor, "value", "name", "numBoneSpheres").text)
    if numBoneSpheres:
        
        # read from file
        boneSpheres_text = find_elem(HairAssetDescriptor, "array", "name", "boneSpheres").text
        boneSpheres = to_array(boneSpheres_text, float, [-1,5]) #interpret bone index as int later
        assert(len(boneSpheres) == numBoneSpheres)
        
        # Add the spheres to the scene
        sphere_objs = []
        for b_sphere in boneSpheres:
            boneName = boneNames[int(b_sphere[0])]
            coordinates_world = skeleton.bones[boneName].matrix_local @ Vector(b_sphere[2:5])
            sphere_objs.append(add_sphere(bpy.context, boneName, b_sphere[1], coordinates_world, True))
    
    #%% BoneCapsules
    numBoneCapsules = int(find_elem(HairAssetDescriptor, "value", "name", "numBoneCapsules").text)
    if numBoneCapsules and numBoneSpheres:
        
        boneCapsuleIndices_text = find_elem(HairAssetDescriptor, "array", "name", "boneCapsuleIndices").text
        boneCapsuleIndices = to_array(boneCapsuleIndices_text, int, [-1, 2])
        assert(len(boneCapsuleIndices) == numBoneCapsules)
        
        for a, b in boneCapsuleIndices:
            add_connection(bpy.context, [sphere_objs[a], sphere_objs[b]])

    #%% pin constraints
    numPinConstraints = int(find_elem(HairAssetDescriptor, "value", "name", "numPinConstraints").text)
    if numPinConstraints:
        
        # read from file
        pin_elem = find_elem(HairAssetDescriptor, "array", "name", "pinConstraints")
        pin_struct = pin_elem.attrib["structElements"]
        pinConstraints_text = pin_elem.text
        if pin_struct == "boneSphereIndex(I32),boneSphereRadius(F32),boneSphereLocalPos(Vec3)":
            pinConstraints = to_array(pinConstraints_text, str, [-1,5])
            pinConstraints = np.hstack((pinConstraints, np.tile(["0", "0", "false", "false", "false", "0", "0", "0", "0"], (len(pinConstraints),1))))
        else:
            pinConstraints = to_array(pinConstraints_text, str, [-1,14])
        assert(len(pinConstraints) == numPinConstraints)
        
        for b_sphere in pinConstraints:
            boneName = boneNames[int(b_sphere[0])]
            coordinates_world = skeleton.bones[boneName].matrix_local @ Vector(b_sphere[2:5].astype(float))
            add_pin(bpy.context, boneName, float(b_sphere[1]), coordinates_world, True, float(b_sphere[5]), float(b_sphere[6]), str2bool(b_sphere[7]), str2bool(b_sphere[8]), str2bool(b_sphere[9]), b_sphere[10:].astype(float))
            
    # Hair Material
    HairSceneDescriptor = find_elem(root, "value", "className", "HairSceneDescriptor")[0] #extra [0] to index into <struct>
    HairInstanceDescriptor = find_elem(root, "value", "className", "HairInstanceDescriptor")[0][0][0] #extra [0]'s to index into first material and <struct>
    
    material = {}
    material["textureDirName"] = ""
    for elem in HairSceneDescriptor:
        elem_text = elem.text
        if elem_text:
            if not material["textureDirName"]:
                material["textureDirName"] = os.path.dirname(elem_text)
            material[elem.attrib["name"]] = os.path.basename(elem_text)
        else:
            material[elem.attrib["name"]] = ''

    for elem in HairInstanceDescriptor:
        elem_name = elem.attrib["name"]
        if elem_name in ["diffuseBoneLocalPos", "wind", "gravity"]:
            material[elem_name] = str2floatvec(elem.text)
        elif "Chan" in elem_name:
            material[elem_name] = str(elem.text)
        elif elem_name == "name":
            if elem.text:
                material["matName"] = str(elem.text)
            else:
                material["matName"] = ''
        else:
            func_type = simValueType(elem.attrib["type"])
            material[elem_name] = func_type(elem.text)
    material["colorizeLODOption"] = str(material["colorizeLODOption"])
    material["strandBlendMode"] = str(material["strandBlendMode"])
    if material["diffuseBoneIndex"] >= numBones:
        material["diffuseBoneIndex"] = 0
    material["diffuseBoneIndex"] = str(material["diffuseBoneIndex"])
    
    SetUpHairworksMaterial(obj, main_coll, material)