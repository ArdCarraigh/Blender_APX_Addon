# -*- coding: utf-8 -*-
# tools/cloth_tools.py

import bpy
from io_mesh_apx.utils import GetCollection
from io_mesh_apx.templates.template_clothing_setup import *
                    
def copyClothSimulation(context, collection):
    main_coll = GetCollection(make_active = False)
    asset = bpy.data.collections[collection]
    for key in templateClothSim.keys():
        if key in asset:
            main_coll[key] = asset[key]
            
def copyClothMaterial(context, object):
    main_obj = bpy.context.active_object
    obj = bpy.data.objects[object]
    for key in templateClothMat.keys():
        if key in obj:
            main_obj[key] = obj[key]