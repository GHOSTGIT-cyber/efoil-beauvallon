# PROMPT DE REPRISE — Site eFoil **COMO Le Beauvallon** (dépôt autonome)

Colle ce prompt en début de nouvelle session. **Lis-le en entier** : la mémoire auto ne suit pas ce dossier.

---

## ⚠️ Nouveau (2026-06-21) — ce dossier est désormais un DÉPÔT GIT AUTONOME

- **Fini les worktrees / la branche partagée.** Ce dossier a son **propre `.git`** indépendant.
- **Dossier** : `D:\efoil_sites\beauvallon`
- **Branche** : `main` · **1er commit** : `init: site Beauvallon autonome` (`0ff0e13`)
- **Pas de remote GitHub** pour l'instant (à créer quand on voudra déployer).
- Les anciens liens de preview `raw.githack.com/.../efoilcotedazur/beauvallon/...` **ne marchent plus** (la branche a été supprimée). Preview = serveur local pour l'instant.
- ⚠️ **Vidéos hors git** : `assets/video/` (207 Mo : `hero.mp4` + reels `.mov`) est dans `.gitignore`. Les fichiers sont sur disque mais **pas suivis par git**. Avant tout déploiement via git, décider de l'hébergement vidéo (**Git LFS**, CDN, ou compression webm légère).

### Règles git (simples maintenant)
```
git branch --show-current   # doit afficher : main
git add <fichiers> && git commit -m "..."
# pas de pull/push tant qu'il n'y a pas de remote
```

---

## Le site

**eFoil au golfe de Saint-Tropez**, sessions encadrées **au départ du ponton du domaine COMO Le Beauvallon** (Grimaud `83310`, Bd des Collines, géo ≈ `43.291, 6.599`).

> **COMO = marque tierce.** Mention « au départ du ponton du domaine COMO Le Beauvallon » **sans logo ni co-marque**. Droits d'usage du **nom et des visuels COMO** (château, beach club, aérien) à **clearer avant mise en ligne publique**.

### Direction artistique (DA v2.1 — continuité COMO beach-club, chaude)
- Fonds **crème / sable**, ambiance **summer / golden hour**.
- Accent **terracotta `#cf5836`** (CTA, signature) + **jaune-soleil `#e0a92e`** (parasols).
- **Zéro bleu en aplat.** Sombre limité au **warm espresso `#2b2419`** (réservation + footer).
- Turquoise Lift réduit à **un seul glint discret**.
- Typo : **Archivo Expanded** (titres) + **Switzer** (corps), self-host woff2 → à déposer dans `assets/fonts/`.

---

## Fichiers présents (HTML uniquement Beauvallon)

| Fichier | Rôle | Statut |
|---|---|---|
| `como-beauvallon-v1-coucher-de-soleil.html` | Édition **V1**, héros vidéo drone coucher de soleil | ⭐ **base retenue** |
| `como-beauvallon-v2-le-domaine.html` | Héros = vue aérienne château + golfe | à fusionner/supprimer |
| `como-beauvallon-v3-escapade.html` | Héros = château, ordre des blocs revu | à fusionner/supprimer |
| `como-beauvallon-v4-full-drone.html` | Tout aérien (mosaïques drone) | à puiser dedans |
| `como-beauvallon-v5-como.html` | Palette claire, typo fine | à fusionner/supprimer |
| `como-beauvallon-efca-bleu.html` | Style EFCA bleu | ❌ **abandonné** |
| `como-beauvallon-efoil.html` | **Template** (placeholders `MEDIA_*`) générant les éditions | conservé |
| `reservation-beauvallon.html` | Réservation : formulaire → confirmation, **sans paiement** | ✅ |
| `trieur-photos.html` / `trieur-contextuel.html` | Outils de tri des photos par slots + annotations | ✅ |
| `como-beauvallon-efoil-LIVRABLE.md` | Doc livrable détaillée (fonts, slots, JSON-LD, intégration WP) | **à lire** |

### Médias & pipeline (`tools/`)
- `medias/` = sources brutes (originaux lourds **gitignorés**) ; `medias/web/` = dérivés WebP optimisés (seul dossier destiné au web).
- Pipeline reproductible : `python tools/apply_packs.py` (lit `tools/packs.json` = ta curation) → `python tools/build_versions.py` (régénère les éditions) ; `python tools/build_sorter.py` (régénère le trieur).

---

## À FAIRE ensuite (ordre)
1. **Trier les photos** dans `trieur-photos.html` (chaque photo dans son slot, double-clic = agrandir + annoter) → **exporter le JSON**.
2. **Finaliser V1** en version unique : bonnes photos aux bons slots (JSON), plans drone retenus, **galeries en défilement auto** (plus de scroll horizontal manuel), toutes les photos exploitées.
3. **Supprimer les autres éditions** (V2/V3/V4/V5 + efca-bleu), ne garder qu'une version.
4. **Réservation** : brancher le formulaire sur un vrai backend (REST WP / CPT `reservation` / Odoo / email) — aujourd'hui front-only.
5. **Remplir les tokens `{{…}}`** : `{{TÉLÉPHONE}}`/E164, `{{PRIX}}`, `{{ÂGE_MINI}}`, `{{HORAIRES}}`, `{{NOTE}}`/`{{NB_AVIS}}`, `{{AVIS_1..3}}` (Google réels), `{{LIEN_INSTAGRAM}}`/`{{LIEN_FICHE_GOOGLE}}`, `{{MODELE_LIFT}}`, n° de voie Bd des Collines. Détail dans le LIVRABLE.
6. **Clearer les droits images COMO** avant prod publique.

## Preview locale
```
cd D:\efoil_sites\beauvallon
python -m http.server 8000
# http://localhost:8000/como-beauvallon-v1-coucher-de-soleil.html
# http://localhost:8000/reservation-beauvallon.html
```

## Déploiement (plus tard)
Créer un repo GitHub dédié → `git remote add origin <url>` → push. Si GitHub Pages : régler d'abord l'hébergement des vidéos (LFS/CDN), sinon le site déployé n'aura pas la vidéo héros.

## Note
`11+Agents+SEO+_+GEO+-+RosoAI/` = squad d'agents SEO/GEO (copie locale, suivie par git).
