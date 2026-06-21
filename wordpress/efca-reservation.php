<?php
/**
 * Plugin Name: EFCA — Démo Réservation + Paiement simulé
 * Description: CPT reservation + API REST + e-mail + admin + flag PAYMENT_MODE. Tunnel de DÉMONSTRATION (paiement simulé, aucune transaction réelle).
 * Version: 1.0.0
 * Author: EFCA
 *
 * -----------------------------------------------------------------------------
 * INSTALLATION (site ANNEXE / staging — JAMAIS la prod réelle) :
 *   - Déposer ce fichier dans  wp-content/mu-plugins/efca-reservation.php
 *     (créer le dossier mu-plugins s'il n'existe pas) → activation automatique.
 *   - OU le placer dans wp-content/plugins/efca-reservation/efca-reservation.php
 *     puis l'activer dans l'admin.
 *
 * BASCULE DU MODE DE PAIEMENT = UNE SEULE VALEUR :
 *   define('EFCA_PAYMENT_MODE', 'simulation'|'off'|'stripe');  // ci-dessous ou wp-config.php
 *
 * GARDE-FOUS : local d'abord (Flywheel) → SFTP vers le site annexe. Backup avant.
 *   Ne touche pas la prod réelle ni sa DB.
 * -----------------------------------------------------------------------------
 */

if (!defined('ABSPATH')) { exit; }

/* =============================================================================
   1) FLAG UNIQUE + RÉGLAGES (surchargeable depuis wp-config.php)
   ============================================================================= */
if (!defined('EFCA_PAYMENT_MODE')) { define('EFCA_PAYMENT_MODE', 'simulation'); } // 'simulation' | 'off' | 'stripe'
if (!defined('EFCA_UNIT_PRICE'))   { define('EFCA_UNIT_PRICE', 150); }            // € / participant / 1h
if (!defined('EFCA_CURRENCY'))     { define('EFCA_CURRENCY', 'EUR'); }
if (!defined('EFCA_NOTIFY_EMAIL')) { define('EFCA_NOTIFY_EMAIL', get_option('admin_email')); } // destinataire (Nico)

/** Statuts métier (stockés en meta _efca_status). */
function efca_statuses() {
    return array(
        'pending'   => 'En attente',
        'validated' => 'Validée',
        'refused'   => 'Refusée',
        'paid_sim'  => 'Payée (simulation)',
    );
}

/* =============================================================================
   2) CPT reservation
   ============================================================================= */
add_action('init', function () {
    register_post_type('efca_reservation', array(
        'labels' => array(
            'name'          => 'Réservations',
            'singular_name' => 'Réservation',
            'menu_name'     => 'Réservations',
            'all_items'     => 'Toutes les réservations',
        ),
        'public'        => false,
        'show_ui'       => true,
        'show_in_menu'  => true,
        'menu_icon'     => 'dashicons-tickets-alt',
        'menu_position' => 26,
        'supports'      => array('title'),
        'capability_type' => 'post',
        'map_meta_cap'  => true,
    ));
});

/* =============================================================================
   3) API REST  (namespace efca/v1)
   ============================================================================= */
add_action('rest_api_init', function () {

    // 3.a — Config publique : le FRONT lit le mode ici (source de vérité = PHP).
    register_rest_route('efca/v1', '/config', array(
        'methods'             => 'GET',
        'permission_callback' => '__return_true',
        'callback'            => function () {
            return array(
                'mode'      => EFCA_PAYMENT_MODE,
                'unitPrice' => (int) EFCA_UNIT_PRICE,
                'currency'  => EFCA_CURRENCY,
            );
        },
    ));

    // 3.b — Création d'une réservation (statut "en attente") + e-mail.
    register_rest_route('efca/v1', '/reservation', array(
        'methods'             => 'POST',
        'permission_callback' => '__return_true', // public : protégé par honeypot + validation (voir note nonce)
        'callback'            => 'efca_rest_create_reservation',
    ));

    // 3.c — Paiement SIMULÉ : passe le statut à "payée (simulation)".
    register_rest_route('efca/v1', '/reservation/(?P<id>\d+)/pay', array(
        'methods'             => 'POST',
        'permission_callback' => '__return_true',
        'callback'            => 'efca_rest_pay_simulation',
    ));

    // 3.d — Dashboard (Option B) : liste + changement de statut. PROTÉGÉ (edit_posts).
    register_rest_route('efca/v1', '/reservations', array(
        'methods'             => 'GET',
        'permission_callback' => function () { return current_user_can('edit_posts'); },
        'callback'            => 'efca_rest_list_reservations',
    ));
    register_rest_route('efca/v1', '/reservation/(?P<id>\d+)/status', array(
        'methods'             => 'POST',
        'permission_callback' => function () { return current_user_can('edit_posts'); },
        'callback'            => 'efca_rest_update_status',
    ));

    /* 3.e — STRIPE (réel) : endpoint commenté, NE PAS activer sans les clés.
       <!-- STRIPE -->
    register_rest_route('efca/v1', '/stripe/session', array(
        'methods'             => 'POST',
        'permission_callback' => '__return_true',
        'callback'            => 'efca_rest_stripe_session',
    ));
    */
});

/**
 * Validation serveur + anti-spam + création du CPT + e-mail.
 */
function efca_rest_create_reservation(WP_REST_Request $req) {

    // --- Anti-spam : honeypot ---
    $hp = $req->get_param('website');
    if (!empty($hp)) {
        return new WP_Error('efca_spam', 'Requête refusée.', array('status' => 400));
    }

    // --- (Optionnel) nonce : vérifié seulement s'il est fourni (page rendue par WP) ---
    $nonce = $req->get_header('x_wp_nonce');
    if ($nonce && !wp_verify_nonce($nonce, 'wp_rest')) {
        return new WP_Error('efca_nonce', 'Jeton invalide.', array('status' => 403));
    }

    // --- Validation des champs ---
    $name  = sanitize_text_field((string) $req->get_param('name'));
    $email = sanitize_email((string) $req->get_param('email'));
    $phone = sanitize_text_field((string) $req->get_param('phone'));
    $base  = sanitize_text_field((string) $req->get_param('base'));
    $date  = sanitize_text_field((string) $req->get_param('date'));
    $slot  = sanitize_text_field((string) $req->get_param('slot'));
    $level = sanitize_text_field((string) $req->get_param('level'));
    $msg   = sanitize_textarea_field((string) $req->get_param('message'));
    $participants = max(1, (int) $req->get_param('participants'));

    $errors = array();
    if ($name === '')           { $errors[] = 'nom'; }
    if (!is_email($email))      { $errors[] = 'email'; }
    if ($phone === '')          { $errors[] = 'téléphone'; }
    if ($date === '')           { $errors[] = 'date'; }
    if ($slot === '')           { $errors[] = 'créneau'; }
    if (!empty($errors)) {
        return new WP_Error('efca_invalid', 'Champs manquants : ' . implode(', ', $errors), array('status' => 422));
    }

    $amount = $participants * (int) EFCA_UNIT_PRICE;

    // --- Création du CPT ---
    $post_id = wp_insert_post(array(
        'post_type'   => 'efca_reservation',
        'post_status' => 'publish',
        'post_title'  => sprintf('%s — %s %s (%d p.)', $name, $date, $slot, $participants),
    ), true);

    if (is_wp_error($post_id)) {
        return new WP_Error('efca_db', 'Enregistrement impossible.', array('status' => 500));
    }

    update_post_meta($post_id, '_efca_status', 'pending');
    update_post_meta($post_id, '_efca_name', $name);
    update_post_meta($post_id, '_efca_email', $email);
    update_post_meta($post_id, '_efca_phone', $phone);
    update_post_meta($post_id, '_efca_base', $base);
    update_post_meta($post_id, '_efca_date', $date);
    update_post_meta($post_id, '_efca_slot', $slot);
    update_post_meta($post_id, '_efca_level', $level);
    update_post_meta($post_id, '_efca_participants', $participants);
    update_post_meta($post_id, '_efca_message', $msg);
    update_post_meta($post_id, '_efca_amount', $amount);

    // --- E-mail à l'équipe (Nico) ---
    $subject = sprintf('[Réservation DÉMO] %s — %s %s', $name, $date, $slot);
    $body  = "Nouvelle réservation (mode : " . EFCA_PAYMENT_MODE . ")\n\n";
    $body .= "Nom : $name\nE-mail : $email\nTéléphone : $phone\n";
    $body .= "Base : $base\nDate : $date\nCréneau : $slot\n";
    $body .= "Participants : $participants\nNiveau : $level\n";
    $body .= "Montant : $amount " . EFCA_CURRENCY . "\n";
    $body .= "Message : " . ($msg !== '' ? $msg : '—') . "\n\n";
    $body .= "Statut : en attente\nÉditer : " . admin_url('post.php?post=' . $post_id . '&action=edit') . "\n";
    wp_mail(EFCA_NOTIFY_EMAIL, $subject, $body);

    return array(
        'id'     => $post_id,
        'amount' => $amount,
        'status' => 'pending',
        'mode'   => EFCA_PAYMENT_MODE,
    );
}

/**
 * Paiement SIMULÉ : marque la réservation "payée (simulation)".
 * Actif uniquement en mode 'simulation' (jamais de transaction réelle).
 */
function efca_rest_pay_simulation(WP_REST_Request $req) {
    if (EFCA_PAYMENT_MODE !== 'simulation') {
        return new WP_Error('efca_mode', 'Paiement simulé désactivé (mode courant : ' . EFCA_PAYMENT_MODE . ').', array('status' => 403));
    }
    $id = (int) $req['id'];
    if (get_post_type($id) !== 'efca_reservation') {
        return new WP_Error('efca_404', 'Réservation introuvable.', array('status' => 404));
    }
    update_post_meta($id, '_efca_status', 'paid_sim');
    return array('id' => $id, 'status' => 'paid_sim', 'demo' => true);
}

/**
 * Dashboard — liste des réservations (protégé edit_posts).
 */
function efca_rest_list_reservations(WP_REST_Request $req) {
    $q = new WP_Query(array(
        'post_type'      => 'efca_reservation',
        'post_status'    => 'publish',
        'posts_per_page' => 200,
        'orderby'        => 'date',
        'order'          => 'DESC',
        'no_found_rows'  => true,
    ));
    $statuses = efca_statuses();
    $out = array();
    foreach ($q->posts as $p) {
        $st = get_post_meta($p->ID, '_efca_status', true);
        $out[] = array(
            'id'           => $p->ID,
            'name'         => get_post_meta($p->ID, '_efca_name', true),
            'email'        => get_post_meta($p->ID, '_efca_email', true),
            'phone'        => get_post_meta($p->ID, '_efca_phone', true),
            'base'         => get_post_meta($p->ID, '_efca_base', true),
            'date'         => get_post_meta($p->ID, '_efca_date', true),
            'slot'         => get_post_meta($p->ID, '_efca_slot', true),
            'participants' => (int) get_post_meta($p->ID, '_efca_participants', true),
            'level'        => get_post_meta($p->ID, '_efca_level', true),
            'amount'       => (int) get_post_meta($p->ID, '_efca_amount', true),
            'status'       => $st ? $st : 'pending',
            'statusLabel'  => isset($statuses[$st]) ? $statuses[$st] : '—',
            'created'      => get_the_date('c', $p),
        );
    }
    return $out;
}

/**
 * Dashboard — changement de statut (protégé edit_posts).
 */
function efca_rest_update_status(WP_REST_Request $req) {
    $id = (int) $req['id'];
    if (get_post_type($id) !== 'efca_reservation') {
        return new WP_Error('efca_404', 'Réservation introuvable.', array('status' => 404));
    }
    $status = sanitize_text_field((string) $req->get_param('status'));
    if (!array_key_exists($status, efca_statuses())) {
        return new WP_Error('efca_status', 'Statut invalide.', array('status' => 422));
    }
    update_post_meta($id, '_efca_status', $status);
    return array('id' => $id, 'status' => $status);
}

/* =============================================================================
   4) ADMIN — colonnes + changement de statut (Option A, zéro build)
   ============================================================================= */

// Colonnes de la liste.
add_filter('manage_efca_reservation_posts_columns', function ($cols) {
    $new = array('cb' => isset($cols['cb']) ? $cols['cb'] : '<input type="checkbox" />');
    $new['title']         = 'Réservation';
    $new['efca_client']   = 'Client';
    $new['efca_creneau']  = 'Date / créneau';
    $new['efca_amount']   = 'Montant';
    $new['efca_status']   = 'Statut';
    $new['date']          = 'Reçue le';
    return $new;
});

add_action('manage_efca_reservation_posts_custom_column', function ($col, $post_id) {
    if ($col === 'efca_client') {
        echo esc_html(get_post_meta($post_id, '_efca_name', true));
        $email = get_post_meta($post_id, '_efca_email', true);
        $phone = get_post_meta($post_id, '_efca_phone', true);
        echo '<br><small>' . esc_html($email) . ' · ' . esc_html($phone) . '</small>';
    } elseif ($col === 'efca_creneau') {
        echo esc_html(get_post_meta($post_id, '_efca_date', true) . ' · ' . get_post_meta($post_id, '_efca_slot', true));
        echo '<br><small>' . esc_html((int) get_post_meta($post_id, '_efca_participants', true)) . ' participant(s)</small>';
    } elseif ($col === 'efca_amount') {
        echo esc_html((int) get_post_meta($post_id, '_efca_amount', true) . ' ' . EFCA_CURRENCY);
    } elseif ($col === 'efca_status') {
        $statuses = efca_statuses();
        $st = get_post_meta($post_id, '_efca_status', true);
        $label = isset($statuses[$st]) ? $statuses[$st] : '—';
        echo '<strong>' . esc_html($label) . '</strong>';
    }
}, 10, 2);

// Meta box sur l'écran d'édition pour changer le statut.
add_action('add_meta_boxes', function () {
    add_meta_box('efca_resa_box', 'Détails & statut', 'efca_render_meta_box', 'efca_reservation', 'side', 'high');
});

function efca_render_meta_box($post) {
    wp_nonce_field('efca_save_status', 'efca_status_nonce');
    $statuses = efca_statuses();
    $current  = get_post_meta($post->ID, '_efca_status', true);
    echo '<p><label for="efca_status"><strong>Statut</strong></label></p>';
    echo '<select name="efca_status" id="efca_status" style="width:100%">';
    foreach ($statuses as $key => $label) {
        echo '<option value="' . esc_attr($key) . '" ' . selected($current, $key, false) . '>' . esc_html($label) . '</option>';
    }
    echo '</select>';

    // Récap lecture seule
    $rows = array(
        'Client'       => get_post_meta($post->ID, '_efca_name', true),
        'E-mail'       => get_post_meta($post->ID, '_efca_email', true),
        'Téléphone'    => get_post_meta($post->ID, '_efca_phone', true),
        'Base'         => get_post_meta($post->ID, '_efca_base', true),
        'Date'         => get_post_meta($post->ID, '_efca_date', true),
        'Créneau'      => get_post_meta($post->ID, '_efca_slot', true),
        'Participants' => get_post_meta($post->ID, '_efca_participants', true),
        'Niveau'       => get_post_meta($post->ID, '_efca_level', true),
        'Montant'      => ((int) get_post_meta($post->ID, '_efca_amount', true)) . ' ' . EFCA_CURRENCY,
    );
    echo '<hr><table style="width:100%;font-size:12px">';
    foreach ($rows as $k => $v) {
        echo '<tr><td style="color:#646970">' . esc_html($k) . '</td><td><strong>' . esc_html($v) . '</strong></td></tr>';
    }
    echo '</table>';
    $msg = get_post_meta($post->ID, '_efca_message', true);
    if ($msg) { echo '<p style="margin-top:8px"><em>' . esc_html($msg) . '</em></p>'; }
}

add_action('save_post_efca_reservation', function ($post_id) {
    if (defined('DOING_AUTOSAVE') && DOING_AUTOSAVE) { return; }
    if (!isset($_POST['efca_status_nonce']) || !wp_verify_nonce($_POST['efca_status_nonce'], 'efca_save_status')) { return; }
    if (!current_user_can('edit_post', $post_id)) { return; }
    if (isset($_POST['efca_status'])) {
        $val = sanitize_text_field(wp_unslash($_POST['efca_status']));
        if (array_key_exists($val, efca_statuses())) {
            update_post_meta($post_id, '_efca_status', $val);
        }
    }
});

/* =============================================================================
   OPTION B — Dashboard FRONT protégé via REST + AJAX  (IMPLÉMENTÉE)
   -----------------------------------------------------------------------------
   Routes actives ci-dessus (section 3.d) :
     GET  /efca/v1/reservations            -> efca_rest_list_reservations()
     POST /efca/v1/reservation/{id}/status -> efca_rest_update_status()
   Toutes deux protégées par permission_callback (capacité edit_posts).
   Page front : dashboard.html + assets/js/efca-dashboard.js (fetch authentifié
   cookie + X-WP-Nonce ; rendu d'un tableau avec menu de statut par ligne).
   Hors connexion, la page affiche des données d'exemple (démo).

   Pour fournir le nonce à la page statique (auth REST par cookie), injecter par ex.
   dans le footer du thème, pour les utilisateurs connectés :
     wp_add_inline_script('efca-dashboard', 'window.EFCA_NONCE="' . wp_create_nonce('wp_rest') . '";', 'before');
   ============================================================================= */

/* =============================================================================
   STRIPE (réel) — STUB COMMENTÉ, NE PAS ACTIVER SANS LES CLÉS DE NICO
   -----------------------------------------------------------------------------
   <!-- STRIPE -->
   Prérequis : composer require stripe/stripe-php  (SDK PHP) + clés en variables
   d'environnement ou options WP — JAMAIS en dur dans le code.

   function efca_stripe_secret_key() {
       // Priorité aux variables d'environnement, repli sur une option WP.
       return getenv('STRIPE_SECRET_KEY') ?: get_option('efca_stripe_secret_key', '');
   }

   function efca_rest_stripe_session(WP_REST_Request $req) {
       if (EFCA_PAYMENT_MODE !== 'stripe') {
           return new WP_Error('efca_mode', 'Mode stripe inactif.', array('status' => 403));
       }
       $sk = efca_stripe_secret_key();
       if (!$sk) {
           return new WP_Error('efca_stripe', 'Clé Stripe absente.', array('status' => 500));
       }
       require_once __DIR__ . '/vendor/autoload.php';
       \Stripe\Stripe::setApiKey($sk);

       $resa_id = (int) $req->get_param('reservation');
       $amount  = (int) get_post_meta($resa_id, '_efca_amount', true);

       $session = \Stripe\Checkout\Session::create(array(
           'ui_mode'    => 'embedded',                 // Embedded Checkout (rendu DANS la page)
           'mode'       => 'payment',
           'line_items' => array(array(
               'price_data' => array(
                   'currency'     => strtolower(EFCA_CURRENCY),
                   'product_data' => array('name' => 'Session eFoil — Mandelieu'),
                   'unit_amount'  => $amount * 100,    // centimes
               ),
               'quantity' => 1,
           )),
           'return_url' => home_url('/reservation.html?status=success&id=' . $resa_id),
           'metadata'   => array('reservation_id' => $resa_id),
       ));

       // Stripe gère son propre iframe : renvoyer le client_secret, NE PAS imbriquer.
       return array('client_secret' => $session->client_secret);
   }

   // Webhook Stripe (à implémenter) : sur 'checkout.session.completed',
   // passer la réservation au statut "payée" (réel) via update_post_meta().
   ============================================================================= */
