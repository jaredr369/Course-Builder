"""Build Course Creator 3.1.27 from 3.5 plus the Canvas Build phase."""
import json, re, sys

src = open('cc35.html', encoding='utf8').read()
snips = json.load(open('canvas/snips.json'))
for _k in [k for k in snips if k == 'wrap' or k.startswith('gs')]:
    snips[_k] = re.sub(r'data-nav-class="[^"]*"', 'data-nav-class=""', snips[_k])
canvas_js = open('src/canvas.js', encoding='utf8').read().replace('/*__CV_SNIPS__*/{}', json.dumps(snips))
canvas_css = open('src/canvas.css', encoding='utf8').read()

def sub(old, new, count=1):
    global src
    n = src.count(old)
    if n != count:
        sys.exit(f'expected {count} match(es), found {n}: {old[:90]!r}')
    src = src.replace(old, new)

# version
sub('title="Version 3.5">3.5<', 'title="Version 3.1.27">3.1.27<')
sub('<title>Course Creator 3.5</title>', '<title>Course Creator 3.1.27</title>')
sub('" · Course Creator 3.5";', '" · Course Creator 3.1.27";')

# styles
sub('</style>', canvas_css + '</style>')

# third phase tab
sub('<button role="tab" data-phase="dev" id="phDev"><span class="pn">2</span>Course Development</button>',
    '<button role="tab" data-phase="dev" id="phDev"><span class="pn">2</span>Course Development</button>\n'
    '      <button role="tab" data-phase="canvas" id="phCanvas"><span class="pn">3</span>Canvas Build</button>')

# chrome: which tab is on, and the window title
sub('$("#phPlan").classList.toggle("on", ph === "plan"); $("#phDev").classList.toggle("on", ph === "dev");',
    'const cv = ph === "dev" && S.view === "canvas";\n'
    '  $("#phPlan").classList.toggle("on", ph === "plan"); $("#phDev").classList.toggle("on", ph === "dev" && !cv); $("#phCanvas").classList.toggle("on", cv);\n'
    '  $("#phCanvas").setAttribute("aria-selected", cv); $("#phCanvas").classList.toggle("locked", S.phase !== "dev");')
sub('$("#phDev").setAttribute("aria-selected", ph === "dev");', '$("#phDev").setAttribute("aria-selected", ph === "dev" && !cv);')
sub('document.title = (ph === "dev" ? "Course Development" : "Course Planning") + " · Course Creator 3.1.27";',
    'document.title = (cv ? "Canvas Build" : ph === "dev" ? "Course Development" : "Course Planning") + " · Course Creator 3.1.27";')

# DEV render routes to Canvas Build
sub('function render() {\n  renderNav();\n  const v = P.view.screen;',
    'function render() {\n  if (S.view === "canvas") { canvasRender(); updateAiDot(); return; }\n  renderNav();\n  const v = P.view.screen;')

# hand-off at the end of Course Development
sub('''  <div class="card"><h2>What happens next</h2>
    <p>Your instructional designer builds the Canvas course from these documents and completes the Media Plan in 06 - Media Production. Video scripts go to Learning Media for review at least three days before recording.</p></div>`;''',
    '''  <div class="card"><h2>What happens next</h2>
    <p>Video scripts go to Learning Media for review at least three days before recording, and your instructional designer completes the Media Plan in 06 - Media Production.</p></div>
  <div class="card dev-card"><div class="eyebrow">Next phase</div><h2>Move on to Canvas Build</h2><p class="sub" style="margin-bottom:10px">Canvas Build reads these documents back, including any edits made in Word, and turns each one into a page in the Mays Canvas template. Whoever builds the course, usually your instructional designer, copies each page into Canvas and follows a checklist for its settings, rubric and quiz questions.</p><button class="btn" data-action="toCanvas">Go to Canvas Build →</button></div>`;''')

# a way back to the document list at the bottom of every document editor
sub("""        <button class="btn" data-action="acceptSave" data-arg="${it.id}">${it.status === "saved" ? "Save again" : "Accept and save"}</button></div>
    </div>
  </div>`;""", """        <button class="btn" data-action="acceptSave" data-arg="${it.id}">${it.status === "saved" ? "Save again" : "Accept and save"}</button></div>
    </div>
  </div>
  <div class="stepnav"><button class="btn sec" data-action="go" data-arg="build">← All documents</button></div>`;""")

# cohort sessions run 90 minutes
sub('time:"60 minutes", students:""', 'time:"90 minutes", students:""')
sub('return m ? (m[2] ? +m[1] : +m[1] / 60) : 1; }', 'return m ? (m[2] ? +m[1] : +m[1] / 60) : 1.5; }')
sub('F.tx("data.time", "Allotted time", "", "For example: 60 minutes")', 'F.tx("data.time", "Allotted time", "Cohort sessions run 90 minutes.", "90 minutes")')
sub('{"sessionTitle": "", "time": "60 minutes",', '{"sessionTitle": "", "time": "90 minutes",')
sub('Build the session around active learning (breakouts, debate, problem solving), with little lecture.',
    'The session runs 90 minutes, and the durations in the instructional plan must add up to 90 minutes. Build the session around active learning (breakouts, debate, problem solving), with little lecture.')
sub('including rough timing for a 60 to 90 minute session.', 'including rough timing within a 90-minute session.')
sub('asynchronous Canvas modules plus a live cohort session in each module.', 'asynchronous Canvas modules plus a live 90-minute cohort session in each module from Module 2 on. Module 1 has no cohort session and no cohort session assignments. Each module takes students 10 to 12 hours, except Module 1, a lighter start of about 4 hours.')
sub('eight weekly modules in Canvas plus a live cohort session in most modules.', 'eight weekly modules in Canvas plus a live 90-minute cohort session in most modules from Module 2 on. Module 1 has no cohort session and no cohort session assignments.')
# check that each lesson plan fills the 90 minutes
sub("""  items.filter(i => i.status === "review").forEach(""", """  items.filter(i => i.kind === "cohort").forEach(i => {
    const segs = (i.data.plan || []).filter(r => r && (r.section || r.details));
    const t = String(i.data.time || ""), tm = t.match(/(\\d+(?:\\.\\d+)?)\\s*(h|hour)?/i), mins = tm ? (tm[2] ? +tm[1] * 60 : +tm[1]) : 90;
    if (mins !== 90) out.push({ level:"warn", area:"Cohort sessions", text:`The Module ${i.module} cohort session is set to ${t}. Cohort sessions run 90 minutes.`, itemId:i.id });
    if (!segs.length) return;
    const sum = segs.reduce((a, r) => { const m = String(r.duration || "").match(/(\\d+(?:\\.\\d+)?)\\s*(h|hour)?/i); return a + (m ? (m[2] ? +m[1] * 60 : +m[1]) : 0); }, 0);
    if (sum && Math.abs(sum - 90) > 5) out.push({ level:"warn", area:"Cohort sessions", text:`The Module ${i.module} lesson plan segments add up to ${Math.round(sum)} minutes. Plan for 90.`, itemId:i.id });
  });
  items.filter(i => i.status === "review").forEach(""")
# sessions not started yet still carrying the old 60-minute default move to 90
sub("""function migrate() {
  if (MIGRATED) return; MIGRATED = true;""", """function migrate() {
  if (MIGRATED) return; MIGRATED = true;
  for (const p of Object.values(LIB.projects)) (p.items || []).forEach(i => { if (i.kind === "cohort" && i.status === "todo" && i.data && i.data.time === "60 minutes") i.data.time = "90 minutes"; });""")

exec(open('src/reading_patch.py', encoding='utf8').read())

# text boxes start at three lines and grow to fit what's typed
sub('\nDEV.folderReady();\n', '''
DEV.folderReady();

/* ---------------- Text boxes: three lines to start, then grow to fit ---------------- */
(function () {
  const skip = t => t.readOnly || t.classList.contains("cv-code");
  function fit(t) {
    if (!t || t.tagName !== "TEXTAREA" || skip(t)) return;
    if (t.rows !== 3) t.rows = 3;
    if (!t.offsetParent) return;
    t.style.overflowY = "hidden"; t.style.height = "auto";
    const cs = getComputedStyle(t);
    t.style.height = (t.scrollHeight + parseFloat(cs.borderTopWidth) + parseFloat(cs.borderBottomWidth)) + "px";
  }
  const fitIn = root => { if (!root || root.nodeType !== 1) return; if (root.tagName === "TEXTAREA") fit(root); else root.querySelectorAll("textarea").forEach(fit); };
  document.addEventListener("input", e => fit(e.target), true);
  document.addEventListener("focusin", e => fit(e.target), true);
  document.addEventListener("toggle", e => fitIn(e.target), true);
  new MutationObserver(muts => {
    const roots = new Set();
    for (const m of muts) {
      if (m.type === "attributes") roots.add(m.target);
      else m.addedNodes.forEach(n => roots.add(n));
    }
    roots.forEach(fitIn);
  }).observe(document.body, { childList:true, subtree:true, attributes:true, attributeFilter:["hidden"] });
  let rt; window.addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(() => fitIn(document.body), 150); });
  fitIn(document.body);
})();
''')

exec(open('src/media_patch.py', encoding='utf8').read())

# Module 1 has no cohort session and no cohort session assignments
sub("""      <textarea id="f_modules_${i}_cohort" data-bind="modules.${i}.cohort" rows="3">${esc(m.cohort)}</textarea>
      ${aiBox("cohort_" + i)}""", """      ${i === 0 ? `<div class="flag${m.cohort.trim() ? "" : " warn"}" style="margin:4px 0 0">Module 1 has no cohort session and no cohort session assignments. Cohort sessions start in Module 2.${m.cohort.trim() ? " Move these activities to a later module, then clear this box." : ""}</div>${m.cohort.trim() ? `<textarea id="f_modules_${i}_cohort" data-bind="modules.${i}.cohort" rows="3">${esc(m.cohort)}</textarea>` : ""}` : `<textarea id="f_modules_${i}_cohort" data-bind="modules.${i}.cohort" rows="3">${esc(m.cohort)}</textarea>
      ${aiBox("cohort_" + i)}`}""")
sub("""        <button class="btn sec small ai" data-action="ai" data-arg="cohort">Suggest activities</button></div>""", """        ${i === 0 ? "" : `<button class="btn sec small ai" data-action="ai" data-arg="cohort">Suggest activities</button>`}</div>""")
sub("""    if (!m.cohort.trim()) add("warn", `${n} has no cohort session activity. This is the main place for active learning.`, 3);""",
    """    if (i > 0 && !m.cohort.trim()) add("warn", `${n} has no cohort session activity. This is the main place for active learning.`, 3);
    if (i === 0 && m.cohort.trim()) add("gap", "Module 1 has no cohort session or cohort session assignments. Move its cohort activities to Module 2 or later.", 3);""")
sub("""  items.filter(i => i.kind === "cohort").forEach(i => {""", """  items.filter(i => i.module === 1 && (i.kind === "cohort" || i.kind === "activity")).forEach(i => out.push({ level:"gap", area:"Cohort sessions", text:`${i.kind === "cohort" ? "Module 1 has a cohort session planned." : `"${bareTitle(i.title)}" is a cohort activity in Module 1.`} Cohort sessions and cohort session assignments start in Module 2, so move it to a later module or remove it.`, itemId:i.id }));
  items.filter(i => i.kind === "cohort").forEach(i => {""")

# Module 1 is a lighter start: about 4 hours of coursework instead of 10 to 12
sub("Each module should take students 10 to 12 hours in total, and each module may hold no more than 30 minutes of recorded video.",
    "Each module should take students 10 to 12 hours in total, except Module 1, which is a lighter start of about 4 hours. Each module may hold no more than 30 minutes of recorded video.")
sub("""    if (s.hours > 12.5) out.push({ level:"warn", area:"Workload", text:`Module ${m} comes to about ${s.hours} hours. The target is 10 to 12.`, module:m });
    else if (s.hours < 9.5) out.push({ level:"warn", area:"Workload", text:`Module ${m} comes to about ${s.hours} hours. The target is 10 to 12.`, module:m });""",
"""    const [lo, hi] = workTarget(m), tgt = m === 1 ? "The target for Module 1 is about 4." : "The target is 10 to 12.";
    if (s.hours > hi + 0.5) out.push({ level:"warn", area:"Workload", text:`Module ${m} comes to about ${s.hours} hours. ${tgt}`, module:m });
    else if (s.hours < lo - 0.5) out.push({ level:"warn", area:"Workload", text:`Module ${m} comes to about ${s.hours} hours. ${tgt}`, module:m });""")
sub("function runChecks() {", "const workTarget = m => m === 1 ? [3.5, 4.5] : [10, 12];\nfunction runChecks() {")
sub("""${meter("Workload", st.hours, 10, 12, 14, "h")}""", """${meter("Workload", st.hours, workTarget(m)[0], workTarget(m)[1], m === 1 ? 6 : 14, "h")}""")
sub("Each module should take students 10 to 12 hours and hold no more than 30 minutes of video.", "Each module should take students 10 to 12 hours, except Module 1, which is a lighter start of about 4 hours. No module may hold more than 30 minutes of video.")
sub("Module workload so far: about ${st.hours} hours of a 10 to 12 hour target.", "Module workload so far: about ${st.hours} hours of ${it.module === 1 ? \"an approximately 4 hour target (Module 1 is a lighter start)\" : \"a 10 to 12 hour target\"}.")
sub("  P.modules = P.plan.modules.map(() => ({ other:\"3\" }));", "  P.modules = P.plan.modules.map((_, k) => ({ other:k ? \"3\" : \"1\" }));")
sub("  P.modules = newP.modules.map((m, k) => P.modules[k] || { other:\"3\" });", "  P.modules = newP.modules.map((m, k) => P.modules[k] || { other:k ? \"3\" : \"1\" });")

# AI suggestions appear directly under the button that asked for them
sub("""      <button class="btn sec ai" data-action="ai" data-arg="vision">Draft options</button></div>
    ${field({ label:"Vision", path:"vision", type:"textarea", rows:4 })}
    <div class="count" id="visionCount">${visionCount()}</div>
    ${aiBox("vision")}""", """      <button class="btn sec ai" data-action="ai" data-arg="vision">Draft options</button></div>
    ${aiBox("vision")}
    ${field({ label:"Vision", path:"vision", type:"textarea", rows:4 })}
    <div class="count" id="visionCount">${visionCount()}</div>""")
sub("""<button class="btn sec ai" data-action="ai" data-arg="suggestClos">Suggest CLOs</button></div></div>
    ${S.clos.map((c, i) => `""", """<button class="btn sec ai" data-action="ai" data-arg="suggestClos">Suggest CLOs</button></div></div>
    ${aiBox("checkClos")}${aiBox("suggestClos")}
    ${S.clos.map((c, i) => `""")
sub("""<span class="count ${fc < 3 || fc > 5 ? "warn" : ""}" id="cloCount">${fc} of 3–5</span></div>
    ${aiBox("checkClos")}${aiBox("suggestClos")}""", """<span class="count ${fc < 3 || fc > 5 ? "warn" : ""}" id="cloCount">${fc} of 3–5</span></div>""")

# suggestions come 3 to 5 at a time, with Show more options for the rest
sub('Suggest 4 to 6 learning activities that together give evidence for every course-level objective.', 'Suggest 3 to 5 learning activities that together give evidence for every course-level objective.')
sub('Suggest 4 course-level objectives for this course,', 'Suggest 3 to 5 course-level objectives for this course,')
sub('Fill each field only with what this module needs.', 'Fill each field only with what this module needs: 3 to 5 module topics, and no more than 3 items in any other field.')
sub("""  suggestClos: {""", """  suggestClos: {
    appendable: true,""")
sub("""  suggestAssess: {""", """  suggestAssess: {
    appendable: true,""")
sub("""  detail: {""", """  detail: {
    appendable: true,""")
sub("""  vision: {""", """  vision: {
    appendable: true,""")
# materials: three searches, two results each, so a module gets 3 to 5 concrete sources at a time
sub('Give 2 article searches (peer-reviewed research or practitioner journals such as Harvard Business Review or MIT Sloan Management Review), 1 book search, 1 video search and 1 website search.',
    'Give exactly 3 searches: 1 article search (peer-reviewed research or practitioner journals such as Harvard Business Review or MIT Sloan Management Review), 1 book or second article search, and 1 video or website search.')
sub('for (const q of (d.searches || []).slice(0, 7)) {', 'for (const q of (d.searches || []).slice(0, 3)) {')
sub('for (const w of await searchArticles(query)) out.push(', 'for (const w of (await searchArticles(query)).slice(0, 2)) out.push(')
sub('for (const bk of await searchBooks(query)) out.push(', 'for (const bk of (await searchBooks(query)).slice(0, 2)) out.push(')
# when asking for more, tell the coach what was already shown, contents and all
sub('${prev.items.map(it => "- " + it.title).join("\\n")}', '${prev.items.filter(it => !it.result).map(it => "- " + [it.title, it.body].filter(Boolean).join(": ").replace(/\\s*\\n\\s*/g, "; ").slice(0, 300)).join("\\n")}\\nGive 3 to 5 new suggestions.')

exec(open('src/fieldai_patch.py', encoding='utf8').read())

exec(open('src/sequence_patch.py', encoding='utf8').read())

exec(open('src/cohortall_patch.py', encoding='utf8').read())
exec(open('src/gettingstarted_patch.py', encoding='utf8').read())
exec(open('src/plandot_patch.py', encoding='utf8').read())
exec(open('src/finishdone_patch.py', encoding='utf8').read())
exec(open('src/modcount_patch.py', encoding='utf8').read())
exec(open('src/restore_patch.py', encoding='utf8').read())
exec(open('src/foundfiles_patch.py', encoding='utf8').read())

# Module 1 needs no cohort activity anywhere: step gate, progress, tab dot, review stat
sub("""      const parts = [!md.title.trim() && "title", !md.clos.length && "CLOs met", !md.cohort.trim() && "cohort session activity"].filter(Boolean);""",
    """      const parts = [!md.title.trim() && "title", !md.clos.length && "CLOs met", k > 0 && !md.cohort.trim() && "cohort session activity"].filter(Boolean);""")
sub("""  if (i === 3) { const ms = activeModules(); return ms.filter(m => m.title.trim() && m.clos.length && m.cohort.trim()).length / ms.length; }""",
    """  if (i === 3) { const ms = activeModules(); return ms.filter((m, k) => m.title.trim() && m.clos.length && (k === 0 || m.cohort.trim())).length / ms.length; }""")
sub("""  const full = mm => mm.title.trim() && mm.clos.length && mm.cohort.trim();""", """  const full = (mm, k) => mm.title.trim() && mm.clos.length && (k === 0 || mm.cohort.trim());""")
sub("""full(mm) ? "full" : \"\"""", """full(mm, k) ? "full" : \"\"""")
sub("""<div class="stat"><b>${ms.filter(m => m.cohort.trim()).length} / ${ms.length}</b><span>modules with a cohort activity</span></div>""",
    """<div class="stat"><b>${ms.slice(1).filter(m => m.cohort.trim()).length} / ${Math.max(0, ms.length - 1)}</b><span>modules with a cohort activity (Module 2 on)</span></div>""")

# Canvas Build code inside the development scope, plus its export
sub('\nreturn {\n  render: () => { select(); render(); },\n  startDialog,',
    '\n' + canvas_js + '\nreturn {\n  render: () => { select(); render(); },\n  openCanvas,\n  startDialog,')

# phase tab handlers
sub('''$("#phDev").onclick = () => {
  if (S.phase !== "dev") return DEV.startDialog();
  if (S.replan) return DEV.returnFromPlanning();
  S.view = "dev"; save(); render();
};''', '''$("#phDev").onclick = () => {
  if (S.phase !== "dev") return DEV.startDialog();
  if (S.replan) return DEV.returnFromPlanning();
  S.view = "dev"; save(); render();
};
$("#phCanvas").onclick = () => {
  if (S.replan) return DEV.returnFromPlanning();
  DEV.openCanvas();
};''')

# a locked third tab reads as not yet available
sub('.phase-switch button.on{', '.phase-switch button.locked{opacity:.5}\n.phase-switch button.on{')

# Getting Started is module 0: labels in the development scope read "GS" and "Getting Started" for it
_a = src.index('const DEV = (function () {'); _b = src.index('\n})();', _a)
_seg = src[_a:_b]
_seg = re.sub(r'(?<![A-Za-z])M\$\{(\w+)\.module\}', r'${MT(\1.module)}', _seg)
_seg = re.sub(r'Module \$\{(\w+\.module|old|module|from)\}', r'${MN(\1)}', _seg)
src = src[:_a] + _seg + src[_b:]

open('dist/Course Creator 3.1.27.html', 'w', encoding='utf8').write(src)
print('built', len(src))
