# Récap session — Landing eFoil **COMO Le Beauvallon**

> **Branche : `beauvallon`** — worktree dédié à **`D:\efoil_sites\beauvallon`** (migré depuis `main` le 2026-06-13). Dépôt partagé par 3 sessions → toujours vérifier `git branch` avant de travailler ; la session Croix-Valmer est sur `croix-valmer-landings` (`D:\efoil_sites\croix-valmer`).
> **Dernier commit :** `bd70653` (base commune avec `main` au moment de la migration).

---

## 1. Ce qui existe (fichiers livrés)

### Pages (à la racine)
| Fichier | Rôle | Statut |
|---|---|---|
| `como-beauvallon-v1-coucher-de-soleil.html` | Édition **V1** — héros **vidéo drone** coucher de soleil | ⭐ **base retenue** |
| `como-beauvallon-v2-le-domaine.html` | Héros = grande vue aérienne (château + golfe) | à fusionner/supprimer |
| `como-beauvallon-v3-escapade.html` | Héros = château + ordre des blocs revu | à fusionner/supprimer |
| `como-beauvallon-v4-full-drone.html` | Tout aérien (mosaïques 100 % drone) — **photos appréciées** | à puiser dedans |
| `como-beauvallon-v5-como.html` | Palette claire, typo fine, grandes images | à fusionner/supprimer |
| `como-beauvallon-efca-bleu.html` | Style efoilcotedazur bleu | ❌ **abandonné** (jugé moche) |
| `como-beauvallon-efoil.html` | **Template** (placeholders MEDIA_*) qui génère les éditions | conservé |
| `reservation-beauvallon.html` | **Page réservation** : formulaire → confirmation, **sans paiement** | ✅ neuf |
| `trieur-photos.html` | **Trieur de photos** par emplacements (slots) + annotations | ✅ refait |
| `como-beauvallon-efoil-LIVRABLE.md` | Doc livrable (fonts, slots, JSON-LD) | conservé |

### Médias
- `medias/` = sources brutes (cannes, saint-tropez, iles-lerins, esterel, como-beauvallon, **como-web** = visuels COMO téléchargés, **video-frames** = frames extraites des vidéos). **Originaux lourds gitignorés.**
- `medias/web/` = **dérivés WebP optimisés** (73 slots nommés + `pool/` **96** keepers + `pool-drone/` **36** aériens + `hero-video.mp4` 11,7 Mo + posters). **Seul ce dossier part en ligne.**
- `medias/thumbs/` = vignettes du trieur.

### Outils (`tools/`, pipeline reproductible)
| Script | Fait quoi |
|---|---|
| `optimize_media.py` | (legacy) recadre + grade chaud les sources nommées |
| `apply_packs.py` | **lit `tools/packs.json`** (ton tri) → régénère `medias/web/` (slots + pools) en **excluant « à proscrire »** |
| `drone_slots.py` | génère les slots/pool aériens (édition full-drone) |
| `build_versions.py` | génère les **éditions** depuis le template (slots, pool injecté, ordre V3, thème V5) |
| `build_sorter.py` | génère le **trieur** (vignettes + catégories=slots + annotations + export JSON) |
| `build_efca_beauvallon.py` | (abandonné) adaptait `index-bleu.html` en Beauvallon |
| `tools/packs.json` | **ton tri exporté** (packs par catégorie) — source de vérité de la curation |

---

## 2. Direction artistique (où on en est)

- **Base = V1** : DA chaude « COMO beach-club », héros = **boucle vidéo drone coucher de soleil**.
- **Teinte chaude COMO** sur toutes les photos via la variable CSS `--cb-warm` (réglable d'un cran).
- Palette : crème/sable, accent **terracotta**, secondaire **or**, sombre = espresso (booking/footer). **Zéro bleu** en aplat (le bleu/teal et le style EFCA bleu ont été écartés).
- Typo : **Archivo Expanded** (titres ultra-light capitales) + **Switzer** (corps), self-host woff2.
- Photos curées depuis **ton tri** (`packs.json`) : château/grande vue/beach **COMO**, pack **pédagogue** pour le déroulé, pépites/aérien/rider/roche rouge/yachts en galerie. **19 « à proscrire » exclus partout.**

---

## 3. À FAIRE ensuite (ordre)

1. **Tu tries** dans `trieur-photos.html` : chaque photo dans son **slot** (Héros, Lieu, Beach aérien/parasols, Exp. silence/apesanteur/rythme, Pour qui 1→4, Déroulé 1→4, Le spot, **Galerie qui défile**, À proscrire). **Double-clic = agrandir + annoter.** → **Exporter le JSON et me l'envoyer.**
2. Je **finalise V1** (version unique) avec : les **bonnes photos aux bons endroits** (ton JSON), les **plans drone** que tu aimes, et **toutes les galeries qui défilent toutes seules** (plus aucune zone à scroll horizontal manuel) en **exploitant toutes les photos**.
3. Je **supprime les autres éditions** (V2/V3/V4/V5 + efca-bleu) pour ne garder qu'**une version**.
4. **Réservation** : brancher le formulaire sur un vrai backend (REST WordPress / CPT `reservation` / Odoo / email) — aujourd'hui front-only, sans paiement.
5. Tokens `{{…}}` à remplir (téléphone, prix, avis Google réels, modèle Lift, n° de voie). Droits images **COMO** à clearer avant prod publique.

---

## 4. Liens

**Local (serveur `python -m http.server 8000`) :**
- Trieur : http://localhost:8000/trieur-photos.html
- V1 : http://localhost:8000/como-beauvallon-v1-coucher-de-soleil.html
- Réservation : http://localhost:8000/reservation-beauvallon.html

**En ligne (githack `beauvallon`) :** `https://raw.githack.com/GHOSTGIT-cyber/efoilcotedazur/beauvallon/<fichier>.html` — ⚠️ ne marchera qu'**après push** de la branche `beauvallon` (pas encore poussée).

---

## 5. Notes opérationnelles
- **Toujours `git branch --show-current` avant d'agir.** Rester sur `beauvallon` (worktree `D:\efoil_sites\beauvallon`). Ne pas régénérer sur `croix-valmer-landings`.
- **Ne jamais committer les originaux lourds** (>100 Mo = rejet GitHub) : `.gitignore` exclut les dossiers sources ; seul `medias/web/` part en ligne.
- **Toujours fournir 2 liens** : local (serveur) + en ligne (githack).
- Reproductible : `python tools/apply_packs.py` puis `python tools/build_versions.py` (+ `build_sorter.py` pour le trieur).
