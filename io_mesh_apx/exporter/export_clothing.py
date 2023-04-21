# -*- coding: utf-8 -*-
# exporter/export_clothing.py

import bpy
import bmesh
import re
import numpy as np
from copy import deepcopy
from mathutils import Matrix, Vector
from io_mesh_apx.exporter.template_clothing import *
from io_mesh_apx.tools.paint_tools import cleanUpDriveLatchGroups, CheckPhysicalPaint, apply_drive
from io_mesh_apx.utils import JoinThem, GetLoopDataPerVertex, Get3Bits, getSubmeshID, selectOnly, applyTransforms, MakeKDTreeFromObject, getClosest, getVertexBary, SplitMesh, TriangulateActiveMesh
    
def write_clothing(context, filepath, maximumMaxDistance):
    kwargs = {}
    parent_coll = bpy.context.view_layer.active_layer_collection
    
    # Get transforms of the armature
    if bpy.context.active_object.type == "ARMATURE":
        arma = bpy.context.active_object
    elif bpy.context.active_object.parent.type == "ARMATURE":
        arma = bpy.context.active_object.parent
    armaScale = np.array(arma.scale)
    armaRot = np.array(arma.rotation_euler)
    armaLoc = np.array(arma.location)
    
    #Get the meshes to export
    if "lod0" not in arma.children[0].name:
        objects = [arma.children[0]]
    else:
        objects = arma.children
    obvg = objects[0]
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
    if "Collision Spheres" in parent_coll.collection.children:
        spheres = parent_coll.collection.children['Collision Spheres'].objects
        sphere_bone_names = [x.name[x.name.find("_")+1:x.name.rfind("_")] for x in spheres]
        spheresBool = [bone.name in sphere_bone_names for bone in bones]
    if "Collision Capsules" in parent_coll.collection.children:
        capsules = parent_coll.collection.children['Collision Capsules'].objects
        capsule_bone_names = [x.name[x.name.find("_")+1:x.name.rfind("_")] for x in capsules]
        capsulesBool = [bone.name in capsule_bone_names for bone in bones]
    
    # Get the used bones vertex groups of the first mesh (we assume lower lod levels will use the same vertex groups or less of them, but definitely not more)
    vertexGroupsBool = []
    for bone in bones:
        if bone.name in obvg.vertex_groups:
            vg = obvg.vertex_groups[bone.name]
            vertexGroupsBool.append(any(vg.index in [g.group for g in v.groups] for v in obvg.data.vertices))
    
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
    storedPhysicalMeshes = []
    storedPhysicalMeshesDicts = []
    storedPhysicalMeshesFacesFinal = []
    storedPhysicalMeshesNormalOffsets = []
    storedPhysicalMeshesMaxEdgeLength = []
    storedPhysicalMeshesAllNormals = []
    graphicalLods = []
    boundingBoxes = []
    for numLod, obj in enumerate(objects):
        kwargs_materials = {}
        kwargs_lod = {}
        kwargs_lod['numLod'] = numLod
        kwargs_lod['physicalMeshId'] = numLod
        
        # Make and prepare a duplicate mesh
        selectOnly(obj)
        bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
        duplicate_obj = bpy.context.active_object

        # Apply transforms
        applyTransforms(duplicate_obj, armaScale, armaRot, armaLoc)
        
        # Triangulate Faces
        TriangulateActiveMesh()
        
        # Apply Drive Paint
        apply_drive(context = bpy.context, group="1", invert = False)
        
        # Split by materials
        bpy.ops.mesh.separate(type='MATERIAL')
        
        #Loop through submeshes
        all_Normals = []
        all_Tangents = []
        submesh_meshes = []
        submeshes = []
        materials = []
        lodUsedBones = []
        numSubmesh = -1
        submeshVertices = []
        startVertex = 0
        obj_name = obj.name
        for submesh in arma.children:
            submesh_name = submesh.name
            if obj_name in submesh_name and obj_name != submesh_name:
                mesh = submesh.data
                selectOnly(submesh)
                numSubmesh += 1
                submesh_meshes.append(submesh)
                
                # Edge Split where split normals or uv seam (necessary as these face corner data are stored per vertex in .apx)
                SplitMesh(mesh)
                
                # Normals and Tangents Calculation
                mesh.calc_normals_split()
                if mesh.uv_layers:
                    mesh.calc_tangents()
                
                n_vertices = len(mesh.vertices) 
                kwargs_submesh = {}
                kwargs_submesh["numVertices"] = n_vertices
                submeshVertices.append([startVertex, startVertex + n_vertices-1])
                startVertex += n_vertices
                bufferData = []
                bufferFormats = []
                
                # Get Vertices Positions
                vertices = np.zeros(n_vertices * 3)
                mesh.attributes['position'].data.foreach_get("vector", vertices)
                kwargs_vertices = {}
                kwargs_vertices['numData'] = n_vertices
                kwargs_vertices['arrayData'] = ', '.join([' '.join(map(str, vert)) for vert in vertices.reshape(-1,3)])
                bufferData.append(templateDataPositionNormal.format(**kwargs_vertices))
                
                # Get Normals
                normals = GetLoopDataPerVertex(mesh, "NORMAL")
                all_Normals.extend(normals)
                kwargs_normals = {}
                kwargs_normals['numData'] = n_vertices
                kwargs_normals['arrayData'] = ', '.join([' '.join(map(str, norm)) for norm in normals])
                bufferData.append(templateDataPositionNormal.format(**kwargs_normals))
                
                # Get Tangents
                tangents = GetLoopDataPerVertex(mesh, "TANGENT")
                all_Tangents.extend(tangents)
                kwargs_tangents = {}
                kwargs_tangents['numData'] = n_vertices
                kwargs_tangents['arrayData'] = ','.join([' '.join(map(str, tang)) for tang in tangents])
                bufferData.append(templateDataTangent.format(**kwargs_tangents))
                
                # Initialise Buffer Formats
                bufferFormats = [templateVertexPositionBuffer, templateVertexNormalBuffer, templateVertexTangentBuffer]
                
                # Get Vertex Color
                for layer in mesh.color_attributes:
                    if not re.search('MaximumDistance|BackstopRadius|BackstopDistance|Drive|Latch', layer.name):
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
                        if i < 4 and g_weight:
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
                n_face_indices = len(mesh.polygons) * 3
                face_array = np.zeros(n_face_indices, dtype=int)
                mesh.polygons.foreach_get("vertices", face_array)
                kwargs_submesh['numIndices'] = n_face_indices
                kwargs_submesh['faceIndices'] = ' '.join(map(str, face_array))
                
                # Vertex and Index Partitions
                kwargs_submesh['vertexPartition'] = '0 ' + str(n_vertices)
                kwargs_submesh['indexPartition'] = '0 ' + str(n_face_indices)
                
                # Materials
                materials.append(mesh.materials[0].name)

                # Append submesh
                submeshes.append(templateSubMesh.format(**kwargs_submesh))
        
        # Join submeshes back together        
        JoinThem(submesh_meshes)
        meshLod = bpy.context.active_object
        mesh = meshLod.data
        
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
        kwargs_materials['simulationMaterialName'] = meshLod.name
        
        # Physical Mesh
        # Duplication and preparation
        bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
        physicalMesh = bpy.context.active_object
        physics_mesh = physicalMesh.data
        n_groups, driveDataGraphical, latchDataGraphical = cleanUpDriveLatchGroups(physicalMesh, True)
        driveLatchGroupGraphical = np.argmax(np.sum([driveDataGraphical, latchDataGraphical], axis=0), axis=1)
        drive_bool_array = np.any(latchDataGraphical > 0.3, axis = 1)
        if ".select_vert" not in physics_mesh.attributes:
            physics_mesh.attributes.new(".select_vert", "BOOLEAN", "POINT")
        physics_mesh.attributes[".select_vert"].data.foreach_set("value", drive_bool_array)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.remove_doubles()
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Get Faces and Maximum Distance Paint to Order Vertices
        #MaximumDistance
        n_vertices = len(physics_mesh.vertices)
        temp_max_dist = np.zeros(n_vertices * 4)
        physics_mesh.color_attributes["MaximumDistance"].data.foreach_get("color", temp_max_dist)
        temp_max_dist = temp_max_dist.reshape(-1,4)
        temp_check_array = np.array([CheckPhysicalPaint(x, 0.1) for x in temp_max_dist])
        temp_max_dist = temp_max_dist[:,0]
        temp_max_dist[temp_check_array & (temp_max_dist == 0)] = 0.0001
        temp_max_dist[~temp_check_array] = 0
        #Faces and Ordering
        n_face_indices = len(physics_mesh.polygons) * 3
        face_array = np.zeros(n_face_indices, dtype=int)
        physics_mesh.polygons.foreach_get("vertices", face_array)
        temp_faces_score = temp_max_dist[face_array].reshape(-1,3)
        temp_faces_nsim = np.count_nonzero(temp_faces_score, axis = 1)
        temp_faces_score = np.sum(temp_faces_score, axis = 1)  
        face_array = np.array([x for z,y,x in sorted(zip(temp_faces_nsim,temp_faces_score,face_array.reshape(-1,3)), key=lambda v: (v[0], v[1]), reverse = True)]).flatten()
        sortedVertices = list(dict.fromkeys(face_array).keys())
        # Get Final Faces Directly
        face_array = np.array([sortedVertices.index(x) for x in face_array])
        faces_final = face_array.reshape(-1,3)
        #Re-order vertices
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(physics_mesh)
        for v in bm.verts:
            v.index = sortedVertices.index(v.index)
        bm.verts.sort()
        bmesh.update_edit_mesh(physics_mesh)
        bpy.ops.object.mode_set(mode='OBJECT')
        
        kwargs_physical = {}
        physics_mesh.calc_normals_split()
        
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
        n_groups, driveDataPhysical, latchDataPhysical = cleanUpDriveLatchGroups(physicalMesh, True)
        driveLatchGroupPhysical = np.argmax(driveDataPhysical, axis=1)
        color_array = np.zeros(n_vertices * 4)
        constrainCoefficients = []
        for vc in ["MaximumDistance", "BackstopRadius", "BackstopDistance"]:
            physics_mesh.color_attributes[vc].data.foreach_get("color", color_array)
            color_array2 = color_array.reshape(-1,4)
            check_array = np.array([CheckPhysicalPaint(x, 0.1) for x in color_array2])
            color_array2 = color_array2[:,0]
            color_array2[check_array & (color_array2 == 0)] = 0.0001
            color_array2[~check_array] = 0
            if vc == "MaximumDistance": color_array2 = color_array2 * maximumMaxDistance
            constrainCoefficients.append(deepcopy(color_array2))
        constrainCoefficients = np.array(constrainCoefficients).T
        kwargs_physical['constrainCoefficients_PhysicalMesh'] = ','.join([' '.join(map(str, x)) for x in constrainCoefficients])        
                
        # Get Bone Weights and Indices
        boneIndices = []
        boneWeights = [] 
        vertex_groups = physicalMesh.vertex_groups    
        for vert in physics_mesh.vertices:
            boneIndices.append(np.full(4, numUsedBones-1, dtype=int))
            boneWeights.append(np.zeros(4, dtype=float))
            i = 0
            for g in vert.groups:
                g_weight = g.weight
                if i < 4 and g_weight:
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
        
        # Maximum Max Distance
        kwargs_physical['maximumMaxDistance'] = maximumMaxDistance
        
        # Edges Length
        edge_array = np.zeros(len(physics_mesh.edges) * 2, dtype=int)
        physics_mesh.edges.foreach_get("vertices", edge_array)
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
            kwargs_physical['physicalLods'] = ', '.join(['0 PX_MAX_U32 0 ' + str(maximumMaxDistance), str(numVertices) + ' 0 1 0'])
        
        # skinClothMap
        kwargs_lod['numImmediateClothMap'] = 0
        kwargs_lod['numSkinClothMap'] = 0
        kwargs_lod['immediateClothMap'] = ''
        kwargs_lod['skinClothMap'] = ''
        kwargs_lod['skinClothMapOffset'] = kwargs_physical['averageEdgeLength']*0.1
        kwargs_lod['physicsSubmeshPartitioning'] = ''
        kwargs_lod['numPhysicsSubmeshPartitioning'] = 0
        
        # Immediate Cloth Map
        if np.all(np.any(driveDataGraphical > 0.3, axis = 1)):
            immediate_kdtree = MakeKDTreeFromObject(physicalMesh)
            immediateClothMap = [getClosest(vert.co, immediate_kdtree, 0.001) for vert in mesh.vertices]
            kwargs_lod['numImmediateClothMap'] = len(immediateClothMap)
            kwargs_lod['immediateClothMap'] = ' '.join(map(str, immediateClothMap))
        
        # Or True Skin Cloth Map TOPERFECT   
        else:
            range_submeshes = range(numSubmesh+1)
            KDTrees = []
            for group in range(n_groups):
                KDTrees.append(MakeKDTreeFromObject(physicalMesh, np.where(driveLatchGroupPhysical == group)[0]))
            skinClothMap = []
            simulatedVertices = [[] for x in range_submeshes]
            for vert in mesh.vertices:
                drive_group = driveLatchGroupGraphical[vert.index]
                closestVert = getClosest(vert.co, KDTrees[drive_group], max_edge_length)
                closestFace = faces_final[np.where(faces_final == closestVert)[0][0]]
                if constrainCoefficients[closestVert][0]:
                    simulatedVertices[getSubmeshID(vert.index, submeshVertices)].append(vert.index)
                vertBary, normBary, tangBary = getVertexBary(vert.co, Vector((all_Normals[vert.index])), physicalMesh, closestVert, closestFace, kwargs_lod['skinClothMapOffset'], Vector((all_Tangents[vert.index][0:3])))
                skinClothMap.append([' '.join(map(str, vertBary)), closestFace[0], ' '.join(map(str, normBary)), closestFace[1], ' '.join(map(str, tangBary)), closestFace[2], vert.index])
            kwargs_lod['numSkinClothMap'] = len(skinClothMap)
            kwargs_lod['skinClothMap'] = ','.join([' '.join(map(str, x)) for x in skinClothMap])
        
            # physicsSubmeshPartitioning TOPERFECT
            simulatedVerticesFlat = np.array(simulatedVertices).flatten()
            simulatedVerticesAdditional = [[] for x in range_submeshes]
            simulatedIndices = [0 for x in range_submeshes]
            for face in mesh.polygons:
                if any(x in simulatedVerticesFlat for x in face.vertices):
                    simulatedVerticesAdditional[getSubmeshID(face.vertices[0], submeshVertices)].extend(face.vertices)
                    simulatedIndices[getSubmeshID(face.vertices[0], submeshVertices)] += 3
            simulatedVerticesAdditional = list(map(set,simulatedVerticesAdditional))    
            physicsSubmeshPartitioning = []
            for i in range_submeshes:
                physicsSubmeshPartitioning.append([i, 0, len(simulatedVertices[i]), len(simulatedVerticesAdditional[i]), simulatedIndices[i]])
            kwargs_lod['numPhysicsSubmeshPartitioning'] = len(physicsSubmeshPartitioning)
            kwargs_lod['physicsSubmeshPartitioning'] = ','.join([' '.join(map(str, x)) for x in physicsSubmeshPartitioning])
            
        # Append Per Lod information
        storedPhysicalMeshesDicts.append(kwargs_physical)
        storedPhysicalMeshes.append(physicalMesh)
        storedPhysicalMeshesFacesFinal.append(faces_final)
        storedPhysicalMeshesNormalOffsets.append(kwargs_lod['skinClothMapOffset'])
        storedPhysicalMeshesMaxEdgeLength.append(max_edge_length)
        storedPhysicalMeshesAllNormals.append(normals)
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
                for vert in storedPhysicalMeshes[i].data.vertices:
                    closestVert = getClosest(vert.co, KDTrees[target_id], storedPhysicalMeshesMaxEdgeLength[target_id])
                    closestFace = storedPhysicalMeshesFacesFinal[target_id][np.where(storedPhysicalMeshesFacesFinal[target_id] == closestVert)[0][0]]
                    vertBary, normBary = getVertexBary(vert.co, Vector((storedPhysicalMeshesAllNormals[i][vert.index])), storedPhysicalMeshes[target_id], closestVert, closestFace, storedPhysicalMeshesDicts[i]["transitionUpOffset"])
                    transitionUp.append([' '.join(map(str, vertBary)), closestFace[0], ' '.join(map(str, normBary)), closestFace[1], "PX_MAX_F32", "PX_MAX_F32", "PX_MAX_F32", closestFace[2], vert.index])
                storedPhysicalMeshesDicts[i]["numTransitionUp"] = len(transitionUp)
                storedPhysicalMeshesDicts[i]['transitionUp'] = ','.join([' '.join(map(str, x)) for x in transitionUp])
            if i:
                target_id = i - 1
                storedPhysicalMeshesDicts[i]["transitionDownThickness"] = 1
                storedPhysicalMeshesDicts[i]["transitionDownOffset"] = storedPhysicalMeshesNormalOffsets[target_id]
                transitionDown = []
                for vert in storedPhysicalMeshes[i].data.vertices:
                    closestVert = getClosest(vert.co, KDTrees[target_id], storedPhysicalMeshesMaxEdgeLength[target_id])
                    closestFace = storedPhysicalMeshesFacesFinal[target_id][np.where(storedPhysicalMeshesFacesFinal[target_id] == closestVert)[0][0]]
                    vertBary, normBary = getVertexBary(vert.co, Vector((storedPhysicalMeshesAllNormals[i][vert.index])), storedPhysicalMeshes[target_id], closestVert, closestFace, storedPhysicalMeshesDicts[i]["transitionDownOffset"])
                    transitionDown.append([' '.join(map(str, vertBary)), closestFace[0], ' '.join(map(str, normBary)), closestFace[1], "PX_MAX_F32", "PX_MAX_F32", "PX_MAX_F32", closestFace[2], vert.index])
                storedPhysicalMeshesDicts[i]["numTransitionDown"] = len(transitionDown)
                storedPhysicalMeshesDicts[i]['transitionDown'] = ','.join([' '.join(map(str, x)) for x in transitionDown])
        
        # Append Per Physical Lod information 
        physicalMeshes.append(templatePhysicalMesh.format(**storedPhysicalMeshesDicts[i]))
    
    # Delete the physical meshes  
    for me in storedPhysicalMeshes:
        bpy.data.objects.remove(me)
    
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
    if "Collision Spheres Connections" in parent_coll.collection.children and "Collision Spheres" in parent_coll.collection.children:
        connections = parent_coll.collection.children['Collision Spheres Connections'].objects
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
            capsule_name = capsule.name
            capsuleBoneName = capsule_bone_names[i]
            #Add a rigid body referenced for this bone
            numRigidBodiesReferenced[boneIndex[capsuleBoneName]] += 1
            selectOnly(capsule)
            # Separate by materials
            bpy.ops.mesh.separate(type='MATERIAL')
            spherePositions = []
            subCapsules = []
            for subCapsule in capsules:
                if capsule_name in subCapsule.name:
                    subCapsules.append(subCapsule)
                    if "Material_Sphere1" in subCapsule.data.materials or "Material_Sphere2" in subCapsule.data.materials:
                        sphereLocation, sphereRadius = applyTransforms(subCapsule, armaScale, armaRot, armaLoc, True)
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
        kwargs_bone['externalIndex'] = boneIndexInternal[bone_name]
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
    
    #%% write the template with generated values
    with open(filepath, 'w', encoding = 'utf-8') as f:
        f.write(templateClothingMain.format(**kwargs))