# -*- coding: utf-8 -*-
# tools/setup_tools.py

import bpy
import random, colorsys
import re
import numpy as np
from io_mesh_apx.tools.paint_tools import cleanUpDriveLatchGroups, add_physx_clothing_palette

def setup_hairworks(context):
    obj = bpy.context.active_object
    mesh = obj.data
    if obj.type == 'MESH':
        bpy.ops.object.particle_system_add()
        obj.particle_systems[0].settings.type = 'HAIR'
        obj.particle_systems[0].settings.hair_step = 5
        obj.particle_systems[0].settings.display_step = 3
        obj.particle_systems[0].settings.emit_from = 'VERT'
        obj.particle_systems[0].settings.use_emit_random = False
        obj.particle_systems[0].settings.count = len(mesh.vertices)
        obj.particle_systems[0].settings.hair_length = 0.1
        bpy.ops.object.mode_set(mode='PARTICLE_EDIT')
        bpy.context.tool_settings.particle_edit.use_emitter_deflect = False
        bpy.context.tool_settings.particle_edit.display_step = 3
        bpy.ops.object.mode_set(mode='OBJECT')
        
        if not mesh.materials:
            temp_mat = bpy.data.materials.new(name="Material")
            mesh.materials.append(temp_mat)
            temp_mat.diffuse_color = (*colorsys.hsv_to_rgb(random.random(), .7, .9), 1)
        
        for vc in ["MaximumDistance", "BackstopRadius", "BackstopDistance", "Drive1", "Latch1"]:
            if vc in mesh.color_attributes:
                mesh.color_attributes.remove(mesh.color_attributes[vc])
                
        for vc in mesh.color_attributes:
            if re.search("(Drive|Latch)[0-9]+", vc.name):
                mesh.color_attributes.remove(vc)
                
def setup_clothing(context):
    obj = bpy.context.active_object
    mesh = obj.data
    if obj.type == 'MESH':
        n_data_array = len(mesh.vertices)
        magenta_array = np.full((n_data_array,4), [1,0,1,1]).flatten()
        white_array = np.full((n_data_array,4), [1,1,1,1]).flatten()
        for vc in ["MaximumDistance", "BackstopRadius", "BackstopDistance", "Drive1", "Latch1"]:
            if vc not in mesh.color_attributes:
                v_col = mesh.color_attributes.new(name=vc, domain = 'POINT', type = 'BYTE_COLOR')
                if vc == 'Drive1':
                    v_col.data.foreach_set("color", white_array)
                else:
                    v_col.data.foreach_set("color", magenta_array)
        
        cleanUpDriveLatchGroups(obj)
        add_physx_clothing_palette()
                
        if not mesh.materials:
            temp_mat = bpy.data.materials.new(name="Material")
            mesh.materials.append(temp_mat)
            temp_mat.diffuse_color = (*colorsys.hsv_to_rgb(random.random(), .7, .9), 1)
            
        while obj.particle_systems:
            bpy.ops.object.particle_system_remove()