# -*- coding: utf-8 -*-
# tools/create_curve.py

import bpy
import copy
from bpy_extras.object_utils import object_data_add
    
def create_curve(context):
    # Get the growthmesh
    growthMesh = bpy.context.active_object.evaluated_get(context.evaluated_depsgraph_get())
    meshScale = copy.deepcopy(growthMesh.scale)
    meshRot = copy.deepcopy(growthMesh.rotation_euler)
    meshLoc = copy.deepcopy(growthMesh.location)
    
    # Make a curve collection
    parent_coll = bpy.context.view_layer.active_layer_collection
    curve_coll = bpy.data.collections.new("Curves")
    curve_coll_name = curve_coll.name
    parent_coll.collection.children.link(curve_coll)
    bpy.context.view_layer.active_layer_collection = parent_coll.children[curve_coll_name]
    
    # Create curves from guides
    hairs = growthMesh.particle_systems[0].particles
    for hair in hairs:
        # create the Curve Datablock
        curveData = bpy.data.curves.new('myCurve', type='CURVE')
        curveData.dimensions = '3D'
        curveData.resolution_u = 2
        curveData.bevel_depth = 0
        
        # map coords to spline
        polyline = curveData.splines.new('POLY')
        polyline.points.add(len(hair.hair_keys) - 1)
        for j in range(len(hair.hair_keys)):
            polyline.points[j].co = (*hair.hair_keys[j].co, 1)
        
        # Add the curves to the scene
        object_data_add(context, curveData)
        bpy.context.active_object.scale = meshScale
        bpy.context.active_object.rotation_euler = meshRot
        bpy.context.active_object.location = meshLoc
        
    #Make parent collection active again
    bpy.context.view_layer.active_layer_collection = parent_coll
    