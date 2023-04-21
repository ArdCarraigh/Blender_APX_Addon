# -*- coding: utf-8 -*-
# tools/paint_tools.py

import bpy
import numpy as np
import re

def cleanUpDriveLatchGroups(obj, paints = False):
    assert(obj.type == 'MESH')
    drive_groups = []
    latch_groups = [] 
    mesh = obj.data        
    for vc in mesh.color_attributes:
        if re.search("Drive[0-9]+", vc.name):
            drive_groups += [vc]
        if re.search("Latch[0-9]+", vc.name):
            latch_groups += [vc]
    if drive_groups:        
        while len(latch_groups) != len(drive_groups):
            if len(latch_groups) > len(drive_groups):
                latch_groups.remove(latch_groups[-1])
                mesh.color_attributes.remove(latch_groups[-1])
            if len(latch_groups) < len(drive_groups):
                drive_groups.remove(drive_groups[-1])
                mesh.color_attributes.remove(drive_groups[-1])
    if drive_groups:   
        for i, [d_vcol, l_vcol] in enumerate(zip(drive_groups, latch_groups)):
            idx = str(i + 1)
            d_vcol.name = "Drive"+idx
            l_vcol.name = "Latch"+idx
                
    n_groups = len(drive_groups)
    
    drive_paints_all = []
    latch_paints_all = []
    if paints and n_groups:
        data_array = np.zeros(len(mesh.vertices)*4)
        for d_vcol, l_vcol in zip(drive_groups, latch_groups):
            d_vcol.data.foreach_get("color", data_array)
            drive_paints_all.append(list(data_array[1::4]))
            l_vcol.data.foreach_get("color", data_array)
            latch_paints_all.append(list(data_array[1::4]))
            
        return n_groups, np.array(drive_paints_all).T, np.array(latch_paints_all).T
    else:
        return n_groups
    
def add_physx_clothing_palette():
    pal = bpy.data.palettes.get('PhysX Clothing Palette')
    if not pal:
        pal = bpy.data.palettes.new("PhysX Clothing Palette")
        purple = pal.colors.new()
        purple.color = (1, 0, 1)
        palette_cols = []
        for i in np.flip(np.arange(0.001,1.04995,0.04995)):
            palette_cols.append(pal.colors.new())
            palette_cols[-1].color = (i, i, i)
        bpy.context.tool_settings.vertex_paint.palette = pal
        
def CheckPhysicalPaint(vertexColor, threshold):
    check = False
    if (vertexColor[1] <= vertexColor[0]+threshold and
    vertexColor[1] >= vertexColor[0]-threshold and
    vertexColor[2] <= vertexColor[0]+threshold and 
    vertexColor[2] >= vertexColor[0]-threshold):
        check = True
    return check
                
def add_drive_latch_group(context):
    obj = bpy.context.active_object
    mesh = obj.data
      
    n_groups, drive_paints, latch_paints = cleanUpDriveLatchGroups(obj, True)
    n_groups += 1
    
    add_physx_clothing_palette()
    
    d_vcol = mesh.color_attributes.new(name="Drive"+str(n_groups), domain = 'POINT', type = 'BYTE_COLOR')
    l_vcol = mesh.color_attributes.new(name="Latch"+str(n_groups), domain = 'POINT', type = 'BYTE_COLOR')
    
    n_data_array = len(mesh.vertices)
    white_array = np.full((n_data_array,4), [1,1,1,1]).flatten()
    drive_array = np.full((n_data_array,4), [1,0,1,1], dtype=float)
    latch_array = np.full((n_data_array,4), [1,0,1,1], dtype=float)
    
    if n_groups <= 1:
        # For some reason you cant declare two color attributes in a row in Blender 3.5,
        # so I re-access the first declared one through its name, instead of the variable storing it
        mesh.color_attributes["Drive"+str(n_groups)].data.foreach_set("color", white_array)
        l_vcol.data.foreach_set("color", latch_array.flatten())  
    else:
        drive_array[np.any(drive_paints > 0.3, axis=1)] = [0.25,0.25,0.25,1]
        latch_array[np.any(latch_paints > 0.3, axis=1)] = [0.25,0.25,0.25,1]
        mesh.color_attributes["Drive"+str(n_groups)].data.foreach_set("color", drive_array.flatten())
        l_vcol.data.foreach_set("color", latch_array.flatten())
                
def apply_drive(context, group, invert):
    obj = bpy.context.active_object
    mesh = obj.data
    add_physx_clothing_palette()
    
    n_groups, drive_paints, latch_paints = cleanUpDriveLatchGroups(obj, True)
    
    drive_name = "Drive"+group
    latch_name = "Latch"+group
    int_group = int(group)-1
    
    check_array_drive = np.any(np.delete(drive_paints, int_group, axis=1) > 0.3, axis=1)
    check_array_latch = np.any(np.delete(latch_paints, int_group, axis=1) > 0.3, axis=1)
    array_length = len(mesh.vertices)*4
    drive_array = np.zeros(array_length)
    latch_array = np.zeros(array_length)
    mesh.color_attributes[drive_name].data.foreach_get("color", drive_array)
    mesh.color_attributes[latch_name].data.foreach_get("color", latch_array)
    drive_array = drive_array.reshape(-1,4)
    latch_array = latch_array.reshape(-1,4)
    
    if not invert:
        check_array = np.array([(x[1]>0.3) & CheckPhysicalPaint(x, 0.1) for x in drive_array])
        drive_array[check_array] = [1,1,1,1]
        drive_array[~check_array] = [1,0,1,1]
        drive_array[~check_array & check_array_drive] = [0.25,0.25,0.25,1]
        latch_array[check_array] = [1,0,1,1]
        latch_array[~check_array & check_array_latch] = [0.25,0.25,0.25,1]
        drive_array = drive_array.flatten()
        latch_array = latch_array.flatten()
        mesh.color_attributes[drive_name].data.foreach_set("color", drive_array)
        mesh.color_attributes[latch_name].data.foreach_set("color", latch_array)
        for i in range(n_groups):
            group_id = str(i+1)
            if group_id != group:
                drive_name = "Drive"+group_id
                latch_name = "Latch"+group_id
                mesh.color_attributes[drive_name].data.foreach_get("color", drive_array)
                mesh.color_attributes[latch_name].data.foreach_get("color", latch_array)
                drive_array.reshape(-1,4)[check_array] = [0.25,0.25,0.25,1]
                latch_array.reshape(-1,4)[check_array] = [1,0,1,1]
                mesh.color_attributes[drive_name].data.foreach_set("color", drive_array)
                mesh.color_attributes[latch_name].data.foreach_set("color", latch_array)
    
    else:
        check_array = np.array([(x[1]>0.3) & CheckPhysicalPaint(x, 0.1) for x in latch_array])
        latch_array[check_array] = [1,1,1,1]
        latch_array[~check_array] = [1,0,1,1]
        latch_array[~check_array & check_array_latch] = [0.25,0.25,0.25,1]
        drive_array[check_array] = [1,0,1,1]
        drive_array[~check_array & check_array_drive] = [0.25,0.25,0.25,1]
        latch_array = latch_array.flatten()
        drive_array = drive_array.flatten()
        mesh.color_attributes[latch_name].data.foreach_set("color", latch_array)
        mesh.color_attributes[drive_name].data.foreach_set("color", drive_array)
        for i in range(n_groups):
            group_id = str(i+1)
            if group_id != group:
                latch_name = "Latch"+group_id
                drive_name = "Drive"+group_id
                mesh.color_attributes[latch_name].data.foreach_get("color", latch_array)
                mesh.color_attributes[drive_name].data.foreach_get("color", drive_array)
                latch_array.reshape(-1,4)[check_array] = [0.25,0.25,0.25,1]
                drive_array.reshape(-1,4)[check_array] = [1,0,1,1]
                mesh.color_attributes[latch_name].data.foreach_set("color", latch_array)
                mesh.color_attributes[drive_name].data.foreach_set("color", drive_array)