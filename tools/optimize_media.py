#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Optimise les médias en WebP web pour la landing eFoil COMO Le Beauvallon.

Deux sorties :
  1) SLOTS NOMMÉS (recadrage précis) → medias/web/<slot>.webp  (héros, lieu, beach, expérience, galerie, déroulé)
  2) POOL (galerie auto / slides aléatoires) → medias/web/pool/*.webp
     = toutes les photos riders + frames vidéo (sauf dubai), ratio natif, grade chaud
       auto sur les plans froids (détection bleu>rouge), frames vidéo filtrées (transitions/noir).

Usage : python tools/optimize_media.py   (Pillow requis)
"""
import os, glob, re
from PIL import Image, ImageOps, ImageEnhance, ImageStat

os.makedirs('medias/web', exist_ok=True)
os.makedirs('medias/web/pool', exist_ok=True)
M = 'medias'

SRC = {
    'ST7':f'{M}/saint-tropez/Stropez_day2-7.jpg','ST11':f'{M}/saint-tropez/Stropez_day2-11.jpg',
    'BVland':f'{M}/como-beauvallon/a715426f-04a3-4407-abce-65a7dffb1f08.JPG',
    'BVp1':f'{M}/como-beauvallon/6f9dea10-981b-4b23-8fde-4a21f87acd52.JPG',
    'BVp2':f'{M}/como-beauvallon/19a1d93b-24c7-4ce7-8e34-fc634e6ce764.JPG',
    'LER26':f'{M}/iles-lerins/Post_4x5-26_First.jpg','LER25':f'{M}/iles-lerins/Post_4x5-25_Secondd.jpg',
    'EST5':f'{M}/esterel/Post_4x5-5.jpg','CAN2':f'{M}/cannes/Cannes_Cote-2.jpg',
    'CAN99':f'{M}/cannes/Cannes_Cote-99.jpg','CAN103':f'{M}/cannes/Cannes_Cote-103.jpg',
    'CAN167':f'{M}/cannes/Cannes_Cote-167.jpg','CAN161':f'{M}/cannes/Cannes_Cote-161.jpg',
    'CO_grandevue':f'{M}/como-web/raw/hero.jpg','CO_chateau':f'{M}/como-web/raw/location.jpg',
    'CO_parasols':f'{M}/como-web/raw/exp2.jpg','CO_dining':f'{M}/como-web/raw/dining1.jpg',
    'VF_sunset':f'{M}/video-frames/awaking-sunset-hi.jpg','VF_cannes':f'{M}/video-frames/puerto-cannes-hi.jpg',
    'VF_esterel':f'{M}/video-frames/torre-esterel-hi.jpg',
}

def warm_grade(im):
    r,g,b=im.split()
    r=r.point(lambda v:min(255,int(v*1.045+3))); b=b.point(lambda v:max(0,int(v*0.95-1)))
    im=Image.merge('RGB',(r,g,b))
    im=ImageEnhance.Color(im).enhance(0.90); im=ImageEnhance.Contrast(im).enhance(1.04)
    return ImageEnhance.Brightness(im).enhance(1.015)

# (out, srckey, (rw,rh), largeur, vfocus, hfocus, grade)
JOBS = [
    ('hero-grandevue','CO_grandevue',(16,9),1920,.5,.5,0),
    ('hero-chateau','CO_chateau',(16,9),1920,.40,.5,0),
    ('hero-sunset','ST7',(16,9),1920,.60,.5,0),
    ('lieu-chateau','CO_chateau',(4,3),1280,.42,.5,0),
    ('spot-aerial','CO_grandevue',(4,3),1280,.30,.18,0),
    ('beach-aerial','CO_dining',(16,9),1280,.5,.5,0),
    ('beach-parasols','CO_parasols',(4,3),1100,.5,.5,0),
    ('exp-silence','ST11',(16,9),1280,.55,.5,0),
    ('exp-apesanteur','BVland',(4,3),1280,.46,.5,1),
    ('exp-rythme','CAN161',(3,4),1000,.45,.5,1),
    ('breath-sunset','VF_sunset',(16,9),1920,.5,.5,0),
    ('breath-redrock','CAN103',(16,9),1920,.5,.5,1),
    ('breath-golfe','CAN167',(16,9),1920,.5,.5,1),
    ('ride-women','BVp2',(3,4),1000,.42,.5,1),
    ('ride-redrock','CAN99',(4,3),1280,.5,.5,1),
    ('ride-lerins-orange','LER26',(3,4),1000,.42,.5,1),
    ('ride-formation','CAN167',(4,3),1280,.5,.5,1),
    ('ride-esterel','EST5',(3,4),1000,.45,.5,1),
    ('ride-yacht','VF_cannes',(3,4),1000,.5,.5,1),
    ('ride-esterel-vert','VF_esterel',(3,4),1000,.45,.5,1),
    ('ride-lerins-green','LER25',(3,4),1000,.42,.5,1),
    ('session-briefing','CAN2',(16,9),1280,.5,.5,1),
    ('session-gear','BVp2',(16,9),1280,.4,.5,1),
    ('session-water','BVp1',(16,9),1280,.45,.5,1),
    ('session-flight','CAN103',(16,9),1280,.5,.5,1),
]

def make(out, srckey, ratio, tw, vf, hf, grade, q=80):
    im=ImageOps.exif_transpose(Image.open(SRC[srckey]).convert('RGB'))
    if grade: im=warm_grade(im)
    W,H=im.size; rw,rh=ratio; tr=rw/rh; cur=W/H
    if cur>tr: nw,nh=int(round(H*tr)),H
    else: nw,nh=W,int(round(W/tr))
    x=int((W-nw)*hf); y=int((H-nh)*vf)
    im=im.crop((x,y,x+nw,y+nh)).resize((tw,int(round(tw/tr))),Image.LANCZOS)
    p=f'medias/web/{out}.webp'; im.save(p,'WEBP',quality=q,method=6)
    return im.size, os.path.getsize(p)//1024

# ---- POOL (galerie auto) ----
POOL_DIRS=[f'{M}/cannes',f'{M}/saint-tropez',f'{M}/iles-lerins',f'{M}/esterel',
           f'{M}/como-beauvallon',f'{M}/video-frames/auto']
def slug(path):
    folder=os.path.basename(os.path.dirname(path)); stem=os.path.splitext(os.path.basename(path))[0]
    s=re.sub(r'[^a-zA-Z0-9]+','-',f'{folder}-{stem}').strip('-').lower()
    return s[:60]
def pool_one(path,maxside=1120,q=76):
    try: im=ImageOps.exif_transpose(Image.open(path).convert('RGB'))
    except Exception: return None
    # filtre qualité (surtout frames vidéo) : rejette noir / transition
    st=ImageStat.Stat(im.convert('L')); bright=st.mean[0]; std=st.stddev[0]
    if bright<26 or std<15: return None
    rgb=ImageStat.Stat(im).mean
    if rgb[2] > rgb[0]+2: im=warm_grade(im)         # froid (bleu>rouge) -> grade chaud
    W,H=im.size; sc=min(1.0, maxside/max(W,H)); im=im.resize((int(W*sc),int(H*sc)),Image.LANCZOS)
    out=f'medias/web/pool/{slug(path)}.webp'; im.save(out,'WEBP',quality=q,method=6)
    return out, os.path.getsize(out)//1024

if __name__=='__main__':
    if os.path.exists('medias/web/hero-video-poster.jpg'):
        Image.open('medias/web/hero-video-poster.jpg').convert('RGB').save('medias/web/hero-video-poster.webp','WEBP',quality=82,method=6)
    tot=0
    for out,sk,r,tw,vf,hf,g in JOBS:
        (w,h),kb=make(out,sk,r,tw,vf,hf,g); tot+=kb
    print(f"SLOTS: {len(JOBS)} fichiers, {tot} Ko")
    # nettoyage pool existant
    for f in glob.glob('medias/web/pool/*.webp'): os.remove(f)
    paths=[]
    for d in POOL_DIRS:
        for ext in ('*.jpg','*.jpeg','*.JPG','*.png'): paths+=glob.glob(f'{d}/{ext}')
    paths=sorted(set(paths)); kept=0; ptot=0; skipped=0
    for p in paths:
        r=pool_one(p)
        if r: kept+=1; ptot+=r[1]
        else: skipped+=1
    print(f"POOL: {kept} images gardees ({ptot} Ko ~ {ptot/1024:.1f} Mo), {skipped} rejetees (noir/transition)")
    print(f"TOTAL web: ~{(tot+ptot)/1024:.1f} Mo")
