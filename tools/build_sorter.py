#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Construit un TRIEUR de photos HTML autonome : génère des vignettes de toutes les
photos + frames vidéo (sauf dubai), et un trieur-photos.html où l'on tague chaque
image par catégories/packs (multi-tag), avec export/import JSON et sauvegarde auto.

Usage : python tools/build_sorter.py
Sortie : medias/thumbs/*.webp  +  trieur-photos.html
"""
import glob, os, re, json
from PIL import Image, ImageOps

HTML_TEMPLATE = r'''<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Trieur photos — eFoil Côte d'Azur</title>
<style>
:root{--bg:#15130f;--panel:#1d1a15;--ink:#f2ead9;--dim:#a99e88;--line:#332e25;--accent:#e0a92e}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.4 system-ui,Segoe UI,Roboto,sans-serif}
header{position:sticky;top:0;z-index:10;background:rgba(21,19,15,.97);border-bottom:1px solid var(--line);padding:10px 14px}
h1{margin:0 0 8px;font-size:15px;letter-spacing:.04em;font-weight:600}
h1 small{color:var(--dim);font-weight:400}
.row{display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.row+.row{margin-top:8px}
.lbl{color:var(--dim);font-size:11px;text-transform:uppercase;letter-spacing:.1em;margin-right:4px}
.chip{display:inline-flex;align-items:center;gap:6px;border:1px solid var(--line);background:var(--panel);color:var(--ink);
  padding:5px 10px;border-radius:999px;cursor:pointer;font-size:12.5px;user-select:none}
.chip:hover{border-color:var(--dim)}
.chip .dot{width:10px;height:10px;border-radius:50%;flex:0 0 auto}
.chip .ct{color:var(--dim);font-variant-numeric:tabular-nums}
.chip.on{border-color:var(--ink)}
.chip.brush{outline:2px solid var(--accent);outline-offset:1px}
.btn{border:1px solid var(--line);background:var(--panel);color:var(--ink);padding:6px 12px;border-radius:6px;cursor:pointer;font-size:12.5px}
.btn:hover{border-color:var(--dim)}
.btn.primary{background:var(--accent);color:#1a1206;border-color:var(--accent);font-weight:600}
input.add{background:#0f0d0a;border:1px solid var(--line);color:var(--ink);padding:6px 8px;border-radius:6px;width:150px}
.hint{color:var(--dim);font-size:11.5px}
main{padding:12px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(148px,1fr));gap:8px}
.tile{position:relative;border-radius:6px;overflow:hidden;background:#0f0d0a;cursor:pointer;border:2px solid transparent;aspect-ratio:1/1}
.tile img{width:100%;height:100%;object-fit:cover;display:block}
.tile .dots{position:absolute;left:4px;top:4px;display:flex;gap:3px;flex-wrap:wrap;max-width:80%}
.tile .dots i{width:12px;height:12px;border-radius:50%;border:1px solid rgba(0,0,0,.45)}
.tile .meta{position:absolute;left:0;right:0;bottom:0;padding:3px 5px;font-size:10px;color:#fff;
  background:linear-gradient(transparent,rgba(0,0,0,.78));opacity:0;transition:.15s;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tile:hover .meta{opacity:1}
.tile .badge{position:absolute;right:4px;top:4px;font-size:9px;background:rgba(0,0,0,.55);color:#fff;padding:1px 4px;border-radius:3px}
.tile.proscrit{opacity:.4;filter:grayscale(.6)}
.tile.proscrit::after{content:"X";position:absolute;inset:0;display:grid;place-items:center;font-size:30px;font-weight:700;color:#ff6a4d;text-shadow:0 1px 3px #000}
.lightbox{position:fixed;inset:0;background:rgba(0,0,0,.93);display:none;place-items:center;z-index:50;padding:20px}
.lightbox.show{display:grid}
.lightbox img{max-width:96vw;max-height:90vh;object-fit:contain}
.lightbox .cap{position:fixed;bottom:10px;left:0;right:0;text-align:center;color:#ddd;font-size:12px}
footer{position:sticky;bottom:0;background:rgba(21,19,15,.97);border-top:1px solid var(--line);padding:8px 14px;font-size:12px;color:var(--dim)}
</style></head>
<body>
<header>
  <h1>Trieur photos — eFoil Côte d'Azur <small id="stats"></small></h1>
  <div class="row"><span class="lbl">Pinceau</span><span id="brushes" class="row" style="gap:6px"></span>
    <input class="add" id="newcat" placeholder="+ catégorie..."><button class="btn" id="addcat">Ajouter</button></div>
  <div class="row"><span class="lbl">Filtre</span><span id="filters" class="row" style="gap:6px"></span></div>
  <div class="row"><button class="btn primary" id="export">Exporter JSON</button>
    <label class="btn">Importer JSON<input type="file" id="import" accept="application/json" hidden></label>
    <button class="btn" id="reset">Reinitialiser</button>
    <span class="hint">Choisis un pinceau (categorie) puis clique les vignettes pour les taguer. Multi-tags OK. Double-clic = agrandir. Sauvegarde auto.</span></div>
</header>
<main><div class="grid" id="grid"></div></main>
<div class="lightbox" id="lb"><img id="lbimg" alt=""><div class="cap" id="lbcap" style="bottom:98px"></div><textarea id="lbnote" placeholder="Annoter cette photo (optionnel) — sauvegarde auto" style="position:fixed;left:50%;bottom:40px;transform:translateX(-50%);width:min(92vw,560px);height:50px;background:#1d1a15;color:#f2ead9;border:1px solid #4a4234;border-radius:6px;padding:8px 10px;font:13px system-ui;resize:none"></textarea></div>
<footer id="foot"></footer>
<script>
var PHOTOS = /*__MANIFEST__*/;
/* Catégories = EMPLACEMENTS exacts (slots) de la page — chaque photo va à un endroit précis */
var DEFCATS=[
 {id:'hero',name:'Heros (poster video)',c:'#f4c542'},
 {id:'lieu',name:'Le lieu / chateau',c:'#46a6b8'},
 {id:'beach1',name:'Beach — aerien',c:'#39c0c8'},
 {id:'beach2',name:'Beach — parasols',c:'#e8c33e'},
 {id:'exp1',name:'Exp. Le silence',c:'#5fbf6a'},
 {id:'exp2',name:'Exp. Apesanteur',c:'#73c98a'},
 {id:'exp3',name:'Exp. A votre rythme',c:'#9fd6a8'},
 {id:'who1',name:'Pour qui 1 debutant',c:'#c98a3a'},
 {id:'who2',name:'Pour qui 2 confirme',c:'#d6a45a'},
 {id:'who3',name:'Pour qui 3 encadrement',c:'#e0bd7a'},
 {id:'who4',name:'Pour qui 4 materiel',c:'#b87a2a'},
 {id:'d1',name:'Deroule 1 briefing',c:'#5a8fd6'},
 {id:'d2',name:'Deroule 2 equipement',c:'#6f9fe0'},
 {id:'d3',name:'Deroule 3 a l-eau',c:'#86b0e8'},
 {id:'d4',name:'Deroule 4 le vol',c:'#a0c2ee'},
 {id:'spot',name:'Le spot (aerien hotel)',c:'#2fb0a0'},
 {id:'defile',name:'Galerie / defile auto',c:'#a784d8'},
 {id:'proscrire',name:'A proscrire',c:'#8a8a8a'}];
var LS='efcaTri3_';
function load(k,d){try{var v=JSON.parse(localStorage.getItem(LS+k));return v==null?d:v}catch(e){return d}}
function persist(){localStorage.setItem(LS+'assign',JSON.stringify(assign));localStorage.setItem(LS+'cats',JSON.stringify(cats));localStorage.setItem(LS+'notes',JSON.stringify(notes));}
var cats=load('cats',DEFCATS.slice()),assign=load('assign',{}),notes=load('notes',{}),brush=cats[0].id,filter='all',lbCur=null;
function catById(id){for(var i=0;i<cats.length;i++)if(cats[i].id===id)return cats[i];return {id:id,name:id,c:'#999'}}
function groups(){var s={};PHOTOS.forEach(function(p){s[p.g]=(s[p.g]||0)+1});return s}
function render(){
  var bh=document.getElementById('brushes');bh.innerHTML='';
  var counts={};Object.keys(assign).forEach(function(id){(assign[id]||[]).forEach(function(c){counts[c]=(counts[c]||0)+1})});
  cats.forEach(function(c){var el=document.createElement('span');el.className='chip'+(brush===c.id?' brush':'');
    el.innerHTML='<span class="dot" style="background:'+c.c+'"></span>'+c.name+' <span class="ct">'+(counts[c.id]||0)+'</span>';
    el.onclick=function(){brush=c.id;render()};bh.appendChild(el)});
  var fh=document.getElementById('filters');fh.innerHTML='';
  function fchip(id,label){var e=document.createElement('span');e.className='chip'+(filter===id?' on':'');e.textContent=label;e.onclick=function(){filter=id;renderGrid()};fh.appendChild(e)}
  fchip('all','Tout ('+PHOTOS.length+')');fchip('untagged','Sans tag');
  cats.forEach(function(c){fchip('cat:'+c.id,c.name)});
  fchip('type:photo','Photos');fchip('type:video','Frames video');
  var g=groups();Object.keys(g).sort().forEach(function(k){fchip('group:'+k,k+' ('+g[k]+')')});
  renderGrid();updateStats();
}
function visible(p){if(filter==='all')return true;var a=assign[p.id]||[];
  if(filter==='untagged')return a.length===0;
  if(filter.indexOf('cat:')===0)return a.indexOf(filter.slice(4))>=0;
  if(filter.indexOf('type:')===0)return p.k===filter.slice(5);
  if(filter.indexOf('group:')===0)return p.g===filter.slice(6);return true}
function renderGrid(){var grid=document.getElementById('grid');grid.innerHTML='';
  PHOTOS.forEach(function(p){if(!visible(p))return;var a=assign[p.id]||[];
    var t=document.createElement('div');t.className='tile'+(a.indexOf('proscrire')>=0?' proscrit':'');
    t.innerHTML='<img loading="lazy" src="'+p.t+'" alt=""><div class="dots"></div><span class="badge">'+(p.k==='video'?'film ':'')+p.g+'</span><div class="meta">'+p.id.split('/').pop()+'</div>';
    var dots=t.querySelector('.dots');a.forEach(function(c){var i=document.createElement('i');i.style.background=catById(c).c;i.title=catById(c).name;dots.appendChild(i)});
    t.onclick=function(){tag(p.id,t)};t.ondblclick=function(e){e.preventDefault();openLb(p)};grid.appendChild(t)})}
function tag(id,t){var a=assign[id]||[],i=a.indexOf(brush);if(i<0)a.push(brush);else a.splice(i,1);
  if(a.length)assign[id]=a;else delete assign[id];persist();
  t.className='tile'+((assign[id]||[]).indexOf('proscrire')>=0?' proscrit':'');
  var dots=t.querySelector('.dots');dots.innerHTML='';(assign[id]||[]).forEach(function(c){var el=document.createElement('i');el.style.background=catById(c).c;el.title=catById(c).name;dots.appendChild(el)});
  render()}
function updateStats(){document.getElementById('stats').textContent='— '+PHOTOS.length+' vignettes, '+Object.keys(assign).length+' taguees';
  document.getElementById('foot').textContent='Touches 1-9 = changer de pinceau. Filtre par categorie/groupe pour verifier tes packs. Exporte le JSON et envoie-le moi.'}
function openLb(p){lbCur=p.id;document.getElementById('lbimg').src=p.t;document.getElementById('lbcap').textContent=p.id;document.getElementById('lbnote').value=notes[p.id]||'';document.getElementById('lb').classList.add('show')}
document.getElementById('lb').onclick=function(e){if(e.target.id==='lbnote')return;this.classList.remove('show')};
document.getElementById('lbnote').addEventListener('input',function(){if(!lbCur)return;if(this.value.trim())notes[lbCur]=this.value;else delete notes[lbCur];persist()});
document.getElementById('addcat').onclick=function(){var v=document.getElementById('newcat').value.trim();if(!v)return;
  var id=v.toLowerCase().replace(/[^a-z0-9]+/g,'-').slice(0,24)||('c'+cats.length);
  if(!catById(id).name||catById(id).name===id){if(!cats.some(function(c){return c.id===id})){var pal=['#e0a92e','#39c0c8','#d4603f','#5fbf6a','#a784d8','#5a8fd6','#e8c33e','#f0823c'];cats.push({id:id,name:v,c:pal[cats.length%pal.length]})}}
  document.getElementById('newcat').value='';brush=id;persist();render()};
document.getElementById('export').onclick=function(){var packs={};cats.forEach(function(c){packs[c.id]=[]});
  Object.keys(assign).forEach(function(id){(assign[id]||[]).forEach(function(c){(packs[c]=packs[c]||[]).push(id)})});
  var out={categories:cats.map(function(c){return {id:c.id,name:c.name}}),packs:packs,assignments:assign,notes:notes,total:PHOTOS.length};
  var b=new Blob([JSON.stringify(out,null,2)],{type:'application/json'});var a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='efca-photo-tri.json';a.click()};
document.getElementById('import').onchange=function(e){var f=e.target.files[0];if(!f)return;var r=new FileReader();
  r.onload=function(){try{var d=JSON.parse(r.result);if(d.assignments)assign=d.assignments;if(d.categories)d.categories.forEach(function(c){if(!cats.some(function(x){return x.id===c.id}))cats.push({id:c.id,name:c.name,c:'#e0a92e'})});persist();render()}catch(err){alert('JSON invalide')}};r.readAsText(f)};
document.getElementById('reset').onclick=function(){if(confirm('Effacer tous les tags ?')){assign={};persist();render()}};
document.addEventListener('keydown',function(e){var n=parseInt(e.key,10);if(!isNaN(n)&&n>=1&&n<=9&&cats[n-1]){brush=cats[n-1].id;render()}if(e.key==='Escape')document.getElementById('lb').classList.remove('show')});
render();
</script></body></html>'''

THUMBS='medias/thumbs'; os.makedirs(THUMBS, exist_ok=True)
for f in glob.glob(f'{THUMBS}/*.webp'): os.remove(f)

PHOTO_DIRS=['medias/cannes','medias/saint-tropez','medias/iles-lerins','medias/esterel',
            'medias/como-beauvallon','medias/como-web/raw']
photo_paths=[]
for d in PHOTO_DIRS:
    for ext in ('*.jpg','*.jpeg','*.JPG','*.png'): photo_paths+=glob.glob(f'{d}/{ext}')
photo_paths=[p for p in photo_paths if '(1)' not in p]   # vire les doublons " (1)"

frame_paths=(glob.glob('medias/video-frames/auto/*.jpg')+glob.glob('medias/video-frames/drone/*.jpg')
             +glob.glob('medias/video-frames/*.jpg'))
def ahash(im):
    g=im.convert('L').resize((8,8)); px=list(g.getdata()); m=sum(px)/64; h=0
    for i,v in enumerate(px):
        if v>m: h|=1<<i
    return h
def ham(a,b): return bin(a^b).count('1')
kept=[]; hashes=[]
for f in sorted(set(p.replace('\\','/') for p in frame_paths)):
    try: im=Image.open(f).convert('RGB')
    except: continue
    h=ahash(im)
    if any(ham(h,k)<10 for k in hashes): continue
    hashes.append(h); kept.append(f)

def slug(p): return re.sub(r'[^a-z0-9]+','_',p.lower()).strip('_')[:90]
def group_of(p):
    if 'video-frames' in p: return 'vidéo'
    if 'como-web' in p: return 'COMO'
    return os.path.basename(os.path.dirname(p))

manifest=[]
def make_thumb(p, kind):
    try: im=ImageOps.exif_transpose(Image.open(p).convert('RGB'))
    except: return
    W,H=im.size; sc=min(1.0, 540/max(W,H)); im=im.resize((max(1,int(W*sc)),max(1,int(H*sc))),Image.LANCZOS)
    name=slug(p)+'.webp'; im.save(f'{THUMBS}/{name}','WEBP',quality=70,method=5)
    manifest.append({'id':p.replace('\\','/'),'t':f'{THUMBS}/{name}','g':group_of(p),'k':kind,
                     'o':'l' if W>=H else 'p'})

for p in sorted(set(x.replace('\\','/') for x in photo_paths)): make_thumb(p,'photo')
for p in kept: make_thumb(p,'video')

html=HTML_TEMPLATE.replace('/*__MANIFEST__*/', json.dumps(manifest, ensure_ascii=False))
open('trieur-photos.html','w',encoding='utf-8').write(html)
print(f"{len(manifest)} vignettes ({sum(1 for m in manifest if m['k']=='photo')} photos, "
      f"{sum(1 for m in manifest if m['k']=='video')} frames vidéo) -> medias/thumbs/ + trieur-photos.html")
