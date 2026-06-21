/* =============================================================================
   efca-reservation.js — Tunnel réservation -> paiement -> succès (DÉMO)
   -----------------------------------------------------------------------------
   - Pilotage par UN flag : PAYMENT_MODE = 'simulation' | 'off' | 'stripe'
     (récupéré côté serveur via /wp-json/efca/v1/config ; fallback front).
   - 'simulation' : faux checkout de bout en bout -> faux succès (aucun PSP).
   - 'off'        : réservation seule, pas de paiement.
   - 'stripe'     : Embedded Checkout (stub, NON actif — voir efca-reservation.php).
   - POST vers l'API REST WP : crée le CPT reservation + e-mail à l'équipe.
   - Dégradation gracieuse : si le backend est absent (preview statique), le
     tunnel continue en local pour la démo visuelle.
   ============================================================================= */
(function () {
  "use strict";

  var CFG = window.EFCA_CONFIG || {};
  var $ = function (s, r) { return (r || document).querySelector(s); };

  var state = {
    mode: CFG.fallbackMode || "simulation",
    unitPrice: Number(CFG.unitPrice) || 150,
    reservationId: null,
    amount: 0,
    data: null
  };

  var form = $("#efca-reservation-form");
  if (!form) { return; } // pas sur la page réservation

  var els = {
    error: $("#efca-form-error"),
    submit: $("#efca-submit"),
    steps: $("#efca-steps"),
    stepForm: $("#efca-step-form"),
    stepPay: $("#efca-step-pay"),
    stepSuccess: $("#efca-step-success"),
    paySim: $("#efca-pay-simulation"),
    payStripe: $("#efca-pay-stripe"),
    payBtn: $("#efca-pay-btn"),
    processing: $("#efca-processing"),
    paycard: $(".efca-paycard"),
    backForm: $("#efca-back-form"),
    successTitle: $("#efca-success-title"),
    successMsg: $("#efca-success-msg"),
    successTag: $("#efca-success-tag"),
    ref: $("#efca-ref")
  };

  /* ---------- utilitaires ---------- */
  function api(path) { return (CFG.apiBase || "") + path; }
  function wait(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }
  function money(n) {
    try {
      return new Intl.NumberFormat("fr-FR", {
        style: "currency", currency: CFG.currency || "EUR",
        minimumFractionDigits: 0, maximumFractionDigits: 0
      }).format(n);
    } catch (e) { return n + " €"; }
  }
  function showError(msg) { if (els.error) { els.error.textContent = msg; els.error.hidden = false; } }
  function hideError() { if (els.error) { els.error.hidden = true; } }
  function setRecap(key, val) {
    document.querySelectorAll('[data-recap="' + key + '"]').forEach(function (n) { n.textContent = val; });
  }

  async function postJSON(url, body) {
    var headers = { "Content-Type": "application/json", "Accept": "application/json" };
    if (window.EFCA_NONCE) { headers["X-WP-Nonce"] = window.EFCA_NONCE; }
    var r = await fetch(url, { method: "POST", headers: headers, body: JSON.stringify(body || {}) });
    if (!r.ok) { throw new Error("HTTP " + r.status); }
    return r.json();
  }

  /* ---------- navigation entre étapes ---------- */
  var ORDER = ["form", "pay", "success"];
  function showStep(name) {
    els.stepForm.hidden = name !== "form";
    els.stepPay.hidden = name !== "pay";
    els.stepSuccess.hidden = name !== "success";
    var idx = ORDER.indexOf(name);
    if (els.steps) {
      els.steps.querySelectorAll("li").forEach(function (li) {
        var i = ORDER.indexOf(li.getAttribute("data-step"));
        li.removeAttribute("aria-current");
        li.removeAttribute("data-done");
        if (i < idx) { li.setAttribute("data-done", "true"); }
        else if (i === idx) { li.setAttribute("aria-current", "true"); }
      });
    }
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  /* ---------- config serveur (source de vérité du mode) ---------- */
  async function loadConfig() {
    try {
      var r = await fetch(api("/wp-json/efca/v1/config"), { headers: { "Accept": "application/json" } });
      if (r.ok) {
        var c = await r.json();
        if (c.mode) { state.mode = c.mode; }
        if (c.unitPrice) { state.unitPrice = Number(c.unitPrice); }
        if (c.currency) { CFG.currency = c.currency; }
      }
    } catch (e) {
      console.debug("[EFCA] Config backend indisponible — fallback mode:", state.mode);
    }
  }

  /* ---------- collecte + validation ---------- */
  function collect() {
    var fd = new FormData(form);
    return {
      name: (fd.get("name") || "").trim(),
      email: (fd.get("email") || "").trim(),
      phone: (fd.get("phone") || "").trim(),
      base: fd.get("base") || CFG.baseName,
      date: fd.get("date") || "",
      slot: fd.get("slot") || "",
      participants: Math.max(1, parseInt(fd.get("participants"), 10) || 1),
      level: fd.get("level") || "debutant",
      message: (fd.get("message") || "").trim(),
      website: fd.get("website") || "" // honeypot
    };
  }

  /* ---------- remplissage récap + branche selon le mode ---------- */
  function fillRecap() {
    var d = state.data, line = d.participants * state.unitPrice;
    setRecap("base", d.base);
    setRecap("when", d.date + " · " + d.slot);
    setRecap("participants", String(d.participants));
    setRecap("unit", String(state.unitPrice));
    setRecap("line", money(line));
    setRecap("total", money(state.amount || line));
    setRecap("total-btn", money(state.amount || line));
  }

  function route() {
    if (state.mode === "off") {
      fillSuccess("off");
      showStep("success");
      return;
    }
    fillRecap();
    var stripe = state.mode === "stripe";
    els.paySim.hidden = stripe;
    els.payStripe.hidden = !stripe;
    if (stripe) { mountStripe(); }
    showStep("pay");
  }

  function fillSuccess(mode) {
    if (mode === "off") {
      els.successTitle.textContent = "Réservation enregistrée";
      els.successMsg.textContent = "Votre demande est bien reçue (statut : en attente). Nous vous recontactons pour confirmer le créneau.";
    } else {
      els.successTitle.textContent = "Paiement confirmé";
      els.successMsg.textContent = "Votre réservation de " + money(state.amount) + " est confirmée. Un e-mail récapitulatif vous est envoyé.";
    }
    if (els.successTag) { els.successTag.textContent = "Simulation / Démo"; }
    if (els.ref) { els.ref.textContent = state.reservationId; }
  }

  /* ---------- soumission du formulaire ---------- */
  form.addEventListener("submit", async function (e) {
    e.preventDefault();
    hideError();
    var d = collect();
    if (d.website) { return; }                         // honeypot rempli -> bot, on ignore
    if (!form.checkValidity()) { form.reportValidity(); return; }

    els.submit.disabled = true;
    els.submit.textContent = "Envoi…";
    var res;
    try {
      res = await postJSON(api("/wp-json/efca/v1/reservation"), d);
    } catch (err) {
      if (state.mode === "stripe") {            // Stripe exige le backend
        els.submit.disabled = false; els.submit.textContent = "Continuer";
        showError("Service de réservation momentanément indisponible. Réessayez ou appelez le 06 35 30 50 67.");
        return;
      }
      // preview statique sans WordPress : on continue en local pour la démo
      console.debug("[EFCA] Backend absent — réservation simulée côté front.");
      res = { id: "DEMO-" + Date.now(), amount: d.participants * state.unitPrice, status: "pending", _fallback: true };
    }
    els.submit.disabled = false; els.submit.textContent = "Continuer";

    state.reservationId = res.id;
    state.amount = res.amount || (d.participants * state.unitPrice);
    state.data = d;
    route();
  });

  /* ---------- paiement simulé ---------- */
  if (els.payBtn) {
    els.payBtn.addEventListener("click", async function () {
      if (els.paycard) { els.paycard.style.display = "none"; }
      if (els.processing) { els.processing.hidden = false; }
      // Mise à jour best-effort du statut côté serveur (payée-simulation)
      try {
        if (state.reservationId && String(state.reservationId).indexOf("DEMO-") !== 0) {
          await postJSON(api("/wp-json/efca/v1/reservation/" + state.reservationId + "/pay"), {});
        }
      } catch (e) { /* démo : on continue malgré tout */ }
      await wait(1800); // fausse animation de traitement
      fillSuccess("simulation");
      showStep("success");
    });
  }

  if (els.backForm) {
    els.backForm.addEventListener("click", function () {
      if (els.paycard) { els.paycard.style.display = ""; }
      if (els.processing) { els.processing.hidden = true; }
      showStep("form");
    });
  }

  /* ---------- STRIPE (stub front, NON actif) ----------
     En mode 'stripe', on monterait ici l'Embedded Checkout. Le client_secret
     vient de l'endpoint REST backend (voir efca-reservation.php, section STRIPE).
     NE PAS imbriquer dans un autre iframe : Stripe gère son propre iframe. */
  function mountStripe() {
    // <!-- STRIPE -->
    // Exemple (à activer avec la clé publique + le SDK stripe.js) :
    //
    //   const stripe = Stripe(window.EFCA_STRIPE_PK);
    //   const r = await postJSON(api('/wp-json/efca/v1/stripe/session'), { reservation: state.reservationId });
    //   const checkout = await stripe.initEmbeddedCheckout({ clientSecret: r.client_secret });
    //   checkout.mount('#efca-stripe-mount');
    //
    console.debug("[EFCA] Mode 'stripe' : montage Embedded Checkout à activer (stub).");
  }

  /* ---------- init ---------- */
  loadConfig();
})();
