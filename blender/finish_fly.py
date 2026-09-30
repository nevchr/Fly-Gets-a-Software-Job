"""Finish the handmade fly's rig and export a web-ready animated model.

Run with Blender 5.2 in background against a copy of the user's .blend file.
The source file is never saved by this script.
"""

import bpy
from math import pi, sin
from pathlib import Path
from mathutils import Quaternion, Vector


ROOT = Path(__file__).resolve().parents[1]
BLEND_OUT = ROOT / "fly-v1-rigged.blend"
GLB_OUT = ROOT / "frontend" / "public" / "models" / "fly-v1.glb"


def world_to_rig(rig, point):
    return rig.matrix_world.inverted() @ Vector(point)


def put_bone(rig, name, head, tail, parent=None):
    bone = rig.data.edit_bones.get(name) or rig.data.edit_bones.new(name)
    bone.head = world_to_rig(rig, head)
    bone.tail = world_to_rig(rig, tail)
    bone.use_connect = False
    bone.parent = rig.data.edit_bones.get(parent) if parent else None
    return bone


def mesh_islands(mesh):
    parent = list(range(len(mesh.vertices)))

    def find(index):
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    for edge in mesh.edges:
        a, b = map(find, edge.vertices)
        parent[a] = b
    groups = {}
    for index in range(len(mesh.vertices)):
        groups.setdefault(find(index), []).append(index)
    return list(groups.values())


def split_leg(obj):
    original = obj.data
    original_world = obj.matrix_world.copy()
    result = []
    for indices in mesh_islands(original):
        kept = set(indices)
        remap = {old: new for new, old in enumerate(indices)}
        vertices = [original.vertices[old].co[:] for old in indices]
        faces = [tuple(remap[index] for index in poly.vertices)
                 for poly in original.polygons if set(poly.vertices) <= kept]
        mesh = bpy.data.meshes.new(obj.name + ".segment")
        mesh.from_pydata(vertices, [], faces)
        mesh.update()
        for material in original.materials:
            mesh.materials.append(material)
        piece = bpy.data.objects.new(obj.name + ".segment", mesh)
        for collection in obj.users_collection:
            collection.objects.link(piece)
        piece.matrix_world = original_world
        world_vertices = [piece.matrix_world @ vertex.co for vertex in piece.data.vertices]
        by_height = sorted(world_vertices, key=lambda point: point.z, reverse=True)
        half = len(by_height) // 2
        top = sum(by_height[:half], Vector()) / half
        bottom = sum(by_height[half:], Vector()) / half
        result.append((piece, top, bottom))
    bpy.data.objects.remove(obj, do_unlink=True)
    result.sort(key=lambda item: item[1].z, reverse=True)
    return result


def bone_parent(rig, obj, bone_name):
    before = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices[:8]] if obj.type == "MESH" else []
    world = obj.matrix_world.copy()
    obj.parent = rig
    obj.parent_type = "BONE"
    obj.parent_bone = bone_name
    obj.matrix_world = world
    bpy.context.view_layer.update()
    after = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices[:8]] if obj.type == "MESH" else []
    if before:
        error = max((a - b).length for a, b in zip(before, after))
        if error > 0.0001:
            raise RuntimeError(f"Parenting displaced {obj.name}: {error:.5f} m")


def local_axis_rotation(rig, bone_name, axis, angle):
    rest = rig.data.bones[bone_name].matrix_local.to_quaternion()
    return rest.inverted() @ Quaternion(Vector(axis), angle) @ rest


def make_clip(rig, name, frames, length):
    rig.animation_data_create()
    rig.animation_data.action = None
    for pose in rig.pose.bones:
        pose.rotation_mode = "QUATERNION"
    for frame, settings in frames:
        bpy.context.scene.frame_set(frame)
        for pose in rig.pose.bones:
            pose.location = (0, 0, 0)
            pose.rotation_quaternion = (1, 0, 0, 0)
            pose.scale = (1, 1, 1)
        for bone_name, transform in settings.items():
            pose = rig.pose.bones[bone_name]
            if "location" in transform:
                pose.location = transform["location"]
            if "rotation" in transform:
                axis, angle = transform["rotation"]
                pose.rotation_quaternion = local_axis_rotation(rig, bone_name, axis, angle)
        for pose in rig.pose.bones:
            pose.keyframe_insert(data_path="location", frame=frame, group=pose.name)
            pose.keyframe_insert(data_path="rotation_quaternion", frame=frame, group=pose.name)
    action = rig.animation_data.action
    if action is None:
        raise RuntimeError(f"No action was created for {name}")
    action.name = name
    action.use_fake_user = True
    track = rig.animation_data.nla_tracks.new()
    track.name = name
    strip = track.strips.new(name, 1, action)
    strip.action_frame_start = 1
    strip.action_frame_end = length
    track.mute = name != "Idle"
    return action


rig = bpy.data.objects.get("Fly_Armature")
if rig is None or rig.type != "ARMATURE":
    raise RuntimeError("Expected the user's Fly_Armature")

if bpy.context.object and bpy.context.object.mode != "OBJECT":
    bpy.ops.object.mode_set(mode="OBJECT")

# Preserve the handmade silhouette while completing its unfinished materials.
head_material = bpy.data.materials.new("Fly_Head_Sage")
head_material.use_nodes = True
head_shader = head_material.node_tree.nodes.get("Principled BSDF")
head_shader.inputs["Base Color"].default_value = (0.57, 0.72, 0.24, 1)
head_shader.inputs["Roughness"].default_value = 0.72
head_material.diffuse_color = (0.57, 0.72, 0.24, 1)
head = bpy.data.objects["Fly_Head"]
head.data.materials.clear()
head.data.materials.append(head_material)

wing_material = bpy.data.materials.new("Fly_Wing_Ice")
wing_material.use_nodes = True
wing_shader = wing_material.node_tree.nodes.get("Principled BSDF")
wing_shader.inputs["Base Color"].default_value = (0.62, 0.88, 0.94, 1)
wing_shader.inputs["Alpha"].default_value = 0.53
wing_shader.inputs["Roughness"].default_value = 0.3
wing_material.diffuse_color = (0.62, 0.88, 0.94, 0.53)
wing_material.surface_render_method = "DITHERED"
for side in ("L", "R"):
    wing = bpy.data.objects[f"Fly_Wing.{side}"]
    wing.data.materials.clear()
    wing.data.materials.append(wing_material)

for material in bpy.data.materials:
    if material.use_nodes:
        shader = next((node for node in material.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
        if shader and material not in (wing_material, head_material):
            material.diffuse_color = shader.inputs["Base Color"].default_value[:]

# The original two experimental leg bones are preserved in fly-v1-working.blend.
# Replace them here with joints that line up with the actual handmade mesh pieces.
bpy.context.view_layer.objects.active = rig
rig.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
for name in ("Bone.001", "Bone"):
    existing = rig.data.edit_bones.get(name)
    if existing:
        rig.data.edit_bones.remove(existing)
put_bone(rig, "Root", (0, 0, -0.2), (0, 0, 0.2))
put_bone(rig, "Thorax", (0, 0, 0), (0, 1.2, 0.1), "Root")
put_bone(rig, "Head", (0, 1.75, -0.05), (0, 2.85, 0.05), "Thorax")
put_bone(rig, "Abdomen", (0, -0.82, -0.25), (0, -2.8, -0.3), "Thorax")
for side, sign in (("L", -1), ("R", 1)):
    put_bone(rig, f"Wing.{side}", (sign * 0.38, 0.1, 0.83),
             (sign * 1.35, -2.6, 0.84), "Thorax")
    put_bone(rig, f"Antenna.{side}", (sign * 0.25, 3.07, 0.47),
             (sign * 0.75, 3.28, 0.48), "Head")
bpy.ops.object.mode_set(mode="OBJECT")

leg_parts = {}
for position in ("Front", "Middle", "Rear"):
    for side in ("L", "R"):
        source = bpy.data.objects.get(f"Leg_{position}.{side}")
        if source is None:
            raise RuntimeError(f"Missing Leg_{position}.{side}")
        leg_parts[(position, side)] = split_leg(source)

bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode="EDIT")
for (position, side), parts in leg_parts.items():
    for index, (_, top, bottom) in enumerate(parts):
        label = ("Upper", "Middle", "Lower")[index]
        name = f"Leg{position}.{side}.{label}"
        parent = "Thorax" if index == 0 else f"Leg{position}.{side}.{'Upper' if index == 1 else 'Middle'}"
        put_bone(rig, name, top, bottom, parent)
bpy.ops.object.mode_set(mode="OBJECT")

for position, side in leg_parts:
    for index, (piece, _, _) in enumerate(leg_parts[(position, side)]):
        label = ("Upper", "Middle", "Lower")[index]
        piece.name = f"Leg_{position}.{side}.{label}"
        bone_parent(rig, piece, f"Leg{position}.{side}.{label}")

for name, bone in (
    ("Fly_Thorax", "Thorax"),
    ("Fly_Head", "Head"),
    ("Fly_Eye.L", "Head"),
    ("Fly_Eye.R", "Head"),
    ("Fly_Abdomen", "Abdomen"),
    ("Fly_Abdomen.Rings", "Abdomen"),
    ("Fly_Wing.L", "Wing.L"),
    ("Fly_Wing.R", "Wing.R"),
):
    bone_parent(rig, bpy.data.objects[name], bone)

for side in ("L", "R"):
    antenna = bpy.data.objects[f"Antenna.{side}"]
    bpy.ops.object.select_all(action="DESELECT")
    antenna.select_set(True)
    bpy.context.view_layer.objects.active = antenna
    bpy.ops.object.convert(target="MESH")
    antenna = bpy.context.object
    antenna.name = f"Antenna.{side}"
    bone_parent(rig, antenna, f"Antenna.{side}")

rig.display_type = "WIRE"
rig.show_in_front = False
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 24

wing_pair = {
    "Wing.L": {"rotation": ((0, 1, 0), -0.12)},
    "Wing.R": {"rotation": ((0, 1, 0), 0.12)},
}
make_clip(rig, "Idle", [
    (1, {}),
    (12, {"Root": {"location": (0, 0, 0.05)}, "Head": {"rotation": ((1, 0, 0), 0.035)}, **wing_pair}),
    (24, {}),
], 24)

make_clip(rig, "WingFlap", [
    (1, {"Wing.L": {"rotation": ((0, 1, 0), -0.22)}, "Wing.R": {"rotation": ((0, 1, 0), 0.22)}}),
    (3, {"Wing.L": {"rotation": ((0, 1, 0), 0.65)}, "Wing.R": {"rotation": ((0, 1, 0), -0.65)}}),
    (5, {"Wing.L": {"rotation": ((0, 1, 0), -0.22)}, "Wing.R": {"rotation": ((0, 1, 0), 0.22)}}),
], 5)

walk_frames = []
for frame in (1, 7, 13, 19, 24):
    phase = 2 * pi * (frame - 1) / 24
    settings = {"Root": {"location": (0, 0, 0.025 * (1 - abs(sin(phase))))}}
    for position in ("Front", "Middle", "Rear"):
        for side in ("L", "R"):
            tripod = 1 if (position, side) in (("Front", "L"), ("Middle", "R"), ("Rear", "L")) else -1
            swing = sin(phase) * tripod
            settings[f"Leg{position}.{side}.Upper"] = {"rotation": ((1, 0, 0), 0.23 * swing)}
            settings[f"Leg{position}.{side}.Middle"] = {"rotation": ((1, 0, 0), 0.16 * max(0, swing))}
    walk_frames.append((frame, settings))
make_clip(rig, "Walk", walk_frames, 24)

type_frames = []
for frame in (1, 4, 7, 10, 13):
    phase = 2 * pi * (frame - 1) / 12
    settings = {"Head": {"rotation": ((1, 0, 0), 0.04 * sin(phase))}}
    for side, sign in (("L", 1), ("R", -1)):
        settings[f"LegFront.{side}.Upper"] = {"rotation": ((1, 0, 0), 0.18 + 0.12 * sign * sin(phase))}
        settings[f"LegFront.{side}.Middle"] = {"rotation": ((1, 0, 0), -0.15 + 0.12 * sign * sin(phase))}
    type_frames.append((frame, settings))
make_clip(rig, "Type", type_frames, 13)

make_clip(rig, "Startle", [
    (1, {}),
    (4, {"Root": {"location": (0, 0, 0.21)},
         "Head": {"rotation": ((1, 0, 0), -0.2)},
         "Wing.L": {"rotation": ((0, 1, 0), 0.5)},
         "Wing.R": {"rotation": ((0, 1, 0), -0.5)}}),
    (10, {"Root": {"location": (0, 0, 0.08)}}),
    (20, {}),
], 20)

# Leave the file in a neutral pose. NLA clips remain available by name.
rig.animation_data.action = None
for pose in rig.pose.bones:
    pose.location = (0, 0, 0)
    pose.rotation_quaternion = (1, 0, 0, 0)
bpy.context.scene.frame_set(1)
bpy.ops.object.select_all(action="DESELECT")
rig.select_set(True)
bpy.context.view_layer.objects.active = rig

for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == "CONSOLE":
            area.type = "VIEW_3D"
        if area.type == "VIEW_3D":
            space = next((candidate for candidate in area.spaces if candidate.type == "VIEW_3D"), None)
            if space is None:
                continue
            space.shading.color_type = "MATERIAL"
            space.region_3d.view_distance = 10
            space.region_3d.view_location = (0, 0, 0)

BLEND_OUT.parent.mkdir(parents=True, exist_ok=True)
GLB_OUT.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_OUT))
for obj in bpy.data.objects:
    if obj.parent == rig:
        obj.select_set(True)
bpy.ops.export_scene.gltf(
    filepath=str(GLB_OUT),
    export_format="GLB",
    use_selection=True,
    export_animations=True,
    export_animation_mode="NLA_TRACKS",
)
print("FLY_FINISH_OK", BLEND_OUT, GLB_OUT)
print("BONES", len(rig.data.bones), "ACTIONS", [action.name for action in bpy.data.actions])
