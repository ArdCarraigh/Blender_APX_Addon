# -*- coding: utf-8 -*-
# tools/shape_hair.py

import bpy
import math
import random
import copy
import numpy as np
from math import sqrt
from bpy_extras.object_utils import object_data_add
from mathutils import Vector, Matrix

def shape_hair(context):
    growthMesh = bpy.context.active_object
    curves = bpy.context.view_layer.active_layer_collection.collection.objects
    segmentsCount = len(curves[0].data.splines[0].points)
    correctCurves = 0
    for curve in curves:
        if curve.type == 'CURVE' or len(curve.data.splines[0].points) == segmentsCount:
            correctCurves += 1
        else:
            print("Something is wrong with your curve collection.")
            break
                
    if correctCurves == len(curves):
        bpy.ops.object.particle_system_add()
        growthMesh.particle_systems[0].settings.type = 'HAIR'
        growthMesh.particle_systems[0].settings.hair_step = segmentsCount - 1
        growthMesh.particle_systems[0].settings.display_step = int(round(sqrt(segmentsCount),0)) + 1 
        growthMesh.particle_systems[0].settings.emit_from = 'VERT'
        growthMesh.particle_systems[0].settings.use_emit_random = False
        growthMesh.particle_systems[0].settings.count = len(growthMesh.data.vertices)
        growthMesh2 = growthMesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
        bpy.ops.object.mode_set(mode='PARTICLE_EDIT')
        bpy.context.tool_settings.particle_edit.use_emitter_deflect = False
        bpy.context.tool_settings.particle_edit.display_step = int(round(sqrt(segmentsCount),0)) + 1 
        bpy.ops.particle.disconnect_hair()
        
        for i in range(len(curves)):
            for j in range(0,len(curves[i].data.splines[0].points)):
                growthMesh2.particle_systems[0].particles[i].hair_keys[j].co_object_set(
                    object = growthMesh2,
                    modifier = growthMesh2.modifiers[-1],
                    particle = growthMesh2.particle_systems[0].particles[i],
                    co = curves[i].data.splines[0].points[j].co[0:3]
                )
                
        bpy.ops.particle.connect_hair()
        bpy.ops.object.mode_set(mode='OBJECT')