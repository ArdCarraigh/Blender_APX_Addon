# -*- coding: utf-8 -*-
#ui/hair_mat_panel.py

import bpy
import numpy as np
from bpy.props import BoolProperty, FloatProperty, IntProperty, EnumProperty, StringProperty, FloatVectorProperty, PointerProperty
from io_mesh_apx.utils import GetCollection, GetArmature, getBonesIndices, GetWind
    
class PhysXHairMaterialPanel(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_PhysX_hair_mat_panel'
    bl_parent_id = 'VIEW3D_PT_PhysX_panel'
    bl_label = 'Hairworks Material'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'PhysX'
    bl_options = {'HIDE_HEADER'}
    
    def draw(self, context):
        layout = self.layout
        physx = context.window_manager.physx
        wm = physx.hair
        if physx.PhysXSubPanel == 'hair_mat':
            main_coll = GetCollection(make_active=False)
            arma = GetArmature()
            obj = arma.children[0]
            if main_coll and obj and obj.type == 'MESH':
                row = layout.row()
                box = row.box()
                box.label(text="General")
                box_row = box.row()
                box_row.prop(wm, "enable", text="Enable")
                if wm.enable != obj["enable"]:
                    wm.enable = obj["enable"]
                box_row = box.row()
                box_row.prop(wm, "useTextures", text="Use Textures")
                if wm.useTextures != obj["useTextures"]:
                    wm.useTextures = obj["useTextures"]
                box_row = box.row()
                box_row.prop(wm, "matName", text="Name")
                if wm.matName != obj["matName"]:
                    wm.matName = obj["matName"]
                box_row = box.row()
                box_row.prop(wm, "textureDirName", text="Texture Directory")
                if wm.textureDirName != obj["textureDirName"]:
                    wm.textureDirName = obj["textureDirName"]
                box_row = box.row()
                box_row.prop(wm, "splineMultiplier", text="Spline Multiplier")
                if wm.splineMultiplier != obj["splineMultiplier"]:
                    wm.splineMultiplier = obj["splineMultiplier"]
                box_row = box.row()
                box_row.prop(wm, "assetType", text="Asset Type")
                if wm.assetType != obj["assetType"]:
                    wm.assetType = obj["assetType"]
                box_row = box.row()
                box_row.prop(wm, "assetPriority", text="Asset Priority")
                if wm.assetPriority != obj["assetPriority"]:
                    wm.assetPriority = obj["assetPriority"]
                box_row = box.row()
                box_row.prop(wm, "assetGroup", text="Asset Group")
                if wm.assetGroup != obj["assetGroup"]:
                    wm.assetGroup = obj["assetGroup"]
                
                layout.separator()
                row = layout.row(align = True)
                row.alignment = "CENTER"
                row.scale_x = 1.44
                row.scale_y = 1.4
                row.prop_enum(wm, "HairworksMaterialSubPanel", 'hair_visualization', text = "")
                row.prop_enum(wm, "HairworksMaterialSubPanel", 'hair_physics', text = "")
                row.prop_enum(wm, "HairworksMaterialSubPanel", 'hair_graphics', text = "")
                row.prop_enum(wm, "HairworksMaterialSubPanel", 'hair_lod', text = "")
                    
        return
    
class PhysXHairVisualizationPanel(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_PhysX_hair_visualization_panel'
    bl_parent_id = 'VIEW3D_PT_PhysX_hair_mat_panel'
    bl_label = 'Hairworks Visualization'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'PhysX'
    bl_options = {'HIDE_HEADER'}
    
    def draw(self, context):
        layout = self.layout
        physx = context.window_manager.physx
        wm = physx.hair
        if physx.PhysXSubPanel == 'hair_mat' and wm.HairworksMaterialSubPanel == 'hair_visualization':
            main_coll = GetCollection(make_active=False)
            arma = GetArmature()
            obj = arma.children[0]
            
            row = layout.row()
            row.prop(wm, "drawRenderHairs", text="Hair")
            if wm.drawRenderHairs != obj["drawRenderHairs"]:
                wm.drawRenderHairs = obj["drawRenderHairs"]
            row = layout.row()
            row.prop(wm, "visualizeGuideHairs", text="Guide Curves")
            if wm.visualizeGuideHairs != obj["visualizeGuideHairs"]:
                wm.visualizeGuideHairs = obj["visualizeGuideHairs"]
            row = layout.row()
            row.prop(wm, "visualizeSkinnedGuideHairs", text="Skinned Guide Curves")
            if wm.visualizeSkinnedGuideHairs != obj["visualizeSkinnedGuideHairs"]:
                wm.visualizeSkinnedGuideHairs = obj["visualizeSkinnedGuideHairs"]
            row = layout.row()
            row.prop(wm, "visualizeControlVertices", text="Control Points")
            if wm.visualizeControlVertices != obj["visualizeControlVertices"]:
                wm.visualizeControlVertices = obj["visualizeControlVertices"]
            row = layout.row()
            row.prop(wm, "visualizeGrowthMesh", text="Growth Mesh")
            if wm.visualizeGrowthMesh != obj["visualizeGrowthMesh"]:
                wm.visualizeGrowthMesh = obj["visualizeGrowthMesh"]
            row = layout.row()
            row.prop(wm, "visualizeBones", text="Bones")
            if wm.visualizeBones != obj["visualizeBones"]:
                wm.visualizeBones = obj["visualizeBones"]
            row = layout.row()
            row.prop(wm, "visualizeBoundingBox", text="Bounding Box")
            if wm.visualizeBoundingBox != obj["visualizeBoundingBox"]:
                wm.visualizeBoundingBox = obj["visualizeBoundingBox"]
            row = layout.row()
            row.prop(wm, "visualizeCapsules", text="Collision Capsules")
            if wm.visualizeCapsules != obj["visualizeCapsules"]:
                wm.visualizeCapsules = obj["visualizeCapsules"]
            row = layout.row()
            row.prop(wm, "visualizeHairInteractions", text="Hair Interaction")
            if wm.visualizeHairInteractions != obj["visualizeHairInteractions"]:
                wm.visualizeHairInteractions = obj["visualizeHairInteractions"]
            row = layout.row()
            row.prop(wm, "visualizePinConstraints", text="Pin Constraints")
            if wm.visualizePinConstraints != obj["visualizePinConstraints"]:
                wm.visualizePinConstraints = obj["visualizePinConstraints"]
            row = layout.row()
            row.prop(wm, "visualizeShadingNormals", text="Shading Normal")
            if wm.visualizeShadingNormals != obj["visualizeShadingNormals"]:
                wm.visualizeShadingNormals = obj["visualizeShadingNormals"]
            row = layout.row()
            row.prop(wm, "visualizeCullSphere", text="Cull Sphere")
            if wm.visualizeCullSphere != obj["visualizeCullSphere"]:
                wm.visualizeCullSphere = obj["visualizeCullSphere"]
            row = layout.row()
            row.prop(wm, "visualizeDiffuseBone", text="Diffuse Bone")
            if wm.visualizeDiffuseBone != obj["visualizeDiffuseBone"]:
                wm.visualizeDiffuseBone = obj["visualizeDiffuseBone"]
            row = layout.row()
            row.prop(wm, "visualizeFrames", text="Frames")
            if wm.visualizeFrames != obj["visualizeFrames"]:
                wm.visualizeFrames = obj["visualizeFrames"]
            row = layout.row()
            row.prop(wm, "visualizeLocalPos", text="Local Position")
            if wm.visualizeLocalPos != obj["visualizeLocalPos"]:
                wm.visualizeLocalPos = obj["visualizeLocalPos"]
            row = layout.row()
            row.prop(wm, "visualizeHairSkips", text="Hair Skips")
            if wm.visualizeHairSkips != obj["visualizeHairSkips"]:
                wm.visualizeHairSkips = obj["visualizeHairSkips"]
            row = layout.row()
            row.prop(wm, "colorizeLODOption", text="Colorize Options")
            if wm.colorizeLODOption != obj["colorizeLODOption"]:
                wm.colorizeLODOption = obj["colorizeLODOption"]
                
        return
    
class PhysXHairPhysicsPanel(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_PhysX_hair_physics_panel'
    bl_parent_id = 'VIEW3D_PT_PhysX_hair_mat_panel'
    bl_label = 'Hairworks Physics'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'PhysX'
    bl_options = {'HIDE_HEADER'}
    
    def draw(self, context):
        layout = self.layout
        physx = context.window_manager.physx
        wm = physx.hair
        if physx.PhysXSubPanel == 'hair_mat' and wm.HairworksMaterialSubPanel == 'hair_physics':
            main_coll = GetCollection(make_active=False)
            arma = GetArmature()
            obj = arma.children[0]
            
            header, panel = layout.panel("hair_general_panel", default_closed=False)
            header.label(text="General")
            if panel:
                row = panel.row()
                row.prop(wm, "simulate", text="Simulate")
                if wm.simulate != obj["simulate"]:
                    wm.simulate = obj["simulate"]
                row = panel.row()
                row.prop(wm, "massScale", text="Mass Scale")
                if wm.massScale != obj["massScale"]:
                    wm.massScale = obj["massScale"]
                row = panel.row()
                row.prop(wm, "damping", text="Damping")
                if wm.damping != obj["damping"]:
                    wm.damping = obj["damping"]
                row = panel.row()
                row.prop(wm, "inertiaScale", text="Inertia Scale")
                if wm.inertiaScale != obj["inertiaScale"]:
                    wm.inertiaScale = obj["inertiaScale"]
                row = panel.row()
                row.prop(wm, "inertiaLimit", text="Inertia Limit")
                if wm.inertiaLimit != obj["inertiaLimit"]:
                    wm.inertiaLimit = obj["inertiaLimit"]
                row = panel.row()
                row.label(text="Gravity")
                row = panel.row()
                row.prop(wm, "gravity", text="")
                if not all(np.array(wm.gravity) == np.array(obj["gravity"])):
                    wm.gravity = obj["gravity"]
                row = panel.row()
                box = row.box()
                box.label(text="Wind")
                box_row = box.row()
                box_row.prop(wm, "wind", text="")
                if not all(np.array(wm.wind) == np.array(obj["wind"])):
                    wm.wind = obj["wind"]
                box_row = box.row()
                box_row.prop(wm, "windNoise", text="Noise")
                if wm.windNoise != obj["windNoise"]:
                    wm.windNoise = obj["windNoise"]
            
            layout.separator()
            header, panel = layout.panel("hair_stiffness_panel", default_closed=False)
            header.label(text="Stiffness")
            if panel:
                row = panel.row()
                box = row.box()
                box.label(text="Global")
                box_row = box.row()
                #box_row.template_ID(wm, "stiffnessTexture", new="image.new", open="image.open")
                split = box_row.split(factor = 0.82, align = True)
                split.prop(wm, "stiffnessTexture", text="", icon='TEXTURE')
                if wm.stiffnessTexture != obj["stiffnessTexture"]:
                    wm.stiffnessTexture = obj["stiffnessTexture"]
                split.prop(wm, "stiffnessTextureChan", text = "")
                if wm.stiffnessTextureChan != obj["stiffnessTextureChan"]:
                    wm.stiffnessTextureChan = obj["stiffnessTextureChan"]
                box_row = box.row()
                split = box_row.split(factor = 0.85, align = True)
                split.prop(wm, "stiffness", text="")
                if wm.stiffness != obj["stiffness"]:
                    wm.stiffness = obj["stiffness"]
                split.prop(wm, "stiffnessCurveToggle", text = "", toggle = True, icon = "FCURVE")
                if wm.stiffnessCurveToggle:
                    box_row = box.row()
                    box_row.prop(wm, "stiffnessCurve", text = "")
                    if not all(np.array(wm.stiffnessCurve) == np.array(obj["stiffnessCurve"])):
                        wm.stiffnessCurve = obj["stiffnessCurve"]
                    col = box.column()
                    col.enabled = False
                    col.template_curve_mapping(obj.modifiers["SimulationCurves"].node_group.nodes["stiffnessCurve"], "mapping")
                    
                row = panel.row()
                box = row.box()
                box.label(text="Root")
                box_row = box.row()
                #box_row.template_ID(wm, "rootStiffnessTexture", new="image.new", open="image.open")
                split = box_row.split(factor = 0.82, align = True)
                split.prop(wm, "rootStiffnessTexture", text="", icon='TEXTURE')
                if wm.rootStiffnessTexture != obj["rootStiffnessTexture"]:
                    wm.rootStiffnessTexture = obj["rootStiffnessTexture"]
                split.prop(wm, "rootStiffnessTextureChan", text="")
                if wm.rootStiffnessTextureChan != obj["rootStiffnessTextureChan"]:
                    wm.rootStiffnessTextureChan = obj["rootStiffnessTextureChan"]
                box_row = box.row()
                box_row.prop(wm, "rootStiffness", text="")
                if wm.rootStiffness != obj["rootStiffness"]:
                    wm.rootStiffness = obj["rootStiffness"]
                
                row = panel.row()
                row.prop(wm, "tipStiffness", text="Tip")
                if wm.tipStiffness != obj["tipStiffness"]:
                    wm.tipStiffness = obj["tipStiffness"]
                    
                row = panel.row()
                split = row.split(factor = 0.85, align = True)
                split.prop(wm, "stiffnessStrength", text="Strength")
                if wm.stiffnessStrength != obj["stiffnessStrength"]:
                    wm.stiffnessStrength = obj["stiffnessStrength"]
                split.prop(wm, "stiffnessStrengthCurveToggle", text = "", toggle = True, icon = "FCURVE")
                if wm.stiffnessStrengthCurveToggle:
                    row = panel.row()
                    row.prop(wm, "stiffnessStrengthCurve", text = "")
                    if not all(np.array(wm.stiffnessStrengthCurve) == np.array(obj["stiffnessStrengthCurve"])):
                        wm.stiffnessStrengthCurve = obj["stiffnessStrengthCurve"]
                    col = panel.column()
                    col.enabled = False
                    col.template_curve_mapping(obj.modifiers["SimulationCurves"].node_group.nodes["stiffnessStrengthCurve"], "mapping")
                    
                row = panel.row()
                split = row.split(factor = 0.85, align = True)
                split.prop(wm, "stiffnessDamping", text="Damping")
                if wm.stiffnessDamping != obj["stiffnessDamping"]:
                    wm.stiffnessDamping = obj["stiffnessDamping"]
                split.prop(wm, "stiffnessDampingCurveToggle", text = "", toggle = True, icon = "FCURVE")
                if wm.stiffnessDampingCurveToggle:
                    row = panel.row()
                    row.prop(wm, "stiffnessDampingCurve", text = "")
                    if not all(np.array(wm.stiffnessDampingCurve) == np.array(obj["stiffnessDampingCurve"])):
                        wm.stiffnessDampingCurve = obj["stiffnessDampingCurve"]
                    col = panel.column()
                    col.enabled = False
                    col.template_curve_mapping(obj.modifiers["SimulationCurves"].node_group.nodes["stiffnessDampingCurve"], "mapping")
                
                row = panel.row()
                split = row.split(factor = 0.85, align = True)
                split.prop(wm, "bendStiffness", text="Bend")
                if wm.bendStiffness != obj["bendStiffness"]:
                    wm.bendStiffness = obj["bendStiffness"]
                split.prop(wm, "bendStiffnessCurveToggle", text = "", toggle = True, icon = "FCURVE")
                if wm.bendStiffnessCurveToggle:
                    row = panel.row()
                    row.prop(wm, "bendStiffnessCurve", text = "")
                    if not all(np.array(wm.bendStiffnessCurve) == np.array(obj["bendStiffnessCurve"])):
                        wm.bendStiffnessCurve = obj["bendStiffnessCurve"]
                    col = panel.column()
                    col.enabled = False
                    col.template_curve_mapping(obj.modifiers["SimulationCurves"].node_group.nodes["bendStiffnessCurve"], "mapping")
            
            layout.separator()
            header, panel = layout.panel("hair_collision_panel", default_closed=False)
            header.label(text="Collision")
            if panel:   
                row = panel.row()
                row.prop(wm, "backStopRadius", text="Backstop")
                if wm.backStopRadius != obj["backStopRadius"]:
                    wm.backStopRadius = obj["backStopRadius"]
                row = panel.row()
                row.prop(wm, "friction", text="Friction")
                if wm.friction != obj["friction"]:
                    wm.friction = obj["friction"]
                row = panel.row()
                row.prop(wm, "useCollision", text="Use Collision")
                if wm.useCollision != obj["useCollision"]:
                    wm.useCollision = obj["useCollision"]
                row = panel.row()
                row.prop(wm, "collisionOffset", text="Collision Offset")
                if wm.collisionOffset != obj["collisionOffset"]:
                    wm.collisionOffset = obj["collisionOffset"]
                row = panel.row()
                split = row.split(factor = 0.85, align = True)
                split.prop(wm, "interactionStiffness", text="Hair Interaction")
                if wm.interactionStiffness != obj["interactionStiffness"]:
                    wm.interactionStiffness = obj["interactionStiffness"]
                split.prop(wm, "interactionStiffnessCurveToggle", text = "", toggle = True, icon = "FCURVE")
                if wm.interactionStiffnessCurveToggle:
                    row = panel.row()
                    row.prop(wm, "interactionStiffnessCurve", text = "")
                    if not all(np.array(wm.interactionStiffnessCurve) == np.array(obj["interactionStiffnessCurve"])):
                        wm.interactionStiffnessCurve = obj["interactionStiffnessCurve"]
                    col = panel.column()
                    col.enabled = False
                    col.template_curve_mapping(obj.modifiers["SimulationCurves"].node_group.nodes["interactionStiffnessCurve"], "mapping")
            
            layout.separator()
            header, panel = layout.panel("hair_pins_panel", default_closed=False)
            header.label(text="Hair Pins")
            if panel:  
                row = panel.row()
                row.prop(wm, "pinStiffness", text="Stiffness")
                if wm.pinStiffness != obj["pinStiffness"]:
                    wm.pinStiffness = obj["pinStiffness"]
                row = panel.row()
                row.prop(wm, "useDynamicPin", text="Use Dynamic Hair Pins")
                if wm.useDynamicPin != obj["useDynamicPin"]:
                    wm.useDynamicPin = obj["useDynamicPin"]
            
            layout.separator()
            header, panel = layout.panel("hair_volume_panel", default_closed=False)
            header.label(text="Volume")
            if panel:  
                row = panel.row()
                box = row.box()
                box.label(text="Density")
                box_row = box.row()
                #box_row.template_ID(wm, "densityTexture", new="image.new", open="image.open")
                split = box_row.split(factor = 0.82, align = True)
                split.prop(wm, "densityTexture", text="", icon='TEXTURE')
                if wm.densityTexture != obj["densityTexture"]:
                    wm.densityTexture = obj["densityTexture"]
                split.prop(wm, "densityTextureChan", text="")
                if wm.densityTextureChan != obj["densityTextureChan"]:
                    wm.densityTextureChan = obj["densityTextureChan"]
                box_row = box.row()
                box_row.prop(wm, "density", text="Scale")
                if wm.density != obj["density"]:
                    wm.density = obj["density"]
                box_row = box.row()
                box_row.prop(wm, "usePixelDensity", text="Use Pixel Density")
                if wm.usePixelDensity != obj["usePixelDensity"]:
                    wm.usePixelDensity = obj["usePixelDensity"]
                
                row = panel.row()
                box = row.box()
                box.label(text="Length")
                box_row = box.row()
                #box_row.template_ID(wm, "lengthTexture", new="image.new", open="image.open")
                split = box_row.split(factor = 0.82, align = True)
                split.prop(wm, "lengthTexture", text="", icon='TEXTURE')
                if wm.lengthTexture != obj["lengthTexture"]:
                    wm.lengthTexture = obj["lengthTexture"]
                split.prop(wm, "lengthTextureChan", text="")
                if wm.lengthTextureChan != obj["lengthTextureChan"]:
                    wm.lengthTextureChan = obj["lengthTextureChan"]
                box_row = box.row()
                box_row.prop(wm, "lengthScale", text="Scale")
                if wm.lengthScale != obj["lengthScale"]:
                    wm.lengthScale = obj["lengthScale"]
                box_row = box.row()
                box_row.prop(wm, "lengthNoise", text="Noise")
                if wm.lengthNoise != obj["lengthNoise"]:
                    wm.lengthNoise = obj["lengthNoise"]
            
            layout.separator()
            header, panel = layout.panel("hair_width_panel", default_closed=False)
            header.label(text="Strand Width")
            if panel: 
                row = panel.row()
                box = row.box()
                box.label(text="Base")
                box_row = box.row()
                #box_row.template_ID(wm, "widthTexture", new="image.new", open="image.open")
                split = box_row.split(factor = 0.82, align = True)
                split.prop(wm, "widthTexture", text="", icon='TEXTURE')
                if wm.widthTexture != obj["widthTexture"]:
                    wm.widthTexture = obj["widthTexture"]
                split.prop(wm, "widthTextureChan", text="")
                if wm.widthTextureChan != obj["widthTextureChan"]:
                    wm.widthTextureChan = obj["widthTextureChan"]
                box_row = box.row()
                box_row.prop(wm, "width", text="Scale")
                if wm.width != obj["width"]:
                    wm.width = obj["width"]
                box_row = box.row()
                box_row.prop(wm, "widthNoise", text="Noise")
                if wm.widthNoise != obj["widthNoise"]:
                    wm.widthNoise = obj["widthNoise"]
            
                row = panel.row()
                box = row.box()
                box.label(text="Root")
                box_row = box.row()
                #box_row.template_ID(wm, "rootWidthTexture", new="image.new", open="image.open")
                split = box_row.split(factor = 0.82, align = True)
                split.prop(wm, "rootWidthTexture", text="", icon='TEXTURE')
                if wm.rootWidthTexture != obj["rootWidthTexture"]:
                    wm.rootWidthTexture = obj["rootWidthTexture"]
                split.prop(wm, "rootWidthTextureChan", text="")
                if wm.rootWidthTextureChan != obj["rootWidthTextureChan"]:
                    wm.rootWidthTextureChan = obj["rootWidthTextureChan"]
                box_row = box.row()
                box_row.prop(wm, "widthRootScale", text="Scale")
                if wm.widthRootScale != obj["widthRootScale"]:
                    wm.widthRootScale = obj["widthRootScale"]
                
                row = panel.row()
                box = row.box()
                box.label(text="Tip")
                box_row = box.row()
                #box_row.template_ID(wm, "tipWidthTexture", new="image.new", open="image.open")
                split = box_row.split(factor = 0.82, align = True)
                split.prop(wm, "tipWidthTexture", text="", icon='TEXTURE')
                if wm.tipWidthTexture != obj["tipWidthTexture"]:
                    wm.tipWidthTexture = obj["tipWidthTexture"]
                split.prop(wm, "tipWidthTextureChan", text="")
                if wm.tipWidthTextureChan != obj["tipWidthTextureChan"]:
                    wm.tipWidthTextureChan = obj["tipWidthTextureChan"]
                box_row = box.row()
                box_row.prop(wm, "widthTipScale", text="Scale")
                if wm.widthTipScale != obj["widthTipScale"]:
                    wm.widthTipScale = obj["widthTipScale"]
            
            layout.separator()
            header, panel = layout.panel("hair_clumping_panel", default_closed=False)
            header.label(text="Clumping")
            if panel: 
                row = panel.row()
                box = row.box()
                box.label(text="Scale")
                box_row = box.row()
                #box_row.template_ID(wm, "clumpScaleTexture", new="image.new", open="image.open")
                split = box_row.split(factor = 0.82, align = True)
                split.prop(wm, "clumpScaleTexture", text="", icon='TEXTURE')
                if wm.clumpScaleTexture != obj["clumpScaleTexture"]:
                    wm.clumpScaleTexture = obj["clumpScaleTexture"]
                split.prop(wm, "clumpScaleTextureChan", text="")
                if wm.clumpScaleTextureChan != obj["clumpScaleTextureChan"]:
                    wm.clumpScaleTextureChan = obj["clumpScaleTextureChan"]
                box_row = box.row()
                box_row.prop(wm, "clumpScale", text="")
                if wm.clumpScale != obj["clumpScale"]:
                    wm.clumpScale = obj["clumpScale"]
                box_row = box.row()
                box_row.prop(wm, "clumpNumSubclumps", text="Number Subclumps")
                if wm.clumpNumSubclumps != obj["clumpNumSubclumps"]:
                    wm.clumpNumSubclumps = obj["clumpNumSubclumps"]
                box_row = box.row()
                box_row.prop(wm, "clumpPerVertex", text="Per Vertex")
                if wm.clumpPerVertex != obj["clumpPerVertex"]:
                    wm.clumpPerVertex = obj["clumpPerVertex"]
                
                row = panel.row()
                box = row.box()
                box.label(text="Roundness")
                box_row = box.row()
                #box_row.template_ID(wm, "clumpRoundnessTexture", new="image.new", open="image.open")
                split = box_row.split(factor = 0.82, align = True)
                split.prop(wm, "clumpRoundnessTexture", text="", icon='TEXTURE')
                if wm.clumpRoundnessTexture != obj["clumpRoundnessTexture"]:
                    wm.clumpRoundnessTexture = obj["clumpRoundnessTexture"]
                split.prop(wm, "clumpRoundnessTextureChan", text="")
                if wm.clumpRoundnessTextureChan != obj["clumpRoundnessTextureChan"]:
                    wm.clumpRoundnessTextureChan = obj["clumpRoundnessTextureChan"]
                box_row = box.row()
                box_row.prop(wm, "clumpRoundness", text="")
                if wm.clumpRoundness != obj["clumpRoundness"]:
                    wm.clumpRoundness = obj["clumpRoundness"]
                
                row = panel.row()
                box = row.box()
                box.label(text="Noise")
                box_row = box.row()
                #box_row.template_ID(wm, "clumpNoiseTexture", new="image.new", open="image.open")
                split = box_row.split(factor = 0.82, align = True)
                split.prop(wm, "clumpNoiseTexture", text="", icon='TEXTURE')
                if wm.clumpNoiseTexture != obj["clumpNoiseTexture"]:
                    wm.clumpNoiseTexture = obj["clumpNoiseTexture"]
                split.prop(wm, "clumpNoiseTextureChan", text="")
                if wm.clumpNoiseTextureChan != obj["clumpNoiseTextureChan"]:
                    wm.clumpNoiseTextureChan = obj["clumpNoiseTextureChan"]
                box_row = box.row()
                box_row.prop(wm, "clumpNoise", text="")
                if wm.clumpNoise != obj["clumpNoise"]:
                    wm.clumpNoise = obj["clumpNoise"]
            
            layout.separator()
            header, panel = layout.panel("hair_waviness_panel", default_closed=False)
            header.label(text="Waviness")
            if panel: 
                row = panel.row()
                box = row.box()
                box.label(text="Scale")
                box_row = box.row()
                #box_row.template_ID(wm, "waveScaletexture", new="image.new", open="image.open")
                split = box_row.split(factor = 0.82, align = True)
                split.prop(wm, "waveScaletexture", text="", icon='TEXTURE')
                if wm.waveScaletexture != obj["waveScaletexture"]:
                    wm.waveScaletexture = obj["waveScaletexture"]
                split.prop(wm, "waveScaleTextureChan", text="")
                if wm.waveScaleTextureChan != obj["waveScaleTextureChan"]:
                    wm.waveScaleTextureChan = obj["waveScaleTextureChan"]
                box_row = box.row()
                box_row.prop(wm, "waveScale", text="")
                if wm.waveScale != obj["waveScale"]:
                    wm.waveScale = obj["waveScale"]
                box_row = box.row()
                box_row.prop(wm, "waveScaleNoise", text="Noise")
                if wm.waveScaleNoise != obj["waveScaleNoise"]:
                    wm.waveScaleNoise = obj["waveScaleNoise"]
                box_row = box.row()
                box_row.prop(wm, "waveScaleStrand", text="Strand")
                if wm.waveScaleStrand != obj["waveScaleStrand"]:
                    wm.waveScaleStrand = obj["waveScaleStrand"]
                box_row = box.row()
                box_row.prop(wm, "waveScaleClump", text="Clump")
                if wm.waveScaleClump != obj["waveScaleClump"]:
                    wm.waveScaleClump = obj["waveScaleClump"]
                
                row = panel.row()
                box = row.box()
                box.label(text="Frequency")
                box_row = box.row()
                #box_row.template_ID(wm, "waveFreqTexture", new="image.new", open="image.open")
                split = box_row.split(factor = 0.82, align = True)
                split.prop(wm, "waveFreqTexture", text="", icon='TEXTURE')
                if wm.waveFreqTexture != obj["waveFreqTexture"]:
                    wm.waveFreqTexture = obj["waveFreqTexture"]
                split.prop(wm, "waveFreqTextureChan", text="")
                if wm.waveFreqTextureChan != obj["waveFreqTextureChan"]:
                    wm.waveFreqTextureChan = obj["waveFreqTextureChan"]
                box_row = box.row()
                box_row.prop(wm, "waveFreq", text="")
                if wm.waveFreq != obj["waveFreq"]:
                    wm.waveFreq = obj["waveFreq"]
                box_row = box.row()
                box_row.prop(wm, "waveFreqNoise", text="Noise")
                if wm.waveFreqNoise != obj["waveFreqNoise"]:
                    wm.waveFreqNoise = obj["waveFreqNoise"]
                
                row = panel.row()
                row.prop(wm, "waveRootStraighten", text="Root Straighten")
                if wm.waveRootStraighten != obj["waveRootStraighten"]:
                    wm.waveRootStraighten = obj["waveRootStraighten"]
                    
        return
    
class PhysXHairGraphicsPanel(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_PhysX_hair_graphics_panel'
    bl_parent_id = 'VIEW3D_PT_PhysX_hair_mat_panel'
    bl_label = 'Hairworks Graphics'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'PhysX'
    bl_options = {'HIDE_HEADER'}
    
    def draw(self, context):
        layout = self.layout
        physx = context.window_manager.physx
        wm = physx.hair
        if physx.PhysXSubPanel == 'hair_mat' and wm.HairworksMaterialSubPanel == 'hair_graphics':
            main_coll = GetCollection(make_active=False)
            arma = GetArmature()
            obj = arma.children[0]
            
            header, panel = layout.panel("hair_color_panel", default_closed=False)
            header.label(text="Color")
            if panel:
                row = panel.row()
                box = row.box()
                box.label(text="Base")
                box_row = box.row()
                box_row.prop(wm, "baseColor", text="")
                if not all(np.array(wm.baseColor) == np.array(obj["baseColor"])):
                    wm.baseColor = obj["baseColor"]
                box_row = box.row()
                box_row.prop(wm, "alpha", text="Alpha")
                if wm.alpha != obj["alpha"]:
                    wm.alpha = obj["alpha"]
                
                row = panel.row()
                box = row.box()
                box.label(text="Root")
                box_row = box.row()
                #box_row.template_ID(wm, "rootColorTexture", new="image.new", open="image.open")
                split = box_row.split(factor = 0.8)
                split.prop(wm, "rootColorTexture", text="", icon='TEXTURE')
                if wm.rootColorTexture != obj["rootColorTexture"]:
                    wm.rootColorTexture = obj["rootColorTexture"]
                split.prop(wm, "rootColor", text="")
                if not all(np.array(wm.rootColor) == np.array(obj["rootColor"])):
                    wm.rootColor = obj["rootColor"]
                box_row = box.row()
                box_row.prop(wm, "rootAlphaFalloff", text="Alpha Falloff")
                if wm.rootAlphaFalloff != obj["rootAlphaFalloff"]:
                    wm.rootAlphaFalloff = obj["rootAlphaFalloff"]
                
                row = panel.row()
                box = row.box()
                box.label(text="Tip")
                box_row = box.row()
                #box_row.template_ID(wm, "tipColorTexture", new="image.new", open="image.open")
                split = box_row.split(factor = 0.8)
                split.prop(wm, "tipColorTexture", text="", icon='TEXTURE')
                if wm.tipColorTexture != obj["tipColorTexture"]:
                    wm.tipColorTexture = obj["tipColorTexture"]
                split.prop(wm, "tipColor", text="")
                if not all(np.array(wm.tipColor) == np.array(obj["tipColor"])):
                    wm.tipColor = obj["tipColor"]
                
                row = panel.row()
                box = row.box()
                box.label(text="Root/Tip")
                box_row = box.row()
                box_row.prop(wm, "rootTipColorWeight", text="Weight")
                if wm.rootTipColorWeight != obj["rootTipColorWeight"]:
                    wm.rootTipColorWeight = obj["rootTipColorWeight"]
                box_row = box.row()
                box_row.prop(wm, "rootTipColorFalloff", text="Falloff")
                if wm.rootTipColorFalloff != obj["rootTipColorFalloff"]:
                    wm.rootTipColorFalloff = obj["rootTipColorFalloff"]
            
            layout.separator()
            header, panel = layout.panel("hair_strand_panel", default_closed=False)
            header.label(text="Strand")
            if panel:
                row = panel.row()
                #row.template_ID(wm, "strandTexture", new="image.new", open="image.open")
                row.prop(wm, "strandTexture", text="", icon='TEXTURE')
                if wm.strandTexture != obj["strandTexture"]:
                    wm.strandTexture = obj["strandTexture"]
                row = panel.row()
                row.prop(wm, "strandBlendMode", text="Blend Mode")
                if wm.strandBlendMode != obj["strandBlendMode"]:
                    wm.strandBlendMode = obj["strandBlendMode"]
                row = panel.row()
                row.prop(wm, "strandBlendScale", text="Blend Scale")
                if wm.strandBlendScale != obj["strandBlendScale"]:
                    wm.strandBlendScale = obj["strandBlendScale"]
                row = panel.row()
                row.prop(wm, "textureBrightness", text="Brightness")
                if wm.textureBrightness != obj["textureBrightness"]:
                    wm.textureBrightness = obj["textureBrightness"]
            
            layout.separator()
            header, panel = layout.panel("hair_diffuse_panel", default_closed=False)
            header.label(text="Diffuse")
            if panel:
                row = panel.row()
                row.prop(wm, "diffuseColor", text="")
                if not all(np.array(wm.diffuseColor) == np.array(obj["diffuseColor"])):
                    wm.diffuseColor = obj["diffuseColor"]
                row = panel.row()
                row.prop(wm, "diffuseBlend", text="Blend")
                if wm.diffuseBlend != obj["diffuseBlend"]:
                    wm.diffuseBlend = obj["diffuseBlend"]
                row = panel.row()
                row.prop(wm, "diffuseScale", text="Scale")
                if wm.diffuseScale != obj["diffuseScale"]:
                    wm.diffuseScale = obj["diffuseScale"]
                row = panel.row()
                row.prop(wm, "diffuseHairNormalWeight", text="Hair Normal Weight")
                if wm.diffuseHairNormalWeight != obj["diffuseHairNormalWeight"]:
                    wm.diffuseHairNormalWeight = obj["diffuseHairNormalWeight"]
                
                row = panel.row()
                box = row.box()
                box.label(text="Bone")
                box_row = box.row()
                box_row.prop(wm, "diffuseBoneIndex", text="Index")
                if wm.diffuseBoneIndex != obj["diffuseBoneIndex"]:
                    wm.diffuseBoneIndex = obj["diffuseBoneIndex"]
                box_row = box.row()
                col = box_row.column()
                col.prop(wm, "diffuseBoneLocalPos", text="Local Position")
                if not all(np.array(wm.diffuseBoneLocalPos) == np.array(obj["diffuseBoneLocalPos"])):
                    wm.diffuseBoneLocalPos = obj["diffuseBoneLocalPos"]
                
                row = panel.row()
                box = row.box()
                box.label(text="Noise")
                box_row = box.row()
                box_row.prop(wm, "diffuseNoiseScale", text="Scale")
                if wm.diffuseNoiseScale != obj["diffuseNoiseScale"]:
                    wm.diffuseNoiseScale = obj["diffuseNoiseScale"]
                box_row = box.row()
                box_row.prop(wm, "diffuseNoiseGain", text="Gain")
                if wm.diffuseNoiseGain != obj["diffuseNoiseGain"]:
                    wm.diffuseNoiseGain = obj["diffuseNoiseGain"]
                box_row = box.row()
                box_row.prop(wm, "diffuseNoiseFreqU", text="Freq U")
                if wm.diffuseNoiseFreqU != obj["diffuseNoiseFreqU"]:
                    wm.diffuseNoiseFreqU = obj["diffuseNoiseFreqU"]
                box_row = box.row()
                box_row.prop(wm, "diffuseNoiseFreqV", text="Freq V")
                if wm.diffuseNoiseFreqV != obj["diffuseNoiseFreqV"]:
                    wm.diffuseNoiseFreqV = obj["diffuseNoiseFreqV"]
            
            layout.separator()
            header, panel = layout.panel("hair_specular_panel", default_closed=False)
            header.label(text="Specular")
            if panel:
                row = panel.row()
                #row.template_ID(wm, "specularTexture", new="image.new", open="image.open")
                split = row.split(factor = 0.8)
                split.prop(wm, "specularTexture", text="", icon='TEXTURE')
                if wm.specularTexture != obj["specularTexture"]:
                    wm.specularTexture = obj["specularTexture"]
                split.prop(wm, "specularColor", text="")
                if not all(np.array(wm.specularColor) == np.array(obj["specularColor"])):
                    wm.specularColor = obj["specularColor"]
                row = panel.row()
                row.prop(wm, "specularNoiseScale", text="Noise Scale")
                if wm.specularNoiseScale != obj["specularNoiseScale"]:
                    wm.specularNoiseScale = obj["specularNoiseScale"]
                row = panel.row()
                row.prop(wm, "specularEnvScale", text="Env Scale")
                if wm.specularEnvScale != obj["specularEnvScale"]:
                    wm.specularEnvScale = obj["specularEnvScale"]
                
                row = panel.row()
                box = row.box()
                box.label(text="Primary")
                box_row = box.row()
                box_row.prop(wm, "specularPrimary", text="Scale")
                if wm.specularPrimary != obj["specularPrimary"]:
                    wm.specularPrimary = obj["specularPrimary"]
                box_row = box.row()
                box_row.prop(wm, "specularPowerPrimary", text="Shininess")
                if wm.specularPowerPrimary != obj["specularPowerPrimary"]:
                    wm.specularPowerPrimary = obj["specularPowerPrimary"]
                box_row = box.row()
                box_row.prop(wm, "specularPrimaryBreakup", text="Breakup")
                if wm.specularPrimaryBreakup != obj["specularPrimaryBreakup"]:
                    wm.specularPrimaryBreakup = obj["specularPrimaryBreakup"]
                
                row = panel.row()
                box = row.box()
                box.label(text="Secondary")
                box_row = box.row()
                box_row.prop(wm, "specularSecondary", text="Scale")
                if wm.specularSecondary != obj["specularSecondary"]:
                    wm.specularSecondary = obj["specularSecondary"]
                box_row = box.row()
                box_row.prop(wm, "specularPowerSecondary", text="Shininess")
                if wm.specularPowerSecondary != obj["specularPowerSecondary"]:
                    wm.specularPowerSecondary = obj["specularPowerSecondary"]
                box_row = box.row()
                box_row.prop(wm, "specularSecondaryOffset", text="Offset")
                if wm.specularSecondaryOffset != obj["specularSecondaryOffset"]:
                    wm.specularSecondaryOffset = obj["specularSecondaryOffset"]
            
            layout.separator()
            header, panel = layout.panel("hair_glint_panel", default_closed=False)
            header.label(text="Glint")
            if panel:
                row = panel.row()
                row.prop(wm, "glintStrength", text="Strength")
                if wm.glintStrength != obj["glintStrength"]:
                    wm.glintStrength = obj["glintStrength"]
                row = panel.row()
                row.prop(wm, "glintCount", text="Size")
                if wm.glintCount != obj["glintCount"]:
                    wm.glintCount = obj["glintCount"]
                row = panel.row()
                row.prop(wm, "glintExponent", text="Exponent")
                if wm.glintExponent != obj["glintExponent"]:
                    wm.glintExponent = obj["glintExponent"]
            
            layout.separator()
            header, panel = layout.panel("hair_shadows_panel", default_closed=False)
            header.label(text="Shadows")
            if panel:
                row = panel.row()
                row.prop(wm, "useShadows", text="Use Shadows")
                if wm.useShadows != obj["useShadows"]:
                    wm.useShadows = obj["useShadows"]
                row = panel.row()
                row.prop(wm, "castShadows", text="Cast")
                if wm.castShadows != obj["castShadows"]:
                    wm.castShadows = obj["castShadows"]
                row = panel.row()
                row.prop(wm, "receiveShadows", text="Receive")
                if wm.receiveShadows != obj["receiveShadows"]:
                    wm.receiveShadows = obj["receiveShadows"]
                row = panel.row()
                row.prop(wm, "shadowSigma", text="Attenuation")
                if wm.shadowSigma != obj["shadowSigma"]:
                    wm.shadowSigma = obj["shadowSigma"]
                row = panel.row()
                row.prop(wm, "shadowDensityScale", text="Density Scale")
                if wm.shadowDensityScale != obj["shadowDensityScale"]:
                    wm.shadowDensityScale = obj["shadowDensityScale"]
              
        return
    
class PhysXHairLODPanel(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_PhysX_hair_lod_panel'
    bl_parent_id = 'VIEW3D_PT_PhysX_hair_mat_panel'
    bl_label = 'Hairworks LOD'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'PhysX'
    bl_options = {'HIDE_HEADER'}
    
    def draw(self, context):
        layout = self.layout
        physx = context.window_manager.physx
        wm = physx.hair
        if physx.PhysXSubPanel == 'hair_mat' and wm.HairworksMaterialSubPanel == 'hair_lod':
            main_coll = GetCollection(make_active=False)
            arma = GetArmature()
            obj = arma.children[0]
            
            row = layout.row()
            box = row.box()
            box.label(text="Culling")
            box_row = box.row()
            box_row.prop(wm, "useViewfrustrumCulling", text="View Frustrum Culling")
            if wm.useViewfrustrumCulling != obj["useViewfrustrumCulling"]:
                wm.useViewfrustrumCulling = obj["useViewfrustrumCulling"]
            box_row = box.row()
            box_row.prop(wm, "useBackfaceCulling", text="Backface Culling")
            if wm.useBackfaceCulling != obj["useBackfaceCulling"]:
                wm.useBackfaceCulling = obj["useBackfaceCulling"]
            box_row = box.row()
            box_row.prop(wm, "backfaceCullingThreshold", text="Threshold")
            if wm.backfaceCullingThreshold != obj["backfaceCullingThreshold"]:
                wm.backfaceCullingThreshold = obj["backfaceCullingThreshold"]
            
            layout.separator()
            row = layout.row()
            box = row.box()
            box.label(text="Distance LOD")
            box_row = box.row()
            box_row.prop(wm, "enableDistanceLOD", text="Enable")
            if wm.enableDistanceLOD != obj["enableDistanceLOD"]:
                wm.enableDistanceLOD = obj["enableDistanceLOD"]
            box_row = box.row()
            box_row.prop(wm, "distanceLODStart", text="Start Distance")
            if wm.distanceLODStart != obj["distanceLODStart"]:
                wm.distanceLODStart = obj["distanceLODStart"]
            box_row = box.row()
            box_row.prop(wm, "distanceLODEnd", text="End Distance")
            if wm.distanceLODEnd != obj["distanceLODEnd"]:
                wm.distanceLODEnd = obj["distanceLODEnd"]
            box_row = box.row()
            box_row.prop(wm, "distanceLODFadeStart", text="Fade Start Distance")
            if wm.distanceLODFadeStart != obj["distanceLODFadeStart"]:
                wm.distanceLODFadeStart = obj["distanceLODFadeStart"]
            box_row = box.row()
            box_row.prop(wm, "distanceLODWidth", text="Base Width Scale")
            if wm.distanceLODWidth != obj["distanceLODWidth"]:
                wm.distanceLODWidth = obj["distanceLODWidth"]
            box_row = box.row()
            box_row.prop(wm, "distanceLODDensity", text="Density Scale")
            if wm.distanceLODDensity != obj["distanceLODDensity"]:
                wm.distanceLODDensity = obj["distanceLODDensity"]
            
            row = layout.row()
            box = row.box()
            box.label(text="Detail LOD")
            box_row = box.row()
            box_row.prop(wm, "enableDetailLOD", text="Enable")
            if wm.enableDetailLOD != obj["enableDetailLOD"]:
                wm.enableDetailLOD = obj["enableDetailLOD"]
            box_row = box.row()
            box_row.prop(wm, "detailLODStart", text="Start Distance")
            if wm.detailLODStart != obj["detailLODStart"]:
                wm.detailLODStart = obj["detailLODStart"]
            box_row = box.row()
            box_row.prop(wm, "detailLODEnd", text="End Distance")
            if wm.detailLODEnd != obj["detailLODEnd"]:
                wm.detailLODEnd = obj["detailLODEnd"]
            box_row = box.row()
            box_row.prop(wm, "detailLODWidth", text="Base Width Scale")
            if wm.detailLODWidth != obj["detailLODWidth"]:
                wm.detailLODWidth = obj["detailLODWidth"]
            box_row = box.row()
            box_row.prop(wm, "detailLODDensity", text="Density Scale")
            if wm.detailLODDensity != obj["detailLODDensity"]:
                wm.detailLODDensity = obj["detailLODDensity"]
                
        return
    
def updateEnable(self, context):
    GetArmature().children[0]["enable"] = self.enable
    
def updateUseTextures(self, context):
    GetArmature().children[0]["useTextures"] = self.useTextures
    
def updateMatName(self, context):
    GetArmature().children[0]["matName"] = self.matName

def updateTextureDirName(self, context):
    GetArmature().children[0]["textureDirName"] = self.textureDirName
    
def updateSplineMultiplier(self, context):
    obj = GetArmature().children[0]
    obj["splineMultiplier"] = self.splineMultiplier
    settings = obj.modifiers['Hairworks'].particle_system.settings
    settings.display_step = (np.array(np.ceil(np.sqrt(settings.hair_step+1)), dtype="byte")-1) + self.splineMultiplier
    
def updateAssetType(self, context):
    GetArmature().children[0]["assetType"] = self.assetType
    
def updateAssetPriority(self, context):
    GetArmature().children[0]["assetPriority"] = self.assetPriority
    
def updateAssetGroup(self, context):
    GetArmature().children[0]["assetGroup"] = self.assetGroup
    
def updateDrawRenderHairs(self, context):
    GetArmature().children[0]["drawRenderHairs"] = self.drawRenderHairs
    
def updateVisualizeGuideHairs(self, context):
    GetArmature().children[0]["visualizeGuideHairs"] = self.visualizeGuideHairs
    
def updateVisualizeSkinnedGuideHairs(self, context):
    GetArmature().children[0]["visualizeSkinnedGuideHairs"] = self.visualizeSkinnedGuideHairs
    
def updateVisualizeControlVertices(self, context):
    GetArmature().children[0]["visualizeControlVertices"] = self.visualizeControlVertices
    
def updateVisualizeGrowthMesh(self, context):
    obj = GetArmature().children[0]
    obj["visualizeGrowthMesh"] = self.visualizeGrowthMesh
    obj.show_instancer_for_viewport = self.visualizeGrowthMesh
    
def updateVisualizeBones(self, context):
    GetArmature().children[0]["visualizeBones"] = self.visualizeBones
    
def updateVisualizeBoundingBox(self, context):
    GetArmature().children[0]["visualizeBoundingBox"] = self.visualizeBoundingBox
    
def updateVisualizeCapsules(self, context):
    GetArmature().children[0]["visualizeCapsules"] = self.visualizeCapsules
    
def updateVisualizeHairInteractions(self, context):
    GetArmature().children[0]["visualizeHairInteractions"] = self.visualizeHairInteractions
    
def updateVisualizePinConstraints(self, context):
    GetArmature().children[0]["visualizePinConstraints"] = self.visualizePinConstraints
    
def updateVisualizeShadingNormals(self, context):
    GetArmature().children[0]["visualizeShadingNormals"] = self.visualizeShadingNormals
    
def updateVisualizeCullSphere(self, context):
    GetArmature().children[0]["visualizeCullSphere"] = self.visualizeCullSphere
    
def updateVisualizeDiffuseBone(self, context):
    GetArmature().children[0]["visualizeDiffuseBone"] = self.visualizeDiffuseBone
    
def updateVisualizeFrames(self, context):
    GetArmature().children[0]["visualizeFrames"] = self.visualizeFrames
    
def updateVisualizeLocalPos(self, context):
    GetArmature().children[0]["visualizeLocalPos"] = self.visualizeLocalPos
    
def updateVisualizeHairSkips(self, context):
    GetArmature().children[0]["visualizeHairSkips"] = self.visualizeHairSkips
    
def updateColorizeLODOption(self, context):
    GetArmature().children[0]["colorizeLODOption"] = self.colorizeLODOption
    
def updateSimulate(self, context):
    obj = GetArmature().children[0]
    obj["simulate"] = self.simulate
    obj.modifiers['Hairworks'].particle_system.use_hair_dynamics = self.simulate
    
def updateMassScale(self, context):
    obj = GetArmature().children[0]
    obj["massScale"] = self.massScale
    obj.modifiers['Hairworks'].particle_system.cloth.settings.mass = 0.03 * self.massScale
    
def updateDamping(self, context):
    obj = GetArmature().children[0]
    obj["damping"] = self.damping
    obj.modifiers['Hairworks'].particle_system.cloth.settings.air_damping = 10 * self.damping
    
def updateInertiaScale(self, context):
    GetArmature().children[0]["inertiaScale"] = self.inertiaScale
    
def updateInertiaLimit(self, context):
    GetArmature().children[0]["inertiaLimit"] = self.inertiaLimit
    
def updateWind(self, context):
    GetArmature().children[0]["wind"] = self.wind
    wind = GetWind()
    wind.rotation_euler = np.average(np.array([[np.pi*0.5, np.pi*0.25, np.pi*0.5], [np.pi*0.25, np.pi*0.5, np.pi*0.75], [0,0, np.pi*0.5]]), 0, abs(np.array(self.wind) + 0.0001))
    wind.field.strength = np.mean(self.wind)
    
def updateWindNoise(self, context):
    GetArmature().children[0]["windNoise"] = self.windNoise
    wind = GetWind()
    wind.field.noise = self.windNoise
    
def updateGravity(self, context):
    obj = GetArmature().children[0]
    obj["gravity"] = self.gravity
    obj.modifiers["Hairworks"].particle_system.settings.effector_weights.gravity = -self.gravity[2]
    
def updateStiffnessTexture(self, context):
    GetArmature().children[0]["stiffnessTexture"] = self.stiffnessTexture
    
def updateStiffnessTextureChan(self, context):
    GetArmature().children[0]["stiffnessTextureChan"] = self.stiffnessTextureChan
    
def updateStiffness(self, context):
    obj = GetArmature().children[0]
    obj["stiffness"] = self.stiffness
    obj.modifiers["Hairworks"].particle_system.cloth.settings.bending_stiffness = self.stiffness * 5
    
def updateStiffnessCurve(self, context):
    obj = GetArmature().children[0]
    obj["stiffnessCurve"] = self.stiffnessCurve
    mapping = obj.modifiers["SimulationCurves"].node_group.nodes["stiffnessCurve"].mapping
    for i, point in enumerate(mapping.curves[0].points):
        point.location[1] = self.stiffnessCurve[i]
    mapping.update()
    
def updateStiffnessStrength(self, context):
    GetArmature().children[0]["stiffnessStrength"] = self.stiffnessStrength
    
def updateStiffnessStrengthCurve(self, context):
    obj = GetArmature().children[0]
    obj["stiffnessStrengthCurve"] = self.stiffnessStrengthCurve
    mapping = obj.modifiers["SimulationCurves"].node_group.nodes["stiffnessStrengthCurve"].mapping
    for i, point in enumerate(mapping.curves[0].points):
        point.location[1] = self.stiffnessStrengthCurve[i]
    mapping.update()
    
def updateStiffnessDamping(self, context):
    obj = GetArmature().children[0]
    obj["stiffnessDamping"] = self.stiffnessDamping
    obj.modifiers["Hairworks"].particle_system.cloth.settings.bending_damping = self.stiffnessDamping
    
def updateStiffnessDampingCurve(self, context):
    obj = GetArmature().children[0]
    obj["stiffnessDampingCurve"] = self.stiffnessDampingCurve
    mapping = obj.modifiers["SimulationCurves"].node_group.nodes["stiffnessDampingCurve"].mapping
    for i, point in enumerate(mapping.curves[0].points):
        point.location[1] = self.stiffnessDampingCurve[i]
    mapping.update()
    
def updateRootStiffnessTexture(self, context):
    GetArmature().children[0]["rootStiffnessTexture"] = self.rootStiffnessTexture
    
def updateRootStiffnessTextureChan(self, context):
    GetArmature().children[0]["rootStiffnessTextureChan"] = self.rootStiffnessTextureChan

def updateRootStiffness(self, context):
    GetArmature().children[0]["rootStiffness"] = self.rootStiffness
    
def updateTipStiffness(self, context):
    GetArmature().children[0]["tipStiffness"] = self.tipStiffness
    
def updateBendStiffness(self, context):
    GetArmature().children[0]["bendStiffness"] = self.bendStiffness
    
def updateBendStiffnessCurve(self, context):
    obj = GetArmature().children[0]
    obj["bendStiffnessCurve"] = self.bendStiffnessCurve
    mapping = obj.modifiers["SimulationCurves"].node_group.nodes["bendStiffnessCurve"].mapping
    for i, point in enumerate(mapping.curves[0].points):
        point.location[1] = self.bendStiffnessCurve[i]
    mapping.update()
    
def updateBackStopRadius(self, context):
    obj = GetArmature().children[0]
    obj["backStopRadius"] = self.backStopRadius
    mods = obj.modifiers
    if self.backStopRadius > 0:
        mods.new(type='COLLISION', name = "Collision")
        obj.collision.thickness_outer = self.backStopRadius * 0.01
    elif 'Collision' in mods:
        mods.remove(mods['Collision'])
    
def updateFriction(self, context):
    GetArmature().children[0]["friction"] = self.friction
    sphere_coll = GetCollection("Collision Spheres", make_active=False) 
    connection_coll = GetCollection("Collision Connections", make_active=False) 
    
    objects = []
    if sphere_coll:
        objects.extend(sphere_coll.objects)
    if connection_coll:
        objects.extend(connection_coll.objects)
    
    for obj in objects:
        obj.modifiers['Collision'].settings.cloth_friction = self.friction * 80
    
def updateUseCollision(self, context):
    obj = GetArmature().children[0]
    obj["useCollision"] = self.useCollision
    settings = obj.modifiers["Hairworks"].particle_system.cloth.collision_settings
    main_coll = GetCollection(make_active=False)
    if self.useCollision:
        coll = GetCollection("No Collision", False, False)
        settings.collection = main_coll
        if coll:
            bpy.data.collections.remove(coll)
    else:
        coll = GetCollection("No Collision", True, False)
        settings.collection = coll
    
def updateCollisionOffset(self, context):
    obj = GetArmature().children[0]
    obj["collisionOffset"] = self.collisionOffset
    obj.modifiers["Hairworks"].particle_system.cloth.collision_settings.distance_min = self.collisionOffset
    
def updateInteractionStiffness(self, context):
    GetArmature().children[0]["interactionStiffness"] = self.interactionStiffness
    
def updateInteractionStiffnessCurve(self, context):
    obj = GetArmature().children[0]
    obj["interactionStiffnessCurve"] = self.interactionStiffnessCurve
    mapping = obj.modifiers["SimulationCurves"].node_group.nodes["interactionStiffnessCurve"].mapping
    for i, point in enumerate(mapping.curves[0].points):
        point.location[1] = self.interactionStiffnessCurve[i]
    mapping.update()
    
def updatePinStiffness(self, context):
    GetArmature().children[0]["pinStiffness"] = self.pinStiffness
    
def updateUseDynamicPin(self, context):
    GetArmature().children[0]["useDynamicPin"] = self.useDynamicPin
    
def updateDensityTexture(self, context):
    GetArmature().children[0]["densityTexture"] = self.densityTexture
    
def updateDensityTextureChan(self, context):
    GetArmature().children[0]["densityTextureChan"] = self.densityTextureChan
    
def updateDensity(self, context):
    obj = GetArmature().children[0]
    obj["density"] = self.density
    obj.modifiers["Hairworks"].particle_system.settings.child_percent = round(self.density * 64)
    obj.modifiers["Hairworks"].particle_system.settings.rendered_child_count = round(self.density * 64)
    
def updateUsePixelDensity(self, context):
    GetArmature().children[0]["usePixelDensity"] = self.usePixelDensity
    
def updateLengthTexture(self, context):
    GetArmature().children[0]["lengthTexture"] = self.lengthTexture
    
def updateLengthTextureChan(self, context):
    GetArmature().children[0]["lengthTextureChan"] = self.lengthTextureChan
    
def updateLengthScale(self, context):
    obj = GetArmature().children[0]
    obj["lengthScale"] = self.lengthScale
    obj.modifiers["Hairworks"].particle_system.settings.child_length = self.lengthScale
    
def updateLengthNoise(self, context):
    GetArmature().children[0]["lengthNoise"] = self.lengthNoise
    
def updateWidthTexture(self, context):
    GetArmature().children[0]["widthTexture"] = self.widthTexture
    
def updateWidthTextureChan(self, context):
    GetArmature().children[0]["widthTextureChan"] = self.widthTextureChan
    
def updateWidth(self, context):
    obj = GetArmature().children[0]
    obj["width"] = self.width
    obj.modifiers["Hairworks"].particle_system.settings.root_radius = (self.width * 0.1) * self.widthRootScale
    obj.modifiers["Hairworks"].particle_system.settings.tip_radius = (self.width * 0.1) * self.widthTipScale
    
def updateWidthNoise(self, context):
    GetArmature().children[0]["widthNoise"] = self.widthNoise
    
def updateRootWidthTexture(self, context):
    GetArmature().children[0]["rootWidthTexture"] = self.rootWidthTexture
    
def updateRootWidthTextureChan(self, context):
    GetArmature().children[0]["rootWidthTextureChan"] = self.rootWidthTextureChan
    
def updateWidthRootScale(self, context):
    obj = GetArmature().children[0]
    obj["widthRootScale"] = self.widthRootScale
    obj.modifiers["Hairworks"].particle_system.settings.root_radius = (self.width * 0.1) * self.widthRootScale
    
def updateTipWidthTexture(self, context):
    GetArmature().children[0]["tipWidthTexture"] = self.tipWidthTexture
    
def updateTipWidthTextureChan(self, context):
    GetArmature().children[0]["tipWidthTextureChan"] = self.tipWidthTextureChan
    
def updateWidthTipScale(self, context):
    obj = GetArmature().children[0]
    obj["widthTipScale"] = self.widthTipScale
    obj.modifiers["Hairworks"].particle_system.settings.tip_radius = (self.width * 0.1) * self.widthTipScale
    
def updateClumpScaleTexture(self, context):
    GetArmature().children[0]["clumpScaleTexture"] = self.clumpScaleTexture
    
def updateClumpScaleTextureChan(self, context):
    GetArmature().children[0]["clumpScaleTextureChan"] = self.clumpScaleTextureChan
    
def updateClumpScale(self, context):
    obj = GetArmature().children[0]
    obj["clumpScale"] = self.clumpScale
    obj.modifiers["Hairworks"].particle_system.settings.clump_factor = self.clumpScale
    
def updateClumpNumSubclumps(self, context):
    GetArmature().children[0]["clumpNumSubclumps"] = self.clumpNumSubclumps
    
def updateClumpPerVertex(self, context):
    GetArmature().children[0]["clumpPerVertex"] = self.clumpPerVertex
    
def updateClumpRoundnessTexture(self, context):
    GetArmature().children[0]["clumpRoundnessTexture"] = self.clumpRoundnessTexture
    
def updateClumpRoundnessTextureChan(self, context):
    GetArmature().children[0]["clumpRoundnessTextureChan"] = self.clumpRoundnessTextureChan
    
def updateClumpRoundness(self, context):
    obj = GetArmature().children[0]
    obj["clumpRoundness"] = self.clumpRoundness
    obj.modifiers["Hairworks"].particle_system.settings.clump_shape = self.clumpRoundness * 0.5 - 0.5
    
def updateClumpNoiseTexture(self, context):
    GetArmature().children[0]["clumpNoiseTexture"] = self.clumpNoiseTexture
    
def updateClumpNoiseTextureChan(self, context):
    GetArmature().children[0]["clumpNoiseTextureChan"] = self.clumpNoiseTextureChan
    
def updateClumpNoise(self, context):
    GetArmature().children[0]["clumpNoise"] = self.clumpNoise
    
def updateWaveScaletexture(self, context):
    GetArmature().children[0]["waveScaletexture"] = self.waveScaletexture
    
def updateWaveScaleTextureChan(self, context):
    GetArmature().children[0]["waveScaleTextureChan"] = self.waveScaleTextureChan
    
def updateWaveScale(self, context):
    obj = GetArmature().children[0]
    obj["waveScale"] = self.waveScale
    obj.modifiers["Hairworks"].particle_system.settings.kink_amplitude = self.waveScale * 0.01

def updateWaveScaleNoise(self, context):
    GetArmature().children[0]["waveScaleNoise"] = self.waveScaleNoise
    
def updateWaveScaleStrand(self, context):
    GetArmature().children[0]["waveScaleStrand"] = self.waveScaleStrand
    
def updateWaveScaleClump(self, context):
    obj = GetArmature().children[0]
    obj["waveScaleClump"] = self.waveScaleClump
    obj.modifiers["Hairworks"].particle_system.settings.kink_amplitude_clump = self.waveScaleClump
    
def updateWaveFreqTexture(self, context):
    GetArmature().children[0]["waveFreqTexture"] = self.waveFreqTexture
    
def updateWaveFreqTextureChan(self, context):
    GetArmature().children[0]["waveFreqTextureChan"] = self.waveFreqTextureChan
    
def updateWaveFreq(self, context):
    obj = GetArmature().children[0]
    obj["waveFreq"] = self.waveFreq
    obj.modifiers["Hairworks"].particle_system.settings.kink_frequency = self.waveFreq
    
def updateWaveFreqNoise(self, context):
    GetArmature().children[0]["waveFreqNoise"] = self.waveFreqNoise
    
def updateWaveRootStraighten(self, context):
    obj = GetArmature().children[0]
    obj["waveRootStraighten"] = self.waveRootStraighten
    obj.modifiers["Hairworks"].particle_system.settings.kink_shape = self.waveRootStraighten * 0.5
    
def updateBaseColor(self, context):
    GetArmature().children[0]["baseColor"] = self.baseColor
    
def updateAlpha(self, context):
    GetArmature().children[0]["alpha"] = self.alpha
    
def updateRootColorTexture(self, context):
    GetArmature().children[0]["rootColorTexture"] = self.rootColorTexture
    
def updateRootColor(self, context):
    obj = GetArmature().children[0]
    obj["rootColor"] = self.rootColor
    obj.data.materials[0].node_tree.nodes["Root Color"].outputs["Color"].default_value = self.rootColor

def updateTipColorTexture(self, context):
    GetArmature().children[0]["tipColorTexture"] = self.tipColorTexture
    
def updateTipColor(self, context):
    obj = GetArmature().children[0]
    obj["tipColor"] = self.tipColor
    obj.data.materials[0].node_tree.nodes["Tip Color"].outputs["Color"].default_value = self.tipColor
    
def updateRootTipColorWeight(self, context):
    obj = GetArmature().children[0]
    obj["rootTipColorWeight"] = self.rootTipColorWeight
    obj.data.materials[0].node_tree.nodes["Root Tip Weight"].outputs["Value"].default_value = self.rootTipColorWeight

def updateRootTipColorFalloff(self, context):
    obj = GetArmature().children[0]
    obj["rootTipColorFalloff"] = self.rootTipColorFalloff
    obj.data.materials[0].node_tree.nodes["Root Tip Falloff"].outputs["Value"].default_value = self.rootTipColorFalloff
    
def updateRootAlphaFalloff(self, context):
    obj = GetArmature().children[0]
    obj["rootAlphaFalloff"] = self.rootAlphaFalloff
    obj.data.materials[0].node_tree.nodes["Root Alpha Falloff"].outputs["Value"].default_value = self.rootAlphaFalloff
    
def updateStrandTexture(self, context):
    GetArmature().children[0]["strandTexture"] = self.strandTexture
    
def updateStrandBlendMode(self, context):
    GetArmature().children[0]["strandBlendMode"] = self.strandBlendMode
    
def updateStrandBlendScale(self, context):
    GetArmature().children[0]["strandBlendScale"] = self.strandBlendScale
    
def updateTextureBrightness(self, context):
    GetArmature().children[0]["textureBrightness"] = self.textureBrightness
    
def updateDiffuseColor(self, context):
    GetArmature().children[0]["diffuseColor"] = self.diffuseColor
    
def updateDiffuseBlend(self, context):
    GetArmature().children[0]["diffuseBlend"] = self.diffuseBlend
    
def updateDiffuseScale(self, context):
    GetArmature().children[0]["diffuseScale"] = self.diffuseScale
    
def updateDiffuseHairNormalWeight(self, context):
    GetArmature().children[0]["diffuseHairNormalWeight"] = self.diffuseHairNormalWeight
    
def updateDiffuseBoneIndex(self, context):
    GetArmature().children[0]["diffuseBoneIndex"] = self.diffuseBoneIndex
    
def updateDiffuseBoneLocalPos(self, context):
    GetArmature().children[0]["diffuseBoneLocalPos"] = self.diffuseBoneLocalPos
    
def updateDiffuseNoiseScale(self, context):
    GetArmature().children[0]["diffuseNoiseScale"] = self.diffuseNoiseScale
    
def updateDiffuseNoiseGain(self, context):
    GetArmature().children[0]["diffuseNoiseGain"] = self.diffuseNoiseGain
    
def updateDiffuseNoiseFreqU(self, context):
    GetArmature().children[0]["diffuseNoiseFreqU"] = self.diffuseNoiseFreqU
    
def updateDiffuseNoiseFreqV(self, context):
    GetArmature().children[0]["diffuseNoiseFreqV"] = self.diffuseNoiseFreqV
    
def updateSpecularTexture(self, context):
    GetArmature().children[0]["specularTexture"] = self.specularTexture
    
def updateSpecularColor(self, context):
    obj = GetArmature().children[0]
    obj["specularColor"] = self.specularColor
    obj.data.materials[0].node_tree.nodes["Specular Color"].outputs["Color"].default_value = self.specularColor
    
def updateSpecularNoiseScale(self, context):
    GetArmature().children[0]["specularNoiseScale"] = self.specularNoiseScale
    
def updateSpecularEnvScale(self, context):
    GetArmature().children[0]["specularEnvScale"] = self.specularEnvScale
    
def updateSpecularPrimary(self, context):
    obj = GetArmature().children[0]
    obj["specularPrimary"] = self.specularPrimary
    obj.data.materials[0].node_tree.nodes["Primary Specular Scale"].outputs["Value"].default_value = self.specularPrimary
    
def updateSpecularPowerPrimary(self, context):
    obj = GetArmature().children[0]
    obj["specularPowerPrimary"] = self.specularPowerPrimary
    obj.data.materials[0].node_tree.nodes["Primary Specular Shininess"].outputs["Value"].default_value = self.specularPowerPrimary
    
def updateSpecularPrimaryBreakup(self, context):
    GetArmature().children[0]["specularPrimaryBreakup"] = self.specularPrimaryBreakup
    
def updateSpecularSecondary(self, context):
    obj = GetArmature().children[0]
    obj["specularSecondary"] = self.specularSecondary
    obj.data.materials[0].node_tree.nodes["Secondary Specular Scale"].outputs["Value"].default_value = self.specularSecondary
    
def updateSpecularPowerSecondary(self, context):
    obj = GetArmature().children[0]
    obj["specularPowerSecondary"] = self.specularPowerSecondary
    obj.data.materials[0].node_tree.nodes["Secondary Specular Shininess"].outputs["Value"].default_value = self.specularPowerSecondary
    
def updateSpecularSecondaryOffset(self, context):
    obj = GetArmature().children[0]
    obj["specularSecondaryOffset"] = self.specularSecondaryOffset
    obj.data.materials[0].node_tree.nodes["Secondary Specular Offset"].outputs["Value"].default_value = self.specularSecondaryOffset
    
def updateGlintStrength(self, context):
    obj = GetArmature().children[0]
    obj["glintStrength"] = self.glintStrength
    obj.data.materials[0].node_tree.nodes["Glint Scale"].outputs["Value"].default_value = self.glintStrength
    
def updateGlintCount(self, context):
    obj = GetArmature().children[0]
    obj["glintCount"] = self.glintCount
    obj.data.materials[0].node_tree.nodes["Glint Size"].outputs["Value"].default_value = self.glintCount
    
def updateGlintExponent(self, context):
    obj = GetArmature().children[0]
    obj["glintExponent"] = self.glintExponent
    obj.data.materials[0].node_tree.nodes["Glint Power"].outputs["Value"].default_value = self.glintExponent
    
def updateUseShadows(self, context):
    GetArmature().children[0]["useShadows"] = self.useShadows
    
def updateCastShadows(self, context):
    obj = GetArmature().children[0]
    obj["castShadows"] = self.castShadows
    obj.data.materials[0].node_tree.nodes['Control Cast Shadows'].inputs[1].default_value = self.castShadows
    
def updateReceiveShadows(self, context):
    GetArmature().children[0]["receiveShadows"] = self.receiveShadows
    
def updateShadowSigma(self, context):
    GetArmature().children[0]["shadowSigma"] = self.shadowSigma
    
def updateShadowDensityScale(self, context):
    GetArmature().children[0]["shadowDensityScale"] = self.shadowDensityScale
    
def updateUseViewfrustrumCulling(self, context):
    GetArmature().children[0]["useViewfrustrumCulling"] = self.useViewfrustrumCulling
    
def updateUseBackfaceCulling(self, context):
    GetArmature().children[0]["useBackfaceCulling"] = self.useBackfaceCulling
    
def updateBackfaceCullingThreshold(self, context):
    GetArmature().children[0]["backfaceCullingThreshold"] = self.backfaceCullingThreshold
    
def updateEnableDistanceLOD(self, context):
    GetArmature().children[0]["enableDistanceLOD"] = self.enableDistanceLOD
    
def updateDistanceLODStart(self, context):
    GetArmature().children[0]["distanceLODStart"] = self.distanceLODStart
    
def updateDistanceLODEnd(self, context):
    GetArmature().children[0]["distanceLODEnd"] = self.distanceLODEnd
    
def updateDistanceLODFadeStart(self, context):
    GetArmature().children[0]["distanceLODFadeStart"] = self.distanceLODFadeStart
    
def updateDistanceLODWidth(self, context):
    GetArmature().children[0]["distanceLODWidth"] = self.distanceLODWidth
    
def updateDistanceLODDensity(self, context):
    GetArmature().children[0]["distanceLODDensity"] = self.distanceLODDensity
    
def updateEnableDetailLOD(self, context):
    GetArmature().children[0]["enableDetailLOD"] = self.enableDetailLOD
    
def updateDetailLODStart(self, context):
    GetArmature().children[0]["detailLODStart"] = self.detailLODStart
    
def updateDetailLODEnd(self, context):
    GetArmature().children[0]["detailLODEnd"] = self.detailLODEnd
    
def updateDetailLODWidth(self, context):
    GetArmature().children[0]["detailLODWidth"] = self.detailLODWidth
    
def updateDetailLODDensity(self, context):
    GetArmature().children[0]["detailLODDensity"] = self.detailLODDensity
        
PROPS_HairMaterial_Panel = [
('HairworksMaterialSubPanel', EnumProperty(
        name="Hairworks Material SubPanel",
        description="Set the active Hairworks material subpanel",
        items=(
            ('hair_visualization', "hair_visualization", "Show the Hairworks visualization subpanel", 'HIDE_OFF', 0),
            ('hair_physics', "hair_physics", "Show the Hairworks physical parameters subpanel", 'SETTINGS', 1),
            ('hair_graphics', "hair_graphics", "Show the Hairworks graphical parameters subpanel", 'COLOR', 2),
            ('hair_lod', "hair_lod", "Show the Hairworks lod parameters subpanel", 'MOD_DECIM', 3)
        ),
        default='hair_visualization'
    )),
('enable', BoolProperty(
        name="Enable",
        description="Toggles hair assets on/off",
        default=True,
        update=updateEnable
    )),
('useTextures', BoolProperty(
        name="Use Textures",
        description="Enable/Disable the use of textures",
        default=False,
        update=updateUseTextures
    )),
('matName', StringProperty(
        name="Name",
        description="Name of the Hairworks material",
        default='',
        update=updateMatName
    )),
('textureDirName', StringProperty(
        name="Texture Directory Name",
        description="Name of the directory where to find the textures",
        default='',
        update=updateTextureDirName
    )),
('splineMultiplier', IntProperty(
        name="Spline Multiplier",
        description="Number of render vertices per line segment of guide hairs. Higher value makes each hair appear smooth, but will slow down rendering",
        default=3,
        min=1,
        max=4,
        update=updateSplineMultiplier
    )),
('assetType', IntProperty(
        name="Asset Type",
        description="This is a generic int settings that can allow developers to do custom filtering of assets if desired",
        default=0,
        min=0,
        max=99,
        update=updateAssetType
    )),
('assetPriority', IntProperty(
        name="Asset Priority",
        description="This is a generic int settings that can allow developers to do custom filtering of assets if desired",
        default=0,
        min=0,
        max=99,
        update=updateAssetPriority
    )),
('assetGroup', IntProperty(
        name="Asset Group",
        description="This is a generic int settings that can allow developers to do custom filtering of assets if desired",
        default=0,
        min=0,
        max=99,
        update=updateAssetGroup
    )),
('drawRenderHairs', BoolProperty(
        name="Draw Render Hairs",
        description="Display the rendered hair for the currently selected asset",
        default=True,
        update=updateDrawRenderHairs
    )),
('visualizeGuideHairs', BoolProperty(
        name="Visualize Guide Hairs",
        description="Display the guide curves for the currently selected asset as red lines",
        default=False,
        update=updateVisualizeGuideHairs
    )),
('visualizeSkinnedGuideHairs', BoolProperty(
        name="Visualize Skinned Guide Hairs",
        description="Display the guide curves at skinned location (no simulation) for the currently selected asset as yellow lines",
        default=False,
        update=updateVisualizeSkinnedGuideHairs
    )),
('visualizeControlVertices', BoolProperty(
        name="Visualize Control Vertices",
        description="Display the control vertices for the guide curves on the selected hair asset",
        default=False,
        update=updateVisualizeControlVertices
    )),
('visualizeGrowthMesh', BoolProperty(
        name="Visualize Growth Mesh",
        description="Display the growth mesh used for the currently selected asset",
        default=False,
        update=updateVisualizeGrowthMesh
    )),
('visualizeBones', BoolProperty(
        name="Visualize Bones",
        description="Display bones for the currently selected hair asset",
        default=False,
        update=updateVisualizeBones
    )),
('visualizeBoundingBox', BoolProperty(
        name="Visualize Bounding Box",
        description="Display bounding box for the currently selected hair asset. Yellow bounding box indicates bounds for the growth mesh only and pink bounding box indicates bounds for entire hair",
        default=False,
        update=updateVisualizeBoundingBox
    )),
('visualizeCapsules', BoolProperty(
        name="Visualize Capsules",
        description="Display collision capsules for the currently selected hair asset",
        default=False,
        update=updateVisualizeCapsules
    )),
('visualizeHairInteractions', BoolProperty(
        name="Visualize Hair Interactions",
        description="Display links used for hair interaction. Pink means each interaction link is within original distance; green means interaction links are too stretched (interaction handling is inactive or low)",
        default=False,
        update=updateVisualizeHairInteractions
    )),
('visualizePinConstraints', BoolProperty(
        name="Visualize Pin Constraints",
        description="Display the pin constraint shape",
        default=False,
        update=updateVisualizePinConstraints
    )),
('visualizeShadingNormals', BoolProperty(
        name="Visualize Shading Normals",
        description="Display normals used for shading. Hairworks internally generates surface normal for hair surface. This is useful for matching mesh based shading where hair normals are not defined. Use this option to visualize and adjust hair normals",
        default=False,
        update=updateVisualizeShadingNormals
    )),
('visualizeCullSphere', BoolProperty(
        name="Visualize Cull Sphere",
        description="Display cull sphere",
        default=False,
        update=updateVisualizeCullSphere
    )),
('visualizeDiffuseBone', BoolProperty(
        name="Visualize Diffuse Bone",
        description="Display diffuse bone",
        default=False,
        update=updateVisualizeDiffuseBone
    )),
('visualizeFrames', BoolProperty(
        name="Visualize Frames",
        description="Display coordinate frames",
        default=False,
        update=updateVisualizeFrames
    )),
('visualizeLocalPos', BoolProperty(
        name="Visualize Local Position",
        description="Display target pose for bending",
        default=False,
        update=updateVisualizeLocalPos
    )),
('visualizeHairSkips', IntProperty(
        name="Visualize Hair Skips",
        description="The number of hairs to skip for per hair visualization",
        default=0,
        min=0,
        update=updateVisualizeHairSkips
    )),
('colorizeLODOption', EnumProperty(
        name="Colorize LOD Option",
        description="Renders the hair strands in different colors depending on what the user is trying to analyze. Options are None, LOD, Tangents, Normals, and Constant Red. For LOD, greener colors indicate closer distance (more detail) and blue color indicates far distance (less detail)",
        items=(
            ('0', "None", ""),
            ('1', "LOD", ""),
            ('2', "Tangents", ""),
            ('3', "Normal", ""),
            ('4', "Constant Red", "")
        ),
        default='0',
        update=updateColorizeLODOption
    )),
('simulate', BoolProperty(
        name="Simulate",
        description="Toggle the simulation of the hair on/off",
        default=True,
        update=updateSimulate
    )),
('massScale', FloatProperty(
        name="Mass Scale",
        description="Determines the weight of the hair by increasing or decreasing the mass of the hair. This value is always set in meter unit, regardless of what the scene scale is set to",
        default=1,
        min=-50,
        max=50,
        update=updateMassScale
    )),
('damping', FloatProperty(
        name="Damping",
        description="The strength of the influence of movement that slows down the fur strands such as air drag or water",
        default=0,
        min=0,
        max=1,
        update=updateDamping
    )),
('inertiaScale', FloatProperty(
        name="Inertia Scale",
        description="When character moves unrealistically fast, hair simulation may produce jerky and wild motion. Use inertia scale to tone down such behavior. No inertia: 0, full inertia motion: 1",
        default=1,
        min=0,
        max=1,
        update=updateInertiaScale
    )),
('inertiaLimit', FloatProperty(
        name="Inertia Limit",
        description="Defines velocity threshold when inertia scale should become active",
        default=1000,
        min=0,
        max=1000,
        update=updateInertiaLimit
    )),
('wind', FloatVectorProperty(
        name="Wind",
        description="Defines the wind orientation and strength",
        default=(0,0,0),
        update=updateWind
    )),
('windNoise', FloatProperty(
        name="Wind Noise",
        description="Defines the wind noise",
        default=0,
        min=0,
        update=updateWindNoise
    )),
('gravity', FloatVectorProperty(
        name="Gravity",
        description="Defines the gravity orientation and strength",
        default=(0,0,-1),
        update=updateGravity
    )),
#("stiffnessTexture", PointerProperty(
#        name="Stiffness Texture",
#        description="The limits on how close each individual hair stays to the skinned position. If a texture map is used, then the texture will influence the stiffness calculation for each simulated (guide) hair",
#        type=bpy.types.Image,
#        update = updateStiffnessTexture
#    )),
("stiffnessTexture", StringProperty(
        name="Stiffness Texture",
        description="The limits on how close each individual hair stays to the skinned position. If a texture map is used, then the texture will influence the stiffness calculation for each simulated (guide) hair",
        default='',
        update = updateStiffnessTexture
    )),
('stiffnessTextureChan', EnumProperty(
        name="Stiffness Texture Channel",
        description="Defines the channel used to control the stiffness",
        items=(
            ('0', "R", ""),
            ('1', "G", ""),
            ('2', "B", ""),
            ('3', "A", "")
        ),
        default='0',
        update=updateStiffnessTextureChan
    )),
('stiffness', FloatProperty(
        name="Stiffness",
        description="The limits on how close each individual hair stays to the skinned position. If a texture map is used, then the texture will influence the stiffness calculation for each simulated (guide) hair",
        default=0.5,
        min=0,
        max=1,
        update=updateStiffness
    )),
('stiffnessCurve', FloatVectorProperty(
        name="Stiffness Curve",
        description="Defines the stiffness along simulated (guide) hairs",
        size = 4,
        default = (1,1,1,1),
        min = -0.2,
        max = 1.2,
        update=updateStiffnessCurve
    )),
("stiffnessCurveToggle", BoolProperty(
        name = "Stiffness Curve Toggle",
        default = False
    )),
('stiffnessStrength', FloatProperty(
        name="Stiffness Strength",
        description="The strength of the spring (bounciness) of the hair to return from a simulated position to its resting stiffness. Full springiness is 0, and 1 is no spring",
        default=1,
        min=0,
        max=1,
        update=updateStiffnessStrength
    )),
('stiffnessStrengthCurve', FloatVectorProperty(
        name="Stiffness Strength Curve",
        description="Defines the stiffness strength along simulated (guide) hairs",
        size = 4,
        default = (1,1,1,1),
        min = -0.2,
        max = 1.2,
        update=updateStiffnessStrengthCurve
    )),
("stiffnessStrengthCurveToggle", BoolProperty(
        name = "Stiffness Strength Curve Toggle",
        default = False
    )),
('stiffnessDamping', FloatProperty(
        name="Stiffness Damping",
        description="The speed of the spring (bounciness) of the hair to return from a simulated position to its resting stiffness. 1: full damping (slowest/no motion), 0: no damping (fastest)",
        default=0,
        min=0,
        max=1,
        update=updateStiffnessDamping
    )),
('stiffnessDampingCurve', FloatVectorProperty(
        name="Stiffness Damping Curve",
        description="Defines the stiffness damping along simulated (guide) hairs",
        size = 4,
        default = (1,1,1,1),
        min = -0.2,
        max = 1.2,
        update=updateStiffnessDampingCurve
    )),
("stiffnessDampingCurveToggle", BoolProperty(
        name = "Stiffness Damping Curve Toggle",
        default = False
    )),
#("rootStiffnessTexture", PointerProperty(
#        name="Root Stiffness Texture",
#        description="The strength of stiffness that weakens toward the tip of the hair. If a texture map is used, then the texture will influence the stiffness calculation for each simulated (guide) hair",
#        type=bpy.types.Image,
#        update = updateRootStiffnessTexture
#    )),
("rootStiffnessTexture", StringProperty(
        name="Root Stiffness Texture",
        description="The strength of stiffness that weakens toward the tip of the hair. If a texture map is used, then the texture will influence the stiffness calculation for each simulated (guide) hai",
        default='',
        update = updateRootStiffnessTexture
    )),
('rootStiffnessTextureChan', EnumProperty(
        name="Root Stiffness Texture Channel",
        description="Defines the channel used to control the root stiffness",
        items=(
            ('0', "R", ""),
            ('1', "G", ""),
            ('2', "B", ""),
            ('3', "A", "")
        ),
        default='0',
        update=updateRootStiffnessTextureChan
    )),
('rootStiffness', FloatProperty(
        name="Root Stiffness",
        description="The strength of stiffness that weakens toward the tip of the hair. If a texture map is used, then the texture will influence the stiffness calculation for each simulated (guide) hair",
        default=0.5,
        min=0,
        max=1,
        update=updateRootStiffness
    )),
('tipStiffness', FloatProperty(
        name="Tip Stiffness",
        description="The strength of stiffness that weakens toward the root of the hair",
        default=0,
        min=0,
        max=1,
        update=updateTipStiffness
    )),
('bendStiffness', FloatProperty(
        name="Bend Stiffness",
        description="The strength of how hair tries to maintain initial curvy hair shapes",
        default=0,
        min=0,
        max=1,
        update=updateBendStiffness
    )),
('bendStiffnessCurve', FloatVectorProperty(
        name="Bend Stiffness Curve",
        description="Defines the bend stiffness along simulated (guide) hairs",
        size = 4,
        default = (1,1,1,1),
        min = -0.2,
        max = 1.2,
        update=updateBendStiffnessCurve
    )),
("bendStiffnessCurveToggle", BoolProperty(
        name = "Bend Stiffness Curve Toggle",
        default = False
    )),
('backStopRadius', FloatProperty(
        name="Backstop Radius",
        description="Approximates the surface of the growth mesh to use as collision. A value of 0 does not use the solution while a value of 1.0 uses the average edge length of the entire growth mesh to determine an approximation. A side effect of this is that it can artificially fluff up the root of the hairs. This can be desired or undesired",
        default=0,
        min=0,
        max=1,
        update=updateBackStopRadius
    )),
('friction', FloatProperty(
        name="Friction",
        description="Hair to collision shape interaction. Typical values are from 0.0 to 0.1",
        default=0,
        min=0,
        max=10,
        update=updateFriction
    )),
('useCollision', BoolProperty(
        name="Use Collision",
        description="Enables collision handling against collision shapes if they are present",
        default=False,
        update=updateUseCollision
    )),
('collisionOffset', FloatProperty(
        name="Collision Offset",
        description="Defines the offset distance between hair and collision shapes",
        default=0,
        min=0,
        update=updateCollisionOffset
    )),
('interactionStiffness', FloatProperty(
        name="Interaction Stiffness",
        description="Helps the hair simulate in groups. 1.0 means full interaction",
        default=0,
        min=0,
        max=1,
        update=updateInteractionStiffness
    )),
('interactionStiffnessCurve', FloatVectorProperty(
        name="Interaction Stiffness Curve",
        description="Defines the interaction stiffness along simulated (guide) hairs",
        size = 4,
        default = (1,1,1,1),
        min = -0.2,
        max = 1.2,
        update=updateInteractionStiffnessCurve
    )),
("interactionStiffnessCurveToggle", BoolProperty(
        name = "Interaction Stiffness Curve Toggle",
        default = False
    )),
('pinStiffness', FloatProperty(
        name="Pin Stiffness",
        description="Scales the stiffness of all the pins",
        default=1,
        min=0,
        max=1,
        update=updatePinStiffness
    )),
('useDynamicPin', BoolProperty(
        name="Use Dynamic Pin",
        description="Allows the use of dynamic pins for this asset",
        default=False,
        update=updateUseDynamicPin
    )),
#("densityTexture", PointerProperty(
#        name="Density Texture",
#        description="The amount of hair strands produced by interpolation between the guide curves. A value of 0 produces no hair. Currently, a density value of 1.0 produces 64 hairs per each triangle of growth mesh. A value above 1.0 will scale the number of hairs correspondingly (a value of 2 would yield 128 hairs or a value of 10 would have 640). If a texture control is used, then this control becomes a multiplier for the texture. A texture control by default is sampled per vertex in UV space",
#        type=bpy.types.Image,
#        update = updateDensityTexture
#    )),
("densityTexture", StringProperty(
        name="Density Texture",
        description="The amount of hair strands produced by interpolation between the guide curves. A value of 0 produces no hair. Currently, a density value of 1.0 produces 64 hairs per each triangle of growth mesh. A value above 1.0 will scale the number of hairs correspondingly (a value of 2 would yield 128 hairs or a value of 10 would have 640). If a texture control is used, then this control becomes a multiplier for the texture. A texture control by default is sampled per vertex in UV space",
        default='',
        update = updateDensityTexture
    )),
('densityTextureChan', EnumProperty(
        name="Density Texture Channel",
        description="Defines the channel used to control the density",
        items=(
            ('0', "R", ""),
            ('1', "G", ""),
            ('2', "B", ""),
            ('3', "A", "")
        ),
        default='0',
        update=updateDensityTextureChan
    )),
('density', FloatProperty(
        name="Density",
        description="The amount of hair strands produced by interpolation between the guide curves. A value of 0 produces no hair. Currently, a density value of 1.0 produces 64 hairs per each triangle of growth mesh. A value above 1.0 will scale the number of hairs correspondingly (a value of 2 would yield 128 hairs or a value of 10 would have 640). If a texture control is used, then this control becomes a multiplier for the texture. A texture control by default is sampled per vertex in UV space",
        default=1,
        min=0,
        max=10,
        update=updateDensity
    )),
('usePixelDensity', BoolProperty(
        name="Use Pixel Density",
        description="If a texture map is used to control density, then the texture will influence the density calculation per pixel in UV space instead of the default per vertex. Users should note, however, that using this option may result in a significant performance drop, so this option should be used only when absolutely necessary",
        default=False,
        update=updateUsePixelDensity
    )),
#("lengthTexture", PointerProperty(
#        name="Length Texture",
#        description="Only grows the hair to a percentage of the full length. A value of 0 is no hair and value of 1 is 100% length. If a texture control is used, then this control becomes a multiplier for the texture. A texture control by default is sampled per vertex in UV space",
#        type=bpy.types.Image,
#        update = updateLengthTexture
#    )),
("lengthTexture", StringProperty(
        name="Length Texture",
        description="Only grows the hair to a percentage of the full length. A value of 0 is no hair and value of 1 is 100% length. If a texture control is used, then this control becomes a multiplier for the texture. A texture control by default is sampled per vertex in UV space",
        default='',
        update = updateLengthTexture
    )),
('lengthTextureChan', EnumProperty(
        name="Length Texture Channel",
        description="Defines the channel used to control the length",
        items=(
            ('0', "R", ""),
            ('1', "G", ""),
            ('2', "B", ""),
            ('3', "A", "")
        ),
        default='0',
        update=updateLengthTextureChan
    )),
('lengthScale', FloatProperty(
        name="Length Scale",
        description="Only grows the hair to a percentage of the full length. A value of 0 is no hair and value of 1 is 100% length. If a texture control is used, then this control becomes a multiplier for the texture. A texture control by default is sampled per vertex in UV space",
        default=1,
        min=0,
        max=1,
        update=updateLengthScale
    )),
('lengthNoise', FloatProperty(
        name="Length Noise",
        description="The strength of random value noise that is applied to the length of the interpolated hairs resulting in non uniformly interpolated hairs",
        default=1,
        min=0,
        max=1,
        update=updateLengthNoise
    )),
#("widthTexture", PointerProperty(
#        name="Width Texture",
#        description="Determines the base width of each hair. All other parameters in this group as well as their textures act as multipliers to this value. This value is always set in millimeters, regardless of what the scene scale is set to",
#        type=bpy.types.Image,
#        update = updateWidthTexture
#    )),
("widthTexture", StringProperty(
        name="Width Texture",
        description="Determines the base width of each hair. All other parameters in this group as well as their textures act as multipliers to this value. This value is always set in millimeters, regardless of what the scene scale is set to",
        default='',
        update = updateWidthTexture
    )),
('widthTextureChan', EnumProperty(
        name="Width Texture Channel",
        description="Defines the channel used to control the width",
        items=(
            ('0', "R", ""),
            ('1', "G", ""),
            ('2', "B", ""),
            ('3', "A", "")
        ),
        default='0',
        update=updateWidthTextureChan
    )),
('width', FloatProperty(
        name="Width",
        description="Determines the base width of each hair. All other parameters in this group as well as their textures act as multipliers to this value. This value is always set in millimeters, regardless of what the scene scale is set to",
        default=1,
        min=0,
        max=10,
        update=updateWidth
    )),
('widthNoise', FloatProperty(
        name="Width Noise",
        description="The strength of random value noise that is applied to the overall width of individual hairs",
        default=1,
        min=0,
        max=1,
        update=updateWidthNoise
    )),
#("rootWidthTexture", PointerProperty(
#        name="Root Width Texture",
#        description="Multiplier to the width scale that applies toward the root of each individual hair. If a texture map is used, then the sampled texture values per each hair will be multiplied to this constant. The combined value then acts as multiplier to the base scale value",
#        type=bpy.types.Image,
#        update = updateRootWidthTexture
#    )),
("rootWidthTexture", StringProperty(
        name="Root Width Texture",
        description="Multiplier to the width scale that applies toward the root of each individual hair. If a texture map is used, then the sampled texture values per each hair will be multiplied to this constant. The combined value then acts as multiplier to the base scale value",
        default='',
        update = updateRootWidthTexture
    )),
('rootWidthTextureChan', EnumProperty(
        name="Root Width Texture Channel",
        description="Defines the channel used to control the root width",
        items=(
            ('0', "R", ""),
            ('1', "G", ""),
            ('2', "B", ""),
            ('3', "A", "")
        ),
        default='0',
        update=updateRootWidthTextureChan
    )),
('widthRootScale', FloatProperty(
        name="Width Root Scale",
        description="Multiplier to the width scale that applies toward the root of each individual hair. If a texture map is used, then the sampled texture values per each hair will be multiplied to this constant. The combined value then acts as multiplier to the base scale value",
        default=1,
        min=0,
        max=1,
        update=updateWidthRootScale
    )),
#("tipWidthTexture", PointerProperty(
#        name="Tip Width Texture",
#        description="Multiplier to the width scale that applies toward the tip of each individual hair. If a texture map is used, then the sampled texture values per each hair will be multiplied to this constant. The combined value then acts as multiplier to the base scale value",
#        type=bpy.types.Image,
#        update = updateTipWidthTexture
#    )),
("tipWidthTexture", StringProperty(
        name="Tip Width Texture",
        description="Multiplier to the width scale that applies toward the tip of each individual hair. If a texture map is used, then the sampled texture values per each hair will be multiplied to this constant. The combined value then acts as multiplier to the base scale value",
        default='',
        update = updateTipWidthTexture
    )),
('tipWidthTextureChan', EnumProperty(
        name="Tip Width Texture Channel",
        description="Defines the channel used to control the tip width",
        items=(
            ('0', "R", ""),
            ('1', "G", ""),
            ('2', "B", ""),
            ('3', "A", "")
        ),
        default='0',
        update=updateTipWidthTextureChan
    )),
('widthTipScale', FloatProperty(
        name="Width Tip Scale",
        description="Multiplier to the width scale that applies toward the tip of each individual hair. If a texture map is used, then the sampled texture values per each hair will be multiplied to this constant. The combined value then acts as multiplier to the base scale value",
        default=0.1,
        min=0,
        max=1,
        update=updateWidthTipScale
    )),
#("clumpScaleTexture", PointerProperty(
#        name="Clump Scale Texture",
#        description="The strength of clump that is applied to each individual hair. If a texture map is used, then the sampled texture value per hair will act as a multiplier to this constant value",
#        type=bpy.types.Image,
#        update = updateClumpScaleTexture
#    )),
("clumpScaleTexture", StringProperty(
        name="Clump Scale Texture",
        description="The strength of clump that is applied to each individual hair. If a texture map is used, then the sampled texture value per hair will act as a multiplier to this constant value",
        default='',
        update = updateClumpScaleTexture
    )),
('clumpScaleTextureChan', EnumProperty(
        name="Clump Scale Texture Channel",
        description="Defines the channel used to control the clump scale",
        items=(
            ('0', "R", ""),
            ('1', "G", ""),
            ('2', "B", ""),
            ('3', "A", "")
        ),
        default='0',
        update=updateClumpScaleTextureChan
    )),
('clumpScale', FloatProperty(
        name="Clump Scale",
        description="The strength of clump that is applied to each individual hair. If a texture map is used, then the sampled texture value per hair will act as a multiplier to this constant value",
        default=0,
        min=0,
        max=1,
        update=updateClumpScale
    )),
('clumpNumSubclumps', IntProperty(
        name="Clump Num Subclumps",
        description="Defines the number of subclumps per clump",
        default=0,
        min=0,
        update=updateClumpNumSubclumps
    )),
('clumpPerVertex', BoolProperty(
        name="Clump Per Vertex",
        description="If set to true, the clump will be created per vertex. How is that different from the default per hair?",
        default=False,
        update=updateClumpPerVertex
    )),
#("clumpRoundnessTexture", PointerProperty(
#        name="Clump Roundness Texture",
#        description="Determines the roundness of each clump. A value of 0 is a concave clump, a value of 2.0 is a convex clump, and the default value of 1.0 is a neutral clump",
#        type=bpy.types.Image,
#        update = updateClumpRoundnessTexture
#    )),
("clumpRoundnessTexture", StringProperty(
        name="Clump Roundness Texture",
        description="Determines the roundness of each clump. A value of 0 is a concave clump, a value of 2.0 is a convex clump, and the default value of 1.0 is a neutral clump",
        default='',
        update = updateClumpRoundnessTexture
    )),
('clumpRoundnessTextureChan', EnumProperty(
        name="Clump Roundness Texture Channel",
        description="Defines the channel used to control the clump roundness",
        items=(
            ('0', "R", ""),
            ('1', "G", ""),
            ('2', "B", ""),
            ('3', "A", "")
        ),
        default='0',
        update=updateClumpRoundnessTextureChan
    )),
('clumpRoundness', FloatProperty(
        name="Clump Roundness",
        description="Determines the roundness of each clump. A value of 0 is a concave clump, a value of 2.0 is a convex clump, and the default value of 1.0 is a neutral clump",
        default=1,
        min=0.01,
        max=2,
        update=updateClumpRoundness
    )),
#("clumpNoiseTexture", PointerProperty(
#        name="Clump Noise Texture",
#        description="The strength of the percentage of hairs that are included in each clump",
#        type=bpy.types.Image,
#        update=updateClumpNoiseTexture
#    )),
("clumpNoiseTexture", StringProperty(
        name="Clump Noise Texture",
        description="The strength of the percentage of hairs that are included in each clump",
        default='',
        update=updateClumpNoiseTexture
    )),
('clumpNoiseTextureChan', EnumProperty(
        name="Clump Noise Texture Channel",
        description="Defines the channel used to control the clump noise",
        items=(
            ('0', "R", ""),
            ('1', "G", ""),
            ('2', "B", ""),
            ('3', "A", "")
        ),
        default='0',
        update=updateClumpNoiseTextureChan
    )),
('clumpNoise', FloatProperty(
        name="Clump Noise",
        description="The strength of the percentage of hairs that are included in each clump",
        default=0,
        min=0,
        max=1,
        update=updateClumpNoise
    )),
#("waveScaletexture", PointerProperty(
#        name="Wave Scale Texture",
#        description="Determines the amplitude of the waves. This value is always set in centimeter unit, regardless of what the scene scale is set to",
#        type=bpy.types.Image,
#        update=updateWaveScaletexture
#    )),
("waveScaletexture", StringProperty(
        name="Wave Scale Texture",
        description="Determines the amplitude of the waves. This value is always set in centimeter unit, regardless of what the scene scale is set to",
        default='',
        update=updateWaveScaletexture
    )),
('waveScaleTextureChan', EnumProperty(
        name="Wave Scale Texture Channel",
        description="Defines the channel used to control the wave scale",
        items=(
            ('0', "R", ""),
            ('1', "G", ""),
            ('2', "B", ""),
            ('3', "A", "")
        ),
        default='0',
        update=updateWaveScaleTextureChan
    )),
('waveScale', FloatProperty(
        name="Wave Scale",
        description="Determines the amplitude of the waves. This value is always set in centimeter unit, regardless of what the scene scale is set to",
        default=0,
        min=0,
        max=5,
        update=updateWaveScale
    )),
('waveScaleNoise', FloatProperty(
        name="Wave Scale Noise",
        description="The strength of noise that is applied to the scale of each individual hair",
        default=0.5,
        min=0,
        max=1,
        update=updateWaveScaleNoise
    )),
('waveScaleStrand', FloatProperty(
        name="Wave Scale Strand",
        description="The strength of the waviness of individual strands. This value is multiplied against the waviness scale",
        default=1,
        min=0,
        max=1,
        update=updateWaveScaleStrand
    )),
('waveScaleClump', FloatProperty(
        name="Wave Scale Clump",
        description="The strength of the waviness of clumped strands. This value is multiplied against the waviness scale",
        default=0,
        min=0,
        max=1,
        update=updateWaveScaleClump
    )),
#("waveFreqTexture", PointerProperty(
#        name="Wave Frequency Texture",
#        description="Determines the number of waves generated down the length of each individual strand",
#        type=bpy.types.Image,
#        update=updateWaveFreqTexture
#    )),
("waveFreqTexture", StringProperty(
        name="Wave Frequency Texture",
        description="Determines the number of waves generated down the length of each individual strand",
        default='',
        update=updateWaveFreqTexture
    )),
('waveFreqTextureChan', EnumProperty(
        name="Wave Frequency Texture Channel",
        description="Defines the channel used to control the wave frequency",
        items=(
            ('0', "R", ""),
            ('1', "G", ""),
            ('2', "B", ""),
            ('3', "A", "")
        ),
        default='0',
        update=updateWaveFreqTextureChan
    )),
('waveFreq', FloatProperty(
        name="Wave Frequency",
        description="Determines the number of waves generated down the length of each individual strand",
        default=3,
        min=1,
        max=10,
        update=updateWaveFreq
    )),
('waveFreqNoise', FloatProperty(
        name="Wave Frequency Noise",
        description="The strength of noise that is applied to the frequency of each individual hair",
        default=0.5,
        min=0,
        max=1,
        update=updateWaveFreqNoise
    )),
('waveRootStraighten', FloatProperty(
        name="Wave Root Straighten",
        description="Determines how much of the root of each individual hair should remain without waves. A value of 0 has no effect. A value of 1.0 makes waves linearly scale up toward the tip, where tip would get the full wave scale, while root will have no waves",
        default=0,
        min=0,
        max=1,
        update=updateWaveRootStraighten
    )),
("baseColor", FloatVectorProperty(
        name="Base Color",
        description="Determines the base color of the hair",
        subtype = 'COLOR',
        default=(0,0,0,0),
        size = 4,
        min = 0,
        max = 1,
        update = updateBaseColor
    )),
('alpha', FloatProperty(
        name="Alpha",
        description="Determines the transparency of the hair??",
        default=0,
        min=0,
        max=1,
        update=updateAlpha
    )),
#("rootColorTexture", PointerProperty(
#        name="Root Color Texture",
#        description="The color that is used for the roots of strands. This is determined by loading a texture input and is sampled per hair",
#        type=bpy.types.Image,
#        update=updateRootColorTexture
#    )),
("rootColorTexture", StringProperty(
        name="Root Color Texture",
        description="The color that is used for the roots of strands. This is determined by loading a texture input and is sampled per hair",
        default='',
        update=updateRootColorTexture
    )),
("rootColor", FloatVectorProperty(
        name="Root Color",
        description="The color that is used for the roots of strands. This is determined by loading a texture input and is sampled per hair",
        subtype = 'COLOR',
        default=(1,1,1,1),
        size = 4,
        min = 0,
        max = 1,
        update = updateRootColor
    )),
#("tipColorTexture", PointerProperty(
#        name="Tip Color Texture",
#        description="The color that is used for the tips of strands. This is determined by loading a texture input and is sampled per hair",
#        type=bpy.types.Image,
#        update=updateTipColorTexture
#    )),
("tipColorTexture", StringProperty(
        name="Tip Color Texture",
        description="The color that is used for the tips of strands. This is determined by loading a texture input and is sampled per hair",
        default='',
        update=updateTipColorTexture
    )),
("tipColor", FloatVectorProperty(
        name="Tip Color",
        description="The color that is used for the tips of strands. This is determined by loading a texture input and is sampled per hair",
        subtype = 'COLOR',
        default=(1,1,1,1),
        size = 4,
        min = 0,
        max = 1,
        update = updateTipColor
    )),
('rootTipColorWeight', FloatProperty(
        name="Root Tip Color Weight",
        description="Balances how much of the Root and Tip color is used along the length strands",
        default=0.5,
        min=0,
        max=1,
        update=updateRootTipColorWeight
    )),
('rootTipColorFalloff', FloatProperty(
        name="Root Tip Color Falloff",
        description="The blend between the root color and tip color. The Root/Tip Color Weight position is the center of the falloff",
        default=0,
        min=0,
        max=1,
        update=updateRootTipColorFalloff
    )),
('rootAlphaFalloff', FloatProperty(
        name="Root Alpha Falloff",
        description="Controls the transparency of the root of a strand up to a portion of the strand, but not to the tip",
        default=0,
        min=0,
        max=1,
        update=updateRootAlphaFalloff
    )),
#("strandTexture", PointerProperty(
#        name="Strand Texture",
#        description="This is a texture that goes along the length of a strand, from root to tip",
#        type=bpy.types.Image,
#        update=updateStrandTexture
#    )),
("strandTexture", StringProperty(
        name="Strand Texture",
        description="This is a texture that goes along the length of a strand, from root to tip",
        default='',
        update=updateStrandTexture
    )),
('strandBlendMode', EnumProperty(
        name="Strand Blend Mode",
        description="How the Strand Texture blends with the base root/tip colors. Modes include Overwrite, Multiply, Add, and Modulate",
        items=(
            ('0', "Overwrite", ""),
            ('1', "Multiply", ""),
            ('2', "Add", ""),
            ('3', "Modulate", "")
        ),
        default='0',
        update=updateStrandBlendMode
    )),
('strandBlendScale', FloatProperty(
        name="Strand Blend Scale",
        description="The strength of the blend. At 0, it is off. At 1.0 the blend is full strength",
        default=1,
        min=0,
        max=1,
        update=updateStrandBlendScale
    )),
('textureBrightness', FloatProperty(
        name="Texture Brightness",
        description="Controls the strand texture brightness",
        default=0,
        update=updateTextureBrightness
    )),
("diffuseColor", FloatVectorProperty(
        name="Diffuse Color",
        description="Defines the diffuse color",
        subtype = 'COLOR',
        default=(0,0,0,0),
        size = 4,
        min = 0,
        max = 1,
        update = updateDiffuseColor
    )),
('diffuseBlend', FloatProperty(
        name="Diffuse Blend",
        description="The diffuse blend attempts to match the rendered shading from the hair with the mesh surface’s shading. By setting this value to 1.0, users can ignore hair diffuse term and match mesh lighting more closely. A value of 0.0 will force hair lighting only",
        default=0.5,
        min=0,
        max=1,
        update=updateDiffuseBlend
    )),
('diffuseScale', FloatProperty(
        name="Diffuse Scale",
        description="Controls the scale of the diffuse blending",
        default=0,
        min=0,
        max=1,
        update=updateDiffuseScale
    )),
('diffuseHairNormalWeight', FloatProperty(
        name="Diffuse Hair Normal Weight",
        description="The strength of the normal derived from the hair normal bone to calculate shading weighted against the diffuse blend. Typically used for long hair",
        default=0,
        min=0,
        max=1,
        update=updateDiffuseHairNormalWeight
    )),
('diffuseBoneIndex', EnumProperty(
        name="Diffuse Bone Index",
        description="Selector to pick a bone that is appropriate for the Hair Normal Weight",
        items=getBonesIndices,
        update = updateDiffuseBoneIndex
    )),
("diffuseBoneLocalPos", FloatVectorProperty(
        name="Diffuse Bone Local Position",
        description="Defines the position used for the Hair Normal Weight, relative to the selected bone",
        subtype = 'COORDINATES',
        default=(0,0,0),
        update = updateDiffuseBoneLocalPos
    )),
('diffuseNoiseScale', FloatProperty(
        name="Diffuse Noise Scale",
        description="Contols the scale of the noise used for diffuse computation",
        default=0,
        update=updateDiffuseNoiseScale
    )),
('diffuseNoiseGain', FloatProperty(
        name="Diffuse Noise Gain",
        description="Contols the gain of the noise used for diffuse computation",
        default=0,
        update=updateDiffuseNoiseGain
    )),
('diffuseNoiseFreqU', FloatProperty(
        name="Diffuse Noise Frequency U",
        description="Contols the frequency of the noise used for diffuse computation along the X axis of the UV space",
        default=0,
        update=updateDiffuseNoiseFreqU
    )),
('diffuseNoiseFreqV', FloatProperty(
        name="Diffuse Noise Frequency V",
        description="Contols the frequency of the noise used for diffuse computation along the Y axis of the UV space",
        default=0,
        update=updateDiffuseNoiseFreqV
    )),
#("specularTexture", PointerProperty(
#        name="Specular Texture",
#        description="The color that is applied to both primary and secondary specular",
#        type=bpy.types.Image,
#        update=updateSpecularTexture
#    )),
("specularTexture", StringProperty(
        name="Specular Texture",
        description="The color that is applied to both primary and secondary specular",
        default='',
        update=updateSpecularTexture
    )),
("specularColor", FloatVectorProperty(
        name="Specular Color",
        description="The color that is applied to both primary and secondary specular",
        subtype = 'COLOR',
        default=(1,1,1,1),
        size = 4,
        min = 0,
        max = 1,
        update = updateSpecularColor
    )),
('specularNoiseScale', FloatProperty(
        name="Specular Noise Scale",
        description="Contols the scale of the noise used for specular computation",
        default=0,
        update=updateSpecularNoiseScale
    )),
('specularEnvScale', FloatProperty(
        name="Specular Environment Scale",
        description="Contols the scale of the environment's influence on specular highlights",
        default=0,
        update=updateSpecularEnvScale
    )),
('specularPrimary', FloatProperty(
        name="Specular Primary Scale",
        description="The strength that the primary specular is applied",
        default=0.1,
        min=0,
        max=1,
        update=updateSpecularPrimary
    )),
('specularPowerPrimary', FloatProperty(
        name="Specular Primary Shininess",
        description="How loose or tight the falloff is for primary specular",
        default=100,
        min=1,
        max=1000,
        update=updateSpecularPowerPrimary
    )),
('specularPrimaryBreakup', FloatProperty(
        name="Specular Primary Breakup",
        description="How wide specular highlight varies based on noise",
        default=0,
        min=0,
        max=1,
        update=updateSpecularPrimaryBreakup
    )),
('specularSecondary', FloatProperty(
        name="Specular Secondary Scale",
        description="The strength that the secondary specular is applied",
        default=0.05,
        min=0,
        max=1,
        update=updateSpecularSecondary
    )),
('specularPowerSecondary', FloatProperty(
        name="Specular Secondary Shininess",
        description="How loose or tight the falloff is for secondary specular",
        default=20,
        min=1,
        max=1000,
        update=updateSpecularPowerSecondary
    )),
('specularSecondaryOffset', FloatProperty(
        name="Specular Secondary Offset",
        description="Offsets the secondary specular term from the primary specular creating separation and two distinct highlight regions. This is part of what makes hair look like hair",
        default=0.1,
        min=-1,
        max=1,
        update=updateSpecularSecondaryOffset
    )),
('glintStrength', FloatProperty(
        name="Glint Strength",
        description="The amount of the glint that is blended back into the hair",
        default=0,
        min=0,
        max=1,
        update=updateGlintStrength
    )),
('glintCount', FloatProperty(
        name="Glint Count",
        description="Determines how much noise is present in the glint",
        default=256,
        min=1,
        max=1024,
        update=updateGlintCount
    )),
('glintExponent', FloatProperty(
        name="Glint Exponent",
        description="The strength of contrast applied to glint",
        default=2,
        min=1,
        max=16,
        update=updateGlintExponent
    )),
('useShadows', BoolProperty(
        name="Use Shadows",
        description="Enable/Disable the use of shadows",
        default=False,
        update=updateUseShadows
    )),
('castShadows', BoolProperty(
        name="Cast Shadows",
        description="Enables hair to cast shadows",
        default=True,
        update=updateCastShadows
    )),
('receiveShadows', BoolProperty(
        name="Receive Shadows",
        description="Enables hair to receive shadows",
        default=True,
        update=updateReceiveShadows
    )),
('shadowSigma', FloatProperty(
        name="Shadow Attenuation",
        description="The strength that shadows are applied to hair",
        default=0.2,
        min=0,
        max=2,
        update=updateShadowSigma
    )),
('shadowDensityScale', FloatProperty(
        name="Shadow Density Scale",
        description="For shadow rendering, we can use less, but thicker hairs for performance. This value is used as multiplier on top of density value. Lower values make hair shadow rougher, but make rendering faster. A value of 0.5 is typically a reasonable choice",
        default=0.5,
        min=0,
        max=1,
        update=updateShadowDensityScale
    )),
('useViewfrustrumCulling', BoolProperty(
        name="Use View frustrum Culling",
        description="Culls hairs when they are off screen",
        default=True,
        update=updateUseViewfrustrumCulling
    )),
('useBackfaceCulling', BoolProperty(
        name="Use Backface Culling",
        description="Enables the hairs to be culled when their associated face is pointing away from the camera. This is based on the Backface Culling Threshold",
        default=False,
        update=updateUseBackfaceCulling
    )),
('backfaceCullingThreshold', FloatProperty(
        name="Backface Culling Threshold",
        description="Threshold that determines the strands that are culled via Backface Culling",
        default=-0.2,
        min=-1,
        max=1,
        update=updateBackfaceCullingThreshold
    )),
('enableDistanceLOD', BoolProperty(
        name="Enable Distance LOD",
        description="Allows the user to use or not use Continuous Distance LOD",
        default=True,
        update=updateEnableDistanceLOD
    )),
('distanceLODStart', FloatProperty(
        name="Distance LOD Start",
        description="The distance from the camera where Continuous Distance LOD begins",
        default=5,
        min=0,
        max=1000,
        update=updateDistanceLODStart
    )),
('distanceLODEnd', FloatProperty(
        name="Distance LOD End",
        description="The distance from the camera where Continuous Distance LOD ends. At this point no hair is drawn",
        default=10,
        min=0,
        max=1000,
        update=updateDistanceLODEnd
    )),
('distanceLODFadeStart', FloatProperty(
        name="Distance LOD Fade Start",
        description="The distance from the camera where Continuous Distance LOD starts to become transparent",
        default=1000,
        min=0,
        max=1000,
        update=updateDistanceLODFadeStart
    )),
('distanceLODWidth', FloatProperty(
        name="Distance LOD Width Scale",
        description="When Continuous LOD reaches its end distance, the Base Width of the strands interpolates to this value. Typically, this is a larger value than what Base Width is set to in the Physical Material, resulting in larger strands when the camera is further away and density becomes lower",
        default=1,
        min=0,
        max=10,
        update=updateDistanceLODWidth
    )),
('distanceLODDensity', FloatProperty(
        name="Distance LOD Density Scale",
        description="When Continuous LOD reaches its end distance, the overall Density interpolates to this value. Typically this value is 0, therefore removing all strands when the camera is at far LOD",
        default=0,
        min=0,
        max=10,
        update=updateDistanceLODDensity
    )),
('enableDetailLOD', BoolProperty(
        name="Enable Detail LOD",
        description="Allows the user to use or not use Continuous Detail LOD",
        default=True,
        update=updateEnableDetailLOD
    )),
('detailLODStart', FloatProperty(
        name="Detail LOD Start",
        description="The distance from the camera where Continuous Detail LOD begins. for Detail LOD, this distance is further from the camera",
        default=2,
        min=0,
        max=1000,
        update=updateDetailLODStart
    )),
('detailLODEnd', FloatProperty(
        name="Detail LOD End",
        description="The distance from the camera where Continuous Detail LOD ends. For Detail LOD, this is closest to the camera and results fur at its highest density",
        default=1,
        min=0,
        max=1000,
        update=updateDetailLODEnd
    )),
('detailLODWidth', FloatProperty(
        name="Detail LOD Width Scale",
        description="When Detail LOD reaches its end distance, the Base Width of the strands interpolates to this value. Typically this is a smaller value than what Base Width is set to in the Physical Material, resulting in finer strands when the camera is closer",
        default=1,
        min=0,
        max=10,
        update=updateDetailLODWidth
    )),
('detailLODDensity', FloatProperty(
        name="Detail LOD Density Scale",
        description="When Detail LOD reaches its end distance, the over all Density interpolates to this value. Typically this value is greater than one, there fore creating more fur when the camera is closer",
        default=1,
        min=0,
        max=10,
        update=updateDetailLODDensity
    ))
]

CLASSES_HairMaterial_Panel = [PhysXHairMaterialPanel, PhysXHairVisualizationPanel, PhysXHairPhysicsPanel, PhysXHairGraphicsPanel, PhysXHairLODPanel]