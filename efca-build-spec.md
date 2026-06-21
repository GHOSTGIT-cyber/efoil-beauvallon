# Build spec — Refonte one-page **efoilcotedazur.fr**

> **Statut : SPEC uniquement.** Aucun fichier de prod modifié, aucune base de
> données touchée, aucun push. foilinparis.fr lu en lecture seule. Ce document
> est la fondation à coder dans une étape ultérieure.

---

## 0. Cadre

| | |
|---|---|
| **Cible** | efoilcotedazur.fr — base de location eFoil, Mandelieu-la-Napoule |
| **NAP (au pixel)** | Plage des Dauphins, Bd du Midi Louise Moreau, 06150 Mandelieu-la-Napoule · **06 35 30 50 67** |
| **Atout massif** | Fiche Google **5,0 ★ / 230 avis** |
| **Offre type** | Session 1h = **150 €** |
| **Booking actuel** | Yumping (lien externe) |
| **Stack cible** | WordPress + **Kadence** + Gutenberg · CSS custom · **mobile-first (91 % du trafic)** |
| **Interdits** | ❌ Elementor (bloqué serveur) · ❌ GenerateBlocks |
| **Source DA** | foilinparis.fr |

### Direction artistique répliquée (résumé)
Source réelle = site **Odoo** (le brief disait Wix), thème **Inter**, registre
*beach-club premium / lifestyle*, **imagery-first** : héro plein écran image +
vidéo de fond, séparateurs **vagues SVG**, textes animés (slide/fade), murs
d'images masonry (desktop) + carrousel (mobile), médias à coins arrondis, fonds
alternés crème/menthe. Palette = **orange `#FF6400`** (accent unique fort) sur
neutres crème/blanc, **menthe `#C7EFE2`** en respiration, **pétrole `#0F2830`**
pour le contraste. Tous les tokens sont dans [`efca-tokens.css`](efca-tokens.css).

---

## 1. Hero immersif

**Objectif :** vendre la sensation en < 1 s + CTA réservation above-the-fold.

- **Contenu**
  - Média de fond : photo rider **à Mandelieu** (pas Paris), plein écran, voile
    pétrole (`--efca-overlay-hero`) pour lisibilité. Option vidéo de fond muette
    en loop (comme la source) — **à valider** selon poids/perf mobile.
  - H1 sensoriel : ex. **« Voler au-dessus de la Méditerranée. »**
    sous-titre : *« Location & initiation eFoil à Mandelieu — Côte d'Azur. »*
  - **CTA primaire** « Réserver ma session » (ancre booking / lien Yumping),
    visible above-the-fold.
  - **Barre preuve sociale** sous le CTA : `★★★★★ 5,0 · 230 avis Google`
    (composant `.efca-rating-bar`, étoiles en orange de marque).
- **Composant :** `.efca-section` plein écran + `.efca-h-display` + `.efca-btn--primary` + `.efca-rating-bar`.
- **CTA sticky mobile :** `.efca-sticky-cta` (barre fixe bas d'écran, masquée ≥ 992px) — réservation toujours à portée de pouce.
- **Mapping Kadence/Gutenberg :**
  - **Kadence Row Layout** en hauteur 100vh, *Background → Image* (+ overlay couleur), 1 colonne centrée.
  - Titres = blocs **Kadence Advanced Heading** ; CTA = **Kadence Advanced Button** (style pill, classe `efca-btn--primary`).
  - Barre d'avis = bloc **Kadence Advanced Text** ou HTML custom (`.efca-rating-bar`).
  - Sticky mobile = **bloc HTML/Kadence** rendu en `position:fixed` via classe `.efca-sticky-cta` (ou Kadence "Sticky" sur une row dédiée mobile-only).
- **Emplacement avis :** barre condensée ici (note + nombre), renvoi visuel vers la section 2.

## 2. Mur d'avis (preuve sociale)

**Objectif :** transformer la note Google en moteur de conversion principal.

- **Contenu**
  - Bloc chiffre fort : **5,0 / 5** (`--efca-fs-stat`, poids 900) + « **230 avis Google** » + 5 étoiles orange.
  - **Carrousel d'avis Google réels** (verbatims + prénom + date).
  - **Badge Google** (logo + « Avis vérifiés »).
  - **[OPTION À VALIDER]** bandeau réseau *« eFoil France — X bases / Y avis cumulés »*. → **NE PAS coder tant que X/Y ne sont pas fournis et validés.** Réserver l'emplacement (sous le carrousel).
- **Composant :** carrousel d'avis (voir incertitudes pour la source des avis) sur fond `.efca-section--cream`.
- **Mapping Kadence/Gutenberg :**
  - Bloc chiffre = **Kadence Advanced Heading** + Row 2 colonnes.
  - Carrousel = **plugin d'avis Google** (ex. widget type *Reviews* compatible Kadence) **ou** Kadence **Carousel/Posts** alimenté manuellement. *Choix plugin = à valider (RGPD + perf).*
  - Badge = bloc image/HTML.
- **Emplacement avis :** **section cœur** — c'est ici que vit le mur d'avis complet.

## 3. L'expérience eFoil

**Objectif :** lever la peur (« c'est accessible, encadré, sûr »).

- **Contenu :** 3 arguments — *Accessible débutant* (debout en quelques minutes), *Encadré* (moniteur dédié), *Sécurisé* (gilet, brief, matériel pro). Photo/vidéo immersive Mandelieu.
- **Composant :** texte + image alternés (pattern `s_text_image` de la source), séparateur **vague SVG**, 3 cards `.efca-card` avec pictos.
- **Mapping Kadence/Gutenberg :** Kadence **Row** image+texte ; trio = **Kadence Info Box** ×3 (icône + titre + texte) dans une row 3 colonnes (empilées mobile).
- **Emplacement avis :** mini-citation d'1 avis pertinent (« jamais fait, debout en 5 min ») en exergue.

## 4. Offre & tarifs

**Objectif :** clarté tarifaire + relance CTA.

- **Contenu :** session 1h = **150 €** (référence), niveaux (découverte / progression), ce qui est **inclus** (matériel, combinaison, moniteur, assurance), durées. CTA « Réserver » répété.
- **Composant :** grille tarifs reprise de la source — cartes « feature » header orange (`--efca-radius-lg`, glow), cellules blanches, **pills menthe** pour les prix. Mobile = cartes empilées (`.efca-card`).
- **Mapping Kadence/Gutenberg :** **Kadence Pricing Table** (ou Row + Info Box) ; prix en `.efca-pill` ; CTA = Kadence Advanced Button `.efca-btn--primary`.
- **Emplacement avis :** rappel barre `5,0 ★ · 230 avis` près du CTA pour rassurer au moment du prix.

## 5. Réserver

**Objectif :** convertir. **Yumping d'abord**, module maison plus tard.

- **Contenu :** bloc réservation = **lien/bouton Yumping** (CTA primaire). Texte de réassurance (annulation, météo). **Module de réservation maison + notif mail/SMS = NE PAS CODER ICI** → simplement **réserver l'emplacement** (conteneur balisé, commentaire `<!-- EFCA: futur module booking maison -->`).
- **Composant :** section CTA pleine largeur sur fond `.efca-section--mint` ou image.
- **Mapping Kadence/Gutenberg :** Row 1 colonne + Advanced Button (Yumping, `target="_blank" rel="noopener"`). Conteneur réservé = bloc HTML vide nommé pour le futur module.
- **Emplacement avis :** badge Google compact à côté du bouton.

## 6. Lieu & accès

**Objectif :** signal SEO local + faciliter la venue (NAP = fiche, au pixel).

- **Contenu (NAP EXACT — ne pas paraphraser) :**
  - **Plage des Dauphins, Bd du Midi Louise Moreau, 06150 Mandelieu-la-Napoule**
  - **06 35 30 50 67**
  - Horaires (saison — **à confirmer**), accès/parking.
- **Composant :** carte Google Maps embed (pattern source) + bloc NAP + horaires.
- **Mapping Kadence/Gutenberg :** Row 2 colonnes (NAP/horaires | carte). Carte = **Kadence Google Maps** ou iframe Maps. NAP = Advanced Text. *Le NAP doit être en texte réel (pas image) pour le SEO.*
- **Emplacement avis :** lien « Voir les 230 avis sur Google » pointant la fiche GMB.

## 7. Encadrement & confiance

**Objectif :** crédibilité humaine + qualité matériel.

- **Contenu :** moniteurs (expérience/diplômes), protocole sécurité, **matériel Lift** mis en avant comme gage de qualité.
- **Composant :** texte + image, logo/visuel Lift, pictos sécurité.
- **Mapping Kadence/Gutenberg :** Kadence Row image+texte + Info Box trio (Moniteurs / Sécurité / Matériel Lift).
- **Emplacement avis :** citation avis mentionnant le moniteur / l'accueil.

## 8. FAQ

**Objectif :** lever les dernières objections + SEO longue traîne.

- **Contenu :** **Niveau requis ?** (aucun, débutants bienvenus) · **Âge minimum ?** (à confirmer) · **Météo ?** (politique en cas de mauvais temps) · **Annulation ?** (conditions). 5–8 questions.
- **Composant :** accordéon.
- **Mapping Kadence/Gutenberg :** **Kadence Accordion**. Couplé au **schema FAQPage** (voir §SEO).
- **Emplacement avis :** —

## 9. Footer

- **Contenu :** **NAP complet** (identique §6, au pixel), réseaux sociaux, lien autres bases (réseau eFoil — **à valider**), mentions légales, CGV, plan d'accès.
- **Composant :** footer Kadence (Footer Builder) sur fond `.efca-section--dark`.
- **Mapping Kadence/Gutenberg :** **Kadence Footer Builder** + Row colonnes.
- **Emplacement avis :** rappel discret `5,0 ★ · 230 avis Google`.

---

## SEO / Technique

- **Slug :** **conservé** (page d'accueil `/`). Ne pas casser l'URL existante ; conserver les éventuelles redirections.
- **Title (transac local) :** `Location eFoil Mandelieu — Côte d'Azur` (≤ 60 car., marque en fin si place).
- **Meta description :** orientée conversion + local + preuve (note 5,0, 230 avis, débutants, matériel Lift). ~150 car.
- **NAP au pixel :** chaîne strictement identique partout (héro/§6/footer/schema/fiche GMB) — orthographe, ponctuation, format téléphone (`06 35 30 50 67`). **Cohérence = facteur de ranking local.**
- **Schema (JSON-LD) :**
  - `LocalBusiness` (type `SportsActivityLocation`) avec `name`, `address` (NAP), `telephone`, `geo`, `openingHours`, `priceRange` (`€€`), `url`, `image`, `sameAs` (réseaux + fiche Google).
  - `AggregateRating` (5,0 / 230) **+** `FAQPage` (section 8).
  - **⚠️ À confirmer :** Google **bride les étoiles auto-déclarées** (rich snippet `AggregateRating` sur un `LocalBusiness` souvent non affiché / risque "structured data manuel"). **Priorité = conversion on-page, pas le snippet.** → Marquer en JSON-LD pour cohérence, mais **ne pas dépendre** de l'affichage des étoiles en SERP. Les vraies étoiles viennent de la **fiche GMB** dans le Local Pack.
- **Performance (91 % mobile) :**
  - Héro : si vidéo de fond → `poster` image + `preload` maîtrisé, lazy sous la ligne de flottaison, images **WebP** responsives (la source sert déjà du WebP).
  - CSS custom = tokens d'abord, mobile-first, pas de framework lourd hérité.
  - LCP = image héro → prioriser (`fetchpriority="high"`), différer le carrousel d'avis.
- **Accessibilité :** contraste texte sur image (overlay), focus visibles sur CTA, `alt` descriptifs orientés local (« rider eFoil plage des Dauphins Mandelieu »).
- **Tracking :** events sur CTA Réserver (héro / sticky / tarifs / section 5) pour mesurer la source des conversions avant le module maison.

### Emplacement du CSS (config WordPress — à confirmer sur l'install réelle)

> **Non présumé.** Je n'ai pas eu accès au filesystem ni à l'admin d'efoilcotedazur.fr (répertoire de travail vide, pas de dépôt git). Le placement exact doit être vérifié sur l'install. Options par ordre de robustesse :
>
> 1. **Child theme Kadence** → `style.css` ou un `assets/efca-tokens.css` enqueue via `functions.php` (`wp_enqueue_style`). ✅ recommandé (versionnable, survit aux MAJ).
> 2. **Kadence → Customizer → CSS additionnel** (Apparence ▸ Personnaliser ▸ CSS additionnel). Rapide, mais lié au thème.
> 3. **Plugin Code Snippets / WPCode** (CSS). Si pas de child theme.
> 4. ❌ Éviter de coller dans le `style.css` du thème parent (écrasé aux mises à jour).
>
> **Action préalable au build :** confirmer (a) child theme présent ? (b) version Kadence (Free/Pro) ? (c) plugins d'avis Google déjà installés ?

---

## Incertitudes — extrait avec certitude vs supposé

### ✅ Extrait avec certitude (lu dans le HTML/CSS source)
- Palette exacte : `#FF6400`, `#C7EFE2`, `#FCF8F3`, `#FFFFFF`, `#0F2830` (var. `--o-color-1..5`) + menthes `#D8F7EA`/`#B2F2DC`, dark `#222`.
- Boutons : primaire bg `#FF6400` / hover `#D95500` / border hover `#CC5000` ; secondaire bg `#C7EFE2` / hover `#CFF1E6`.
- Police **Inter** (400/600/700, logo 900), letter-spacing −2px sur gros logo.
- Échelle titres : `display-3 = 4rem`, `h2 = 3rem` desktop / `28px` mobile.
- Rayons : 12 / 16 / 20px (cartes), 999px/10rem (pills), 0.4rem (boutons).
- Ombres : `0 2px 8–10px rgba(0,0,0,.05)`, glow `0 4px 12px #FF6400`.
- Échelle d'espacement Odoo pt/pb (24/32/40/56/64/104/112/120/160).
- Breakpoints 768/769 + lg 992.
- Patterns : héro `s_cover` plein écran image **+ vidéo Vimeo de fond**, vagues SVG, textes animés, masonry desktop / carrousel mobile, Google Maps embed, motif rayé menthe.

### ⚠️ Supposé / à valider (non vérifiable sur la source ou propre à EFCA)
- **Stack réelle de la source** = Odoo (le brief annonçait Wix) — DA répliquée quand même.
- **Avis Google sur la home** : la source ne les affiche **pas** en widget sur l'accueil (page dédiée « ils parlent de nous »). Le mur d'avis §2 est une **brique nouvelle pour EFCA** → choix de la source des avis à trancher : plugin officiel Google, widget tiers (Elfsight/Trustindex…), ou import manuel. Impacts RGPD + perf.
- **Contenus rédactionnels** (H1, FAQ, textes) = **propositions**, à valider/réécrire.
- **Bandeau réseau « X bases / Y avis cumulés »** : chiffres inconnus → **non codé**, emplacement réservé.
- **Module booking maison + notif mail/SMS** : hors périmètre, **emplacement réservé** uniquement.
- **Horaires, âge minimum, politique météo/annulation** : à fournir par le client.
- **Géocoordonnées exactes** (schema `geo`) : à récupérer depuis la fiche GMB.
- **Emplacement du CSS / config WordPress** : non vérifié (pas d'accès à l'install) — voir options ci-dessus.
- **Affichage des étoiles en SERP** : non garanti (politique Google) — priorité conversion.
- **o-color-5 `#0F2830`** : présent dans le thème ; son usage exact (dark sections) sur la home source est limité — réemployé ici comme couleur d'encre/contraste pour EFCA.
