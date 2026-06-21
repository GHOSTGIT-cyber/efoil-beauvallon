#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Applique le tri CONTEXTUEL (export de trieur-contextuel.html) :
chaque emplacement (slot) de la page -> son fichier WebP medias/web/<name>.webp,
régénéré depuis la photo source choisie (recadrage au bon ratio + teinte chaude).
Le héros : poster = photo choisie dans HERO_VIDEO (la vidéo reste hero-video.mp4).

⚠️ À lancer là où vivent les originaux (dossier efoilcotedazur), puis copier
medias/web/*.webp vers le worktree beauvallon, puis python tools/build_versions.py.

Usage : python tools/apply_context.py [chemin/vers/como-beauvallon-tri-contextuel.json]
"""
import json, os, sys, re
from PIL import Image, ImageOps, ImageEnhance, ImageStat

JSONP = sys.argv[1] if len(sys.argv) > 1 else 'como-beauvallon-tri-contextuel.json'
J = json.load(open(JSONP, encoding='utf-8'))
slots_in = J['slots']

# ctx slot -> (webp name, ratio, largeur, vf, hf)   (ratios/largeurs alignés sur build_versions)
SLOT_MAP = {
 'HERO_VIDEO':('hero-video-poster',(16,9),1920,.42,.5),
 'LIEU':('lieu-chateau',(4,3),1280,.42,.5),
 'EXP_1':('exp-silence',(16,9),1280,.50,.5),
 'EXP_2':('exp-apesanteur',(4,3),1280,.46,.5),
 'EXP_3':('exp-rythme',(3,4),1000,.45,.5),
 'WHO_1':('who-1',(4,3),1100,.45,.5),
 'WHO_2':('who-2',(4,3),1100,.50,.5),
 'WHO_3':('who-3',(4,3),1100,.40,.5),
 'WHO_4':('who-4',(4,3),1100,.50,.5),
 'RIDE_1':('ride-women',(3,4),1000,.40,.5),
 'RIDE_2':('ride-redrock',(4,3),1280,.50,.5),
 'RIDE_3':('ride-lerins-orange',(3,4),1000,.42,.5),
 'RIDE_4':('ride-formation',(4,3),1280,.50,.5),
 'RIDE_5':('ride-esterel',(3,4),1000,.45,.5),
 'RIDE_6':('ride-yacht',(3,4),1000,.50,.5),
 'RIDE_7':('ride-esterel-vert',(3,4),1000,.45,.5),
 'RIDE_8':('ride-lerins-green',(3,4),1000,.42,.5),
 'RIDE_9':('ride-9',(4,3),1280,.50,.5),
 'RIDE_10':('ride-10',(3,4),1000,.42,.5),
 'RIDE_11':('ride-11',(4,3),1280,.50,.5),
 'RIDE_12':('ride-12',(3,4),1000,.42,.5),
 'RIDE_13':('ride-13',(4,3),1280,.50,.5),
 'RIDE_14':('ride-14',(3,4),1000,.42,.5),
 'SESSION_1':('session-briefing',(16,9),1280,.50,.5),
 'SESSION_2':('session-gear',(16,9),1280,.40,.5),
 'SESSION_3':('session-water',(16,9),1280,.45,.5),
 'SESSION_4':('session-flight',(16,9),1280,.50,.5),
 'BEACH_1':('beach-aerial',(16,9),1280,.50,.5),
 'BEACH_2':('beach-parasols',(4,3),1100,.50,.5),
 'SPOT':('spot-aerial',(4,3),1280,.40,.5),
}

def warm_grade(im):
    r,g,b=im.split(); r=r.point(lambda v:min(255,int(v*1.045+3))); b=b.point(lambda v:max(0,int(v*0.95-1)))
    im=Image.merge('RGB',(r,g,b)); im=ImageEnhance.Color(im).enhance(0.90)
    return ImageEnhance.Brightness(ImageEnhance.Contrast(im).enhance(1.04)).enhance(1.015)
def load(p): return ImageOps.exif_transpose(Image.open(p).convert('RGB'))
def cool(im): m=ImageStat.Stat(im).mean; return m[2]>m[0]+2
def crop(im,ratio,tw,vf=.5,hf=.5):
    W,H=im.size; rw,rh=ratio; tr=rw/rh; cur=W/H
    if cur>tr: nw,nh=int(round(H*tr)),H
    else: nw,nh=W,int(round(W/tr))
    x=int((W-nw)*hf); y=int((H-nh)*vf)
    return im.crop((x,y,x+nw,y+nh)).resize((tw,int(round(tw/tr))),Image.LANCZOS)

os.makedirs('medias/web', exist_ok=True)
done=0; miss=[]
for ctx,(name,r,w,vf,hf) in SLOT_MAP.items():
    srcs=slots_in.get(ctx) or []
    if not srcs: miss.append((ctx,'(vide)')); continue
    src=srcs[0]
    if not os.path.exists(src): miss.append((ctx,src)); continue
    im=load(src)
    if cool(im): im=warm_grade(im)
    crop(im,r,w,vf,hf).save(f'medias/web/{name}.webp','WEBP',quality=82,method=6)
    done+=1
print(f"slots régénérés : {done}/{len(SLOT_MAP)}")
for c,s in miss: print("  ! manquant/vide:",c,s)

# pool mosaïque défilante : photos choisies dans GALERIE_DEFILE
# --enrich-pool : on ajoute TOUS les autres keepers de packs.json (hors proscrits), tes 5 en tête.
defile=[p for p in slots_in.get('GALERIE_DEFILE',[]) if os.path.exists(p)]
if '--enrich-pool' in sys.argv and os.path.exists('tools/packs.json'):
    pk=json.load(open('tools/packs.json',encoding='utf-8'))['packs']
    pros=set(J.get('proscrire',[])) | set(pk.get('proscrire',[]))
    extra=[]
    for cid,lst in pk.items():
        if cid=='proscrire': continue
        for p in lst:
            if p in pros or p in defile or p in extra or not os.path.exists(p): continue
            extra.append(p)
    defile = defile + extra
if defile:
    import glob
    def slug(p): return re.sub(r'[^a-z0-9]+','_',p.lower()).strip('_')[:80]
    os.makedirs('medias/web/pool', exist_ok=True)
    for f in glob.glob('medias/web/pool/*.webp'): os.remove(f)
    for p in defile:
        im=load(p)
        if cool(im): im=warm_grade(im)
        W,H=im.size; sc=min(1.0,1120/max(W,H)); im=im.resize((int(W*sc),int(H*sc)),Image.LANCZOS)
        im.save(f'medias/web/pool/{slug(p)}.webp','WEBP',quality=76,method=6)
    # fallbacks no-JS des deux mosaïques
    crop(load(defile[0]),(16,9),1280,.5,.5).save('medias/web/breath-sunset.webp','WEBP',quality=80,method=6)
    crop(load(defile[min(1,len(defile)-1)]),(16,9),1280,.5,.5).save('medias/web/breath-golfe.webp','WEBP',quality=80,method=6)
    print(f"pool mosaïque (GALERIE_DEFILE) : {len(defile)} photos")
else:
    print("pool mosaïque : inchangé (GALERIE_DEFILE vide)")
