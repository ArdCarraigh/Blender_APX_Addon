# -*- coding: utf-8 -*-
# exporter/export_clothing.py

import bpy
from math import sqrt
from mathutils import Matrix, Euler
from statistics import mean
from io_scene_apx.exporter import template_clothing_bone, template_clothing_buffer_data, template_clothing_buffer_formats, template_clothing_graphical_mesh, template_clothing_main, template_clothing_material, template_clothing_physical_mesh, template_clothing_submesh
from io_scene_apx.exporter.template_clothing_bone import templateBone
from io_scene_apx.exporter.template_clothing_buffer_data import templateDataPositionNormal, templateDataTangent, templateDataColor, templateDataUV, templateDataBoneIndex, templateDataBoneWeight
from io_scene_apx.exporter.template_clothing_buffer_formats import templateVertexPositionBuffer, templateVertexNormalBuffer, templateVertexTangentBuffer, templateVertexColorBuffer, templateVertexUVBuffer, templateVertexBoneIndexBuffer, templateVertexBoneWeightBuffer
from io_scene_apx.exporter.template_clothing_graphical_mesh import templateGraphicalMesh
from io_scene_apx.exporter.template_clothing_main import templateClothingMain
from io_scene_apx.exporter.template_clothing_material import templateSimulationMaterial
from io_scene_apx.exporter.template_clothing_physical_mesh import templatePhysicalMesh
from io_scene_apx.exporter.template_clothing_submesh import templateSubMesh
import numpy as np
import copy
from io_scene_apx.importer import import_hairworks
from io_scene_apx.importer.import_hairworks import JoinThem
from io_scene_apx.tools import shape_hair_interp
from io_scene_apx.tools.shape_hair_interp import getConnectedVertices
from io_scene_apx.exporter import export_hairworks
from io_scene_apx.exporter.export_hairworks import getClosest

def GetLoopDataPerVertex(mesh, type, layername = None):
    vert_ids = []
    data = []
    for face in mesh.data.polygons:
        for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
            if vert_idx not in vert_ids:
                if type == "NORMAL":
                    data.append(list(mesh.data.loops[loop_idx].normal))
                elif type == "TANGENT":
                    data.append(list(mesh.data.loops[loop_idx].tangent)+[1])
                elif type == "UV":
                    data.append([mesh.data.uv_layers[layername].data[loop_idx].uv.x, mesh.data.uv_layers[layername].data[loop_idx].uv.y])
                elif type == "VERTEXCOLOR":
                    data.append(mesh.data.vertex_colors[layername].data[loop_idx].color)
                vert_ids.append(vert_idx)
    vert_ids, data = (list(t) for t in zip(*sorted(zip(vert_ids, data))))
    return(data)

def CheckPhysicalPaint(vertexColor, threshold):
    if vertexColor[1] <= vertexColor[0]+threshold and vertexColor[1] >= vertexColor[0]-threshold and vertexColor[2] <= vertexColor[0]+threshold and vertexColor[2] >= vertexColor[0]-threshold and vertexColor[2] <= vertexColor[1]+threshold and vertexColor[2] >= vertexColor[1]-threshold:
        return True
    else:
        return False
    
def Get3Bits(int):
    bits = format(int,'b')
    while len(bits)<3:
        bits = '0'+bits
    return bits

def getClosestInMesh(vertex, mesh):
    verts = []
    verts_coords = []
    #connec = getConnectedVertices(mesh, vertex, 1)
    for v in mesh.data.vertices:
        if vertex != v: # and v.index not in connec:
            verts.append(v.index)
            verts_coords.append(v.co)
    closest = getClosest(vertex.co, verts_coords)
    return verts[closest]
    
def getClosestNumber(int, intList):
    int = np.asarray(int)
    intList = np.asarray(intList)
    diff = abs(intList - int)
    return np.argmin(diff)
    
def write_clothing(context, filepath, maximumMaxDistance):
    kwargs = {}
    
    # Get transforms of the armature
    if bpy.context.active_object.parent.type == "ARMATURE":
        arma = bpy.context.active_object.parent
    elif bpy.context.active_object.type == "ARMATURE":
        arma = bpy.context.active_object
    
    # Armature
    armaScale = copy.deepcopy(arma.scale)
    armaRot = copy.deepcopy(arma.rotation_euler)
    armaLoc = copy.deepcopy(arma.location)
    usedBones = []
    boneIndex = {}
    boneIndex_value = 0
    bones = arma.data.bones
    boneNames = []
    bindPoses = []
    numMeshReferenced = []
    numRigidBodiesReferenced = []
    for bone in bones:
        usedBones.append(bone)
        numMeshReferenced.append(0)
        numRigidBodiesReferenced.append(0)
        boneNames.append(bone.name)
        boneIndex[bone.name] = boneIndex_value
        # Bind Poses Matrices
        par_mat_inv = bone.parent.matrix_local.inverted_safe() if bone.parent and bone.use_relative_parent else Matrix()
        matrix = par_mat_inv @ bone.matrix_local
        if bone.parent is not None and bone.use_relative_parent:
            matrix = bone.parent.matrix_local.inverted_safe() * bone.parent.matrix_local * matrix
        matrix.transpose()
        matrix = Matrix((matrix[0][0:3], matrix[1][0:3], matrix[2][0:3], matrix[3][0:3]))
        bindPoses.append(matrix)
        boneIndex_value += 1
    
    #Get the meshes to export
    objects = []
    if "lod0" not in arma.children[0].name:
        objects.append(arma.children[0])
    else:
        for child in arma.children:
            objects.append(child)
            
    kwargs['numPhysicalMeshes'] = len(objects)
    kwargs['numGraphicalMeshes'] = len(objects)
    
    # Get the used bones for collision volumes
    spheres = []
    capsules = []
    spheresBool = []
    capsulesBool = []
    collisionVolumesBool = []
    if "Collision Spheres" in bpy.context.view_layer.active_layer_collection.collection.children:
        spheres = bpy.context.view_layer.active_layer_collection.collection.children['Collision Spheres'].objects
        for bone in usedBones:
            spheresBool.append(bone.name in [v[v.find("_")+1:v.rfind("_")] for v in [x.name for x in spheres]])
    if "Collision Capsules" in bpy.context.view_layer.active_layer_collection.collection.children:
        capsules = bpy.context.view_layer.active_layer_collection.collection.children['Collision Capsules'].objects
        for bone in usedBones:
            capsulesBool.append(bone.name in [v[v.find("_")+1:v.rfind("_")] for v in [x.name for x in capsules]])
    
    # Get the used bones vertex groups of the first mesh (we assume lower lod levels will use the same vertex groups or less of them, but definitely not more)
    vertexGroupsBool = []
    obvg = objects[0]
    for bone in usedBones:
        if bone.name in obvg.vertex_groups:
            vg = obvg.vertex_groups[bone.name]
            vertexGroupsBool.append(any(vg.index in [g.group for g in v.groups] for v in obvg.data.vertices))
            
    usedBonesBool = np.array(vertexGroupsBool)
    if spheres:
        usedBonesBool += np.array(spheresBool)
    if capsules:
        usedBonesBool += np.array(capsulesBool)
    
    numUsedBones = np.count_nonzero(usedBonesBool) + 1
    
    boneIds = list(range(len(usedBones)))
    sortedBoneIds = list(x for y,x in sorted(zip(usedBonesBool,boneIds),key=lambda v: (v[0], -v[1]), reverse = True))
    boneIndexInternal = {}
    for bone in usedBones:
        boneIndexInternal[bone.name] = sortedBoneIds.index(boneIndex[bone.name])
        
    # For each LOD
    simulationMaterials = []
    physicalMeshes = []
    graphicalLods = []
    boundingBoxes = []
    numLod = -1
    for obj in objects:
        numLod += 1
        kwargs_materials = {}
        kwargs_lod = {}
        kwargs_lod['numLod'] = numLod
        kwargs_lod['physicalMeshId'] = numLod
        # Make and prepare a duplicate mesh
        bpy.context.view_layer.objects.active = None
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = obj
        bpy.context.active_object.select_set(state=True)
        bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
        duplicate_obj = bpy.context.active_object
        bpy.context.view_layer.objects.active = None
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = duplicate_obj
        bpy.context.active_object.select_set(state=True)
        # Apply transforms
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.context.active_object.scale = [1/x for x in armaScale]
        bpy.context.active_object.rotation_euler = [2*(np.pi)-x for x in armaRot]
        bpy.context.active_object.location = [-1*x for x in armaLoc] 
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        # Triangulate faces
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.quads_convert_to_tris(quad_method='SHORTEST_DIAGONAL', ngon_method='BEAUTY')
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.object.mode_set(mode='OBJECT')
        # Apply Drive Paint
        bpy.ops.physx.apply_drive(invert = False)
        # Split by materials
        bpy.ops.mesh.separate(type='MATERIAL')
        
        #Loop through submeshes
        submeshNames = []
        submeshes = []
        materials = []
        lodUsedBones = []
        numSubmesh = -1
        for submesh in arma.children:
            if obj.name in submesh.name and obj.name != submesh.name:
                bpy.context.view_layer.objects.active = None
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = submesh
                bpy.context.active_object.select_set(state=True)
                numSubmesh += 1
                submeshNames.append(submesh.name)
                
                #Invert active UVmap's Y-axis for Tangent computation and back
                #uvs_pre = GetLoopDataPerVertex(submesh, "UV", submesh.data.uv_layers.active.name)
                submesh.data.calc_normals_split()
                if submesh.data.uv_layers:
                    #for face in submesh.data.polygons:
                    #    for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                    #        submesh.data.uv_layers.active.data[loop_idx].uv = (1-uvs_pre[vert_idx][0], 1-uvs_pre[vert_idx][1])
                    submesh.data.calc_tangents()
                    #for face in submesh.data.polygons:
                    #    for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                    #        submesh.data.uv_layers.active.data[loop_idx].uv = uvs_pre[vert_idx]
                    
                kwargs_submesh = {}
                kwargs_submesh["numVertices"] = len(submesh.data.vertices)
                bufferData = []
                bufferFormats = []
                
                #Get data per vertex except UV and vertex color
                vertices = []
                boneIndices = []
                boneWeights = []
                for vert in submesh.data.vertices:
                    vertices.append(vert.co)
                    boneIndices.append(np.full(4, numUsedBones-1, dtype=int))
                    boneWeights.append(np.zeros(4, dtype=float))
                    i = 0
                    for g in vert.groups:
                        if i < 4 and g.weight > 0:
                            boneIndices[-1][i] = boneIndexInternal[submesh.vertex_groups[g.group].name]
                            # Add to the used bones for that mesh
                            if boneIndices[-1][i] not in lodUsedBones:
                                lodUsedBones.append(boneIndices[-1][i])
                            #Add a vertex referenced for this bone
                            numMeshReferenced[boneIndex[submesh.vertex_groups[g.group].name]] += 1
                            boneWeights[-1][i] = g.weight
                            i += 1
                normals = GetLoopDataPerVertex(submesh, "NORMAL")
                tangents = GetLoopDataPerVertex(submesh, "TANGENT")
                boneWeights = [x/np.linalg.norm(x, ord = 1) for x in boneWeights]
                                        
                # Write Vertices' Position, Normal and Tangent Buffers
                kwargs_vertices = {}
                kwargs_vertices['numData'] = len(vertices)
                kwargs_vertices['arrayData'] = ', '.join([' '.join(map(str, vert)) for vert in vertices])
                bufferData.append(templateDataPositionNormal.format(**kwargs_vertices))
                kwargs_normals = {}
                kwargs_normals['numData'] = len(normals)
                kwargs_normals['arrayData'] = ', '.join([' '.join(map(str, norm)) for norm in normals])
                bufferData.append(templateDataPositionNormal.format(**kwargs_normals))
                kwargs_tangents = {}
                kwargs_tangents['numData'] = len(tangents)
                kwargs_tangents['arrayData'] = ','.join([' '.join(map(str, tang)) for tang in tangents])
                bufferData.append(templateDataTangent.format(**kwargs_tangents))
                bufferFormats = [templateVertexPositionBuffer, templateVertexNormalBuffer, templateVertexTangentBuffer]
                
                # Get Vertex Color
                for layer in submesh.data.vertex_colors:
                    if layer.name not in ['MaximumDistance', 'BackstopRadius', 'BackstopDistance', 'Drive', 'Latch']:
                        vcol = GetLoopDataPerVertex(submesh, "VERTEXCOLOR", layer.name)
                        # Write Vertex Color Buffer
                        kwargs_vcol = {}
                        kwargs_vcol['numData'] = len(vcol)
                        kwargs_vcol['arrayData'] = ','.join([' '.join([str(int(x * 255)) for x in v]) for v in vcol])
                        bufferData.append(templateDataColor.format(**kwargs_vcol))
                        bufferFormats.append(templateVertexColorBuffer)
                        break
                    
                # Get UV Maps
                uv_index = 0
                semantic = 5
                id = 6
                for uv in submesh.data.uv_layers:
                    if semantic < 9:
                        uvs = GetLoopDataPerVertex(submesh, "UV", uv.name)
                        # Write UV Buffer
                        kwargs_uvs = {}
                        kwargs_uvs['numData'] = len(uvs)
                        kwargs_uvs['arrayData'] = ','.join([' '.join(map(str, x)) for x in uvs])
                        bufferData.append(templateDataUV.format(**kwargs_uvs))
                        kwargs_uv_buffer = {}
                        kwargs_uv_buffer['numUVBuffer'] = uv_index
                        kwargs_uv_buffer['semanticUVBuffer'] = semantic
                        kwargs_uv_buffer['idEndUVBuffer'] = id
                        bufferFormats.append(templateVertexUVBuffer.format(**kwargs_uv_buffer))
                        uv_index += 1
                        semantic += 1
                        id += 1
                        
                # Write Bone Indices
                kwargs_boneIndices = {}
                kwargs_boneIndices['numData'] = len(boneIndices)
                kwargs_boneIndices['arrayData'] = ','.join([' '.join(map(str, x)) for x in boneIndices])
                bufferData.append(templateDataBoneIndex.format(**kwargs_boneIndices))
                bufferFormats.append(templateVertexBoneIndexBuffer)
                
                # Write Bone Weights
                kwargs_boneWeights = {}
                kwargs_boneWeights['numData'] = len(boneWeights)
                kwargs_boneWeights['arrayData'] = ','.join([' '.join(map(str, x)) for x in boneWeights])
                bufferData.append(templateDataBoneWeight.format(**kwargs_boneWeights))
                bufferFormats.append(templateVertexBoneWeightBuffer)
                
                #Write Buffers
                kwargs_submesh['numBuffers'] = len(bufferFormats)
                kwargs_submesh['bufferFormats'] = '\n                              '.join(buffer for buffer in bufferFormats)
                kwargs_submesh['bufferData'] = '\n                          '.join(buffer for buffer in bufferData)
                
                # Get Faces
                faces = []
                for face in submesh.data.polygons:
                    for vert in face.vertices:
                        faces.append(vert)
                # Write Faces
                kwargs_submesh['numIndices'] = len(faces)
                kwargs_submesh['faceIndices'] = ' '.join(map(str,faces))
                
                # Vertex and Index Partitions
                kwargs_submesh['vertexPartition'] = str(0) + ' ' + str(len(vertices))
                kwargs_submesh['indexPartition'] = str(0) + ' ' + str(len(faces))
                
                # Materials
                materials.append(submesh.data.materials[0].name)

                # Append submesh
                submeshes.append(templateSubMesh.format(**kwargs_submesh))
        
        # Join submeshes back together        
        JoinThem(submeshNames)
        meshLod = bpy.context.active_object
        
        # Write submeshes and materials
        kwargs_lod['numSubMeshes'] = len(submeshes)
        kwargs_lod['subMeshes'] = '\n                '.join(x for x in submeshes)
        kwargs_lod['materials'] = '\n                '.join('<value type="String">{}</value>'.format(mat) for mat in materials)
        
        # Number of Used Bones
        kwargs_lod['numUsedBones'] = numUsedBones
        
        # LOD Bounding Box
        lodBoundingBox = list(np.array(meshLod.bound_box)[0]) + list(np.array(meshLod.bound_box)[6])
        kwargs_lod['partBounds'] = ' '.join(str(x) for x in lodBoundingBox)
        boundingBoxes.append(lodBoundingBox)
        
        # Simulation Materials
        kwargs_materials['simulationMaterialName'] = meshLod.name
        
        # Physical Mesh
        # Duplication and preparation
        bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
        physicalMesh = bpy.context.active_object
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.remove_doubles()
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.object.mode_set(mode='OBJECT')
        while physicalMesh.data.materials:
            physicalMesh.data.materials.pop(index = 0)
        driveData = GetLoopDataPerVertex(physicalMesh, "VERTEXCOLOR", layername = "Drive")
        for vert in physicalMesh.data.vertices:
            if not CheckPhysicalPaint(driveData[vert.index], 0.1):
                vert.select = True
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Get Data per Vertex
        kwargs_physical = {}
        physicalMesh.data.calc_normals_split()
        vertices = []
        boneIndices = []
        boneWeights = []
        for vert in physicalMesh.data.vertices:
            vertices.append(vert.co)
            boneIndices.append(np.full(4, numUsedBones-1, dtype=int))
            boneWeights.append(np.zeros(4, dtype=float))
            i = 0
            for g in vert.groups:
                if i < 4 and g.weight > 0:
                    boneIndices[-1][i] = boneIndexInternal[physicalMesh.vertex_groups[g.group].name]
                    boneWeights[-1][i] = g.weight
                    i += 1
        normals = GetLoopDataPerVertex(physicalMesh, "NORMAL")
        boneWeights = [x/np.linalg.norm(x, ord = 1) for x in boneWeights]
        
        # Constrain Coefficients
        maximumDistance = GetLoopDataPerVertex(physicalMesh, "VERTEXCOLOR", layername = "MaximumDistance")
        backstopRadius = GetLoopDataPerVertex(physicalMesh, "VERTEXCOLOR", layername = "BackstopRadius")
        backstopDistance = GetLoopDataPerVertex(physicalMesh, "VERTEXCOLOR", layername = "BackstopDistance")
        constrainCoefficients = []
        for vert in physicalMesh.data.vertices:
            constrainCoefficients.append(np.zeros(3, dtype=float))
            if CheckPhysicalPaint(maximumDistance[vert.index], 0.1):
                constrainCoefficients[-1][0] = maximumDistance[vert.index][0] * maximumMaxDistance
                if constrainCoefficients[-1][0] == 0:
                    constrainCoefficients[-1][0] = 0.0001 * maximumMaxDistance
            if CheckPhysicalPaint(backstopRadius[vert.index], 0.1):
                constrainCoefficients[-1][1] = backstopRadius[vert.index][0]
                if constrainCoefficients[-1][1] == 0:
                    constrainCoefficients[-1][1] = 0.0001
            if CheckPhysicalPaint(backstopDistance[vert.index], 0.1):
                constrainCoefficients[-1][2] = backstopDistance[vert.index][0]
                if constrainCoefficients[-1][2] == 0:
                    constrainCoefficients[-1][2] = 0.0001
                    
        # Get Faces to order faces and vertices
        faces = []
        for face in physicalMesh.data.polygons:
            faces.append(list(face.vertices))
            
        faces_score = []
        faces_nsim = []
        for face in faces:
            faces_score.append(0)
            faces_nsim.append(0)
            for id in face:
                faces_score[-1] += constrainCoefficients[id][0]
                if constrainCoefficients[id][0] > 0:
                    faces_nsim[-1] += 1
                
        faces_final = list(x for z,y,x in sorted(zip(faces_nsim,faces_score,faces), key=lambda v: (v[0], v[1]), reverse = True))
        
        sortedVertices = []
        faces_final_flat = list(np.array(faces_final).flat)
        for id in faces_final_flat:
            if id not in sortedVertices:
                sortedVertices.append(id)
                        
        kwargs_physical['numVertices_PhysicalMesh'] = len(vertices)
        kwargs_physical['vertices_PhysicalMesh'] = ', '.join([' '.join(map(str, vertices[sortedVertices[x]])) for x in range(len(vertices))])
        kwargs_physical['normals_PhysicalMesh'] = ', '.join([' '.join(map(str, normals[sortedVertices[x]])) for x in range(len(normals))])
        kwargs_physical['skinningNormals_PhysicalMesh'] = ', '.join([' '.join(map(str, normals[sortedVertices[x]])) for x in range(len(normals))])
        kwargs_physical['numBoneIndices_PhysicalMesh'] = len(boneIndices)*4
        kwargs_physical['boneIndices_PhysicalMesh'] = ' '.join([' '.join(map(str, boneIndices[sortedVertices[x]])) for x in range(len(boneIndices))])
        kwargs_physical['boneWeights_PhysicalMesh'] = ' '.join([' '.join(map(str, boneWeights[sortedVertices[x]])) for x in range(len(boneWeights))])        
        kwargs_physical['constrainCoefficients_PhysicalMesh'] = ','.join([' '.join(map(str, constrainCoefficients[sortedVertices[x]])) for x in range(len(constrainCoefficients))])
        
        # OptimizationData
        optimizationData = []
        for i in range(0,len(physicalMesh.data.vertices),2):
            opt1 = np.count_nonzero(boneWeights[sortedVertices[i]])
            opt2 = np.count_nonzero(boneWeights[sortedVertices[i+1]]) if i+1 < len(boneWeights) else 0
            byte = "0" + Get3Bits(opt2) + "0" + Get3Bits(opt1)
            optimizationData.append(byte)
        
        kwargs_physical['numOptimizationData'] = len(optimizationData)
        kwargs_physical['optimizationData'] = ' '.join(str(int(x,2)) for x in optimizationData)
                
        # Write Faces
        kwargs_physical['numFaceIndices_PhysicalMesh'] = len(faces_final_flat)
        kwargs_physical['faceIndices_PhysicalMesh'] = ' '.join(map(str,[sortedVertices.index(x) for x in faces_final_flat]))
        
        # Maximum Max Distance
        kwargs_physical['maximumMaxDistance'] = maximumMaxDistance
        
        # Edges Length
        edgesLength = []
        for face in physicalMesh.data.polygons:
            for edge in face.edge_keys:
                vert1_coord = physicalMesh.data.vertices[edge[0]].co
                vert2_coord = physicalMesh.data.vertices[edge[1]].co
                edgesLength.append(sqrt((vert1_coord[0]-vert2_coord[0])**2 + (vert1_coord[1]-vert2_coord[1])**2 + (vert1_coord[2]-vert2_coord[2])**2))
        kwargs_physical['shortestEdgeLength'] = min(edgesLength)
        kwargs_physical['averageEdgeLength'] = mean(edgesLength)
        
        #Physical Submesh and Lods
        kwargs_physical['subMeshes_PhysicalMesh'] = ''
        kwargs_physical['numSubMeshes_PhysicalMesh'] = 0
        kwargs_physical['numPhysicalLods'] = 1
        kwargs_physical['physicalLods'] = ' '.join(map(str,[0, 'PX_MAX_U32', 0, 0]))
        numVertices = 0
        numIndices = np.count_nonzero(faces_nsim) * 3
        if numIndices > 0:
            simFaces = faces_final_flat[0:numIndices]
            numVertices = len(set(simFaces))
            numMaxDistance0 = numVertices - np.count_nonzero([x[0] for x in constrainCoefficients])
            kwargs_physical['numSubMeshes_PhysicalMesh'] = 1
            kwargs_physical['subMeshes_PhysicalMesh'] = ' '.join(map(str,[numIndices, numVertices, numMaxDistance0]))
            kwargs_physical['numPhysicalLods'] = 2
            kwargs_physical['physicalLods'] = ', '.join([' '.join(map(str,[0, 'PX_MAX_U32', 0, maximumMaxDistance])), ' '.join(map(str,[numVertices, 0, 1, 0]))])
        
        #Transition UP/Down TODO
        
        # skinClothMap TODO
        kwargs_lod['numImmediateClothMap'] = 0
        kwargs_lod['numSkinClothMap'] = 0
        kwargs_lod['immediateClothMap'] = ''
        kwargs_lod['skinClothMap'] = ''
        kwargs_lod['skinClothMapOffset'] = kwargs_physical['averageEdgeLength']/10
        
        driveDataMeshLod = GetLoopDataPerVertex(meshLod, "VERTEXCOLOR", layername = "Drive")
        if all([CheckPhysicalPaint(driveDataMeshLod[vert.index], 0.1) for vert in meshLod.data.vertices]):
            immediateClothMap = [sortedVertices.index(getClosestInMesh(vert, physicalMesh))for vert in meshLod.data.vertices]
            kwargs_lod['numImmediateClothMap'] = len(immediateClothMap)
            kwargs_lod['immediateClothMap'] = ' '.join(map(str, immediateClothMap))
        
        # physicsSubmeshPartitioning TODO
        kwargs_lod['physicsSubmeshPartitioning'] = ''
        kwargs_lod['numPhysicsSubmeshPartitioning'] = 0

        # Append Per Lod information
        physicalMeshes.append(templatePhysicalMesh.format(**kwargs_physical))
        graphicalLods.append(templateGraphicalMesh.format(**kwargs_lod))
        simulationMaterials.append(templateSimulationMaterial.format(**kwargs_materials))
        
        # Delete the duplicate meshes
        for me in [meshLod, physicalMesh]:
            bpy.context.view_layer.objects.active = None
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = me
            bpy.context.active_object.select_set(state=True)
            bpy.ops.object.delete(use_global=False, confirm=False)
    
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
    sphereIndex_value = 0
    sphereBoneIndex = []
    sphereRadius = []
    sphereVec3 = []
    sphereAll = []
    if len(spheres) > 0:
        for sphere in spheres:
            bpy.context.view_layer.objects.active = None
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = sphere
            bpy.context.active_object.select_set(state=True)
            sphereIndex[sphere.name] = sphereIndex_value
            sphereIndex_value += 1
            sphereBoneName = sphere.name[sphere.name.find("_")+1:sphere.name.rfind("_")]
            sphereBoneIndex.append(boneIndexInternal[sphereBoneName])
            #Add a rigid body referenced for this bone
            numRigidBodiesReferenced[boneIndex[sphereBoneName]] += 1
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            sphere.scale = [1/x for x in armaScale]
            sphere.rotation_euler = [2*(np.pi)-x for x in armaRot]
            sphere.location = [-1*x for x in armaLoc]
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='MEDIAN')
            vert_coord = sphere.data.vertices[0].co
            sphereRadius.append(sqrt((vert_coord[0])**2 + (vert_coord[1])**2 + (vert_coord[2])**2))
            sphereWorldVec = sphere.matrix_world.translation
            boneMatrix = bones[sphereBoneName].matrix_local
            sphereVec3.append(boneMatrix.inverted() @ sphereWorldVec)
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
            sphere.scale = armaScale
            sphere.rotation_euler = armaRot
            sphere.location = armaLoc
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            
        for i in range(len(sphereBoneIndex)):
            sphereAll.append([sphereBoneIndex[i], sphereRadius[i], sphereVec3[i][0], sphereVec3[i][1], sphereVec3[i][2]])
        
        kwargs['numBoneSpheres'] = len(spheres)
        kwargs['boneSpheres'] = ','.join(' '.join(map(str, x)) for x in sphereAll)
        
    # BoneSphereConnections
    kwargs['numBoneSphereConnections'] = "0"
    kwargs['boneSphereConnections'] = ""
    boneSphereConnections = []
    if "Collision Spheres Connections" and "Collision Spheres" in bpy.context.view_layer.active_layer_collection.collection.children:
        connections = bpy.context.view_layer.active_layer_collection.collection.children['Collision Spheres Connections'].objects
        if len(connections) > 0:
            for connection in connections:
                sphereName1 = connection.name[:connection.name.find("_to_")]
                sphereName2 = connection.name[connection.name.find("_to_")+4:]
                boneSphereConnections.append([sphereIndex[sphereName1], sphereIndex[sphereName2]])
                
            kwargs['numBoneSphereConnections'] = len(connections) * 2
            kwargs['boneSphereConnections'] = ' '.join(' '.join(map(str,x)) for x in boneSphereConnections)
            
    # BoneCapsules
    kwargs['numBoneActors'] = 0
    kwargs['boneActors'] = ""
    capsuleBoneIndex = []
    capsuleRadius = []
    capsuleHeight = []
    capsuleMatrices = []
    capsuleAll = []
    if len(capsules) > 0:
        for capsule in capsules:
            bpy.context.view_layer.objects.active = None
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = capsule
            bpy.context.active_object.select_set(state=True)
            capsuleRot = copy.deepcopy(capsule.rotation_euler)
            capsuleRotation = Euler([x - y for (x, y) in zip(capsuleRot, armaRot)])
            bpy.context.view_layer.objects.active = None
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = capsule
            bpy.context.active_object.select_set(state=True)
            capsuleBoneName = capsule.name[capsule.name.find("_")+1:capsule.name.rfind("_")]
            capsuleBoneIndex.append(boneIndexInternal[capsuleBoneName])
            #Add a rigid body referenced for this bone
            numRigidBodiesReferenced[boneIndex[capsuleBoneName]] += 1
            # Separate by materials
            bpy.ops.mesh.separate(type='MATERIAL')
            spherePositions = []
            subCapsuleNames = []
            for subCapsule in capsules:
                if capsule.name in subCapsule.name:
                    subCapsuleNames.append(subCapsule.name)
                    if "Material_Sphere1" in subCapsule.data.materials or "Material_Sphere2" in subCapsule.data.materials:
                        bpy.context.view_layer.objects.active = None
                        bpy.ops.object.select_all(action='DESELECT')
                        bpy.context.view_layer.objects.active = subCapsule
                        bpy.context.active_object.select_set(state=True)
                        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                        subCapsule.scale = [1/x for x in armaScale]
                        subCapsule.rotation_euler = [2*(np.pi)-x for x in armaRot]
                        subCapsule.location = [-1*x for x in armaLoc]
                        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='MEDIAN')
                        if "capsuleRad" not in locals():
                            vert_coord = subCapsule.data.vertices[0].co
                            capsuleRad = sqrt((vert_coord[0])**2 + (vert_coord[1])**2 + (vert_coord[2])**2)
                            capsuleRadius.append(capsuleRad)
                        spherePositions.append(copy.deepcopy(subCapsule.matrix_world.translation))
                        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
                        subCapsule.scale = armaScale
                        subCapsule.rotation_euler = armaRot
                        subCapsule.location = armaLoc
                        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            if "capsuleRad" in locals():
                del(capsuleRad)     
            JoinThem(subCapsuleNames)
            capsuleHeight.append(sqrt((spherePositions[0][0]-spherePositions[1][0])**2 + (spherePositions[0][1]-spherePositions[1][1])**2 + (spherePositions[0][2]-spherePositions[1][2])**2))
            capsulePosition = [(x+y)/2 for (x, y) in zip(spherePositions[0], spherePositions[1])]
            capsuleMat = capsuleRotation.to_matrix().to_4x4()
            capsuleMat.col[3] = capsulePosition + [1]
            boneMatrix = bones[capsuleBoneName].matrix_local
            capsuleMatLocal = boneMatrix.inverted() @ capsuleMat
            capsuleMatLocal = Matrix((capsuleMatLocal.col[0][0:3], capsuleMatLocal.col[1][0:3], capsuleMatLocal.col[2][0:3], capsuleMatLocal.col[3][0:3]))
            capsuleMatrices.append(capsuleMatLocal)
            
        for i in range(len(capsuleBoneIndex)):
            capsuleAll.append([capsuleBoneIndex[i], 0, 0, capsuleRadius[i], capsuleHeight[i], ' '.join(map(str, np.array(capsuleMatrices[i]).flat))])
        
        kwargs['numBoneActors'] = len(capsules)
        kwargs['boneActors'] = ','.join(' '.join(map(str, x)) for x in capsuleAll)
    
    # Bone Parents
    boneParents = []  
    for bone in usedBones:
        if bone.parent is not None:
            boneParents.append(boneIndexInternal[bone.parent.name])
        else:
            boneParents.append(-1)
            
    # Write armature
    boneDefinitions = []
    bonesReferenced = 0
    bonesReferencedByMesh = 0
    for bone in usedBones:
        kwargs_bone = {}
        kwargs_bone['internalIndex'] = boneIndexInternal[bone.name]
        kwargs_bone['externalIndex'] = boneIndexInternal[bone.name]
        kwargs_bone['numMeshReferenced'] = numMeshReferenced[boneIndex[bone.name]]
        kwargs_bone['numRigidBodiesReferenced'] = numRigidBodiesReferenced[boneIndex[bone.name]]
        kwargs_bone['parentIndex'] = boneParents[boneIndex[bone.name]]
        kwargs_bone['bindPose'] = ' '.join(map(str, np.array(bindPoses[boneIndex[bone.name]]).flat))
        kwargs_bone['boneName'] = boneNames[boneIndex[bone.name]]
        boneDefinitions.append(kwargs_bone)
        if numMeshReferenced[boneIndex[bone.name]]>0 or numRigidBodiesReferenced[boneIndex[bone.name]]>0:
            bonesReferenced += 1
        if numMeshReferenced[boneIndex[bone.name]]>0:
            bonesReferencedByMesh += 1
    sortedBoneDefinitions = sorted(boneDefinitions, key=lambda v: v['internalIndex'])
        
    # Write the armature in the main template
    kwargs['numBones'] = len(boneDefinitions)
    kwargs['bones'] = '\n      '.join(templateBone.format(**x) for x in sortedBoneDefinitions)
    kwargs['bonesReferenced'] = bonesReferenced
    kwargs['bonesReferencedByMesh'] = bonesReferencedByMesh
    kwargs['rootBoneIndex'] = boneIndexInternal[usedBones[0].name]
    
    #%% write the template with generated values
    with open(filepath, 'w', encoding = 'utf-8') as f:
        f.write(templateClothingMain.format(**kwargs))