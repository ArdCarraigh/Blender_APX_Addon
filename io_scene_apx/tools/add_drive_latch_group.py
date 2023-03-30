# -*- coding: utf-8 -*-
# tools/add_drive_latch_group.py

import bpy
from io_scene_apx.tools import setup_physx
from io_scene_apx.tools.setup_physx import cleanUpDriveLatchGroups, add_physx_clothing_palette
                
def add_drive_latch_group(context):
    obj = bpy.context.active_object
      
    n_groups, drive_paints, latch_paints = cleanUpDriveLatchGroups(obj, True)
    n_groups += 1
    
    add_physx_clothing_palette()
        
    obj.data.color_attributes.new(name="Drive"+str(n_groups), domain = 'POINT', type = 'BYTE_COLOR')
    obj.data.color_attributes.new(name="Latch"+str(n_groups), domain = 'POINT', type = 'BYTE_COLOR')
    
    if n_groups <= 1:
        for vert in obj.data.vertices:
            obj.data.color_attributes["Drive"+str(n_groups)].data[vert.index].color = [1,1,1,1]
            obj.data.color_attributes["Latch"+str(n_groups)].data[vert.index].color = [1,0,1,1]
            
    else:
        for vert in obj.data.vertices:
            if any([x > 0.3 for x in drive_paints[vert.index]]):
                obj.data.color_attributes["Drive"+str(n_groups)].data[vert.index].color = [0.25,0.25,0.25,1]
            else:
                obj.data.color_attributes["Drive"+str(n_groups)].data[vert.index].color = [1,0,1,1]
            if any([x > 0.3 for x in latch_paints[vert.index]]):
                obj.data.color_attributes["Latch"+str(n_groups)].data[vert.index].color = (0.25,0.25,0.25,1)
            else:
                obj.data.color_attributes["Latch"+str(n_groups)].data[vert.index].color = [1,0,1,1]