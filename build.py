#!/usr/bin/env python3
"""
Genera public/index.html a partir de src/template.html, embebiendo las imagenes
en base64 para que el HTML resultante sea autocontenido (se abre con doble clic).

Uso:  python build.py
"""
import base64
import pathlib
import sys

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "src" / "template.html"
OUT = ROOT / "public" / "index.html"
ASSETS = ROOT / "assets"

IMAGENES = {
    "{{IMG_LOGO}}": "logo.webp",
    "{{IMG_SEMAFORO_SISTEMA}}": "web/sistema_semaforo.webp",
    "{{IMG_PATRON}}": "web/patron_senales.webp",
    "{{IMG_PLACA_L}}": "logo-referencia/isotipo-placa-L-transparente.png",
    "{{IMG_LOGO_TRANSPARENTE}}": "logo-referencia/logo-tecnovial-transparente.png",
    "{{IMG_BD_LOGO}}": "web/bd-logo.webp",
    "{{IMG_BD_ISOTIPO}}": "web/bd-isotipo.webp",
    # Escenas de la palanca de cambios (N -> 1a)
    "{{IMG_P_HERO}}": "palanca/n-hero.webp",
    "{{IMG_P_BARRIDO}}": "palanca/barrido.webp",
    "{{IMG_P_PASILLO}}": "palanca/1-pasillo.webp",
    "{{IMG_P_RECEPCION}}": "palanca/1-recepcion.webp",
}

# Las 16 fotos de la sesion, en assets/web/01.webp ... 16.webp
IMAGENES.update({"{{IMG_%02d}}" % n: "web/%02d.webp" % n for n in range(1, 17)})


def data_uri(nombre: str) -> str:
    ruta = ASSETS / nombre
    if not ruta.exists():
        sys.exit(f"ERROR: falta el activo {ruta}")
    ext = ruta.suffix.lower()
    mime = {"webp": "image/webp", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}.get(ext, "image/webp")
    if ext == ".webp":
        mime = "image/webp"
    elif ext == ".png":
        mime = "image/png"
    else:
        mime = "image/jpeg"
    b64 = base64.b64encode(ruta.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def main() -> None:
    html = SRC.read_text(encoding="utf-8")

    for marca, fichero in IMAGENES.items():
        if marca not in html:
            print(f"  aviso: {marca} no aparece en la plantilla")
        html = html.replace(marca, data_uri(fichero))

    restantes = [m for m in IMAGENES if m in html]
    if restantes:
        sys.exit(f"ERROR: quedan marcadores sin sustituir: {restantes}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")

    kb = OUT.stat().st_size / 1024
    print(f"OK  {OUT.relative_to(ROOT)}  ({kb:.0f} KB)")


if __name__ == "__main__":
    main()
