/* =============================================================================
   efca-dashboard.js — Tableau de bord des réservations (Option B : front + REST)
   -----------------------------------------------------------------------------
   - GET  /wp-json/efca/v1/reservations           (liste, capacité edit_posts)
   - POST /wp-json/efca/v1/reservation/{id}/status (changement de statut)
   - Auth réelle : cookie WordPress + X-WP-Nonce (utilisateur connecté).
   - Hors connexion / sans backend : DONNÉES D'EXEMPLE pour la démo visuelle.
   ============================================================================= */
(function () {
  "use strict";

  var CFG = window.EFCA_CONFIG || {};
  var $ = function (s, r) { return (r || document).querySelector(s); };
  function api(p) { return (CFG.apiBase || "") + p; }

  var STATUSES = {
    pending: "En attente",
    validated: "Validée",
    refused: "Refusée",
    paid_sim: "Payée (simulation)"
  };

  var state = { items: [], live: false };

  var els = {
    conn: $("#efca-conn"),
    connLabel: $("#efca-conn-label"),
    rows: $("#efca-rows"),
    empty: $("#efca-empty"),
    filter: $("#efca-filter"),
    refresh: $("#efca-refresh")
  };

  function money(n) {
    try {
      return new Intl.NumberFormat("fr-FR", { style: "currency", currency: CFG.currency || "EUR", minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(n);
    } catch (e) { return n + " €"; }
  }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  /* ---------- données d'exemple (preview / non connecté) ---------- */
  function sampleData() {
    return [
      { id: "DEMO-1", name: "Camille Roux", email: "camille.roux@email.fr", phone: "06 12 34 56 78", base: "Mandelieu — Plage des Dauphins", date: "2026-06-14", slot: "10:30", participants: 2, level: "debutant", amount: 300, status: "paid_sim" },
      { id: "DEMO-2", name: "Thomas Bernard", email: "t.bernard@email.fr", phone: "06 98 76 54 32", base: "Mandelieu — Plage des Dauphins", date: "2026-06-15", slot: "14:00", participants: 1, level: "intermediaire", amount: 150, status: "pending" },
      { id: "DEMO-3", name: "Léa Martin", email: "lea.martin@email.fr", phone: "07 11 22 33 44", base: "Mandelieu — Plage des Dauphins", date: "2026-06-16", slot: "09:00", participants: 3, level: "debutant", amount: 450, status: "validated" },
      { id: "DEMO-4", name: "Hugo Lefèvre", email: "hugo.l@email.fr", phone: "06 55 44 33 22", base: "Mandelieu — Plage des Dauphins", date: "2026-06-12", slot: "17:00", participants: 1, level: "confirme", amount: 150, status: "refused" },
      { id: "DEMO-5", name: "Inès Garcia", email: "ines.garcia@email.fr", phone: "07 88 77 66 55", base: "Mandelieu — Plage des Dauphins", date: "2026-06-18", slot: "15:30", participants: 2, level: "debutant", amount: 300, status: "pending" }
    ];
  }

  /* ---------- connexion indicateur ---------- */
  function setConn(live) {
    state.live = live;
    if (els.conn) { els.conn.setAttribute("data-state", live ? "live" : "demo"); }
    if (els.connLabel) { els.connLabel.textContent = live ? "Connecté à WordPress" : "Mode démo (données d'exemple)"; }
  }

  /* ---------- chargement ---------- */
  async function load() {
    try {
      var headers = { "Accept": "application/json" };
      if (window.EFCA_NONCE) { headers["X-WP-Nonce"] = window.EFCA_NONCE; }
      var r = await fetch(api("/wp-json/efca/v1/reservations"), { headers: headers, credentials: "include" });
      if (!r.ok) { throw new Error("HTTP " + r.status); }
      state.items = await r.json();
      setConn(true);
    } catch (e) {
      console.debug("[EFCA] Liste backend indisponible — données d'exemple.", e.message);
      state.items = sampleData();
      setConn(false);
    }
    render();
  }

  /* ---------- statistiques ---------- */
  function renderStats() {
    var counts = { total: state.items.length, pending: 0, validated: 0, paid_sim: 0, refused: 0 };
    state.items.forEach(function (it) { if (counts[it.status] != null) { counts[it.status]++; } });
    Object.keys(counts).forEach(function (k) {
      var n = document.querySelector('[data-stat="' + k + '"]');
      if (n) { n.textContent = counts[k]; }
    });
  }

  /* ---------- rendu de la table ---------- */
  function statusOptions(current) {
    return Object.keys(STATUSES).map(function (k) {
      return '<option value="' + k + '"' + (k === current ? " selected" : "") + ">" + esc(STATUSES[k]) + "</option>";
    }).join("");
  }

  function render() {
    renderStats();
    var f = els.filter ? els.filter.value : "";
    var list = f ? state.items.filter(function (it) { return it.status === f; }) : state.items;

    if (!list.length) {
      els.rows.innerHTML = "";
      if (els.empty) { els.empty.hidden = false; }
      return;
    }
    if (els.empty) { els.empty.hidden = true; }

    els.rows.innerHTML = list.map(function (it) {
      var label = STATUSES[it.status] || "—";
      return "<tr>" +
        "<td><strong>" + esc(it.name) + "</strong></td>" +
        "<td><small>" + esc(it.email) + "<br>" + esc(it.phone) + "</small></td>" +
        "<td>" + esc(it.date) + " · " + esc(it.slot) + "<br><small>" + esc(it.base) + "</small></td>" +
        "<td>" + esc(it.participants) + "</td>" +
        '<td class="efca-table__amount">' + esc(money(it.amount)) + "</td>" +
        '<td><span class="efca-status efca-status--' + esc(it.status) + '">' + esc(label) + "</span></td>" +
        '<td><select class="efca-status-select" data-id="' + esc(it.id) + '" aria-label="Changer le statut de ' + esc(it.name) + '">' + statusOptions(it.status) + "</select></td>" +
        "</tr>";
    }).join("");
  }

  /* ---------- changement de statut ---------- */
  async function changeStatus(id, status) {
    var item = state.items.filter(function (it) { return String(it.id) === String(id); })[0];
    if (!item) { return; }
    var prev = item.status;
    item.status = status; // optimiste
    render();

    if (!state.live) { return; } // mode démo : local uniquement

    try {
      var headers = { "Content-Type": "application/json", "Accept": "application/json" };
      if (window.EFCA_NONCE) { headers["X-WP-Nonce"] = window.EFCA_NONCE; }
      var r = await fetch(api("/wp-json/efca/v1/reservation/" + encodeURIComponent(id) + "/status"), {
        method: "POST", headers: headers, credentials: "include", body: JSON.stringify({ status: status })
      });
      if (!r.ok) { throw new Error("HTTP " + r.status); }
    } catch (e) {
      item.status = prev; // rollback
      render();
      alert("Échec de la mise à jour du statut. Vérifiez votre connexion / vos droits.");
    }
  }

  /* ---------- événements ---------- */
  if (els.rows) {
    els.rows.addEventListener("change", function (e) {
      var sel = e.target.closest(".efca-status-select");
      if (sel) { changeStatus(sel.getAttribute("data-id"), sel.value); }
    });
  }
  if (els.filter) { els.filter.addEventListener("change", render); }
  if (els.refresh) { els.refresh.addEventListener("click", load); }

  load();
})();
