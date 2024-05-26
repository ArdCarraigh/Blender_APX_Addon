# -*- coding: utf-8 -*-
# importer/import_clothing.py

import bpy
import random, colorsys
import xml.etree.ElementTree as ET
import numpy as np
import os.path
from bpy_extras.object_utils import object_data_add
from mathutils import Vector, Matrix
from io_mesh_apx.number_to_words import getWords
from io_mesh_apx.tools.collision_tools import *
from io_mesh_apx.utils import find_elem, to_array, JoinThem, selectOnly, simValueType, SetAttributes, SetUpWind, SetUpDrag
from io_mesh_apx.tools.setup_tools import SetUpClothMaterial

def read_clothing(context, filepath, rotate_180, rm_ph_me):
    # Create Main Collection
    file_name = os.path.splitext(os.path.basename(filepath))[0]
    parent_coll = bpy.context.view_layer.active_layer_collection
    main_coll = bpy.data.collections.new(file_name)
    main_coll["PhysXAssetType"] = "Clothing"
    parent_coll.collection.children.link(main_coll)
    bpy.context.view_layer.active_layer_collection = parent_coll.children[main_coll.name]
    
    # Set Up Wind
    SetUpWind()
    SetUpDrag()

    # Parse File
    root = ET.parse(filepath).getroot() #NxParameters element
    ClothingAssetParameters = find_elem(root, "value", "className", "ClothingAssetParameters")[0] #extra [0] to index into <struct>
    
    # Simulation Materials
    sim_mats = []
    sim_mats_xml = find_elem(ClothingAssetParameters, "value", "name", "materialLibrary")[0][0] #extra [0][0] to index into <array name="materials">
    for mat in sim_mats_xml:
        sim_mat = {}
        for elem in mat[1:]:
            name = elem.attrib["name"]
            if name == "zeroStretchStiffness":
                pass
            elif name in ["verticalStiffnessScaling", "horizontalStiffnessScaling", "bendingStiffnessScaling", "shearingStiffnessScaling"]:
                for elem2 in elem:
                    func_type = simValueType(elem2.attrib["type"])
                    sim_mat[name + "_" + elem2.attrib["name"]] = func_type(elem2.text)
            else:
                func_type = simValueType(elem.attrib["type"])
                sim_mat[elem.attrib["name"]] = func_type(elem.text)
        sim_mats.append(sim_mat)
    
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
                #elif bufferFormats[k] == 'SEMANTIC_TANGENT':
                #    tangents_text = find_elem(buffer, "array", "name", "data").text
                #    tangents = to_array(tangents_text, float, [-1, 4])
                #    assert (len(tangents) == numVertices)
                elif 'SEMANTIC_TEXCOORD' in bufferFormats[k]:
                    uvs_text = find_elem(buffer, "array", "name", "data").text
                    uvs = to_array(uvs_text, float, [-1, 2])
                    assert (len(uvs) == numVertices)
                    allUVMaps.append(uvs)
                elif bufferFormats[k] == 'SEMANTIC_BONE_INDEX':
                    boneIndices_text = find_elem(buffer, "array", "name", "data").text
                    numBonesPerVertex = np.array([int(x) for x in boneIndices_text[:boneIndices_text.find(",")].split()]).size
                    boneIndices = to_array(boneIndices_text, int, [-1, numBonesPerVertex])
                    assert (len(boneIndices) == numVertices)
                elif bufferFormats[k] == 'SEMANTIC_BONE_WEIGHT':
                    boneWeights_text = find_elem(buffer, "array", "name", "data").text
                    boneWeights = to_array(boneWeights_text, float, [-1, numBonesPerVertex])
                    assert (len(boneWeights) == numVertices)
                elif bufferFormats[k] == 'SEMANTIC_COLOR':
                    vertexColor_text = find_elem(buffer, "array", "name", "data").text
                    vertexColor = to_array(vertexColor_text, float, [-1]) / 255
                    assert (len(vertexColor) == numVertices*4)
            faces_text = find_elem(SubMeshes[j][0], "array", "name", "indexBuffer").text
            faces = to_array(faces_text, int, [-1, 3])

            # Add the mesh to the scene
            mesh = bpy.data.meshes.new(name="GMesh_lod"+str(i))
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
                        
            # Vertex Color
            if 'vertexColor' in locals():
                v_col = mesh.color_attributes.new(name = 'Color', domain = 'POINT', type = 'BYTE_COLOR')
                v_col.data.foreach_set("color", vertexColor)
                del(vertexColor)
                    
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
                for l in range(numBonesPerVertex):
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
        mesh.shade_smooth()
        
        # Normals
        mesh.normals_split_custom_set_from_vertices(normals)
        #Tangents are read-only in Blender, we can't import them
                
        # Clothing Paints
        n_verts = len(constrainCoefficients)
        constrainCoefficients = constrainCoefficients.T
        #Scale Maximum Distance Paint
        if maximumMaxDistance:
            constrainCoefficients[0] = constrainCoefficients[0]/maximumMaxDistance
        max_dist_group = obj.vertex_groups.new(name="PhysXMaximumDistance")
        back_rad_group = obj.vertex_groups.new(name="PhysXBackstopRadius")
        back_dist_group = obj.vertex_groups.new(name="PhysXBackstopDistance")
        for k in range(n_verts):
            max_dist_group.add([k], constrainCoefficients[0][k], 'REPLACE')
            back_rad_group.add([k], constrainCoefficients[1][k], 'REPLACE')
            back_dist_group.add([k], constrainCoefficients[2][k], 'REPLACE')
                
        # Rotation of the mesh if requested
        if rotate_180:
            obj.rotation_euler[2] = np.pi
        
        ## Parenting # Not needed for Physical Mesh
        #obj.select_set(state=True)
        #bpy.context.view_layer.objects.active = arma
        #bpy.ops.object.parent_set(type="ARMATURE_NAME", xmirror=False, keep_transform=False)
        #bpy.context.view_layer.objects.active = None
        #bpy.ops.object.select_all(action='DESELECT')
        ## Bone Weighting
        #for k, (indices, weights) in enumerate(zip(boneIndices, boneWeights)):
        #    for l in range(numBonesPerVertex):
        #        weight = weights[l]
        #        if weight:
        #            obj.vertex_groups[boneNames[indices[l]]].add([k], weight, 'REPLACE')
            
        # Copy vertex groups data to Graphical Meshes
        graph_mesh.vertex_groups.new(name="SimplyPin")
        graph_mesh.vertex_groups.new(name="PhysXMaximumDistance")
        graph_mesh.vertex_groups.new(name="PhysXBackstopRadius")
        graph_mesh.vertex_groups.new(name="PhysXBackstopDistance")
        graph_mesh.vertex_groups.new(name="PhysXDrive1")
        graph_mesh.vertex_groups.new(name="PhysXLatch1")
        bpy.context.view_layer.objects.active = graph_mesh
        paintModifier = graph_mesh.modifiers.new(type='DATA_TRANSFER', name = "ClothingPaintTransfer")
        paintModifier.object = obj
        paintModifier.use_vert_data = True
        paintModifier.data_types_verts = {'VGROUP_WEIGHTS'}
        paintModifier.vert_mapping = 'NEAREST'
        paintModifier.use_max_distance = True
        paintModifier.max_distance = 0.000001
        paintModifier.layers_vgroup_select_src = 'ALL'
        paintModifier.layers_vgroup_select_dst = 'NAME'
        bpy.ops.object.modifier_apply(modifier = paintModifier.name)
                        
        # Delete physical mesh if requested
        if rm_ph_me:
            bpy.data.objects.remove(obj)
        
        # Interpret Drive/Latch
        for k, vert in enumerate(graph_mesh.data.vertices):
            existing_layers = [graph_mesh.vertex_groups[g.group].name for g in vert.groups]
            if "PhysXMaximumDistance" in existing_layers:
                graph_mesh.vertex_groups["PhysXDrive1"].add([k], 1, 'REPLACE')
                graph_mesh.vertex_groups["PhysXLatch1"].add([k], 0, 'REPLACE')
            else:
                graph_mesh.vertex_groups["PhysXDrive1"].add([k], 0, 'REPLACE')
                graph_mesh.vertex_groups["PhysXLatch1"].add([k], 1, 'REPLACE')
                
        # Setup Cloth Material
        SetUpClothMaterial(graph_mesh, main_coll, maximumMaxDistance, sim_mats[i])
        
    # Setup Cloth Simulation
    sim_xml = find_elem(ClothingAssetParameters, "struct", "name", "simulation")
    sim = {}
    for elem in sim_xml:
        func_type = simValueType(elem.attrib["type"])
        sim[elem.attrib["name"]] = func_type(elem.text)
    SetAttributes(bpy.context.window_manager.physx.cloth, sim)
        
    # Collision Capsules
    boneActors_text = find_elem(ClothingAssetParameters, "array", "name", "boneActors").text
    if boneActors_text:
        boneActors = to_array(boneActors_text, float, [-1, 17])
        for b_capsule in boneActors:
            boneName = boneNames[int(b_capsule[0])]
            boneCapsuleMatrix = Matrix(np.array(b_capsule[5:]).reshape([-1, 4, 3]).T).to_4x4()
            matrix_world = skeleton.bones[boneName].matrix_local @ boneCapsuleMatrix
            add_capsule(bpy.context, boneName, b_capsule[3], b_capsule[4], matrix_world.translation, matrix_world.to_euler(), True)
    
    # Collision Sphere       
    boneSpheres_text = find_elem(ClothingAssetParameters, "array", "name", "boneSpheres").text
    if boneSpheres_text:
        boneSpheres = to_array(boneSpheres_text, float, [-1, 5])
        sphere_objs = []
        for b_sphere in boneSpheres:
            boneName = boneNames[int(b_sphere[0])]
            coordinates_world = skeleton.bones[boneName].matrix_local @ Vector(b_sphere[2:5])
            sphere_objs.append(add_sphere(bpy.context, boneName, b_sphere[1], coordinates_world, True))
            
    # Collision Sphere Connections 
    boneCapsuleIndices_text = find_elem(ClothingAssetParameters, "array", "name", "boneSphereConnections").text
    if boneCapsuleIndices_text:
        boneCapsuleIndices = to_array(boneCapsuleIndices_text, int, [-1, 2])
        for a, b in boneCapsuleIndices:
            add_connection(bpy.context, [sphere_objs[a], sphere_objs[b]])