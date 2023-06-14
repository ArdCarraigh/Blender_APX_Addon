# -*- coding: utf-8 -*-
# importer/import_clothing.py

import bpy
import random, colorsys
import xml.etree.ElementTree as ET
import numpy as np
from bpy_extras.object_utils import object_data_add
from mathutils import Vector, Matrix
from io_mesh_apx.number_to_words import getWords
from io_mesh_apx.tools.paint_tools import add_physx_clothing_palette
from io_mesh_apx.tools.collision_tools import *
from io_mesh_apx.utils import find_elem, to_array, JoinThem, selectOnly

def read_clothing(context, filepath, rotate_180, rm_ph_me):
    
    # Create Color Palette
    add_physx_clothing_palette()

    # Parse File
    root = ET.parse(filepath).getroot() #NxParameters element
    ClothingAssetParameters = find_elem(root, "value", "className", "ClothingAssetParameters")[0] #extra [0] to index into <struct>
    
    # Armature and Bones
    Armature = find_elem(ClothingAssetParameters, "array", "name", "bones")
    numBones = int(Armature.attrib["size"])
    assert(len(Armature) == numBones)
    
    boneNames = []
    boneParents = []
    skeleton = bpy.data.armatures.new(name="Armature")
    arma = object_data_add(context, skeleton)
    # Edit mode required to add bones to the armature
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    for i in range(numBones):
        boneParent = int(find_elem(Armature[i], "value", "name", "parentIndex").text)
        boneParents.append(boneParent)
        bindPose_text = find_elem(Armature[i], "value", "name", "bindPose").text
        bindPose = to_array(bindPose_text, float, [-1, 4, 3])
        boneName = find_elem(Armature[i], "value", "name", "name").text
        boneNames.append(boneName)
        b = skeleton.edit_bones.new(boneName)
        b.head = Vector((0,0,0))
        b.tail = Vector((0,1,0))
        b.matrix = Matrix(bindPose.T).to_4x4()
    # Parenting Bones  
    for i, bone in enumerate(skeleton.edit_bones):
        if boneParents[i] != -1:
            bone.parent = skeleton.edit_bones[boneNames[boneParents[i]]]
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Rotation of the armature
    if rotate_180:
        arma.rotation_euler[2] = np.pi
    
    # Graphical Meshes
    GraphicalLods = find_elem(ClothingAssetParameters, "array", "name", "graphicalLods")
    numGraphicalLods = int(GraphicalLods.attrib["size"])
    assert(len(GraphicalLods) == numGraphicalLods)
    finalMeshes = []
    for i in range(numGraphicalLods):
        GraphicalLod = GraphicalLods[i][0] #extra [0] to index into <struct>
        GraphicalMesh = find_elem(GraphicalLod, "value", "name", "renderMeshAsset")[0] #extra [0] to index into <struct>
        # Materials
        materials = find_elem(GraphicalMesh, "array", "name", "materialNames")
        materialNames = []
        for j in range(len(materials)):
            material_name = materials[j].text
            if len(material_name) > 63: #Deal with Blender's material's name length limit
                material_name = material_name[-63:]
            materialNames.append(material_name)
        SubMeshes = find_elem(GraphicalMesh, "array", "name", "submeshes")
        numSubMeshes = int(SubMeshes.attrib["size"])
        assert (len(SubMeshes) == numSubMeshes)
        assert(len(materials) == numSubMeshes)
        meshes = []
        for j in range(numSubMeshes):
            SubMesh = SubMeshes[j][0][0][0] #extra [0]s to index into <struct>
            numVertices = int(find_elem(SubMesh, "value", "name", "vertexCount").text)
            SubMesh_VertexFormat = find_elem(SubMesh, "value", "name", "vertexFormat")[0]
            SubMesh_BufferFormats = find_elem(SubMesh_VertexFormat, "array", "name", "bufferFormats")
            numSubMesh_BufferFormats = int(SubMesh_BufferFormats.attrib["size"])
            assert (len(SubMesh_BufferFormats) == numSubMesh_BufferFormats)
            bufferFormats = []
            for k in range(numSubMesh_BufferFormats):
                bufferFormats.append(find_elem(SubMesh_BufferFormats[k], "value", "name", "name").text)
            SubMesh_Buffers = find_elem(SubMesh, "array", "name", "buffers")
            numSubMesh_Buffers = int(SubMesh_Buffers.attrib["size"])
            assert (len(SubMesh_Buffers) == numSubMesh_Buffers)
            assert (numSubMesh_BufferFormats == numSubMesh_Buffers)
            allUVMaps = []
            for k in range(numSubMesh_Buffers):
                buffer = SubMesh_Buffers[k][0]
                if bufferFormats[k] == 'SEMANTIC_POSITION':
                    vertices_text = find_elem(buffer, "array", "name", "data").text
                    vertices = to_array(vertices_text, float, [-1, 3])
                    assert (len(vertices) == numVertices)
                elif bufferFormats[k] == 'SEMANTIC_NORMAL':
                    normals_text = find_elem(buffer, "array", "name", "data").text
                    normals = to_array(normals_text, float, [-1, 3])
                    assert (len(normals) == numVertices)
                elif bufferFormats[k] == 'SEMANTIC_TANGENT':
                    tangents_text = find_elem(buffer, "array", "name", "data").text
                    tangents = to_array(tangents_text, float, [-1, 4])
                    assert (len(tangents) == numVertices)
                elif 'SEMANTIC_TEXCOORD' in bufferFormats[k]:
                    uvs_text = find_elem(buffer, "array", "name", "data").text
                    uvs = to_array(uvs_text, float, [-1, 2])
                    assert (len(uvs) == numVertices)
                    allUVMaps.append(uvs)
                elif bufferFormats[k] == 'SEMANTIC_BONE_INDEX':
                    boneIndices_text = find_elem(buffer, "array", "name", "data").text
                    boneIndices = to_array(boneIndices_text, int, [-1, 4])
                    assert (len(boneIndices) == numVertices)
                elif bufferFormats[k] == 'SEMANTIC_BONE_WEIGHT':
                    boneWeights_text = find_elem(buffer, "array", "name", "data").text
                    boneWeights = to_array(boneWeights_text, float, [-1, 4])
                    assert (len(boneWeights) == numVertices)
                elif bufferFormats[k] == 'SEMANTIC_BONE_WEIGHT':
                    boneWeights_text = find_elem(buffer, "array", "name", "data").text
                    boneWeights = to_array(boneWeights_text, float, [-1, 4])
                    assert (len(boneWeights) == numVertices)
                elif bufferFormats[k] == 'SEMANTIC_COLOR':
                    vertexColor_text = find_elem(buffer, "array", "name", "data").text
                    vertexColor = to_array(vertexColor_text, float, [-1]) * 0.003922
                    assert (len(vertexColor) == numVertices*4)
            faces_text = find_elem(SubMeshes[j][0], "array", "name", "indexBuffer").text
            faces = to_array(faces_text, int, [-1, 3])

            # Add the mesh to the scene
            mesh = bpy.data.meshes.new(name="GMesh_lod"+str(i))
            mesh.from_pydata(vertices, [], list(faces))
            obj = object_data_add(context, mesh)
            for k in mesh.polygons:
                k.use_smooth = True
            
            # Normals
            #bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            #bpy.ops.mesh.normals_make_consistent(inside=False)
            #bpy.ops.object.mode_set(mode='OBJECT')
            mesh.normals_split_custom_set_from_vertices(normals)
            mesh.use_auto_smooth = True
            #Tangents are read-only in Blender, we can't import them

            # UVmaps creation
            for k in range(len(allUVMaps)):
                uvmap_name = getWords(k+1)+'UV'
                uvmap = mesh.attributes.new(uvmap_name, 'FLOAT2', 'CORNER')
                uv_array = allUVMaps[k]
                uv_array = np.array([uv_array[vert] for vert in np.array([list(zip(face.vertices, face.loop_indices)) for face in mesh.polygons]).reshape((-1,2)).flatten()[::2]]).flatten()
                uvmap.data.foreach_set("vector", uv_array)
                        
            # Vertex Color
            if 'vertexColor' in locals():
                v_col = mesh.color_attributes.new(name = 'Color', domain = 'POINT', type = 'BYTE_COLOR')
                v_col.data.foreach_set("color", vertexColor)
                del(vertexColor)
            
            # Clothing Paints
            n_data_array = len(mesh.vertices)
            magenta_array = np.full((n_data_array,4), [1,0,1,1]).flatten()
            white_array = np.full((n_data_array,4), [1,1,1,1]).flatten()
            green_array = np.full((n_data_array,4), [0,1,0,1]).flatten()
            for k in ["MaximumDistance", "BackstopRadius", "BackstopDistance", "Drive1", "Latch1"]:
                v_col = mesh.color_attributes.new(name = k, domain = 'POINT', type = 'BYTE_COLOR')
                if k == "Drive1":
                    v_col.data.foreach_set("color", white_array)
                elif k == "Latch1":
                    v_col.data.foreach_set("color", magenta_array)
                else:
                    v_col.data.foreach_set("color", green_array)
                    
            # Material
            if materialNames[j] in bpy.data.materials:
                mesh.materials.append(bpy.data.materials[materialNames[j]])
            else:
                temp_mat = bpy.data.materials.new(materialNames[j])
                mesh.materials.append(temp_mat)
                temp_mat.diffuse_color = (*colorsys.hsv_to_rgb(random.random(), .7, .9), 1)

            # Rotation of the mesh if requested
            if rotate_180:
                obj.rotation_euler[2] = np.pi
                
            # Get the actual mesh in a list
            meshes.append(obj)
            
            #Parenting
            obj.select_set(state=True)
            bpy.context.view_layer.objects.active = arma
            bpy.ops.object.parent_set(type="ARMATURE_NAME", xmirror=False, keep_transform=False)
            bpy.context.view_layer.objects.active = None
            bpy.ops.object.select_all(action='DESELECT')
            
            # Bone Weighting
            for k, (indices, weights) in enumerate(zip(boneIndices, boneWeights)):
                for l in range(4):
                    weight = weights[l]
                    if weight:
                        obj.vertex_groups[boneNames[indices[l]]].add([k], weight, 'REPLACE')

        # Join submeshes under the same lod
        JoinThem(meshes)
        finalMeshes.append(bpy.context.active_object)
    
    # Physical Meshes
    PhysicalMeshes = find_elem(ClothingAssetParameters, "array", "name", "physicalMeshes")
    numPhysicalMeshes = int(PhysicalMeshes.attrib["size"])
    assert(len(PhysicalMeshes) == numPhysicalMeshes)
    assert(len(finalMeshes) == numPhysicalMeshes)
    physicalMeshes_boneIndices_all = []
    physicalMeshes_boneWeights_all = []
    for i, graph_mesh in enumerate(finalMeshes):
        PhysicalMesh = PhysicalMeshes[i][0][0] #extra [0][0] to index into <struct name="physicalMesh">
        numVertices = int(find_elem(PhysicalMesh, "value", "name", "numVertices").text)
        numFaces = int(find_elem(PhysicalMesh, "value", "name", "numIndices").text)/3
        numBonesPerVertex = int(find_elem(PhysicalMesh, "value", "name", "numBonesPerVertex").text)
        vertices_text = find_elem(PhysicalMesh, "array", "name", "vertices").text
        vertices = to_array(vertices_text, float, [-1, 3])
        assert (len(vertices) == numVertices)
        normals_text = find_elem(PhysicalMesh, "array", "name", "normals").text
        normals = to_array(normals_text, float, [-1, 3])
        assert (len(normals) == numVertices)
        skinningNormals_text = find_elem(PhysicalMesh, "array", "name", "skinningNormals").text
        skinningNormals = to_array(skinningNormals_text, float, [-1, 3])
        assert (len(skinningNormals) == numVertices)
        constrainCoefficients_text = find_elem(PhysicalMesh, "array", "name", "constrainCoefficients").text
        constrainCoefficients = to_array(constrainCoefficients_text, float, [-1, 3])
        assert (len(constrainCoefficients) == numVertices)
        boneIndices_text = find_elem(PhysicalMesh, "array", "name", "boneIndices").text
        boneIndices = to_array(boneIndices_text, int, [-1, numBonesPerVertex])
        assert (len(boneIndices) == numVertices)
        boneWeights_text = find_elem(PhysicalMesh, "array", "name", "boneWeights").text
        boneWeights = to_array(boneWeights_text, float, [-1, numBonesPerVertex])
        assert (len(boneWeights) == numVertices)
        faces_text = find_elem(PhysicalMesh, "array", "name", "indices").text
        faces = to_array(faces_text, int, [-1, 3])
        assert (len(faces) == numFaces)
        maximumMaxDistance = float(find_elem(PhysicalMesh, "value", "name", "maximumMaxDistance").text)
            
        # Add the mesh to the scene
        mesh = bpy.data.meshes.new(name="PMesh_lod"+str(i))
        mesh.from_pydata(vertices, [], list(faces))
        obj = object_data_add(context, mesh)
        for j in mesh.polygons:
            j.use_smooth = True
        
        # Normals
        #bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        #bpy.ops.mesh.normals_make_consistent(inside=False)
        #bpy.ops.object.mode_set(mode='OBJECT')
        mesh.normals_split_custom_set_from_vertices(normals)
        mesh.use_auto_smooth = True
        #Tangents are read-only in Blender, we can't import them
                
        # Clothing Paints
        array_ones = np.ones(len(constrainCoefficients))
        constrainCoefficients = constrainCoefficients.T
        #Scale Maximum Distance Paint
        if maximumMaxDistance:
            constrainCoefficients[0] = constrainCoefficients[0]/maximumMaxDistance
        for k, col_name in enumerate(["MaximumDistance", "BackstopRadius", "BackstopDistance"]):
            data_array = np.c_[np.repeat(constrainCoefficients[k],3).reshape((-1,3)), array_ones]
            data_array[data_array[:,0] == 0] = [1,0,1,1]
            v_col = mesh.color_attributes.new(name = col_name, domain = 'POINT', type = 'BYTE_COLOR')
            v_col.data.foreach_set("color", data_array.flatten())
                
        # Rotation of the mesh if requested
        if rotate_180:
            obj.rotation_euler[2] = np.pi
        
        #Parenting
        obj.select_set(state=True)
        bpy.context.view_layer.objects.active = arma
        bpy.ops.object.parent_set(type="ARMATURE_NAME", xmirror=False, keep_transform=False)
        bpy.context.view_layer.objects.active = None
        bpy.ops.object.select_all(action='DESELECT')
        # Bone Weighting
        for k, (indices, weights) in enumerate(zip(boneIndices, boneWeights)):
            for l in range(4):
                weight = weights[l]
                if weight:
                    obj.vertex_groups[boneNames[indices[l]]].add([k], weight, 'REPLACE')
            
        # Copy vertex color data to Graphical Meshes
        bpy.context.view_layer.objects.active = graph_mesh
        paintModifier = graph_mesh.modifiers.new(type='DATA_TRANSFER', name = "ClothingPaintTransfer")
        paintModifier.object = obj
        paintModifier.use_vert_data = True
        paintModifier.data_types_verts = {'COLOR_VERTEX'}
        paintModifier.vert_mapping = 'NEAREST'
        paintModifier.use_max_distance = True
        paintModifier.max_distance = 0.000001
        bpy.ops.object.modifier_apply(modifier = paintModifier.name)
                        
        # Delete physical mesh if requested
        if rm_ph_me:
            bpy.data.objects.remove(obj)
        
        # Interpret Drive/Latch
        mesh = graph_mesh.data
        empty_array = np.zeros(len(mesh.vertices)*4)
        for k in ["MaximumDistance", "BackstopRadius", "BackstopDistance", "Drive1", "Latch1"]:
            data_array = empty_array
            mesh.color_attributes[k].data.foreach_get("color", data_array)
            data_array = data_array.reshape((-1,4))
            if k == "MaximumDistance":
                check_array = data_array[:,0] < data_array[:,1]
            if k == "Latch1":
                data_array[check_array] = [1,1,1,1]  
            else:
                data_array[check_array] = [1,0,1,1]
            mesh.color_attributes[k].data.foreach_set("color", data_array.flatten())
    
    # Collision Capsules
    boneActors_text = find_elem(ClothingAssetParameters, "array", "name", "boneActors").text
    if boneActors_text:
        boneActors = to_array(boneActors_text, float, [-1, 17])
        for b_capsule in boneActors:
            bpy.context.view_layer.objects.active = arma
            skeleton.bones.active = skeleton.bones[boneNames[int(b_capsule[0])]]
            boneCapsuleRadius = b_capsule[3]
            boneCapsuleHeight = b_capsule[4]
            boneCapsuleMatrix = Matrix(np.array(b_capsule[5:]).reshape([-1, 4, 3]).T).to_4x4()
            matrix_world = skeleton.bones.active.matrix_local @ boneCapsuleMatrix
            coordinates_world = matrix_world.translation
            boneCapsuleRotation = matrix_world.to_euler()
            add_capsule(context = bpy.context, radius = boneCapsuleRadius, height = boneCapsuleHeight, location = coordinates_world, rotation = boneCapsuleRotation, use_location = True)
    
    # Collision Sphere       
    boneSpheres_text = find_elem(ClothingAssetParameters, "array", "name", "boneSpheres").text
    if boneSpheres_text:
        boneSpheres = to_array(boneSpheres_text, float, [-1, 5])
        sphere_objs = []
        for b_sphere in boneSpheres: 
            bpy.context.view_layer.objects.active = arma
            skeleton.bones.active = skeleton.bones[boneNames[int(b_sphere[0])]]
            coordinates_world = skeleton.bones.active.matrix_local @ Vector(b_sphere[2:5])
            boneSphereRadius = b_sphere[1]
            sphere_objs.append(add_sphere(bpy.context, boneSphereRadius, coordinates_world, True))
            
    # Collision Sphere Connections 
    boneCapsuleIndices_text = find_elem(ClothingAssetParameters, "array", "name", "boneSphereConnections").text
    if boneCapsuleIndices_text:
        boneCapsuleIndices = to_array(boneCapsuleIndices_text, int, [-1, 2])
        for a, b in boneCapsuleIndices:
            sphere_a = sphere_objs[a]
            sphere_b = sphere_objs[b]
            selectOnly(sphere_a)
            bpy.context.view_layer.objects.active = sphere_b
            sphere_b.select_set(state=True)
            add_connection(context = bpy.context)