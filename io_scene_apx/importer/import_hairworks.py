# -*- coding: utf-8 -*-
# importer/import_hairworks.py

import xml.etree.ElementTree as ET
import numpy as np
import random, colorsys
import bpy
from bpy_extras.object_utils import object_data_add
from mathutils import Matrix, Vector
from itertools import count

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

def make_cone(pos_1, R1, pos_2, R2, name, rotate_180, scale_down):
    AB = np.linalg.norm(pos_2-pos_1)
    BE = abs(R2-R1)
    AE = (AB**2 - (R2-R1)**2)**.5
    cone_radius_1 = R1 * AE / AB
    cone_radius_2 = R2 * AE / AB
    AG = R1 * BE / AB
    BF = R2 * BE / AB
    
    AB_dir = (pos_2-pos_1)/AB
    if R1 > R2:
        cone_pos = pos_1 + AB_dir * AG
    else:
        cone_pos = pos_1 - AB_dir * AG
    
    cone_depth = AB - abs(AG-BF)
    cone_pos = cone_pos + AB_dir * cone_depth * .5 #cone pos is midpoint of centerline
    rotation = Vector([0,0,1]).rotation_difference(Vector(AB_dir)).to_euler("XYZ") ### may need to change
    
    bpy.ops.mesh.primitive_cone_add(
        vertices=24, 
        radius1=cone_radius_1, 
        radius2=cone_radius_2, 
        depth=cone_depth, 
        location=cone_pos, 
        rotation=rotation, 
        )
    bpy.context.active_object.name = name
    bpy.context.active_object.display_type = 'WIRE'
    # Rotation of the spheres
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    if rotate_180 == True:
        bpy.context.active_object.rotation_euler[2] += np.pi #took me way too long to find that I needed += 
    # Scale down if requested
    if scale_down == True:
        bpy.context.active_object.scale = (0.01, 0.01, 0.01)

def read_hairworks(context, filepath, rotate_180, scale_down, minimal_armature):

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
    
    # compute edges
    guide_edges = [[i, i+1] for i in range(numVertices) if i not in endIndices]
    
    # add the guides to the scene
    guides_mesh = bpy.data.meshes.new(name="Guides")
    guides_mesh.from_pydata(vertices, guide_edges, [])
    object_data_add(context, guides_mesh)

    # scene options
    # Rotation of the guies if requested
    if rotate_180 == True:
        bpy.context.active_object.rotation_euler[2] = np.pi

    # Scale down if requested
    if scale_down == True:
        bpy.context.active_object.scale = (0.01, 0.01, 0.01)
        
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
        if rotate_180 == True:
            bpy.context.active_object.rotation_euler[2] = np.pi
        
        # Scale down if requested
        if scale_down == True:
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
    if rotate_180 == True:
        bpy.context.active_object.rotation_euler[2] = np.pi

    # Scale down if requested
    if scale_down == True:
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
            growth_mesh.uv_layers.active.data[loop_idx].uv = faceUVs[loop_idx] * [1,-1] + [0,1]
            
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
    
    # boneParents_text = find_elem(HairAssetDescriptor, "array", "name", "boneParents").text
    # boneParents = to_array(boneParents_text, int, [-1])
    
    # create 1 armature per bone
    armaNames = []
    for i in range([len(boneNames), boneIndices.max()+1][minimal_armature]):
        bpy.context.view_layer.objects.active = None
        bpy.ops.object.select_all(False)
        skeleton = bpy.data.armatures.new(name="Armature")
        object_data_add(context, skeleton)
        armaNames.append(bpy.context.active_object.name)
        # Edit mode required to add bones to the armature
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        b = skeleton.edit_bones.new(boneNames[i])
        
        b.head = np.array((0,0,0))
        b.tail = np.array((0,1,0))
        #Transform the armature to have the correct transformation, edit_bone.transform() gives wrong results
        bpy.ops.object.mode_set(mode='OBJECT')
        
        skeleton.transform(Matrix(bindPoses[i].T))
        
    # Join the armatures made for each bone together
    for i in reversed(range(len(armaNames))):
        bpy.context.view_layer.objects.active = bpy.data.objects[armaNames[i]]
        bpy.context.active_object.select_set(state=True)
    bpy.ops.object.join()
    
    # Back to object mode
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # scene options
    # Rotation of the armature if requested
    if rotate_180 == True:
        bpy.context.active_object.rotation_euler[2] = np.pi

    # Scale down if requested
    if scale_down == True:
        bpy.context.active_object.scale = (0.01, 0.01, 0.01)

    arma_name = bpy.context.active_object.name
    
    # Parenting
    bpy.context.view_layer.objects.active = None
    bpy.context.view_layer.objects.active = bpy.data.objects[growth_mesh_name]
    bpy.context.active_object.select_set(state=True)
    bpy.context.view_layer.objects.active = bpy.data.objects[arma_name]
    bpy.ops.object.parent_set(type="ARMATURE_NAME", xmirror=False, keep_transform=False)

    # Bone Weighting
    bpy.context.view_layer.objects.active = None
    bpy.context.view_layer.objects.active = bpy.data.objects[growth_mesh_name]
    # mesh2 = bpy.data.objects[growth_mesh_name] #redundant from line 99? same as `growth_mesh`?
    #active object same as growth_mesh?
    for j, (indices, weights) in enumerate(zip(boneIndices, boneWeights)):
        for i in range(4):
            if weights[i] != 0:
                bpy.context.active_object.vertex_groups[indices[i]].add([j], weights[i], 'REPLACE')
    
    
    #%% bone spheres
    numBoneSpheres = int(find_elem(HairAssetDescriptor, "value", "name", "numBoneSpheres").text)
    if numBoneSpheres > 0:
        
        # read from file
        boneSpheres_text = find_elem(HairAssetDescriptor, "array", "name", "boneSpheres").text
        boneSpheres = to_array(boneSpheres_text, float, [-1,5]) #interpret bone index as int later
        #assert(len(boneSpheres) == numBoneSpheres) #off by 1 error? 
        
        # Create a collection for collision spheres
        sphere_coll = bpy.data.collections.new("Collision Spheres")
        sphere_coll_name = sphere_coll.name
        parent_coll.collection.children.link(sphere_coll)
        bpy.context.view_layer.active_layer_collection = parent_coll.children[sphere_coll_name]
        
        # Add the spheres to the scene
        sphere_names = []
        sphere_coords = []
        sphere_radii = []
        for b_sphere in boneSpheres:
            bone_name = boneNames[int(b_sphere[0])]
            for i in count():
                sphere_name = f"sphere_{bone_name}_{i+1}"
                if sphere_name not in sphere_names:
                    sphere_names.append(sphere_name)
                    break
                elif i > 100:
                    raise ValueError("something went very wrong") #don't count() forever. we dont likely need more than 100 spheres per bone...
            sphere_coords.append(Matrix(bindPoses[int(b_sphere[0])].T) @ Vector(b_sphere[2:5]))
            sphere_radii.append(b_sphere[1])
            bpy.ops.mesh.primitive_uv_sphere_add(radius = b_sphere[1], 
                                                 location = sphere_coords[-1], 
                                                 segments=24, ring_count=16)
            bpy.context.active_object.name = sphere_name
            # sphere_names.append(bpy.context.active_object.name)
            bpy.context.active_object.display_type = 'WIRE'
            # Rotation of the spheres
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
            if rotate_180 == True:
                bpy.context.active_object.rotation_euler[2] = np.pi
            # Scale down if requested
            if scale_down == True:
                bpy.context.active_object.scale = (0.01, 0.01, 0.01)
    
    #%% BoneCapsules
    numBoneCapsules = int(find_elem(HairAssetDescriptor, "value", "name", "numBoneCapsules").text)
    if numBoneCapsules > 0 and numBoneSpheres > 0:

        sphere_coll_connec = bpy.data.collections.new("Collision Spheres Connections")
        sphere_coll_connec_name = sphere_coll_connec.name
        parent_coll.collection.children.link(sphere_coll_connec)
        bpy.context.view_layer.active_layer_collection = parent_coll.children[sphere_coll_connec_name]
        
        boneCapsuleIndices_text = find_elem(HairAssetDescriptor, "array", "name", "boneCapsuleIndices").text
        boneCapsuleIndices = to_array(boneCapsuleIndices_text, int, [-1, 2])
        assert(len(boneCapsuleIndices) == numBoneCapsules)
        
        for a, b in boneCapsuleIndices:
            make_cone(sphere_coords[a], sphere_radii[a], 
                      sphere_coords[b], sphere_radii[b], 
                      sphere_names[a] + "_to_" + sphere_names[b], 
                      rotate_180, scale_down)

    #%% pin constraints
    # read from file
    numPinConstraints = int(find_elem(HairAssetDescriptor, "value", "name", "numPinConstraints").text)
    if numPinConstraints > 0:

        pin_coll = bpy.data.collections.new("Pin Constraints")
        pin_coll_name = pin_coll.name
        parent_coll.collection.children.link(pin_coll)
        bpy.context.view_layer.active_layer_collection = parent_coll.children[pin_coll_name]
        
        pinConstraints_text = find_elem(HairAssetDescriptor, "array", "name", "pinConstraints").text
        pinConstraints_flat = pinConstraints_text.replace(',', ' ').split()
        
        pin_names = []
        assert(len(pinConstraints_flat) == numPinConstraints * 14)
        for i in range(0,len(pinConstraints_flat), 14):
            boneSphereIndex = int(pinConstraints_flat[i])
            boneSphereRadius = float(pinConstraints_flat[i+1])
            boneSphereLocalPos = np.array([float(x) for x in pinConstraints_flat[i+2:i+5]])
        
            bone_name = boneNames[boneSphereIndex]
            for i in count():
                pin_name = f"pin_{bone_name}_{i+1}"
                if pin_name not in pin_names:
                    pin_names.append(pin_name)
                    break
                elif i > 100:
                    raise ValueError("something went very wrong") #don't count() forever. we dont likely need more than 100 spheres per bone...
        
            coordinates_world = Matrix(bindPoses[boneSphereIndex].T) @ Vector(boneSphereLocalPos)
            
            bpy.ops.mesh.primitive_uv_sphere_add(radius = boneSphereRadius, location = coordinates_world, segments=24, ring_count=16)
            bpy.context.active_object.name = pin_name
            
            bpy.context.active_object.display_type = 'WIRE'
            # Rotation of the pins
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
            if rotate_180 == True:
                bpy.context.active_object.rotation_euler[2] = np.pi
            # Scale down if requested
            if scale_down == True:
                bpy.context.active_object.scale = (0.01, 0.01, 0.01)

    bpy.context.view_layer.active_layer_collection = parent_coll
    
    pass

    
