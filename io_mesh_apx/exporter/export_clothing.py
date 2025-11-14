# -*- coding: utf-8 -*-
# exporter/export_clothing.py

import bpy
import re
import numpy as np
import os.path
from copy import deepcopy
from mathutils import Matrix, Vector
from io_mesh_apx.exporter.template_clothing import *
from io_mesh_apx.tools.paint_tools import cleanUpDriveLatchGroups, apply_drive
from io_mesh_apx.utils import JoinThem, GetLoopDataPerVertex, Get3Bits, selectOnly, applyTransforms, MakeKDTreeFromObject, getClosest, getVertexBary, SplitMesh, TriangulateActiveMesh, OrderVertices, GetCollection, GetArmature, getWeightArray, deleteIsolatedVertices
    
def write_clothing(context, filepath, apply_modifiers):
    kwargs = {}
    main_coll = GetCollection()
    assert(main_coll is not None)
    
    # Get transforms of the armature
    arma = GetArmature()
    armaScale = np.array(arma.scale)
    armaRot = np.array(arma.rotation_euler)
    armaLoc = np.array(arma.location)
    assert(arma.children is not None)
    
    #Get the meshes to export
    obvg = arma.children[0]
    if "lod0" not in obvg.name:
        objects = [obvg]
    else:
        objects = arma.children
    num_objects = len(objects)     
    kwargs['numPhysicalMeshes'] = num_objects
    kwargs['numGraphicalMeshes'] = kwargs['numPhysicalMeshes']
    
    # Armature
    boneIndex = {}
    bones = arma.data.bones
    boneNames = []
    numMeshReferenced = []
    numRigidBodiesReferenced = []
    for i, bone in enumerate(bones):
        bone_name = bone.name
        numMeshReferenced.append(0)
        numRigidBodiesReferenced.append(0)
        boneNames.append(bone_name)
        boneIndex[bone_name] = i
    n_bones = i + 1
      
    # boneParents bindPoses
    boneParents = []
    bindPoses = np.zeros(n_bones*16)
    bones.foreach_get("matrix_local", bindPoses)
    bindPoses = bindPoses.reshape(-1,4,4)
    for i, bone in enumerate(bones):
        bone_parent = bone.parent
        if bone_parent:
            boneParents.append(boneIndex[bone_parent.name])
            if bone.use_relative_parent:
                bindPoses[i] = np.array(obvg.matrix_parent_inverse.inverted() * bone.parent.matrix_local * (bone_parent.matrix_local.inverted_safe() @ Matrix(bindPoses[i])))
        else:
            boneParents.append(-1)
    bindPoses = bindPoses[:,:,:3]
    
    # Get the used bones for collision volumes
    sphere_coll = GetCollection("Collision Spheres", make_active=False)
    capsule_coll = GetCollection("Collision Capsules", make_active=False)
    if sphere_coll:
        spheres = sphere_coll.objects
        sphere_bone_names = [x.name[x.name.find("_")+1:x.name.rfind("_")] for x in spheres]
        spheresBool = [bone.name in sphere_bone_names for bone in bones]
    if capsule_coll:
        capsules = capsule_coll.objects
        capsule_bone_names = [x.name[x.name.find("_")+1:x.name.rfind("_")] for x in capsules]
        capsulesBool = [bone.name in capsule_bone_names for bone in bones]
    
    # Get the used bones vertex groups of the first mesh (we assume lower lod levels will use the same vertex groups or less of them, but definitely not more)
    selectOnly(obvg)
    bpy.ops.object.vertex_group_clean(group_select_mode='ALL')
    vertexGroupsBool = []
    for bone in bones:
        if bone.name in obvg.vertex_groups:
            vg = obvg.vertex_groups[bone.name]
            vertexGroupsBool.append(any(vg.index in [g.group for g in v.groups] for v in obvg.data.vertices))
        else:
            vertexGroupsBool.append(False)
    
    # Get Number of Used Bones        
    usedBonesBool = np.array(vertexGroupsBool)
    if "spheres" in locals():
        usedBonesBool += np.array(spheresBool)
    if "capsules" in locals():
        usedBonesBool += np.array(capsulesBool)
    numUsedBones = np.count_nonzero(usedBonesBool) + 1
    
    # Sort Bones by Use to Get the Internal Index
    sortedBoneIds = list(x for y,x in sorted(zip(usedBonesBool,list(boneIndex.values())),key=lambda v: (v[0], -v[1]), reverse = True))
    boneIndexInternal = dict([(bone.name, sortedBoneIds.index(i)) for i, bone in enumerate(bones)])
        
    # For each LOD
    simulationMaterials = []
    physicalMeshes = []
    graphicalLods = []
    boundingBoxes = []
    storedPhysicalMeshes = []
    storedPhysicalMeshesDicts = []
    storedPhysicalMeshesFacesFinal = []
    storedPhysicalMeshesNormalOffsets = []
    storedPhysicalMeshesMaxEdgeLength = []
    storedPhysicalMeshesAllNormals = []
    for numLod, obj in enumerate(objects):
        kwargs_materials = {}
        kwargs_lod = {}
        kwargs_lod['numLod'] = numLod
        kwargs_lod['physicalMeshId'] = numLod
        kwargs_physical = {}
        
        # Make and prepare a duplicate mesh
        selectOnly(obj)
        bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
        duplicate_obj = bpy.context.active_object
        duplicate_obj.name = "tempGraphicalMesh"
        #Apply modifiers
        for mod in duplicate_obj.modifiers:
            if mod.type != 'ARMATURE' and mod.name != 'ClothSimulation':
                bpy.ops.object.modifier_apply(modifier = mod.name)
        applyTransforms(duplicate_obj, armaScale, armaRot, armaLoc)
        TriangulateActiveMesh()
        deleteIsolatedVertices(duplicate_obj)
        apply_drive(duplicate_obj, 1, False)
        
        # Export Physical Mesh
        # Duplication and preparation
        bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
        physicalMesh = bpy.context.active_object
        physicalMesh.name = "tempPhysicalMesh"
        physics_mesh = physicalMesh.data
        n_groups, driveDataGraphical, latchDataGraphical = cleanUpDriveLatchGroups(physicalMesh, True)
        drive_bool_array = np.any(latchDataGraphical > 0.6, axis = 1)
        if ".select_vert" not in physics_mesh.attributes:
            physics_mesh.attributes.new(".select_vert", "BOOLEAN", "POINT")
        physics_mesh.attributes[".select_vert"].data.foreach_set("value", drive_bool_array)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.remove_doubles(threshold = 0.001)
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.object.mode_set(mode='OBJECT')
        deleteIsolatedVertices(physicalMesh)
        
        # Get Faces and Maximum Distance Paint to Order Vertices
        #MaximumDistance
        verts = physics_mesh.vertices
        n_vertices = len(verts)
        vertex_groups = physicalMesh.vertex_groups
        temp_max_dist = getWeightArray(verts, vertex_groups["PhysXMaximumDistance"])
        #Faces and Ordering
        n_face_indices = len(physics_mesh.polygons) * 3
        face_array = np.zeros(n_face_indices, dtype=int)
        physics_mesh.attributes[".corner_vert"].data.foreach_get("value", face_array)
        temp_faces_score = temp_max_dist[face_array].reshape(-1,3)
        temp_faces_nsim = np.count_nonzero(temp_faces_score, axis = 1)
        temp_faces_score = np.sum(temp_faces_score, axis = 1)  
        face_array = np.array([x for z,y,x in sorted(zip(temp_faces_nsim,temp_faces_score,face_array.reshape(-1,3)), key=lambda v: (v[0], v[1]), reverse = True)]).flatten()
        sortedVertices = np.array(list(dict.fromkeys(face_array).keys()))
        #Get Final Faces Directly
        face_array = np.array([np.where(sortedVertices == x) for x in face_array]).flatten()
        faces_final = face_array.reshape(-1,3)
        #Re-order Vertices
        OrderVertices(physics_mesh, sortedVertices, True)
        
        # Vertices Positions
        vertices = np.zeros(n_vertices * 3)
        physics_mesh.attributes['position'].data.foreach_get("vector", vertices)
        vertices = vertices.reshape(-1,3)
        kwargs_physical['numVertices_PhysicalMesh'] = n_vertices
        kwargs_physical['vertices_PhysicalMesh'] = ', '.join([' '.join(map(str, x)) for x in vertices])
        
        # Normals
        normals = GetLoopDataPerVertex(physics_mesh, "NORMAL")
        kwargs_physical['normals_PhysicalMesh'] = ', '.join([' '.join(map(str, x)) for x in normals])
        #I don't know what to do with these skinning normals yet
        kwargs_physical['skinningNormals_PhysicalMesh'] = kwargs_physical['normals_PhysicalMesh']
        
        # Constrain Coefficients
        maximumMaxDistance = obj['maximumMaxDistance']
        n_groups, driveDataPhysical, latchDataPhysical = cleanUpDriveLatchGroups(physicalMesh, True)
        driveLatchGroupPhysical = np.argmax(driveDataPhysical, axis=1)
        constrainCoefficients = []
        for vg in ["PhysXMaximumDistance", "PhysXBackstopRadius", "PhysXBackstopDistance"]:
            color_array2 = getWeightArray(physics_mesh.vertices, vertex_groups[vg])
            if vg != "PhysXBackstopDistance": color_array2[color_array2 < 0.001] = 0
            if vg == "PhysXMaximumDistance": color_array2 *= maximumMaxDistance
            constrainCoefficients.append(deepcopy(color_array2))
        constrainCoefficients = np.array(constrainCoefficients).T
        kwargs_physical['constrainCoefficients_PhysicalMesh'] = ','.join([' '.join(map(str, x)) for x in constrainCoefficients])
        
        # Maximum Max Distance
        kwargs_physical['maximumMaxDistance'] = np.max(constrainCoefficients[:,0])
                
        # Get Bone Weights and Indices
        boneIndices = []
        boneWeights = []  
        for vert in physics_mesh.vertices:
            boneIndices.append(np.full(4, numUsedBones-1, dtype=int))
            boneWeights.append(np.zeros(4, dtype=float))
            i = 0
            for g in vert.groups:
                g_weight = g.weight
                if i < 4 and g_weight and vertex_groups[g.group].name in boneIndexInternal:
                    boneIndices[-1][i] = boneIndexInternal[vertex_groups[g.group].name]
                    boneWeights[-1][i] = g_weight
                    i += 1
        boneWeights = [x/x.sum() for x in boneWeights]             
        kwargs_physical['numBoneIndices_PhysicalMesh'] = n_vertices*4
        kwargs_physical['boneIndices_PhysicalMesh'] = ' '.join([' '.join(map(str, x)) for x in boneIndices])
        kwargs_physical['boneWeights_PhysicalMesh'] = ' '.join([' '.join(map(str, x)) for x in boneWeights])
        
        # OptimizationData
        optimizationData = []
        for i in range(0,n_vertices,2):
            second_i = i + 1
            opt1 = np.count_nonzero(boneWeights[i])
            opt2 = np.count_nonzero(boneWeights[second_i]) if second_i < len(boneWeights) else 0
            byte = "0" + Get3Bits(opt2) + "0" + Get3Bits(opt1)
            optimizationData.append(int(byte,2))
        kwargs_physical['numOptimizationData'] = len(optimizationData)
        kwargs_physical['optimizationData'] = ' '.join(map(str, optimizationData))
        
        # Write Faces
        kwargs_physical['numFaceIndices_PhysicalMesh'] = n_face_indices
        kwargs_physical['faceIndices_PhysicalMesh'] = ' '.join(map(str,face_array))
        
        # Edges Length
        edge_array = np.zeros(len(physics_mesh.edges) * 2, dtype=int)
        physics_mesh.attributes['.edge_verts'].data.foreach_get("value", edge_array)
        edge_array = edge_array.reshape(-1,2)
        edgesLength = [np.linalg.norm(vertices[x[0]] - vertices[x[1]]) for x in edge_array]
        max_edge_length = np.max(edgesLength)
        kwargs_physical['shortestEdgeLength'] = np.min(edgesLength)
        kwargs_physical['averageEdgeLength'] = np.mean(edgesLength)
        
        #Physical Submesh and Lods
        kwargs_physical['subMeshes_PhysicalMesh'] = ''
        kwargs_physical['numSubMeshes_PhysicalMesh'] = 0
        kwargs_physical['numPhysicalLods'] = 1
        kwargs_physical['physicalLods'] = '0 PX_MAX_U32 0 0'
        numIndices = np.count_nonzero(temp_faces_nsim) * 3
        if numIndices:
            numVertices = len(set(face_array[0:numIndices]))
            numMaxDistance0 = numVertices - np.count_nonzero(constrainCoefficients[:,0])
            kwargs_physical['numSubMeshes_PhysicalMesh'] = 1
            kwargs_physical['subMeshes_PhysicalMesh'] = ' '.join(map(str,[numIndices, numVertices, numMaxDistance0]))
            kwargs_physical['numPhysicalLods'] = 2
            kwargs_physical['physicalLods'] = ', '.join(['0 PX_MAX_U32 0 ' + str(kwargs_physical['maximumMaxDistance']), str(numVertices) + ' 0 1 0'])
            
        # Prepare Skin Cloth Map
        kwargs_lod['numImmediateClothMap'] = 0
        kwargs_lod['numSkinClothMap'] = 0
        kwargs_lod['immediateClothMap'] = ''
        kwargs_lod['skinClothMap'] = ''
        kwargs_lod['skinClothMapOffset'] = kwargs_physical['averageEdgeLength']*0.1
        kwargs_lod['physicsSubmeshPartitioning'] = ''
        kwargs_lod['numPhysicsSubmeshPartitioning'] = 0
        if np.all(np.any(driveDataGraphical > 0.6, axis = 1)):
            immediateClothMap_bool = True
            immediate_kdtree = MakeKDTreeFromObject(physicalMesh)
            immediateClothMap = []
        else:
            immediateClothMap_bool = False
            KDTrees = []
            for group in range(n_groups):
                KDTrees.append(MakeKDTreeFromObject(physicalMesh, np.where(driveLatchGroupPhysical == group)[0]))
            skinClothMap = []
            physicsSubmeshPartitioning = []
            
        # Append Per Physical Lod Information  
        storedPhysicalMeshesDicts.append(kwargs_physical)
        storedPhysicalMeshes.append(physicalMesh)
        storedPhysicalMeshesFacesFinal.append(faces_final)
        storedPhysicalMeshesNormalOffsets.append(kwargs_lod['skinClothMapOffset'])
        storedPhysicalMeshesMaxEdgeLength.append(max_edge_length)
        storedPhysicalMeshesAllNormals.append(normals)
        
        # Export Graphical Mesh
        selectOnly(duplicate_obj)
        #Edge Split where split normals or uv seam (necessary as these face corner data are stored per vertex in .apx)
        SplitMesh(duplicate_obj.data)
        #Split by materials # In edit mode to avoid messing up normals
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.separate(type='MATERIAL')
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.object.mode_set(mode='OBJECT')
        
        #Loop through submeshes
        submesh_meshes = []
        submeshes = []
        materials = []
        lodUsedBones = []
        numSubmesh = -1
        n_vertices_all = 0
        for submesh in arma.children:
            if "tempGraphicalMesh" in submesh.name:
                mesh = submesh.data
                selectOnly(submesh)
                numSubmesh += 1
                submesh_meshes.append(submesh)
                kwargs_submesh = {}
                bufferData = []
                
                # VertexCount
                n_vertices = len(mesh.vertices)
                kwargs_submesh["numVertices"] = n_vertices

                # Re-Oder Graphical Vertices
                #Get Faces
                n_face_indices = len(mesh.polygons) * 3
                face_array = np.zeros(n_face_indices, dtype=int)
                mesh.attributes[".corner_vert"].data.foreach_get("value", face_array)
                #Get Closest Physical Vertices
                if immediateClothMap_bool:
                    submesh_closestVerts = np.array([getClosest(vert.co, immediate_kdtree, 0.001) for vert in mesh.vertices])
                else:
                    n_groups, driveDataGraphical, latchDataGraphical = cleanUpDriveLatchGroups(submesh, True)
                    driveLatchGroupGraphical = np.argmax(np.sum([driveDataGraphical, latchDataGraphical], axis=0), axis=1)
                    submesh_closestVerts = np.array([getClosest(vert.co, KDTrees[driveLatchGroupGraphical[vert_id]], max_edge_length) for vert_id, vert in enumerate(mesh.vertices)])
                #Ordering by Maximum Distance
                temp_verts_score = constrainCoefficients[submesh_closestVerts][:,0]
                temp_faces_score = temp_verts_score[face_array].reshape(-1,3)
                temp_faces_nsim = np.count_nonzero(temp_faces_score, axis = 1)
                temp_verts_sim_dict = dict(zip(face_array, (temp_faces_nsim>0).repeat(3)))
                temp_verts_sim_bool = list(dict(sorted(zip(temp_verts_sim_dict.keys(), temp_verts_sim_dict.values()), key=lambda v: v[0])).values())
                sortedVertices = np.array([x for x,y,z in sorted(zip(range(n_vertices), temp_verts_score, temp_verts_sim_bool), key=lambda v: (v[2], v[1]), reverse = True)])
                submesh_closestVerts = submesh_closestVerts[sortedVertices]
                #Re-order Vertices
                OrderVertices(mesh, sortedVertices, True)
                
                # Get Vertices Positions
                vertices = np.zeros(n_vertices * 3)
                mesh.attributes['position'].data.foreach_get("vector", vertices)
                kwargs_vertices = {}
                kwargs_vertices['numData'] = n_vertices
                kwargs_vertices['arrayData'] = ', '.join([' '.join(map(str, vert)) for vert in vertices.reshape(-1,3)])
                bufferData.append(templateDataPositionNormal.format(**kwargs_vertices))
                
                # Get Normals
                normals = GetLoopDataPerVertex(mesh, "NORMAL")
                kwargs_normals = {}
                kwargs_normals['numData'] = n_vertices
                kwargs_normals['arrayData'] = ', '.join([' '.join(map(str, norm)) for norm in normals])
                bufferData.append(templateDataPositionNormal.format(**kwargs_normals))
                
                # Get Tangents
                if mesh.uv_layers:
                    mesh.calc_tangents()
                tangents = GetLoopDataPerVertex(mesh, "TANGENT")
                kwargs_tangents = {}
                kwargs_tangents['numData'] = n_vertices
                kwargs_tangents['arrayData'] = ','.join([' '.join(map(str, tang)) for tang in tangents])
                bufferData.append(templateDataTangent.format(**kwargs_tangents))
                
                # Initialise Buffer Formats
                bufferFormats = [templateVertexPositionBuffer, templateVertexNormalBuffer, templateVertexTangentBuffer]
                
                # Get Vertex Color
                for layer in mesh.color_attributes:
                    if layer.domain == 'CORNER':
                        mesh.color_attributes.active_color = layer
                        bpy.ops.geometry.color_attribute_convert(domain='POINT', data_type='FLOAT_COLOR')
                        layer = mesh.color_attributes.active_color
                    vcol = np.zeros(n_vertices * 4)
                    layer.data.foreach_get("color", vcol)
                    # Write Vertex Color Buffer
                    kwargs_vcol = {}
                    kwargs_vcol['numData'] = len(vcol)
                    kwargs_vcol['arrayData'] = ','.join([' '.join(map(str, map(int, x))) for x in (vcol * 255).reshape(-1,4)])
                    bufferData.append(templateDataColor.format(**kwargs_vcol))
                    bufferFormats.append(templateVertexColorBuffer)
                    break
                    
                # Get UV Maps
                semantic = 5
                id = 6
                for uv_index, uv in enumerate(mesh.uv_layers):
                    if semantic < 9:
                        uvs = GetLoopDataPerVertex(mesh, "UV", uv.name)
                        # Write UV Buffer
                        kwargs_uvs = {}
                        kwargs_uvs['numData'] = n_vertices
                        kwargs_uvs['arrayData'] = ','.join([' '.join(map(str, x)) for x in uvs])
                        bufferData.append(templateDataUV.format(**kwargs_uvs))
                        kwargs_uv_buffer = {}
                        kwargs_uv_buffer['numUVBuffer'] = uv_index
                        kwargs_uv_buffer['semanticUVBuffer'] = semantic
                        kwargs_uv_buffer['idEndUVBuffer'] = id
                        bufferFormats.append(templateVertexUVBuffer.format(**kwargs_uv_buffer))
                        semantic += 1
                        id += 1
                
                # Get Bone Indices and Weights    
                boneIndices = []
                boneWeights = []
                vertex_groups = submesh.vertex_groups
                for vert in mesh.vertices:
                    boneIndices.append(np.full(4, numUsedBones-1, dtype=int))
                    boneWeights.append(np.zeros(4, dtype=float))
                    i = 0
                    for g in vert.groups:
                        g_weight = g.weight
                        if i < 4 and g_weight and vertex_groups[g.group].name in boneIndexInternal:
                            bone_id = boneIndexInternal[vertex_groups[g.group].name]
                            boneIndices[-1][i] = bone_id
                            # Add to the used bones for that mesh
                            if bone_id not in lodUsedBones:
                                lodUsedBones.append(bone_id)
                            #Add a vertex referenced for this bone
                            numMeshReferenced[boneIndex[vertex_groups[g.group].name]] += 1
                            boneWeights[-1][i] = g_weight
                            i += 1
                boneWeights = [x/x.sum() for x in boneWeights]
                kwargs_boneIndices = {}
                kwargs_boneIndices['numData'] = n_vertices
                kwargs_boneIndices['arrayData'] = ','.join([' '.join(map(str, x)) for x in boneIndices])
                bufferData.append(templateDataBoneIndex.format(**kwargs_boneIndices))
                bufferFormats.append(templateVertexBoneIndexBuffer)
                kwargs_boneWeights = {}
                kwargs_boneWeights['numData'] = n_vertices
                kwargs_boneWeights['arrayData'] = ','.join([' '.join(map(str, x)) for x in boneWeights])
                bufferData.append(templateDataBoneWeight.format(**kwargs_boneWeights))
                bufferFormats.append(templateVertexBoneWeightBuffer)
                
                #Write Buffers
                kwargs_submesh['numBuffers'] = len(bufferFormats)
                kwargs_submesh['bufferFormats'] = '\n                              '.join(buffer for buffer in bufferFormats)
                kwargs_submesh['bufferData'] = '\n                          '.join(buffer for buffer in bufferData)
                
                # Get Faces
                mesh.attributes[".corner_vert"].data.foreach_get("value", face_array)
                kwargs_submesh['numIndices'] = n_face_indices
                kwargs_submesh['faceIndices'] = ' '.join(map(str, face_array))
                
                # Vertex and Index Partitions
                kwargs_submesh['vertexPartition'] = '0 ' + str(n_vertices)
                kwargs_submesh['indexPartition'] = '0 ' + str(n_face_indices)
                
                # Materials
                materials.append(mesh.materials[0].name)
                
                # Compute Submesh Cloth Map
                if immediateClothMap_bool:
                    immediateClothMap.extend(submesh_closestVerts)
                else:
                    for vert_id, vert in enumerate(mesh.vertices):
                        closestFace = faces_final[np.where(faces_final == submesh_closestVerts[vert_id])[0][0]]
                        vertBary, normBary, tangBary = getVertexBary(vert.co, Vector((normals[vert_id])), physicalMesh, submesh_closestVerts[vert_id], closestFace, kwargs_lod['skinClothMapOffset'], Vector((tangents[vert_id][0:3])))
                        skinClothMap.append([' '.join(map(str, vertBary)), closestFace[0], ' '.join(map(str, normBary)), closestFace[1], ' '.join(map(str, tangBary)), closestFace[2], n_vertices_all + vert_id])
                    # Compute physicsSubmeshPartitioning
                    numIndices = np.count_nonzero(temp_faces_nsim) * 3
                    if numIndices:
                        numVerticesAdditional = len(set(face_array[0:numIndices]))
                        numVertices = np.count_nonzero(constrainCoefficients[submesh_closestVerts][:,0])
                        physicsSubmeshPartitioning.append([numSubmesh, 0, numVertices, numVerticesAdditional, numIndices])
                    else:
                        physicsSubmeshPartitioning.append([numSubmesh, 0, 0, 0, 0])

                # Append submesh
                submeshes.append(templateSubMesh.format(**kwargs_submesh))
                n_vertices_all += n_vertices
        
        # Join submeshes back together        
        JoinThem(submesh_meshes)
        meshLod = bpy.context.active_object
        
        # Write submeshes and materials
        kwargs_lod['numSubMeshes'] = len(submeshes)
        kwargs_lod['subMeshes'] = '\n                '.join(x for x in submeshes)
        kwargs_lod['materials'] = '\n                '.join('<value type="String">{}</value>'.format(mat) for mat in materials)
        
        # Number of Used Bones
        kwargs_lod['numUsedBones'] = numUsedBones
        
        # LOD Bounding Box
        lodBoundingBox = (*list(meshLod.bound_box[0]), *list(meshLod.bound_box[6]))
        kwargs_lod['partBounds'] = ' '.join(map(str, lodBoundingBox))
        boundingBoxes.append(lodBoundingBox)
        
        # Simulation Materials
        sim_mat_name = main_coll.name
        if numLod: 
            sim_mat_name += ("_LOD" + str(numLod))
        kwargs_materials['simulationMaterialName'] = sim_mat_name
        
        for key in meshLod.keys():
            kwargs_materials[key] = meshLod[key]
            if type(kwargs_materials[key]) == bool:
                kwargs_materials[key] = str(kwargs_materials[key]).lower()
        kwargs_materials.pop("maximumMaxDistance")
        
        # Immediate Cloth Map
        if immediateClothMap_bool:
            kwargs_lod['numImmediateClothMap'] = n_vertices_all
            kwargs_lod['immediateClothMap'] = ' '.join(map(str, immediateClothMap))
        
        # Or True Skin Cloth Map  
        else:
            kwargs_lod['numSkinClothMap'] = n_vertices_all
            kwargs_lod['skinClothMap'] = ','.join([' '.join(map(str, x)) for x in skinClothMap])
        
            # physicsSubmeshPartitioning   
            kwargs_lod['numPhysicsSubmeshPartitioning'] = numSubmesh+1
            kwargs_lod['physicsSubmeshPartitioning'] = ','.join([' '.join(map(str, x)) for x in physicsSubmeshPartitioning])
            
        # Append Per Graphical Lod information
        graphicalLods.append(templateGraphicalMesh.format(**kwargs_lod))
        simulationMaterials.append(templateSimulationMaterial.format(**kwargs_materials))
        
        # Delete the duplicate graphical mesh
        bpy.data.objects.remove(meshLod)
    
    # Deal with Physical Meshes
    if num_objects > 1:
        KDTrees = []
        for i in range(num_objects):
            KDTrees.append(MakeKDTreeFromObject(storedPhysicalMeshes[i]))
    for i in range(num_objects):
        # Transition Up/Down
        storedPhysicalMeshesDicts[i]["numTransitionDown"] = 0
        storedPhysicalMeshesDicts[i]["transitionDown"] = ""
        storedPhysicalMeshesDicts[i]["transitionDownThickness"] = 0
        storedPhysicalMeshesDicts[i]["transitionDownOffset"] = 0
        storedPhysicalMeshesDicts[i]["numTransitionUp"] = 0
        storedPhysicalMeshesDicts[i]["transitionUp"] = ""
        storedPhysicalMeshesDicts[i]["transitionUpThickness"] = 0
        storedPhysicalMeshesDicts[i]["transitionUpOffset"] = 0
        if num_objects > 1:
            if i < numLod:
                target_id = i + 1
                storedPhysicalMeshesDicts[i]["transitionUpThickness"] = 1
                storedPhysicalMeshesDicts[i]["transitionUpOffset"] = storedPhysicalMeshesNormalOffsets[target_id]
                transitionUp = []
                for vert_id, vert in enumerate(storedPhysicalMeshes[i].data.vertices):
                    closestVert = getClosest(vert.co, KDTrees[target_id], storedPhysicalMeshesMaxEdgeLength[target_id])
                    closestFace = storedPhysicalMeshesFacesFinal[target_id][np.where(storedPhysicalMeshesFacesFinal[target_id] == closestVert)[0][0]]
                    vertBary, normBary = getVertexBary(vert.co, Vector((storedPhysicalMeshesAllNormals[i][vert_id])), storedPhysicalMeshes[target_id], closestVert, closestFace, storedPhysicalMeshesDicts[i]["transitionUpOffset"])
                    transitionUp.append([' '.join(map(str, vertBary)), closestFace[0], ' '.join(map(str, normBary)), closestFace[1], "PX_MAX_F32", "PX_MAX_F32", "PX_MAX_F32", closestFace[2], vert_id])
                storedPhysicalMeshesDicts[i]["numTransitionUp"] = len(transitionUp)
                storedPhysicalMeshesDicts[i]['transitionUp'] = ','.join([' '.join(map(str, x)) for x in transitionUp])
            if i:
                target_id = i - 1
                storedPhysicalMeshesDicts[i]["transitionDownThickness"] = 1
                storedPhysicalMeshesDicts[i]["transitionDownOffset"] = storedPhysicalMeshesNormalOffsets[target_id]
                transitionDown = []
                for vert_id, vert in enumerate(storedPhysicalMeshes[i].data.vertices):
                    closestVert = getClosest(vert.co, KDTrees[target_id], storedPhysicalMeshesMaxEdgeLength[target_id])
                    closestFace = storedPhysicalMeshesFacesFinal[target_id][np.where(storedPhysicalMeshesFacesFinal[target_id] == closestVert)[0][0]]
                    vertBary, normBary = getVertexBary(vert.co, Vector((storedPhysicalMeshesAllNormals[i][vert_id])), storedPhysicalMeshes[target_id], closestVert, closestFace, storedPhysicalMeshesDicts[i]["transitionDownOffset"])
                    transitionDown.append([' '.join(map(str, vertBary)), closestFace[0], ' '.join(map(str, normBary)), closestFace[1], "PX_MAX_F32", "PX_MAX_F32", "PX_MAX_F32", closestFace[2], vert_id])
                storedPhysicalMeshesDicts[i]["numTransitionDown"] = len(transitionDown)
                storedPhysicalMeshesDicts[i]['transitionDown'] = ','.join([' '.join(map(str, x)) for x in transitionDown])
        
        # Append Per Physical Lod information 
        physicalMeshes.append(templatePhysicalMesh.format(**storedPhysicalMeshesDicts[i]))
    
    # Delete the physical meshes  
    for obj in storedPhysicalMeshes:
        bpy.data.objects.remove(obj)
    
    # Write Mesh Information in Main Template
    kwargs['physicalMeshes'] = '\n      '.join(x for x in physicalMeshes)
    kwargs['graphicalMeshes'] = '\n      '.join(x for x in graphicalLods)
    kwargs['simulationMaterials'] = '\n          '.join(x for x in simulationMaterials)
    
    # General Bounding Box
    boundingBox = np.array(boundingBoxes).T
    generalBoundingBox = [min(x) if any(y<0 for y in x) else max(x) for x in boundingBox]
    kwargs['boundingBox'] = ' '.join(str(x) for x in generalBoundingBox)
    
    # Bone Spheres
    kwargs['numBoneSpheres'] = "0"
    kwargs['boneSpheres'] = ""
    sphereIndex = {}
    sphereAll = []
    if "spheres" in locals():
        for i, sphere in enumerate(spheres):
            sphere_name = sphere.name
            sphereIndex[sphere_name] = i
            sphereBoneName = sphere_bone_names[i]
            #Add a rigid body referenced for this bone
            numRigidBodiesReferenced[boneIndex[sphereBoneName]] += 1
            sphereLocation, sphereRadius = applyTransforms(sphere, armaScale, armaRot, armaLoc, True, True, bones[sphereBoneName])
            sphereAll.append([boneIndexInternal[sphereBoneName], sphereRadius, *sphereLocation])
        kwargs['numBoneSpheres'] = len(spheres)
        kwargs['boneSpheres'] = ','.join(' '.join(map(str, x)) for x in sphereAll)
        
    # BoneSphereConnections
    kwargs['numBoneSphereConnections'] = "0"
    kwargs['boneSphereConnections'] = ""
    boneSphereConnections = []
    connection_coll = GetCollection("Collision Connections", make_active=False)
    if connection_coll and sphere_coll:
        connections = connection_coll.objects
        if connections:
            for connection in connections:
                connection_name = connection.name
                sphereName1 = connection_name[:connection_name.find("_to_")]
                sphereName2 = connection_name[connection_name.find("_to_")+4:]
                boneSphereConnections.append([sphereIndex[sphereName1], sphereIndex[sphereName2]])
            kwargs['numBoneSphereConnections'] = len(connections) * 2
            kwargs['boneSphereConnections'] = ' '.join(' '.join(map(str,x)) for x in boneSphereConnections)
            
    # BoneCapsules
    kwargs['numBoneActors'] = 0
    kwargs['boneActors'] = ""
    capsuleAll = []
    if "capsules" in locals():
        for i, capsule in enumerate(capsules):
            capsuleBoneName = capsule_bone_names[i]
            #Add a rigid body referenced for this bone
            numRigidBodiesReferenced[boneIndex[capsuleBoneName]] += 1
            selectOnly(capsule)
            # Separate by materials
            bpy.ops.mesh.separate(type='MATERIAL')
            spherePositions = []
            subCapsules = []
            for subCapsule in capsules:
                if capsule.name in subCapsule.name:
                    subCapsules.append(subCapsule)
                    if "Material_Sphere1" in subCapsule.data.materials or "Material_Sphere2" in subCapsule.data.materials:
                        sphereLocation, sphereRadius = applyTransforms(subCapsule, armaScale, armaRot, armaLoc, True, half = True)
                        spherePositions.append(sphereLocation)    
            JoinThem(subCapsules)
            capsuleDir = spherePositions[0] - spherePositions[1]
            capsuleHeight = np.linalg.norm(capsuleDir)
            capsulePosition = np.mean(spherePositions, axis = 0)
            capsuleMat = Vector((0,-capsuleHeight,0)).rotation_difference(capsuleDir).to_matrix().to_4x4()
            capsuleMat.col[3] = [*capsulePosition, 1]
            capsuleMatLocal = bones[capsuleBoneName].matrix_local.inverted() @ capsuleMat
            capsuleMatLocal = np.array(capsuleMatLocal).T[:,:3]
            capsuleAll.append([boneIndexInternal[capsuleBoneName], 0, 0, sphereRadius, capsuleHeight, ' '.join(map(str, np.array(capsuleMatLocal).flat))])
        kwargs['numBoneActors'] = len(capsules)
        kwargs['boneActors'] = ','.join(' '.join(map(str, x)) for x in capsuleAll)
            
    # Write armature
    boneDefinitions = []
    bonesReferenced = 0
    bonesReferencedByMesh = 0
    for i, bone in enumerate(bones):
        bone_name = bone.name
        kwargs_bone = {}
        kwargs_bone['internalIndex'] = boneIndexInternal[bone_name]
        kwargs_bone['externalIndex'] = boneIndex[bone_name]
        kwargs_bone['numMeshReferenced'] = numMeshReferenced[i]
        kwargs_bone['numRigidBodiesReferenced'] = numRigidBodiesReferenced[i]
        kwargs_bone['parentIndex'] = boneParents[i]
        kwargs_bone['bindPose'] = ' '.join(map(str, bindPoses[i].flat))
        kwargs_bone['boneName'] = boneNames[i]
        boneDefinitions.append(kwargs_bone)
        if numMeshReferenced[i] or numRigidBodiesReferenced[i]:
            bonesReferenced += 1
        if numMeshReferenced[i]:
            bonesReferencedByMesh += 1
    sortedBoneDefinitions = sorted(boneDefinitions, key=lambda v: v['internalIndex'])
        
    # Write the armature in the main template
    kwargs['numBones'] = n_bones
    kwargs['bones'] = '\n      '.join(templateBone.format(**x) for x in sortedBoneDefinitions)
    kwargs['bonesReferenced'] = bonesReferenced
    kwargs['bonesReferencedByMesh'] = bonesReferencedByMesh
    kwargs['rootBoneIndex'] = boneIndexInternal[bones[0].name]
    
    # Write Simulation Parameters
    for key in main_coll.keys():
        kwargs[key] = main_coll[key]
        if type(kwargs[key]) == bool:
            kwargs[key] = str(kwargs[key]).lower()
        elif key == 'gravityDirection':
            kwargs[key] = ' '.join(map(str, list(kwargs[key])))
            
    #%% write the template with generated values
    with open(filepath, 'w', encoding = 'utf-8') as f:
        f.write(templateClothingMain.format(**kwargs))
        
    # Compute cooked data if possible
    apex_path = bpy.context.preferences.addons[__package__[:-9]].preferences.apex_sdk_cli
    if os.path.exists(apex_path):
        import subprocess
        command = [apex_path, "-s", "apx", filepath]
        subprocess.run(command)