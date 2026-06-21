#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Applique le tri du trieur (tools/packs.json) :
- POOL mosaïque (medias/web/pool/)      = TOUS les keepers (hors "proscrire")
- POOL drone (medias/web/pool-drone/)   = keepers AÉRIENS (pack aerien + frames drone)
- SLOTS nommés (medias/web/*.webp)       = recadrés depuis les images choisies dans les packs
- SLOTS drone (medias/web/drone-*.webp)  = depuis les keepers aériens
Les "à proscrire" sont exclus partout.

Usage : python tools/apply_packs.py   (puis tools/build_versions.py)
"""
import json, os, glob, re
from PIL import Image, ImageOps, ImageEnhance, ImageStat

P=json.load(open('tools/packs.json',encoding='utf-8'))
packs=P['packs']; proscrire=set(packs.get('proscrire',[]))

def ex(p): return os.path.exists(p)
keepers=[]; seen=set()
for cid,lst in packs.items():
    if cid=='proscrire': continue
    for p in lst:
        if p in proscrire or p in seen or not ex(p): continue
        seen.add(p); keepers.append(p)
aerien=set(packs.get('aerien',[])); top=set(packs.get('top',[]))
def is_aerial(p): return p in aerien or 'drone/' in p or '/aw-' in p or 'awaking' in p or (p in top and ('drone' in p or 'aw-' in p))
aerial=[p for p in keepers if is_aerial(p)]
print(f"keepers:{len(keepers)} | aeriens:{len(aerial)} | proscrits exclus:{len(proscrire)}")

def warm_grade(im):
    r,g,b=im.split(); r=r.point(lambda v:min(255,int(v*1.045+3))); b=b.point(lambda v:max(0,int(v*0.95-1)))
    im=Image.merge('RGB',(r,g,b)); im=ImageEnhance.Color(im).enhance(0.90)
    return ImageEnhance.Brightness(ImageEnhance.Contrast(im).enhance(1.04)).enhance(1.015)
def load(p): return ImageOps.exif_transpose(Image.open(p).convert('RGB'))
def cool(im): m=ImageStat.Stat(im).mean; return m[2]>m[0]+2
def slug(p): return re.sub(r'[^a-z0-9]+','_',p.lower()).strip('_')[:80]
def crop(im,ratio,tw,vf=.5,hf=.5):
    W,H=im.size; rw,rh=ratio; tr=rw/rh; cur=W/H
    if cur>tr: nw,nh=int(round(H*tr)),H
    else: nw,nh=W,int(round(W/tr))
    x=int((W-nw)*hf); y=int((H-nh)*vf)
    return im.crop((x,y,x+nw,y+nh)).resize((tw,int(round(tw/tr))),Image.LANCZOS)
def genpool(paths,outdir,maxside=1120,q=76):
    os.makedirs(outdir,exist_ok=True)
    for f in glob.glob(f'{outdir}/*.webp'): os.remove(f)
    n=0
    for p in paths:
        try: im=load(p)
        except: continue
        if cool(im): im=warm_grade(im)
        W,H=im.size; sc=min(1.0,maxside/max(W,H)); im=im.resize((int(W*sc),int(H*sc)),Image.LANCZOS)
        im.save(f'{outdir}/{slug(p)}.webp','WEBP',quality=q,method=6); n+=1
    return n
def slot(src,ratio,tw,out,vf=.5,hf=.5,q=80):
    if not ex(src): print('   ! manquant:',src); return
    im=load(src)
    if cool(im): im=warm_grade(im)
    crop(im,ratio,tw,vf,hf).save(f'medias/web/{out}.webp','WEBP',quality=q,method=6)

# ---- pools ----
print("POOL mosaïque:",genpool(keepers,'medias/web/pool'),"images")
print("POOL drone   :",genpool(aerial,'medias/web/pool-drone'),"images")

# ---- slots nommés (sources choisies dans tes packs) ----
BV='medias/como-beauvallon/'
SLOTS={
 'hero-grandevue':('medias/como-web/raw/hero.jpg',(16,9),1920,.5,.5),
 'hero-chateau':('medias/como-web/raw/location.jpg',(16,9),1920,.40,.5),
 'lieu-chateau':('medias/como-web/raw/location.jpg',(4,3),1280,.42,.5),
 'beach-aerial':('medias/como-web/raw/dining1.jpg',(16,9),1280,.5,.5),
 'beach-parasols':('medias/como-web/raw/exp2.jpg',(4,3),1100,.5,.5),
 'spot-aerial':('medias/como-web/raw/hero.jpg',(4,3),1280,.30,.18),
 'exp-silence':('medias/saint-tropez/Stropez_day2-11.jpg',(16,9),1280,.55,.5),
 'exp-apesanteur':(BV+'a715426f-04a3-4407-abce-65a7dffb1f08.JPG',(4,3),1280,.46,.5),
 'exp-rythme':(BV+'6f9dea10-981b-4b23-8fde-4a21f87acd52.JPG',(3,4),1000,.45,.5),
 'session-briefing':('medias/cannes/Cannes_Cote-2.jpg',(16,9),1280,.5,.5),
 'session-gear':(BV+'19a1d93b-24c7-4ce7-8e34-fc634e6ce764.JPG',(16,9),1280,.4,.5),
 'session-water':('medias/cannes/Cannes_Cote-161.jpg',(16,9),1280,.45,.5),
 'session-flight':('medias/cannes/Cannes_Cote-167.jpg',(16,9),1280,.5,.5),
 'ride-women':('medias/cannes/Cannes_Cote-155.jpg',(3,4),1000,.4,.5),
 'ride-redrock':('medias/cannes/Cannes_Cote-99.jpg',(4,3),1280,.5,.5),
 'ride-lerins-orange':('medias/iles-lerins/Post_4x5-26_First.jpg',(3,4),1000,.42,.5),
 'ride-formation':('medias/cannes/Cannes_Cote-189.jpg',(4,3),1280,.5,.5),
 'ride-esterel':('medias/esterel/Post_4x5-5.jpg',(3,4),1000,.45,.5),
 'ride-yacht':('medias/cannes/Cannes_Cote-45.jpg',(3,4),1000,.5,.5),
 'ride-esterel-vert':('medias/cannes/Cannes_Cote-96.jpg',(3,4),1000,.45,.5),
 'ride-lerins-green':('medias/iles-lerins/Post_4x5-25_Secondd.jpg',(3,4),1000,.42,.5),
 'ride-9':('medias/cannes/Cannes_Cote-90.jpg',(4,3),1280,.5,.5),
 'ride-10':('medias/cannes/Cannes_Cote-135.jpg',(3,4),1000,.42,.5),
 'ride-11':('medias/cannes/Cannes_Cote-180.jpg',(4,3),1280,.5,.5),
 'ride-12':('medias/cannes/Cannes_Cote-109.jpg',(3,4),1000,.42,.5),
 'ride-13':('medias/cannes/Cannes_Cote-73.jpg',(4,3),1280,.5,.5),
 'ride-14':('medias/cannes/Cannes_Cote-153.jpg',(3,4),1000,.42,.5),
 'who-1':('medias/cannes/Cannes_Cote-161.jpg',(4,3),1100,.45,.5),
 'who-2':('medias/cannes/Cannes_Cote-194.jpg',(4,3),1100,.5,.5),
 'who-3':(BV+'19a1d93b-24c7-4ce7-8e34-fc634e6ce764.JPG',(4,3),1100,.4,.5),
 'who-4':('medias/video-frames/drone/aw-034.6.jpg',(4,3),1100,.5,.5),
}
for name,(src,r,w,vf,hf) in SLOTS.items(): slot(src,r,w,name,vf,hf)
print("SLOTS photo:",len(SLOTS))

# ---- slots drone (édition full-drone) depuis les keepers aériens ----
land=[p for p in aerial if load(p).size[0]>=load(p).size[1]]
port=[p for p in aerial if p not in land]
land=land or aerial; port=port or aerial
DR_LAND=[('drone-lieu',(4,3),1280),('drone-exp1',(16,9),1280),('drone-exp2',(4,3),1280),
 ('drone-slide1',(16,9),1280),('drone-slide2',(16,9),1280),('drone-beach2',(4,3),1100),
 ('drone-session-1',(16,9),1280),('drone-session-2',(16,9),1280),('drone-session-3',(16,9),1280),
 ('drone-session-4',(16,9),1280),('drone-ride-2',(4,3),1280),('drone-ride-4',(4,3),1280),
 ('drone-ride-9',(4,3),1280),('drone-ride-11',(4,3),1280),('drone-ride-13',(4,3),1280),
 ('drone-who-1',(4,3),1100),('drone-who-2',(4,3),1100),('drone-who-3',(4,3),1100),('drone-who-4',(4,3),1100)]
DR_PORT=[('drone-exp3',(3,4),1000),('drone-ride-1',(3,4),1000),('drone-ride-3',(3,4),1000),
 ('drone-ride-5',(3,4),1000),('drone-ride-6',(3,4),1000),('drone-ride-7',(3,4),1000),('drone-ride-8',(3,4),1000),
 ('drone-ride-10',(3,4),1000),('drone-ride-12',(3,4),1000),('drone-ride-14',(3,4),1000)]
for i,(name,r,w) in enumerate(DR_LAND): slot(sorted(land)[i%len(land)],r,w,name)
for i,(name,r,w) in enumerate(DR_PORT): slot(sorted(port)[i%len(port)],r,w,name)
print("SLOTS drone:",len(DR_LAND)+len(DR_PORT))
