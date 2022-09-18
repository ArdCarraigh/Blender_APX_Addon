# -*- coding: utf-8 -*-
# tools/apply_drive.py

import bpy
from io_scene_apx.exporter import export_clothing
from io_scene_apx.exporter.export_clothing import CheckPhysicalPaint

def apply_drive(context, invert):
    obj = bpy.context.active_object
    if obj.type == 'MESH' and "Drive" in obj.data.color_attributes and "Latch" in obj.data.color_attributes:
        
        if not invert:
            for vert in obj.data.vertices:
                if CheckPhysicalPaint(obj.data.color_attributes["Drive"].data[vert.index].color, 0.1):
                    obj.data.color_attributes["Drive"].data[vert.index].color = (1,1,1,1)
                    obj.data.color_attributes["Latch"].data[vert.index].color = (1,0,1,1)
                else:
                    obj.data.color_attributes["Latch"].data[vert.index].color = (1,1,1,1)
                    obj.data.color_attributes["Drive"].data[vert.index].color = (1,0,1,1)
        else:
            for vert in obj.data.vertices:
                if CheckPhysicalPaint(obj.data.color_attributes["Latch"].data[vert.index].color, 0.1):
                    obj.data.color_attributes["Latch"].data[vert.index].color = (1,1,1,1)
                    obj.data.color_attributes["Drive"].data[vert.index].color = (1,0,1,1)
                else:
                    obj.data.color_attributes["Drive"].data[vert.index].color = (1,1,1,1)
                    obj.data.color_attributes["Latch"].data[vert.index].color = (1,0,1,1)    