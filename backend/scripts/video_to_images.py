import cv2
from pathlib import Path

video_path = "/home/donmathiuz/Vídeos/VID_20260524_043607.mp4"
output_dir = Path("/home/donmathiuz/multi-view-3d-reconstruction/data/controlgamecube/images")
output_dir.mkdir(parents=True, exist_ok=True)

cap = cv2.VideoCapture(video_path)
total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps   = cap.get(cv2.CAP_PROP_FPS)
print(f"Total frames: {total}  |  FPS: {fps:.1f}  |  Duración: {total/fps:.1f}s")

frame_num = 0
saved = 0
every_n = 5  # guarda 1 de cada 5 frames (ajusta según cuántas fotos quieras)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    if frame_num % every_n == 0:
        name = output_dir / f"frame{saved+1:06d}.jpg"
        cv2.imwrite(str(name), frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
        saved += 1
    frame_num += 1

cap.release()
print(f"Guardadas {saved} imágenes en {output_dir}")
