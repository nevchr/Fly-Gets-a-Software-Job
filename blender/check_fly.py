"""Check animation poses and render small contact images for visual QA."""

import bpy
from pathlib import Path
from mathutils import Vector


root = Path(__file__).resolve().parents[1]
out_dir = root / "blender" / "qa"
out_dir.mkdir(parents=True, exist_ok=True)
rig = bpy.data.objects["Fly_Armature"]
scene = bpy.context.scene

camera_data = bpy.data.cameras.new("QA_Camera")
camera = bpy.data.objects.new("QA_Camera", camera_data)
scene.collection.objects.link(camera)
camera.location = (8.5, 6.5, 4.0)
target = Vector((0, 0, -0.25))
camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
camera_data.type = "ORTHO"
camera_data.ortho_scale = 9.5
scene.camera = camera
scene.render.engine = "BLENDER_WORKBENCH"
scene.render.resolution_x = 900
scene.render.resolution_y = 600
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.display.shading.light = "STUDIO"
scene.display.shading.color_type = "MATERIAL"
scene.render.film_transparent = False

for name, frame in (("Idle", 12), ("WingFlap", 3), ("Walk", 7), ("Type", 4), ("Startle", 4)):
    rig.animation_data.action = bpy.data.actions[name]
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    wing_heights = []
    for side in ("L", "R"):
        wing = bpy.data.objects[f"Fly_Wing.{side}"]
        world = [wing.matrix_world @ vertex.co for vertex in wing.data.vertices]
        wing_heights.append((side, round(min(v.z for v in world), 3), round(max(v.z for v in world), 3)))
    scene.render.filepath = str(out_dir / f"{name}.png")
    bpy.ops.render.render(write_still=True)
    print("CHECK_POSE", name, frame, "wing-z", wing_heights)
