# -*- coding: utf-8 -*-
# clothing.py

import bpy
import math
import random
from bpy_extras.object_utils import object_data_add
from mathutils import Vector, Matrix
from io_import_apx import number_to_words
from io_import_apx.number_to_words import process, getWords

def read_clothing(context, filepath, rm_db, use_mat, rotate_180, minimal_armature):

    with open(filepath, 'r', encoding='utf-8') as file:
        
        ## Physical ##
        for line in file:
            if 'array name="physicalMeshes"' in line:
                temp16 = line.split()
                physicalMeshes_count = temp16[2][6:-1]
                physicalMeshes_names = []
                physicalMeshes_boneIndices_all = []
                physicalMeshes_boneWeights_all = []
                break
        
        # For all physical meshes
        for w in range(int(physicalMeshes_count)):
            
            # Vertices
            for line in file:
                if 'array name="vertices"' in line:
                    vertices = []
                    break
            for line in file:
                if '/array' in line:
                    for j in range(len(vertices)):
                        if "," in vertices[j]:
                            l = len(vertices[j])
                            vertices[j] = vertices[j][:l - 1]
                    break
                temp17 = line.split()
                for i in temp17:
                    vertices.append(i)
                        
            # Normals
            for line in file:
                if 'array name="normals"' in line:
                    normals = []
                    break
            for line in file:
                if '/array' in line:
                    for j in range(len(normals)):
                        if "," in normals[j]:
                            l = len(normals[j])
                            normals[j] = normals[j][:l - 1]
                    break
                temp18 = line.split()
                for i in temp18:
                    normals.append(i)
                        
            # Skinning Normals ??
            for line in file:
                if 'array name="skinningNormals"' in line:
                    skinningNormals = []
                    break
            for line in file:
                if '/array' in line:
                    for j in range(len(skinningNormals)):
                        if "," in skinningNormals[j]:
                            l = len(skinningNormals[j])
                            skinningNormals[j] = skinningNormals[j][:l - 1]
                    break
                temp19 = line.split()
                for i in temp19:
                    skinningNormals.append(i)
                        
            # Constrain Coefficients
            for line in file:
                if 'array name="constrainCoefficients"' in line:
                    constrainCoefficients = []
                    break
            for line in file:
                if '/array' in line:
                    list_coma = []
                    n = 0
                    for j in range(len(constrainCoefficients)):
                        if "," in constrainCoefficients[j]:
                            list_coma.append(j)
                    for k in list_coma:
                        constrainCoefficients.insert(k + n + 1, constrainCoefficients[k + n][constrainCoefficients[k + n].find(",") + 1:len(constrainCoefficients[k + n])])
                        constrainCoefficients[k + n] = constrainCoefficients[k + n][:constrainCoefficients[k + n].find(",")]
                        n += 1
                    constrainCoefficients2 = list(filter(None, constrainCoefficients))
                    break
                temp20 = line.split()
                for i in temp20:
                    constrainCoefficients.append(i)
                    
            # Bone Indices
            for line in file:
                if 'array name="boneIndices"' in line:
                    boneIndices = []
                    break
            for line in file:
                if '/array' in line:
                    break
                temp21 = line.split()
                for i in temp21:
                    boneIndices.append(i)
                    
            # Bone Weights
            for line in file:
                if 'array name="boneWeights"' in line:
                    boneWeights = []
                    break
            for line in file:
                if '/array' in line:
                    break
                temp22 = line.split()
                for i in temp22:
                    boneWeights.append(i)
                    
            # Optimization Data ??
            for line in file: 
                if 'array name="optimizationData"' in line:
                    break
                
            # Face Indices
            for line in file:
                if 'array name="indices"' in line:
                    indices = []
                    break
            for line in file:
                if '/array' in line:
                    break
                temp23 = line.split()
                for i in temp23:
                    indices.append(i)
                    
            # Maximum MaximumDistance Value
            for line in file:
                if 'value name="maximumMaxDistance"' in line:
                    temp24 = line.split()
                    maximumMaxDistance = temp24[2][11:len(temp24[2])-8]
                    break
                    
            # Creation of the physical meshes
            verts = []
            for i in range(0,len(vertices), 3):
                verts.append(Vector((float(vertices[i]), float(vertices[i+1]), float(vertices[i+2]))))
            edges = []
            faces = []
            for i in range(0,len(indices), 3):
                faces.append([int(indices[i]), int(indices[i+1]),int(indices[i+2])])
                    
            normals2 = []
            for i in range(0, len(normals), 3):
                normals2.append(Vector([float(normals[i]), float(normals[i+1]), float(normals[i+2])]))
            
            # Prepare Clothing Paints
            clothingPaints = []
            for i in range(0, len(constrainCoefficients2), 3):
                clothingPaints.append([(float(constrainCoefficients2[i])/float(maximumMaxDistance)), float(constrainCoefficients2[i+1]), float(constrainCoefficients2[i+2])])
                
            maximumDistance = []
            backstopRadius = []
            backstopDistance = []
            for i in range(len(clothingPaints)):
                maximumDistance.append([clothingPaints[i][0], clothingPaints[i][0], clothingPaints[i][0], 1])
                backstopRadius.append([clothingPaints[i][1], clothingPaints[i][1], clothingPaints[i][1], 1])
                backstopDistance.append([clothingPaints[i][2], clothingPaints[i][2], clothingPaints[i][2], 1])
                
            # Add the mesh to the scene
            mesh = bpy.data.meshes.new(name="PMesh_lod"+str(w))
            mesh.from_pydata(verts, edges, faces)
            for i in mesh.polygons:
                i.use_smooth = True
            object_data_add(context, mesh)
            
            # Normals #Looks like this part is kinda useless
            mesh.calc_normals()
            for i in range(len(mesh.vertices)):
                mesh.vertices[i].normal = normals2[i]
            for face in mesh.polygons:
                for vert in [mesh.loops[i] for i in face.loop_indices]:
                    vert.normal = normals2[vert.vertex_index]
                    
            # Apply Clothing Paints
            mesh.vertex_colors.new(name="MaximumDistance")
            for face in mesh.polygons:
                for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                    if maximumDistance[vert_idx][0] == 0:
                        mesh.vertex_colors["MaximumDistance"].data[loop_idx].color = [1,0,1,1]
                    else:
                        mesh.vertex_colors["MaximumDistance"].data[loop_idx].color = maximumDistance[vert_idx]
                        
            mesh.vertex_colors.new(name="BackstopRadius")
            for face in mesh.polygons:
                for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                    if backstopRadius[vert_idx][0] == 0:
                        mesh.vertex_colors["BackstopRadius"].data[loop_idx].color = [1,0,1,1]
                    else:
                        mesh.vertex_colors["BackstopRadius"].data[loop_idx].color = backstopRadius[vert_idx]
                        
            mesh.vertex_colors.new(name="BackstopDistance")
            for face in mesh.polygons:
                for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                    if backstopDistance[vert_idx][0] == 0:
                        mesh.vertex_colors["BackstopDistance"].data[loop_idx].color = [1,0,1,1]
                    else:
                        mesh.vertex_colors["BackstopDistance"].data[loop_idx].color = backstopDistance[vert_idx] 

            # Rotation of the mesh if requested
            if rotate_180 == True:
                bpy.context.active_object.rotation_euler[2] = math.radians(180)
                
            # Get the actual mesh name in a list
            physicalMeshes_names.append(bpy.context.active_object.name)

            # Creation of bones indices and weights list for all lods
            boneIndices3 = []
            for i in range(0, len(boneIndices), 4):
                boneIndices3.append([int(boneIndices[i]), int(boneIndices[i+1]), int(boneIndices[i+2]),
                                    int(boneIndices[i+3])])
            boneWeights3 = []
            for i in range(0, len(boneWeights), 4):
                boneWeights3.append([float(boneWeights[i]), float(boneWeights[i+1]), float(boneWeights[i+2]),
                                    float(boneWeights[i+3])])
            physicalMeshes_boneIndices_all.append(boneIndices3)
            physicalMeshes_boneWeights_all.append(boneWeights3)
            
        
        ## Graphical ##
        SEMANTIC_POSITION = False
        SEMANTIC_NORMAL = False
        SEMANTIC_TANGENT = False
        SEMANTIC_BINORMAL = False
        SEMANTIC_COLOR = False
        SEMANTIC_TEXCOORD0 = False
        SEMANTIC_BONE_INDEX = False
        SEMANTIC_BONE_WEIGHT = False
        DCC_INDEX = False
        for line in file:
            # Just to go at the place I'm intesrested in
            if 'array name="graphicalLods"' in line:
                temp13 = line.split()
                lod_count = temp13[2][6:-1]
                lod_mesh_names = []
                lod_boneIndices_all = []
                lod_boneWeights_all = []
                lod_materials_all = []
                break

        # For all the LODs
        for z in range(int(lod_count)):
            for line in file:
                if 'value name="lod"' in line:
                    temp12 = line.split()
                    lod_number = temp12[2][11:len(temp12[2]) - 8]
                    SEMANTIC_TEXCOORDs = 0
                    break
            for line in file:
                if 'array name="submeshes"' in line:
                    temp11 = line.split()
                    submeshes_count = temp11[2][6:-1]
                    mesh_names = []
                    boneIndices_all = []
                    boneWeights_all = []
                    materials_all = []
                    break
            for line in file:
                if '<value name="name" type="String">SEMANTIC_POSITION</value>' in line:
                    SEMANTIC_POSITION = True
                if '<value name="name" type="String">SEMANTIC_NORMAL</value>' in line:
                    SEMANTIC_NORMAL = True
                if '<value name="name" type="String">SEMANTIC_TANGENT</value>' in line:
                    SEMANTIC_TANGENT = True
                if '<value name="name" type="String">SEMANTIC_BINORMAL</value>' in line:
                    SEMANTIC_BINORMAL = True
                if '<value name="name" type="String">SEMANTIC_COLOR</value>' in line:
                    SEMANTIC_COLOR = True
                if '<value name="name" type="String">SEMANTIC_TEXCOORD' in line:
                    SEMANTIC_TEXCOORD0 = True
                    SEMANTIC_TEXCOORDs += 1
                if '<value name="name" type="String">SEMANTIC_BONE_INDEX</value>' in line:
                    SEMANTIC_BONE_INDEX = True
                if '<value name="name" type="String">SEMANTIC_BONE_WEIGHT</value>' in line:
                    SEMANTIC_BONE_WEIGHT = True
                if '<value name="name" type="String">DCC_INDEX</value>' in line:
                    DCC_INDEX = True
                if '</array>' in line:
                    break

            # For all Submeshes in the LOD
            for x in range(int(submeshes_count)):

                # Vertices
                if SEMANTIC_POSITION == True:
                    for line in file:
                        if 'array name="data"' in line:
                            vertices = []
                            break
                    for line in file:
                        if '/array' in line:
                            for j in range(len(vertices)):
                                if "," in vertices[j]:
                                    l = len(vertices[j])
                                    vertices[j] = vertices[j][:l - 1]
                            break
                        temp = line.split()
                        for i in temp:
                            vertices.append(i)

                # Normals
                if SEMANTIC_NORMAL == True:
                    for line in file:
                        if 'array name="data"' in line:
                            normals = []
                            break
                    for line in file:
                        if '/array' in line:
                            for j in range(len(normals)):
                                if "," in normals[j]:
                                    l = len(normals[j])
                                    normals[j] = normals[j][:l - 1]
                            break
                        temp2 = line.split()
                        for i in temp2:
                            normals.append(i)

                # Tangents
                if SEMANTIC_TANGENT == True:
                    for line in file:
                        if 'array name="data"' in line:
                            tangents = []
                            break
                    for line in file:
                        if '/array' in line:
                            list_coma = []
                            n = 0
                            for j in range(len(tangents)):
                                if "," in tangents[j]:
                                    list_coma.append(j)
                            for k in list_coma:
                                tangents.insert(k + n + 1, tangents[k + n][tangents[k + n].find(",") + 1:len(tangents[k + n])])
                                tangents[k + n] = tangents[k + n][:tangents[k + n].find(",")]
                                n += 1
                            tangents2 = list(filter(None, tangents))
                            break
                        temp3 = line.split()
                        for i in temp3:
                            tangents.append(i)

                # Binormals
                if SEMANTIC_BINORMAL == True:
                    for line in file:
                        if 'array name="data"' in line:
                            break

                # Vertex Color
                if SEMANTIC_COLOR == True:
                    for line in file:
                        if 'array name="data"' in line:
                            vertex_color = []
                            break
                    for line in file:
                        if '/array' in line:
                            list_coma = []
                            n = 0
                            for j in range(len(vertex_color)):
                                if "," in vertex_color[j]:
                                    list_coma.append(j)
                            for k in list_coma:
                                vertex_color.insert(k + n + 1, vertex_color[k + n][vertex_color[k + n].find(",") + 1:len(vertex_color[k + n])])
                                vertex_color[k + n] = vertex_color[k + n][:vertex_color[k + n].find(",")]
                                n += 1
                            vertex_color2 = list(filter(None, vertex_color))
                            break
                        temp14 = line.split()
                        for i in temp14:
                            vertex_color.append(i)

                # UVmaps
                if SEMANTIC_TEXCOORD0 == True:
                    texCoords_all = []
                    for u in range(SEMANTIC_TEXCOORDs):
                        for line in file:
                            if 'array name="data"' in line:
                                texCoords = []
                                break
                        for line in file:
                            if '/array' in line:
                                list_coma = []
                                n = 0
                                for j in range(len(texCoords)):
                                    if "," in texCoords[j]:
                                        list_coma.append(j)
                                for k in list_coma:
                                    texCoords.insert(k + n + 1, texCoords[k + n][texCoords[k + n].find(",") + 1:len(texCoords[k + n])])
                                    texCoords[k + n] = texCoords[k + n][:texCoords[k + n].find(",")]
                                    n += 1
                                texCoords2 = list(filter(None, texCoords))
                                break
                            temp4 = line.split()
                            for i in temp4:
                                texCoords.append(i)
                        texCoords_all.append(texCoords2)

                # Bone indices
                if SEMANTIC_BONE_INDEX == True:
                    for line in file:
                        if 'array name="data"' in line:
                            boneIndices = []
                            break
                    for line in file:
                        if '/array' in line:
                            list_coma = []
                            n = 0
                            for j in range(len(boneIndices)):
                                if "," in boneIndices[j]:
                                    list_coma.append(j)
                            for k in list_coma:
                                boneIndices.insert(k + n + 1, boneIndices[k + n][boneIndices[k + n].find(",") + 1:len(boneIndices[k + n])])
                                boneIndices[k + n] = boneIndices[k + n][:boneIndices[k + n].find(",")]
                                n += 1
                            boneIndices2 = list(filter(None, boneIndices))
                            break
                        temp5 = line.split()
                        for i in temp5:
                            boneIndices.append(i)

                # Bone weights
                if SEMANTIC_BONE_WEIGHT == True:
                    for line in file:
                        if 'array name="data"' in line:
                            boneWeights = []
                            break
                    for line in file:
                        if '/array' in line:
                            list_coma = []
                            n = 0
                            for j in range(len(boneWeights)):
                                if "," in boneWeights[j]:
                                    list_coma.append(j)
                            for k in list_coma:
                                boneWeights.insert(k + n + 1, boneWeights[k + n][boneWeights[k + n].find(",") + 1:len(boneWeights[k + n])])
                                boneWeights[k + n] = boneWeights[k + n][:boneWeights[k + n].find(",")]
                                n += 1
                            boneWeights2 = list(filter(None, boneWeights))
                            break
                        temp6 = line.split()
                        for i in temp6:
                            boneWeights.append(i)

                # DCC_INDEX ??
                if DCC_INDEX == True:
                    for line in file:
                        if 'array name="data"' in line:
                            break

                # Faces Indices
                for line in file:
                    if 'array name="indexBuffer"' in line:
                        indices = []
                        break
                for line in file:
                    if '/array' in line:
                        break
                    temp7 = line.split()
                    for i in temp7:
                        indices.append(i)


                # Creation of the graphical meshes
                verts = []
                for i in range(0,len(vertices), 3):
                    verts.append(Vector((float(vertices[i]), float(vertices[i+1]), float(vertices[i+2]))))
                edges = []
                faces = []
                for i in range(0,len(indices), 3):
                    faces.append([int(indices[i]), int(indices[i+1]),int(indices[i+2])])
                    
                normals2 = []
                for i in range(0, len(normals), 3):
                    normals2.append(Vector([float(normals[i]), float(normals[i+1]), float(normals[i+2])]))
                tangents3 = []
                for i in range(0, len(tangents2), 4):
                    tangents3.append(Vector([float(tangents2[i]), float(tangents2[i + 1]), float(tangents2[i + 2])]))
                bitangent_sign0 = []
                for i in range(0, len(tangents2), 4):
                    bitangent_sign0.append(float(tangents2[i+3]))
                    
                if SEMANTIC_COLOR == True:
                    vertex_color3 = []
                    for i in range(0, len(vertex_color2), 4):
                        vertex_color3.append([float(vertex_color2[i])/255, float(vertex_color2[i + 1])/255, float(vertex_color2[i + 2])/255, float(vertex_color2[i + 3])/255])
                        
                texCoords2_all = []
                for u in range(SEMANTIC_TEXCOORDs):
                    texCoords3 = []
                    for i in range(0,len(texCoords_all[u]), 2):
                        texCoords3.append([float(texCoords_all[u][i]), float(texCoords_all[u][i+1])])
                    texCoords2_all.append(texCoords3)

                # Add the mesh to the scene
                mesh = bpy.data.meshes.new(name="GMesh_lod"+str(lod_number))
                mesh.from_pydata(verts, edges, faces)
                for i in mesh.polygons:
                    i.use_smooth = True
                object_data_add(context, mesh)

                # UVmaps creation
                uvmap_names = []
                for i in range(SEMANTIC_TEXCOORDs):
                    uvmap_names.append(getWords(i+1)+'UV')
                for i in range(len(uvmap_names)):
                    mesh.uv_layers.new(name=uvmap_names[i])
                    for face in mesh.polygons:
                        for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                            mesh.uv_layers.active.data[loop_idx].uv = (texCoords2_all[i][vert_idx][0], texCoords2_all[i][vert_idx][1])
                            
                # Tangent and Normals #Looks like this part is kinda useless
                mesh.calc_normals()
                for i in range(len(mesh.vertices)):
                    mesh.vertices[i].normal = normals2[i]
                mesh.calc_tangents()
                for face in mesh.polygons:
                    for vert in [mesh.loops[i] for i in face.loop_indices]:
                        vert.normal = normals2[vert.vertex_index]
                        #Read-only... :(
                        #vert.tangent = tangents3[vert.vertex_index]
                        #vert.bitangent_sign = bitangent_sign0[vert.vertex_index]
                        
                # Vertex Color
                mesh.vertex_colors.new()
                for face in mesh.polygons:
                    for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                        if SEMANTIC_COLOR == False:
                            mesh.vertex_colors.active.data[loop_idx].color = (0, 0, 0, 1)
                        else:
                            mesh.vertex_colors.active.data[loop_idx].color = vertex_color3[vert_idx]

                # Rotation of the mesh if requested
                if rotate_180 == True:
                    bpy.context.active_object.rotation_euler[2] = math.radians(180)

                # Get the actual mesh name in a list
                mesh_names.append(bpy.context.active_object.name)

                # Creation of bones indices and weights list for all submeshes
                boneIndices3 = []
                for i in range(0, len(boneIndices2), 4):
                    boneIndices3.append([int(boneIndices2[i]), int(boneIndices2[i+1]), int(boneIndices2[i+2]),
                                        int(boneIndices2[i+3])])
                boneWeights3 = []
                for i in range(0, len(boneWeights2), 4):
                    boneWeights3.append([float(boneWeights2[i]), float(boneWeights2[i+1]), float(boneWeights2[i+2]),
                                        float(boneWeights2[i+3])])
                boneIndices_all.append(boneIndices3)
                boneWeights_all.append(boneWeights3)

            # Materials
            for line in file:
                if 'array name="materialNames"' in line:
                    break
            for line in file:
                if '/array' in line:
                    break
                temp15 = line.split()
                material_name = temp15[1][14:-8]
                if "::" in material_name:
                    material_name = material_name[material_name.find("::")+2:]
                materials_all.append(material_name)

            # Creation of list for all lods
            lod_mesh_names.append(mesh_names)
            lod_boneIndices_all.append(boneIndices_all)
            lod_boneWeights_all.append(boneWeights_all)
            lod_materials_all.append(materials_all)

        # Bone Count
        for line in file:
            if 'value name="boneCount"' in line:
                temp8 = line.split()
                bone_count = temp8[2][11:len(temp8[2])-8]
                break

        # Armature and Bones
        for line in file:
            if 'array name="bones"' in line:
                skeleton = bpy.data.armatures.new(name="Armature")
                object_data_add(context, skeleton)
                boneIndexation = {}
                boneMatrices = {}
                # Edit mode required to add bones to the armature
                bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                break
        for line in file:
            if 'value name="internalIndex"' in line:
                temp9 = line.split()
                bone_index_internal = temp9[2][11:len(temp9[2])-8]
                if minimal_armature == True:
                    if int(bone_index_internal) > int(bone_count)-1:
                        break
            if 'value name="bindPose"' in line:
                bind_pose = line.split()
                del(bind_pose[0:2])
                bind_pose[0] = bind_pose[0][13:len(bind_pose[0])]
                bind_pose[-1] = bind_pose[-1][:len(bind_pose[-1])-8]
            if 'value name="name"' in line:
                temp10 = line.split()
                bone_name = temp10[2][14:len(temp10[2])-8]
                boneIndexation[bone_index_internal] = bone_name
                b = skeleton.edit_bones.new(bone_name)
                
                matrix = Matrix((Vector((float(bind_pose[0]), float(bind_pose[1]), float(bind_pose[2]), 0)),
                                    Vector((float(bind_pose[3]), float(bind_pose[4]), float(bind_pose[5]), 0)),
                                    Vector((float(bind_pose[6]), float(bind_pose[7]), float(bind_pose[8]), 0)),
                                    Vector((float(bind_pose[9]), float(bind_pose[10]), float(bind_pose[11]), 1))
                                    ))
                                    
                matrix.transpose()
                boneMatrices[bone_name] = matrix
                b.head = Vector((matrix.col[3][0:3]))
                b.tail = Vector((matrix.col[1][0:3])) + b.head
                #b.roll = ??
            if '/array' in line:
                break
            
        # Back to object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Rotation of the armature
        if rotate_180 == True:
            bpy.context.active_object.rotation_euler[2] = math.radians(180)

        arma_name = bpy.context.active_object.name
        
        # Collision Spheres
        for line in file:
            if 'array name="boneSpheres"' in line:
                collisionSpheres = []
                break
        for line in file:
            if '/array' in line:
                list_coma = []
                n = 0
                for j in range(len(collisionSpheres)):
                    if "," in collisionSpheres[j]:
                        list_coma.append(j)
                for k in list_coma:
                    collisionSpheres.insert(k + n + 1, collisionSpheres[k + n][collisionSpheres[k + n].find(",") + 1:len(collisionSpheres[k + n])])
                    collisionSpheres[k + n] = collisionSpheres[k + n][:collisionSpheres[k + n].find(",")]
                    n += 1
                collisionSpheres2 = list(filter(None, collisionSpheres))
                break
            temp25 = line.split()
            for i in temp25:
                collisionSpheres.append(i)
                
        # Collision Spheres Connections
        for line in file:
            if 'array name="boneSphereConnections"' in line:
                collisionSpheresConnections = []
                break
        for line in file:
            if '/array' in line:
                break
            temp26 = line.split()
            for i in temp26:
                collisionSpheresConnections.append(i)

        # Parenting Physical Meshes
        for y in range(len(physicalMeshes_names)):
            bpy.context.view_layer.objects.active = None
            bpy.context.view_layer.objects.active = bpy.data.objects[physicalMeshes_names[y]]
            bpy.context.active_object.select_set(state=True)
            bpy.context.view_layer.objects.active = bpy.data.objects[arma_name]
            bpy.ops.object.parent_set(type="ARMATURE_NAME", xmirror=False, keep_transform=False)

            # Weighting Physical Meshes
            bpy.context.view_layer.objects.active = None
            bpy.context.view_layer.objects.active = bpy.data.objects[physicalMeshes_names[y]]
            mesh2 = bpy.data.objects[physicalMeshes_names[y]]
            for j in range(len(mesh2.data.vertices)):
                if physicalMeshes_boneWeights_all[y][j][0] != 0:
                    bpy.context.active_object.vertex_groups[physicalMeshes_boneIndices_all[y][j][0]].add([mesh2.data.vertices[j].index], physicalMeshes_boneWeights_all[y][j][0], 'REPLACE')
                if physicalMeshes_boneWeights_all[y][j][1] != 0:
                    bpy.context.active_object.vertex_groups[physicalMeshes_boneIndices_all[y][j][1]].add([mesh2.data.vertices[j].index], physicalMeshes_boneWeights_all[y][j][1], 'REPLACE')
                if physicalMeshes_boneWeights_all[y][j][2] != 0:
                    bpy.context.active_object.vertex_groups[physicalMeshes_boneIndices_all[y][j][2]].add([mesh2.data.vertices[j].index], physicalMeshes_boneWeights_all[y][j][2], 'REPLACE')
                if physicalMeshes_boneWeights_all[y][j][3] != 0:
                    bpy.context.active_object.vertex_groups[physicalMeshes_boneIndices_all[y][j][3]].add([mesh2.data.vertices[j].index], physicalMeshes_boneWeights_all[y][j][3], 'REPLACE')
        
        # Parenting Graphical Meshes
        for y in range(len(lod_mesh_names)):
            for i in range(len(lod_mesh_names[y])):
                bpy.context.view_layer.objects.active = None
                bpy.context.view_layer.objects.active = bpy.data.objects[lod_mesh_names[y][i]]
                bpy.context.active_object.select_set(state=True)
                bpy.context.view_layer.objects.active = bpy.data.objects[arma_name]
                bpy.ops.object.parent_set(type="ARMATURE_NAME", xmirror=False, keep_transform=False)

                # Weighting Graphical Meshes
                bpy.context.view_layer.objects.active = None
                bpy.context.view_layer.objects.active = bpy.data.objects[lod_mesh_names[y][i]]
                mesh2 = bpy.data.objects[lod_mesh_names[y][i]]
                for j in range(len(mesh2.data.vertices)):
                    if lod_boneWeights_all[y][i][j][0] != 0:
                        bpy.context.active_object.vertex_groups[lod_boneIndices_all[y][i][j][0]].add([mesh2.data.vertices[j].index], lod_boneWeights_all[y][i][j][0], 'REPLACE')
                    if lod_boneWeights_all[y][i][j][1] != 0:
                        bpy.context.active_object.vertex_groups[lod_boneIndices_all[y][i][j][1]].add([mesh2.data.vertices[j].index], lod_boneWeights_all[y][i][j][1], 'REPLACE')
                    if lod_boneWeights_all[y][i][j][2] != 0:
                        bpy.context.active_object.vertex_groups[lod_boneIndices_all[y][i][j][2]].add([mesh2.data.vertices[j].index], lod_boneWeights_all[y][i][j][2], 'REPLACE')
                    if lod_boneWeights_all[y][i][j][3] != 0:
                        bpy.context.active_object.vertex_groups[lod_boneIndices_all[y][i][j][3]].add([mesh2.data.vertices[j].index], lod_boneWeights_all[y][i][j][3], 'REPLACE')

                # Materials attribution
                if use_mat == True:
                    if lod_materials_all[y][i] in bpy.data.materials:
                        mesh2.data.materials.append(bpy.data.materials[lod_materials_all[y][i]])
                    else:
                        temp_mat = bpy.data.materials.new(lod_materials_all[y][i])
                        mesh2.data.materials.append(temp_mat)
                        temp_mat.diffuse_color = (random.random(), random.random(), random.random(), 1)
                else:
                    temp_mat = bpy.data.materials.new(lod_materials_all[y][i])
                    mesh2.data.materials.append(temp_mat)
                    temp_mat.diffuse_color = (random.random(), random.random(), random.random(), 1)

        # Join submeshes under the same LOD
        for y in range(len(lod_mesh_names)):
            bpy.context.view_layer.objects.active = None
            bpy.ops.object.select_all(False)
            for i in reversed(range(len(lod_mesh_names[y]))):
                bpy.context.view_layer.objects.active = bpy.data.objects[lod_mesh_names[y][i]]
                bpy.context.active_object.select_set(state=True)
            bpy.ops.object.join()

            # Remove doubles if requested
            if rm_db == True:
                bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                bpy.ops.mesh.remove_doubles()
                bpy.ops.object.mode_set(mode='OBJECT')
                
        # Set up the ragdoll definitons
        collisionSpheres_index = []
        collisionSpheres_radius = []
        collisionSpheres_coordinates = []
        for i in range (0, len(collisionSpheres2), 5):
            collisionSpheres_index.append(collisionSpheres2[i])
            collisionSpheres_radius.append(float(collisionSpheres2[i+1]))
            collisionSpheres_coordinates.append([float(collisionSpheres2[i+2]), float(collisionSpheres2[i+3]), float(collisionSpheres2[i+4])])
            
        collisionSpheresConnections2 = []
        for i in range(0, len(collisionSpheresConnections), 2):
            collisionSpheresConnections2.append([collisionSpheresConnections[i], collisionSpheresConnections[i+1]])
        
        # Create a collection for collision spheres
        sphere_coll = bpy.data.collections.new("Collision Spheres")
        sphere_coll_name = sphere_coll.name
        #Will throw an error message if not found, but won't stop the script from doing its job
        if bpy.context.scene.collection.children.find("Collection") >= 0:
            bpy.context.scene.collection.children['Collection'].children.link(sphere_coll)
            bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children["Collection"].children[sphere_coll_name]
        else:
            bpy.context.scene.collection.children.link(sphere_coll)
            bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[sphere_coll_name]
            
        # Add the spheres to the scene
        collisionSpheres_coordinates_world = []
        for i in range(len(collisionSpheres_index)):
            sphereName = boneIndexation[collisionSpheres_index[i]]
            boneMatrix = boneMatrices[sphereName]
            coordinates_world =  boneMatrix @ Vector((collisionSpheres_coordinates[i]))
            collisionSpheres_coordinates_world.append(coordinates_world)
            bpy.ops.mesh.primitive_uv_sphere_add(radius = collisionSpheres_radius[i], location = coordinates_world)
            bpy.context.active_object.name = sphereName
            bpy.context.active_object.display_type = 'WIRE'
            # Rotation of the spheres
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
            if rotate_180 == True:
                bpy.context.active_object.rotation_euler[2] = math.radians(180)
                
        # Create a collection for collision spheres connections
        sphere_coll_connec = bpy.data.collections.new("Collision Spheres Connections")
        sphere_coll_connec_name = sphere_coll_connec.name
        #Will throw an error message if not found, but won't stop the script from doing its job
        if bpy.context.scene.collection.children.find("Collection") >= 0:
            bpy.context.scene.collection.children['Collection'].children.link(sphere_coll_connec)
            bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children["Collection"].children[sphere_coll_connec_name]
        else:
            bpy.context.scene.collection.children.link(sphere_coll_connec)
            bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[sphere_coll_connec_name]
            
        # Add the connections to the scene
        for i in collisionSpheresConnections2:
            verticesConnection = [collisionSpheres_coordinates_world[int(i[0])], collisionSpheres_coordinates_world[int(i[1])]]
            edgesConnection = [[0,1]]
            facesConnection = []
            meshConnection = bpy.data.meshes.new(name = boneIndexation[collisionSpheres_index[int(i[0])]] + "_to_" + boneIndexation[collisionSpheres_index[int(i[1])]])
            meshConnection.from_pydata(verticesConnection, edgesConnection, facesConnection)
            object_data_add(context, meshConnection)
            bpy.context.active_object.display_type = 'WIRE'
            # Rotation of the connections
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
            if rotate_180 == True:
                bpy.context.active_object.rotation_euler[2] = math.radians(180)
            
        # Make the new collections inactive
        if bpy.context.scene.collection.children.find("Collection") >= 0:    
            bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children["Collection"]
        else:
            bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection