# -*- coding: utf-8 -*-
# tools/apply_drive.py

import bpy
from io_scene_apx.exporter import export_clothing
from io_scene_apx.exporter.export_clothing import CheckPhysicalPaint

def apply_drive(context, invert):
    obj = bpy.context.active_object
    if obj.type == 'MESH' and "Drive" in obj.data.vertex_colors and "Latch" in obj.data.vertex_colors:
        
        if not invert:
            for face in obj.data.polygons:
                for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                    if CheckPhysicalPaint(obj.data.vertex_colors["Drive"].data[loop_idx].color, 0.1):
                        obj.data.vertex_colors["Drive"].data[loop_idx].color = (1,1,1,1)
                        obj.data.vertex_colors["Latch"].data[loop_idx].color = (1,0,1,1)
                    else:
                        obj.data.vertex_colors["Latch"].data[loop_idx].color = (1,1,1,1)
                        obj.data.vertex_colors["Drive"].data[loop_idx].color = (1,0,1,1)
        else:
            for face in obj.data.polygons:
                for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                    if CheckPhysicalPaint(obj.data.vertex_colors["Latch"].data[loop_idx].color, 0.1):
                        obj.data.vertex_colors["Latch"].data[loop_idx].color = (1,1,1,1)
                        obj.data.vertex_colors["Drive"].data[loop_idx].color = (1,0,1,1)
                    else:
                        obj.data.vertex_colors["Drive"].data[loop_idx].color = (1,1,1,1)
                        obj.data.vertex_colors["Latch"].data[loop_idx].color = (1,0,1,1)    