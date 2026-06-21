"""
Extrait une frame poster de chaque .mov et la sauvegarde en WebP.
Utilise OpenCV + Pillow.
"""
import cv2
from PIL import Image
import numpy as np
import os

VIDEOS = [
    ("d:/efoilcotedazur/medias/videos-espagne/REEL FORTALEZA Y SUPERYATES.mov", "reel-superyachts"),
    ("d:/efoilcotedazur/medias/videos-espagne/REEL PUERTO Y HOTEL 1.mov",        "reel-session"),
    ("d:/efoilcotedazur/medias/videos-espagne/REEL TORRE TIN TIN.mov",           "reel-cote"),
]

OUT = "d:/efoilcotedazur/assets/img"
os.makedirs(OUT, exist_ok=True)

for src, name in VIDEOS:
    cap = cv2.VideoCapture(src)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps   = cap.get(cv2.CAP_PROP_FPS) or 30
    # frame à ~15% du clip (évite le noir du début)
    target = max(1, int(total * 0.15))
    cap.set(cv2.CAP_PROP_POS_FRAMES, target)
    ok, frame = cap.read()
    if not ok:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 1)
        ok, frame = cap.read()
    cap.release()
    if not ok:
        print(f"SKIP {name} — impossible de lire la frame")
        continue
    # BGR → RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(rgb)
    # Redimensionne à 1280px max
    img.thumbnail((1280, 1280), Image.LANCZOS)
    out_path = f"{OUT}/{name}-poster.webp"
    img.save(out_path, "WEBP", quality=72)
    size_kb = os.path.getsize(out_path) // 1024
    print(f"OK  {name}-poster.webp  — {img.width}x{img.height}  {size_kb} Ko")

print("Terminé.")
