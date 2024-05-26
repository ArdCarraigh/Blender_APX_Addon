# -*- coding: utf-8 -*-
# importer/import_destruction.py

import bpy
import random, colorsys
import xml.etree.ElementTree as ET
import numpy as np
import os.path
from bpy_extras.object_utils import object_data_add
from mathutils import Vector, Matrix
from io_mesh_apx.number_to_words import getWords
from io_mesh_apx.utils import find_elem, to_array, JoinThem, GetCollection, getWeightArray, selectOnly

def read_destruction(context, filepath, rotate_180):
    # Create Main Collection #
    file_name = os.path.splitext(os.path.basename(filepath))[0]
    parent_coll = bpy.context.view_layer.active_layer_collection
    main_coll = bpy.data.collections.new(file_name)
    main_coll["PhysXAssetType"] = "Destruction"
    parent_coll.collection.children.link(main_coll)
    bpy.context.view_layer.active_layer_collection = parent_coll.children[main_coll.name]

    # Parse File
    root = ET.parse(filepath).getroot() #NxParameters element
    DestructibleAssetParameters = find_elem(root, "value", "className", "DestructibleAssetParameters")[0] #extra [0] to index into <struct>
    
    # Graphical Meshes
    GraphicalMesh = find_elem(DestructibleAssetParameters, "value", "name", "renderMeshAsset")[0] #extra [0] to index into <struct>
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
        bufferNames = []
        bufferFormats = []
        for k in range(numSubMesh_BufferFormats):
            bufferNames.append(find_elem(SubMesh_BufferFormats[k], "value", "name", "name").text)
            bufferFormats.append(find_elem(SubMesh_BufferFormats[k], "value", "name", "format").text)
        SubMesh_Buffers = find_elem(SubMesh, "array", "name", "buffers")
        numSubMesh_Buffers = int(SubMesh_Buffers.attrib["size"])
        assert (len(SubMesh_Buffers) == numSubMesh_Buffers)
        assert (numSubMesh_BufferFormats == numSubMesh_Buffers)
        allUVMaps = []
        for k in range(numSubMesh_Buffers):
            buffer = SubMesh_Buffers[k][0]
            if bufferNames[k] == 'SEMANTIC_POSITION':
                vertices_text = find_elem(buffer, "array", "name", "data").text
                vertices = to_array(vertices_text, float, [-1, 3])
                assert (len(vertices) == numVertices)
            elif bufferNames[k] == 'SEMANTIC_NORMAL':
                normals_text = find_elem(buffer, "array", "name", "data").text
                normals = to_array(normals_text, float, [-1, 3])
                assert (len(normals) == numVertices)
                if bufferFormats[k] == "31":
                    normals = normals / 127
                    normals[normals > 1] -= 2 
            #elif bufferNames[k] == 'SEMANTIC_TANGENT':
            #    tangents_text = find_elem(buffer, "array", "name", "data").text
            #    tangents = to_array(tangents_text, float, [-1, 3])
            #    assert (len(tangents) == numVertices)
            elif 'SEMANTIC_TEXCOORD' in bufferNames[k]:
                uvs_text = find_elem(buffer, "array", "name", "data").text
                uvs = to_array(uvs_text, float, [-1, 2])
                assert (len(uvs) == numVertices)
                allUVMaps.append(uvs)
            elif bufferNames[k] == 'SEMANTIC_BONE_INDEX':
                boneIndices_text = find_elem(buffer, "array", "name", "data").text
                boneIndices = to_array(boneIndices_text, int, [-1,])
                assert (len(boneIndices) == numVertices)
        faces_text = find_elem(SubMeshes[j][0], "array", "name", "indexBuffer").text
        faces = to_array(faces_text, int, [-1, 3])

        # Add the mesh to the scene
        mesh = bpy.data.meshes.new(name="GMesh")
        mesh.from_pydata(vertices, [], list(faces))
        obj = object_data_add(context, mesh)
        mesh.shade_smooth()
        
        # Normals
        #bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        #bpy.ops.mesh.normals_make_consistent(inside=False)
        #bpy.ops.object.mode_set(mode='OBJECT')
        mesh.normals_split_custom_set_from_vertices(normals)
        #Tangents are read-only in Blender, we can't import them

        # UVmaps creation
        corner_verts = mesh.attributes[".corner_vert"].data
        corner_verts_array = np.zeros(len(corner_verts), dtype = int)
        corner_verts.foreach_get("value", corner_verts_array)
        for k, uv in enumerate(allUVMaps):
            uvmap_name = getWords(k+1)+'UV'
            uvmap = mesh.attributes.new(uvmap_name, 'FLOAT2', 'CORNER')
            uv_array = uv[corner_verts_array].flatten()
            uvmap.data.foreach_set("vector", uv_array)
                
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
        
        # Bone Indexing
        chunk_groups = {}
        for chunk in set(boneIndices):
            chunk_groups[chunk] = obj.vertex_groups.new(name="Chunk"+str(chunk))
        for k, index in enumerate(boneIndices):
            chunk_groups[index].add([k], 1, 'REPLACE')
                    
    # Join submeshes under the same lod
    JoinThem(meshes)
    final_obj = bpy.context.active_object
    final_mesh = final_obj.data
    min_z = bpy.context.active_object.bound_box[0][2]
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Split by Vertex Group
    chunk_coll = GetCollection("Chunks", True)
    for i, vg in enumerate(final_obj.vertex_groups):
        selectOnly(final_obj)
        weight_array = getWeightArray(final_mesh.vertices, vg)
        bool_array = weight_array > 0
        select_set = final_mesh.attributes.new(".select_vert", "BOOLEAN", "POINT")
        select_set.data.foreach_set("value", bool_array)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.separate(type='SELECTED')
        bpy.ops.object.mode_set(mode='OBJECT')
        chunk_mesh = bpy.context.selected_objects[-1]
        if not i:
            chunk_mesh.name = "Base_Mesh"
        else:
            chunk_mesh.name = "Chunk"+str(i)
            chunk_coll.objects.link(chunk_mesh)
            for coll in chunk_mesh.users_collection:
                if coll != chunk_coll:
                    coll.objects.unlink(chunk_mesh)
            bpy.ops.rigidbody.objects_add(type='ACTIVE')
            rigid_body = chunk_mesh.rigid_body
            rigid_body.friction = 1
            rigid_body.use_deactivation = True
            rigid_body.use_start_deactivated = True
            
    bpy.data.objects.remove(final_obj)
            
    # Add a ground plane
    GetCollection()
    bpy.ops.mesh.primitive_plane_add(size = 20, enter_editmode=False, align='WORLD', location=(0, 0, min_z), scale=(1, 1, 1))
    plane = bpy.context.active_object
    bpy.ops.rigidbody.objects_add(type='PASSIVE')
    plane.rigid_body.friction = 1