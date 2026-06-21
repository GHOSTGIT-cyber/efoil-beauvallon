POLICES — Inter auto-hébergée (zéro Google Fonts bloquant)
==========================================================

Déposer ici les 4 fichiers .woff2 attendus par efca.css (et par le preload du <head>) :

  inter-400.woff2   (Regular  — corps de texte)
  inter-600.woff2   (SemiBold — labels / boutons secondaires)
  inter-700.woff2   (Bold     — titres, CTA)    <-- préchargé dans index.html
  inter-900.woff2   (Black    — logo, gros chiffre note 5,0)

Où récupérer Inter (licence SIL Open Font License, libre d'usage web) :
  - https://github.com/rsms/inter  (dossier "web" → fichiers .woff2)
  - ou rsms.me/inter

Sous-set conseillé pour la perf : générer un subset latin (glyphes FR) via
fonttools/glyphhanger pour réduire le poids (~30–50 Ko par graisse).

IMPORTANT
- Tant que les fichiers ne sont pas déposés, le site reste 100 % fonctionnel :
  la stack système (system-ui / Segoe UI / Roboto…) prend le relais grâce au
  fallback défini dans le token --efca-font-base. Inter se chargera ensuite en
  font-display:swap (pas de blocage du rendu).
- Si la licence Inter pose problème, supprimer les @font-face dans efca.css et
  le <link rel="preload"> de la police dans index.html : la stack système suffit.
