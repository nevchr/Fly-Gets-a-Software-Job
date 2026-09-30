"""Summarize the current handmade fly scene without changing it."""

import bpy
from mathutils import Vector


print("FLY_SCENE_BEGIN")
print("BLEND", bpy.data.filepath)
print("FRAME", bpy.context.scene.frame_start, bpy.context.scene.frame_end)
for obj in bpy.data.objects:
    print(
        "OBJECT",
        repr(obj.name),
        obj.type,
        "location", tuple(round(v, 3) for v in obj.location),
        "dimensions", tuple(round(v, 3) for v in obj.dimensions),
        "parent", repr(obj.parent.name if obj.parent else None),
        "parent_bone", repr(obj.parent_bone),
    )
    if obj.type == "MESH":
        world = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
        if world:
            print(
                "  BOUNDS",
                tuple(round(min(point[axis] for point in world), 3) for axis in range(3)),
                tuple(round(max(point[axis] for point in world), 3) for axis in range(3)),
                "verts", len(world),
            )
    elif obj.type == "ARMATURE":
        for bone in obj.data.bones:
            print(
                "  BONE",
                repr(bone.name),
                "head", tuple(round(v, 3) for v in bone.head_local),
                "tail", tuple(round(v, 3) for v in bone.tail_local),
                "parent", repr(bone.parent.name if bone.parent else None),
            )
print("FLY_SCENE_END")
