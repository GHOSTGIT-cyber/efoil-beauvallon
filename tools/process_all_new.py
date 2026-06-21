"""
1. Posters des nouveaux reels (medias/reel/)
2. Thumbnails photos Dubai (moniteur en noir -> étapes process)
3. Poster du hero video (Cotedezur_Awaking_Subtitled.MP4)
"""
import cv2
from PIL import Image, ImageOps
import os, glob

def save_webp(img_pil, path, quality=74, max_w=1400):
    img_pil.thumbnail((max_w, max_w), Image.LANCZOS)
    img_pil.save(path, "WEBP", quality=quality)
    return os.path.getsize(path) // 1024

def frame_from_video(src, pct=0.15, max_w=960):
    cap = cv2.VideoCapture(src)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.set(cv2.CAP_PROP_POS_FRAMES, max(1, int(total * pct)))
    ok, f = cap.read()
    if not ok:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 1); ok, f = cap.read()
    cap.release()
    if not ok: return None
    rgb = cv2.cvtColor(f, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(rgb)
    img.thumbnail((max_w, max_w), Image.LANCZOS)
    return img

OUT_IMG = "d:/efoilcotedazur/assets/img"
OUT_VID = "d:/efoilcotedazur/assets/video"
os.makedirs(OUT_IMG, exist_ok=True)
os.makedirs(OUT_VID, exist_ok=True)

# ─── 1. Nouveaux reels (skip les gros) ───────────────────────────────────────
REELS = [
    ("d:/efoilcotedazur/medias/reel/Efoil Community_v3.mov",        "reel-community"),
    ("d:/efoilcotedazur/medias/reel/Efoil In One Word (French).mov","reel-oneword"),
    ("d:/efoilcotedazur/medias/reel/REEL ISLOTE PLAYA RARO.mov",    "reel-islote"),
    ("d:/efoilcotedazur/medias/reel/REEL MUNTANYA DIA 1.mov",       "reel-muntanya"),
    ("d:/efoilcotedazur/medias/reel/REEL saintropez.mov",           "reel-saintropez"),
    ("d:/efoilcotedazur/medias/reel/REEL STATION I CASTILLO_v2.mov","reel-station"),
]
for src, name in REELS:
    if not os.path.exists(src): print(f"MANQUANT {src}"); continue
    # Poster
    img = frame_from_video(src, pct=0.12)
    if img:
        ko = save_webp(img, f"{OUT_IMG}/{name}-poster.webp", quality=70)
        print(f"POSTER  {name}-poster.webp  {img.width}x{img.height}  {ko}Ko")
    # Copie vidéo (seulement si < 25 Mo)
    size_mo = os.path.getsize(src) / 1e6
    dst = f"{OUT_VID}/{name}.mov"
    if not os.path.exists(dst):
        if size_mo < 25:
            import shutil
            shutil.copy2(src, dst)
            print(f"COPIE   {name}.mov  ({size_mo:.1f}Mo)")
        else:
            print(f"SKIP    {name}.mov  trop lourd ({size_mo:.1f}Mo)")

# ─── 2. Photos Dubai (moniteur en noir) → étapes process ─────────────────────
DUBAI = {
    "step-briefing":  "d:/efoilcotedazur/medias/dubai/Lift_Dubai_day1-19.jpg",  # briefing/accueil
    "step-materiel":  "d:/efoilcotedazur/medias/dubai/Lift_Dubai_day0-26.jpg",  # matériel
    "step-session":   "d:/efoilcotedazur/medias/dubai/Lift_Dubai_day1-34.jpg",  # en action
    "step-progress":  "d:/efoilcotedazur/medias/dubai/Lift_Dubai_day2-14.jpg",  # progression
}
for name, src in DUBAI.items():
    if not os.path.exists(src): print(f"MANQUANT {src}"); continue
    img = ImageOps.exif_transpose(Image.open(src).convert("RGB"))
    ko = save_webp(img, f"{OUT_IMG}/{name}.webp", quality=76, max_w=1200)
    print(f"DUBAI   {name}.webp  {img.width}x{img.height}  {ko}Ko")

# ─── 3. Hero poster depuis Cotedezur_Awaking_Subtitled.MP4 ───────────────────
hero_src = "d:/efoilcotedazur/medias/videos-cotedazur/Cotedezur_Awaking_Subtitled.MP4"
if os.path.exists(hero_src):
    img = frame_from_video(hero_src, pct=0.08, max_w=1920)
    if img:
        ko = save_webp(img, f"{OUT_IMG}/hero-awaking-poster.webp", quality=75)
        print(f"HERO    hero-awaking-poster.webp  {img.width}x{img.height}  {ko}Ko")

print("Terminé.")
