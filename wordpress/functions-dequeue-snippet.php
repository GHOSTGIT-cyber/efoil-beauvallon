<?php
/**
 * SNIPPET DEQUEUE — à coller dans le functions.php du CHILD THEME
 * (ou via le plugin Code Snippets / WPCode).
 * -----------------------------------------------------------------------------
 * À UTILISER UNIQUEMENT si vous gardez wp_head()/wp_footer() sur la page EFCA
 * (variante "WordPress allégé" plutôt que le canvas full-bypass de page-efca.php).
 *
 * Objectif : sur la page EFCA seulement, retirer les styles/scripts Kadence +
 * plugins qui plombent la perf, et laisser uniquement notre CSS/JS.
 *
 * ⚠️ Adapter les "handles" : ceux ci-dessous sont les handles COURANTS de
 *    Kadence ; vérifier les vrais handles de VOTRE install avec, en debug :
 *      add_action('wp_print_styles', function(){
 *        if (function_exists('efca_is_target')) error_log(print_r(wp_styles()->queue, true));
 *      }, 9999);
 *
 * GARDE-FOU : tester en LOCAL (Flywheel) d'abord. Backup avant prod.
 * -----------------------------------------------------------------------------
 */

if ( ! defined( 'ABSPATH' ) ) { exit; }

/**
 * La page EFCA est-elle en cours d'affichage ?
 * Cible la page qui utilise le template page-efca.php (ou, à défaut, la home).
 */
function efca_is_target() {
    if ( is_admin() ) { return false; }
    if ( is_page_template( 'page-efca.php' ) ) { return true; }
    // Repli : si la one-page est la page d'accueil.
    return is_front_page();
}

/**
 * 1) Enqueue de NOTRE CSS/JS sur la page cible.
 *    (Inutile si vous servez index.html via page-efca.php en full-bypass.)
 */
add_action( 'wp_enqueue_scripts', function () {
    if ( ! efca_is_target() ) { return; }

    $base = get_stylesheet_directory_uri() . '/efca/assets';
    $ver  = '1.0.0';

    wp_enqueue_style( 'efca', $base . '/css/efca.css', array(), $ver );
    wp_enqueue_script( 'efca', $base . '/js/efca.js', array(), $ver, true ); // in_footer = true
}, 20 );

/**
 * 2) DEQUEUE Kadence + plugins sur la page cible (priorité très tardive
 *    pour passer après leurs propres enqueues).
 */
add_action( 'wp_enqueue_scripts', function () {
    if ( ! efca_is_target() ) { return; }

    // --- Styles Kadence (handles courants) ---
    $styles = array(
        'kadence-global',
        'kadence-header',
        'kadence-footer',
        'kadence-content',
        'kadence-base',
        'kadence-blocks-css',
        'kadence-blocks-style-css',
        'kadence_blocks_global',
        'global-styles',          // styles globaux WP (theme.json)
        'classic-theme-styles',
        'wp-block-library',       // CSS des blocs Gutenberg core
        'wp-block-library-theme',
    );
    foreach ( $styles as $h ) {
        wp_dequeue_style( $h );
        wp_deregister_style( $h );
    }

    // --- Scripts Kadence / divers ---
    $scripts = array(
        'kadence-navigation',
        'kadence-mobile-navigation',
        'kadence-blocks-js',
        'kadence-header',
    );
    foreach ( $scripts as $h ) {
        wp_dequeue_script( $h );
        wp_deregister_script( $h );
    }

    // --- Emoji WP (toujours bon à virer pour la perf) ---
    remove_action( 'wp_head', 'print_emoji_detection_script', 7 );
    remove_action( 'wp_print_styles', 'print_emoji_styles' );

    // --- (Optionnel) couper Yoast sur cette page : on gère le SEO à la main
    //     dans index.html. Décommenter si Yoast injecte des balises en double.
    // add_filter( 'wpseo_head', '__return_empty_string' );

}, 9999 );

/*
 * RAPPEL : si vous utilisez page-efca.php en mode full-bypass (il fait `exit;`
 * après avoir imprimé index.html), ce snippet n'est PAS nécessaire — aucun
 * asset de thème/plugin n'est imprimé puisque wp_head()/wp_footer() ne sont
 * jamais appelés. Le snippet sert la variante "WordPress allégé avec wp_head".
 */
