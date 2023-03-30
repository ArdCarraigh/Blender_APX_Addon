# -*- coding: utf-8 -*-
# tools/apply_drive.py

import bpy
from io_scene_apx.exporter import export_clothing
from io_scene_apx.exporter.export_clothing import CheckPhysicalPaint
from io_scene_apx.tools import setup_physx
from io_scene_apx.tools.setup_physx import cleanUpDriveLatchGroups, add_physx_clothing_palette

def apply_drive(context, group, invert):
    obj = bpy.context.active_object
    
    n_groups, drive_paints, latch_paints = cleanUpDriveLatchGroups(obj, True)
    
    add_physx_clothing_palette()
    
    if obj.type == 'MESH' and "Drive"+group in obj.data.color_attributes and "Latch"+group in obj.data.color_attributes:
        if not invert:
            for vert in obj.data.vertices:
                if CheckPhysicalPaint(obj.data.color_attributes["Drive"+group].data[vert.index].color, 0.1):
                    if obj.data.color_attributes["Drive"+group].data[vert.index].color[1] > 0.6:
                        obj.data.color_attributes["Drive"+group].data[vert.index].color = (1,1,1,1)
                        obj.data.color_attributes["Latch"+group].data[vert.index].color = (1,0,1,1)
                        for i in range(n_groups):
                            if str(i+1) != group:
                                obj.data.color_attributes["Drive"+str(i+1)].data[vert.index].color = (0.25,0.25,0.25,1)
                else:
                    if any([x > 0.3 for x in latch_paints[vert.index][:int(group)-1] + latch_paints[vert.index][int(group):]]):
                        obj.data.color_attributes["Latch"+group].data[vert.index].color = (0.25,0.25,0.25,1)
                    else:
                        obj.data.color_attributes["Latch"+group].data[vert.index].color = (1,1,1,1)
                        for i in range(n_groups):
                            if str(i+1) != group:
                                obj.data.color_attributes["Latch"+str(i+1)].data[vert.index].color = (0.25,0.25,0.25,1)
                    if any([x > 0.3 for x in drive_paints[vert.index][:int(group)-1] + drive_paints[vert.index][int(group):]]):
                        obj.data.color_attributes["Drive"+group].data[vert.index].color = (0.25,0.25,0.25,1)
                    else:
                        obj.data.color_attributes["Drive"+group].data[vert.index].color = (1,0,1,1)
        
        else:
            for vert in obj.data.vertices:
                if CheckPhysicalPaint(obj.data.color_attributes["Latch"+group].data[vert.index].color, 0.1):
                    if obj.data.color_attributes["Latch"+group].data[vert.index].color[1] > 0.6:
                        obj.data.color_attributes["Latch"+group].data[vert.index].color = (1,1,1,1)
                        obj.data.color_attributes["Drive"+group].data[vert.index].color = (1,0,1,1)
                        for i in range(n_groups):
                            if str(i+1) != group:
                                obj.data.color_attributes["Latch"+str(i+1)].data[vert.index].color = (0.25,0.25,0.25,1)
                else:
                    if any([x > 0.3 for x in drive_paints[vert.index][:int(group)-1] + drive_paints[vert.index][int(group):]]):
                        obj.data.color_attributes["Drive"+group].data[vert.index].color = (0.25,0.25,0.25,1)
                    else:
                        obj.data.color_attributes["Drive"+group].data[vert.index].color = (1,1,1,1)
                        for i in range(n_groups):
                            if str(i+1) != group:
                                obj.data.color_attributes["Drive"+str(i+1)].data[vert.index].color = (0.25,0.25,0.25,1)
                    if any([x > 0.3 for x in latch_paints[vert.index][:int(group)-1] + latch_paints[vert.index][int(group):]]):
                        obj.data.color_attributes["Latch"+group].data[vert.index].color = (0.25,0.25,0.25,1)
                    else:
                        obj.data.color_attributes["Latch"+group].data[vert.index].color = (1,0,1,1)