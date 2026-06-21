#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Construit un TRIEUR CONTEXTUEL : reprend la page V1 section par section.
Chaque emplacement (slot) de la page est un cadre cliquable ; on choisit la photo
depuis le pool DIRECTEMENT à sa place. La galerie défilante = sélection multiple.
Bac "à proscrire" (pré-rempli depuis tools/packs.json). Export / import JSON.

Entrée : trieur-photos.html (manifeste des vignettes déjà généré) + tools/packs.json
Sortie : trieur-contextuel.html
Usage  : python tools/build_context_sorter.py
"""
import json, re, os

# ---- modèle des sections / slots, dérivé du template como-beauvallon-efoil.html ----
SECTIONS = [
 {"t":"① Héros","d":"Boucle vidéo plein écran (drone, coucher de soleil). Ici tu choisis l'image de repli / poster ; la vidéo reste hero-video.mp4.",
  "slots":[{"id":"HERO_VIDEO","l":"Héros — poster vidéo","r":"16:9","h":"drone golfe / rider en vol — plein écran"}]},
 {"t":"② Le lieu — le domaine","d":"Grande image d'ouverture : le domaine au calme.",
  "slots":[{"id":"LIEU","l":"Le lieu / château","r":"4:3","h":"domaine / ponton / eau au calme du matin"}]},
 {"t":"③ Mosaïque défilante (auto)","d":"Bandeaux qui défilent tout seuls, en boucle. Sélectionne PLUSIEURS photos — c'est le pool qui alimente les deux mosaïques de la page.",
  "slots":[{"id":"GALERIE_DEFILE","l":"Pool mosaïque défilante","r":"multi","h":"plusieurs photos (golfe, riders, ambiances)","multi":True}]},
 {"t":"④ L'expérience","d":"Trois temps forts, une image chacun.",
  "slots":[
    {"id":"EXP_1","l":"Le silence","r":"16:9","h":"un rider glisse en silence au couchant"},
    {"id":"EXP_2","l":"L'apesanteur","r":"4:3","h":"riders portés par l'aile au-dessus du golfe"},
    {"id":"EXP_3","l":"À votre rythme","r":"3:4","h":"un moniteur accompagne un débutant"}]},
 {"t":"⑤ Pour qui","d":"Quatre profils.",
  "slots":[
    {"id":"WHO_1","l":"Débutant accompagné","r":"4:3","h":"débutant + moniteur"},
    {"id":"WHO_2","l":"Rider confirmé","r":"4:3","h":"session libre sur le golfe"},
    {"id":"WHO_3","l":"Encadrement & sécurité","r":"4:3","h":"briefing / matériel de sécu"},
    {"id":"WHO_4","l":"Matériel Lift","r":"4:3","h":"foils électriques carbone (détail)"}]},
 {"t":"⑥ Galerie","d":"Les 14 cartes de la galerie principale (chacune légendée).",
  "slots":[
    {"id":"RIDE_1","l":"Le vol","r":"3:4","h":"rideuses en vol, eau calme"},
    {"id":"RIDE_2","l":"La roche rouge","r":"4:3","h":"riders devant les roches rouges"},
    {"id":"RIDE_3","l":"Lérins","r":"3:4","h":"planche Lift orange devant le fort"},
    {"id":"RIDE_4","l":"La formation","r":"4:3","h":"riders en formation"},
    {"id":"RIDE_5","l":"L'Estérel","r":"3:4","h":"couple sur une planche, massif rouge"},
    {"id":"RIDE_6","l":"Les yachts","r":"3:4","h":"devant le port et les yachts"},
    {"id":"RIDE_7","l":"La calanque","r":"3:4","h":"au pied des roches rouges"},
    {"id":"RIDE_8","l":"Le sourire","r":"3:4","h":"rideuse souriante, planche verte"},
    {"id":"RIDE_9","l":"Le golfe","r":"4:3","h":"riders devant la roche rouge"},
    {"id":"RIDE_10","l":"Le matin","r":"3:4","h":"rider en vol au matin"},
    {"id":"RIDE_11","l":"Au mouillage","r":"4:3","h":"riders et yachts au mouillage"},
    {"id":"RIDE_12","l":"La glisse","r":"3:4","h":"rider sur l'eau calme"},
    {"id":"RIDE_13","l":"L'Estérel","r":"4:3","h":"roche rouge de l'Estérel"},
    {"id":"RIDE_14","l":"La lumière","r":"3:4","h":"rider, golden hour"}]},
 {"t":"⑦ Le déroulé","d":"Les 4 étapes d'une session (16:9).",
  "slots":[
    {"id":"SESSION_1","l":"Briefing","r":"16:9","h":"briefing à terre"},
    {"id":"SESSION_2","l":"Équipement","r":"16:9","h":"mise à l'eau de l'équipement"},
    {"id":"SESSION_3","l":"À l'eau","r":"16:9","h":"les premiers mètres"},
    {"id":"SESSION_4","l":"Le vol","r":"16:9","h":"le vol au-dessus du golfe"}]},
 {"t":"⑧ Beach club","d":"Le beach club du domaine.",
  "slots":[
    {"id":"BEACH_1","l":"Vue aérienne beach","r":"16:9","h":"sable, parasols dorés, eau turquoise (drone)"},
    {"id":"BEACH_2","l":"Parasols","r":"4:3","h":"parasols dorés face au golfe"}]},
 {"t":"⑨ Le spot","d":"Vue aérienne du domaine avec l'hôtel.",
  "slots":[{"id":"SPOT","l":"Le spot — l'hôtel","r":"4:3","h":"aérien : hôtel Belle Époque, plage, golfe"}]},
]

# ---- récupère le manifeste de vignettes depuis le trieur plat ----
src = open('trieur-photos.html', encoding='utf-8').read()
m = re.search(r'var PHOTOS\s*=\s*(\[.*?\]);', src, re.S)
if not m:
    raise SystemExit("Manifeste introuvable dans trieur-photos.html — lance d'abord python tools/build_sorter.py")
manifest = json.loads(m.group(1))

# ---- proscrire par défaut depuis packs.json ----
default_proscrire = []
if os.path.exists('tools/packs.json'):
    pk = json.load(open('tools/packs.json', encoding='utf-8'))
    default_proscrire = pk.get('packs', {}).get('proscrire', [])

HTML = r'''<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Trieur contextuel — COMO Le Beauvallon</title>
<style>
:root{--bg:#f3e9da;--panel:#fbf5ec;--ink:#3a2c20;--dim:#94806a;--line:#e4d6c2;
  --accent:#c0623b;--accent-ink:#fff;--gold:#c2992f;--ok:#7a8a4e;--bad:#b5482e;--shadow:0 6px 22px rgba(58,44,32,.12)}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 "Switzer",system-ui,Segoe UI,Roboto,sans-serif}
a{color:var(--accent)}
header{position:sticky;top:0;z-index:30;background:rgba(243,233,218,.97);backdrop-filter:blur(6px);border-bottom:1px solid var(--line);padding:12px 18px}
.h-top{display:flex;flex-wrap:wrap;gap:12px;align-items:center;justify-content:space-between}
h1{margin:0;font:600 16px/1.2 system-ui;letter-spacing:.04em;text-transform:uppercase}
h1 b{color:var(--accent)}
.tools{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.btn{border:1px solid var(--line);background:var(--panel);color:var(--ink);padding:8px 14px;border-radius:8px;cursor:pointer;font:inherit;font-size:13px}
.btn:hover{border-color:var(--dim)}
.btn.primary{background:var(--accent);color:var(--accent-ink);border-color:var(--accent);font-weight:600}
.prog{margin-top:10px;display:flex;gap:16px;flex-wrap:wrap;font-size:12.5px;color:var(--dim)}
.prog b{color:var(--ink)}
.bar{height:6px;background:var(--line);border-radius:99px;overflow:hidden;flex:1;min-width:120px;align-self:center;max-width:260px}
.bar i{display:block;height:100%;background:var(--gold)}
main{max-width:1080px;margin:0 auto;padding:18px}
section.sec{margin:26px 0 8px}
.sec>h2{font:600 20px/1.2 "Archivo",system-ui;margin:0 0 2px;letter-spacing:.01em}
.sec>p.d{margin:0 0 14px;color:var(--dim);font-size:13.5px;max-width:70ch}
.slots{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:14px}
.slot{background:var(--panel);border:1px solid var(--line);border-radius:12px;overflow:hidden;box-shadow:var(--shadow)}
.slot .lab{padding:10px 12px 8px;display:flex;align-items:baseline;justify-content:space-between;gap:8px}
.slot .lab b{font-size:14px}
.slot .lab .r{font-size:10.5px;color:var(--dim);border:1px solid var(--line);border-radius:99px;padding:1px 7px;white-space:nowrap}
.slot .hint{padding:0 12px 8px;color:var(--dim);font-size:12px;min-height:30px}
.frame{position:relative;margin:0 12px 12px;border-radius:8px;overflow:hidden;background:#efe3d2;border:2px dashed var(--line);cursor:pointer;display:grid;place-items:center;min-height:130px}
.frame.set{border-style:solid;border-color:var(--gold)}
.frame img{width:100%;height:100%;object-fit:cover;display:block}
.frame .empty{color:var(--dim);font-size:13px;text-align:center;padding:20px}
.frame .empty .plus{font-size:26px;display:block;margin-bottom:4px;color:var(--accent)}
.frame .x{position:absolute;top:6px;right:6px;background:rgba(58,44,32,.78);color:#fff;border:none;border-radius:6px;width:26px;height:26px;cursor:pointer;font-size:14px;line-height:1;display:none}
.frame.set:hover .x{display:block}
.frame .chg{position:absolute;left:0;right:0;bottom:0;background:linear-gradient(transparent,rgba(58,44,32,.8));color:#fff;font-size:11.5px;padding:14px 8px 6px;opacity:0;transition:.15s;text-align:center}
.frame.set:hover .chg{opacity:1}
/* pool multi */
.pool{margin:0 12px 12px}
.pool .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(74px,1fr));gap:5px;margin-bottom:8px}
.pool .grid .pt{position:relative;aspect-ratio:1;border-radius:6px;overflow:hidden;background:#efe3d2}
.pool .grid .pt img{width:100%;height:100%;object-fit:cover}
.pool .grid .pt button{position:absolute;top:2px;right:2px;background:rgba(58,44,32,.8);color:#fff;border:none;border-radius:5px;width:20px;height:20px;cursor:pointer;font-size:12px;line-height:1}
.pool .empty{color:var(--dim);font-size:12.5px;padding:10px 0}
.ratio-169{aspect-ratio:16/9}.ratio-43{aspect-ratio:4/3}.ratio-34{aspect-ratio:3/4}
/* picker */
.pick{position:fixed;inset:0;background:rgba(36,26,18,.62);z-index:60;display:none}
.pick.show{display:block}
.pick__panel{position:absolute;inset:4vh 3vw;background:var(--panel);border-radius:14px;display:flex;flex-direction:column;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,.4)}
.pick__head{padding:14px 18px;border-bottom:1px solid var(--line);display:flex;flex-wrap:wrap;gap:10px;align-items:center}
.pick__head h3{margin:0;font:600 16px system-ui}
.pick__head .sub{color:var(--dim);font-size:12.5px}
.pick__filters{display:flex;gap:6px;flex-wrap:wrap;margin-left:auto}
.chip{border:1px solid var(--line);background:var(--bg);color:var(--ink);border-radius:99px;padding:5px 11px;font-size:12px;cursor:pointer}
.chip.on{background:var(--ink);color:#fff;border-color:var(--ink)}
.pick__body{flex:1;overflow:auto;padding:14px 18px}
.pgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(132px,1fr));gap:9px}
.cell{position:relative;border-radius:8px;overflow:hidden;background:#efe3d2;cursor:pointer;aspect-ratio:1;border:3px solid transparent}
.cell img{width:100%;height:100%;object-fit:cover;display:block}
.cell.sel{border-color:var(--gold)}
.cell.used{outline:0}
.cell .g{position:absolute;left:4px;top:4px;background:rgba(58,44,32,.6);color:#fff;font-size:9.5px;padding:1px 5px;border-radius:4px}
.cell .u{position:absolute;left:4px;bottom:4px;right:4px;background:rgba(192,98,59,.92);color:#fff;font-size:9.5px;padding:2px 5px;border-radius:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.cell .ban{position:absolute;right:4px;top:4px;background:rgba(58,44,32,.7);color:#fff;border:none;border-radius:5px;width:24px;height:24px;cursor:pointer;font-size:13px;line-height:1}
.cell .ban.on{background:var(--bad)}
.cell.proscrit{opacity:.34;filter:grayscale(.7)}
.cell .chk{position:absolute;right:4px;bottom:4px;background:var(--gold);color:#3a2c20;border-radius:50%;width:22px;height:22px;display:none;place-items:center;font-size:13px;font-weight:700}
.cell.sel .chk{display:grid}
.pick__foot{padding:10px 18px;border-top:1px solid var(--line);display:flex;gap:10px;align-items:center;font-size:12.5px;color:var(--dim)}
footer{max-width:1080px;margin:0 auto;padding:20px 18px 60px;color:var(--dim);font-size:12.5px}
</style></head>
<body>
<header>
  <div class="h-top">
    <h1>Trieur contextuel — <b>COMO Le Beauvallon</b></h1>
    <div class="tools">
      <button class="btn primary" id="export">Exporter JSON</button>
      <label class="btn">Importer JSON<input type="file" id="import" accept="application/json" hidden></label>
      <button class="btn" id="reset">Réinitialiser</button>
    </div>
  </div>
  <div class="prog">
    <span>Emplacements remplis : <b id="pcount">0</b></span>
    <span class="bar"><i id="pbar" style="width:0%"></i></span>
    <span>Mosaïque défilante : <b id="poolcount">0</b></span>
    <span>À proscrire : <b id="proscount">0</b></span>
  </div>
</header>
<main id="page"></main>
<footer>Clique un cadre pour choisir sa photo. La galerie défilante accepte plusieurs photos. Dans le sélecteur, le bouton ⊘ marque une photo « à proscrire ». Sauvegarde auto dans le navigateur — pense à <b>Exporter JSON</b> pour me l'envoyer.</footer>

<div class="pick" id="pick"><div class="pick__panel">
  <div class="pick__head">
    <div><h3 id="pkTitle">Choisir une photo</h3><div class="sub" id="pkSub"></div></div>
    <div class="pick__filters" id="pkFilters"></div>
  </div>
  <div class="pick__body"><div class="pgrid" id="pkGrid"></div></div>
  <div class="pick__foot"><span id="pkFoot"></span><button class="btn" id="pkClose" style="margin-left:auto">Fermer</button></div>
</div></div>

<script>
var PHOTOS = /*__MANIFEST__*/;
var SECTIONS = /*__SECTIONS__*/;
var DEFAULT_PROSCRIRE = /*__PROSCRIRE__*/;
var PH = {}; PHOTOS.forEach(function(p){PH[p.id]=p});
// index slot -> meta
var SLOTMETA={}; SECTIONS.forEach(function(s){s.slots.forEach(function(sl){SLOTMETA[sl.id]=sl})});
var SINGLE=[]; SECTIONS.forEach(function(s){s.slots.forEach(function(sl){if(!sl.multi)SINGLE.push(sl.id)})});

var LS='cbCtx1_';
function load(k,d){try{var v=JSON.parse(localStorage.getItem(LS+k));return v==null?d:v}catch(e){return d}}
function save(){localStorage.setItem(LS+'assign',JSON.stringify(assign));localStorage.setItem(LS+'pros',JSON.stringify(proscrire))}
var assign=load('assign',null), proscrire=load('pros',null);
if(assign===null){assign={}}
if(proscrire===null){proscrire=DEFAULT_PROSCRIRE.filter(function(id){return PH[id]})}

function ratioClass(r){return r==='16:9'?'ratio-169':r==='4:3'?'ratio-43':r==='3:4'?'ratio-34':'ratio-43'}
function thumb(id){return PH[id]?PH[id].t:''}
function usedBy(id){ // liste des slots simples qui utilisent cette photo
  var out=[];SINGLE.forEach(function(sid){if((assign[sid]||[]).indexOf(id)>=0)out.push(SLOTMETA[sid].l)});return out}

/* ---------- rendu de la page ---------- */
function renderPage(){
  var page=document.getElementById('page');page.innerHTML='';
  SECTIONS.forEach(function(s){
    var sec=document.createElement('section');sec.className='sec';
    sec.innerHTML='<h2>'+s.t+'</h2><p class="d">'+s.d+'</p>';
    var wrap=document.createElement('div');wrap.className='slots';
    s.slots.forEach(function(sl){wrap.appendChild(sl.multi?poolCard(sl):slotCard(sl))});
    sec.appendChild(wrap);page.appendChild(sec);
  });
  updateProg();
}
function slotCard(sl){
  var d=document.createElement('div');d.className='slot';
  var cur=(assign[sl.id]||[])[0];
  var inner='<div class="lab"><b>'+sl.l+'</b><span class="r">'+sl.r+'</span></div><div class="hint">'+sl.h+'</div>';
  if(cur){
    inner+='<div class="frame set '+ratioClass(sl.r)+'"><img src="'+thumb(cur)+'" alt=""><button class="x" title="Retirer">✕</button><div class="chg">Changer</div></div>';
  }else{
    inner+='<div class="frame '+ratioClass(sl.r)+'"><div class="empty"><span class="plus">＋</span>Choisir une photo</div></div>';
  }
  d.innerHTML=inner;
  var fr=d.querySelector('.frame');
  fr.onclick=function(){openPicker(sl.id)};
  var x=d.querySelector('.x');if(x)x.onclick=function(e){e.stopPropagation();delete assign[sl.id];save();renderPage()};
  return d;
}
function poolCard(sl){
  var d=document.createElement('div');d.className='slot';
  var arr=assign[sl.id]||[];
  var g='';arr.forEach(function(id){g+='<div class="pt"><img src="'+thumb(id)+'" alt=""><button data-id="'+id+'" title="Retirer">✕</button></div>'});
  d.innerHTML='<div class="lab"><b>'+sl.l+'</b><span class="r">'+arr.length+' photo'+(arr.length>1?'s':'')+'</span></div><div class="hint">'+sl.h+'</div>'
    +'<div class="pool"><div class="grid">'+(g||'')+'</div>'+(arr.length?'':'<div class="empty">Aucune photo — clique « Ajouter / gérer ».</div>')
    +'<button class="btn" style="width:100%">Ajouter / gérer les photos</button></div>';
  d.querySelector('.btn').onclick=function(){openPicker(sl.id)};
  d.querySelectorAll('.pt button').forEach(function(b){b.onclick=function(){var id=b.getAttribute('data-id');assign[sl.id]=(assign[sl.id]||[]).filter(function(x){return x!==id});save();renderPage()}});
  return d;
}
function updateProg(){
  var filled=SINGLE.filter(function(id){return (assign[id]||[]).length}).length;
  document.getElementById('pcount').textContent=filled+' / '+SINGLE.length;
  document.getElementById('pbar').style.width=(100*filled/SINGLE.length)+'%';
  var pool=0;SECTIONS.forEach(function(s){s.slots.forEach(function(sl){if(sl.multi)pool+=(assign[sl.id]||[]).length})});
  document.getElementById('poolcount').textContent=pool;
  document.getElementById('proscount').textContent=proscrire.length;
}

/* ---------- sélecteur (picker) ---------- */
var pkSlot=null, pkFilter='avail';
var GROUPS=(function(){var s={};PHOTOS.forEach(function(p){s[p.g]=1});return Object.keys(s).sort()})();
function openPicker(slotId){pkSlot=slotId;pkFilter='avail';
  var sl=SLOTMETA[slotId];
  document.getElementById('pkTitle').textContent=(sl.multi?'Mosaïque défilante — ':'Emplacement — ')+sl.l;
  document.getElementById('pkSub').textContent=sl.h+' · '+(sl.multi?'sélection multiple, clique pour ajouter/retirer':'clique une photo pour la placer');
  document.getElementById('pick').classList.add('show');renderFilters();renderPick();
}
function closePicker(){document.getElementById('pick').classList.remove('show');pkSlot=null}
function renderFilters(){
  var f=document.getElementById('pkFilters');f.innerHTML='';
  function chip(id,label){var c=document.createElement('span');c.className='chip'+(pkFilter===id?' on':'');c.textContent=label;c.onclick=function(){pkFilter=id;renderFilters();renderPick()};f.appendChild(c)}
  chip('avail','Disponibles');chip('all','Toutes ('+PHOTOS.length+')');chip('pros','Proscrites ('+proscrire.length+')');
  GROUPS.forEach(function(g){chip('g:'+g,g)});
}
function passFilter(p){
  var pros=proscrire.indexOf(p.id)>=0;
  if(pkFilter==='all')return true;
  if(pkFilter==='pros')return pros;
  if(pkFilter==='avail')return !pros && usedBy(p.id).length===0;
  if(pkFilter.indexOf('g:')===0)return p.g===pkFilter.slice(2);
  return true;
}
function renderPick(){
  var sl=SLOTMETA[pkSlot], grid=document.getElementById('pkGrid');grid.innerHTML='';
  var sel=assign[pkSlot]||[];var shown=0;
  PHOTOS.forEach(function(p){
    if(!passFilter(p))return;shown++;
    var pros=proscrire.indexOf(p.id)>=0, isSel=sel.indexOf(p.id)>=0, used=usedBy(p.id).filter(function(l){return l!==sl.l});
    var c=document.createElement('div');c.className='cell'+(isSel?' sel':'')+(pros?' proscrit':'');
    c.innerHTML='<img loading="lazy" src="'+p.t+'" alt=""><span class="g">'+p.g+'</span>'
      +(used.length?'<span class="u" title="déjà utilisée">déjà : '+used.join(', ')+'</span>':'')
      +'<button class="ban'+(pros?' on':'')+'" title="À proscrire">⊘</button><span class="chk">✓</span>';
    c.querySelector('.ban').onclick=function(e){e.stopPropagation();toggleProscrire(p.id)};
    c.onclick=function(){choose(p.id)};
    grid.appendChild(c);
  });
  document.getElementById('pkFoot').textContent=shown+' photo'+(shown>1?'s':'')+' affichée'+(shown>1?'s':'')
    +(sl.multi?(' · '+sel.length+' sélectionnée'+(sel.length>1?'s':'')+' pour ce bandeau'):'');
}
function choose(id){
  var sl=SLOTMETA[pkSlot];
  if(sl.multi){var a=assign[pkSlot]||[];var i=a.indexOf(id);if(i<0)a.push(id);else a.splice(i,1);if(a.length)assign[pkSlot]=a;else delete assign[pkSlot];save();renderPick();renderPage();}
  else{assign[pkSlot]=[id];save();renderPage();closePicker();}
}
function toggleProscrire(id){var i=proscrire.indexOf(id);if(i<0)proscrire.push(id);else proscrire.splice(i,1);save();renderFilters();renderPick();updateProg()}

document.getElementById('pkClose').onclick=closePicker;
document.getElementById('pick').onclick=function(e){if(e.target===this)closePicker()};
document.addEventListener('keydown',function(e){if(e.key==='Escape')closePicker()});

/* ---------- export / import / reset ---------- */
document.getElementById('export').onclick=function(){
  var slots={};SECTIONS.forEach(function(s){s.slots.forEach(function(sl){slots[sl.id]=assign[sl.id]||[]})});
  var out={version:2,tool:"trieur-contextuel",projet:"como-beauvallon",
    slots:slots,proscrire:proscrire,
    counts:{remplis:SINGLE.filter(function(id){return (assign[id]||[]).length}).length,total_slots:SINGLE.length,
            mosaique:(assign['GALERIE_DEFILE']||[]).length,proscrire:proscrire.length},
    pool_total:PHOTOS.length};
  var b=new Blob([JSON.stringify(out,null,2)],{type:'application/json'});
  var a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='como-beauvallon-tri-contextuel.json';a.click();
};
document.getElementById('import').onchange=function(e){var f=e.target.files[0];if(!f)return;var r=new FileReader();
  r.onload=function(){try{var d=JSON.parse(r.result);
    if(d.slots){assign={};Object.keys(d.slots).forEach(function(k){if(d.slots[k]&&d.slots[k].length)assign[k]=d.slots[k]})}
    if(d.proscrire)proscrire=d.proscrire;
    save();renderPage();alert('Tri importé.');}catch(err){alert('JSON invalide')}};r.readAsText(f)};
document.getElementById('reset').onclick=function(){if(confirm('Effacer tout le tri (emplacements + proscrits) ?')){assign={};proscrire=DEFAULT_PROSCRIRE.filter(function(id){return PH[id]});save();renderPage()}};

renderPage();
</script></body></html>'''

HTML = (HTML
        .replace('/*__MANIFEST__*/', json.dumps(manifest, ensure_ascii=False))
        .replace('/*__SECTIONS__*/', json.dumps(SECTIONS, ensure_ascii=False))
        .replace('/*__PROSCRIRE__*/', json.dumps(default_proscrire, ensure_ascii=False)))
open('trieur-contextuel.html', 'w', encoding='utf-8').write(HTML)
nslots = sum(len(s['slots']) for s in SECTIONS)
print(f"trieur-contextuel.html -> {len(SECTIONS)} sections, {nslots} emplacements, "
      f"{len(manifest)} photos dans le pool, {len(default_proscrire)} proscrites par défaut")
