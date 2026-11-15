"""Template Blender scene: extruded 3D title, floor, area light and a camera
dolly over frames 1-90. Build your own scene the same way (from Python, starting
from Blender's factory scene) and render with
  python tools/blender/render_blender.py --script tools/blender/templates/title.py --out title.mp4
"""

import math

import bpy

scene = bpy.context.scene
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)

bpy.ops.object.text_add(location=(0, 0, 0), rotation=(math.radians(90), 0, 0))
title = bpy.context.object
title.data.body = "Title"
title.data.align_x = "CENTER"
title.data.align_y = "CENTER"
title.data.extrude = 0.08
title.data.bevel_depth = 0.012
material = bpy.data.materials.new("title")
material.use_nodes = True
bsdf = material.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.25, 0.5, 1.0, 1.0)
bsdf.inputs["Metallic"].default_value = 0.6
bsdf.inputs["Roughness"].default_value = 0.25
title.data.materials.append(material)

bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, -0.9))
bpy.ops.object.light_add(type="AREA", location=(3, -4, 5))
light = bpy.context.object
light.data.energy = 1500
light.data.size = 5

world = bpy.data.worlds.new("backdrop")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.02, 0.025, 0.04, 1.0)
scene.world = world

bpy.ops.object.camera_add(location=(-2.5, -11, 1.8))
camera = bpy.context.object
# A 32 mm lens keeps the whole title (about 8.5 units wide) in frame from 8.5 units away.
camera.data.lens = 32
scene.camera = camera
aim = camera.constraints.new("TRACK_TO")
aim.target = title
aim.track_axis = "TRACK_NEGATIVE_Z"
aim.up_axis = "UP_Y"

scene.frame_start, scene.frame_end = 1, 90
camera.keyframe_insert("location", frame=1)
camera.location = (1.5, -8.5, 0.9)
camera.keyframe_insert("location", frame=90)
