# -*- coding: utf-8 -*-
# tools/setup_physx.py

import bpy
import random, colorsys
import re
import numpy as np

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
        
        for vc in ["MaximumDistance", "BackstopRadius", "BackstopDistance", "Drive1", "Latch1"]:
            if vc in growthMesh.data.color_attributes:
                growthMesh.data.color_attributes.remove(growthMesh.data.color_attributes[vc])
                
        for vc in growthMesh.data.color_attributes:
            if re.search("(Drive|Latch)[0-9]+", vc.name):
                growthMesh.data.color_attributes.remove(vc)
                
def setup_clothing(context):
    obj = bpy.context.active_object
    if obj.type == 'MESH':
        for vc in ["MaximumDistance", "BackstopRadius", "BackstopDistance", "Drive1", "Latch1"]:
            if vc not in obj.data.color_attributes:
                obj.data.color_attributes.new(name=vc, domain = 'POINT', type = 'BYTE_COLOR')
                for vert in obj.data.vertices:
                    if vc in ["MaximumDistance", "BackstopRadius", "BackstopDistance", "Latch1"]:
                        obj.data.color_attributes[vc].data[vert.index].color = [1,0,1,1]
                    elif vc == "Drive1":
                        obj.data.color_attributes[vc].data[vert.index].color = [1,1,1,1]
        
        cleanUpDriveLatchGroups(obj)
        add_physx_clothing_palette()
                
        if not bpy.context.active_object.data.materials:
            temp_mat = bpy.data.materials.new(name="Material")
            obj.data.materials.append(temp_mat)
            temp_mat.diffuse_color = (*colorsys.hsv_to_rgb(random.random(), .7, .9), 1)
            
        while obj.particle_systems:
            bpy.ops.object.particle_system_remove()
            
def cleanUpDriveLatchGroups(obj, paints = False):
    drive_groups = []
    latch_groups = []
    if obj.data.color_attributes:         
        for vc in obj.data.color_attributes:
            if re.search("Drive[0-9]+", vc.name):
                drive_groups += [vc]
            if re.search("Latch[0-9]+", vc.name):
                latch_groups += [vc]
        if drive_groups:        
            while len(latch_groups) != len(drive_groups):
                if len(latch_groups) > len(drive_groups):
                    latch_groups.remove(latch_groups[-1])
                    obj.data.color_attributes.remove(latch_groups[-1])
                if len(latch_groups) < len(drive_groups):
                    drive_groups.remove(drive_groups[-1])
                    obj.data.color_attributes.remove(drive_groups[-1])
        if drive_groups:   
            for i in range(len(drive_groups)):
                obj.data.color_attributes[drive_groups[i].name].name = "Drive"+str(i+1)
                obj.data.color_attributes[latch_groups[i].name].name = "Latch"+str(i+1)
                
    n_groups = len(drive_groups)
    
    if paints:
        drive_paints_all = []
        latch_paints_all = []
        if n_groups > 0:
            for vert in obj.data.vertices:
                drive_paints_vertex = []
                latch_paints_vertex = []
                for i in range(len(drive_groups)):
                    drive_paints_vertex.append(obj.data.color_attributes["Drive"+str(i+1)].data[vert.index].color[1])
                    latch_paints_vertex.append(obj.data.color_attributes["Latch"+str(i+1)].data[vert.index].color[1])
                drive_paints_all.append(drive_paints_vertex)
                latch_paints_all.append(latch_paints_vertex)
                
        return n_groups, drive_paints_all, latch_paints_all
    else:
        return n_groups
    
def add_physx_clothing_palette():
    pal = bpy.data.palettes.get('PhysX Clothing Palette')
    if not pal:
        pal = bpy.data.palettes.new("PhysX Clothing Palette")
        purple = pal.colors.new()
        purple.color = (1, 0, 1)
        palette_cols = []
        for i in reversed(np.arange(0.001,1.04995,0.04995)):
            palette_cols.append(pal.colors.new())
            palette_cols[-1].color = (i, i, i)
        bpy.context.tool_settings.vertex_paint.palette = pal