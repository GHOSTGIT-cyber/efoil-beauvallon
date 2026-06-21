#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Édition "full drone" : à partir des frames aériennes distinctes
(medias/video-frames/drone/, produites par l'extraction + dédup perceptuelle),
génère des SLOTS NOMMÉS drone-* (chaque slot = une frame DIFFÉRENTE) + un POOL
aérien (medias/web/pool-drone/) pour les galeries auto.

Usage : python tools/drone_slots.py   (puis tools/build_versions.py régénère v4)
"""
import glob, os, re, shutil
from PIL import Image, ImageOps, ImageEnhance, ImageStat

DR='medias/video-frames/drone'
POOL='medias/web/pool-drone'
shutil.rmtree(POOL, ignore_errors=True); os.makedirs(POOL, exist_ok=True)
frames=sorted(glob.glob(f'{DR}/*.jpg'))

def warm_grade(im):
    r,g,b=im.split()
    r=r.point(lambda v:min(255,int(v*1.045+3))); b=b.point(lambda v:max(0,int(v*0.95-1)))
    im=Image.merge('RGB',(r,g,b)); im=ImageEnhance.Color(im).enhance(0.90)
    return ImageEnhance.Brightness(ImageEnhance.Contrast(im).enhance(1.04)).enhance(1.015)
def load(p): return ImageOps.exif_transpose(Image.open(p).convert('RGB'))
def cool(im): m=ImageStat.Stat(im).mean; return m[2]>m[0]+2
def slug(p):
    s=re.sub(r'[^a-z0-9]+','-',os.path.splitext(os.path.basename(p))[0].lower()); return s.strip('-')
def crop(im,ratio,tw,vf=.5,hf=.5):
    W,H=im.size; rw,rh=ratio; tr=rw/rh; cur=W/H
    if cur>tr: nw,nh=int(round(H*tr)),H
    else: nw,nh=W,int(round(W/tr))
    x=int((W-nw)*hf); y=int((H-nh)*vf)
    return im.crop((x,y,x+nw,y+nh)).resize((tw,int(round(tw/tr))),Image.LANCZOS)

order=sorted(frames)
print(f"frames aériennes distinctes : {len(order)}")

# POOL aérien : toutes les frames (ratio natif), grade chaud sur les froides
ptot=0
for f in order:
    im=load(f)
    if cool(im): im=warm_grade(im)
    W,H=im.size; sc=min(1.0,1200/max(W,H)); im=im.resize((int(W*sc),int(H*sc)),Image.LANCZOS)
    p=f'{POOL}/{slug(f)}.webp'; im.save(p,'WEBP',quality=76,method=6); ptot+=os.path.getsize(p)//1024
print(f"POOL drone : {len(order)} images ({ptot} Ko ~ {ptot/1024:.1f} Mo)")

# SLOTS nommés : chaque slot = une frame DIFFÉRENTE (recadrée à son ratio).
# Toutes les frames étant aériennes, on recadre indifféremment (un plan large aérien
# recadré en portrait reste aérien).
SLOTS=[('drone-lieu',(4,3),1280),('drone-exp1',(16,9),1280),('drone-exp2',(4,3),1280),
       ('drone-slide1',(16,9),1280),('drone-slide2',(16,9),1280),('drone-beach2',(4,3),1100),
       ('drone-session-1',(16,9),1280),('drone-session-2',(16,9),1280),
       ('drone-session-3',(16,9),1280),('drone-session-4',(16,9),1280),
       ('drone-ride-2',(4,3),1280),('drone-ride-4',(4,3),1280),
       ('drone-exp3',(3,4),1000),('drone-ride-1',(3,4),1000),('drone-ride-3',(3,4),1000),
       ('drone-ride-5',(3,4),1000),('drone-ride-6',(3,4),1000),('drone-ride-7',(3,4),1000),
       ('drone-ride-8',(3,4),1000)]
for i,(name,ratio,tw) in enumerate(SLOTS):
    f=order[i % len(order)]
    im=load(f)
    if cool(im): im=warm_grade(im)
    crop(im,ratio,tw).save(f'medias/web/{name}.webp','WEBP',quality=80,method=6)
print(f"SLOTS drone : {len(SLOTS)} générés (medias/web/drone-*.webp)")
