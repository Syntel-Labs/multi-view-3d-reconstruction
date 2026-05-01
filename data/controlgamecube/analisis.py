import os
import cv2
import numpy as np
from PIL import Image, ExifTags
from collections import Counter
from datetime import datetime

ruta = r"C:\Users\donMatthiuz\Pictures\controlgamecube"

resoluciones = []
dispositivos = []
fechas = []
brillos = []
nitidez = []
colores = []

def obtener_exif(img):
    try:
        exif = img._getexif()
        if not exif:
            return {}
        return {
            ExifTags.TAGS.get(tag, tag): val
            for tag, val in exif.items()
        }
    except:
        return {}

for archivo in os.listdir(ruta):
    if archivo.lower().endswith((".jpg", ".jpeg", ".png")):
        path = os.path.join(ruta, archivo)

        try:
            # PIL (EXIF)
            img_pil = Image.open(path)
            resoluciones.append(img_pil.size)

            exif = obtener_exif(img_pil)

            if "Model" in exif:
                dispositivos.append(exif["Model"])

            if "DateTimeOriginal" in exif:
                fechas.append(exif["DateTimeOriginal"])

            # OpenCV (análisis)
            img = cv2.imread(path)

            gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Brillo (0-255)
            brillos.append(np.mean(gris))

            # Nitidez (Laplaciano)
            lap = cv2.Laplacian(gris, cv2.CV_64F)
            nitidez.append(lap.var())

            # Color promedio
            colores.append(np.mean(img, axis=(0, 1)))

        except Exception as e:
            print(f"Error con {archivo}: {e}")

print("\n===== RESULTADOS AVANZADOS =====")

print(f"Cantidad de imágenes: {len(resoluciones)}")

# Resoluciones
if resoluciones:
    ancho = [r[0] for r in resoluciones]
    alto = [r[1] for r in resoluciones]

    print(f"Resolución más común: {Counter(resoluciones).most_common(1)[0][0]}")
    print(f"Resolución mínima: {min(ancho)}x{min(alto)}")
    print(f"Resolución máxima: {max(ancho)}x{max(alto)}")
    print(f"Resolución promedio: {int(np.mean(ancho))}x{int(np.mean(alto))}")

# Dispositivo
if dispositivos:
    print(f"Dispositivo: {Counter(dispositivos).most_common(1)[0][0]}")
else:
    print("Dispositivo: No detectado (sin EXIF)")

# Fechas
if fechas:
    fechas_dt = []
    for f in fechas:
        try:
            fechas_dt.append(datetime.strptime(f, "%Y:%m:%d %H:%M:%S"))
        except:
            pass

    if fechas_dt:
        print(f"Rango de fechas: {min(fechas_dt)} → {max(fechas_dt)}")

# Brillo
if brillos:
    print(f"Brillo promedio: {np.mean(brillos):.2f}")
    print(f"Brillo min/max: {min(brillos):.2f} / {max(brillos):.2f}")

# Nitidez
if nitidez:
    print(f"Nitidez promedio: {np.mean(nitidez):.2f}")
    print(f"Nitidez min/max: {min(nitidez):.2f} / {max(nitidez):.2f}")

    borrosas = sum(1 for n in nitidez if n < 100)
    print(f"Imágenes borrosas (estimado): {borrosas}")

# Color
if colores:
    color_prom = np.mean(colores, axis=0)
    print(f"Color promedio (BGR): {color_prom.astype(int)}")

print("===============================")
