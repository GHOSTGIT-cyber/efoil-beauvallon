<?php
/**
 * Template Name: EFCA Canvas (one-page HTML pur)
 * Template Post Type: page
 *
 * -----------------------------------------------------------------------------
 * Refonte one-page efoilcotedazur.fr — WordPress NEUTRALISÉ sur cette page.
 *
 * Ce template "canvas vierge" :
 *   - N'appelle NI get_header() NI get_footer() du thème → aucun chrome Kadence.
 *   - N'imprime PAS wp_head()/wp_footer() → aucun style/script du thème ni des
 *     plugins n'est injecté sur cette page (zéro render-blocking hérité).
 *   - Sert le HTML statique tel quel (source unique = index.html du child theme).
 *
 * INSTALLATION
 *   1. Déposer ce fichier dans le child theme :  wp-content/themes/<child>/page-efca.php
 *   2. Déposer index.html + /assets dans le child theme :
 *        wp-content/themes/<child>/efca/index.html
 *        wp-content/themes/<child>/efca/assets/...
 *   3. Dans l'admin : créer/éditer la page d'accueil → Attributs de page →
 *      Modèle = "EFCA Canvas (one-page HTML pur)".
 *   4. Réglages → Lecture → Page d'accueil = cette page (slug conservé : « / »).
 *
 * NOTE CHEMINS D'ASSETS
 *   index.html référence les assets en relatif (assets/css/...). Servi via ce
 *   template, l'URL de base n'est pas le dossier du thème. Deux options :
 *     (A) Réécrire les chemins en absolus pointant le child theme (voir $base
 *         ci-dessous : on injecte une <base> — simple et fiable).
 *     (B) Préférer l'option A "Autonome" (index.html à la racine via SFTP) si
 *         l'install le permet : zéro PHP.
 *
 * ⚠️ GARDE-FOU : ce fichier est livré pour intégration manuelle. Faire un BACKUP
 *   (fichiers + DB) AVANT de l'activer. Ne rien désactiver en prod sans backup.
 * -----------------------------------------------------------------------------
 */

if ( ! defined( 'ABSPATH' ) ) { exit; }

// Dossier physique + URL du bundle statique dans le child theme.
$efca_dir = get_stylesheet_directory() . '/efca';
$efca_url = get_stylesheet_directory_uri() . '/efca';

$index = $efca_dir . '/index.html';

if ( ! file_exists( $index ) ) {
    status_header( 500 );
    echo '<!-- EFCA: index.html introuvable dans ' . esc_html( $efca_dir ) . ' -->';
    exit;
}

$html = file_get_contents( $index );

// Injecte une <base> pour résoudre les chemins relatifs assets/... vers le child theme.
// (Insère juste après <head>.)
$base_tag = '<base href="' . esc_url( trailingslashit( $efca_url ) ) . '">';
$html = preg_replace( '/<head(\s[^>]*)?>/i', '$0' . "\n  " . $base_tag, $html, 1 );

// On sert notre propre document complet, sans wp_head()/wp_footer().
header( 'Content-Type: text/html; charset=UTF-8' );
echo $html;
exit;
