# -*- coding: utf-8 -*-
# importer/import_hairworks.py

import xml.etree.ElementTree as ET
import numpy as np
import random, colorsys
import bpy
from bpy_extras.object_utils import object_data_add
from mathutils import Matrix, Vector

def find_elem(root, tag, attr=None, attr_value=None):
    for elem in root:
        if elem.tag == tag:
            if not attr:
                return elem
            else:
                if attr in elem.attrib and attr_value == elem.attrib[attr]:
                    return elem
    raise Exception("element not found")
    
def to_array(text, dtype, shape):
    return(np.array([dtype(x) for x in text.replace(',', ' ').split()]).reshape(shape))

def JoinThem(mesh_names):
    bpy.context.view_layer.objects.active = None
    bpy.ops.object.select_all(action='DESELECT')
    for j in reversed(range(len(mesh_names))):
        bpy.context.view_layer.objects.active = bpy.data.objects[mesh_names[j]]
        bpy.context.active_object.select_set(state=True)
    bpy.ops.object.join()

def read_hairworks(context, filepath, rotate_180, scale_down):

    root = ET.parse(filepath).getroot() #NvParameters element
    HairAssetDescriptor = find_elem(root, "value", "className", "HairAssetDescriptor")[0] #extra [0] to index into <struct>

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
    curve_coll_name = curve_coll.name
    parent_coll.collection.children.link(curve_coll)
    bpy.context.view_layer.active_layer_collection = parent_coll.children[curve_coll_name]
    
    # Create curves from guides
    start_idx = 0
    for end_idx in endIndices + 1: #endIndices + 1 because of inclusive indexing
        # create the Curve Datablock
        curveData = bpy.data.curves.new('myCurve', type='CURVE')
        curveData.dimensions = '3D'
        curveData.resolution_u = 2
        curveData.bevel_depth = 0
        
        # map coords to spline
        polyline = curveData.splines.new('POLY')
        polyline.points.add(end_idx - start_idx - 1)
        for j in range(start_idx, end_idx):
            polyline.points[j-start_idx].co = (*vertices[j], 1)
        
        # Add the curves to the scene
        object_data_add(context, curveData)
        
        # Rotation of the curves if requested
        if rotate_180:
            bpy.context.active_object.rotation_euler[2] = np.pi
        
        # Scale down if requested
        if scale_down:
            bpy.context.active_object.scale = (0.01, 0.01, 0.01)
        start_idx = end_idx
        
    bpy.context.view_layer.active_layer_collection = parent_coll

    #%% growth mesh
    # read from file
    numFaces = int(find_elem(HairAssetDescriptor, "value", "name", "numFaces").text)
    
    faceIndices_text = find_elem(HairAssetDescriptor, "array", "name", "faceIndices").text
    faceIndices = to_array(faceIndices_text, int, [-1, 3])
    assert(len(faceIndices) == numFaces)
    
    faceUVs_text = find_elem(HairAssetDescriptor, "array", "name", "faceUVs").text
    faceUVs = to_array(faceUVs_text, float, [-1, 2])
    assert(len(faceUVs) == numFaces * 3)
    
    # compute vertices
    #(first vert from each hair)
    growth_verts = [vertices[0]]
    for idx in endIndices[:-1]:
        growth_verts.append(vertices[idx+1])
    
    # Add the growthmesh to the scene
    growth_mesh = bpy.data.meshes.new(name="GrowthMesh")
    growth_mesh.from_pydata(growth_verts, [], list(faceIndices))
    object_data_add(context, growth_mesh)
    for i in growth_mesh.polygons:
        i.use_smooth = True

    # scene options
    # Rotation of the growthmesh if requested
    if rotate_180:
        bpy.context.active_object.rotation_euler[2] = np.pi

    # Scale down if requested
    if scale_down:
        bpy.context.active_object.scale = (0.01, 0.01, 0.01)
        
    # Materials attribution
    growth_mesh_name = bpy.context.active_object.name
    mesh2 = bpy.data.objects[growth_mesh_name]
    temp_mat = bpy.data.materials.new("Material0")
    mesh2.data.materials.append(temp_mat)
    temp_mat.diffuse_color = (*colorsys.hsv_to_rgb(random.random(), .7, .9), 1) #random hue more pleasing than random rgb

    # UVmap creation
    growth_mesh.uv_layers.new(name="DiffuseUV")
    for face in growth_mesh.polygons:
        for loop_idx in face.loop_indices:
            growth_mesh.uv_layers["DiffuseUV"].data[loop_idx].uv = faceUVs[loop_idx] * [1,-1] + [0,1]
            
    #%% Armature and bones creation
    
    # read from file
    # numBones = int(find_elem(HairAssetDescriptor, "value", "name", "numBones").text)
    
    boneIndices_text = find_elem(HairAssetDescriptor, "array", "name", "boneIndices").text
    boneIndices = to_array(boneIndices_text, int, [-1, 4])
    assert(len(boneIndices) == numGuideHairs)
    
    boneWeights_text = find_elem(HairAssetDescriptor, "array", "name", "boneWeights").text
    boneWeights = to_array(boneWeights_text, float, [-1, 4])
    assert(len(boneWeights) == numGuideHairs)
    
    #XXX is this really the common way to encode bone names? it's bass ackwards...
    boneNames = find_elem(HairAssetDescriptor, "array", "name", "boneNames").text
    boneNames = ''.join(map(lambda c: chr(int(c)), boneNames.replace(',', ' ').split())).replace('\x00', ' ').split()
    
    # boneNameList = find_elem(HairAssetDescriptor, "array", "name", "boneNameList").text.split(',') #I'm just assuming the separator because I don't have any examples
    
    bindPoses_text = find_elem(HairAssetDescriptor, "array", "name", "bindPoses").text
    bindPoses = to_array(bindPoses_text, float, [-1, 4, 4])
    
    boneParents_text = find_elem(HairAssetDescriptor, "array", "name", "boneParents").text
    boneParents = to_array(boneParents_text, int, [-1])
    
    # create 1 armature per bone
    armaNames = []
    for i in range(len(boneNames)):
        bpy.context.view_layer.objects.active = None
        bpy.ops.object.select_all(action='DESELECT')
        skeleton = bpy.data.armatures.new(name="Armature")
        object_data_add(context, skeleton)
        armaNames.append(bpy.context.active_object.name)
        # Edit mode required to add bones to the armature
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        b = skeleton.edit_bones.new(boneNames[i])
        b.head = np.array((0,0,0))
        b.tail = np.array((0,1,0))
        bpy.ops.object.mode_set(mode='OBJECT')
        #Transform the armature to have the correct transformation, edit_bone.transform() gives wrong results
        skeleton.transform(Matrix(bindPoses[i].T))
        
    # Join the armatures made for each bone together
    JoinThem(armaNames)
    arma = bpy.context.active_object
    
    # Parenting Bones
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    for i in range(len(arma.data.edit_bones)):
        if scale_down:
            arma.data.edit_bones[i].length = 100
        if boneParents[i] != -1:
            arma.data.edit_bones[i].parent = arma.data.edit_bones[boneNames[boneParents[i]]]
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # scene options
    # Rotation of the armature if requested
    if rotate_180:
        arma.rotation_euler[2] = np.pi

    # Scale down if requested
    if scale_down:
        arma.scale = (0.01, 0.01, 0.01)
    
    # Parenting
    bpy.context.view_layer.objects.active = None
    bpy.context.view_layer.objects.active = bpy.data.objects[growth_mesh_name]
    bpy.context.active_object.select_set(state=True)
    bpy.context.view_layer.objects.active = bpy.data.objects[arma.name]
    bpy.ops.object.parent_set(type="ARMATURE_NAME", xmirror=False, keep_transform=False)
    bpy.context.view_layer.objects.active = None
    bpy.ops.object.select_all(action='DESELECT')

    # Bone Weighting
    bpy.context.view_layer.objects.active = bpy.data.objects[growth_mesh_name]
    for j, (indices, weights) in enumerate(zip(boneIndices, boneWeights)):
        for i in range(4):
            if weights[i] != 0:
                bpy.context.active_object.vertex_groups[boneNames[indices[i]]].add([j], weights[i], 'REPLACE')
        
    # Apply curves as hair particle system
    bpy.context.active_object.select_set(state=True)
    bpy.context.view_layer.active_layer_collection = parent_coll.children[curve_coll_name]
    bpy.ops.physx.shape_hair_interp(steps = 0)
    bpy.context.view_layer.active_layer_collection = parent_coll
    
    #%% bone spheres
    numBoneSpheres = int(find_elem(HairAssetDescriptor, "value", "name", "numBoneSpheres").text)
    if numBoneSpheres > 0:
        
        # read from file
        boneSpheres_text = find_elem(HairAssetDescriptor, "array", "name", "boneSpheres").text
        boneSpheres = to_array(boneSpheres_text, float, [-1,5]) #interpret bone index as int later
        #assert(len(boneSpheres) == numBoneSpheres) #off by 1 error? 
        
        # Add the spheres to the scene
        sphere_names = []
        for b_sphere in boneSpheres:
            bone_name = boneNames[int(b_sphere[0])]
            bpy.context.view_layer.objects.active = arma
            arma.data.bones.active = arma.data.bones[bone_name]
            coordinates_world = bpy.context.active_bone.matrix_local @ Vector(b_sphere[2:5])
            boneSphereRadius = b_sphere[1]*[1,0.01][scale_down]
            bpy.ops.physx.add_collision_sphere(radius = boneSphereRadius, location = coordinates_world, use_location = True)
            sphere_names.append(bpy.context.active_object.name)
    
    #%% BoneCapsules
    numBoneCapsules = int(find_elem(HairAssetDescriptor, "value", "name", "numBoneCapsules").text)
    if numBoneCapsules > 0 and numBoneSpheres > 0:
        
        boneCapsuleIndices_text = find_elem(HairAssetDescriptor, "array", "name", "boneCapsuleIndices").text
        boneCapsuleIndices = to_array(boneCapsuleIndices_text, int, [-1, 2])
        assert(len(boneCapsuleIndices) == numBoneCapsules)
        
        for a, b in boneCapsuleIndices:
            bpy.context.view_layer.objects.active = None
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = bpy.data.objects[sphere_names[a]]
            bpy.context.active_object.select_set(state=True)
            bpy.context.view_layer.objects.active = bpy.data.objects[sphere_names[b]]
            bpy.context.active_object.select_set(state=True)
            bpy.ops.physx.add_sphere_connection()

    #%% pin constraints
    
    numPinConstraints = int(find_elem(HairAssetDescriptor, "value", "name", "numPinConstraints").text)
    if numPinConstraints > 0:
        
        # read from file
        pinConstraints_text = find_elem(HairAssetDescriptor, "array", "name", "pinConstraints").text
        pinConstraints_flat = pinConstraints_text.replace(',', ' ').split()
        
        assert(len(pinConstraints_flat) == numPinConstraints * 14)
        for i in range(0,len(pinConstraints_flat), 14):
            boneSphereIndex = int(pinConstraints_flat[i])
            boneSphereRadius = float(pinConstraints_flat[i+1])*[1,0.01][scale_down]
            boneSphereLocalPos = np.array([float(x) for x in pinConstraints_flat[i+2:i+5]])
            bone_name = boneNames[boneSphereIndex]
            bpy.context.view_layer.objects.active = arma
            arma.data.bones.active = arma.data.bones[bone_name]
            coordinates_world = bpy.context.active_bone.matrix_local @ Vector(boneSphereLocalPos)
            bpy.ops.physx.add_pin_sphere(radius = boneSphereRadius, location = coordinates_world, use_location = True)
    
    pass