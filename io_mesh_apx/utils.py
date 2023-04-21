# -*- coding: utf-8 -*-
# utils.py

import bpy
import numpy as np
from mathutils import kdtree, Vector
from copy import deepcopy

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
    bpy.ops.outliner.orphans_purge(override)
    
def getConnectedVertices(obj, v_idx, steps):
    interest_verts = [v_idx]
    for i in range(steps):
        connec_verts = []
        for edge in obj.data.edges:
            edge_verts = list(edge.vertices)
            check = any(item in interest_verts for item in edge_verts)
            if check is True:
                connec_verts.extend(edge_verts)
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
            index = None
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
    vertices_loops = np.array([list(zip(face.vertices, face.loop_indices)) for face in mesh.polygons]).reshape(-1,2)
    loops = mesh.loops
    data = [[] for i in range(len(mesh.vertices))]
    
    if type == "NORMAL": 
        data_array = np.zeros(len(loops) * 3)
        loops.foreach_get("normal", data_array)
        data_array = data_array.reshape(-1,3)
        for loop in vertices_loops:
            data[loop[0]].append(data_array[loop[1]])
        for i in range(len(data)):
            data[i] = np.mean(data[i], axis=0)
    
    elif type == "TANGENT":
        data_array = np.zeros(len(loops) * 3)
        loops.foreach_get("tangent", data_array)
        data_array = data_array.reshape(-1,3)
        for loop in vertices_loops:
            data[loop[0]].append(data_array[loop[1]])
        for i in range(len(data)):
            data[i] = (*np.mean(data[i], axis=0), 1)
            
    elif type == "UV":
        data_array = np.zeros(len(loops) * 2)
        mesh.attributes[layername].data.foreach_get("vector", data_array)
        data_array = data_array.reshape(-1,2)
        for loop in vertices_loops:
            data[loop[0]].append(data_array[loop[1]])
        for i in range(len(data)):
            data[i] = np.mean(data[i], axis=0)
    
    return(data)

def Get3Bits(int):
    bits = format(int,'b')
    while len(bits)<3:
        bits = '0'+bits
    return bits

def getSubmeshID(vertID, intervals):
    id = -1
    for i in range(len(intervals)):
        if vertID >= intervals[i][0] and vertID <= intervals[i][1]:
            id = i
            break
    return id

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
    target_co = mesh.vertices[target_vertex].co
    target_normal = mesh.vertices[target_vertex].normal
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
    vertices_loops = np.array([list(zip(face.vertices, face.loop_indices)) for face in mesh.polygons]).reshape(-1,2)
    loops = mesh.loops
    n_vertices = len(mesh.vertices)
    n_loops = len(loops)
    
    # Normals
    data_array = np.zeros(n_loops * 3)
    loops.foreach_get("normal", data_array)
    data_array = data_array.reshape(-1,3)
    normals = [[] for i in range(n_vertices)]
    for loop in vertices_loops:
        normals[loop[0]].append(data_array[loop[1]])
    for i in range(n_vertices):
        normals[i] = np.any(np.array(normals[i]) != normals[i][0])
    
    # UVs
    UVs_all = np.zeros(n_vertices, dtype=bool)
    for uv in mesh.uv_layers:
        data_array = np.zeros(n_loops * 2)
        mesh.attributes[uv.name].data.foreach_get("vector", data_array)
        data_array = data_array.reshape(-1,2)
        UVs = [[] for i in range(n_vertices)]
        for loop in vertices_loops:
            UVs[loop[0]].append(data_array[loop[1]])
        for i in range(n_vertices):
            UVs[i] = np.any(np.array(UVs[i]) != UVs[i][0])
        UVs_all += np.array(UVs)
    
    # Select Vertices and Split   
    select_array = UVs_all + np.array(normals)
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
    
def RemoveDoubles():
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles()
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    