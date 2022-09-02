# -*- coding: utf-8 -*-
# importer/import_clothing.py

import bpy
import random, colorsys
import xml.etree.ElementTree as ET
import numpy as np
from bpy_extras.object_utils import object_data_add
from mathutils import Vector, Matrix
from io_scene_apx import number_to_words
from io_scene_apx.number_to_words import getWords
from io_scene_apx.importer import import_hairworks
from io_scene_apx.importer.import_hairworks import find_elem, to_array, JoinThem

def read_clothing(context, filepath, rm_db, use_mat, rotate_180, rm_ph_me):

    root = ET.parse(filepath).getroot() #NxParameters element
    ClothingAssetParameters = find_elem(root, "value", "className", "ClothingAssetParameters")[0] #extra [0] to index into <struct>
    
    # Armature and Bones
    Armature = find_elem(ClothingAssetParameters, "array", "name", "bones")
    numBones = int(Armature.attrib["size"])
    assert(len(Armature) == numBones)
    armaNames = []
    boneNames = []
    boneParents = []
    for i in range(numBones):
        boneParent = int(find_elem(Armature[i], "value", "name", "parentIndex").text)
        boneParents.append(boneParent)
        bindPose_text = find_elem(Armature[i], "value", "name", "bindPose").text
        bindPose = to_array(bindPose_text, float, [-1, 4, 3])
        boneName = find_elem(Armature[i], "value", "name", "name").text
        boneNames.append(boneName)
        bpy.context.view_layer.objects.active = None
        bpy.ops.object.select_all(action='DESELECT')
        skeleton = bpy.data.armatures.new(name="Armature")
        object_data_add(context, skeleton)
        armaNames.append(bpy.context.active_object.name)
        # Edit mode required to add bones to the armature
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        b = skeleton.edit_bones.new(boneName)
        b.head = Vector((0,0,0))
        b.tail = Vector((0,1,0))
        bpy.ops.object.mode_set(mode='OBJECT')
        #Transform the armature to have the correct transformation, edit_bone.transform() gives wrong results
        skeleton.transform(Matrix(bindPose.T).to_4x4())
        
    # Join the armatures made for each bone together
    JoinThem(armaNames)
    arma = bpy.context.active_object   
    
    # Parenting Bones
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    for i in range(len(arma.data.edit_bones)):
        if boneParents[i] != -1:
            arma.data.edit_bones[i].parent = arma.data.edit_bones[boneNames[boneParents[i]]]
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Rotation of the armature
    if rotate_180:
        arma.rotation_euler[2] = np.pi
    
    # Graphical Meshes
    GraphicalLods = find_elem(ClothingAssetParameters, "array", "name", "graphicalLods")
    numGraphicalLods = int(GraphicalLods.attrib["size"])
    assert(len(GraphicalLods) == numGraphicalLods)
    finalMeshes_names = []
    for i in range(numGraphicalLods):
        GraphicalLod = GraphicalLods[i][0] #extra [0] to index into <struct>
        GraphicalMesh = find_elem(GraphicalLod, "value", "name", "renderMeshAsset")[0] #extra [0] to index into <struct>
        # Materials
        materials = find_elem(GraphicalMesh, "array", "name", "materialNames")
        materialNames = []
        for j in range(len(materials)):
            materialName = materials[j].text
            materialNames.append(materialName[materialName.find("::")+2:])
        SubMeshes = find_elem(GraphicalMesh, "array", "name", "submeshes")
        numSubMeshes = int(SubMeshes.attrib["size"])
        assert (len(SubMeshes) == numSubMeshes)
        assert(len(materials) == numSubMeshes)
        mesh_names = []
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
                    vertexColor = to_array(vertexColor_text, int, [-1, 4])
                    assert (len(vertexColor) == numVertices)
            faces_text = find_elem(SubMeshes[j][0], "array", "name", "indexBuffer").text
            faces = to_array(faces_text, int, [-1, 3])

            # Add the mesh to the scene
            mesh = bpy.data.meshes.new(name="GMesh_lod"+str(i))
            mesh.from_pydata(vertices, [], list(faces))
            for k in mesh.polygons:
                k.use_smooth = True
            object_data_add(context, mesh)
            
            #Normals
            #bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            #bpy.ops.mesh.normals_make_consistent(inside=False)
            #bpy.ops.object.mode_set(mode='OBJECT')
            mesh.normals_split_custom_set_from_vertices(normals)
            mesh.use_auto_smooth = True
            #Tangents are read-only in Blender, we can't import them

            # UVmaps creation
            uvmap_names = []
            for k in range(len(allUVMaps)):
                uvmap_names.append(getWords(k+1)+'UV')
            for k in range(len(uvmap_names)):
                mesh.uv_layers.new(name=uvmap_names[k])
                for face in mesh.polygons:
                    for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                        mesh.uv_layers[uvmap_names[k]].data[loop_idx].uv = allUVMaps[k][vert_idx]
                        
            # Vertex Color
            if 'vertexColor' in locals():
                mesh.vertex_colors.new()
                for face in mesh.polygons:
                    for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                        mesh.vertex_colors.active.data[loop_idx].color = vertexColor[vert_idx]
                del(vertexColor)
            
            #Clothing Paints
            mesh.vertex_colors.new(name="MaximumDistance")
            mesh.vertex_colors.new(name="BackstopRadius")
            mesh.vertex_colors.new(name="BackstopDistance")
            mesh.vertex_colors.new(name="Drive")
            mesh.vertex_colors.new(name="Latch")
            for face in mesh.polygons:
                for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                        mesh.vertex_colors["MaximumDistance"].data[loop_idx].color = [0,1,0,1]
                        mesh.vertex_colors["BackstopRadius"].data[loop_idx].color = [0,1,0,1]
                        mesh.vertex_colors["BackstopDistance"].data[loop_idx].color = [0,1,0,1]
                        mesh.vertex_colors["Drive"].data[loop_idx].color = [1,1,1,1]
                        mesh.vertex_colors["Latch"].data[loop_idx].color = [1,0,1,1]
                    
            # Material
            if use_mat == True and materialNames[j] in bpy.data.materials:
                mesh.materials.append(bpy.data.materials[materialNames[j]])
            else:
                temp_mat = bpy.data.materials.new(materialNames[j])
                mesh.materials.append(temp_mat)
                temp_mat.diffuse_color = (*colorsys.hsv_to_rgb(random.random(), .7, .9), 1)

            # Rotation of the mesh if requested
            if rotate_180:
                bpy.context.active_object.rotation_euler[2] = np.pi
                
            # Get the actual mesh name in a list
            mesh_names.append(bpy.context.active_object.name)
            
            #Parenting
            bpy.context.active_object.select_set(state=True)
            bpy.context.view_layer.objects.active = bpy.data.objects[arma.name]
            bpy.ops.object.parent_set(type="ARMATURE_NAME", xmirror=False, keep_transform=False)
            bpy.context.view_layer.objects.active = None
            bpy.ops.object.select_all(action='DESELECT')
            # Bone Weighting
            bpy.context.view_layer.objects.active = bpy.data.objects[mesh_names[-1]]
            for k, (indices, weights) in enumerate(zip(boneIndices, boneWeights)):
                for l in range(4):
                    if weights[l] != 0:
                        bpy.context.active_object.vertex_groups[boneNames[indices[l]]].add([k], weights[l], 'REPLACE')

        # Join submeshes under the same lod
        JoinThem(mesh_names)
        finalMeshes_names.append(bpy.context.active_object.name)
        # Remove doubles if requested
        if rm_db:
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            bpy.ops.mesh.remove_doubles()
            bpy.ops.object.mode_set(mode='OBJECT')
    
    # Physical Meshes
    PhysicalMeshes = find_elem(ClothingAssetParameters, "array", "name", "physicalMeshes")
    numPhysicalMeshes = int(PhysicalMeshes.attrib["size"])
    assert(len(PhysicalMeshes) == numPhysicalMeshes)
    physicalMeshes_names = []
    physicalMeshes_boneIndices_all = []
    physicalMeshes_boneWeights_all = []
    for i in range(numPhysicalMeshes):
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
            
        # Scale Maximum Distance Paint
        for j in range(len(constrainCoefficients)):
            if maximumMaxDistance > 0:
                constrainCoefficients[j][0] = constrainCoefficients[j][0]/maximumMaxDistance
            
        # Add the mesh to the scene
        mesh = bpy.data.meshes.new(name="PMesh_lod"+str(i))
        mesh.from_pydata(vertices, [], list(faces))
        for j in mesh.polygons:
            j.use_smooth = True
        object_data_add(context, mesh)
        
        #Normals
        #bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        #bpy.ops.mesh.normals_make_consistent(inside=False)
        #bpy.ops.object.mode_set(mode='OBJECT')
        mesh.normals_split_custom_set_from_vertices(normals)
        mesh.use_auto_smooth = True
        #Tangents are read-only in Blender, we can't import them
                
        # Apply Clothing Paints
        mesh.vertex_colors.new(name="MaximumDistance")
        mesh.vertex_colors.new(name="BackstopRadius")
        mesh.vertex_colors.new(name="BackstopDistance")
        for face in mesh.polygons:
            for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                if constrainCoefficients[vert_idx][0] == 0:
                    mesh.vertex_colors["MaximumDistance"].data[loop_idx].color = [1,0,1,1]
                else:
                    mesh.vertex_colors["MaximumDistance"].data[loop_idx].color = [constrainCoefficients[vert_idx][0]]*3+[1]
                if constrainCoefficients[vert_idx][1] == 0:
                    mesh.vertex_colors["BackstopRadius"].data[loop_idx].color = [1,0,1,1]
                else:
                    mesh.vertex_colors["BackstopRadius"].data[loop_idx].color = [constrainCoefficients[vert_idx][1]]*3+[1]
                if constrainCoefficients[vert_idx][2] == 0:
                    mesh.vertex_colors["BackstopDistance"].data[loop_idx].color = [1,0,1,1]
                else:
                    mesh.vertex_colors["BackstopDistance"].data[loop_idx].color = [constrainCoefficients[vert_idx][2]]*3+[1]
                
        # Rotation of the mesh if requested
        if rotate_180:
            bpy.context.active_object.rotation_euler[2] = np.pi
            
        # Get the actual mesh name in a list
        physicalMeshes_names.append(bpy.context.active_object.name)
        
        #Parenting
        bpy.context.active_object.select_set(state=True)
        bpy.context.view_layer.objects.active = bpy.data.objects[arma.name]
        bpy.ops.object.parent_set(type="ARMATURE_NAME", xmirror=False, keep_transform=False)
        bpy.context.view_layer.objects.active = None
        bpy.ops.object.select_all(action='DESELECT')
        # Bone Weighting
        bpy.context.view_layer.objects.active = bpy.data.objects[physicalMeshes_names[-1]]
        for k, (indices, weights) in enumerate(zip(boneIndices, boneWeights)):
            for l in range(4):
                if weights[l] != 0:
                    bpy.context.active_object.vertex_groups[boneNames[indices[l]]].add([k], weights[l], 'REPLACE')
            
        # Copy vertex color data to Graphical Meshes
        bpy.context.view_layer.objects.active = bpy.data.objects[finalMeshes_names[i]]
        bpy.context.active_object.modifiers.new(type='DATA_TRANSFER', name = "ClothingPaintTransfer")
        paintModifier = bpy.context.active_object.modifiers[-1]
        paintModifier.object = bpy.data.objects[physicalMeshes_names[-1]]
        paintModifier.use_loop_data = True
        paintModifier.data_types_loops = {'VCOL'}
        paintModifier.loop_mapping = 'NEAREST_POLYNOR'
        paintModifier.use_max_distance = True
        paintModifier.max_distance = 0.000001
        bpy.ops.object.modifier_apply(modifier = paintModifier.name)
                        
        # Delete physical mesh if requested
        if rm_ph_me:
            bpy.context.view_layer.objects.active = None
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = bpy.data.objects[physicalMeshes_names[-1]]
            bpy.context.active_object.select_set(state=True)
            bpy.ops.object.delete()
            bpy.context.view_layer.objects.active = None
            bpy.ops.object.select_all(action='DESELECT')
        
    # Interpret Drive/Latch
    for i in range(len(finalMeshes_names)):
        me = bpy.data.objects[finalMeshes_names[i]].data
        for face in me.polygons:
            for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                if me.vertex_colors["MaximumDistance"].data[loop_idx].color[1] > me.vertex_colors["MaximumDistance"].data[loop_idx].color[0]:
                    me.vertex_colors["Latch"].data[loop_idx].color = [1,1,1,1]
                    me.vertex_colors["Drive"].data[loop_idx].color = [1,0,1,1]
                    me.vertex_colors["MaximumDistance"].data[loop_idx].color = [1,0,1,1]
                    me.vertex_colors["BackstopRadius"].data[loop_idx].color = [1,0,1,1]
                    me.vertex_colors["BackstopDistance"].data[loop_idx].color = [1,0,1,1]
                else:
                    me.vertex_colors["Drive"].data[loop_idx].color = [1,1,1,1]
                    me.vertex_colors["Latch"].data[loop_idx].color = [1,0,1,1]
    
    # Collision Capsules
    boneActors_text = find_elem(ClothingAssetParameters, "array", "name", "boneActors").text
    if boneActors_text:
        boneActors = to_array(boneActors_text, float, [-1, 17])
        for b_capsule in boneActors:
            bone_name = boneNames[int(b_capsule[0])]
            bpy.context.view_layer.objects.active = arma
            arma.data.bones.active = arma.data.bones[bone_name]
            boneCapsuleRadius = b_capsule[3]
            boneCapsuleHeight = b_capsule[4]
            boneCapsuleMatrix = Matrix(np.array(b_capsule[5:]).reshape([-1, 4, 3]).T).to_4x4()
            matrix_world = bpy.context.active_bone.matrix_local @ boneCapsuleMatrix
            coordinates_world = matrix_world.translation
            boneCapsuleRotation = matrix_world.to_euler()
            bpy.ops.physx.add_collision_capsule(radius = boneCapsuleRadius, height = boneCapsuleHeight, location = coordinates_world, rotation = boneCapsuleRotation, use_location = True)
    
    # Collision Sphere       
    boneSpheres_text = find_elem(ClothingAssetParameters, "array", "name", "boneSpheres").text
    if boneSpheres_text:
        boneSpheres = to_array(boneSpheres_text, float, [-1, 5])
        sphere_names = []
        for b_sphere in boneSpheres:
            bone_name = boneNames[int(b_sphere[0])]
            bpy.context.view_layer.objects.active = arma
            arma.data.bones.active = arma.data.bones[bone_name]
            coordinates_world = bpy.context.active_bone.matrix_local @ Vector(b_sphere[2:5])
            boneSphereRadius = b_sphere[1]
            bpy.ops.physx.add_collision_sphere(radius = boneSphereRadius, location = coordinates_world, use_location = True)
            sphere_names.append(bpy.context.active_object.name)
            
    # Collision Sphere Connections 
    boneCapsuleIndices_text = find_elem(ClothingAssetParameters, "array", "name", "boneSphereConnections").text
    if boneCapsuleIndices_text:
        boneCapsuleIndices = to_array(boneCapsuleIndices_text, int, [-1, 2])
        for a, b in boneCapsuleIndices:
            bpy.context.view_layer.objects.active = None
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = bpy.data.objects[sphere_names[a]]
            bpy.context.active_object.select_set(state=True)
            bpy.context.view_layer.objects.active = bpy.data.objects[sphere_names[b]]
            bpy.context.active_object.select_set(state=True)
            bpy.ops.physx.add_sphere_connection()