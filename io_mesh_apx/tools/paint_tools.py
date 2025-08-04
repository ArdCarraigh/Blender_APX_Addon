# -*- coding: utf-8 -*-
# tools/paint_tools.py

import bpy
import numpy as np
import re
from io_mesh_apx.utils import getWeightArray

def cleanUpDriveLatchGroups(obj, paints = False):
    assert(obj.type == 'MESH')
    drive_groups = []
    latch_groups = [] 
    vgroups = obj.vertex_groups      
    for vg in vgroups:
        if re.search("PhysXDrive[0-9]+", vg.name):
            drive_groups.append(vg)
        if re.search("PhysXLatch[0-9]+", vg.name):
            latch_groups.append(vg)
    if drive_groups:        
        while len(latch_groups) != len(drive_groups):
            if len(latch_groups) > len(drive_groups):
                latch_groups.remove(latch_groups[-1])
                vgroups.remove(latch_groups[-1])
            if len(latch_groups) < len(drive_groups):
                drive_groups.remove(drive_groups[-1])
                vgroups.remove(drive_groups[-1])
    if drive_groups:   
        for i, [d_vg, l_vg] in enumerate(zip(drive_groups, latch_groups)):
            idx = str(i + 1)
            d_vg.name = "PhysXDrive"+idx
            l_vg.name = "PhysXLatch"+idx
                
    n_groups = len(drive_groups)
    
    if paints and n_groups:
        drive_paints_all = []
        latch_paints_all = []
        verts = obj.data.vertices
        for d_vg, l_vg in zip(drive_groups, latch_groups):
            drive_paints_all.append(getWeightArray(verts, d_vg))
            latch_paints_all.append(getWeightArray(verts, l_vg))
            
        return n_groups, np.array(drive_paints_all).T, np.array(latch_paints_all).T
    else:
        return n_groups
                
def add_drive_latch_group(obj):
    mesh = obj.data
    n_verts = len(mesh.vertices)
      
    n_groups, drive_paints, latch_paints = cleanUpDriveLatchGroups(obj, True)
    n_groups += 1
    
    d_vg = obj.vertex_groups.new(name="PhysXDrive"+str(n_groups))
    l_vg = obj.vertex_groups.new(name="PhysXLatch"+str(n_groups))
    
    drive_array = np.zeros(n_verts, dtype=float)
    latch_array = np.zeros(n_verts, dtype=float)
    
    if n_groups <= 1:
        for k in range(n_verts):
            d_vg.add([k], 1, 'REPLACE')
            l_vg.add([k], 0, 'REPLACE')
    else:
        drive_array[np.any(drive_paints > 0.6, axis=1)] = 0.5
        latch_array[np.any(latch_paints > 0.6, axis=1)] = 0.5
        for k in range(n_verts):
            d_vg.add([k], drive_array[k], 'REPLACE')
            l_vg.add([k], latch_array[k], 'REPLACE')
                
def apply_drive(obj, group, invert):
    mesh = obj.data
    vgroups = obj.vertex_groups
    verts = mesh.vertices
    n_verts = len(verts)
    
    n_groups, drive_paints, latch_paints = cleanUpDriveLatchGroups(obj, True)
    
    drive_name = "PhysXDrive"+str(group)
    latch_name = "PhysXLatch"+str(group)
    group -= 1
    
    check_array_drive = np.any(np.delete(drive_paints, group, axis=1) > 0.6, axis=1)
    check_array_latch = np.any(np.delete(latch_paints, group, axis=1) > 0.6, axis=1)
    drive_array = getWeightArray(verts, vgroups[drive_name])
    latch_array = getWeightArray(verts, vgroups[latch_name])
    
    if not invert:
        check_array = drive_array > 0.6
        drive_array[check_array] = 1
        drive_array[~check_array] = 0
        drive_array[~check_array & check_array_drive] = 0.5
        latch_array[check_array] = 0
        latch_array[~check_array & check_array_latch] = 0.5
        for k in range(n_verts):
            vgroups[drive_name].add([k], drive_array[k], 'REPLACE')
            vgroups[latch_name].add([k], latch_array[k], 'REPLACE')
        for i in range(n_groups):
            group_id = str(i+1)
            if i != group:
                drive_name = "PhysXDrive"+group_id
                latch_name = "PhysXLatch"+group_id
                drive_array = getWeightArray(verts, vgroups[drive_name])
                latch_array = getWeightArray(verts, vgroups[latch_name])
                drive_array[check_array] = 0.5
                latch_array[check_array] = 0
                for k in range(n_verts):
                    vgroups[drive_name].add([k], drive_array[k], 'REPLACE')
                    vgroups[latch_name].add([k], latch_array[k], 'REPLACE')
    
    else:
        check_array = latch_array > 0.6
        latch_array[check_array] = 1
        latch_array[~check_array] = 0
        latch_array[~check_array & check_array_latch] = 0.5
        drive_array[check_array] = 0
        drive_array[~check_array & check_array_drive] = 0.5
        for k in range(n_verts):
            vgroups[latch_name].add([k], latch_array[k], 'REPLACE')
            vgroups[drive_name].add([k], drive_array[k], 'REPLACE')
        for i in range(n_groups):
            group_id = str(i+1)
            if i != group:
                latch_name = "PhysXLatch"+group_id
                drive_name = "PhysXDrive"+group_id
                latch_array = getWeightArray(verts, vgroups[latch_name])
                drive_array = getWeightArray(verts, vgroups[drive_name])
                latch_array[check_array] = 0.5
                drive_array[check_array] = 0
                for k in range(n_verts):
                    vgroups[latch_name].add([k], latch_array[k], 'REPLACE')
                    vgroups[drive_name].add([k], drive_array[k], 'REPLACE')
                    
def applyDriveLatch(obj):
    vgroups = obj.vertex_groups
    active_name = vgroups[vgroups.active_index].name
    if re.search("PhysXDrive[0-9]+", active_name):
        apply_drive(obj, int(active_name[10:]), False)
    elif re.search("PhysXLatch[0-9]+", active_name):
        apply_drive(obj, int(active_name[10:]), True)
    return vgroups

def floodAllVertices(context, obj, group_name, value):
    vgroups = obj.vertex_groups
    for k in range(len(obj.data.vertices)):
        vgroups[group_name].add([k], value, 'REPLACE')
    
def smoothAllVertices(context, obj, group_name):
    vgroups = obj.vertex_groups
    vgroups.active_index = vgroups[group_name].index
    bpy.ops.object.vertex_group_smooth(group_select_mode='ACTIVE', factor=1, repeat=1)
    
def copyMaxDistance(context, obj):
    vgroups = obj.vertex_groups
    verts = obj.data.vertices
    weights = getWeightArray(verts, vgroups['PhysXMaximumDistance']) * obj['maximumMaxDistance']
    for k in range(len(verts)):
        vgroups['PhysXBackstopDistance'].add([k], weights[k], 'REPLACE')