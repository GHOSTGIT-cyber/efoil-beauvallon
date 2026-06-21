# efoilcotedazur.fr — one-page HTML pur

Refonte one-page de la base de location eFoil de Mandelieu, en **HTML/CSS/JS pur**
(WordPress neutralisé : zéro builder, zéro Gutenberg, zéro Kadence sur cette page).
DA répliquée de foilinparis.fr via [`efca-tokens.css`](efca-tokens.css) /
[`efca-build-spec.md`](efca-build-spec.md).

> ⚠️ **Local d'abord. BACKUP avant tout push. Ne pas toucher la prod ni la DB.**
> Ce dépôt livre du **code + des instructions** — rien n'est déployé ni désactivé
> automatiquement.

---

## Arborescence

```
.
├── index.html                      # la one-page (CSS critique inliné + SEO + JSON-LD)
├── assets/
│   ├── css/efca.css                # feuille complète (tokens + composants + sections)
│   ├── js/efca.js                  # JS vanilla : carrousel avis, reveal, année, hooks CTA
│   ├── fonts/README.txt            # déposer ici inter-400/600/700/900.woff2
│   └── img/                        # médias réels efoilcotedazur.fr (WebP)
│       ├── hero-poster.webp        # poster vidéo héro (LCP)
│       ├── encadrement.webp        # photo blob + carte "Encadré"
│       └── gallery-1/2/3.webp      # cartes Expérience + galerie hublots
├── wordpress/
│   ├── page-efca.php               # template "canvas vierge" (Option B)
│   └── functions-dequeue-snippet.php
├── efca-tokens.css                 # (entrée de spec) tokens DA
├── efca-build-spec.md              # (entrée de spec) structure section par section
└── README.md
```

---

## Tunnel de réservation + paiement simulé (DÉMO)
Le bouton « Réserver » mène à **`reservation.html`** (formulaire → paiement **simulé**
→ succès), avec back WordPress (CPT + REST + e-mail + admin) et stub Stripe.
Tout est documenté dans **[`README-DEMO.md`](README-DEMO.md)** — flag unique
`EFCA_PAYMENT_MODE` = `simulation` | `off` | `stripe`.

---

## Deux options d'intégration

### Option A — Autonome (recommandée si l'install le permet)
100 % statique. Aucun PHP.

1. Via **SFTP** (OVH = SFTP only, pas de SSH), envoyer `index.html` + le dossier
   `assets/` à l'emplacement servi (racine du site, ou un sous-dossier dédié).
2. Vérifier l'URL. Les chemins d'assets sont **relatifs** → fonctionnent tels quels.

### Option B — Dans WordPress (template canvas vierge)
WP allégé, slug conservé via une page d'accueil dédiée.

1. Copier `wordpress/page-efca.php` → `wp-content/themes/<child>/page-efca.php`.
2. Copier `index.html` + `assets/` → `wp-content/themes/<child>/efca/`.
3. Admin → page d'accueil → **Attributs de page → Modèle = "EFCA Canvas"**.
4. **Réglages → Lecture →** page d'accueil = cette page (slug « / » conservé).
5. `page-efca.php` sert le HTML **sans `wp_head()`/`wp_footer()`** → aucun
   style/script Kadence ni plugin n'est injecté. Il insère une `<base>` pour
   résoudre les chemins d'assets vers le child theme.

> Variante « WP allégé avec `wp_head` » : si vous voulez garder `wp_head()`
> (ex. analytics), utilisez plutôt `wordpress/functions-dequeue-snippet.php`
> qui **dequeue** Kadence + blocs + emoji uniquement sur la page cible et
> enqueue notre CSS/JS. **Vérifier les vrais handles de votre install** (méthode
> de debug fournie en commentaire du snippet).

**Workflow conseillé :** tout valider en **local (Flywheel)** avant le moindre
push SFTP. Backup fichiers + DB avant.

---

## Placeholders à remplir (tous balisés dans le code)

| Placeholder | Où | Quoi mettre |
|---|---|---|
| _(CTA Réserver)_ | header, héro, tarifs, section Réserver, sticky | pointent vers `reservation.html` (tunnel — voir `README-DEMO.md`) |
| `{{LIEN_FICHE_GOOGLE}}` | avis, lieu, JSON-LD `sameAs` | URL de la fiche Google Business |
| `{{LIEN_INSTAGRAM}}` / `{{LIEN_FACEBOOK}}` | footer, JSON-LD | réseaux sociaux |
| `{{LIEN_RESEAU}}` | footer | autres bases eFoil (**à valider**) |
| `{{LIEN_MENTIONS}}` / `{{LIEN_CGV}}` | footer | pages légales |
| `{{PRIX}}` | tarifs (carte « Progression ») | prix du pack à confirmer |
| `{{X}}` / `{{Y}}` | bandeau réseau (section avis, `hidden`) | nb de bases / avis cumulés — **ne pas afficher tant que non validé** |
| `<!-- AVIS À INJECTER -->` | section 2 | avis Google **réels** (Places API ou collage manuel) — remplacer les 3 exemples |
| `<!-- EFCA: futur module booking maison -->` | section Réserver | conteneur `#efca-booking-module` réservé — **backend non codé ici** |
| Polices `inter-*.woff2` | `assets/fonts/` | voir `assets/fonts/README.txt` |
| JSON-LD `geo` / `openingHours` | `<head>` | géocoordonnées + horaires réels (**à confirmer**) |

### Avis Google (section 2) — décision à trancher
La source d'avis n'est pas figée (cf. `efca-build-spec.md`) :
- **(a) Google Places API** → générer les cartes `.efca-review` au build/serveur ;
- **(b) collage manuel** des verbatims réels dans le markup.
Dans les deux cas : conserver la structure `.efca-review`, vérifier RGPD et ne pas
réintroduire de script tiers bloquant (rester fidèle à l'objectif perf).

---

## DA révisée & médias

- **Palette = logo officiel : ORANGE `#F4631F` + TURQUOISE `#00A7C7`** (+ pétrole
  `#0F2830`). Orange = CTA/accents forts (texte blanc) ; turquoise = liens, « e » du
  logo, « Côte d'Azur ». Turquoise profond `#0E7C8B` (`--efca-color-accent-deep`)
  pour le petit texte/libellés sur fond clair (contraste). Cohérent avec les sites
  du réseau (efoil-sainttropez.fr, efoil-letouquet.fr). Tokens : `efca-tokens.css`
  + `assets/css/efca.css`.
- **Logo** : reproduction typographique bicolore (`e` turquoise + `FOIL` orange +
  « Côte d'Azur ») dans header/footer — remplaçable par le SVG/PNG officiel.
- **Co-branding Lift France** : bandeau « Distributeur officiel Lift France —
  Vente · Location · Maintenance » sous le héro.
- **Style Foil in Paris** ré-intégré :
  - **Hublots ronds** (`.efca-porthole`) — galerie « Notre terrain de jeux ».
  - **Blob organique** (`.efca-blob`) sur la photo Encadrement.
  - **Vagues SVG** (`.efca-wavesep`) entre sections (héro→expérience, faq→avis, avis→réserver, réserver→footer).
  - **Cartes Expérience illustrées par photo** (`.efca-feature`) : Accessible & débutant / Encadré / Sécurisé. **Aucun emoji sur la page.**
- **Ordre des sections** : Héro → Expérience → Tarifs → Lieu → Encadrement → Galerie → FAQ → **Avis → Réserver** → Footer (preuve sociale + conversion en fin de page).
- **Médias récupérés du site actuel efoilcotedazur.fr (locaux dans `assets/img/`) :**
  - **Vidéo héro** : `…/2021/03/foil-electrique-LIFT.mp4` — servie depuis l'URL live
    (29 Mo, à recompresser, cf. checklist perf), poster = `hero-poster.webp`.
  - `hero-poster.webp` (1800×1200), `encadrement.webp` (1000×1294),
    `gallery-1/2/3.webp` (baie de Cannes / riders) — 22–172 Ko, déjà WebP.
  - **OG image** : image réelle hébergée sur le domaine live.
- Autres médias dispo sur leur `wp-content/uploads/` si besoin :
  `DSC00480-2…jpg`, `P1181440.jpg`, `IMG-20210302…jpg`, `DSC09252…jpg`.

## SEO (fait main, sans Yoast)
- `title` / `meta description` transac local + `canonical` + OG/Twitter dans `<head>`.
- **NAP au pixel** identique partout (héro / section Lieu / footer / JSON-LD / fiche GMB) :
  `Plage des Dauphins, Bd du Midi Louise Moreau, 06150 Mandelieu-la-Napoule` · `06 35 30 50 67`.
- JSON-LD `SportsActivityLocation` + `AggregateRating` (5.0 / 230) + `FAQPage`.
- ⚠️ Les **étoiles auto-déclarées** (`AggregateRating`) sont souvent **non affichées**
  en rich snippet par Google → priorité **conversion on-page**, pas le snippet.
  Les vraies étoiles viennent de la fiche Google (Local Pack). (Commenté dans le `<head>`.)
- En Option B : si Yoast est actif, éviter le doublon de balises (dequeue / `wpseo_head`).

---

## Checklist perf (raison d'être du HTML pur — cible LCP mobile < 2 s)

- [x] **CSS critique inliné** dans `<head>` ; reste de `efca.css` chargé async (`preload`+`onload`, fallback `<noscript>`).
- [x] **JS en `defer`** (non bloquant) ; FAQ en `<details>` natif (zéro JS).
- [x] **Polices auto-hébergées** + `font-display:swap` + `preload` du poids 700 ; **pas de Google Fonts bloquant** ; fallback système.
- [x] **Image LCP** = poster WebP local du héro (`fetchpriority="high"` + `width/height` anti-CLS + `preload`).
- [x] **Vidéo héro** en `preload="metadata"` (ne télécharge pas les 29 Mo avant le 1er rendu) ; le poster reste le LCP.
- [x] Images sous la ligne de flottaison en `loading="lazy"` + `decoding="async"` ; **iframe carte en `loading="lazy"`**.
- [x] Mobile-first ; **CTA « Réserver » sticky** en bas sur mobile.
- [x] `prefers-reduced-motion` respecté (animations coupées).
- [ ] **À faire avant prod (levier LCP/data n°1) :** recompresser la vidéo héro `foil-electrique-LIFT.mp4` (**29 Mo → ~3-5 Mo**) et fournir un `.webm` ; ou désactiver l'autoplay vidéo sur mobile et ne garder que le poster.
- [ ] Activer **gzip/brotli** + cache long sur `assets/` (header serveur OVH).
- [ ] Mesurer Lighthouse mobile **après** dépôt des polices + recompression vidéo.

### Vérifier en local (rapide)
```bash
# servir le dossier en statique pour tester index.html
python -m http.server 8080        # puis http://localhost:8080
```

---

## Accessibilité (base couverte)
Landmarks (`header`/`main`/`footer`/`section[aria-labelledby]`), skip-link, `alt`
descriptifs orientés local, focus visibles, contrastes (voile pétrole sur le héro),
FAQ clavier-friendly via `<details>`.

---

## Hors périmètre (volontairement non codé)
- Backend du **module de réservation maison + notif mail/SMS** → emplacement réservé seulement.
- **Bandeau réseau** (X bases / Y avis) → masqué tant que les chiffres ne sont pas validés.
- Aucune désactivation en prod, aucun push, aucune modif DB.
