/* =============================================================================
   efca-config.js — Configuration FRONT du tunnel réservation / paiement
   -----------------------------------------------------------------------------
   NB — La SOURCE DE VÉRITÉ du mode de paiement est la constante PHP
      EFCA_PAYMENT_MODE (récupérée au chargement via /wp-json/efca/v1/config).
   Les valeurs ci-dessous ne servent que de FALLBACK pour la preview STATIQUE
   (sans WordPress) — elles n'ont aucun effet si le backend répond.
   ============================================================================= */
window.EFCA_CONFIG = {
  // Base de l'API WP REST. '' = même domaine ("/wp-json/...").
  // Exemple cross-domaine : "https://staging.exemple.fr"
  apiBase: '',

  // Fallback si le backend ne répond pas (preview statique uniquement) :
  //   'simulation' | 'off' | 'stripe'
  fallbackMode: 'simulation',

  // Tarif unitaire (€) par participant pour 1 h — PLACEHOLDER, à ajuster.
  unitPrice: 150,
  currency: 'EUR',
  baseName: 'Mandelieu — Plage des Dauphins'
};
