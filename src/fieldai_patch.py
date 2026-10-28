# Per-box AI suggestions in Course Planning: a quiet "✦ Suggest" link beside each eligible label,
# results directly under that box. Card-level "Suggest all" / "Draft all" stay as the fast route.
# Run by build.py with its sub() helper in scope.

# quiet link styling
sub('</style>', '''.ai-link{background:none;border:0;padding:0 2px;color:var(--muted);font:inherit;font-size:12.5px;cursor:pointer;white-space:nowrap}
.ai-link:hover,.ai-link:focus-visible{color:var(--maroon);text-decoration:underline}
.ai-link:disabled{opacity:.5;cursor:default;text-decoration:none}
.field-head{display:flex;justify-content:space-between;align-items:baseline;gap:10px;margin-bottom:3px}
.field-head label{margin:0}
</style>''')

# field() can carry a suggest link and its result box
sub('''function field({ label, path, type = "text", rows = 3, hint = "", placeholder = "" }) {''',
    '''const aiLink = (path, text = "✦ Suggest") => `<button class="ai-link" data-action="ai" data-arg="field" data-target="${path}" title="Suggest ideas for this box">${text}</button>`;
const fieldKey = path => "fld_" + String(path).replace(/\\W/g, "_");
function field({ label, path, type = "text", rows = 3, hint = "", placeholder = "", suggest = false }) {''')
sub('''  return `<div class="field"><label for="${id}">${label}</label>${hint ? `<div class="hint">${hint}</div>` : ""}${input}</div>`;
}''', '''  const head = suggest ? `<div class="field-head"><label for="${id}">${label}</label>${aiLink(path)}</div>` : `<label for="${id}">${label}</label>`;
  return `<div class="field">${head}${hint ? `<div class="hint">${hint}</div>` : ""}${input}${suggest ? aiBox(fieldKey(path)) : ""}</div>`;
}''')

# learning activity card
sub('''<button class="btn sec small ai" data-action="ai" data-arg="draftAssess" data-target="${a.id}">Draft this activity</button>''',
    '''<button class="btn sec small ai" data-action="ai" data-arg="draftAssess" data-target="${a.id}" title="Draft every part of this activity at once">Draft all</button>''')
sub('''${field({ label:"Title", path:`assessments.${i}.title`, placeholder:"For example: Assignment: Pricing Recommendation Memo" })}''',
    '''${field({ label:"Title", path:`assessments.${i}.title`, placeholder:"For example: Assignment: Pricing Recommendation Memo", suggest:true })}''')
sub('''${field({ label:"What students will produce", path:`assessments.${i}.notes`, type:"textarea", rows:2, hint:"Optional. A sentence or two is enough for now." })}''',
    '''${field({ label:"What students will produce", path:`assessments.${i}.notes`, type:"textarea", rows:2, hint:"Optional. A sentence or two is enough for now.", suggest:true })}''')
sub('''${field({ label:"Real-world context", path:`assessments.${i}.context`, type:"textarea", rows:2, hint:"What professional task does this mirror? Where would students do something like this at work?" })}''',
    '''${field({ label:"Real-world context", path:`assessments.${i}.context`, type:"textarea", rows:2, hint:"What professional task does this mirror? Where would students do something like this at work?", suggest:true })}''')

# module card
sub('''<div class="row"><button class="btn sec ai" data-action="ai" data-arg="detail">Suggest details</button></div></div>''',
    '''<div class="row"><button class="btn sec ai" data-action="ai" data-arg="detail" title="Suggest topics, activities, materials and media for this module at once">Suggest all</button></div></div>''')
sub('''${field({ label:"Module title", path:`modules.${i}.title` })}''', '''${field({ label:"Module title", path:`modules.${i}.title`, suggest:true })}''')
sub('''${field({ label:"Module topics", path:`modules.${i}.topics`, type:"textarea", rows:3, hint:"One per line." })}''',
    '''${field({ label:"Module topics", path:`modules.${i}.topics`, type:"textarea", rows:3, hint:"One per line.", suggest:true })}''')
sub('''    <div class="field"><label>Learning Activities Plan, Part 1 (Canvas assignments)</label>''',
    '''    <div class="field"><div class="field-head"><label>Learning Activities Plan, Part 1 (Canvas assignments)</label>${aiLink(`modules.${i}.practice`)}</div>''')
sub('''placeholder="For example: Assignment: Plotting Graphs">${esc(m.practice)}</textarea></div>''',
    '''placeholder="For example: Assignment: Plotting Graphs">${esc(m.practice)}</textarea>${aiBox(fieldKey(`modules.${i}.practice`))}</div>''')
sub('''    <div class="field"><label>Learning Activities Plan, Part 2 (third-party tool activities)</label>''',
    '''    <div class="field"><div class="field-head"><label>Learning Activities Plan, Part 2 (third-party tool activities)</label>${aiLink(`modules.${i}.thirdParty`)}</div>''')
sub('''placeholder="For example: Perusall: Article Review">${esc(m.thirdParty)}</textarea></div>''',
    '''placeholder="For example: Perusall: Article Review">${esc(m.thirdParty)}</textarea>${aiBox(fieldKey(`modules.${i}.thirdParty`))}</div>''')
sub('''<button class="btn sec small ai" data-action="ai" data-arg="materials">Find materials</button></div>''',
    '''<button class="ai-link" data-action="ai" data-arg="materials" title="Search real article and book databases">✦ Find materials</button></div>''')
sub('''<button class="btn sec small ai" data-action="ai" data-arg="cohort">Suggest activities</button>''',
    '''<button class="ai-link" data-action="ai" data-arg="cohort" title="Suggest cohort session activities">✦ Suggest</button>''')
sub('''${field({ label:"Learning Media Plan", path:`modules.${i}.media`, type:"textarea", rows:2,''',
    '''${field({ label:"Learning Media Plan", path:`modules.${i}.media`, type:"textarea", rows:2, suggest:true,''')

# the suggestion type behind every box
sub('''  materials: {
    label: "Learning materials",''', '''  field: {
    perField: true,
    appendable: true,
    needs: () => firstNeed(NEED.clos),
    label: path => (fieldSpec(path) || {}).label || "Suggestions",
    prompt: path => {
      const sp = fieldSpec(path); if (!sp) return "";
      const n = +path.split(".")[1], cur = String(getPath(S, path) || "").trim();
      let ctx = "";
      if (path.startsWith("assessments.")) { const a = S.assessments[n] || {}; ctx = `\\n\\nLearning Activity ${n + 1} so far: title "${a.title || ""}", ${a.type === "thirdparty" ? `third-party tool ${a.tool || ""}` : "Canvas assignment"}, Module ${a.module || "?"}, measures ${(a.clos || []).map(cloLabel).join(", ") || "no objectives yet"}.${a.notes ? ` Students produce: ${a.notes}.` : ""}${a.context ? ` Context: ${a.context}.` : ""}`; }
      else { const md = S.modules[n] || {}; ctx = `\\n\\nModule ${n + 1} so far: title "${md.title || ""}", objectives ${(md.clos || []).map(cloLabel).join(", ") || "none yet"}, learning activities placed here: ${assessmentsIn(n).map(a => a.title).join("; ") || "none"}.${n > 0 ? ` Module ${n}: "${(S.modules[n - 1] || {}).title || ""}".` : ""}${S.modules[n + 1] && n + 1 < modCount() ? ` Module ${n + 2}: "${S.modules[n + 1].title || ""}".` : ""}`; }
      const now = cur ? `\\n\\nWhat's in this box now:\\n${cur}\\n${sp.mode === "append" ? "Suggest different items, not these." : "Offer real alternatives to it, not lightly reworded copies."}` : "";
      return `${sp.ask(n)}${ctx}${now}\\n\\nReturn only JSON: {"options":["..."]}`;
    },
    items: (d, path) => { const sp = fieldSpec(path) || {}; return (d.options || []).map(o => String(Array.isArray(o) ? o.join("\\n") : o).trim()).filter(Boolean)
      .map(o => ({ body:o, actions:[{ label:sp.mode === "append" ? "Add" : "Use this", once:true, fn:() => { if (sp.mode === "append") appendTo(path, o); else setPath(S, path, o); } }] })); }
  },
  materials: {
    label: "Learning materials",''')
sub('''const AIR = {}; // results by box key''', '''const AIR = {}; // results by box key
/* What each per-box suggestion asks for. append: options are added as new lines; replace: one option replaces the box */
const FIELD_SPECS = [
  { re:/^modules\\.\\d+\\.title$/, mode:"replace", label:"Module title ideas", ask:n => `Suggest 4 titles for Module ${n + 1}. Base them on its topics, the objectives it meets and the learning activities placed in it, and make them fit the modules before and after it. Each is 3 to 7 words, plain and specific, with no colon or subtitle.` },
  { re:/^modules\\.\\d+\\.topics$/, mode:"append", label:"Topic ideas", ask:n => `Suggest 3 to 5 topics for Module ${n + 1}, one short phrase each, that build toward its objectives and the learning activities placed in it. Don't repeat topics listed in this or other modules.` },
  { re:/^modules\\.\\d+\\.practice$/, mode:"append", label:"Canvas activity ideas", ask:n => `Suggest 3 practice or formative Canvas activities for Module ${n + 1} that prepare students for the learning activities placed in it. Write each as "Assignment: Title", "Discussion: Title" or "Quiz: Title".` },
  { re:/^modules\\.\\d+\\.thirdParty$/, mode:"append", label:"Third-party tool ideas", ask:n => `Suggest 3 third-party tool activities for Module ${n + 1}, using Perusall, Peerceptiv or another tool a business course could use. Write each as "Perusall: Title" or "Peerceptiv: Title".` },
  { re:/^modules\\.\\d+\\.media$/, mode:"append", label:"Media ideas", ask:n => `Suggest 3 pieces of media the faculty member could record or produce for Module ${n + 1}, beyond the required module overview, course introduction and course conclusion videos. Write each as "Recorded Video: Topic", "Audio: Topic" or "Graphic: Topic". The module must stay within 30 minutes of video.` },
  { re:/^assessments\\.\\d+\\.title$/, mode:"replace", label:"Title ideas", ask:n => `Suggest 4 titles for Learning Activity ${n + 1}. Start each with its kind, as in "Assignment: Pricing Recommendation Memo" or "Perusall: Article Review", and name what students produce.` },
  { re:/^assessments\\.\\d+\\.notes$/, mode:"replace", label:"What students will produce", ask:n => `Suggest 3 ways to describe what students will produce in Learning Activity ${n + 1}, one or two sentences each, naming the deliverable and its scope.` },
  { re:/^assessments\\.\\d+\\.context$/, mode:"replace", label:"Real-world context ideas", ask:n => `Suggest 3 real-world contexts for Learning Activity ${n + 1}, one or two sentences each, naming the professional task it mirrors and where these learners would do it at work.` }
];
const fieldSpec = path => FIELD_SPECS.find(f => f.re.test(String(path || "")));''')
sub('''  const def = AI_DEFS[r.def];
  const head = `<div class="ai-label"><span>✦ ${def.label}</span>''', '''  const def = AI_DEFS[r.def];
  const head = `<div class="ai-label"><span>✦ ${typeof def.label === "function" ? def.label(r.target) : def.label}</span>''')
sub('''  const i = def.perAssessment ? target : Math.min(S.moduleTab || 0, modCount() - 1);
  const key = def.perAssessment ? `${defName}_${target}` : def.perModule ? `${defName}_${i}` : defName;''',
    '''  const i = def.perField || def.perAssessment ? target : Math.min(S.moduleTab || 0, modCount() - 1);
  const key = def.perField ? fieldKey(target) : def.perAssessment ? `${defName}_${target}` : def.perModule ? `${defName}_${i}` : defName;''')
