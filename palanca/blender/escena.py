"""
Tecnovial · El dibujo de la palanca convertido en espacio.

Planta en doble H:            [1]     [3]     [5]
tres corredores verticales     |       |       |
(carriles) cruzados por el     +-------+-------+   <- travesano (neutro)
travesano central.             |       |       |
Cada extremo es una sala.     [2]     [4]     [R]
"""
import bpy, math, sys

# ---------- parametros del espacio (metros) ----------
LANES   = {-1: -14.0, 0: 0.0, 1: 14.0}   # x de cada carril
ARM     = 17.0                            # hasta donde llega cada brazo
HALF    = 3.0                             # media anchura de corredor
WALL_H  = 5.0
WALL_T  = 0.45
CAM_H   = 1.62                            # altura de ojos

GEARS = {                                  # (carril, profundidad)
    "1": (-1, -1), "2": (-1, 1),
    "3": ( 0, -1), "4": ( 0, 1),
    "5": ( 1, -1), "R": ( 1, 1),
    "N": ( 0,  0),
}

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name, rgb, rough=0.6, emit=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*rgb, 1)
        b.inputs["Emission Strength"].default_value = emit
    return m

def box(name, cx, cy, cz, sx, sy, sz, material):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy, cz))
    o = bpy.context.object; o.name = name
    o.scale = (sx/2, sy/2, sz/2)
    o.data.materials.append(material)
    return o

def build():
    reset()
    M_SUELO  = mat("suelo",  (0.035, 0.042, 0.075), rough=0.35)
    M_PARED  = mat("pared",  (0.055, 0.085, 0.45),  rough=0.85)
    M_GUIA   = mat("guia",   (1.0,   0.62,  0.06),  rough=0.4, emit=7.0)
    M_PANEL  = mat("panel",  (0.95,  0.96,  1.0),   rough=0.5, emit=2.2)
    M_ZOCALO = mat("zocalo", (0.9,   0.92,  0.98),  rough=0.7)

    # --- suelo ---
    box("suelo", 0, 0, -0.05, 70, 70, 0.1, M_SUELO)

    # --- guia luminosa: el dibujo exacto de la H sobre el suelo ---
    for lane, x in LANES.items():
        box(f"guia_v{lane}", x, 0, 0.012, 0.16, ARM*2, 0.02, M_GUIA)
    box("guia_h", 0, 0, 0.012, LANES[1]-LANES[-1], 0.16, 0.02, M_GUIA)

    # --- paredes de los carriles, partidas donde cruza el travesano ---
    for lane, x in LANES.items():
        for side in (-1, 1):
            for y0, y1 in ((-ARM, -HALF), (HALF, ARM)):
                box(f"p_lane{lane}_{side}_{y0:.0f}",
                    x + side*HALF, (y0+y1)/2, WALL_H/2,
                    WALL_T, y1-y0, WALL_H, M_PARED)

    # --- paredes del travesano, partidas donde cruzan los carriles ---
    for side in (-1, 1):
        for x0, x1 in ((LANES[-1]+HALF, LANES[0]-HALF), (LANES[0]+HALF, LANES[1]-HALF)):
            box(f"p_cross_{side}_{x0:.0f}",
                (x0+x1)/2, side*HALF, WALL_H/2,
                x1-x0, WALL_T, WALL_H, M_PARED)

    # --- fondo de cada sala: el panel donde ira el contenido ---
    for g, (lane, depth) in GEARS.items():
        if g == "N":
            continue
        x, y = LANES[lane], depth*ARM
        box(f"fondo_{g}", x, y + depth*0.2, WALL_H/2, HALF*2, WALL_T, WALL_H, M_PARED)
        box(f"panel_{g}", x, y + depth*0.1, 2.3, 3.6, 0.06, 2.0, M_PANEL)

    # --- techo: sin el, el espacio se escapa por arriba ---
    box("techo", 0, 0, WALL_H+0.2, 70, 70, 0.4, M_PARED)

    # --- testeros: cierran los extremos del travesano ---
    for side in (-1, 1):
        box(f"testero_{side}", side*(ARM+HALF), 0, WALL_H/2,
            WALL_T, HALF*2+WALL_T*2, WALL_H, M_PARED)

    # --- marcas viales: dan velocidad percibida al avanzar ---
    for lane, x in LANES.items():
        n = 0
        y = -ARM + 1.5
        while y < ARM - 1.5:
            if abs(y) > HALF + 0.6:
                box(f"m{lane}_{n}", x, y, 0.012, 0.13, 1.1, 0.02, M_ZOCALO)
                n += 1
            y += 2.6

    # --- zocalo continuo, da escala y lee bien en movimiento ---
    for lane, x in LANES.items():
        for side in (-1, 1):
            for y0, y1 in ((-ARM, -HALF), (HALF, ARM)):
                box(f"z{lane}_{side}_{y0:.0f}", x + side*(HALF-0.02), (y0+y1)/2, 0.14,
                    0.10, y1-y0, 0.28, M_ZOCALO)

    # --- luz ---
    w = bpy.data.worlds.new("w"); w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.02, 0.03, 0.07, 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = 1.0
    bpy.context.scene.world = w
    for lane, x in LANES.items():
        for y in (-ARM*0.6, 0, ARM*0.6):
            bpy.ops.object.light_add(type='AREA', location=(x, y, WALL_H-0.4))
            L = bpy.context.object
            L.data.energy = 420; L.data.size = 4.0
            L.data.color = (1.0, 0.97, 0.9)

def camera_at(gear, look):
    """Camara a la altura de los ojos en la posicion de una marcha."""
    lane, depth = GEARS[gear]
    x, y = LANES[lane], depth*(ARM-6.0)
    bpy.ops.object.camera_add(location=(x, y, CAM_H))
    cam = bpy.context.object
    cam.data.lens = 24
    dx, dy = look[0]-x, look[1]-y
    cam.rotation_euler = (math.radians(90), 0, math.atan2(dy, dx) - math.radians(90))
    bpy.context.scene.camera = cam
    return cam

def render(path, gear, look, samples=48, w=960, h=540):
    s = bpy.context.scene
    s.render.engine = 'CYCLES'
    s.cycles.device = 'CPU'
    s.cycles.samples = samples
    s.cycles.use_denoising = True
    s.render.resolution_x, s.render.resolution_y = w, h
    s.render.film_transparent = False
    s.render.filepath = path
    camera_at(gear, look)
    bpy.ops.render.render(write_still=True)
    print("OK ->", path)

def path_frames(gear, n=16):
    """Puntos del trayecto del travesano a una marcha, en dos tiempos:
       primero el carril, despues la profundidad."""
    lane, depth = GEARS[gear]
    xt, yt = LANES[lane], depth*(ARM-8.5)
    pts = []
    for i in range(n):
        t = i/(n-1)
        if t < 0.42:                     # tramo 1: desplazamiento lateral
            k = t/0.42
            k = k*k*(3-2*k)
            x, y = LANES[0] + (xt-LANES[0])*k, 0.0
        else:                            # tramo 2: entrada en profundidad
            k = (t-0.42)/0.58
            k = k*k*(3-2*k)
            x, y = xt, yt*k
        pts.append((x, y))
    return pts

def render_path(out, gear, n=16, samples=32, w=800, h=450):
    build()
    s = bpy.context.scene
    s.render.engine='CYCLES'; s.cycles.device='CPU'
    s.cycles.samples=samples; s.cycles.use_denoising=True
    s.render.resolution_x, s.render.resolution_y = w, h
    lane, depth = GEARS[gear]
    look = (LANES[lane], depth*ARM)
    bpy.ops.object.camera_add(location=(0,0,CAM_H))
    cam = bpy.context.object; cam.data.lens = 24
    s.camera = cam
    for i,(x,y) in enumerate(path_frames(gear,n)):
        cam.location = (x,y,CAM_H)
        dx,dy = look[0]-x, look[1]-y
        cam.rotation_euler = (math.radians(90), 0, math.atan2(dy,dx)-math.radians(90))
        s.render.filepath = f"{out}{gear}-{i:02d}"
        bpy.ops.render.render(write_still=True)
    print("secuencia lista:", gear, n, "frames")

if __name__ == "__main__":
    out = sys.argv[-1] if len(sys.argv) > 1 else "/tmp/"
    modo = sys.argv[-2] if len(sys.argv) > 2 else "still"
    if modo == "path":
        render_path(out, "3", n=16)
    else:
        build()
        render(out + "n.png", "N", look=(0.0, ARM))
