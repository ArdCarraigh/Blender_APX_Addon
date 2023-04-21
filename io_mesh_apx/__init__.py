# -*- coding: utf-8 -*-
# __init__.py

bl_info = {
    "name": "APX Importer/Exporter (.apx)",
    "author": "Ard Carraigh & Aaron Thompson",
    "version": (3, 0),
    "blender": (3, 5, 0),
    "location": "File > Import-Export",
    "description": "Import and export .apx meshes",
    "doc_url": "https://github.com/ArdCarraigh/Blender_APX_Addon",
    "tracker_url": "https://github.com/ArdCarraigh/Blender_APX_Addon/issues",
    "support": "COMMUNITY",
    "category": "Import-Export",
}

import bpy
from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy_extras.object_utils import AddObjectHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatProperty, FloatVectorProperty, IntProperty
from bpy.types import Operator
from io_mesh_apx.importer.import_clothing import read_clothing
from io_mesh_apx.importer.import_hairworks import read_hairworks
from io_mesh_apx.exporter.export_hairworks import write_hairworks
from io_mesh_apx.exporter.export_clothing import write_clothing
from io_mesh_apx.tools.collision_tools import *
from io_mesh_apx.tools.hair_tools import *
from io_mesh_apx.tools.paint_tools import apply_drive, cleanUpDriveLatchGroups, add_drive_latch_group 
from io_mesh_apx.tools.setup_tools import *


def read_apx(context, filepath, rotate_180, rm_ph_me):
    print("running read_apx...")
    
    # Should work from all modes
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
    bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
    with open(filepath, 'r', encoding='utf-8') as file:

        # Get the type of .apx we have
        for line in file:
            if 'className=' in line:
                if 'ClothingAssetParameters' in line:
                    type = 'cloth'
                if 'HairWorksInfo' in line:
                    type = 'hair'
                break

    # If PhysX Clothing type
    if type == 'cloth':
        read_clothing(context, filepath, rotate_180, rm_ph_me)

    # If Hairworks type
    if type == 'hair':
        read_hairworks(context, filepath, rotate_180)

    # Unselect everything
    bpy.context.view_layer.objects.active = None
    bpy.ops.object.select_all(False)

    return {'FINISHED'}

class ImportApx(Operator, ImportHelper):
    """Load a APX file"""
    bl_idname = "import.apx"  # important since its how bpy.ops.import.apx is constructed
    bl_label = "Import APX"

    # ImportHelper mixin class uses this
    filename_ext = ".apx"

    filter_glob: StringProperty(
        default="*.apx",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    
    rotate_180: BoolProperty(
        name="Rotate 180°",
        description="Rotate both the mesh and the armature on the Z-axis by 180°",
        default=True
    )
    
    rm_ph_me: BoolProperty(
        name="Remove Physical Meshes",
        description="Remove the physical meshes after transfer of vertex colors to graphical meshes",
        default=True
    )

    def draw(self, context):
        layout = self.layout
        
        sections = ["General", "Clothing"]
        
        section_options = {
            "General" : ["rotate_180"], 
            "Clothing" : ["rm_ph_me"], 
        }
        
        section_icons = {
            "General" : "WORLD", "Clothing" : "MATCLOTH"
        }
        
        for section in sections:
            row = layout.row()
            box = row.box()
            box.label(text=section, icon=section_icons[section])
            for prop in section_options[section]:
                box.prop(self, prop)
                
    def execute(self, context):
        return read_apx(context, self.filepath, self.rotate_180, self.rm_ph_me)


def write_apx(context, filepath, type, resample_value, spline, maximumMaxDistance):
    print("running read_apx...")
    
    # Should work from all modes
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
    bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
    
    if type == 'Hairworks':
        write_hairworks(context, filepath, resample_value, spline)
        
    if type == 'Clothing':
        write_clothing(context, filepath, maximumMaxDistance)
    
    return {'FINISHED'}

class ExportApx(Operator, ExportHelper):
    """Write a APX file"""
    bl_idname = "export.apx"  # important since its how bpy.ops.export.apx is constructed
    bl_label = "Export APX"

    # ExportHelper mixin class uses this
    filename_ext = ".apx"

    filter_glob: StringProperty(
        default="*.apx",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.

    type: EnumProperty(
        name="APX Type",
        description="Choose between Clothing and Hairworks",
        items=(
            ('Hairworks', "Hairworks", "Write a hairworks .apx"),
            ('Clothing', "Clothing", "Write a clothing .apx"),
        ),
        default='Hairworks',
    )
    
    resample_value: IntProperty(
        name = "Resample",
        default = 4,
        description = "Set the number of vertices used to resample. Root and tip vertices are included",
        max = 99,
        min = 2,
    )
    
    spline: IntProperty(
        name = "Spline Multiplier",
        default = 4,
        description = "Set the spline multiplier of the hairworks asset",
        max = 4,
        min = 1,
    )
    
    maximumMaxDistance: FloatProperty(
        name = "Maximum Max Distance",
        default = 1,
        description = "Set the maximum max distance used by the clothing physical meshes",
        min = 0.000001,
    )

    def draw(self, context):
        layout = self.layout

        sections = ["General", "Hairworks", "Clothing"]

        section_options = {
            "General": ["type"],
            "Hairworks": ["resample_value", "spline"],
            "Clothing": ["maximumMaxDistance"]
        }

        section_icons = {
            "General": "WORLD", "Hairworks": "CURVE_DATA", "Clothing": "MATCLOTH"
        }

        row = layout.row()
        box = row.box()
        box.label(text="General", icon=section_icons["General"])
        box.prop(self, section_options["General"][0])
        
        row = layout.row()
        box = row.box()
        box.label(text=self.type, icon=section_icons[self.type])
        for prop in section_options[self.type]:
            box.prop(self, prop)

    def execute(self, context):
        return write_apx(context, self.filepath, self.type, self.resample_value, self.spline, self.maximumMaxDistance)
    
class AddCollisionCapsule(Operator):
    """Create a new Collision Capsule"""
    bl_idname = "physx.add_collision_capsule"
    bl_label = "Add Collision Capsule"
    bl_options = {'REGISTER', 'UNDO'}

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

    def execute(self, context):
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
        add_capsule(context, self.radius, self.height, self.location, self.rotation, self.use_location)
        return {'FINISHED'}
      
class AddCollisionSphere(Operator):
    """Create a new Collision Sphere"""
    bl_idname = "physx.add_collision_sphere"
    bl_label = "Add Collision Sphere"
    bl_options = {'REGISTER', 'UNDO'}

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

    def execute(self, context):
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
        add_sphere(context, self.radius, self.location, self.use_location)
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
        add_connection(context)
        return {'FINISHED'}
    
class AddPinSphere(Operator):
    """Create a new Pin Sphere"""
    bl_idname = "physx.add_pin_sphere"
    bl_label = "Add Pin Sphere"
    bl_options = {'REGISTER', 'UNDO'}

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

    def execute(self, context):
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
        add_pin(context, self.radius, self.location, self.use_location)
        return {'FINISHED'}
    
class ShapeHairInterp(Operator):
    """Shape Hair from Curves"""
    bl_idname = "physx.shape_hair_interp"
    bl_label = "Shape Hair from Curves."
    bl_options = {'REGISTER', 'UNDO'}
    
    steps: IntProperty(
        name="Interpolation Steps",
        default = 0,
        min = 0,
        description="Number of steps taken around each vertex for interpolation. Interpolation occurs when superior to 0"
    )
    threshold: FloatProperty(
        name="Proximity Threshold",
        default = 0.001,
        min = 0,
        description="Proximity threshold over which interpolation occurs"
    )
    hair_key: IntProperty(
        name="Hair Key",
        default = 0,
        min = 0,
        description="Index of the vertex along the curve used to compute proximity"
    )

    def execute(self, context):
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
        shape_hair_interp(context, self.steps, self.threshold, self.hair_key)
        return {'FINISHED'}
    
class CreateCurve(Operator):
    """Create Curves from Hair"""
    bl_idname = "physx.create_curve"
    bl_label = "Create Curves from Hair"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
        create_curve(context)
        return {'FINISHED'}
    
class HaircardCurve(Operator):
    """Create Curves from Haircard Mesh"""
    bl_idname = "physx.haircard_curve"
    bl_label = "Create Curves from Haircard Mesh"
    bl_options = {'REGISTER', 'UNDO'}
    
    uv_orientation: EnumProperty(
        name="UV Orientation",
        description="Inform the orientation of your hair cards on the UV map",
        items=(
            ('-Y', "-Y", "From top to bottom"),
            ('Y', "Y", "From bottom to top"),
            ('X', "X", "From left to right"),
            ('-X', "-X", "From right to left")
        ),
        default='-Y',
    )
    
    tolerance: FloatProperty(
        name="Tolerance threshold",
        default = 0.05,
        min = 0,
        description="Tolerance threshold of UV coordinates difference used to assess which vertices to gather"
    )

    def execute(self, context):
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
        haircard_curve(context, self.uv_orientation, self.tolerance)
        return {'FINISHED'}
    
def getDriveLatchGroups(scene, context):
    items=[]
    n_groups = cleanUpDriveLatchGroups(bpy.context.active_object)
    for i in range(n_groups):
        items.append((str(i+1), "Group "+str(i+1), "Choose the group "+str(i+1)+" for applying drive/latch paint"))
    return items
    
class ApplyDrive(Operator):
    """Apply Drive Paint to Latch Paint"""
    bl_idname = "physx.apply_drive"
    bl_label = "Apply Drive Paint to Latch Paint"
    bl_options = {'REGISTER', 'UNDO'}
    
    group: EnumProperty(
        name="Drive/Latch Group",
        items = getDriveLatchGroups
    )

    invert: BoolProperty(
        name="Invert",
        default = False,
        description="Apply Latch Paint to Drive Paint instead"
    )
    
    def execute(self, context):
        prev_mode = bpy.context.mode
        if prev_mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
        apply_drive(context, self.group, self.invert)
        if prev_mode == "PAINT_VERTEX":
            bpy.ops.object.mode_set(mode="VERTEX_PAINT")
        return {'FINISHED'}
    
class AddDrive(Operator):
    """Add a Drive/Latch Group"""
    bl_idname = "physx.add_drive_latch_group"
    bl_label = "Add a Drive/Latch Group"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        prev_mode = bpy.context.mode
        if prev_mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
        add_drive_latch_group(context)
        if prev_mode == "PAINT_VERTEX":
            bpy.ops.object.mode_set(mode="VERTEX_PAINT")
        return {'FINISHED'}
    
class SetupHairworks(Operator):
    """Set Up a Hairworks Asset"""
    bl_idname = "physx.setup_hairworks"
    bl_label = "Set Up a Hairworks Asset"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
        setup_hairworks(context)
        return {'FINISHED'}
    
class SetupClothing(Operator):
    """Set Up a Clothing Asset"""
    bl_idname = "physx.setup_clothing"
    bl_label = "Set Up a Clothing Asset"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
        setup_clothing(context)
        return {'FINISHED'}
    
class ConvertCapsuleToSphere(Operator):
    """Convert Collision Capsules to Collision Spheres and Connections"""
    bl_idname = "physx.convert_collision_capsule"
    bl_label = "Convert Collision Capsules to Collision Spheres and Connections"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
        convert_capsule(context)
        return {'FINISHED'}
    
class PhysXSetupSubMenu(bpy.types.Menu):
    bl_label = "Set Up"
    bl_idname = "VIEW3D_MT_object_PhysX_menu_Setup"
    
    def draw(self, context):
        layout = self.layout
        
        layout.operator(SetupClothing.bl_idname, text = "Set Up a Clothing Asset", icon="MATCLOTH")
        layout.operator(SetupHairworks.bl_idname, text = "Set Up a Hairworks Asset", icon='CURVE_DATA')
        
class PhysXCollisionsSubMenu(bpy.types.Menu):
    bl_label = "Collisions"
    bl_idname = "VIEW3D_MT_object_PhysX_menu_Collisions"
    
    def draw(self, context):
        layout = self.layout
        
        layout.operator(AddCollisionCapsule.bl_idname, text = "Add Collision Capsule (Clothing)", icon='MESH_CAPSULE')
        layout.operator(ConvertCapsuleToSphere.bl_idname, text = "Convert Collision Capsules (Clothing)", icon='MESH_CAPSULE')
        layout.operator(AddCollisionSphere.bl_idname, text = "Add Collision Sphere", icon='MESH_UVSPHERE')
        layout.operator(AddSphereConnection.bl_idname, text = "Add Sphere Connection", icon='MESH_CAPSULE')

class PhysXToolsClothingSubMenu(bpy.types.Menu):
    bl_label = "Clothing Tools"
    bl_idname = "VIEW3D_MT_object_PhysX_menu_Tools_Clothing"
    
    def draw(self, context):
        layout = self.layout
        
        layout.operator(AddDrive.bl_idname, text = "Add a Drive/Latch Group", icon='MATCLOTH')
        layout.operator(ApplyDrive.bl_idname, text = "Apply to Drive Paint to Latch Paint", icon="MATCLOTH")
        
class PhysXToolsHairSubMenu(bpy.types.Menu):
    bl_label = "Hairworks Tools"
    bl_idname = "VIEW3D_MT_object_PhysX_menu_Tools_Hair"
    
    def draw(self, context):
        layout = self.layout
        
        layout.operator(ShapeHairInterp.bl_idname, text = "Shape Hair from Curves", icon='CURVE_DATA')
        layout.operator(CreateCurve.bl_idname, text = "Create Curves from Hair", icon='CURVE_DATA')
        layout.operator(HaircardCurve.bl_idname, text = "Create Curves from Haircard Mesh", icon='CURVE_DATA')
        layout.operator(AddPinSphere.bl_idname, text = "Add Pin Sphere", icon='MESH_UVSPHERE')

class PhysXToolsSubMenu(bpy.types.Menu):
    bl_label = "Tools"
    bl_idname = "VIEW3D_MT_object_PhysX_menu_Tools"
    
    def draw(self, context):
        layout = self.layout
        
        layout.menu(PhysXToolsClothingSubMenu.bl_idname)
        layout.separator()
        layout.menu(PhysXToolsHairSubMenu.bl_idname)
    
class PhysXMenu(bpy.types.Menu):
    bl_label = "PhysX"
    bl_idname = "VIEW3D_MT_object_PhysX_menu"

    def draw(self, context):
        layout = self.layout

        layout.menu(PhysXSetupSubMenu.bl_idname)
        layout.separator()
        layout.menu(PhysXCollisionsSubMenu.bl_idname)
        layout.separator()
        layout.menu(PhysXToolsSubMenu.bl_idname)
        
class PhysXToolsClothingSubMenuVertexPaint(bpy.types.Menu):
    bl_label = "Clothing Tools"
    bl_idname = "VIEW3D_MT_paint_vertex_PhysX_menu_Tools_Clothing"
    
    def draw(self, context):
        layout = self.layout
        
        layout.operator(AddDrive.bl_idname, text = "Add a Drive/Latch Group", icon='MATCLOTH')
        layout.operator(ApplyDrive.bl_idname, text = "Apply to Drive Paint to Latch Paint", icon="MATCLOTH")
        
class PhysXToolsSubMenuVertexPaint(bpy.types.Menu):
    bl_label = "Tools"
    bl_idname = "VIEW3D_MT_paint_vertex_PhysX_menu_Tools"
    
    def draw(self, context):
        layout = self.layout
        
        layout.menu(PhysXToolsClothingSubMenuVertexPaint.bl_idname)
        
class PhysXMenuVertexPaint(bpy.types.Menu):
    bl_label = "PhysX"
    bl_idname = "VIEW3D_MT_paint_vertex_PhysX_menu"

    def draw(self, context):
        layout = self.layout

        layout.menu(PhysXToolsSubMenuVertexPaint.bl_idname)
        
CLASSES = [ImportApx, ExportApx, AddCollisionCapsule, AddCollisionSphere, AddSphereConnection, AddPinSphere, ShapeHairInterp, CreateCurve, HaircardCurve, ApplyDrive, AddDrive, SetupHairworks, SetupClothing, ConvertCapsuleToSphere, PhysXMenu, PhysXSetupSubMenu, PhysXCollisionsSubMenu, PhysXToolsSubMenu, PhysXToolsClothingSubMenu, PhysXToolsHairSubMenu, PhysXToolsClothingSubMenuVertexPaint, PhysXToolsSubMenuVertexPaint, PhysXMenuVertexPaint]

# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(ImportApx.bl_idname, text="APX (.apx)")

def menu_func_export(self, context):
    self.layout.operator(ExportApx.bl_idname, text="APX (.apx)")
    
def draw_item(self, context):
    layout = self.layout
    layout.separator()
    layout.menu(PhysXMenu.bl_idname)
    
def draw_item_vertex_paint(self, context):
    layout = self.layout
    layout.separator()
    layout.menu(PhysXMenuVertexPaint.bl_idname)

def register():
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
    bpy.types.VIEW3D_MT_object.append(draw_item)
    bpy.types.VIEW3D_MT_paint_vertex.append(draw_item_vertex_paint)
    
    for klass in CLASSES:
        bpy.utils.register_class(klass)
        
def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    bpy.types.VIEW3D_MT_object.remove(draw_item)
    bpy.types.VIEW3D_MT_paint_vertex.remove(draw_item_vertex_paint)
    
    for klass in CLASSES:
        bpy.utils.unregister_class(klass)

if __name__ == "__main__":
    register()
    
    # test call
    bpy.ops.import_test.apx('INVOKE_DEFAULT')
