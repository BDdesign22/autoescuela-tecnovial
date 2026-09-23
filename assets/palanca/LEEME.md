# Escenas de la palanca de cambios

Cada sección es una marcha de una caja en H (N en el centro):

```
1 (Precios)     3 (Nosotros)
      \---- N (Inicio) ----/
2 (Permisos)    4 (Propuesta)
```

| Fichero            | Uso                                                        |
|--------------------|------------------------------------------------------------|
| n-hero.webp        | Punto muerto: cabecera de Inicio                           |
| barrido.webp       | Fotograma de barrido lateral (y puerta provisional de 3ª/4ª) |
| 1-pasillo.webp     | Puerta de la columna izquierda: la 1ª se ve al fondo       |
| 1-recepcion.webp   | Escena de 1ª: cabecera de Precios                          |

Pendientes (hoy usan la cabecera azul de marca): escena de 2ª, puerta de la
columna derecha y escenas de 3ª y 4ª. Formato 16:9, 1672×941 o mayor, con el
lado izquierdo despejado para el texto. Para añadir una: meter el marcador en
`build.py`, un `<img id="sc-...">` en la plantilla y apuntar `puerta`/`escena`
en `MARCHAS` (script de `src/template.html`).
