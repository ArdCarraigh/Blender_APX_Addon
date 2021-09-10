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
                
        COLLISION_SPHERES = False
        COLLISION_SPHERES_CONNECTIONS = False
        PIN_CONSTRAINTS = False
                
        # Collision Spheres
        for line in file:
            if 'array name="boneSpheres"' in line:
                collisionSpheres = []
                temp27 = line.split()
                spheres_count = temp27[2][6:-1]
                if int(spheres_count) >= 1:
                    COLLISION_SPHERES = True
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
            if 'array name="boneCapsuleIndices"' in line:
                collisionSpheresConnections = []
                temp28 = line.split()
                spheres_connections_count = temp28[2][6:-1]
                if int(spheres_connections_count) >= 1:
                    COLLISION_SPHERES_CONNECTIONS = True
                break
        for line in file:
            if '/array' in line:
                break
            temp29 = line.split()
            for i in temp29:
                collisionSpheresConnections.append(i)
                
        # Pin Constraints
        for line in file:
            if 'array name="pinConstraints' in line:
                pinConstraints = []
                temp30 = line.split()
                pin_count = temp30[2][6:-1]
                if int(pin_count) >= 1:
                    PIN_CONSTRAINTS = True
                break
        for line in file:
            if '/array' in line:
                list_coma = []
                n = 0
                for j in range(len(pinConstraints)):
                    if "," in pinConstraints[j]:
                        list_coma.append(j)
                for k in list_coma:
                    pinConstraints.insert(k + n + 1, pinConstraints[k + n][pinConstraints[k + n].find(",") + 1:len(pinConstraints[k + n])])
                    pinConstraints[k + n] = pinConstraints[k + n][:pinConstraints[k + n].find(",")]
                    n += 1
                pinConstraints2 = list(filter(None, pinConstraints))
                break
            temp31 = line.split()
            for i in temp31:
                pinConstraints.append(i)
            

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

        # Rotation of the guies if requested
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

        # Rotation of the growthmesh if requested
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

        # Armature and bones creation
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
        armaNames = []
        boneIndexation = {}
        boneMatrices = {}
        boneIndex = 0
        for i in range(len(boneNames2)):
            if minimal_armature == True:
                if i > int(used_bones_count):
                    break
            bpy.context.view_layer.objects.active = None
            bpy.ops.object.select_all(False)
            skeleton = bpy.data.armatures.new(name="Armature")
            object_data_add(context, skeleton)
            armaNames.append(bpy.context.active_object.name)
            boneIndexation[boneIndex] = boneNames2[i]
            boneIndex += 1
            # Edit mode required to add bones to the armature
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            b = skeleton.edit_bones.new(boneNames2[i])
            
            matrix = Matrix((Vector((float(bindPoses2[i][0]), float(bindPoses2[i][1]), float(bindPoses2[i][2]), float(bindPoses2[i][3]))),
                                    Vector((float(bindPoses2[i][4]), float(bindPoses2[i][5]), float(bindPoses2[i][6]), float(bindPoses2[i][7]))),
                                    Vector((float(bindPoses2[i][8]), float(bindPoses2[i][9]), float(bindPoses2[i][10]), float(bindPoses2[i][11]))),
                                    Vector((float(bindPoses2[i][12]), float(bindPoses2[i][13]), float(bindPoses2[i][14]), float(bindPoses2[i][15])))
                                    ))
                                    
            matrix.transpose()
            boneMatrices[boneNames2[i]] = matrix
            b.head = Vector((0,0,0))
            b.tail = Vector((0,1,0))
            #Transform the armature to have the correct transformation, edit_bone.transform() gives wrong results
            bpy.ops.object.mode_set(mode='OBJECT')
            skeleton.transform(matrix)
            
        # Join the armatures made for each bone together
        for i in reversed(range(len(armaNames))):
            bpy.context.view_layer.objects.active = bpy.data.objects[armaNames[i]]
            bpy.context.active_object.select_set(state=True)
        bpy.ops.object.join()

        # Back to object mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # Rotation of the armature if requested
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
            
            # Rotation of the curves if requested
            if rotate_180 == True:
                bpy.context.active_object.rotation_euler[2] = math.radians(180)
            
            # Scale down if requested
            if scale_down == True:
                bpy.context.active_object.scale = (0.01, 0.01, 0.01)
        
        # Set up the ragdoll definitons        
        if COLLISION_SPHERES == True:
            collisionSpheres_index = []
            collisionSpheres_radius = []
            collisionSpheres_coordinates = []
            for i in range (0, len(collisionSpheres2), 5):
                collisionSpheres_index.append(collisionSpheres2[i])
                collisionSpheres_radius.append(float(collisionSpheres2[i+1]))
                collisionSpheres_coordinates.append([float(collisionSpheres2[i+2]), float(collisionSpheres2[i+3]), float(collisionSpheres2[i+4])])
        
        if COLLISION_SPHERES_CONNECTIONS == True:
            collisionSpheresConnections2 = []
            for i in range(0, len(collisionSpheresConnections), 2):
                collisionSpheresConnections2.append([collisionSpheresConnections[i], collisionSpheresConnections[i+1]])
                
        if PIN_CONSTRAINTS == True:
            pinConstraints_index = []
            pinConstraints_radius = []
            pinConstraints_coordinates = []
            for i in range(0,len(pinConstraints2),14):
                pinConstraints_index.append(pinConstraints2[i])
                pinConstraints_radius.append(float(pinConstraints2[i+1]))
                pinConstraints_coordinates.append([float(pinConstraints2[i+2]), float(pinConstraints2[i+3]), float(pinConstraints2[i+4])])
                
        # Create a collection for collision spheres
        if COLLISION_SPHERES == True:
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
            spheres_name = []
            num = 1
            for i in range(len(collisionSpheres_index)):
                sphereName = boneIndexation[int(collisionSpheres_index[i])]
                boneMatrix = boneMatrices[sphereName]
                coordinates_world =  boneMatrix @ Vector((collisionSpheres_coordinates[i]))
                collisionSpheres_coordinates_world.append(coordinates_world)
                bpy.ops.mesh.primitive_uv_sphere_add(radius = collisionSpheres_radius[i], location = coordinates_world, segments=24, ring_count=16)
                if "sphere_" + sphereName + "_1" in spheres_name:
                    num += 1
                else:
                    num = 1
                bpy.context.active_object.name = "sphere_" + sphereName + "_" + str(num)
                spheres_name.append(bpy.context.active_object.name)
                bpy.context.active_object.display_type = 'WIRE'
                # Rotation of the spheres
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
                if rotate_180 == True:
                    bpy.context.active_object.rotation_euler[2] = math.radians(180)
                # Scale down if requested
                if scale_down == True:
                    bpy.context.active_object.scale = (0.01, 0.01, 0.01)
                    
        # Create a collection for collision spheres connections
        if COLLISION_SPHERES_CONNECTIONS == True:
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
                meshConnection_name = spheres_name[int(i[0])] + "_to_" + spheres_name[int(i[1])]
                # create the Curve Datablock
                curveData = bpy.data.curves.new(meshConnection_name, type='CURVE')
                curveData.dimensions = '3D'
                curveData.resolution_u = 2
                curveData.bevel_depth = 1.0
                curveData.bevel_resolution = 10
                edge_vertices = 4 + (10*2)
            
                # map coords to spline
                polyline = curveData.splines.new('POLY')
                polyline.points.add(len(verticesConnection)-1)
                for j, coord in enumerate(verticesConnection):
                    x,y,z = coord
                    polyline.points[j].co = (x, y, z, 1)
                    
                # Add the curves to the scene
                object_data_add(context, curveData)
            
                # Scale the edge loops to the spheres' radius
                bpy.ops.object.convert(target = 'MESH')
                mesh3 = bpy.context.active_object
                for j in range(edge_vertices):
                    mesh3.data.vertices[j].select = True
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.transform.resize(value = (collisionSpheres_radius[int(i[0])], collisionSpheres_radius[int(i[0])], collisionSpheres_radius[int(i[0])]))
                bpy.ops.mesh.select_all(action="DESELECT")
                bpy.ops.object.mode_set(mode='OBJECT')
                for j in range(edge_vertices, edge_vertices * 2):
                    mesh3.data.vertices[j].select = True
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.transform.resize(value = (collisionSpheres_radius[int(i[1])], collisionSpheres_radius[int(i[1])], collisionSpheres_radius[int(i[1])]))      
                bpy.ops.mesh.select_all(action="DESELECT")
                bpy.ops.object.mode_set(mode='OBJECT')
    
                bpy.context.active_object.display_type = 'WIRE'
                # Rotation of the connections
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
                if rotate_180 == True:
                    bpy.context.active_object.rotation_euler[2] = math.radians(180)
                # Scale down if requested
                if scale_down == True:
                    bpy.context.active_object.scale = (0.01, 0.01, 0.01)
                    
        # Create a collection for pin constraints
        if PIN_CONSTRAINTS == True:
            pin_coll = bpy.data.collections.new("Pin Constraints")
            pin_coll_name = pin_coll.name
            #Will throw an error message if not found, but won't stop the script from doing its job
            if bpy.context.scene.collection.children.find("Collection") >= 0:
                bpy.context.scene.collection.children['Collection'].children.link(pin_coll)
                bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children["Collection"].children[pin_coll_name]
            else:
                bpy.context.scene.collection.children.link(pin_coll)
                bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[pin_coll_name]
            
            # Add the pins to the scene
            pinConstraints_coordinates_world = []
            pins_name = []
            num = 1
            for i in range(len(pinConstraints_index)):
                pinName = boneIndexation[int(pinConstraints_index[i])]
                boneMatrix = boneMatrices[pinName]
                coordinates_world =  boneMatrix @ Vector((pinConstraints_coordinates[i]))
                pinConstraints_coordinates_world.append(coordinates_world)
                bpy.ops.mesh.primitive_uv_sphere_add(radius = pinConstraints_radius[i], location = coordinates_world, segments=24, ring_count=16)
                if "pin_" + pinName + "_1" in pins_name:
                    num += 1
                else:
                    num = 1
                bpy.context.active_object.name = "pin_" + pinName + "_" + str(num)
                pins_name.append(bpy.context.active_object.name)
                bpy.context.active_object.display_type = 'WIRE'
                # Rotation of the pins
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
                if rotate_180 == True:
                    bpy.context.active_object.rotation_euler[2] = math.radians(180)
                # Scale down if requested
                if scale_down == True:
                    bpy.context.active_object.scale = (0.01, 0.01, 0.01)
        
        # Make the new collections inactive  
        if bpy.context.scene.collection.children.find("Collection") >= 0:    
            bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children["Collection"]
        else:
            bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection