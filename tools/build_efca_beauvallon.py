#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Construit UNE page Beauvallon dans le style efoilcotedazur BLEU (index-bleu.html) :
reprend la DA EFCA (bleu #0A7FB0 + orange #F4631F, Inter, pills, efca.css) mais
centrée sur le golfe de Saint-Tropez / COMO Le Beauvallon, avec nos photos chaudes.

Sortie : como-beauvallon-efca-bleu.html  (réutilise assets/css/efca.css + assets/img/logo.webp)
"""
import re
src=open('index-bleu.html',encoding='utf-8').read()

# 1) retirer le bandeau "2 versions" + les 2 sections reels (.mov non dispo en web)
src=re.sub(r'<div class="efca-themer"[\s\S]*?</div>\s*','',src,count=1)
src=re.sub(r'\s*<!-- ===================== REEL STRIP[\s\S]*?</section>','',src,count=1)
src=re.sub(r'\s*<!-- ===================== 10\. REELS VID[\s\S]*?</section>','',src,count=1)

# 2) héros : notre boucle vidéo drone compressée
src=src.replace(
 '          <source src="assets/video/hero.mp4" type="video/mp4">\n          <source src="https://efoilcotedazur.fr/wp-content/uploads/2021/03/foil-electrique-LIFT.mp4" type="video/mp4">',
 '          <source src="medias/web/hero-video.mp4" type="video/mp4">')

# 3) médias EFCA -> nos photos Beauvallon (chaudes)
MEDIA={
 'assets/img/hero-0611-poster.webp':'medias/web/hero-video-poster.webp',
 'assets/img/cdz-12.webp':'medias/web/exp-rythme.webp',
 'assets/img/cdz-10.webp':'medias/web/session-gear.webp',
 'assets/img/cdz-05.webp':'medias/web/session-briefing.webp',
 'assets/img/step-briefing.webp':'medias/web/session-briefing.webp',
 'assets/img/step-materiel.webp':'medias/web/session-gear.webp',
 'assets/img/step-session.webp':'medias/web/session-water.webp',
 'assets/img/step-progress.webp':'medias/web/session-flight.webp',
 'assets/img/cdz-09.webp':'medias/web/exp-apesanteur.webp',
 'assets/img/cdz-03.webp':'medias/web/beach-parasols.webp',
 'assets/img/cdz-04.webp':'medias/web/ride-formation.webp',
 'assets/img/cdz-01.webp':'medias/web/ride-lerins-orange.webp',
 'assets/img/cdz-02.webp':'medias/web/hero-grandevue.webp',
 'assets/img/cdz-11.webp':'medias/web/ride-women.webp',
 'assets/img/cdz-07.webp':'medias/web/session-water.webp',
 'assets/img/cdz-08.webp':'medias/web/ride-redrock.webp',
}
for a,b in MEDIA.items(): src=src.replace(a,b)

# 4) copy : Mandelieu/baie de Cannes -> golfe de Saint-Tropez / Beauvallon (specifique d'abord)
COPY=[
 ("Location eFoil Mandelieu — Côte d'Azur | eFoil Côte d'Azur","eFoil au golfe de Saint-Tropez — COMO Le Beauvallon | eFoil Côte d'Azur"),
 ("Location & initiation eFoil à Mandelieu-la-Napoule. Débutants bienvenus, moniteur dédié, matériel Lift. Noté 5,0 ★ (230 avis Google). Session 1h dès 150 €.",
  "Sessions d'eFoil au départ du ponton du domaine COMO Le Beauvallon, golfe de Saint-Tropez. Débutants bienvenus, moniteur dédié, matériel Lift. 5,0 ★ (230 avis Google). Session 1h dès 150 €."),
 ("Location eFoil Mandelieu — Côte d'Azur","eFoil au golfe de Saint-Tropez · COMO Le Beauvallon"),
 ("Volez au-dessus de la Méditerranée.","Volez au-dessus du golfe de Saint-Tropez."),
 ("Location &amp; initiation eFoil à Mandelieu. Sensation de vol silencieux, accessible dès la première session — encadré par un moniteur.",
  "Sessions d'eFoil au départ du ponton du domaine COMO Le Beauvallon. Vol silencieux, accessible dès la première session — encadré par un moniteur."),
 ("Initiation eFoil encadrée à Mandelieu.","Sessions d'eFoil encadrées au golfe de Saint-Tropez."),
 ("Mandelieu, Plage des Dauphins, face à la baie de Cannes.","Au départ du ponton du domaine COMO Le Beauvallon, golfe de Saint-Tropez."),
 ("1ʳᵉ base de la Côte d'Azur","Au cœur du golfe"),
 ("base de la Côte d'Azur","spot du golfe"),
 ("La baie de Cannes et Mandelieu, rien que pour vos sessions.","Le golfe de Saint-Tropez, rien que pour vos sessions."),
 ("Réservez votre première session eFoil à Mandelieu et survolez la Méditerranée.",
  "Réservez votre session eFoil au départ du domaine COMO Le Beauvallon et survolez le golfe de Saint-Tropez."),
 ("Réservez votre première session eFoil à Mandelieu","Réservez votre session eFoil au départ du domaine COMO Le Beauvallon"),
 ("Plage des Dauphins, Mandelieu","Le golfe de Saint-Tropez · COMO Le Beauvallon"),
 # NAP / JSON-LD
 ("Plage des Dauphins, Bd du Midi Louise Moreau, 06150 Mandelieu-la-Napoule","Boulevard des Collines, 83310 Grimaud — ponton du domaine COMO Le Beauvallon"),
 ('"streetAddress": "Plage des Dauphins, Bd du Midi Louise Moreau"','"streetAddress": "Boulevard des Collines"'),
 ('"postalCode": "06150"','"postalCode": "83310"'),
 ('"addressLocality": "Mandelieu-la-Napoule"','"addressLocality": "Grimaud"'),
 ("06150 Mandelieu-la-Napoule","83310 Grimaud"),
 ('"latitude": "43.5260"','"latitude": "43.291"'),
 ('"longitude": "6.9380"','"longitude": "6.9380"'.replace("6.9380","6.599")),
 ("eFoil+C%C3%B4te+d%27Azur+Mandelieu-la-Napoule","COMO+Le+Beauvallon+Grimaud"),
 ("baie de Cannes","golfe de Saint-Tropez"),
 ("Mandelieu-la-Napoule","Grimaud"),
 ("à Mandelieu","au golfe de Saint-Tropez"),
 ("Mandelieu","Beauvallon"),
]
for a,b in COPY: src=src.replace(a,b)

# 5) ambiance chaude (coucher de soleil) sur toutes les images
warm=('<style>/* Ambiance chaude coucher de soleil — Beauvallon */\n'
 '.efca-hero__media img,.efca-hero__media video,.efca-feature__media img,.efca-imgwall img,'
 '.efca-media-text__img img,.efca-process__img img,.efca-cover__media img{filter:saturate(1.14) sepia(.14) brightness(1.02)}'
 '</style>\n</head>')
src=src.replace('</head>',warm,1)

# titre onglet propre
src=src.replace('<body class="theme-bleu">','<body class="theme-bleu"><!-- Style efoilcotedazur BLEU, centré golfe de Saint-Tropez / COMO Le Beauvallon -->')

open('como-beauvallon-efca-bleu.html','w',encoding='utf-8').write(src)
# garde-fous
left=src.count('assets/img/cdz')+src.count('assets/img/step')
print("como-beauvallon-efca-bleu.html écrit |",len(src.encode('utf-8'))//1024,"Ko | refs cdz/step restants:",left,
      "| 'Mandelieu' restants:",src.count('Mandelieu'),"| 'baie de Cannes' restants:",src.count('baie de Cannes'))
