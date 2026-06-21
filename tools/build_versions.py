#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Génère les éditions de la landing eFoil COMO Le Beauvallon depuis le template,
en câblant les slots MEDIA_*, en injectant le POOL (galerie auto) et en
réordonnant les blocs pour V3.

Usage : python tools/build_versions.py   (après tools/optimize_media.py)
"""
import re, os, glob, json
from PIL import Image

BASE = 'como-beauvallon-efoil.html'
base = open(BASE, encoding='utf-8').read()

def dims(name):
    with Image.open(f'medias/web/{name}.webp') as im: return im.size
def esc(s): return s.replace('"', '&quot;')

def img_fill(name, alt, lazy=True):
    w,h=dims(name); l=' loading="lazy" decoding="async"' if lazy else ' fetchpriority="high" decoding="async"'
    return f'<img class="cb-fill" src="medias/web/{name}.webp" width="{w}" height="{h}"{l} alt="{esc(alt)}">'
def img_media(name, ratio, alt):
    w,h=dims(name)
    return (f'<img class="cb-media cb-ratio-{ratio}" src="medias/web/{name}.webp" '
            f'width="{w}" height="{h}" loading="lazy" decoding="async" alt="{esc(alt)}">')
def slide_fallback(name, alt):
    w,h=dims(name)
    return (f'<img class="cb-mosaic__fallback" src="medias/web/{name}.webp" '
            f'width="{w}" height="{h}" loading="lazy" decoding="async" alt="{esc(alt)}">')
def video_fill(alt):
    w,h=dims('hero-video-poster')
    return (f'<video class="cb-fill" muted loop playsinline preload="metadata" '
            f'poster="medias/web/hero-video-poster.webp" width="{w}" height="{h}" data-cb-autoplay '
            f'aria-label="{esc(alt)}"><source src="medias/web/hero-video.mp4" type="video/mp4"></video>')

def replace_slot(html, tag, markup):
    pat = re.compile(r'<div class="cb-ph[^"]*"[^>]*>\s*<div class="cb-ph__inner">'
                     r'<span class="cb-ph__tag">' + re.escape(tag) + r'</span>.*?</div>\s*</div>', re.DOTALL)
    html, n = pat.subn(lambda m: markup, html, count=1)
    assert n == 1, f"slot {tag}: {n} remplacement(s)"
    return html

# ---- réordonnancement des blocs (sections délimitées par les commentaires ══ LABEL ══) ----
def _keyof(label):
    L=label.upper()
    if 'AUTO #1' in L: return 'slide1'
    if 'AUTO #2' in L: return 'slide2'
    if 'HERO' in L: return 'hero'
    if 'LIEU' in L: return 'lieu'
    if 'EXP' in L: return 'exp'
    if 'POUR QUI' in L: return 'pourqui'
    if 'SPOT' in L: return 'spot'
    if 'GALERIE' in L: return 'gallery'
    if 'DÉROUL' in L or 'DEROUL' in L: return 'deroule'
    if 'BEACH' in L: return 'beach'
    if 'PREUVE' in L: return 'proof'
    if 'RÉSERV' in L or 'RESERV' in L: return 'reserver'
    if 'FAQ' in L: return 'faq'
    if 'FOOTER' in L: return 'footer'
    return 'unknown'

def reorder(html, order):
    marks=[(m.start(), m.group(1).strip()) for m in re.finditer(r'<!-- ═{6,} (.+?) ═{6,}', html)]
    if not marks: return html
    keys=[_keyof(l) for _,l in marks]
    starts=[s for s,_ in marks]+[len(html)]
    chunks={keys[i]: html[starts[i]:starts[i+1]] for i in range(len(marks))}
    pos={keys[i]:i for i in range(len(marks))}
    if 'lieu' not in pos or 'footer' not in pos: return html
    il, ifoot = pos['lieu'], pos['footer']
    middle=[keys[i] for i in range(il, ifoot)]
    if set(order)!=set(middle):
        print("   ! reorder ignoré (clés:", set(middle)^set(order), ")"); return html
    return html[:starts[il]] + ''.join(chunks[k] for k in order) + html[starts[ifoot]:]

ALT = {
 'hero-grandevue':"Vue aérienne du domaine COMO Le Beauvallon : le palace Belle Époque, la pinède, la plage et le ponton sur le golfe.",
 'hero-chateau':"Le palace Belle Époque du domaine COMO Le Beauvallon dans la pinède, au coucher du soleil, au-dessus du golfe.",
 'lieu-chateau':"Le palace Belle Époque du domaine COMO Le Beauvallon, dans les pins, au coucher du soleil.",
 'beach-aerial':"Vue aérienne du beach club du domaine : sable, parasols dorés et eau turquoise.",
 'beach-parasols':"Les parasols dorés du beach club face au golfe.",
 'spot-aerial':"Vue aérienne du domaine COMO Le Beauvallon : l'hôtel Belle Époque, la plage et le golfe de Saint-Tropez.",
 'who-1':"Débutant accompagné par un moniteur lors de ses premiers vols.","drone-who-1":"Vue aérienne : un rider accompagné sur le golfe.",
 'who-2':"Rider confirmé en session libre sur le golfe.","drone-who-2":"Vue aérienne : rider en session libre.",
 'who-3':"Encadrement et sécurité : briefing et matériel.","drone-who-3":"Vue aérienne du plan d'eau et des riders.",
 'who-4':"Matériel Lift : foils électriques en carbone.","drone-who-4":"Vue aérienne : détail d'un rider en vol.",
 'ride-9':"Riders sur le golfe.",'ride-10':"Rider en vol.",'ride-11':"Riders et yachts au mouillage.",
 'ride-12':"Rider sur l'eau calme.",'ride-13':"Roche rouge de l'Estérel.",'ride-14':"Rider à la golden hour.",
 'exp-silence':"Des riders glissent en silence sur le golfe au coucher du soleil.",
 'exp-apesanteur':"Deux riders portés par leur aile au-dessus du golfe, devant le domaine.",
 'exp-rythme':"Un moniteur accompagne un débutant lors de ses premiers vols.",
 'breath-sunset':"Vue drone : des riders en eFoil sur le golfe au coucher du soleil.",
 'breath-golfe':"Riders en vol au-dessus du golfe.",
 'ride-women':"Deux rideuses en eFoil sur l'eau calme, reflets du matin.",
 'ride-redrock':"Trois riders en vol devant les roches rouges.",
 'ride-lerins-orange':"Rider sur une planche Lift orange devant le fort de Sainte-Marguerite.",
 'ride-formation':"Riders en formation au-dessus du golfe.",
 'ride-esterel':"Couple partageant une planche, en vol devant le massif rouge de l'Estérel.",
 'ride-yacht':"Riders en eFoil devant le port et ses yachts.",
 'ride-esterel-vert':"Riders au pied des roches rouges de l'Estérel.",
 'ride-lerins-green':"Rideuse souriante en vol sur une planche Lift verte.",
 'session-briefing':"Briefing au ponton : prise en main de la télécommande.",
 'session-gear':"Équipement : planches Lift et télécommandes.",
 'session-water':"Premiers mètres à l'eau, accompagné d'un moniteur.",
 'session-flight':"Le vol : la planche s'élève au-dessus du golfe.",
}
A=lambda n: ALT.get(n, "Vue aérienne par drone : le golfe de Saint-Tropez, la côte et les riders en eFoil.")
VIDEO_ALT="Vue drone au coucher du soleil : des riders en eFoil glissent sur le golfe de Saint-Tropez."

COMMON=[
 ('MEDIA_LIEU',     lambda: img_media('lieu-chateau','43',A('lieu-chateau'))),
 ('MEDIA_BEACH_1',  lambda: img_media('beach-aerial','169',A('beach-aerial'))),
 ('MEDIA_BEACH_2',  lambda: img_media('beach-parasols','43',A('beach-parasols'))),
 ('MEDIA_EXP_1',    lambda: img_media('exp-silence','169',A('exp-silence'))),
 ('MEDIA_EXP_2',    lambda: img_media('exp-apesanteur','43',A('exp-apesanteur'))),
 ('MEDIA_EXP_3',    lambda: img_media('exp-rythme','34',A('exp-rythme'))),
 ('MEDIA_SLIDE_1',  lambda: slide_fallback('breath-sunset',A('breath-sunset'))),
 ('MEDIA_SLIDE_2',  lambda: slide_fallback('breath-golfe',A('breath-golfe'))),
 ('MEDIA_SESSION_1',lambda: img_media('session-briefing','169',A('session-briefing'))),
 ('MEDIA_SESSION_2',lambda: img_media('session-gear','169',A('session-gear'))),
 ('MEDIA_SESSION_3',lambda: img_media('session-water','169',A('session-water'))),
 ('MEDIA_SESSION_4',lambda: img_media('session-flight','169',A('session-flight'))),
 ('MEDIA_SPOT',     lambda: img_media('spot-aerial','43',A('spot-aerial'))),
 ('MEDIA_WHO_1',    lambda: img_media('who-1','43',A('who-1'))),
 ('MEDIA_WHO_2',    lambda: img_media('who-2','43',A('who-2'))),
 ('MEDIA_WHO_3',    lambda: img_media('who-3','43',A('who-3'))),
 ('MEDIA_WHO_4',    lambda: img_media('who-4','43',A('who-4'))),
]
GALLERY=['ride-women','ride-redrock','ride-lerins-orange','ride-formation',
         'ride-esterel','ride-yacht','ride-esterel-vert','ride-lerins-green',
         'ride-9','ride-10','ride-11','ride-12','ride-13','ride-14']
GAL_RATIOS=['34','43','34','43','34','34','34','34','43','34','43','34','43','34']

# ---- Édition FULL DRONE : slots aériens distincts (drone-*) + pool aérien ----
DRONE_COMMON=[
 ('MEDIA_LIEU',     lambda: img_media('drone-lieu','43',A('drone-lieu'))),
 ('MEDIA_BEACH_1',  lambda: img_media('beach-aerial','169',A('beach-aerial'))),   # beach club COMO vu du ciel
 ('MEDIA_BEACH_2',  lambda: img_media('drone-beach2','43',A('drone-beach2'))),
 ('MEDIA_EXP_1',    lambda: img_media('drone-exp1','169',A('drone-exp1'))),
 ('MEDIA_EXP_2',    lambda: img_media('drone-exp2','43',A('drone-exp2'))),
 ('MEDIA_EXP_3',    lambda: img_media('drone-exp3','34',A('drone-exp3'))),
 ('MEDIA_SLIDE_1',  lambda: slide_fallback('drone-slide1',A('drone-slide1'))),
 ('MEDIA_SLIDE_2',  lambda: slide_fallback('drone-slide2',A('drone-slide2'))),
 ('MEDIA_SESSION_1',lambda: img_media('drone-session-1','169',A('drone-session-1'))),
 ('MEDIA_SESSION_2',lambda: img_media('drone-session-2','169',A('drone-session-2'))),
 ('MEDIA_SESSION_3',lambda: img_media('drone-session-3','169',A('drone-session-3'))),
 ('MEDIA_SESSION_4',lambda: img_media('drone-session-4','169',A('drone-session-4'))),
 ('MEDIA_SPOT',     lambda: img_media('spot-aerial','43',A('spot-aerial'))),
 ('MEDIA_WHO_1',    lambda: img_media('drone-who-1','43',A('drone-who-1'))),
 ('MEDIA_WHO_2',    lambda: img_media('drone-who-2','43',A('drone-who-2'))),
 ('MEDIA_WHO_3',    lambda: img_media('drone-who-3','43',A('drone-who-3'))),
 ('MEDIA_WHO_4',    lambda: img_media('drone-who-4','43',A('drone-who-4'))),
]
GALLERY_DRONE=['drone-ride-1','drone-ride-2','drone-ride-3','drone-ride-4',
               'drone-ride-5','drone-ride-6','drone-ride-7','drone-ride-8',
               'drone-ride-9','drone-ride-10','drone-ride-11','drone-ride-12','drone-ride-13','drone-ride-14']

V3_ORDER=['exp','slide1','lieu','gallery','deroule','beach','slide2','pourqui','proof','reserver','faq','spot']

EDITIONS={
 'v1-coucher-de-soleil': dict(label="Coucher de soleil", hero=('video',None)),
 'v2-le-domaine':        dict(label="Le domaine",        hero=('img','hero-grandevue')),
 'v3-escapade':          dict(label="Escapade",          hero=('img','hero-chateau'), order=V3_ORDER),
 'v4-full-drone':        dict(label="Full drone",        hero=('video',None),
                              media=DRONE_COMMON, gallery=GALLERY_DRONE, pooldir='pool-drone'),
 'v5-como':              dict(label="COMO",              hero=('img','hero-chateau'), theme='cb-como'),
}

def pool_script(dirn):
    pl=sorted(p.replace('\\','/') for p in glob.glob(f'medias/web/{dirn}/*.webp'))
    return '<script>window.CB_POOL='+json.dumps(pl, ensure_ascii=False)+';</script>\n', len(pl)

if __name__=='__main__':
    for key,cfg in EDITIONS.items():
        media=cfg.get('media',COMMON); gallery=cfg.get('gallery',GALLERY); pooldir=cfg.get('pooldir','pool')
        h=base
        if cfg.get('order'): h=reorder(h, cfg['order'])
        h=h.replace('<title>eFoil au golfe de Saint-Tropez — sessions au départ du domaine COMO Le Beauvallon</title>',
                    f'<title>eFoil · COMO Le Beauvallon — golfe de Saint-Tropez · Édition {cfg["label"]}</title>')
        h=h.replace('cb-lieu__fig cb-parallax','cb-lieu__fig').replace('cb-beach__fig cb-parallax cb-fade','cb-beach__fig cb-fade')
        if cfg.get('theme'): h=h.replace('<div class="cb-root" id="cb-top">','<div class="cb-root '+cfg['theme']+'" id="cb-top">',1)
        kind,name=cfg['hero']
        h=replace_slot(h,'MEDIA_HERO_VIDEO', video_fill(VIDEO_ALT) if kind=='video' else img_fill(name,A(name),lazy=False))
        for tag,fn in media: h=replace_slot(h,tag,fn())
        for i,(nm,rt) in enumerate(zip(gallery,GAL_RATIOS),1):
            h=replace_slot(h,f'MEDIA_RIDE_{i}', img_media(nm,rt,A(nm)))
        ps,npool=pool_script(pooldir)
        h=h.replace('<!-- ══ GSAP + ScrollTrigger', ps+'<!-- ══ GSAP + ScrollTrigger', 1)
        out=f'como-beauvallon-{key}.html'; open(out,'w',encoding='utf-8').write(h)
        left=len(re.findall(r'cb-ph__tag">MEDIA_', h))
        print(f"  -> {out}   pool:{npool}  MEDIA restants:{left}")
