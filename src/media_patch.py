# Required videos in Course Planning: seeded into each module's Learning Media Plan, then checked.
# Run by build.py with its sub() helper in scope.

sub('function modCount(s = S) { return Math.max(1, parseInt(s.course.moduleCount, 10) || 8); }',
'''function modCount(s = S) { return Math.max(1, parseInt(s.course.moduleCount, 10) || 8); }

/* Flex Online standard: a course introduction video (Module 1), a module overview video in every module,
   and a course conclusion video (last module). Each is written into the Learning Media Plan once;
   after that, deleting one shows up as a gap in the plan checks instead of being re-added. */
const RQM = {
  intro:/welcome|course intro|introduction to the course|course introduction|course overview|meet your instructor/i,
  overview:/\\bmodule\\s*\\d*\\s*overview\\b|^\\s*(recorded video:\\s*)?overview\\b|module introduction|introduction to (the )?module|welcome to module/i,
  conclusion:/conclusion|wrap[- ]?up|closing|farewell|course summary|final thoughts/i
};
const RQM_LINE = { intro:"Recorded Video: Course Introduction", overview:"Recorded Video: Module Overview", conclusion:"Recorded Video: Course Conclusion" };
function mediaHas(text, kind) { return String(text || "").split("\\n").some(l => l.trim() && RQM[kind].test(l) && (kind !== "overview" || !RQM.intro.test(l))); }
function mediaAdd(md, kind) {
  const ls = String(md.media || "").split("\\n").filter(l => l.trim());
  if (kind === "intro") ls.unshift(RQM_LINE.intro);
  else if (kind === "overview") ls.splice(ls.length && RQM.intro.test(ls[0]) ? 1 : 0, 0, RQM_LINE.overview);
  else ls.push(RQM_LINE.conclusion);
  md.media = ls.join("\\n");
}
function seedMedia(s) {
  if (!s || s.phase === "dev" || !Array.isArray(s.modules)) return s;
  const n = modCount(s), r = s.reqMedia = s.reqMedia || { intro:false, ov:[], conclusion:0 };
  if (!r.intro) { if (s.modules[0] && !mediaHas(s.modules[0].media, "intro")) mediaAdd(s.modules[0], "intro"); r.intro = true; }
  for (let i = 0; i < n; i++) if (!r.ov[i]) { if (s.modules[i] && !mediaHas(s.modules[i].media, "overview")) mediaAdd(s.modules[i], "overview"); r.ov[i] = true; }
  if (r.conclusion !== n) {
    const old = r.conclusion - 1;
    if (old >= 0 && old < n - 1 && s.modules[old]) s.modules[old].media = String(s.modules[old].media || "").split("\\n").filter(l => l.trim() !== RQM_LINE.conclusion).join("\\n");
    if (s.modules[n - 1] && !mediaHas(s.modules[n - 1].media, "conclusion")) mediaAdd(s.modules[n - 1], "conclusion");
    r.conclusion = n;
  }
  return s;
}''')

# seed new, opened and resized plans (development-phase plans are left alone)
sub('  resizeModules(out);\n  return out;\n}', '  resizeModules(out); seedMedia(out);\n  return out;\n}')
sub('  first = first || blankState();', '  first = first || seedMedia(blankState());')
sub('S = blankState();', 'S = seedMedia(blankState());', 2)
sub('if (t.id === "modCount") { S.course.moduleCount = t.value; resizeModules(S); save(); rerender(); }',
    'if (t.id === "modCount") { S.course.moduleCount = t.value; resizeModules(S); seedMedia(S); save(); rerender(); }')

# say so on the field
sub('hint:"Media that needs to be created: recorded video, audio, graphics. For example: Recorded Video: Risk Management" })}',
    'hint:`Media that needs to be created: recorded video, audio, graphics. For example: Recorded Video: Risk Management. Required: a module overview video${i === 0 ? " and the course introduction video" : ""}${i === modCount() - 1 ? " and the course conclusion video" : ""}.` })}')

# plan checks flag a missing one, with a one-click fix
sub('  const add = (lvl, text, step) => out.push({ lvl, text, step });', '  const add = (lvl, text, step, fix) => out.push({ lvl, text, step, fix });')
sub('''    if (!doing) add("gap", `${n} has no activity where students practice or apply anything.`, 3);''',
'''    if (!doing) add("gap", `${n} has no activity where students practice or apply anything.`, 3);
    if (i === 0 && !mediaHas(m.media, "intro")) add("gap", "Module 1 needs the course introduction video in its Learning Media Plan.", 3, "intro:0");
    if (!mediaHas(m.media, "overview")) add("gap", `${n} needs a module overview video in its Learning Media Plan.`, 3, `overview:${i}`);
    if (i === modCount() - 1 && !mediaHas(m.media, "conclusion")) add("gap", `${n}, the last module, needs the course conclusion video in its Learning Media Plan.`, 3, `conclusion:${i}`);''')
sub('''<button class="btn link" data-action="go" data-arg="${c.step}">Go to ${STEPS[c.step].title.toLowerCase()}</button></span></li>`;''',
    '''${c.fix ? `<button class="btn link" data-action="addReqMedia" data-arg="${c.fix}">Add it</button> ` : ""}<button class="btn link" data-action="go" data-arg="${c.step}">Go to ${STEPS[c.step].title.toLowerCase()}</button></span></li>`;''')
sub('''  const actions = {
    startDev: () => DEV.startDialog(),''', '''  const actions = {
    addReqMedia: () => { const [kind, i] = String(arg).split(":"); if (S.modules[+i]) { mediaAdd(S.modules[+i], kind); save(); rerender(); toast("Added to the Learning Media Plan"); } },
    startDev: () => DEV.startDialog(),''')
