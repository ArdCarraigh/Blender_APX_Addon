bl_info = {
    "name": "APX Importer (.apx)",
    "author": "Ard Carraigh",
    "version": (1, 0),
    "blender": (2, 92, 0),
    "location": "File > Import > APX (.apx)",
    "description": "Import an .apx mesh",
    "warning": "",
    "doc_url": "",
    "support": "COMMUNITY",
    "category": "Import-Export",
}

import bpy
import bmesh
import math
# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
from bpy.props import FloatVectorProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector
import random



def read_apx(context, filepath, rm_db, use_mat):
    print("running read_apx...")
    
    # Ensure that it works even when in edit mode
    if bpy.context.mode == 'EDIT_MESH':
        bpy.ops.object.mode_set(mode='OBJECT')
    with open(filepath, 'r', encoding='utf-8') as file:
        
        # Get the type of .apx we have
        for line in file:
            if 'className=' in line:
                if 'ClothingAssetParameters' in line:
                    type = 'cloth'
                if 'HairWorksInfo' in line:
                    type = 'hair'
                break
            
        # If PhysX Clothing type
        if type == 'cloth':
            SEMANTIC_POSITION = False
            SEMANTIC_NORMAL = False
            SEMANTIC_TANGENT = False
            SEMANTIC_COLOR = False
            SEMANTIC_TEXCOORD0 = False
            SEMANTIC_TEXCOORD1 = False
            SEMANTIC_TEXCOORD2 = False
            SEMANTIC_TEXCOORD3 = False
            SEMANTIC_TEXCOORD4 = False
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
                    if '<value name="name" type="String">SEMANTIC_COLOR</value>' in line:
                        SEMANTIC_COLOR = True
                    if '<value name="name" type="String">SEMANTIC_TEXCOORD0</value>' in line:
                        SEMANTIC_TEXCOORD0 = True
                    if '<value name="name" type="String">SEMANTIC_TEXCOORD1</value>' in line:
                        SEMANTIC_TEXCOORD1 = True
                    if '<value name="name" type="String">SEMANTIC_TEXCOORD2</value>' in line:
                        SEMANTIC_TEXCOORD2 = True
                    if '<value name="name" type="String">SEMANTIC_TEXCOORD3</value>' in line:
                        SEMANTIC_TEXCOORD3 = True
                    if '<value name="name" type="String">SEMANTIC_TEXCOORD4</value>' in line:
                        SEMANTIC_TEXCOORD4 = True
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

                    #Normals
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

                    #Tangents
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

                    # Material Color
                    if SEMANTIC_COLOR == True:
                        for line in file:
                            if 'array name="data"' in line:
                                break

                    # UVmap 1
                    if SEMANTIC_TEXCOORD0 == True:
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

                    # UVmap 2
                    if SEMANTIC_TEXCOORD1 == True:
                        for line in file:
                            if 'array name="data"' in line:
                                texCoords_bis = []
                                break
                        for line in file:
                            if '/array' in line:
                                list_coma = []
                                n = 0
                                for j in range(len(texCoords_bis)):
                                    if "," in texCoords_bis[j]:
                                        list_coma.append(j)
                                for k in list_coma:
                                    texCoords_bis.insert(k + n + 1, texCoords_bis[k + n][texCoords_bis[k + n].find(",") + 1:len(texCoords_bis[k + n])])
                                    texCoords_bis[k + n] = texCoords_bis[k + n][:texCoords_bis[k + n].find(",")]
                                    n += 1
                                texCoords_bis2 = list(filter(None, texCoords_bis))
                                break
                            temp14 = line.split()
                            for i in temp14:
                                texCoords_bis.append(i)

                    # UVmap 3
                    if SEMANTIC_TEXCOORD2 == True:
                        for line in file:
                            if 'array name="data"' in line:
                                break

                    # UVmap 4
                    if SEMANTIC_TEXCOORD3 == True:
                        for line in file:
                            if 'array name="data"' in line:
                                break

                    # UVmap 5
                    if SEMANTIC_TEXCOORD4 == True:
                        for line in file:
                            if 'array name="data"' in line:
                                break

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

                    # Faces
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


                    # Creation of the mesh
                    verts = []
                    for i in range(0,len(vertices), 3):
                        verts.append(Vector((float(vertices[i]), float(vertices[i+1]), float(vertices[i+2]))))
                    edges = []
                    faces = []
                    for i in range(0,len(indices), 3):
                        faces.append([int(indices[i]), int(indices[i+1]),int(indices[i+2])])
                    normals2 = []
                    for i in range(0, len(normals), 3):
                        normals2.append([float(normals[i]), float(normals[i+1]), float(normals[i+2])])
                    texCoords3 = []
                    for i in range(0,len(texCoords2), 2):
                        texCoords3.append([float(texCoords2[i]), float(texCoords2[i+1])])
                    if SEMANTIC_TEXCOORD1 == True:
                        texCoords_bis3 = []
                        for i in range(0,len(texCoords_bis2), 2):
                            texCoords_bis3.append([float(texCoords_bis2[i]), float(texCoords_bis2[i+1])])

                    # Add the mesh to the scene
                    mesh = bpy.data.meshes.new(name="Mesh_lod"+str(lod_number))
                    mesh.from_pydata(verts, edges, faces)
                    for i in range(len(mesh.vertices)):
                        mesh.vertices[i].normal = normals2[i]
                    for i in mesh.polygons:
                        i.use_smooth = True
                    object_data_add(context, mesh)

                    # Rotation of the mesh
                    bpy.context.active_object.rotation_euler[2] = math.radians(180)

                    # UVmaps creation
                    mesh.uv_layers.new(name="DiffuseUV")
                    for face in mesh.polygons:
                        for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                            mesh.uv_layers.active.data[loop_idx].uv = (texCoords3[vert_idx][0], texCoords3[vert_idx][1])

                    if SEMANTIC_TEXCOORD1 == True:
                        for face in mesh.polygons:
                            for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                                mesh.uv_layers.active.data[loop_idx].uv = (texCoords_bis3[vert_idx][0], texCoords_bis3[vert_idx][1])
                        mesh.uv_layers.new(name="SecondUV")
                        for face in mesh.polygons:
                            for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                                mesh.uv_layers.active.data[loop_idx].uv = (texCoords3[vert_idx][0], texCoords3[vert_idx][1])

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
                    # Edit mode required to add bones to the armature
                    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                    break
            for line in file:
                if 'value name="internalIndex"' in line:
                    temp9 = line.split()
                    bone_index_internal = temp9[2][11:len(temp9[2])-8]
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
                    b = skeleton.edit_bones.new(bone_name)
                    b.head = (float(bind_pose[9]), float(bind_pose[10]), float(bind_pose[11]))
                    b.tail = (float(bind_pose[0]), float(bind_pose[1]), float(bind_pose[2]))


            # Back to object mode
            bpy.ops.object.mode_set(mode='OBJECT')
            # Rotation of the armature
            bpy.context.active_object.rotation_euler[2] = math.radians(180)
            arma_name = bpy.context.active_object.name

            # Parenting
            for y in range(len(lod_mesh_names)):
                for i in range(len(lod_mesh_names[y])):
                    bpy.context.view_layer.objects.active = None
                    bpy.context.view_layer.objects.active = bpy.data.objects[lod_mesh_names[y][i]]
                    bpy.context.active_object.select_set(state=True)
                    bpy.context.view_layer.objects.active = bpy.data.objects[arma_name]
                    bpy.ops.object.parent_set(type="ARMATURE_NAME", xmirror=False, keep_transform=False)

                    # Weighting
                    bpy.context.view_layer.objects.active = None
                    bpy.context.view_layer.objects.active = bpy.data.objects[lod_mesh_names[y][i]]
                    mesh2 = bpy.data.objects[lod_mesh_names[y][i]]
                    for j in range(len(mesh2.data.vertices)):
                        bpy.context.active_object.vertex_groups[lod_boneIndices_all[y][i][j][0]].add([mesh2.data.vertices[j].index], lod_boneWeights_all[y][i][j][0], 'REPLACE')
                        bpy.context.active_object.vertex_groups[lod_boneIndices_all[y][i][j][1]].add([mesh2.data.vertices[j].index], lod_boneWeights_all[y][i][j][1], 'REPLACE')
                        bpy.context.active_object.vertex_groups[lod_boneIndices_all[y][i][j][2]].add([mesh2.data.vertices[j].index], lod_boneWeights_all[y][i][j][2], 'REPLACE')
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
                for i in range(len(lod_mesh_names[y])):
                    bpy.context.view_layer.objects.active = bpy.data.objects[lod_mesh_names[y][i]]
                    bpy.context.active_object.select_set(state=True)
                bpy.ops.object.join()

                # Remove doubles if requested
                if rm_db == True:
                    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                    bpy.ops.mesh.remove_doubles()
                    bpy.ops.object.mode_set(mode='OBJECT')
        
        # If Hairworks type
        if type == 'hair':
            
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
            
            # Faces
            for line in file:
                if 'array name="faceIndices"' in line:
                    indices = []
                    break
            for line in file:
                if '/array' in line:
                    break
                temp17 = line.split()
                for i in temp17:
                    indices.append(i)
                    
            verts = []
            for i in range(0,len(vertices), 3):
                verts.append(Vector((float(vertices[i]), float(vertices[i+1]), float(vertices[i+2]))))
            edges = []
            faces = []
            for i in range(0,len(indices), 3):
                faces.append([int(indices[i]), int(indices[i+1]),int(indices[i+2])])
             
            mesh = bpy.data.meshes.new(name="Mesh")
            mesh.from_pydata(verts, edges, faces)
            object_data_add(context, mesh)
        
        # Unselect everything
        bpy.context.view_layer.objects.active = None
        bpy.ops.object.select_all(False)
    
    return {'FINISHED'}

class ImportApx(Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "import_test.apx"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import APX"

    # ImportHelper mixin class uses this
    filename_ext = ".apx"

    filter_glob: StringProperty(
        default="*.apx",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    rm_db: BoolProperty(
        name="Remove Doubles",
        description="Remove Doubles",
        default=True,
    )
    
    use_mat: BoolProperty(
        name="Prevent Material Duplication",
        description="Use existing materials from the scene if their name is identical to the one of your mesh",
        default=True,
    )

    def execute(self, context):
        return read_apx(context, self.filepath, self.rm_db, self.use_mat)


# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(ImportApx.bl_idname, text="APX (.apx)")


def register():
    bpy.utils.register_class(ImportApx)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportApx)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()
    
    # test call
    bpy.ops.import_test.apx('INVOKE_DEFAULT')
