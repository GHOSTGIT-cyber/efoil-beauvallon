# DÉMO — Réservation + Paiement simulé + Dashboard

Tunnel de **démonstration** à héberger sur un **site annexe (staging)** pour présentation.
Le paiement est **simulé** (aucune transaction réelle, aucun PSP appelé). WordPress reste
actif en back pour stocker les réservations et notifier par e-mail.

> ⚠️ **DÉMO uniquement.** Local d'abord (Flywheel) → SFTP vers le **site annexe**.
> **Backup avant tout push.** Ne touche pas la prod réelle (efoilcotedazur / liftfoils) ni sa DB.
> La page `reservation.html` est en `noindex,nofollow`.

---

## Pièces livrées

| Fichier | Rôle |
|---|---|
| `reservation.html` | Tunnel 3 étapes : **formulaire → paiement simulé → succès** (DA conservée, bandeau DÉMO). |
| `assets/js/efca-config.js` | Config **front** (fallback de mode, tarif, base API). |
| `assets/js/efca-reservation.js` | Logique tunnel : validation, honeypot, `fetch` REST, simulation paiement, stub Stripe. |
| `dashboard.html` | **Tableau de bord** front : stats, filtre, table des réservations, changement de statut. |
| `assets/js/efca-dashboard.js` | Logique dashboard : `fetch` REST (auth), rendu, maj statut, **données d'exemple** en fallback. |
| `assets/css/efca.css` | Styles tunnel + dashboard (étapes, formulaire, carte paiement, table, pills) ajoutés en fin de fichier. |
| `wordpress/efca-reservation.php` | **Back** : flag `PAYMENT_MODE`, CPT `efca_reservation`, API REST (résa + paiement + **dashboard**), `wp_mail`, admin (colonnes + statut), **stub Stripe commenté**. |

---

## Architecture — UN seul flag

Le mode de paiement est piloté par **une seule valeur**, la constante PHP
**`EFCA_PAYMENT_MODE`** (source de vérité). Le front la lit via `/wp-json/efca/v1/config`.

```php
// wp-config.php  (recommandé)  OU  en tête de wordpress/efca-reservation.php
define('EFCA_PAYMENT_MODE', 'simulation'); // 'simulation' | 'off' | 'stripe'
```

| Mode | Comportement | Usage |
|---|---|---|
| `simulation` | Faux checkout de bout en bout → faux succès. CPT passe à **payée (simulation)**. | **La démo, maintenant.** |
| `off` | Pas de paiement : réservation seule (statut **en attente**), écran de confirmation direct. | Mise en ligne en attendant Stripe. |
| `stripe` | Embedded Checkout réel (rendu dans la page). **Inactif tant que stub non décommenté + clés absentes.** | Plus tard, avec les clés de Nico. |

**Changer de mode = éditer cette seule ligne.** Le reste (front + back) s'adapte.

> Preview **statique sans WordPress** : si l'API ne répond pas, le front retombe sur
> `EFCA_CONFIG.fallbackMode` (`efca-config.js`) pour que la démo visuelle fonctionne
> quand même (en mode `simulation`/`off`). En `stripe`, le backend est requis.

---

## Installation (site annexe)

### Back — WordPress
1. Copier `wordpress/efca-reservation.php` dans **`wp-content/mu-plugins/`**
   (créer le dossier si besoin) → activé automatiquement. *(ou dossier `plugins/` + activation manuelle.)*
2. Vérifier le destinataire des e-mails : `EFCA_NOTIFY_EMAIL` (par défaut l'e-mail admin du site).
3. Régler le tarif si besoin : `EFCA_UNIT_PRICE` (défaut 150 €/participant).

### Front
4. Envoyer `reservation.html` + `assets/` en **SFTP** au même domaine que le WordPress
   (pour que `/wp-json/...` soit en same-origin). Sinon, renseigner `apiBase` dans
   `assets/js/efca-config.js` (et gérer le CORS côté WP).
5. Tester : ouvrir `reservation.html`, remplir, **Continuer → Payer → succès**.
6. Vérifier dans **wp-admin → Réservations** que la fiche est créée et passe à
   *Payée (simulation)*, et que l'e-mail est parti.

---

## 3) Tableau de bord (validation des réservations)

Deux vues, au choix :

**Option A (zéro build)** — `wp-admin → Réservations` :
- Colonnes : **Client · Date/créneau · Montant · Statut · Reçue le**.
- Écran d'édition : encart **« Détails & statut »** avec menu déroulant
  (En attente / Validée / Refusée / Payée (simulation)).

**Option B (page front livrée)** — **`dashboard.html`** :
- Cartes de stats (Total / En attente / Validées / Payées-simulation / Refusées),
  filtre par statut, table, et **menu de statut par ligne** (mise à jour en direct).
- API : `GET /efca/v1/reservations` + `POST /efca/v1/reservation/{id}/status`,
  **protégées** par `permission_callback` (capacité `edit_posts`).
- **Auth** : la page appelle l'API avec le **cookie WordPress + `X-WP-Nonce`**.
  Pour fournir le nonce à une page statique, injecter pour les connectés :
  `window.EFCA_NONCE = '<?php echo wp_create_nonce("wp_rest"); ?>';`
  (snippet d'injection rappelé dans `efca-reservation.php`).
- **Hors connexion / sans backend** : `dashboard.html` affiche des **données
  d'exemple** (badge « Mode démo ») pour être présentable immédiatement.

---

## API REST (namespace `efca/v1`)

| Méthode | Route | Rôle |
|---|---|---|
| GET  | `/config` | Renvoie `mode`, `unitPrice`, `currency` (lu par le front). |
| POST | `/reservation` | Crée le CPT (statut *en attente*) + `wp_mail`. **Honeypot + validation serveur** ; nonce vérifié s'il est fourni. |
| POST | `/reservation/{id}/pay` | **Mode simulation uniquement** : passe le statut à *payée (simulation)*. |
| GET  | `/reservations` | **Dashboard** — liste (protégé `edit_posts`). |
| POST | `/reservation/{id}/status` | **Dashboard** — changement de statut (protégé `edit_posts`). |
| POST | `/stripe/session` | *(commenté)* crée la Checkout Session Stripe. |

Anti-spam : champ **honeypot** `website` (caché), **validation serveur** de tous les
champs, aucune donnée perso en URL (POST JSON). Le nonce `X-WP-Nonce` est vérifié
si présent (page rendue par WP) ; en page statique, le honeypot + la validation
assurent la protection de base — durcir si besoin (rate-limit, captcha).

---

## 4) Basculer vers le VRAI Stripe (préparé, NON activé)

Tout est prêt mais **désactivé** :
1. `composer require stripe/stripe-php` dans le plugin.
2. Clés Stripe en **variables d'environnement** (`STRIPE_SECRET_KEY`) ou options WP —
   **jamais en dur**.
3. Décommenter, dans `efca-reservation.php`, le bloc **`<!-- STRIPE -->`** (route
   `/stripe/session` + `efca_rest_stripe_session()` en `ui_mode: 'embedded'`).
4. Décommenter le montage dans `efca-reservation.js` (`mountStripe()`), en chargeant
   `stripe.js` et la clé publique. **Stripe gère son propre iframe : ne pas l'imbriquer
   dans un autre iframe.**
5. Implémenter le **webhook** `checkout.session.completed` pour passer la réservation
   au statut *payée* (réel).
6. Passer `EFCA_PAYMENT_MODE` à `'stripe'`.

---

## Retrait du paiement en prod (sans Stripe)

Pour une mise en ligne « réservation seule » avant Stripe : `EFCA_PAYMENT_MODE = 'off'`.
Le tunnel saute l'étape paiement et confirme directement (statut *en attente*).

---

## Garde-fous (rappel)
- Local d'abord → **site annexe** en SFTP. **Backup** fichiers + DB avant push.
- **Aucune** intervention sur la prod réelle ni sa base.
- Paiement **simulé** clairement marqué (bandeau + libellés + statut `paid_sim`).
- Placeholders : `EFCA_UNIT_PRICE` (montant), `EFCA_NOTIFY_EMAIL` (destinataire),
  médias/`{{…}}` de la one-page (voir `README.md`).
