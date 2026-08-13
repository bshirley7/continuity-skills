"""Private native consultation board for Continuity Design."""

from __future__ import annotations

import base64
import hashlib
import json
import secrets
import shutil
import time
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

import design


MAX_FEEDBACK_BYTES = 64 * 1024
TOKEN_TTL_SECONDS = 1800


class ConsultationSocketError(design.DesignError):
    """Loopback startup failure that permits the documented static fallback."""


CSS = r"""
:root{color-scheme:light;--paper:#f2f0e9;--ink:#111513;--muted:#56615c;--line:#b9c0ba;--signal:#17614d;--risk:#c46c24;--white:#fff}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font-family:ui-sans-serif,system-ui,sans-serif;font-size:16px;line-height:1.5}button,select,textarea{font:inherit;border:1px solid currentColor;background:var(--white);color:var(--ink)}button{padding:.8rem 1rem;cursor:pointer}button.primary{background:var(--ink);color:var(--white)}button:focus-visible,select:focus-visible,textarea:focus-visible,input:focus-visible,figure:focus-visible,summary:focus-visible{outline:3px solid #ef9f35;outline-offset:3px}main{max-width:1800px;margin:auto;padding:clamp(1rem,3vw,3rem)}header{display:grid;grid-template-columns:minmax(0,1fr) minmax(20rem,.7fr);gap:2rem;padding-bottom:2rem;border-bottom:2px solid var(--ink)}h1{font-family:Georgia,serif;font-size:clamp(2.8rem,6vw,6rem);font-weight:400;line-height:.92;letter-spacing:-.055em;margin:.15em 0}.eyebrow{font:700 .72rem ui-monospace,monospace;letter-spacing:.14em;text-transform:uppercase}.lede{font-size:1.1rem;line-height:1.5;max-width:58ch}.notice{border-left:4px solid var(--signal);padding:1rem;background:var(--white)}.comparison-wrap{padding:2rem 0}.comparison-wrap>h2{font-family:Georgia,serif;font-size:clamp(2rem,4vw,4rem);font-weight:400;margin:.1rem 0}.comparison{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1rem;margin-top:1.25rem}.comparison-card{background:var(--white);border-top:4px solid var(--ink);min-width:0}.comparison-card img{width:100%;height:clamp(18rem,42vw,42rem);object-fit:cover;object-position:top;border-bottom:1px solid var(--line)}.comparison-card div{padding:1rem}.comparison-card h3{font-family:Georgia,serif;font-size:1.65rem;font-weight:400;margin:.2rem 0}.concepts{display:grid;gap:3rem;margin:2rem 0}.concept{background:var(--white);border-top:6px solid var(--ink)}.concept-head{padding:clamp(1rem,2.5vw,2rem);display:grid;grid-template-columns:minmax(0,1fr) minmax(18rem,.65fr);gap:2rem}.concept h2{font-family:Georgia,serif;font-size:clamp(2.4rem,4vw,4.5rem);font-weight:400;line-height:1;margin:.2rem 0}.meta{display:flex;flex-wrap:wrap;gap:.5rem;margin:1rem 0}.tag{font:700 .7rem ui-monospace,monospace;border:1px solid var(--ink);padding:.35rem .5rem}.remember{font-family:Georgia,serif;font-size:clamp(1.4rem,2.2vw,2.2rem);line-height:1.12;margin:0}.visuals{display:grid;grid-template-columns:minmax(0,2fr) minmax(15rem,.72fr);background:#cdd3ce;gap:1px}.visuals figure{margin:0;background:#d8ddd9;height:clamp(32rem,72vh,58rem);overflow:auto;overscroll-behavior:contain;position:relative}.visuals img{display:block;width:100%;height:auto}.visuals figcaption{position:sticky;bottom:.5rem;left:.5rem;width:max-content;background:var(--ink);color:var(--white);padding:.4rem .55rem;font-size:.76rem}.concept-feedback{padding:1rem clamp(1rem,2.5vw,2rem);background:#eef0ec}.concept-feedback h3{margin:.3rem 0}.reaction{display:grid;grid-template-columns:minmax(12rem,.5fr) minmax(9rem,.25fr) minmax(18rem,1fr);gap:1rem;align-items:start;border-top:1px solid var(--line);padding:1rem 0}.reaction label{display:grid;gap:.35rem}.reaction select,.reaction textarea{width:100%;padding:.65rem}.reaction textarea{min-height:4.5rem}.detail{border-top:1px solid var(--line);padding:0 clamp(1rem,2.5vw,2rem) 1.5rem}.detail summary{cursor:pointer;font-weight:700;padding:1.1rem 0}.decision-grid,.guideline-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem}.panel{border:1px solid var(--line);padding:1rem}.panel h3{margin-top:0}.panel ul{padding-left:1.25rem}.risk{border-left:4px solid var(--risk)}.safe{border-left:4px solid var(--signal)}.swatches{display:flex;flex-wrap:wrap;gap:.5rem}.swatch{border:1px solid var(--line);padding:.6rem;min-width:9rem}.chip{display:block;width:100%;height:2.5rem;border:1px solid var(--line);margin-bottom:.4rem}.feedback{background:#0f1512;color:#f5f5ef;padding:clamp(1rem,4vw,3rem);margin-top:3rem}.feedback h2{font-family:Georgia,serif;font-size:clamp(2rem,5vw,4rem);font-weight:400;margin-top:0}.feedback-extra{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem}.feedback-extra label{display:grid;gap:.5rem}.feedback textarea,.feedback select{padding:.7rem}.iteration{margin-top:1rem}.actions{display:flex;flex-wrap:wrap;gap:.75rem;margin-top:1.25rem}.status{min-height:1.5rem;margin-top:1rem}.status.error{color:#ff9c83}.status.success{color:#8ee3b7}.quiet{color:var(--muted)}@media(max-width:1050px){.comparison{grid-template-columns:1fr}.comparison-card{display:grid;grid-template-columns:1.4fr 1fr}.comparison-card img{height:30rem}.concept-head,.visuals,.decision-grid,.guideline-grid,.feedback-extra,.reaction{grid-template-columns:1fr}.visuals figure{height:clamp(26rem,65vh,44rem)}}@media(max-width:600px){main{padding:.8rem}header,.comparison-card{display:block}.comparison-card img{height:25rem}.concept-head{gap:.5rem}.visuals figure{height:34rem}.reaction textarea{min-height:6rem}}@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important;transition:none!important;animation:none!important}}
"""


JS = r"""
(()=>{'use strict';
const embedded=document.getElementById('continuity-board-data');
const status=document.getElementById('status');
let snapshot=null;
const token=location.hash.startsWith('#token=')?decodeURIComponent(location.hash.slice(7)):'';
if(token)history.replaceState(null,'',location.pathname);
const el=(name,attrs={},text='')=>{const node=document.createElement(name);for(const [key,value] of Object.entries(attrs)){if(key==='class')node.className=value;else if(key==='dataset')for(const [d,v] of Object.entries(value))node.dataset[d]=v;else node.setAttribute(key,String(value))}if(text)node.textContent=text;return node};
const addList=(parent,items,formatter=x=>x)=>{const list=el('ul');for(const item of items||[])list.append(el('li',{},formatter(item)));parent.append(list)};
const panel=(title,klass='panel')=>{const node=el('section',{class:klass});node.append(el('h3',{},title));return node};
const reactionRow=item=>{const row=el('div',{class:'reaction',dataset:{elementId:item.element_id}});row.append(el('div',{},item.label));const choiceLabel=el('label',{},'Reaction');const select=el('select',{'aria-label':`Reaction for ${item.label}`});select.append(el('option',{value:''},'Choose…'));for(const value of ['keep','change','avoid','uncertain'])select.append(el('option',{value},value));choiceLabel.append(select);const whyLabel=el('label',{},'Why');whyLabel.append(el('textarea',{'aria-label':`Reason for ${item.label}`,placeholder:'What should stay, change, or be explored?'}));row.append(choiceLabel,whyLabel);return row};
const renderComparison=data=>{const grid=document.getElementById('comparison');for(const concept of data.concepts){const card=el('article',{class:'comparison-card'});const image=concept.images[0];card.append(el('img',{src:image.src,alt:`${concept.title} opening composition`}));const copy=el('div');copy.append(el('span',{class:'eyebrow'},concept.role.replace('-',' ')),el('h3',{},concept.title),el('p',{},concept.consultation_summary?concept.consultation_summary.memorable_thing:concept.thesis));card.append(copy);grid.append(card)}};
const renderConcept=(concept,index)=>{const article=el('article',{class:'concept'});const head=el('div',{class:'concept-head'});const intro=el('div');intro.append(el('span',{class:'eyebrow'},`${String(index+1).padStart(2,'0')} · ${concept.role.replace('-',' ')}`),el('h2',{},concept.title),el('p',{class:'lede'},concept.thesis));const tags=el('div',{class:'meta'});for(const value of [concept.recommended?'Recommended':null,concept.primary_carrier,concept.emotional_register].filter(Boolean))tags.append(el('span',{class:'tag'},value));intro.append(tags);const decision=el('div');decision.append(el('p',{class:'remember'},concept.consultation_summary?concept.consultation_summary.memorable_thing:concept.impact_thesis),el('p',{},`Tradeoff: ${concept.tradeoff}`));head.append(intro,decision);article.append(head);
const visuals=el('div',{class:'visuals'});for(const image of concept.images){const figure=el('figure',{tabindex:'0','aria-label':`${image.label}. Scroll to inspect the full evidence.`});figure.append(el('img',{src:image.src,alt:image.alt}),el('figcaption',{},image.label));visuals.append(figure)}article.append(visuals);
const feedback=el('section',{class:'concept-feedback'});feedback.append(el('h3',{},'React while the visuals are in view'),el('p',{},'Comment only on the parts that matter to you. Every reaction needs a reason.'));for(const item of snapshot.elements.filter(x=>x.element_id.startsWith(`${index+1}.`)))feedback.append(reactionRow(item));article.append(feedback);
const detail=el('details',{class:'detail'});detail.append(el('summary',{},'Open rationale, safe choices, risks, and brand rules'));const body=el('div');if(concept.consultation_summary){body.append(el('p',{class:'lede'},concept.consultation_summary.coherence_rationale));const decisions=el('div',{class:'decision-grid'});const safe=panel('Safe choices','panel safe');addList(safe,concept.consultation_summary.safe_choices,x=>`${x.decision} — ${x.rationale}`);const risks=panel('Creative risks','panel risk');addList(risks,concept.consultation_summary.creative_risks,x=>`${x.move} — gain: ${x.gain}; cost: ${x.cost}; boundary: ${x.boundary}`);decisions.append(safe,risks);body.append(decisions)}if(concept.brand_guideline){const guide=el('div',{class:'guideline-grid'});const colors=panel('Color system');const swatches=el('div',{class:'swatches'});for(const color of concept.brand_guideline.color.roles){const swatch=el('div',{class:'swatch'});const chip=el('span',{class:'chip'});chip.style.background=color.value;swatch.append(chip,el('strong',{},color.name),el('div',{class:'quiet'},`${color.token} · ${color.value}`));swatches.append(swatch)}colors.append(swatches);const type=panel('Typography');addList(type,concept.brand_guideline.typography.roles,x=>`${x.role}: ${x.family} ${x.weight_style} — ${x.usage}`);const spatial=panel('Spacing and layout');spatial.append(el('p',{},`Base ${concept.brand_guideline.spatial.base_unit}. ${concept.brand_guideline.spatial.grid}`));addList(spatial,concept.brand_guideline.spatial.transformations,x=>`${x.context}: ${x.rule}`);const behavior=panel('Motion and voice');behavior.append(el('p',{},`${concept.brand_guideline.motion.status}: ${concept.brand_guideline.motion.rationale}`),el('p',{},`Reduced motion: ${concept.brand_guideline.motion.reduced_motion}`));addList(behavior,concept.brand_guideline.voice.principles);guide.append(colors,type,spatial,behavior);body.append(guide)}detail.append(body);article.append(detail);return article};
const render=data=>{snapshot=data;document.getElementById('title').textContent=data.title;document.getElementById('context').textContent=data.intent;document.getElementById('revision').textContent=`Design ${data.design_id} · revision ${data.revision}`;renderComparison(data);const concepts=document.getElementById('concepts');for(const [index,concept] of data.concepts.entries())concepts.append(renderConcept(concept,index));const preferred=document.getElementById('preferred');preferred.append(el('option',{value:''},'No preference yet'));for(const concept of data.concepts.filter(x=>x.direction_id))preferred.append(el('option',{value:concept.direction_id},concept.title));document.getElementById('submit').disabled=!token};
const payload=()=>{const reactions=[];for(const row of document.querySelectorAll('.reaction')){const reaction=row.querySelector('select').value;const why=row.querySelector('textarea').value.trim();if(reaction){if(!why)throw new Error(`Add a reason for ${row.firstChild.textContent}`);reactions.push({element_id:row.dataset.elementId,reaction,why,user_language:why})}}if(!reactions.length)throw new Error('Choose at least one numbered reaction.');const iteration=document.getElementById('iteration').value;const preferred=document.getElementById('preferred').value;const remix=document.getElementById('remix').value.trim();if(['more-like-preferred','refine-preferred'].includes(iteration)&&!preferred)throw new Error('Choose a preferred direction for that iteration request.');if(iteration==='remix'&&!remix)throw new Error('Describe which parts should be remixed.');const changed=iteration!=='none'||reactions.some(x=>x.reaction==='change'||x.reaction==='avoid');return{design_id:snapshot.design_id,revision:snapshot.revision,board_hash:snapshot.board_hash,concept_evidence_hash:snapshot.concept_evidence_hash,actor:snapshot.actor,actor_type:'human',reactions,contract_changed:changed,ready_for_selection:changed?false:document.getElementById('ready').checked,preferred_direction_id:preferred,iteration_request:iteration,remix_notes:remix,overall_notes:document.getElementById('overall').value.trim()}};
const download=value=>{const blob=new Blob([JSON.stringify(value,null,2)+'\n'],{type:'application/json'});const link=el('a',{href:URL.createObjectURL(blob),download:`${snapshot.design_id}-feedback-r${snapshot.revision}.json`});document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(link.href),0)};
document.getElementById('export').addEventListener('click',()=>{try{download(payload());status.textContent='Feedback JSON exported. Record it with continuity design feedback-record.';status.className='status success'}catch(error){status.textContent=error.message;status.className='status error'}});
document.getElementById('submit').addEventListener('click',async()=>{try{const value=payload();const response=await fetch('/api/v1/feedback',{method:'POST',headers:{Authorization:`Bearer ${token}`,'Content-Type':'application/json'},body:JSON.stringify(value)});const result=await response.json();if(!response.ok)throw new Error(result.error||'Feedback submission failed.');status.textContent=`Feedback round ${result.feedback_round} captured. This is not selection or approval. Status: ${result.status}.`;status.className='status success';document.getElementById('submit').disabled=true}catch(error){status.textContent=error.message;status.className='status error'}});
const load=async()=>{try{const text=embedded.textContent.trim();if(text){render(JSON.parse(text));return}if(!token)throw new Error('Consultation authorization is missing. Reopen the URL printed by Continuity.');const response=await fetch('/api/v1/board',{headers:{Authorization:`Bearer ${token}`}});const data=await response.json();if(!response.ok)throw new Error(data.error||'Could not load consultation board.');for(const concept of data.concepts){for(const image of concept.images){const media=await fetch(`/api/v1/${image.src}`,{headers:{Authorization:`Bearer ${token}`}});if(!media.ok)throw new Error('Could not load validated consultation media.');image.src=URL.createObjectURL(await media.blob())}}render(data)}catch(error){status.textContent=error.message;status.className='status error'}};load();
})();
"""


def _document(embedded: dict[str, Any] | None) -> str:
    data = json.dumps(embedded, sort_keys=True, separators=(",", ":"), ensure_ascii=False) if embedded else ""
    data = data.replace("<", "\\u003c")
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Continuity Design consultation</title><style>{CSS}</style></head><body><main><header><div><span class="eyebrow" id="revision">Private design consultation</span><h1 id="title">Continuity Design</h1></div><div><p class="lede" id="context">Loading current design evidence…</p><p class="notice">Judge the visual directions first. Supporting rationale and brand rules are available inside each direction. This board can request iteration, but it cannot select, approve, publish, generate, or authorize implementation.</p></div></header><section class="comparison-wrap" aria-labelledby="comparison-title"><span class="eyebrow">First impression</span><h2 id="comparison-title">Compare the openings before reading the rationale.</h2><p>Look for a clear user outcome, primary action, product proof, and a signature you can recognize in five seconds.</p><div id="comparison" class="comparison"></div></section><section id="concepts" class="concepts" aria-label="Complete design concepts"></section><section class="feedback" aria-labelledby="feedback-title"><span class="eyebrow">Your direction</span><h2 id="feedback-title">Choose what should happen next.</h2><p>Your preference is advisory until the separate selection command. Iteration requests create material feedback and therefore cannot be marked ready.</p><div class="feedback-extra"><label>Preferred direction (advisory only)<select id="preferred"></select></label><label>Next creative move<select id="iteration" class="iteration"><option value="none">No iteration request</option><option value="refine-preferred">Refine the preferred direction</option><option value="more-like-preferred">Generate more like the preferred direction</option><option value="remix">Remix elements across directions</option><option value="different-directions">Start over with different directions</option></select></label><label>Remix notes<textarea id="remix" rows="4" placeholder="For example: composition from 1, material from 2, typography posture from 3."></textarea></label><label>Overall notes<textarea id="overall" rows="4" placeholder="What should the next revision feel or do differently?"></textarea></label></div><label><input id="ready" type="checkbox"> I am the human reviewer, and this refreshed concept set is ready for the separate selection step.</label><div class="actions"><button id="submit" class="primary" type="button">Submit privately</button><button id="export" type="button">Export feedback JSON</button></div><p id="status" class="status" role="status" aria-live="polite"></p></section></main><script id="continuity-board-data" type="application/json">{data}</script><script>{JS}</script></body></html>'''


def _private_root(root: Path, config: dict[str, Any]) -> tuple[Path, Path]:
    relative = Path(str(config.get("private_dir", ".continuity/private")))
    if relative.is_absolute() or ".." in relative.parts:
        raise design.DesignError("Design consultation private_dir must be project-relative")
    resolved = (root / relative).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise design.DesignError("Design consultation private_dir escapes the project root") from exc
    return relative, resolved


def _snapshot(root: Path, record: dict[str, Any], actor: str) -> tuple[dict[str, Any], dict[str, Path]]:
    evidence = record["concept_evidence"]
    directions = {item["direction_id"]: item for item in record["directions"]}
    concepts: list[dict[str, Any]] = []
    elements: list[dict[str, str]] = []
    hash_concepts: list[dict[str, Any]] = []
    asset_sources: dict[str, Path] = {}
    for index, concept in enumerate(evidence["concepts"], 1):
        direction = directions.get(concept.get("direction_id"))
        title = direction["name"] if direction else concept["concept_id"].replace("-", " ").title()
        images = []
        hash_images = []
        for key, label in (("wide_composition", "Wide composition"), ("narrow_transformation", "Narrow transformation")):
            item = concept[key]
            relative, path = design._artifact_relative_path(root, item["path"])
            if path.suffix.lower() != ".png" or hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
                raise design.DesignError("Consultation media must be current validated PNG evidence")
            if path.stat().st_size > 25 * 1024 * 1024:
                raise design.DesignError("Consultation media exceeds the 25 MiB per-image limit")
            design._png_dimensions(path)
            asset_name = f"{item['sha256']}.png"
            images.append({"label": label, "alt": f"{title} — {label}", "src": f"assets/{asset_name}"})
            asset_sources[asset_name] = path
            hash_images.append({"path": relative, "sha256": item["sha256"], "label": label})
        normalized = {
            "concept_id": concept["concept_id"], "direction_id": concept.get("direction_id"), "role": concept["role"],
            "title": title, "recommended": concept["recommended"], "thesis": concept["thesis"],
            "impact_thesis": concept["impact_thesis"], "primary_carrier": concept["primary_carrier"],
            "emotional_register": concept["emotional_register"], "tradeoff": concept["tradeoff"],
            "palette": concept["palette"], "typography_system": concept["typography_system"],
            "consultation_summary": concept.get("consultation_summary"), "brand_guideline": concept.get("brand_guideline"),
            "brand_guideline_hash": concept.get("brand_guideline_hash"), "images": images,
        }
        concepts.append(normalized)
        hash_concepts.append({**normalized, "images": hash_images})
        elements.append({"element_id": f"{index}.concept", "label": f"{index}. Concept: {title}"})
        if concept.get("brand_guideline"):
            elements.extend([
                {"element_id": f"{index}.color", "label": f"{index}. Color system"},
                {"element_id": f"{index}.typography", "label": f"{index}. Typography system"},
                {"element_id": f"{index}.brand", "label": f"{index}. Brand and application rules"},
            ])
    evidence_hash = design._canonical_hash(evidence)
    board_basis = {
        "design_id": record["design_id"], "revision": record["revision"], "concept_evidence_hash": evidence_hash,
        "title": record["title"], "intent": record["intent"], "concepts": hash_concepts, "elements": elements,
    }
    return {
        "schema_version": 1, "private": True, "design_id": record["design_id"], "revision": record["revision"],
        "concept_evidence_hash": evidence_hash, "board_hash": design._canonical_hash(board_basis),
        "actor": actor, "title": record["title"], "intent": record["intent"], "concepts": concepts,
        "elements": elements, "execution_authorized": False,
    }, asset_sources


def _prepare(root: Path, config: dict[str, Any], design_id: str, actor: str) -> tuple[dict[str, Any], dict[str, Any], Path]:
    design._enabled(config)
    design_id = design._identifier(design_id, "design ID")
    actor = design._required_text(actor, "Consultation actor")
    private_relative, private_root = _private_root(root, config)
    design_dir = private_root / "design" / design_id
    record = design._read_json(design_dir / "draft.json")
    if record.get("workflow_version", 1) < 4:
        raise design.DesignError("Native consultation boards require workflow_version 4")
    evidence = record.get("concept_evidence")
    if not isinstance(evidence, dict) or not evidence.get("validated") or record.get("status") not in {"awaiting-feedback", "refining", "awaiting-selection"}:
        raise design.DesignError("Consultation requires current validated concept evidence")
    snapshot, asset_sources = _snapshot(root, record, actor)
    relative = private_relative / "design" / design_id / "consultations" / f"v{record['revision']}" / f"{snapshot['board_hash']}.html"
    output = root / relative
    output.parent.mkdir(parents=True, exist_ok=True)
    asset_dir = output.parent / "assets"
    asset_dir.mkdir(exist_ok=True)
    for asset_name, source in asset_sources.items():
        target = asset_dir / asset_name
        if target.is_symlink():
            raise design.DesignError("Consultation media destination cannot be a symlink")
        if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != asset_name[:-4]:
            shutil.copy2(source, target)
    output.write_text(_document(snapshot), encoding="utf-8")
    record["active_consultation"] = {
        "board_hash": snapshot["board_hash"], "concept_evidence_hash": snapshot["concept_evidence_hash"],
        "revision": record["revision"], "actor": actor, "path": relative.as_posix(), "rendered_at": design._now(),
    }
    design._write_json(design_dir / "draft.json", record)
    result = {
        "schema_version": 1, "private": True, "design_id": design_id, "revision": record["revision"],
        "path": relative.as_posix(), "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "board_hash": snapshot["board_hash"], "concept_evidence_hash": snapshot["concept_evidence_hash"],
        "feedback_modes": ["loopback-submit", "json-export"], "execution_authorized": False,
    }
    return result, snapshot, asset_dir


def render(root: Path, config: dict[str, Any], design_id: str, actor: str) -> dict[str, Any]:
    return _prepare(root, config, design_id, actor)[0]


class ConsultationHandler(BaseHTTPRequestHandler):
    server_version = "ContinuityDesignConsultation/1"

    def _headers(self, status: int, content_type: str = "application/json; charset=utf-8") -> None:
        css_hash = base64.b64encode(hashlib.sha256(CSS.encode()).digest()).decode()
        js_hash = base64.b64encode(hashlib.sha256(JS.encode()).digest()).decode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Security-Policy", f"default-src 'none'; script-src 'sha256-{js_hash}'; style-src 'sha256-{css_hash}'; connect-src 'self'; img-src 'self' blob:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        self.end_headers()

    def _context_ok(self) -> bool:
        expected = {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}
        if self.headers.get("Host", "") not in expected:
            self._headers(HTTPStatus.BAD_REQUEST); self.wfile.write(b'{"error":"invalid host"}'); return False
        origin = self.headers.get("Origin")
        if origin and origin not in {f"http://{value}" for value in expected}:
            self._headers(HTTPStatus.FORBIDDEN); self.wfile.write(b'{"error":"cross-origin request rejected"}'); return False
        return True

    def _authorized(self) -> bool:
        return time.monotonic() < self.server.token_expires_at and secrets.compare_digest(self.headers.get("Authorization", ""), f"Bearer {self.server.bearer_token}")

    def _path(self) -> str | None:
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        if ".." in Path(path).parts or "\\" in path or "%2f" in self.path.lower() or "%5c" in self.path.lower():
            self._headers(HTTPStatus.BAD_REQUEST); self.wfile.write(b'{"error":"invalid path"}'); return None
        return path

    def do_GET(self) -> None:  # noqa: N802
        if not self._context_ok(): return
        path = self._path()
        if path is None: return
        if path in {"/", "/index.html"}:
            body = _document(None).encode(); self._headers(HTTPStatus.OK, "text/html; charset=utf-8"); self.wfile.write(body); return
        if not self._authorized():
            self._headers(HTTPStatus.UNAUTHORIZED); self.wfile.write(b'{"error":"bearer authorization required"}'); return
        if path == "/api/v1/board":
            body = json.dumps(self.server.snapshot, sort_keys=True).encode()
        elif path == "/api/v1/health":
            body = b'{"status":"ok","private":true,"write_scope":"design-feedback-only"}'
        elif path.startswith("/api/v1/assets/"):
            asset_name = path.removeprefix("/api/v1/assets/")
            if asset_name not in self.server.allowed_assets or Path(asset_name).name != asset_name:
                self._headers(HTTPStatus.NOT_FOUND); self.wfile.write(b'{"error":"not found"}'); return
            body = (self.server.asset_dir / asset_name).read_bytes()
            self._headers(HTTPStatus.OK, "image/png"); self.wfile.write(body); return
        else:
            self._headers(HTTPStatus.NOT_FOUND); self.wfile.write(b'{"error":"not found"}'); return
        self._headers(HTTPStatus.OK); self.wfile.write(body)

    def do_POST(self) -> None:  # noqa: N802
        if not self._context_ok(): return
        path = self._path()
        if path is None: return
        if path != "/api/v1/feedback":
            self._headers(HTTPStatus.METHOD_NOT_ALLOWED); self.wfile.write(b'{"error":"feedback is the only writable endpoint"}'); return
        if not self._authorized():
            self._headers(HTTPStatus.UNAUTHORIZED); self.wfile.write(b'{"error":"bearer authorization required"}'); return
        if self.headers.get_content_type() != "application/json":
            self._headers(HTTPStatus.UNSUPPORTED_MEDIA_TYPE); self.wfile.write(b'{"error":"application/json required"}'); return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if length <= 0 or length > MAX_FEEDBACK_BYTES:
            self._headers(HTTPStatus.REQUEST_ENTITY_TOO_LARGE); self.wfile.write(b'{"error":"feedback payload size is invalid"}'); return
        try:
            payload = json.loads(self.rfile.read(length))
            result = design.feedback_record_payload(self.server.project_root, self.server.config, self.server.design_id, payload, actor_override=self.server.actor)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            self._headers(HTTPStatus.BAD_REQUEST); self.wfile.write(json.dumps({"error": f"invalid JSON: {exc}"}).encode()); return
        except design.DesignError as exc:
            status = HTTPStatus.CONFLICT if "stale" in str(exc).lower() else HTTPStatus.BAD_REQUEST
            self._headers(status); self.wfile.write(json.dumps({"error": str(exc)}).encode()); return
        self._headers(HTTPStatus.OK); self.wfile.write(json.dumps(result, sort_keys=True).encode())

    def do_PUT(self) -> None:  # noqa: N802
        if not self._context_ok(): return
        self._headers(HTTPStatus.METHOD_NOT_ALLOWED); self.wfile.write(b'{"error":"method not allowed"}')
    do_PATCH = do_DELETE = do_PUT  # type: ignore[assignment]

    def log_message(self, format: str, *args: Any) -> None:
        return


class ConsultationServer(ThreadingHTTPServer):
    allow_reuse_address = False
    daemon_threads = True

    def __init__(self, address: tuple[str, int], *, root: Path, config: dict[str, Any], design_id: str, actor: str, snapshot: dict[str, Any], asset_dir: Path, token: str):
        if address[0] != "127.0.0.1":
            raise design.DesignError("Design consultation must bind to 127.0.0.1")
        self.project_root = root.resolve(); self.config = config; self.design_id = design_id; self.actor = actor; self.snapshot = snapshot
        self.asset_dir = asset_dir.resolve()
        self.allowed_assets = {image["src"].removeprefix("assets/") for concept in snapshot["concepts"] for image in concept["images"]}
        self.bearer_token = token; self.token_expires_at = time.monotonic() + TOKEN_TTL_SECONDS
        super().__init__(address, ConsultationHandler)


def create_server(root: Path, config: dict[str, Any], design_id: str, actor: str, *, port: int = 0, token: str | None = None) -> tuple[ConsultationServer, dict[str, Any]]:
    if port < 0 or port > 65535:
        raise design.DesignError("Invalid consultation port")
    result, snapshot, asset_dir = _prepare(root, config, design_id, actor)
    try:
        server = ConsultationServer(("127.0.0.1", port), root=root, config=config, design_id=design_id, actor=actor, snapshot=snapshot, asset_dir=asset_dir, token=token or secrets.token_urlsafe(32))
    except PermissionError:
        raise
    except OSError as exc:
        raise ConsultationSocketError(f"Could not start loopback design consultation: {exc}") from exc
    return server, result


def serve(root: Path, config: dict[str, Any], design_id: str, actor: str, *, port: int = 0, open_browser: bool = False) -> dict[str, Any]:
    try:
        server, rendered = create_server(root, config, design_id, actor, port=port)
    except (PermissionError, OSError, ConsultationSocketError):
        rendered = render(root, config, design_id, actor)
        return {**rendered, "degraded_to_static": True, "degradation_reason": "loopback-unavailable"}
    url = f"http://127.0.0.1:{server.server_port}/#token={server.bearer_token}"
    print(json.dumps({**rendered, "url": url, "token_ttl_seconds": TOKEN_TTL_SECONDS}), flush=True)
    if open_browser:
        if not webbrowser.open(url, new=2):
            server.server_close()
            return {**rendered, "degraded_to_static": True, "degradation_reason": "browser-open-unavailable"}
    try:
        server.serve_forever(poll_interval=0.1)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return {"stopped": True, "design_id": design_id, "execution_authorized": False}
