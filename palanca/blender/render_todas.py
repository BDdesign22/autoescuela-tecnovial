"""Renderiza el trayecto de cada marcha. Pensado para lanzar en segundo plano."""
import bpy, math, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from escena import build, GEARS, LANES, ARM, CAM_H, path_frames

OUT = sys.argv[-1]
build()
s = bpy.context.scene
s.render.engine='CYCLES'; s.cycles.device='CPU'
s.cycles.samples=32; s.cycles.use_denoising=True
s.render.resolution_x, s.render.resolution_y = 800, 450
bpy.ops.object.camera_add(location=(0,0,CAM_H))
cam = bpy.context.object; cam.data.lens=24; s.camera=cam

for g in ("1","2","4","5","R"):
    lane, depth = GEARS[g]
    look = (LANES[lane], depth*ARM)
    for i,(x,y) in enumerate(path_frames(g,16)):
        cam.location=(x,y,CAM_H)
        dx,dy = look[0]-x, look[1]-y
        cam.rotation_euler=(math.radians(90),0,math.atan2(dy,dx)-math.radians(90))
        s.render.filepath=f"{OUT}{g}-{i:02d}"
        bpy.ops.render.render(write_still=True)
    print("### marcha lista:", g, flush=True)
print("### TODAS LISTAS", flush=True)
