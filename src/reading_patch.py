# Interactive readings in Course Development: key terms, a video spot and a knowledge check per section.
# Run by build.py with its sub() helper in scope.

sub('    case "reading": return { overview:"", topics:[], conclusion:"", references:"", aiUsed:false };',
    '    case "reading": return { overview:"", terms:[], topics:[], conclusion:"", references:"", aiUsed:false };')

sub('''  reading: [F.sec("Reading"), F.ta("data.overview", "Overview", "Purpose, context, scope and key terms.", 4),
    { type:"list", path:"data.topics", item:"Topic", add:"Add a topic", fields:[F.tx("heading", "Heading", ""), F.ta("body", "Content", LINES_HINT + " Use ## for a subheading.", 8)] },''',
'''  reading: [F.sec("Reading"), { type:"readingHelp" }, F.ta("data.overview", "Overview", "Purpose, context, scope and key terms.", 4),
    F.sec("Key terms"), { type:"list", path:"data.terms", item:"Term", add:"Add a key term", fields:[F.tx("term", "Term", ""), F.ta("definition", "Definition", "One or two sentences. It appears on the back of a flip card.", 2)] },
    F.sec("Sections"), { type:"list", path:"data.topics", item:"Section", add:"Add a section", fields:[F.tx("heading", "Heading", "Becomes a tab on the Canvas page."), F.ta("body", "Content", LINES_HINT + " Use ## for a subheading.", 8),
      F.tx("video", "Video in this section (optional)", "The video's title. The page gets a placeholder box where it's embedded in Canvas."),
      F.ta("check", "Knowledge check question (optional)", "One multiple-choice question students can try at the end of this section. It isn't graded.", 2),
      F.ta("checkChoices", "Answer choices", "One per line. Put * in front of the correct answer.", 4), F.tx("checkWhy", "Why that answer is correct", "Shown when students select Show answer.")] },
    F.sec("Wrap-up"),''')

sub('    case "slidesActions":',
    '''    case "readingHelp": return `<div class="howto">This reading is saved as a Word document. In Canvas Build it becomes an <b>Interactive Reading</b> page: the overview and key terms open the page, each section becomes a tab with its video spot and knowledge check, and the conclusion closes it out.</div>`;
    case "slidesActions":''')

_plan = '/\\.plan$/.test(a) ? { duration:"", section:"", details:"" }'
sub(_plan, _plan + ' : /terms$/.test(a) ? { term:"", definition:"" } : /data\\.topics$/.test(a) && it.kind === "reading" ? { heading:"", body:"", video:"", check:"", checkChoices:"", checkWhy:"" }')

# Word document carries the new pieces; subheadings inside a section sit one level down
sub('''  let lines = [{ kind:"p", proto:"H1", text:bareTitle(it.title) }, { kind:"p", proto:"H2", text:"Overview" }].concat(parseLines(d.overview));
  (d.topics || []).forEach(t => { if (!t) return; lines.push({ kind:"p", proto:"H2", text:t.heading || "Topic" }); lines = lines.concat(parseLines(t.body)); });''',
'''  const sub3 = ls => ls.map(l => l.kind === "h2" || l.kind === "h3" ? Object.assign({}, l, { proto:"H3" }) : l);
  let lines = [{ kind:"p", proto:"H1", text:bareTitle(it.title) }, { kind:"p", proto:"H2", text:"Overview" }].concat(sub3(parseLines(d.overview)));
  const terms = (d.terms || []).filter(t => t && (String(t.term || "").trim() || String(t.definition || "").trim()));
  if (terms.length) { lines.push({ kind:"p", proto:"H2", text:"Key Terms" }); terms.forEach(t => lines.push({ kind:"bullet", text:`**${String(t.term || "").trim()}:** ${String(t.definition || "").replace(/\\s*\\n\\s*/g, " ").trim()}` })); }
  (d.topics || []).forEach(t => {
    if (!t) return; lines.push({ kind:"p", proto:"H2", text:t.heading || "Topic" }); lines = lines.concat(sub3(parseLines(t.body)));
    if (String(t.video || "").trim()) lines.push({ kind:"p", text:`**Video:** ${String(t.video).trim()}` });
    if (String(t.check || "").trim()) {
      lines.push({ kind:"p", proto:"H3", text:"Knowledge Check" }); lines.push({ kind:"p", text:String(t.check).replace(/\\s*\\n\\s*/g, " ").trim() });
      linesOf(t.checkChoices).forEach((c, k) => { const ok = /^\\*/.test(c); lines.push({ kind:"p", text:`${"ABCDEFGH"[k]}. ${c.replace(/^\\*\\s*/, "")}${ok ? " **(correct)**" : ""}` }); });
      if (String(t.checkWhy || "").trim()) lines.push({ kind:"p", text:`**Answer:** ${String(t.checkWhy).trim()}` });
    }
  });''')

# preview in Course Development
sub('''    case "reading": return brand + `<h1>${t}</h1><h2>Overview</h2>${pvOr(md(d.overview), "Overview")}${(d.topics || []).map(x => `<h2>${esc(x.heading)}</h2>${md(x.body)}`).join("")}''',
'''    case "reading": return brand + `<h1>${t}</h1><h2>Overview</h2>${pvOr(md(d.overview), "Overview")}${(d.terms || []).filter(x => x && x.term).length ? `<h2>Key Terms</h2><ul>${d.terms.filter(x => x && x.term).map(x => `<li><b>${esc(x.term)}:</b> ${esc(x.definition)}</li>`).join("")}</ul>` : ""}${(d.topics || []).map(x => `<h2>${esc(x.heading)}</h2>${md(x.body)}${x.video ? `<p><b>Video:</b> ${esc(x.video)}</p>` : ""}${x.check ? `<div class="pv-box"><b>Knowledge Check</b><p>${esc(x.check)}</p><p>${linesOf(x.checkChoices).map((c, k) => `${"ABCDEFGH"[k]}. ${esc(c.replace(/^\\*\\s*/, ""))}${/^\\*/.test(c) ? " <b>(correct)</b>" : ""}`).join("<br>")}</p>${x.checkWhy ? `<p><b>Answer:</b> ${esc(x.checkWhy)}</p>` : ""}</div>` : ""}`).join("")}''')

# AI drafting fills the new fields
sub('''{"overview": "${LINES_HINT}", "topics": [{"heading": "", "body": "${LINES_HINT} Use ## for a subheading."}], "conclusion": "", "references": "APA, one per line"}` };''',
'''{"overview": "${LINES_HINT}", "terms": [{"term": "", "definition": "one or two sentences"}], "topics": [{"heading": "short heading, it becomes a tab", "body": "${LINES_HINT} Use ## for a subheading.", "video": "title of a short video that would help here, or empty string", "check": "one multiple-choice question on this section", "checkChoices": "4 choices, one per line, with * in front of the correct one", "checkWhy": "one sentence on why it is correct"}], "conclusion": "", "references": "APA, one per line"}
Give 4 to 8 key terms. Never include citation markers such as [cite: 1] or [source].` };''')
sub('reading:["overview", "topics", "conclusion", "references"]', 'reading:["overview", "terms", "topics", "conclusion", "references"]')
sub('if (["rubric", "chunks", "topics", "questions", "plan"].includes(k) && Array.isArray(v)) {', 'if (["rubric", "chunks", "topics", "questions", "plan", "terms"].includes(k) && Array.isArray(v)) {')
sub('      else if (k === "topics" && kind === "reading") v = v.map(x => ({ heading:asText(x.heading), body:asText(x.body) }));',
'''      else if (k === "topics" && kind === "reading") v = v.map(x => ({ heading:asText(x.heading), body:asText(x.body), video:asText(x.video), check:asText(x.check), checkChoices:asText(x.checkChoices), checkWhy:asText(x.checkWhy) }));
      else if (k === "terms") v = v.map(x => ({ term:asText(x.term), definition:asText(x.definition) }));''')
