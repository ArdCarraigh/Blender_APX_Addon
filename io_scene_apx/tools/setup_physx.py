# -*- coding: utf-8 -*-
# tools/setup_physx.py

import bpy
import random, colorsys

def setup_hairworks(context):
    growthMesh = bpy.context.active_object
    if growthMesh.type == 'MESH':
        bpy.ops.object.particle_system_add()
        growthMesh.particle_systems[0].settings.type = 'HAIR'
        growthMesh.particle_systems[0].settings.hair_step = 5
        growthMesh.particle_systems[0].settings.display_step = 3
        growthMesh.particle_systems[0].settings.emit_from = 'VERT'
        growthMesh.particle_systems[0].settings.use_emit_random = False
        growthMesh.particle_systems[0].settings.count = len(growthMesh.data.vertices)
        growthMesh.particle_systems[0].settings.hair_length = 0.1
        bpy.ops.object.mode_set(mode='PARTICLE_EDIT')
        bpy.context.tool_settings.particle_edit.use_emitter_deflect = False
        bpy.context.tool_settings.particle_edit.display_step = 3
        bpy.ops.object.mode_set(mode='OBJECT')
        
        for vc in ["MaximumDistance", "BackstopRadius", "BackstopDistance", "Drive", "Latch"]:
            if vc in growthMesh.data.vertex_colors:
                growthMesh.data.vertex_colors.remove(growthMesh.data.vertex_colors[vc])
                
def setup_clothing(context):
    obj = bpy.context.active_object
    if obj.type == 'MESH':
        for vc in ["MaximumDistance", "BackstopRadius", "BackstopDistance", "Drive", "Latch"]:
            if vc not in obj.data.vertex_colors:
                obj.data.vertex_colors.new(name=vc)
                for face in obj.data.polygons:
                    for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                        if vc in ["MaximumDistance", "BackstopRadius", "BackstopDistance", "Latch"]:
                            obj.data.vertex_colors[vc].data[loop_idx].color = [1,0,1,1]
                        elif vc == "Drive":
                            obj.data.vertex_colors[vc].data[loop_idx].color = [1,1,1,1]
                
        if not bpy.context.active_object.data.materials:
            temp_mat = bpy.data.materials.new(name="Material")
            obj.data.materials.append(temp_mat)
            temp_mat.diffuse_color = (*colorsys.hsv_to_rgb(random.random(), .7, .9), 1)
            
        while obj.particle_systems:
            bpy.ops.object.particle_system_remove()