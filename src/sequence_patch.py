# Module sequence list in Course Planning: one row per module with its title box, context,
# a title suggestion link, and drag handle / arrows to reorder whole modules (before development only).
# Run by build.py with its sub() helper in scope.

sub('</style>', '''.seq-list{list-style:none;margin:12px 0 0;padding:0}
.seq-row{display:grid;grid-template-columns:auto 84px minmax(0,1fr) auto;gap:4px 10px;align-items:start;padding:8px 6px;border-top:1px solid var(--line);border-radius:6px}
.seq-row:first-child{border-top:0}
.seq-row.drop-before{box-shadow:0 -3px 0 0 var(--maroon)}
.seq-row.drop-after{box-shadow:0 3px 0 0 var(--maroon)}
.seq-row.dragging{opacity:.45}
.seq-row.flash{animation:fl 1.4s ease-out}
.seq-handle{cursor:grab;color:#a59b92;font-size:15px;letter-spacing:-3px;padding:9px 6px 4px 2px;border-radius:5px;user-select:none;line-height:1}
.seq-handle:hover{background:#f0ebe6;color:var(--maroon)}
.seq-handle:active{cursor:grabbing}
.seq-n{font-weight:700;font-size:13.5px;padding-top:9px;white-space:nowrap}
.seq-main .field-head{margin:0;align-items:center}
.seq-main input{flex:1}
.seq-meta{font-size:12.5px;color:var(--muted);margin-top:4px}
.seq-tag{display:inline-block;font-size:11px;font-weight:700;color:var(--maroon);background:var(--maroon-tint);border-radius:4px;padding:1px 6px;margin-right:6px}
.seq-arrows{display:flex;gap:2px;padding-top:4px}
@media (max-width:600px){.seq-row{grid-template-columns:auto minmax(0,1fr) auto}.seq-n{grid-column:2;padding-top:6px}.seq-main{grid-column:1 / -1}}
</style>''')

# the list itself, inside the Module sequence card
sub('''<p class="sub">Get a starting outline of module titles and CLO mapping from your objectives and learning activities.</p></div>
      <button class="btn sec ai" data-action="ai" data-arg="sequence">Suggest a sequence</button></div>
    ${aiBox("sequence")}
  </div>''', '''<p class="sub">The course at a glance. Type each module's title here or on its tab below.${canMoveModules() ? " Drag a module, or use its arrows, to change the order. Everything planned for it moves with it." : ""}</p></div>
      <button class="btn sec ai" data-action="ai" data-arg="sequence">Suggest a sequence</button></div>
    ${aiBox("sequence")}
    ${sequenceList()}
  </div>''')

sub('/* Step 3 */\nfunction renderModules() {', '''/* Step 3 */
const canMoveModules = () => S.phase !== "dev" && !viewOnly();
function sequenceList() {
  const move = canMoveModules(), n = modCount();
  return `<ol class="seq-list" id="seqList">${activeModules().map((mm, k) => {
    const acts = assessmentsIn(k).map(a => a.title.trim()).filter(Boolean);
    const meta = [(mm.clos || []).filter(id => cloNum(id) > 0).map(cloLabel).join(", ") || "No objectives yet", acts.length ? acts.join("; ") : "No learning activities placed here"];
    return `<li class="seq-row" data-seq="${k}">
      ${move ? `<span class="seq-handle" draggable="true" title="Drag to reorder" aria-hidden="true">⋮⋮</span>` : "<span></span>"}
      <span class="seq-n">Module ${k + 1}</span>
      <div class="seq-main"><div class="field-head"><input type="text" data-bind="modules.${k}.title" value="${esc(mm.title)}" placeholder="Module title" aria-label="Module ${k + 1} title">${aiLink(`seq.${k}`)}</div>
        <div class="seq-meta">${k === 0 ? `<span class="seq-tag">Lighter start: about 4 hours, no cohort session</span>` : ""}${esc(meta.join(" · "))}</div>
        ${aiBox(fieldKey(`seq.${k}`))}</div>
      ${move ? `<span class="seq-arrows"><button class="icon-btn" data-action="moveMod" data-arg="${k}" data-dir="-1" ${k === 0 ? "disabled" : ""} aria-label="Move Module ${k + 1} up" title="Move up">↑</button><button class="icon-btn" data-action="moveMod" data-arg="${k}" data-dir="1" ${k === n - 1 ? "disabled" : ""} aria-label="Move Module ${k + 1} down" title="Move down">↓</button></span>` : "<span></span>"}
    </li>`; }).join("")}</ol>`;
}
/* Move a whole module. Learning activities follow it; the course introduction stays in Module 1 and the conclusion in the last module. */
function moveModule(from, to) {
  const n = modCount(); if (!canMoveModules() || from === to || from < 0 || to < 0 || from >= n || to >= n) return;
  const order = Array.from({ length:n }, (_, k) => k); const [o] = order.splice(from, 1); order.splice(to, 0, o);
  const newIdx = []; order.forEach((old, pos) => newIdx[old] = pos);
  const oldFirst = S.modules[0], oldLast = S.modules[n - 1];
  const moved = order.map(k => S.modules[k]); S.modules.splice(0, n, ...moved);
  S.assessments.forEach(a => { const k = (parseInt(a.module, 10) || 1) - 1; if (k < n) a.module = String(newIdx[k] + 1); });
  const pull = (md, kind) => { const ls = String(md.media || "").split("\\n"), keep = [], out = []; ls.forEach(l => (l.trim() && RQM[kind].test(l) && (kind !== "conclusion" || !RQM.intro.test(l)) ? out : keep).push(l)); md.media = keep.join("\\n").replace(/^\\n+|\\n+$/g, ""); return out; };
  if (S.modules[0] !== oldFirst) { const ls = pull(oldFirst, "intro"); if (ls.length && !mediaHas(S.modules[0].media, "intro")) S.modules[0].media = ls.concat(String(S.modules[0].media || "").split("\\n").filter(l => l.trim())).join("\\n"); }
  if (S.modules[n - 1] !== oldLast) { const ls = pull(oldLast, "conclusion"); if (ls.length && !mediaHas(S.modules[n - 1].media, "conclusion")) S.modules[n - 1].media = String(S.modules[n - 1].media || "").split("\\n").filter(l => l.trim()).concat(ls).join("\\n"); }
  if (S.moduleTab != null && newIdx[S.moduleTab] != null) S.moduleTab = newIdx[S.moduleTab];
  for (const key of Object.keys(AIR)) if (/^(detail|materials|cohort)_\\d+$|^fld_modules_|^fld_seq_/.test(key)) delete AIR[key];
  save(); rerender(); toast(`Moved to Module ${to + 1}`);
  const row = document.querySelector(`.seq-row[data-seq="${to}"]`); if (row) row.classList.add("flash");
}
function renderModules() {''')

# the title box in the list and on the module tab stay in step while typing
sub('''function live(path, el) {
  renderNav();''', '''function live(path, el) {
  renderNav();
  if (el && /^modules\\.\\d+\\.title$/.test(path)) document.querySelectorAll(`[data-bind="${path}"]`).forEach(x => { if (x !== el) x.value = el.value; });''')

# arrows
sub('''    addReqMedia: () =>''', '''    moveMod: () => moveModule(+arg, +arg + (+b.dataset.dir)),
    addReqMedia: () =>''')

# drag and drop on the sequence list (separate from learning activity cards)
sub('''main.addEventListener("dragend", () => { DRAG_ID = null;''', '''let SEQ_FROM = null;
const seqDropAt = (e, row) => { const r = row.getBoundingClientRect(); return e.clientY < r.top + r.height / 2; };
main.addEventListener("dragstart", e => {
  const h = e.target.closest && e.target.closest(".seq-handle"); if (!h || !canMoveModules()) return;
  const row = h.closest(".seq-row"); SEQ_FROM = +row.dataset.seq;
  e.dataTransfer.effectAllowed = "move"; e.dataTransfer.setData("text/plain", "module-" + SEQ_FROM);
  try { e.dataTransfer.setDragImage(row, 24, 18); } catch (err) {}
  setTimeout(() => row.classList.add("dragging"), 0);
});
main.addEventListener("dragover", e => {
  if (SEQ_FROM === null) return;
  const row = e.target.closest && e.target.closest(".seq-row"); if (!row) return;
  e.preventDefault(); e.dataTransfer.dropEffect = "move"; clearDrop();
  if (+row.dataset.seq !== SEQ_FROM) row.classList.add(seqDropAt(e, row) ? "drop-before" : "drop-after");
});
main.addEventListener("drop", e => {
  if (SEQ_FROM === null) return;
  e.preventDefault();
  const row = e.target.closest && e.target.closest(".seq-row"), from = SEQ_FROM; SEQ_FROM = null; clearDrop();
  if (!row || +row.dataset.seq === from) return;
  let to = +row.dataset.seq + (seqDropAt(e, row) ? 0 : 1); if (from < to) to--;
  moveModule(from, to);
});
main.addEventListener("dragend", () => { SEQ_FROM = null; document.querySelectorAll(".seq-row.dragging").forEach(x => x.classList.remove("dragging")); });
main.addEventListener("dragend", () => { DRAG_ID = null;''')

# title ideas from a sequence row write into that module's title
sub('''  { re:/^assessments\\.\\d+\\.title$/,''', '''  { re:/^seq\\.\\d+$/, mode:"replace", dest:p => `modules.${p.split(".")[1]}.title`, label:"Module title ideas", ask:n => `Suggest 4 titles for Module ${n + 1}. Base them on its topics, the objectives it meets and the learning activities placed in it, and make them fit the modules before and after it. Each is 3 to 7 words, plain and specific, with no colon or subtitle.` },
  { re:/^assessments\\.\\d+\\.title$/,''')
sub('''      const n = +path.split(".")[1], cur = String(getPath(S, path) || "").trim();''', '''      const n = +path.split(".")[1], cur = String(getPath(S, sp.dest ? sp.dest(path) : path) || "").trim();''')
sub('''fn:() => { if (sp.mode === "append") appendTo(path, o); else setPath(S, path, o); } }] })); }''', '''fn:() => { const dest = sp.dest ? sp.dest(path) : path; if (sp.mode === "append") appendTo(dest, o); else setPath(S, dest, o); } }] })); }''')
