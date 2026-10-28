# Getting Started (module 0): its own document in Course Development, the course introduction video,
# and any learning activities placed there in planning.
# Run by build.py with its sub() helper in scope.

# ---------- shared labels, visible to planning and development ----------
sub('const RQM = {', r'''/* Getting Started is module 0 */
const MT = m => String(m) === "0" ? "GS" : `M${m}`;
const MN = m => String(m) === "0" ? "Getting Started" : `Module ${m}`;
const isGS = m => String(m) === "0";
const modNum = v => { const n = parseInt(v, 10); return Number.isNaN(n) ? 1 : n; };
const RQM = {''')

# ---------- planning: a learning activity can sit in Getting Started ----------
sub('S.assessments.forEach(a => { const k = (parseInt(a.module, 10) || 1) - 1; if (k < n) a.module = String(newIdx[k] + 1); });',
    'S.assessments.forEach(a => { if (isGS(a.module)) return; const k = (parseInt(a.module, 10) || 1) - 1; if (k < n) a.module = String(newIdx[k] + 1); });')
sub('parseInt(a.module, 10) || 1', 'modNum(a.module)', 8)
sub('parseInt(o.module, 10) || 1,', 'modNum(o.module),')
sub('''        <select id="mod_${a.id}" data-bind-select="assessments.${i}.module">
          ${Array.from''', '''        <select id="mod_${a.id}" data-bind-select="assessments.${i}.module">
          <option value="0" ${isGS(a.module) ? "selected" : ""}>Getting Started</option>
          ${Array.from''')
sub('''(a.tool || "tool not set")}, Module ${a.module}, measures''', '''(a.tool || "tool not set")}, ${MN(a.module)}, measures''')
sub('Required: a module overview video${i === 0 ? " and the course introduction video" : ""}${i === modCount() - 1 ? " and the course conclusion video" : ""}.`',
    'Required: a module overview video${i === modCount() - 1 ? " and the course conclusion video" : ""}.${i === 0 ? " The course introduction video belongs to Getting Started, and Course Development adds it for you." : ""}`')
# the course introduction video is no longer planned in Module 1: it's added to Getting Started in development
sub('  if (!r.intro) { if (s.modules[0] && !mediaHas(s.modules[0].media, "intro")) mediaAdd(s.modules[0], "intro"); r.intro = true; }', '  r.intro = true;')
sub('    if (i === 0 && !mediaHas(m.media, "intro")) add("gap", "Module 1 needs the course introduction video in its Learning Media Plan.", 3, "intro:0");\n', '')
sub('/* Move a whole module. Learning activities follow it; the course introduction stays in Module 1 and', '/* Move a whole module. Learning activities follow it; a course introduction line stays in Module 1 and')

# ---------- development: the Getting Started document ----------
sub('''  activity:   { label:"Cohort activity", file:"Cohort Activity", folder:"cohort", graded:false, hours:0 }
};''', '''  activity:   { label:"Cohort activity", file:"Cohort Activity", folder:"cohort", graded:false, hours:0 },
  gettingstarted: { label:"Getting Started", file:"Getting Started", folder:"activities", graded:false, hours:0 }
};''')
sub('function fileBaseFor(it) {\n', 'function fileBaseFor(it) {\n  if (it.kind === "gettingstarted") return "GS Getting Started";\n')
sub('const KIND_ORDER = { video:0,', 'const KIND_ORDER = { gettingstarted:-1, video:0,')

sub('function defaultData(kind, title, extra = {}) {', r'''/* What faculty write for Getting Started. Canvas Build fills the Welcome page, the Welcome announcement,
   Class Introductions and the Syllabus Acknowledgement Quiz from it. */
const GS_KEYS = ["welcome", "instructorIntro", "profName", "email", "phone", "hours", "taName", "taEmail", "taHours", "materials"];
const GS_FIRST_NOTE = "This is students' first course in the program, so the discussion uses the standard introduction prompt.";
const GS_QA = "Include the optional General Q&A discussion";
function gsDefaults(p) {
  p = p || {};
  const books = [], seen = new Set();
  ((p.plan || {}).modules || []).forEach(m => linesOf(m.materials).filter(l => /^\s*textbook\b/i.test(l)).forEach(l => { const k = norm(l.replace(/chapters?\s*[\d\-–, ]+\.?\s*$/i, "")); if (!seen.has(k)) { seen.add(k); books.push(l.replace(/\s*,?\s*chapters?\s*[\d\-–, ]+\.?\s*$/i, ".").replace(/\.\.$/, ".")); } }));
  const d = { welcome:"", instructorIntro:"", profName:(p.setup || {}).instructor || "", email:"Contact me using the Canvas Inbox in the toolbar.", phone:"", hours:"", taName:"", taEmail:"", taHours:"",
    materials:books.join("\n"), introFirst:false, introPrompt:"", includeQA:true, questions:[] };
  // anything already typed on the old Canvas Build Welcome page carries over
  const pg = ((p.canvas || {}).pages || {}).welcome || {};
  GS_KEYS.forEach(k => { if (pg[k] !== undefined && String(pg[k]).trim()) d[k] = pg[k]; });
  return d;
}
const isIntroVideo = it => it.kind === "video" && REQ.intro.test(it.title) && !REQ.overview.test(it.title);
/* Every course in development has one Getting Started document, and its introduction videos live there */
function gsEnsure(p) {
  if (!p || !p.plan || !Array.isArray(p.items)) return false;
  let changed = false;
  if (!p.items.some(i => i.kind === "gettingstarted")) {
    const it = newItem("gettingstarted", 0, "Getting Started", { origin:"required" }); it.data = gsDefaults(p); it.src = null; it.srcKey = null;
    p.items.unshift(it); changed = true;
  }
  if (!p.gsV) {
    p.items.forEach(i => { if (i.module === 1 && isIntroVideo(i)) { i.module = 0; changed = true; } });
    p.gsV = 1; changed = true;
  }
  if (changed) p.items.sort((a, b) => a.module - b.module || ((KIND_ORDER[a.kind] ?? 9) - (KIND_ORDER[b.kind] ?? 9)) || (a.origin === "required" ? -1 : 0) - (b.origin === "required" ? -1 : 0));
  return changed;
}
function defaultData(kind, title, extra = {}) {''')
sub('''    case "activity": return { graded:false,''', '''    case "gettingstarted": return gsDefaults(P);
    case "activity": return { graded:false,''')

# the course introduction video belongs to Getting Started; the plan keeps it in Module 1's media list
sub('''  if (!vids(1).some(v => REQ.intro.test(v.title))) need.push({ module:1, title:"Course Introduction", req:"intro" });''',
    '''  if (!vids(0).some(v => REQ.intro.test(v.title))) need.push({ module:0, title:"Course Introduction", req:"intro" });''')
sub('''    linesOf(mod.media).forEach(l => add("video", m, l, { clos }, { t:"l", f:"media", m, line:l }));''',
    '''    linesOf(mod.media).forEach(l => add("video", m === 1 && REQ.intro.test(l) && !REQ.overview.test(l) ? 0 : m, l, { clos }, { t:"l", f:"media", m, line:l }));''')
sub('''  P.items = itemsFromPlan(P.plan);
  P.modules =''', '''  P.items = itemsFromPlan(P.plan); P.gsV = 1; gsEnsure(P);
  P.modules =''')
sub('''function select() {
  migrate();
  if (P && P.id === S.id && LIB.projects[S.id] === P) return;''', '''function select() {
  migrate();
  if (P && P.id === S.id && LIB.projects[S.id] === P) { if (gsEnsure(P)) save(); return; }''')
sub('''  if (!P) { P = blankProject(S.id); P.devStarted = Date.now(); LIB.projects[S.id] = P; adoptPlan(S); saveNow(); }
}''', '''  if (!P) { P = blankProject(S.id); P.devStarted = Date.now(); LIB.projects[S.id] = P; adoptPlan(S); saveNow(); }
  if (gsEnsure(P)) saveNow();
}''')
sub('''  for (const p of Object.values(LIB.projects)) (p.items || []).forEach(i => { if (i.kind === "cohort" && i.status === "todo" && i.data && i.data.time === "60 minutes") i.data.time = "90 minutes"; });''',
    '''  for (const p of Object.values(LIB.projects)) (p.items || []).forEach(i => { if (i.kind === "cohort" && i.status === "todo" && i.data && i.data.time === "60 minutes") i.data.time = "90 minutes"; });
  if (Object.values(LIB.projects).map(gsEnsure).some(Boolean)) saveNow();''')

# dates: Getting Started runs in the first week
sub('function datesFor(n) {\n  const w = weekOf(n);', 'function datesFor(n) {\n  const w = weekOf(Math.max(1, n));')

# checks: Getting Started has no module objectives to compare against
sub('else { const off = i.clos.filter(c => !mod.clos.includes(c));', 'else { const off = i.module === 0 ? [] : i.clos.filter(c => !mod.clos.includes(c));')

# document list: a Getting Started card before Module 1
sub('  for (let m = 1; m <= modCount(); m++) html += moduleCard(m);\n  return html;',
    '  html += gsCard();\n  for (let m = 1; m <= modCount(); m++) html += moduleCard(m);\n  return html;')
sub('function moduleCard(m) {', r'''function gsCard() {
  const its = live().filter(i => i.module === 0), removed = P.items.filter(i => i.removed && i.module === 0), d = datesFor(0);
  return `<section class="card mod-card" id="mod0">
    <div class="mod-head"><div style="min-width:0;flex:1">
      <div class="eyebrow">Orientation${d.short ? ` · due ${d.short}` : ""}</div><h2>Getting Started</h2>
      <p class="sub">The orientation module students open before Module 1. Its work isn't counted in Module 1's hours or video time.</p></div></div>
    <ul class="items">${its.map(itemRow).join("")}</ul>
    <div class="mod-foot"><button class="btn sec small" data-action="addItem" data-arg="0">+ Add an item</button></div>
    ${removed.length ? `<div class="removed-list">Removed: ${removed.map(r => `${esc(bareTitle(r.title))} <button class="btn link small" data-action="restoreItem" data-arg="${r.id}">Restore</button>`).join(" · ")}</div>` : ""}
  </section>`;
}
function moduleCard(m) {''')
sub('''<button class="btn sec small" data-action="changeItem" data-arg="${it.id}" title="Rename, move, change type or objectives, or remove">Change</button>''',
    '''${it.kind === "gettingstarted" ? "" : `<button class="btn sec small" data-action="changeItem" data-arg="${it.id}" title="Rename, move, change type or objectives, or remove">Change</button>`}''')
sub('''<button class="btn link small" data-action="changeItem" data-arg="${it.id}">Change title, type, module or objectives</button>''',
    '''${it.kind === "gettingstarted" ? "" : `<button class="btn link small" data-action="changeItem" data-arg="${it.id}">Change title, type, module or objectives</button>`}''')
sub('''├─ 03 - Learning Activities  (assignments, discussions, quizzes)''', '''├─ 03 - Learning Activities  (Getting Started, assignments, discussions, quizzes)''')

# change dialog: Getting Started is a place to move things to; the document itself isn't a type to pick
sub('''  const mods = Array.from({ length:modCount() }, (_, k) =>''', '''  const mods = `<option value="0" ${(it ? it.module : addModule) === 0 ? "selected" : ""}>Getting Started</option>` + Array.from({ length:modCount() }, (_, k) =>''')
sub('''  const kinds = Object.entries(KINDS).filter(([k]) => k !== "cohort" || isAdd)''', '''  const kinds = Object.entries(KINDS).filter(([k]) => k !== "gettingstarted" && (k !== "cohort" || isAdd))''')
sub('''logChange(it, "Added", `Added video script "${t}" to Module ${m}`''', '''logChange(it, "Added", `Added video script "${t}" to ${MN(m)}`''')
# a plan line for something moved into Getting Started stays where it is in the plan
sub('''    if (type === "module") { removeLine(src.m, src.f, oldLine); addLine(it.module, src.f, oldLine); src.m = it.module; }''',
    '''    if (type === "module" && it.module !== 0) { removeLine(src.m, src.f, oldLine); addLine(it.module, src.f, oldLine); src.m = it.module; }''')

# editor
sub('''const SCHEMAS = {''', r'''const SCHEMAS = {
  gettingstarted: [{ type:"gsHelp" },
    F.sec("Welcome"), F.ta("data.welcome", "Welcome message", "A few sentences in your own voice about what the course offers and what students can expect. It goes on the course Welcome page, after \"Welcome to the course!\", and in the Welcome announcement.", 4),
    F.ta("data.instructorIntro", "About you", "A short introduction for the Instructor tab: your background, your career path, why you teach this course. It's added to the Welcome announcement too.", 4),
    F.sec("Contact information"),
    { type:"pair", fields:[F.tx("data.profName", "Professor", "As students should see it.", "For example: Dr. Jordan Rivera"), F.tx("data.email", "Email", "Leave the Canvas Inbox wording, or replace it with an address.")] },
    { type:"pair", fields:[F.tx("data.phone", "Phone (optional)", "Leave blank to leave it off the page."), F.tx("data.hours", "Virtual office hours", "", "For example: Tuesdays, 5:00 to 6:00 p.m. CT")] },
    { type:"pair", fields:[F.tx("data.taName", "Teaching assistant (optional)", "Leave blank if the course has none."), F.tx("data.taEmail", "TA email", "")] },
    F.tx("data.taHours", "TA virtual office hours", ""),
    F.sec("Course materials"), F.ta("data.materials", "Assigned materials", "One per line, in APA style. Start with a label such as Textbook: to match the template, or say that all materials are provided in Canvas.", 3),
    F.sec("Class Introductions"),
    F.ck("data.introFirst", "This is students' first course in the program", "Uses the standard introduction discussion: preferred name, what students hope to gain, and a fun fact."),
    F.ta("data.introPrompt", "Introduction prompt", "Used when the box above isn't ticked. Ask students to introduce themselves in a way that ties to this course, such as their experience with the subject. Add any links they need.", 3),
    F.sec("General Q&A"), F.ck("data.includeQA", "Include the General Q&A discussion", "An optional, ungraded board where students ask questions about the course all term."),
    F.sec("Syllabus Acknowledgement Quiz"), { type:"gsQuizHelp" }, { type:"questions", path:"data.questions" }],''')
sub('    case "slidesActions":', r'''    case "gsHelp": return `<div class="howto">Getting Started is the orientation module students open before Module 1. This document holds the parts only you can write. In Canvas Build it fills the course <b>Welcome</b> page, the <b>Welcome</b> announcement, the <b>Class Introductions</b> discussion and the <b>Syllabus Acknowledgement Quiz</b>. The course introduction video and any learning activities placed in Getting Started are their own documents.</div>`;
    case "gsQuizHelp": { const n = (it.data.questions || []).filter(q => q && String(q.q || "").trim()).length; return `<p class="hint">The template's quiz has 5 questions, 2 attempts and 30 minutes, with the syllabus open. Ask about what students need to act on: due dates, late work, how to reach you, cohort sessions and academic integrity.</p><p class="count ${n && n !== 5 ? "warn" : ""}">${n} of 5 questions written</p>`; }
    case "slidesActions":''')
sub('''  const pick = { assignment:''', '''  const pick = { gettingstarted:[d.welcome, d.instructorIntro, (d.questions || []).length], assignment:''')

# preview
sub('''    case "activity": return brand + ''', r'''    case "gettingstarted": {
      const qs = (d.questions || []).filter(q => q && String(q.q || "").trim());
      const contact = [["Professor", d.profName], ["Email", d.email], ["Phone", d.phone], ["Virtual Office Hours", d.hours], ["Teaching Assistant", d.taName], ["TA Email", d.taEmail], ["TA Virtual Office Hours", d.taHours]].filter(([, v]) => String(v || "").trim());
      return brand + `<h1>Getting Started</h1><h2>Welcome Message</h2>${pvOr(md(d.welcome), "Welcome message")}<h2>About the Instructor</h2>${pvOr(md(d.instructorIntro), "About you")}
        <h2>Contact Information</h2>${contact.length ? contact.map(([k, v]) => `<p><b>${k}:</b> ${esc(v)}</p>`).join("") : `<p class="pv-empty">Contact information</p>`}
        <h2>Course Materials</h2>${linesOf(d.materials).length ? linesOf(d.materials).map(l => `<p>${esc(l)}</p>`).join("") : `<p class="pv-empty">Assigned materials</p>`}
        <h2>Class Introductions</h2>${d.introFirst ? `<p>${esc(GS_FIRST_NOTE)}</p>` : pvOr(md(d.introPrompt), "Introduction prompt")}
        <h2>General Q&amp;A</h2><p>${esc(GS_QA)}: ${d.includeQA === false ? "No" : "Yes"}</p>
        <h2>Syllabus Acknowledgement Quiz</h2>${qs.length ? qs.map((q, n) => `<p><b>Question ${n + 1}:</b> ${esc(q.q)}</p><p>${(q.choices || []).filter(c => String(c).trim()).map((c, k) => `${"ABCDEFGH"[k]}. ${esc(c)}${(q.choices || []).indexOf(c) === Number(q.correct) ? " <b>(correct)</b>" : ""}`).join("<br>")}</p>${q.feedback ? `<p><b>Feedback:</b> ${esc(q.feedback)}</p>` : ""}`).join("") : `<p class="pv-empty">No questions yet.</p>`}`;
    }
    case "activity": return brand + ''')

# Word document, on the reading template's styles
sub('async function buildActivity(it, ctx) {', r'''async function buildGettingStarted(it, ctx) {
  const d = it.data, L = [];
  const h2 = t => L.push({ kind:"p", proto:"H2", text:t });
  const body = t => parseLines(t).forEach(l => L.push(l));
  const row = (k, v) => L.push({ kind:"p", text:`**${k}:** ${String(v || "").replace(/\s*\n\s*/g, " ").trim()}` });
  L.push({ kind:"p", proto:"H1", text:"Getting Started" });
  h2("Welcome Message"); body(d.welcome);
  h2("About the Instructor"); body(d.instructorIntro);
  h2("Contact Information");
  row("Professor", d.profName); row("Email", d.email); row("Phone", d.phone); row("Virtual Office Hours", d.hours);
  row("Teaching Assistant", d.taName); row("TA Email", d.taEmail); row("TA Virtual Office Hours", d.taHours);
  h2("Course Materials"); linesOf(d.materials).forEach(l => L.push({ kind:"p", text:l.trim() }));
  h2("Class Introductions"); if (d.introFirst) L.push({ kind:"p", text:GS_FIRST_NOTE }); else body(d.introPrompt);
  h2("General Q&A"); L.push({ kind:"p", text:`${GS_QA}: ${d.includeQA === false ? "No" : "Yes"}` });
  h2("Syllabus Acknowledgement Quiz");
  (d.questions || []).filter(q => q && String(q.q || "").trim()).forEach((q, k) => {
    L.push({ kind:"p", text:`**Question ${k + 1}:** ${String(q.q).replace(/\s*\n\s*/g, " ").trim()}` });
    (q.choices || []).map((c, j) => [String(c || "").trim(), j === Number(q.correct)]).filter(([c]) => c).forEach(([c, ok], j) => L.push({ kind:"p", text:`${"ABCDEFGH"[j]}. ${c}${ok ? " **(correct)**" : ""}` }));
    if (String(q.feedback || "").trim()) L.push({ kind:"p", text:`**Feedback:** ${String(q.feedback).trim()}` });
  });
  return packDocx("reading", f => f.block("BODY", L, READ_P), "Getting Started", ctx.courseTitle);
}
async function buildActivity(it, ctx) {''')
sub('''    else if (it.kind === "activity") blob = await buildActivity(it, ctx);''', '''    else if (it.kind === "activity") blob = await buildActivity(it, ctx);
    else if (it.kind === "gettingstarted") blob = await buildGettingStarted(it, ctx);''')

# AI drafting
sub('''MODULE ${it.module}: ${mod.title || ""}''', '''${it.module === 0 ? "GETTING STARTED: the orientation module students open before Module 1" : `MODULE ${it.module}: ${mod.title || ""}`}''')
sub('''of ${it.module === 1 ? "an approximately 4 hour target''', '''of ${it.module === 0 ? "no set target, since Getting Started is orientation" : it.module === 1 ? "an approximately 4 hour target''')
sub('''  return { tokens:3000, text:"" };
}''', r'''  if (it.kind === "gettingstarted") { const first = !!d.introFirst;
    return { tokens:4000, text:`Write the faculty-authored parts of the Getting Started module, in the instructor's own voice. Use only facts from the course plan above. For anything personal or any course policy you don't know, write a bracketed placeholder such as [Add your years of industry experience] or [Add the late work policy].
- welcome: 3 to 5 sentences. It follows "Welcome to the course!", so don't open with a greeting. Say what the course offers working professionals and how it runs: ${modCount()} weekly modules, with a live 90-minute cohort session in most modules from Module 2 on.
- instructorIntro: 3 or 4 first-person sentences on the instructor's background, career path and why this course matters to them. Every fact is a placeholder.
${first ? "" : "- introPrompt: a Class Introductions discussion prompt, 1 to 3 lines, asking students to introduce themselves in a way tied to this course's subject, such as their experience with it or a problem they want to solve.\n"}- questions: 5 multiple-choice questions for the Syllabus Acknowledgement Quiz. Students answer with the syllabus open. Ask about what they need to act on: when work is due (Sunday at 11:59 p.m. CT, with discussion initial posts due Wednesday), how to contact the instructor (Canvas Inbox), cohort sessions, academic integrity (the Aggie Honor Code) and course policies. When a correct answer depends on a policy detail the plan doesn't give, put a placeholder in that choice, such as [late work policy from the syllabus]. Each question has 4 choices, one correct, and one sentence of feedback.
JSON shape:
{"welcome": "", "instructorIntro": "", ${first ? "" : `"introPrompt": "", `}"questions": [{"q": "", "choices": ["", "", "", ""], "correct": 0, "feedback": ""}]}` }; }
  return { tokens:3000, text:"" };
}''')
sub('const MERGE_KEYS = { assignment:', 'const MERGE_KEYS = { gettingstarted:["welcome", "instructorIntro", "introPrompt", "questions"], assignment:')

# kind chip colour
sub('</style>', '.kind.k-gettingstarted{background:#e6eef6;color:#003c71}\n</style>')

# an AI draft of a Getting Started activity keeps it in Getting Started
sub('a.module = String(Math.min(Math.max(parseInt(o.module, 10) || modNum(a.module), 1), modCount()));',
    'a.module = isGS(a.module) ? "0" : String(Math.min(Math.max(parseInt(o.module, 10) || modNum(a.module), 1), modCount()));')

# the Getting Started document's editor says so once
sub('<div class="eyebrow">Module ${it.module} · ${esc(kindLabel(it))}</div>', '<div class="eyebrow">${it.kind === "gettingstarted" ? "Getting Started · Orientation module" : `Module ${it.module} · ${esc(kindLabel(it))}`}</div>')

# slide outline help: say how to indent
sub('Lines that start with - become bullets on that slide, and indented bullets become sub-points.',
    'Lines that start with - become bullets on that slide. To make a sub-point, indent the bullet: press the space bar twice before the -.')

# Course folder button: a green dot once a folder is connected and writable, red when it isn't
sub('<button id="btnFolder" hidden title="Choose the course project folder where documents are saved">Course folder</button>',
    '<button id="btnFolder" hidden title="Choose the course project folder where documents are saved"><span class="ai-dot" id="folderDot"></span>Course folder</button>')
sub('async function chooseFolder() {', r'''let FOLDER_DOT_T = 0;
async function updateFolderDot() {
  const dot = $("#folderDot"), btn = $("#btnFolder"); if (!dot || !btn) return;
  const t = ++FOLDER_DOT_T, h = P && P.plan ? await folderHandle(false) : null; if (t !== FOLDER_DOT_T) return;
  dot.classList.toggle("on", !!h);
  btn.title = h ? `Connected: documents save to ${h.name}. Click to choose a different folder.`
    : !FS_OK ? "Not connected: this browser can't save into folders, so documents go to your Downloads folder. Open the tool in Chrome or Edge to connect one."
    : P && P.folderName ? `Not connected: the browser needs permission again, so documents would go to your Downloads folder. Click to reconnect ${P.folderName}.`
    : "Not connected: documents go to your Downloads folder. Click to choose the course project folder.";
}
async function chooseFolder() {''')
sub('  if (S.view === "canvas") { canvasRender(); updateAiDot(); return; }', '  if (S.view === "canvas") { canvasRender(); updateAiDot(); updateFolderDot(); return; }')
sub('  if (v === "item") afterItemRender();\n  updateAiDot();\n}', '  if (v === "item") afterItemRender();\n  updateAiDot(); updateFolderDot();\n}')

# Finish: with a course folder connected the documents are already there, so the zip is only an extra copy
sub('''      <button class="btn ${FS_OK && P.folderName ? "sec" : ""}" data-action="zipAll">Download all saved documents (.zip)</button>''',
    '''      ${FS_OK && P.folderName ? `<span class="sub" style="text-align:right">Your documents are saved in <b>${esc(P.folderName)}</b>.<br><button class="btn link small" data-action="zipAll">Download a copy as a .zip</button></span>` : `<button class="btn" data-action="zipAll" title="Each document is in its course folder, such as 03 - Learning Activities, ready to copy into the course project folder.">Download all saved documents (.zip)</button>`}''')
