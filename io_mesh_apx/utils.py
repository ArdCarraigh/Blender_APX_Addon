# -*- coding: utf-8 -*-
# utils.py

import bpy
import numpy as np
from mathutils import kdtree, Vector
from copy import deepcopy
import bmesh
import os.path
import re
from bpy_extras.object_utils import object_data_add
import gpu
from gpu_extras.batch import batch_for_shader
from itertools import chain

def find_elem(root, tag, attr=None, attr_value=None):
    for elem in root:
        if elem.tag == tag:
            if not attr:
                return elem
            else:
                if attr in elem.attrib and attr_value == elem.attrib[attr]:
                    return elem
    raise Exception("element not found")
    
def to_array(text, dtype, shape):
    return(np.array([dtype(x) for x in text.replace(',', ' ').split()]).reshape(shape))

def JoinThem(objects):
    bpy.context.view_layer.objects.active = None
    bpy.ops.object.select_all(action='DESELECT')
    for obj in reversed(objects):
        bpy.context.view_layer.objects.active = obj
        obj.select_set(state=True)
    bpy.ops.object.join()
    # Purge orphan data left by the joining
    override = bpy.context.copy()
    override["area.type"] = ['OUTLINER']
    override["display_mode"] = ['ORPHAN_DATA']
    with bpy.context.temp_override(**override):
        bpy.ops.outliner.orphans_purge()
    
def getConnectedVertices(obj, v_idx, steps):
    interest_verts = [v_idx]
    edge_array = np.zeros(len(obj.data.edges) * 2, dtype=int)
    obj.data.attributes['.edge_verts'].data.foreach_get("value", edge_array)
    edge_array = edge_array.reshape(-1,2)
    for i in range(steps):
        connec_verts = []
        for edge in edge_array:
            if any(item in interest_verts for item in edge):
                connec_verts.extend(edge)
        interest_verts = list(set(connec_verts))
    return(list(filter(lambda v: v!=v_idx, interest_verts)))

def MakeKDTree(veclist, indices = None):
    size = len(veclist)
    kd = kdtree.KDTree(size)
    if indices is None:
        for i, v in enumerate(veclist):
            kd.insert(v, i)
    else:
        for i,v in zip(indices, veclist):
            kd.insert(v, i)
    kd.balance()
    return kd

def getClosest(vec, kd, range = None):
    if range:
        index = np.array([x[1:] for x in kd.find_range(vec, range)], dtype="object")
        if index.size > 2:
            index = index[:,0][index[:,1].argmin()]
        elif index.size > 1:
            index = index[0][0]
        else:
            co, index, dist = kd.find(vec)
    else:
        co, index, dist = kd.find(vec)
    return index

def MakeKDTreeFromObject(obj, filter = None):
    mesh = obj.data
    array = np.zeros(len(mesh.vertices) * 3)
    mesh.attributes["position"].data.foreach_get("vector", array)
    if filter is None:
        array = array.reshape(-1,3)
    else:
        array = array.reshape(-1,3)[filter]
    kd = MakeKDTree(array, filter)
    return kd

def GetLoopDataPerVertex(mesh, type, layername = None):
    corner_verts = mesh.attributes[".corner_vert"].data
    corner_verts_array = np.zeros(len(corner_verts), dtype = int)
    corner_verts.foreach_get("value", corner_verts_array)
    loops = mesh.loops
    data = [[] for i in range(len(mesh.vertices))]
    
    match type:
        case "NORMAL": 
            data_array = np.zeros(len(loops) * 3)
            loops.foreach_get("normal", data_array)
            data_array = data_array.reshape(-1,3)
            for loop, vert in enumerate(corner_verts_array):
                data[vert].append(data_array[loop])
            for i in range(len(data)):
                data[i] = np.mean(data[i], axis=0)
        
        case "TANGENT":
            data_array = np.zeros(len(loops) * 3)
            loops.foreach_get("tangent", data_array)
            data_array = data_array.reshape(-1,3)
            for loop, vert in enumerate(corner_verts_array):
                data[vert].append(data_array[loop])
            for i in range(len(data)):
                data[i] = (*np.mean(data[i], axis=0), 1)
                
        case "UV":
            data_array = np.zeros(len(loops) * 2)
            mesh.attributes[layername].data.foreach_get("vector", data_array)
            data_array = data_array.reshape(-1,2)
            for loop, vert in enumerate(corner_verts_array):
                data[vert].append(data_array[loop])
            for i in range(len(data)):
                data[i] = np.mean(data[i], axis=0)
    
    return(data)

def Get3Bits(int):
    bits = format(int,'b')
    while len(bits)<3:
        bits = '0'+bits
    return bits

def getProjectedVertex(vert_co, norm, origin):
    thickness = norm.dot((vert_co - origin))
    return vert_co - thickness * norm, thickness

def cart2bary(obj, face, vert_co):
    mesh = obj.data
    vect_0 = mesh.vertices[face[0]].co
    vect_1 = mesh.vertices[face[1]].co
    vect_2 = mesh.vertices[face[2]].co
    vect_1_0 = vect_1 - vect_0
    vect_2_0 = vect_2 - vect_0
    
    n = (vect_1_0).cross(vect_2_0)
    na = (vect_2 - vect_1).cross(vert_co - vect_1)
    nb = (-vect_2_0).cross(vert_co - vect_2)
    nc = (vect_1_0).cross(vert_co - vect_0)
    
    n_lenght_squared = n.length_squared
    A = (n.dot(na))/n_lenght_squared
    B = (n.dot(nb))/n_lenght_squared
    C = (n.dot(nc))/n_lenght_squared
    return [A,B,C]

def applyTransforms(obj, parent_scale = np.array([1,1,1]), parent_rotation = np.array([0,0,0]), parent_location = np.array([0,0,0]), export = False, local = False, bone = None):
    selectOnly(obj)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    obj.scale = 1/parent_scale
    obj.rotation_euler = 2*(np.pi)-parent_rotation
    obj.location = -parent_location
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    Pos = None
    Radius = None
    if export:
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='MEDIAN')
        Pos = deepcopy(obj.matrix_world.translation)
        Radius = np.linalg.norm(obj.data.vertices[0].co)
        if local:
            Pos = bone.matrix_local.inverted() @ Pos
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    obj.scale = parent_scale
    obj.rotation_euler = parent_rotation
    obj.location = parent_location
    return Pos, Radius

def selectOnly(obj):
    bpy.context.view_layer.objects.active = None
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = obj
    obj.select_set(state=True)
    
def getVertexBary(vert_co, vert_normal, target_obj, target_vertex, target_face, normal_offset, vert_tangent = None):
    mesh = target_obj.data
    t_vert = mesh.vertices[target_vertex]
    target_co = t_vert.co
    target_normal = t_vert.normal
    vertProj, vertThickness = getProjectedVertex(vert_co, target_normal, target_co)
    vertBary = cart2bary(target_obj, target_face, vertProj)
    vertBary[2] = vertThickness
    vert_normal.length = normal_offset
    normProj, normThickness = getProjectedVertex(vert_co + vert_normal, target_normal, target_co)
    normBary = cart2bary(target_obj, target_face, normProj)
    normBary[2] = normThickness
    if vert_tangent:
        tangProj, tangThickness = getProjectedVertex(vert_co + vert_tangent, target_normal, target_co)
        tangBary = cart2bary(target_obj, target_face, tangProj)
        tangBary[2] =  tangThickness
        return vertBary, normBary, tangBary
    else:
        return vertBary, normBary
    
def SplitMesh(mesh):
    corner_verts = mesh.attributes[".corner_vert"].data
    corner_verts_array = np.zeros(len(corner_verts), dtype = int)
    corner_verts.foreach_get("value", corner_verts_array)
    loops = mesh.loops
    n_vertices = len(mesh.vertices)
    n_loops = len(loops)
    select_array = np.zeros(n_vertices, dtype=bool)
    
    # Normals
    data_array = np.zeros(n_loops * 3)
    loops.foreach_get("normal", data_array)
    data_array = data_array.reshape(-1,3).tolist()
    normals = [[] for i in range(n_vertices)]
    for loop, vert in enumerate(corner_verts_array):
        if select_array[vert]:
            continue
        normals[vert].append(data_array[loop])
        if normals[vert][-1] != normals[vert][0]:
            select_array[vert] = True
    
    # UVs
    for uv in mesh.uv_layers:
        data_array = np.zeros(n_loops * 2)
        mesh.attributes[uv.name].data.foreach_get("vector", data_array)
        data_array = data_array.reshape(-1,2).tolist()
        UVs = [[] for i in range(n_vertices)]
        for loop, vert in enumerate(corner_verts_array):
            if select_array[vert]:
                continue
            UVs[vert].append(data_array[loop])
            if UVs[vert][-1] != UVs[vert][0]:
                select_array[vert] = True
    
    # Select Vertices and Split
    if ".select_vert" not in mesh.attributes:
        mesh.attributes.new(".select_vert", "BOOLEAN", "POINT")
    mesh.attributes[".select_vert"].data.foreach_set("value", select_array)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.edge_split(type='EDGE')
    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.object.mode_set(mode='OBJECT')
    
def TriangulateActiveMesh():
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.quads_convert_to_tris(quad_method='SHORTEST_DIAGONAL', ngon_method='BEAUTY')
    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.object.mode_set(mode='OBJECT')
    
def QuadrangulateActiveMesh():
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.tris_convert_to_quads()
    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.object.mode_set(mode='OBJECT')
    
def RemoveDoubles():
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles()
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    
def OrderVertices(mesh, order, index = False):
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(mesh)
    if index:
        for vert_id, v in enumerate(bm.verts):
            v.index = np.where(order == vert_id)[0][0]
    else:
        for vert_id, v in enumerate(bm.verts):
            v.index = order[vert_id]
    bm.verts.sort()
    bmesh.update_edit_mesh(mesh)
    bm.free()
    bpy.ops.object.mode_set(mode='OBJECT')
    
def get_parent_collection(coll, parent_colls):
    for parent_collection in bpy.data.collections:
        if coll.name in parent_collection.children.keys():
            parent_colls.append(parent_collection)
    
def GetCollection(target = "Main", create_if_missing = False, make_active = True):
    active_coll = bpy.context.view_layer.active_layer_collection
    
    if re.search(target, active_coll.name) or ("PhysXAssetType" in active_coll.collection and target == "Main"):
        target_coll = active_coll.collection
        
    else:
        main_coll = None
        target_coll = None
        parent_colls = []
        get_parent_collection(active_coll, parent_colls)
        if "PhysXAssetType" in active_coll.collection:
            main_coll = active_coll.collection
        elif parent_colls:
            if "PhysXAssetType" in parent_colls[0]:
                main_coll = parent_colls[0]
                
        if main_coll:
            main_coll_layer = bpy.context.view_layer.layer_collection
            parent_colls = []
            get_parent_collection(main_coll, parent_colls)
            for col in reversed(parent_colls):
                main_coll_layer = main_coll_layer.children[col.name]
                    
            if target == "Main":
                target_coll = main_coll
                if make_active:
                    bpy.context.view_layer.active_layer_collection = main_coll_layer.children[main_coll.name]
            
            elif target in ["Collision Spheres", "Collision Connections", "Pin Constraints", "Collision Capsules", "No Collision"]:
                for col in main_coll.children:
                    if re.search(target, col.name):
                        target_coll = col
                        break
            
                if not target_coll and create_if_missing:
                    target_coll = bpy.data.collections.new(target)
                    main_coll.children.link(target_coll)
                    
                if target_coll and make_active:
                    bpy.context.view_layer.active_layer_collection = main_coll_layer.children[main_coll.name].children[target_coll.name]
    
    return target_coll

def ImportTemplates():
    #if 'apx_geometry_nodes_templates.blend' not in bpy.data.libraries:
    with bpy.data.libraries.load(os.path.dirname(__file__) + "/templates/apx_geometry_nodes_templates.blend", link = False) as (data_from, data_to):
        data_to.node_groups = data_from.node_groups
    
def GetArmature():
    main_coll = GetCollection(make_active = False)
    arma = None
    if main_coll:
        objects = main_coll.objects
        meshes_bool = [obj.type == 'MESH' for obj in objects]
        meshes = np.array(objects)[meshes_bool]
        armas_bool = [obj.type == 'ARMATURE' for obj in objects]
        
        if not any(armas_bool):
            skeleton = bpy.data.armatures.new(name="Armature")
            arma = object_data_add(bpy.context, skeleton)
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            b = skeleton.edit_bones.new("root")
            b.head = Vector((0,0,0))
            b.tail = Vector((0,1,0))
            bpy.ops.object.mode_set(mode='OBJECT')
            
        else:
            armas = np.array(objects)[armas_bool]
            while armas.size != 1:
                bpy.data.objects.remove(armas[-1], do_unlink=True)
                armas = np.delete(armas, -1)
            arma = armas[0]
            
        for mesh in meshes:
            if mesh.parent != arma:
                selectOnly(mesh)
                bpy.context.view_layer.objects.active = arma
                bpy.ops.object.parent_set(type="ARMATURE_AUTO", xmirror=False, keep_transform=False)
                
    return arma

def set_active_tool(tool_name):
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            override = bpy.context.copy()
            override["space_data"] = area.spaces[0]
            override["area"] = area
            with bpy.context.temp_override(**override):
                bpy.ops.wm.tool_set_by_id(name=tool_name)
            
def getWeightArray(verts, vg):
    idx = vg.index
    weights = []
    for v in verts:
        try:
            weights.append(v.groups[[g.group for g in v.groups].index(idx)].weight)
        except:
            weights.append(0)
    return np.array(weights)

def simValueType(type):
    match type:
        case 'F32':
            return float
        case 'U32':
            return int
        case 'Bool':
            return str2bool
        case 'Vec3': 
            return str2intvec
        case 'Vec4': 
            return str2floatvec
        case 'String':
            return str

def str2bool(string):
    return eval(string.capitalize())

def str2intvec(string):
    return list(map(round, map(float, string.split())))

def str2floatvec(string):
    return list(map(float, string.split()))
    
def GetWind():
    main_coll = GetCollection(make_active = True)
    wind = None
    if main_coll:
        objects = main_coll.objects
        winds_bool = [obj.field.type == "WIND" if obj.field else False for obj in objects]
        
        if not any(winds_bool):
            wind = SetUpWind()
            
        else:
            winds = np.array(objects)[winds_bool]
            while winds.size != 1:
                bpy.data.objects.remove(winds[-1], do_unlink=True)
                winds = np.delete(winds, -1)
            wind = winds[0]
        
    return wind

def GetDrag():
    main_coll = GetCollection(make_active = True)
    drag = None
    if main_coll:
        objects = main_coll.objects
        drags_bool = [obj.field.type == "DRAG" if obj.field else False for obj in objects]
        
        if not any(drags_bool):
            drag = SetUpDrag()
            
        else:
            drags = np.array(objects)[drags_bool]
            while drags.size != 1:
                bpy.data.objects.remove(drags[-1], do_unlink=True)
                drags = np.delete(drags, -1)
            drag = drags[0]
        
    return drag

def SetUpWind():
    bpy.ops.object.effector_add(type='WIND')
    wind = bpy.context.active_object
    wind.rotation_euler = (0, np.pi*0.5, np.pi*0.5)
    wind.field.strength = 2000
    wind.field.noise = 5
    return wind
        
def SetUpDrag():
    bpy.ops.object.effector_add(type='DRAG')
    drag = bpy.context.active_object
    drag.field.linear_drag = 2
    drag.field.quadratic_drag = 2
    return drag

def SetAttributes(elem, dict):
    for k in dict.keys():
        setattr(elem, k, dict[k])
        
def ConvertMode(mode):
    match mode:
        case 'OBJECT':
            return 'OBJECT'
        case 'EDIT_MESH':
            return 'EDIT'
        case 'SCULPT':
            return 'SCULPT'
        case 'PAINT_VERTEX':
            return 'VERTEX_PAINT'
        case 'PAINT_WEIGHT':
            return 'WEIGHT_PAINT'
        case 'PAINT_TEXTURE':
            return 'TEXTURE_PAINT'
        case 'PARTICLE':
            return 'PARTICLE_EDIT'
        
def draw_max_dist_vectors(obj, vg, max_max_dist, coords, normals):
    shader_line = gpu.shader.from_builtin('POLYLINE_SMOOTH_COLOR') if not bpy.app.background else None
    gpu.state.blend_set('ALPHA')
    gpu.state.depth_mask_set(True)
    gpu.state.depth_test_set('LESS')
    region = bpy.context.region
    rv3d = bpy.context.space_data.region_3d
    shader_line.uniform_float("lineWidth", 1)
    shader_line.uniform_float("viewportSize", (region.width, region.height))
    
    max_dists = getWeightArray(obj.data.vertices, vg)
    colors = [[x,x,x,1] for x in max_dists]
    colors = np.repeat(colors, 2, axis = 0).tolist()
    coords2 = list(chain.from_iterable(zip(coords, coords + normals * np.repeat(max_dists, 3, axis=0).reshape(-1,3) * max_max_dist)))
    
    batch = batch_for_shader(shader_line, 'LINES', {"pos": coords2, "color": colors})
    batch.draw(shader_line)
        
    gpu.state.blend_set('NONE')
    
def vertices_global_co_normal(obj):
    mesh = obj.data
    rotation_and_scale = obj.matrix_world.to_3x3().transposed()
    offset = obj.matrix_world.translation
    verts = mesh.vertices
    vlen = len(verts)
    
    vertices_local = np.empty([vlen*3], dtype='f')
    mesh.attributes['position'].data.foreach_get("vector", vertices_local)
    vertices_local = vertices_local.reshape(vlen, 3)
    vertices_global = np.matmul(vertices_local, rotation_and_scale)
    vertices_global += offset
    
    vertices_local = vertices_local.flatten()
    verts.foreach_get("normal", vertices_local)
    vertices_local = vertices_local.reshape(vlen, 3)
    normals_global = np.matmul(vertices_local, rotation_and_scale)
    normals_global += offset

    return vertices_global, normals_global

def setCustomWeightPalette(type):
    elems = bpy.context.preferences.view.weight_color_range.elements
    if len(elems) > 3:
        while len(elems) != 3:
            elems.remove(elems[-1])
    elif len(elems) < 3:
        while len(elems) != 3:
            elems.new(0.5)
    elems[0].position = 0
    elems[2].position = 1
    elems[0].color = (1,0,1,1)
    elems[2].color = (1,1,1,1)
    match type:
        case 'DEFAULT':
            elems[1].position = 0.0000001
            elems[1].color = (0,0,0,1)
            
        case 'DRIVE/LATCH':
            elems[1].position = 0.5
            elems[1].color = (0.5,0.5,0.5,1)
        
def getBones(self, context):
    arma = GetArmature()
    bones = [(bone.name, bone.name, "") for bone in arma.data.bones]
    return bones

def getBonesIndices(self, context):
    arma = GetArmature()
    bones = [(str(i), bone.name, "") for i, bone in enumerate(arma.data.bones)]
    return bones

def getRiggedObjects(self, context):
    objects = []
    for obj in bpy.data.objects:
        if obj.type == "MESH" and obj.parent and obj.parent.type == 'ARMATURE':
            objects.append((obj.name, obj.name, ""))
    return objects

def getObjects(self, context):
    objects = []
    for obj in bpy.data.objects:
        if obj.type == "MESH":
            objects.append((obj.name, obj.name, ""))
    return objects

def getCurvesCollections(self, context):
    colls = []
    for coll in bpy.data.collections:
        if "Hairworks Curves" in coll:
            colls.append((coll.name, coll.name, ""))
    return colls

def getNumberHairVerts():
    nverts = 4
    main_coll = GetCollection(make_active=False)
    if "PhysXAssetType" in main_coll and main_coll["PhysXAssetType"] == 'Hairworks':
        nverts = len(GetArmature().children[0].modifiers['Hairworks'].particle_system.particles[0].hair_keys)
    return nverts
