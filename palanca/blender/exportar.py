"""Genera el .blend para abrirlo en Blender de escritorio."""
import bpy, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from escena import build, GEARS, LANES, ARM, CAM_H
import math

build()

# camaras colocadas en cada marcha, listas para mirar por ellas
for g, (lane, depth) in GEARS.items():
    if g == "N":
        x, y, look = 0.0, 0.0, (0.0, ARM)
    else:
        x, y = LANES[lane], depth*(ARM-8.5)
        look = (LANES[lane], depth*ARM)
    bpy.ops.object.camera_add(location=(x, y, CAM_H))
    c = bpy.context.object
    c.name = f"CAM_{g}"
    c.data.lens = 24
    dx, dy = look[0]-x, look[1]-y
    c.rotation_euler = (math.radians(90), 0, math.atan2(dy, dx) - math.radians(90))

bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080

out = sys.argv[-1]
bpy.ops.wm.save_as_mainfile(filepath=out)
print("guardado:", out, round(os.path.getsize(out)/1024), "KB")
