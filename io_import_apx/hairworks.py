# -*- coding: utf-8 -*-
# hairworks.py

import bpy
import math
import random
from bpy_extras.object_utils import object_data_add
from mathutils import Vector, Matrix

def read_hairworks(context, filepath, rotate_180, scale_down, minimal_armature):

    with open(filepath, 'r', encoding='utf-8') as file:

        # Hair Count
        for line in file:
            if 'value name="numGuideHairs"' in line:
                temp19 = line.split()
                hair_count = temp19[2][11:-8]
                break

        # Vertices Count
        for line in file:
            if 'value name="numVertices"' in line:
                temp20 = line.split()
                vertices_count = temp20[2][11:-8]
                break

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
            temp16 = line.split()
            for i in temp16:
                vertices.append(i)

        # Guides' end
        for line in file:
            if 'array name="endIndices"' in line:
                endIndices = []
                break
        for line in file:
            if '/array' in line:
                break
            temp17 = line.split()
            for i in temp17:
                endIndices.append(i)

        # Faces
        for line in file:
            if 'array name="faceIndices"' in line:
                indices = []
                break
        for line in file:
            if '/array' in line:
                break
            temp18 = line.split()
            for i in temp18:
                indices.append(i)

        # UVmap
        for line in file:
            if 'array name="faceUVs"' in line:
                texCoords = []
                break
        for line in file:
            if '/array' in line:
                for j in range(len(texCoords)):
                    if "," in texCoords[j]:
                        l = len(texCoords[j])
                        texCoords[j] = texCoords[j][:l - 1]
                break
            temp21 = line.split()
            for i in temp21:
                texCoords.append(i)

        # Bone Count
        for line in file:
            if 'value name="numBones"' in line:
                temp22 = line.split()
                bone_count = temp22[2][11:len(temp22[2])-8]
                break

        # Bone Indices
        for line in file:
            if 'array name="boneIndices"' in line:
                boneIndices = []
                break
        for line in file:
            if '/array' in line:
                for j in range(len(boneIndices)):
                    if "," in boneIndices[j]:
                        l = len(boneIndices[j])
                        boneIndices[j] = boneIndices[j][:l - 1]
                break
            temp23 = line.split()
            for i in temp23:
                boneIndices.append(i)

        # Bone Weights
        for line in file:
            if 'array name="boneWeights"' in line:
                boneWeights = []
                break
        for line in file:
            if '/array' in line:
                for j in range(len(boneWeights)):
                    if "," in boneWeights[j]:
                        l = len(boneWeights[j])
                        boneWeights[j] = boneWeights[j][:l - 1]
                break
            temp24 = line.split()
            for i in temp24:
                boneWeights.append(i)

        # Bone Names
        for line in file:
            if 'array name="boneNames"' in line:
                boneNames = []
                break
        for line in file:
            if '/array' in line:
                break
            temp25 = line.split()
            for i in temp25:
                boneNames.append(i)

        # Bind Pose
        for line in file:
            if 'array name="bindPoses"' in line:
                bindPoses = []
                break
        for line in file:
            if '/array' in line:
                for j in range(len(bindPoses)):
                    if "," in bindPoses[j]:
                        l = len(bindPoses[j])
                        bindPoses[j] = bindPoses[j][:l - 1]
                break
            temp26 = line.split()
            for i in temp26:
                bindPoses.append(i)


        # Creation of the guides
        guides_verts = []
        for i in range(0,len(vertices), 3):
            guides_verts.append(Vector((float(vertices[i]), float(vertices[i+1]), float(vertices[i+2]))))
        guideS = []
        for i in range(len(endIndices)):
            guide = []
            if int(endIndices[i]) > int(vertices_count)/int(hair_count):
                for j in range(int(endIndices[i-1])+1, int(endIndices[i])+1):
                    guide.append(j)
                guideS.append(guide)
            else:
                for j in range(int(endIndices[i])+1):
                    guide.append(j)
                guideS.append(guide)
        guides_edges = []
        for i in range(len(guideS)):
            for j in range(len(guideS[i])):
                if guideS[i][j] == guideS[i][-1]:
                    break
                edge = [int(guideS[i][j]), int(guideS[i][j+1])]
                guides_edges.append(edge)
        guides_faces = []

        # Add the guides to the scene
        guides_mesh = bpy.data.meshes.new(name="Guides")
        guides_mesh.from_pydata(guides_verts, guides_edges, guides_faces)
        object_data_add(context, guides_mesh)

        # Rotation of the armature
        if rotate_180 == True:
            bpy.context.active_object.rotation_euler[2] = math.radians(180)

        # Scale down if requested
        if scale_down == True:
            bpy.context.active_object.scale = (0.01, 0.01, 0.01)

        guides_mesh_name = bpy.context.active_object.name

        # Creation of the growthmesh
        growth_verts = []
        for i in range(0, len(vertices), int((3 * int(vertices_count)/int(hair_count)))):
            growth_verts.append(Vector((float(vertices[i]), float(vertices[i+1]), float(vertices[i+2]))))
        growth_edges = []
        growth_faces = []
        for i in range(0,len(indices), 3):
            growth_faces.append([int(indices[i]), int(indices[i+1]),int(indices[i+2])])
        texCoords2 = []
        for i in range(0,len(texCoords), 2):
            texCoords2.append([float(texCoords[i]), float(texCoords[i+1])])

        # Add the growthmesh to the scene
        growth_mesh = bpy.data.meshes.new(name="GrowthMesh")
        growth_mesh.from_pydata(growth_verts, growth_edges, growth_faces)
        object_data_add(context, growth_mesh)
        for i in growth_mesh.polygons:
            i.use_smooth = True

        # Rotation of the armature
        if rotate_180 == True:
            bpy.context.active_object.rotation_euler[2] = math.radians(180)

        # Scale down if requested
        if scale_down == True:
            bpy.context.active_object.scale = (0.01, 0.01, 0.01)
            
        # Materials attribution
        growth_mesh_name = bpy.context.active_object.name
        mesh2 = bpy.data.objects[growth_mesh_name]
        temp_mat = bpy.data.materials.new("Material0")
        mesh2.data.materials.append(temp_mat)
        temp_mat.diffuse_color = (random.random(), random.random(), random.random(), 1)

        # UVmap creation
        growth_mesh.uv_layers.new(name="DiffuseUV")
        for face in growth_mesh.polygons:
            for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                growth_mesh.uv_layers.active.data[loop_idx].uv = (texCoords2[loop_idx][0],  -texCoords2[loop_idx][1] + 1)

        # Creation of the armature
        skeleton = bpy.data.armatures.new(name="Armature")
        object_data_add(context, skeleton)
        # Edit mode required to add bones to the armature
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        # Bones creation
        boneNames_str = []
        for i in boneNames:
            boneNames_str.append(chr(int(i)))
        boneNames2 = []
        start = -1
        for i in range(int(bone_count)):
            bone_name = ''
            for j in range(start + 1, len(boneNames_str)):
                if boneNames_str[j] == """\x00""":
                    start = j
                    break
                bone_name += boneNames_str[j]
            boneNames2.append(bone_name)
        bindPoses2 = []
        for i in range(0, len(bindPoses), 16):
            bindPoses2.append(bindPoses[i:i+16])

        used_bones_count = max(boneIndices)  
        for i in range(len(boneNames2)):
            if minimal_armature == True:
                if i > int(used_bones_count):
                    break
            b = skeleton.edit_bones.new(boneNames2[i])
            
            matrix = Matrix((Vector((float(bindPoses2[i][0]), float(bindPoses2[i][1]), float(bindPoses2[i][2]), float(bindPoses2[i][3]))),
                                    Vector((float(bindPoses2[i][4]), float(bindPoses2[i][5]), float(bindPoses2[i][6]), float(bindPoses2[i][7]))),
                                    Vector((float(bindPoses2[i][8]), float(bindPoses2[i][9]), float(bindPoses2[i][10]), float(bindPoses2[i][11]))),
                                    Vector((float(bindPoses2[i][12]), float(bindPoses2[i][13]), float(bindPoses2[i][14]), float(bindPoses2[i][15])))
                                    ))
                                    
            matrix.transpose()
            b.head = Vector((matrix.col[3][0:3]))
            b.tail = Vector((matrix.col[1][0:3])) + b.head
            #b.roll = ??

        # Back to object mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # Rotation of the armature
        if rotate_180 == True:
            bpy.context.active_object.rotation_euler[2] = math.radians(180)

        # Scale down if requested
        if scale_down == True:
            bpy.context.active_object.scale = (0.01, 0.01, 0.01)

        arma_name = bpy.context.active_object.name

        # Creation of bones indices and weights list
        for i in range(len(boneWeights)):
            if boneWeights[i] == '1':
                boneWeights[i] = int(boneWeights[i])
            else:
                boneWeights[i] = float(boneWeights[i])

        boneIndices2 = []
        for i in range(0, len(boneIndices), 4):
            boneIndices2.append([int(boneIndices[i]), int(boneIndices[i+1]), int(boneIndices[i+2]),
                                int(boneIndices[i+3])])
        boneWeights2 = []
        for i in range(0, len(boneWeights), 4):
            boneWeights2.append([boneWeights[i], boneWeights[i+1], boneWeights[i+2],
                                boneWeights[i+3]])

        # Parenting
        bpy.context.view_layer.objects.active = None
        bpy.context.view_layer.objects.active = bpy.data.objects[growth_mesh_name]
        bpy.context.active_object.select_set(state=True)
        bpy.context.view_layer.objects.active = bpy.data.objects[arma_name]
        bpy.ops.object.parent_set(type="ARMATURE_NAME", xmirror=False, keep_transform=False)

        # Weighting
        bpy.context.view_layer.objects.active = None
        bpy.context.view_layer.objects.active = bpy.data.objects[growth_mesh_name]
        mesh2 = bpy.data.objects[growth_mesh_name]
        for j in range(len(mesh2.data.vertices)):
            if boneWeights2[j][0] != 0:
                bpy.context.active_object.vertex_groups[boneIndices2[j][0]].add([mesh2.data.vertices[j].index], boneWeights2[j][0], 'REPLACE')
            if boneWeights2[j][1] != 0:
                bpy.context.active_object.vertex_groups[boneIndices2[j][1]].add([mesh2.data.vertices[j].index], boneWeights2[j][1], 'REPLACE')
            if boneWeights2[j][2] != 0:
                bpy.context.active_object.vertex_groups[boneIndices2[j][2]].add([mesh2.data.vertices[j].index], boneWeights2[j][2], 'REPLACE')
            if boneWeights2[j][3] != 0:
                bpy.context.active_object.vertex_groups[boneIndices2[j][3]].add([mesh2.data.vertices[j].index], boneWeights2[j][3], 'REPLACE')
                
        # Create a new collection to store curves
        curve_coll = bpy.data.collections.new("Curves")
        curve_coll_name = curve_coll.name
        #Will throw an error message if not found, but won't stop the script from doing its job
        if bpy.context.scene.collection.children.find("Collection") >= 0:
            bpy.context.scene.collection.children['Collection'].children.link(curve_coll)
            bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children["Collection"].children[curve_coll_name]
        else:
            bpy.context.scene.collection.children.link(curve_coll)
            bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[curve_coll_name]
            
        # Create curves
        guides_vertices = []
        for i in range(0, len(vertices), int((3 * int(vertices_count)/int(hair_count)))):
            guide_vertices = (vertices[i:i+int((3 * int(vertices_count)/int(hair_count)))])
            vertex = []
            for j in range(0, len(guide_vertices), 3):
                vertex.append([float(guide_vertices[j]), float(guide_vertices[j+1]), float(guide_vertices[j+2])])
            guides_vertices.append(vertex)
                
        for i in range(len(guideS)):
                
            # create the Curve Datablock
            curveData = bpy.data.curves.new('myCurve', type='CURVE')
            curveData.dimensions = '3D'
            curveData.resolution_u = 2
            curveData.bevel_depth = 0.01
            
            # map coords to spline
            polyline = curveData.splines.new('POLY')
            polyline.points.add(len(guideS[i])-1)
            for j, coord in enumerate(guides_vertices[i]):
                x,y,z = coord
                polyline.points[j].co = (x, y, z, 1)
            
            # Add the curves to the scene
            object_data_add(context, curveData)
            
            # Rotation of the armature
            if rotate_180 == True:
                bpy.context.active_object.rotation_euler[2] = math.radians(180)
            
            # Scale down if requested
            if scale_down == True:
                bpy.context.active_object.scale = (0.01, 0.01, 0.01)
                
        if bpy.context.scene.collection.children.find("Collection") >= 0:    
            bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children["Collection"]
        else:
            bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection