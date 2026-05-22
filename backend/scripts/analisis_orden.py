# reorder_dataset.py
import numpy as np
from sfm_pipeline import features, matching, preprocess
from sfm_pipeline.utils import list_images

paths = list_images("data/apple_co3d/images")
n = len(paths)

print(f"Cargando descriptores de {n} imágenes...")
descs = []
for p in paths:
    gray = preprocess.to_grayscale(preprocess.load_image(p))
    _, des = features.detect_sift(gray)
    descs.append(des)

# Construir matriz de similitud (solo triangulo superior para no duplicar)
print("Calculando similitud entre pares...")
sim = np.zeros((n, n), dtype=np.int32)
for i in range(n):
    for j in range(i + 1, n):
        m = matching.match_descriptors(descs[i], descs[j], ratio=0.75)
        sim[i, j] = len(m)
        sim[j, i] = len(m)
    if i % 10 == 0:
        print(f"  {i}/{n}")

# Greedy nearest-neighbor: empezar por la imagen con más matches globales
visited = [False] * n
order = []
current = int(np.argmax(sim.sum(axis=1)))
for _ in range(n):
    visited[current] = True
    order.append(current)
    # siguiente: vecino no visitado con más matches
    row = sim[current].copy()
    row[[i for i, v in enumerate(visited) if v]] = -1
    nxt = int(np.argmax(row))
    if row[nxt] < 0:
        break
    current = nxt

print(f"\nOrden sugerido ({len(order)} imágenes):")
print(order)
print("\nNombre de archivos en ese orden:")
for idx in order:
    print(f"  {idx:3d} → {paths[idx].name}  (mejor vecino: {sim[idx].max()} matches)")
