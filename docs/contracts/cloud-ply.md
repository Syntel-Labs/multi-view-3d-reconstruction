# Contrato - cloud.ply

- Version: 0.1.0
- Productor: Persona B
- Consumidores: Persona C, Persona D

Define el archivo de nube de puntos generado por el pipeline.

## Ubicacion

```text
outputs/<name>/cloud.ply
```

## Formato

PLY ASCII (no binario) con cabecera estandar:

```text
ply
format ascii 1.0
element vertex N
property float x
property float y
property float z
property uchar red
property uchar green
property uchar blue
end_header
<x1> <y1> <z1> <r1> <g1> <b1>
...
```

## Reglas

- En el core sin coloreado por foto, los canales `red`, `green`, `blue` se llenan con `255` (puntos blancos) para mantener compatibilidad con visores que esperan color.
- Sin normales por punto en la version core. Si se anaden mas adelante, bumping de version.
- El sistema de coordenadas es el de la primera camara: origen en su centro optico, eje Z apuntando hacia la escena.
