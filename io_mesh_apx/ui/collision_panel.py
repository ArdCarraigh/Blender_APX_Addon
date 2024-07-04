# -*- coding: utf-8 -*-
# ui/collision_panel.py

import bpy
import numpy as np
from copy import deepcopy
from mathutils import Vector
from bpy.props import FloatProperty, FloatVectorProperty, IntProperty, PointerProperty, BoolProperty, EnumProperty, StringProperty
from bpy.types import Operator
from io_mesh_apx.tools.collision_tools import add_sphere, remove_sphere, add_connection, remove_connection, add_capsule, remove_capsule, convert_capsule, generateRagdoll, mirrorRagdoll
from io_mesh_apx.utils import GetCollection, selectOnly, GetArmature, getRiggedObjects, getBones

class GenerateRagdoll(Operator):
    """Generate a Ragdoll !!!Keep in mind PhysX only supports 31 collision spheres!!!"""
    bl_idname = "physx.generate_ragdoll"
    bl_label = "Generate a Ragdoll !!!Keep in mind PhysX only supports 31 collision spheres!!!"
    bl_options = {'REGISTER', 'UNDO'}
    bl_property = "object"
    
    object: EnumProperty(
        options={'HIDDEN'},
        name="Object",
        items=getRiggedObjects
    )
    
    def execute(self, context):
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
        generateRagdoll(context, self.object)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        #context.window_manager.invoke_confirm(self, event)
        return {'RUNNING_MODAL'}
        
    
class MirrorRagdoll(Operator):
    """Mirror collision objects according to string pattern in bone names"""
    bl_idname = "physx.mirror_ragdoll"
    bl_label = "Mirror collision spheres and capsules according to string pattern in bone names"
    bl_options = {'REGISTER', 'UNDO'}
    
    pattern: StringProperty(
        name="Pattern to Replace",
        default=""
    )
    
    replacement: StringProperty(
        name="Replacement String",
        default=""
    )
    
    axis: EnumProperty(
        name="Axis for Mirroring",
        default="X",
        items=(
        ('X', "X", ""),
        ('Y', "Y", ""),
        ('Z', "Z", "")
        )
    )
    
    def execute(self, context):
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
        mirrorRagdoll(context, self.pattern, self.replacement, self.axis)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return bpy.context.window_manager.invoke_props_dialog(self)

class AddCollisionSphere(Operator):
    """Create a new Collision Sphere"""
    bl_idname = "physx.add_collision_sphere"
    bl_label = "Add Collision Sphere"
    bl_options = {'REGISTER', 'UNDO'}
    bl_property = "bone"
    
    radius: FloatProperty(
        name="Radius",
        default = 0.15,
        min = 0,
        description="Set the radius of the sphere",
    )
    location: FloatVectorProperty(
        name="Location",
        default=(0, 0, 0),
        description="Set the location of the sphere",
        subtype = 'COORDINATES'
    )
    use_location: BoolProperty(
        name="Use Location",
        default=False,
        description="Use custom location, or bone location"
    )
    bone: EnumProperty(
        options={'HIDDEN'},
        name="Bone",
        items=getBones
    )
    
    def execute(self, context):
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
        coll = GetCollection("Collision Spheres", make_active=False)
        add_sphere(context, self.bone, self.radius, self.location, self.use_location, coll is None)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'RUNNING_MODAL'}
    
class RemoveCollisionSphere(Operator):
    """Remove a Collision Sphere"""
    bl_idname = "physx.remove_collision_sphere"
    bl_label = "Remove Collision Sphere"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
        wm = bpy.context.window_manager.physx
        index = wm.PhysXCollisionSpheresIndex
        remove_sphere(context, index)
        if not index:
            wm.PhysXCollisionSpheresIndex = 0
        elif index > 0:
            wm.PhysXCollisionSpheresIndex = index - 1    
        return {'FINISHED'}
    
class AddSphereConnection(Operator):
    """Create a new Connection"""
    bl_idname = "physx.add_sphere_connection"
    bl_label = "Add Sphere Connection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
        coll = GetCollection("Collision Connections", make_active=False)
        wm = bpy.context.window_manager.physx
        add_connection(context, [wm.collisionSphere1, wm.collisionSphere2], coll is None)
        wm.collisionSphere1 = None
        wm.collisionSphere2 = None
        return {'FINISHED'}
    
class AddSphereConnectionKey(Operator):
    """Create a new Connection"""
    bl_idname = "physx.add_sphere_connection_key"
    bl_label = "Add Sphere Connection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
        sphere_coll = GetCollection("Collision Spheres", make_active=False)
        objs = bpy.context.selected_objects
        assert(len(objs) == 2)
        assert(all([obj.name in sphere_coll.objects for obj in objs]))
        add_connection(context, objs)
        return {'FINISHED'}
    
class RemoveCollisionSphereConnection(Operator):
    """Remove a Collision Sphere Connection"""
    bl_idname = "physx.remove_collision_sphere_connection"
    bl_label = "Remove Collision Sphere Connection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
        wm = bpy.context.window_manager.physx
        index = wm.PhysXCollisionSpheresConnectionsIndex
        remove_connection(context, index)
        if not index:
            wm.PhysXCollisionSpheresConnectionsIndex = 0
        elif index > 0:
            wm.PhysXCollisionSpheresConnectionsIndex = index - 1    
        return {'FINISHED'}
    
class AddCollisionCapsule(Operator):
    """Create a new Collision Capsule"""
    bl_idname = "physx.add_collision_capsule"
    bl_label = "Add Collision Capsule"
    bl_options = {'REGISTER', 'UNDO'}
    bl_property = "bone"

    radius: FloatProperty(
        name="Radius",
        default = 0.15,
        min = 0,
        description="Set the radius of the capsule",
    )
    height: FloatProperty(
        name="Height",
        default = 0.3,
        min = 0,
        description="Set the height of the capsule",
    )
    location: FloatVectorProperty(
        name="Location",
        default=(0, 0, 0),
        description="Set the location of the capsule",
        subtype = 'COORDINATES'
    )
    rotation: FloatVectorProperty(
        name="Rotation",
        default=(0, 0, 0),
        description="Set the rotation of the capsule",
        subtype = 'COORDINATES'
    )
    use_location: BoolProperty(
        name="Use Location",
        default=False,
        description="Use custom location, or bone location"
    )
    bone: EnumProperty(
        options={'HIDDEN'},
        name="Bone",
        items=getBones
    )

    def execute(self, context):
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
        coll = GetCollection("Collision Capsules", make_active=False)
        add_capsule(context, self.bone, self.radius, self.height, self.location, self.rotation, self.use_location, coll is None)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'RUNNING_MODAL'}
    
class RemoveCollisionCapsule(Operator):
    """Remove a Collision Capsule"""
    bl_idname = "physx.remove_collision_capsule"
    bl_label = "Remove Collision Capsule"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
        wm = bpy.context.window_manager.physx
        index = wm.PhysXCollisionCapsulesIndex
        remove_capsule(context, index)
        if not index:
            wm.PhysXCollisionCapsulesIndex = 0
        elif index > 0:
            wm.PhysXCollisionCapsulesIndex = index - 1    
        return {'FINISHED'}
    
class ConvertCapsuleToSphere(Operator):
    """Convert Collision Capsules to Collision Spheres and Connections !!!This will delete your capsule collection!!!"""
    bl_idname = "physx.convert_collision_capsule"
    bl_label = "Convert Collision Capsules to Collision Spheres and Connections !!!This will delete your capsule collection!!!"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
        convert_capsule(context)
        context.window_manager.physx.PhysXCollisionCapsulesIndex != -1
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return bpy.context.window_manager.invoke_confirm(self, event)
                                    
class PHYSX_UL_spheres(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        coll = data
        ob = item
            
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if ob:
                layout.prop(ob, "name", text="", emboss=False)
            else:
                layout.label(text="", translate=False)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="")
            
class PHYSX_UL_connections(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        coll = data
        ob = item
            
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if ob:
                layout.prop(ob, "name", text="", emboss=False)
            else:
                layout.label(text="", translate=False)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="")
        
class PHYSX_UL_capsules(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        coll = data
        ob = item
            
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if ob:
                layout.prop(ob, "name", text="", emboss=False)
            else:
                layout.label(text="", translate=False)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="")
                                        
class PhysXCollisionPanel(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_PhysX_collision_panel'
    bl_parent_id = 'VIEW3D_PT_PhysX_panel'
    bl_label = 'PhysX Collisions'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'PhysX'
    bl_options = {'HIDE_HEADER'}
    
    def draw(self, context):
        layout = self.layout
        wm = context.window_manager.physx
        if wm.PhysXSubPanel == 'collision':
            main_coll = GetCollection(make_active=False)
            if main_coll and main_coll["PhysXAssetType"] != "Destruction":
                
                sphere_coll = GetCollection("Collision Spheres", make_active=False)
                connection_coll = GetCollection("Collision Connections", make_active=False)
                capsule_coll = GetCollection("Collision Capsules", make_active=False)
                n_spheres = 0
                if sphere_coll:
                    n_spheres += len(sphere_coll.objects)
                if capsule_coll:
                    n_spheres += len(capsule_coll.objects)*2
                    
                row = layout.row()
                box = row.box()
                box.label(text="General", icon='SETTINGS')
                if n_spheres:
                    box_row = box.row()
                    box_row.prop(wm, "CollisionDisplayType", text = "Display As")
                box_row = box.row()
                box_row.operator(GenerateRagdoll.bl_idname, text = "Generate Ragdoll")
                if n_spheres:
                    box_row = box.row()
                    box_row.operator(MirrorRagdoll.bl_idname, text = "Mirror Ragdoll", icon = 'MOD_MIRROR')
                    
                row = layout.row()
                box = row.box()
                box.label(text="Collision Spheres", icon = 'MESH_UVSPHERE')
                if sphere_coll:
                    box.template_list("PHYSX_UL_spheres", "", sphere_coll, "objects", wm, "PhysXCollisionSpheresIndex", rows=3)
                    index_sphere = np.where(np.array(sphere_coll.objects) == bpy.context.active_object)[0]
                    if index_sphere.size:
                        if wm.PhysXCollisionSpheresIndex != index_sphere[0]:
                            wm.PhysXCollisionSpheresIndex = index_sphere[0]
                    else:
                        wm.PhysXCollisionSpheresIndex = -1
                    
                box_row = box.row()
                col = box_row.column()
                col.enabled = (n_spheres < 32 and main_coll["PhysXAssetType"] == "Clothing") or main_coll["PhysXAssetType"] == "Hairworks"
                col.operator(AddCollisionSphere.bl_idname, text="Add")
                col = box_row.column()
                col.enabled = wm.PhysXCollisionSpheresIndex != -1
                col.operator(RemoveCollisionSphere.bl_idname, text = "Remove")
                
                if sphere_coll and len(sphere_coll.objects) >= 2:
                    row = layout.row()
                    box = row.box()
                    box.label(text="Collision Connections", icon = 'MESH_CYLINDER')    
                    if connection_coll:
                        box.template_list("PHYSX_UL_connections", "", connection_coll, "objects", wm, "PhysXCollisionSpheresConnectionsIndex", rows=3)
                        index_connection = np.where(np.array(connection_coll.objects) == bpy.context.active_object)[0]
                        if index_connection.size:
                            if wm.PhysXCollisionSpheresConnectionsIndex != index_connection[0]:
                                wm.PhysXCollisionSpheresConnectionsIndex = index_connection[0]
                        else:
                            wm.PhysXCollisionSpheresConnectionsIndex = -1
                            
                    box_row = box.row(align=True)
                    box_row.prop(wm, "collisionSphere1", text = "From")
                    box_row.prop(wm, "collisionSphere2", text = "To")
                    box_row = box.row()
                    col = box_row.column()
                    col.enabled = wm.collisionSphere1 is not None and wm.collisionSphere2 is not None
                    col.operator(AddSphereConnection.bl_idname, text = "Add")
                    col = box_row.column()
                    col.enabled = wm.PhysXCollisionSpheresConnectionsIndex != -1
                    col.operator(RemoveCollisionSphereConnection.bl_idname, text = "Remove")
                    
                if main_coll["PhysXAssetType"] == "Clothing":
                    row = layout.row()
                    box = row.box()
                    box.label(text="Collision Capsules", icon = 'MESH_CAPSULE')
                    if capsule_coll:
                        box.template_list("PHYSX_UL_capsules", "", capsule_coll, "objects", wm, "PhysXCollisionCapsulesIndex", rows=3)
                        index_capsule = np.where(np.array(capsule_coll.objects) == bpy.context.active_object)[0]
                        if index_capsule.size:
                            if wm.PhysXCollisionCapsulesIndex != index_capsule[0]:
                                wm.PhysXCollisionCapsulesIndex = index_capsule[0]
                        else:
                            wm.PhysXCollisionCapsulesIndex = -1
                        
                    box_row = box.row()
                    col = box_row.column()
                    col.enabled = n_spheres < 31
                    col.operator(AddCollisionCapsule.bl_idname, text="Add")
                    col = box_row.column()
                    col.enabled = wm.PhysXCollisionCapsulesIndex != -1
                    col.operator(RemoveCollisionCapsule.bl_idname, text = "Remove")
                    
                    if capsule_coll:
                        if wm.PhysXCollisionCapsulesIndex != -1:
                            box_row = box.row()
                            box_row.prop(wm, "capsuleRadius", text = "Radius")
                            box_row = box.row()
                            box_row.prop(wm, "capsuleHeight", text = "Height")
                        
                        box_row = box.row()
                        box_row.operator(ConvertCapsuleToSphere.bl_idname, text = "Convert Capsules")

        return
    
def updateCollisionDisplayType(self, context):
    sphere_coll = GetCollection("Collision Spheres", make_active=False) 
    connection_coll = GetCollection("Collision Connections", make_active=False) 
    capsule_coll = GetCollection("Collision Capsules", make_active=False)
    
    objects = []
    if sphere_coll:
        objects.extend(sphere_coll.objects)
    if connection_coll:
        objects.extend(connection_coll.objects)
    if capsule_coll:
        objects.extend(capsule_coll.objects)
    
    for obj in objects:
        obj.display_type = self.CollisionDisplayType
            
def updatePhysXCollisionSpheresIndex(self, context):
    collision_coll = GetCollection("Collision Spheres", make_active=False)      
    if collision_coll:
        if collision_coll.objects and self.PhysXCollisionSpheresIndex != -1:
            selectOnly(collision_coll.objects[self.PhysXCollisionSpheresIndex])
            
def updatePhysXCollisionSpheresConnectionsIndex(self, context):
    collision_coll = GetCollection("Collision Connections", make_active=False)      
    if collision_coll:
        if collision_coll.objects and self.PhysXCollisionSpheresConnectionsIndex != -1:
            selectOnly(collision_coll.objects[self.PhysXCollisionSpheresConnectionsIndex])
            
def updatePhysXCollisionCapsulesIndex(self, context):
    collision_coll = GetCollection("Collision Capsules", make_active=False)      
    if collision_coll:
        if collision_coll.objects and self.PhysXCollisionCapsulesIndex != -1:
            selectOnly(collision_coll.objects[self.PhysXCollisionCapsulesIndex])
            
def pollCollisionSphere1(self, object):
    collision_coll = GetCollection("Collision Spheres", make_active=False)
    return collision_coll == object.users_collection[0] and object != self.collisionSphere2
        
def pollCollisionSphere2(self, object):
    collision_coll = GetCollection("Collision Spheres", make_active=False)    
    return collision_coll == object.users_collection[0] and object != self.collisionSphere1

def updateCapsuleRadius(self, context):
    arma = GetArmature()
    capsules = GetCollection("Collision Capsules", make_active=False).objects
    capsule = context.active_object
    capsuleBoneName = capsule.name[capsule.name.find("_")+1:capsule.name.rfind("_")]
    selectOnly(capsule)
    bpy.ops.mesh.separate(type='MATERIAL')
    spherePositions = []
    subCapsules = []
    for subCapsule in capsules:
        if capsule.name in subCapsule.name:
            subCapsules.append(subCapsule)
            if "Material_Sphere1" in subCapsule.data.materials or "Material_Sphere2" in subCapsule.data.materials:
                selectOnly(subCapsule)
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                subCapsule.scale = 1/np.array(arma.scale)
                subCapsule.rotation_euler = 2*(np.pi)-np.array(arma.rotation_euler)
                subCapsule.location = -np.array(arma.location)
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='MEDIAN')
                spherePositions.append(deepcopy(subCapsule.matrix_world.translation))
    for obj in subCapsules:
        bpy.data.objects.remove(obj)
    capsuleDir = spherePositions[0] - spherePositions[1]
    capsuleHeight = np.linalg.norm(capsuleDir)
    capsulePosition = np.mean(spherePositions, axis = 0)
    capsuleRotation = Vector((0,-capsuleHeight,0)).rotation_difference(capsuleDir).to_euler()
    add_capsule(context, capsuleBoneName, self.capsuleRadius, capsuleHeight, capsulePosition, capsuleRotation, True)

def updateCapsuleHeight(self, context):
    arma = GetArmature()
    capsules = GetCollection("Collision Capsules", make_active=False).objects
    capsule = context.active_object
    capsuleBoneName = capsule.name[capsule.name.find("_")+1:capsule.name.rfind("_")]
    selectOnly(capsule)
    bpy.ops.mesh.separate(type='MATERIAL')
    spherePositions = []
    subCapsules = []
    for subCapsule in capsules:
        if capsule.name in subCapsule.name:
            subCapsules.append(subCapsule)
            if "Material_Sphere1" in subCapsule.data.materials or "Material_Sphere2" in subCapsule.data.materials:
                selectOnly(subCapsule)
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                subCapsule.scale = 1/np.array(arma.scale)
                subCapsule.rotation_euler = 2*(np.pi)-np.array(arma.rotation_euler)
                subCapsule.location = -np.array(arma.location)
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='MEDIAN')
                Radius = np.linalg.norm(subCapsule.data.vertices[0].co)
                spherePositions.append(deepcopy(subCapsule.matrix_world.translation))
    for obj in subCapsules:
        bpy.data.objects.remove(obj)
    capsuleDir = spherePositions[0] - spherePositions[1]
    capsulePosition = np.mean(spherePositions, axis = 0)
    capsuleRotation = Vector((0,-self.capsuleHeight,0)).rotation_difference(capsuleDir).to_euler()
    add_capsule(context, capsuleBoneName, Radius, self.capsuleHeight, capsulePosition, capsuleRotation, True)
    
PROPS_Collision_Panel = [
("CollisionDisplayType", EnumProperty(
        name = "Set the Display Type for collision objects",
        default = 'WIRE',
        items = (
        ('WIRE', "WIRE", ""),
        ('SOLID', "SOLID", "")
        ),
        update = updateCollisionDisplayType
    )),
("PhysXCollisionSpheresIndex", IntProperty(
        name = "Index of the PhysX Collision Sphere",
        update = updatePhysXCollisionSpheresIndex,
        default = -1
    )),
("PhysXCollisionSpheresConnectionsIndex", IntProperty(
        name = "Index of the PhysX Collision Sphere Connection",
        update = updatePhysXCollisionSpheresConnectionsIndex,
        default = -1
    )),
("PhysXCollisionCapsulesIndex", IntProperty(
        name = "Index of the PhysX Collision Capsule",
        update = updatePhysXCollisionCapsulesIndex,
        default = -1
    )),
("collisionSphere1", PointerProperty(
        type=bpy.types.Object,
        poll = pollCollisionSphere1,
        name="Collision Sphere 1",
        description="Set the first collision sphere to connect"
    )),
("collisionSphere2", PointerProperty(
        type=bpy.types.Object,
        poll = pollCollisionSphere2,
        name="Collision Sphere 2",
        description="Set the second collision sphere to connect"
    )),
("capsuleRadius", FloatProperty(
        name = "Collision Capsule Radius",
        update = updateCapsuleRadius,
        min = 0.01
    )),
("capsuleHeight", FloatProperty(
        name = "Collision Capsule Height",
        update = updateCapsuleHeight,
        min = 0.01
    ))
]

CLASSES_Collision_Panel = [GenerateRagdoll, MirrorRagdoll, AddCollisionSphere, RemoveCollisionSphere, AddSphereConnection, AddSphereConnectionKey, RemoveCollisionSphereConnection, AddCollisionCapsule, RemoveCollisionCapsule, ConvertCapsuleToSphere, PHYSX_UL_spheres, PHYSX_UL_connections, PHYSX_UL_capsules, PhysXCollisionPanel]