/* ============================================================
   CANVAS BUILD
   The third phase. Each page is built in Canvas one at a time: the tool
   writes the page HTML in the DesignPLUS template format, lists the settings
   Canvas keeps outside the page, and lays out the rubric and quiz questions.
   Content comes from the saved Word documents, so edits faculty made in Word
   after saving are picked up.
   ============================================================ */
const CV_SNIP = /*__CV_SNIPS__*/{};
const CV_BANNER_URL = "https://files.ciditools.com/tamu/ModuleBannerTemplate_Meeting.jpg";
const CV_FOOTER_URL = "https://s3.us-east-1.amazonaws.com/prod.files.ciditools.com/tamu/Banners_Footer/Banners_Footer/Footer.png";
const CV_GUIDE = {
  assignment:"https://community.instructure.com/en/kb/articles/661207-how-do-i-view-assignments-as-a-student",
  discussion:"https://community.instructure.com/en/kb/articles/661284-how-do-i-view-discussions-as-a-student"
};
const CV_HELP = {
  "Perusall":"https://www.youtube.com/watch?v=-ysn9nEZyKs",
  "Peerceptiv":"https://peerceptiv.zendesk.com/hc/en-us/categories/6265536320659-Students",
  "Cengage":"https://help.cengage.com/student/index.html",
  "Harvard Business Publishing":"https://hbsp.harvard.edu/contact-us/",
  "McGraw Hill Connect":"https://www.mheducation.com/highered/support/support-at-every-step/student/connect",
  "MyBusiness Course":"https://mybusinesscourse.com/user_guide/161737/home",
  "MyEducator":"https://www.myeducator.com/student-contact/",
  "Packback":"https://help.packback.co/hc/en-us/categories/203990168-Student-Support",
  "Pearson":"https://support.pearson.com/getsupport/s/contactsupport"
};
const CV_NUM = { 1:"one", 2:"two", 3:"three", 4:"four", 5:"five", 6:"six", 7:"seven", 8:"eight", 9:"nine", 10:"ten", 11:"eleven", 12:"twelve", 13:"thirteen", 14:"fourteen", 15:"fifteen", 16:"sixteen" };

/* ---------- DesignPLUS pieces, copied from the Mays Canvas template course ---------- */
const cvIcon = cls => `<i class="dp-icon ${cls}" aria-hidden="true"><span class="dp-icon-content" style="display: none;">&nbsp;</span></i>`;
const CV_HR = `<hr class="dp-hr-solid-light dp-border-dir-tblr dp-border-style-solid cp-out-dp-primary dp-margin-direction-tblr" style="border-top-width: 3px; margin-top: 8px; margin-bottom: 20px;">`;
function cvOpen(title) {
  return `${CV_SNIP.wrap}<header class="${CV_SNIP.hdr}">\n<h2 class="${CV_SNIP.h2[0]}"><span class="${CV_SNIP.h2[1]}">${esc(title)}</span></h2>\n</header>\n`
    + `<div class="dp-banner-image"><img role="presentation" src="${CV_BANNER_URL}" alt="" loading="lazy"></div>\n${CV_HR}\n`;
}
const CV_NEXT = `<p style="text-align: right;">&nbsp;</p>\n<p style="text-align: right;"><strong><em>Click Next (below) to progress through the course.</em></strong></p>\n`;
const cvFooter = () => `<p><img style="width: 100%; min-width: 100%; height: auto; border-radius: 4px;" role="presentation" src="${CV_FOOTER_URL}" alt="" loading="lazy"></p>\n</div>`;
const cvClose = () => CV_NEXT + cvFooter();
function cvStatus(text) {
  return `<div class="dp-card card cp-bg-dp-secondary mx-auto d-block dp-border-dir-tblr dp-border-style-solid text-start dp-shadow-b3" style="border-color: #003c71; border-left-width: 9px; font-size: 16px; background-color: #f7f7f7; color: #000000; border-right-width: 9px;">\n<div class="card-body dp-border-dir-tblr dp-margin-direction-tblr dp-padding-direction-tblr dp-border-style-none" style="padding: 8px; border-right-width: 0px; background-color: #f7f7f7; color: #000000;">\n<p class="card-text" style="text-align: center;"><em><strong>${cvIcon("fas fa-info-circle")} &nbsp;${text}</strong></em></p>\n</div>\n</div>\n`;
}
const cvH3 = (icon, label) => `<h3 class="paragraph ng-attr-widget dp-has-icon">${cvIcon(icon)} <strong>${label}</strong></h3>\n`;
function cvCard(inner, label, icon) {
  return `<div class="dp-card card cp-bg-dp-gray dp-border-dir-tblr dp-border-style-solid" style="border-color: #003c71; background-color: #f7f7f7; color: #000000; border-left-width: 6px; border-right-width: 6px;">\n<div class="card-body" style="background-color: #f7f7f7; color: #000000;">\n`
    + (label ? `<h4 class="dp-has-icon"><i class="dp-icon ${icon || "far fa-clipboard"}"><span class="dp-icon-content" style="display: none;">&nbsp;</span></i> <span style="font-size: 18pt; color: #003c71;"><strong>${label}</strong></span></h4>\n` : "")
    + inner + `</div>\n</div>\n`;
}
const cvSubLabel = (icon, label) => `<p>${cvIcon(icon + " cp-txt-dp-primary")} <span style="color: #500000;"><strong>${label}</strong></span></p>\n`;
const cvButton = (href, label) => `<p><a class="external dp-external-link inline_disabled" style="display: inline-block; background-color: #500000; color: #ffffff; padding: 12px 25px; border-radius: 6px; text-decoration: none; font-size: 15px;" href="${esc(href)}" target="_blank"><i class="fas fa-external-link-alt" style="margin-right: 8px;"><span class="dp-icon-content" style="display: none;">&nbsp;</span></i> ${esc(label)}</a></p>\n`;

/* where a video goes: the template's placeholder box; the video itself is embedded in Canvas */
const cvVideoBox = label => `<div class="dp-border-style-solid dp-border-dir-tblr" style="background-color: #f5f5f5; border-radius: 8px; padding: 30px 10px; margin-bottom: 20px; text-align: center; border: 3px dashed #500000;">\n<p style="font-size: 16px; color: #666; margin: 0;"><strong>[Video Placeholder: ${esc(label)}]</strong><br>Embed the video here in Canvas.</p>\n</div>\n`;

/* faculty text (one line per paragraph, - bullets, 1. numbers, **bold**) to Canvas HTML */
function cvInline(t) {
  return esc(t).replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/(https?:\/\/[^\s<]+[^\s<.,;:)])/g, u => `<a class="inline_disabled" href="${u}" target="_blank">${u}</a>`);
}
function cvBlocks(text, pAttr) {
  const ls = parseLines(text); let h = "", list = null;
  for (const l of ls) {
    const want = l.kind === "bullet" ? "ul" : l.kind === "number" ? "ol" : null;
    if (list && want !== list) { h += `</${list}>\n`; list = null; }
    if (want && !list) { h += `<${want}>\n`; list = want; }
    if (want) h += `<li>${cvInline(l.text)}</li>\n`;
    else if (l.kind === "h2" || l.kind === "h3") h += `<p><strong>${cvInline(l.text)}</strong></p>\n`;
    else h += `<p${pAttr ? " " + pAttr : ""}>${cvInline(l.text)}</p>\n`;
  }
  return h + (list ? `</${list}>\n` : "");
}
const cvLines = t => linesOf(t).map(x => x.replace(/^\s*[-*•]\s+/, ""));

/* ---------- What goes into Canvas, in Canvas module order ---------- */
const cvScannable = it => cvBuildable(it) || it.kind === "reading" || it.kind === "gettingstarted";
function cvBuildable(it) { return it.kind === "activity" ? !!it.data.graded : ["assignment", "discussion", "quiz", "thirdparty"].includes(it.kind); }
const CV_ORDER = { discussion:0, assignment:1, activity:2, thirdparty:3, quiz:4 };
function cvActivities(m) { return live().filter(i => i.module === m && cvBuildable(i)).sort((a, b) => CV_ORDER[a.kind] - CV_ORDER[b.kind]); }
const cvGsItem = () => live().find(i => i.kind === "gettingstarted");
/* The Getting Started document's content, with the professor's name from Setup when it was left blank */
function cvGsData() {
  const it = cvGsItem(), d = it ? cvData(it) : gsDefaults(P);
  return Object.assign({}, d, { profName:String(d.profName || "").trim() || P.setup.instructor || "" });
}
const CV_GS_ACT = { gsintro:1, gsquiz:1, item:1 };
function cvEntries() {
  const gs = cvGsItem(), g = cvGsData();
  const out = [{ key:"welcome", type:"welcome", m:0, it:gs, title:`Welcome to ${courseTitle() || "the Course"}` }, { key:"gs:announce", type:"announce", m:0, it:gs, title:"Welcome!" }];
  if (g.includeQA !== false) out.push({ key:"gs:qa", type:"gsqa", m:0, it:gs, title:"GS: General Q&A" });
  out.push({ key:"gs:intro", type:"gsintro", m:0, it:gs, title:"GS: Discussion | Class Introductions" }, { key:"gs:quiz", type:"gsquiz", m:0, it:gs, title:"GS: Quiz | Syllabus Acknowledgement Quiz" });
  cvActivities(0).forEach(it => out.push({ key:it.id, type:"item", m:0, it, title:cvTitle(it) }));
  for (let m = 1; m <= modCount(); m++) {
    out.push({ key:`lm:${m}`, type:"materials", m, title:`M${m}: Learning Materials` });
    live().filter(i => i.module === m && i.kind === "reading").forEach(it => out.push({ key:it.id, type:"reading", m, it, title:`M${m}: Interactive Reading | ${bareTitle(it.title)}` }));
    cvActivities(m).forEach(it => out.push({ key:it.id, type:"item", m, it, title:cvTitle(it) }));
    out.push({ key:`sum:${m}`, type:"summary", m, title:`M${m}: Module Summary` });
  }
  return out;
}
function cvTitle(it) {
  if (it.kind === "gettingstarted") return "Getting Started document";
  const m = `M${it.module}`, t = bareTitle(it.title);
  if (it.kind === "assignment") return `${m}: Assignment | ${t}`;
  if (it.kind === "discussion") return `${m}: Discussion | ${t}`;
  if (it.kind === "quiz") return `${m}: Quiz | ${t}`;
  if (it.kind === "thirdparty") return `${m}: ${it.data.tool || "Third-Party Tool"} Assignment | ${t}`;
  if (it.kind === "reading") return `${m}: Interactive Reading | ${t}`;
  return `${m}: Cohort Session Assignment | ${t}`;
}
const cvKindName = e => e.type === "announce" ? "Announcement" : e.type === "gsqa" || e.type === "gsintro" ? "Discussion" : e.type === "gsquiz" ? "Quiz" : e.type === "materials" || e.type === "reading" ? "Page" : e.type === "summary" ? "Page" : e.it.kind === "quiz" ? "Quiz" : e.it.kind === "discussion" ? "Discussion" : "Assignment";
function cvState() {
  if (!P.canvas) P.canvas = { screen:"setup", sel:null, cohortDay:"", cohortTime:"", status:{}, ticks:{}, links:{}, pages:{} };
  return P.canvas;
}
const cvStat = key => cvState().status[key] || "todo";
const CV_STATUS = { todo:"Not started", pasted:"Pasted", done:"Built" };

/* ============================================================
   Reading the saved Word documents
   ============================================================ */
const WNS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main", W14NS = "http://schemas.microsoft.com/office/word/2010/wordml";
const wkids = (el, name) => [...el.childNodes].filter(n => n.nodeType === 1 && n.namespaceURI === WNS && (!name || n.localName === name));
const wattr = (el, a) => el ? (el.getAttributeNS(WNS, a) || el.getAttribute("w:" + a)) : null;
function wPara(p) {
  const pPr = wkids(p, "pPr")[0], st = pPr && wkids(pPr, "pStyle")[0], style = st ? wattr(st, "val") || "" : "";
  const list = !!(pPr && wkids(pPr, "numPr").length) || /^List/.test(style);
  const segs = [];
  for (const r of p.getElementsByTagNameNS(WNS, "r")) {
    const rPr = wkids(r, "rPr")[0], b = rPr && wkids(rPr, "b")[0];
    const bold = !!b && !/^(0|false)$/.test(wattr(b, "val") || "");
    let t = "";
    for (const n of r.childNodes) { if (n.namespaceURI !== WNS) continue; if (n.localName === "t") t += n.textContent; else if (n.localName === "tab" || n.localName === "br") t += " "; }
    if (!t) continue;
    if (segs.length && segs[segs.length - 1].bold === bold) segs[segs.length - 1].t += t; else segs.push({ t, bold });
  }
  const text = segs.map(s => s.t).join("").replace(/ /g, " ").replace(/[​]/g, "").replace(/\s+/g, " ").trim();
  const md = segs.map(s => { const v = s.t.replace(/ /g, " ").replace(/​/g, ""); return s.bold && v.trim() ? v.replace(/^(\s*)(.*?)(\s*)$/, "$1**$2**$3") : v; }).join("").replace(/\s+/g, " ").trim();
  return { t:"p", style, list, text, md };
}
function wBlocks(parent, out = []) {
  for (const el of wkids(parent)) {
    if (el.localName === "p") out.push(wPara(el));
    else if (el.localName === "tbl") out.push({ t:"tbl", rows:wkids(el, "tr").map(tr => wkids(tr, "tc").map(tc => wBlocks(tc).filter(b => b.t === "p"))) });
    else if (el.localName === "sdt") { const c = wkids(el, "sdtContent")[0]; if (c) wBlocks(c, out); }
  }
  return out;
}
const tblText = b => b.rows.map(r => r.map(c => c.map(p => p.text).join(" ")).join(" | ")).join("\n");
function wChecks(doc) {
  const out = {};
  for (const sdt of doc.getElementsByTagNameNS(WNS, "sdt")) {
    const pr = wkids(sdt, "sdtPr")[0]; if (!pr) continue;
    const tag = wkids(pr, "tag")[0], v = tag && wattr(tag, "val"); if (!v || !v.startsWith("cb:")) continue;
    const ch = pr.getElementsByTagNameNS(W14NS, "checked")[0];
    let on = ch ? /^(1|true)$/.test(ch.getAttributeNS(W14NS, "val") || ch.getAttribute("w14:val") || "") : null;
    if (on === null) on = /☒/.test(sdt.textContent);
    out[v.slice(3)] = on;
  }
  return out;
}
/* paragraphs from just after the one matching `from` up to the first stop */
function between(B, from, stop) {
  const i = B.findIndex(from); if (i < 0) return null;
  const out = [];
  for (let k = i + 1; k < B.length; k++) { const b = B[k]; if (stop(b)) break; if (b.t === "p" && b.text) out.push(b); }
  return out;
}
const isHead = txt => b => b.t === "p" && norm(b.text) === norm(txt);
const isHeading = b => b.t === "p" && /^Heading[12]$/.test(b.style);
const toMd = ps => ps.map(p => (p.list ? "- " : "") + p.md).join("\n");
function wRubric(B) {
  const t = B.find(b => b.t === "tbl" && b.rows[0] && /^Criteria/.test((b.rows[0][0] || []).map(p => p.text).join(" ")));
  if (!t) return null;
  const rows = [];
  for (const r of t.rows.slice(1)) {
    const first = (r[0] || []).map(p => p.text).join(" ").trim();
    if (/^TOTAL/i.test(first)) break;
    if (!r.some(c => c.some(p => p.text))) continue;
    const c0 = r[0] || [], ptsP = c0.find(p => /^[\d.]+\s*points?$/i.test(p.text));
    const crit = c0.filter(p => p !== ptsP).map(p => p.text).join(" ").replace(/\*\*/g, "").trim();
    const cell = k => (r[k] || []).map(p => p.text).join("\n").trim();
    rows.push({ criterion:crit, points:ptsP ? ptsP.text.match(/[\d.]+/)[0] : "", excellent:cell(1), sufficient:cell(2), minimal:cell(3), unacceptable:cell(4) });
  }
  return rows;
}
function settingsFromChecks(c, base) {
  const s = clone(base || {});
  if (!Object.keys(c).some(k => k.startsWith("submission_type."))) return s;
  const sub = [];
  ["file_uploads", "text_entry", "website_url", "media_recordings", "student_annotation"].forEach(k => { if (c["submission_type." + k]) sub.push(k); });
  if (c["submission_type.external_tool"]) sub.push("external");
  if (c["submission_type.on_paper"]) sub.push("paper");
  if (c["submission_type.no_submission"]) sub.push("none");
  if (sub.length) s.submission = sub;
  s.attempts = c["submission_attempts.unlimited"] ? "unlimited" : "limited";
  s.plagiarism = c["plagiarism_review.turnitin"] ? "turnitin" : "none";
  s.group = !!c["group_assignment.this_is_a_group_assignment"];
  s.groupIndividual = !!c["group_assignment.assign_grades_to_each_student_individually"];
  s.peer = !!c["peer_review.require_peer_reviews"];
  if (s.peer) { s.peerHow = c["peer_review.manually_assign_peer_reviews"] ? "manual" : "auto"; s.peerAnon = !!c["peer_review.peer_reviews_appear_anonymously"]; }
  return s;
}
const settingsRow = (B, label) => { for (const b of B) if (b.t === "tbl") for (const r of b.rows) if (norm((r[0] || []).map(p => p.text).join(" ")) === norm(label)) return r; return null; };
const cellText = c => (c || []).map(p => p.text).join(" ").trim();

/* Read a saved document back into the same shape Course Development uses */
async function parseSavedDoc(it, buf) {
  const entries = readZip(new Uint8Array(buf)), e = entries.find(x => x.name === "word/document.xml");
  if (!e) throw new Error("not a Word document");
  const doc = new DOMParser().parseFromString(await unzipText(e), "application/xml");
  const body = doc.getElementsByTagNameNS(WNS, "body")[0]; if (!body) throw new Error("no document body");
  const B = wBlocks(body), checks = wChecks(doc), out = {};
  const h1 = B.find(b => b.t === "p" && b.style === "Heading1");
  if (h1) out.title = h1.text.replace(/^[^|]*\|\s*/, "").trim();
  const kind = it.kind === "activity" ? "assignment" : it.kind;
  if (kind === "reading") return Object.assign(out, parseReading(B));
  if (kind === "gettingstarted") return Object.assign(out, parseGettingStarted(B));
  const status = B.find(b => b.t === "tbl" && /This is an? /.test(tblText(b)));
  if (kind === "assignment" || kind === "thirdparty") {
    const stopOv = b => b.t === "tbl" || isHeading(b);
    const ov = between(B, isHead("Overview"), stopOv); if (ov) out.overview = toMd(ov);
    if (kind === "assignment") {
      const note = B.find(b => b.t === "tbl" && /^Note:?/.test(cellText(b.rows[0] && b.rows[0][0])));
      if (note) out.note = toMd(note.rows[0][0].filter(p => p.text)).replace(/^\*{0,2}Note:?\*{0,2}\s*/, "").trim();
      else out.note = "";
      const g = between(B, isHead("Guidelines"), b => isHead("Format:")(b) || isHead("Submission")(b) || isHeading(b)); if (g) out.instructions = toMd(g);
      const f = between(B, isHead("Format:"), b => isHead("Submission")(b) || (isHeading(b) && !/^Heading3$/.test(b.style))); if (f) out.format = f.map(p => p.text).join("\n");
      const s = B.find(b => b.t === "p" && /^Click on [“"]Start Assignment[”"] to upload a document\./.test(b.text));
      if (s) out.submission = s.text.replace(/^Click on [“"]Start Assignment[”"] to upload a document\.\s*/, "").trim();
    } else {
      const tm = h1 && h1.text.match(/^M\d+:\s*(.+?)\s+Assignment\s*\|/); if (tm) out.tool = TOOLS.find(t => norm(t) === norm(tm[1])) || tm[1];
      const g = between(B, isHead("Guidelines"), b => isHead("Submission")(b) || isHeading(b)); if (g) out.instructions = toMd(g);
      const s = B.find(b => b.t === "p" && /button below to begin\./.test(b.text));
      if (s) out.submission = s.text.replace(/^.*?button below to begin\.\s*/, "").trim();
      // the template's standard wording means the field was left blank in Course Development
      const tool = out.tool || it.data.tool || "Third-Party Tool";
      if (out.overview != null && cvNormText(out.overview) === cvNormText(`This assignment uses ${tool}, an interactive learning platform. Select the button at the bottom of this page to enter the ${tool} portal. In the ${tool} assignment, you will read the instructions and complete the assignment.`)) out.overview = "";
      if (out.instructions != null && cvNormText(out.instructions).startsWith(cvNormText(`${tool} assignments are graded automatically within the tool site.`))) out.instructions = "";
    }
    const r = wRubric(B); if (r) out.rubric = r;
    const set = settingsFromChecks(checks, it.data.settings);
    const att = settingsRow(B, "Submission Attempts"), an = att && cellText(att[1]).match(/(\d+)\s*$|Allowed Attempts:?\s*(\d+)/i);
    if (an && set.attempts !== "unlimited") set.attemptsNum = an[1] || an[2];
    if (status) set.group = /group/i.test(tblText(status)) || set.group;
    out.settings = set;
  } else if (kind === "discussion") {
    const ov = between(B, isHead("Overview"), b => b.t === "tbl" || isHeading(b)); if (ov) out.overview = toMd(ov);
    const pr = B.find(b => b.t === "tbl" && /^Prompt/.test(cellText(b.rows[0] && b.rows[0][0])));
    if (pr) out.prompt = toMd(pr.rows[0][0].filter(p => p.text && !/^\*{0,2}Prompt\*{0,2}$/.test(p.md))).trim();
    const rp = B.find(b => b.t === "p" && /Reply to at least (\S+) classmates/.test(b.text)); if (rp) out.replies = rp.text.match(/Reply to at least (\S+) classmates/)[1];
    if (status) out.graded = !/non-graded/i.test(tblText(status));
    const pts = B.filter(b => b.t === "tbl").map(tblText).join("\n").match(/Possible Points:\s*([\d.]+)/); if (pts) out.points = pts[1];
    const r = wRubric(B); if (r) out.rubric = r;
    if (Object.keys(checks).some(k => k.startsWith("options."))) {
      const s = clone(it.data.settings || {});
      s.anonymous = checks["options.full_student_names_and_profile_pictures_will_be_"] ? "full" : checks["options.partial_students_can_choose_to_reveal_their_name"] ? "partial" : "off";
      s.mustPost = !!checks["options.participants_must_respond_to_the_topic_before_vi"]; s.noThreads = !!checks["options.disallow_threaded_replies"]; s.liking = !!checks["options.allow_liking"];
      s.group = !!checks["group_discussion.this_is_a_group_discussion"]; s.peer = checks["peer_review.assign_manually"] ? "manual" : checks["peer_review.automatically_assign"] ? "auto" : "";
      out.settings = s;
    }
  } else if (kind === "quiz") {
    const g = B.find(b => b.t === "p" && /paying particular attention to/.test(b.text));
    if (g) out.focus = g.text.replace(/^.*paying particular attention to\s*/, "").replace(/\.\s*$/, "").trim();
    const all = B.filter(b => b.t === "tbl").map(tblText).join("\n");
    if (/closed-book/i.test(all)) out.openBook = false; else if (/open-book/i.test(all)) out.openBook = true;
    const am = all.match(/You will have (\S+) attempts?/i);
    if (am) { const w = am[1].toLowerCase(), n = Object.entries(CV_NUM).find(([, v]) => v === w); out.attempts = w === "unlimited" ? "unlimited" : n ? n[0] : /^\d+$/.test(w) ? w : out.attempts; }
    const km = all.match(/with your (highest|latest|average) score/i); if (km) out.keep = km[1].toLowerCase();
    const mm = all.match(/allotted (\d+) minutes/i); out.minutes = mm ? mm[1] : (/no time limit/i.test(all) ? "" : it.data.minutes);
    if (/After your last attempt/i.test(all)) out.showAnswers = "last"; else if (/After you have submitted your attempt/i.test(all)) out.showAnswers = "each"; else if (/will not be shown/i.test(all)) out.showAnswers = "never";
    const qs = between(B, b => b.t === "p" && /^Questions$/.test(b.text), isHead("Canvas Settings"));
    if (qs) {
      const list = []; let cur = null;
      for (const p of qs) {
        let m;
        if ((m = p.text.match(/^(\d+)\.\s+(.*)$/)) && (p.md.startsWith("**") || !cur || cur.choices.length)) { cur = { q:m[2].trim(), choices:[], correct:0, feedback:"" }; list.push(cur); }
        else if (cur && (m = p.text.match(/^([a-h])[.)]\s+(.*)$/i))) { let c = m[2]; if (/\(Correct\)\s*$/i.test(c)) { c = c.replace(/\s*\(Correct\)\s*$/i, ""); cur.correct = cur.choices.length; } cur.choices.push(c.trim()); }
        else if (cur && (m = p.text.match(/^Feedback:\s*(.*)$/i))) cur.feedback = m[1].trim();
        else if (cur && !cur.choices.length) cur.q += " " + p.text;
      }
      out.questions = list;
    }
    const ppq = settingsRow(B, "Points per question"); if (ppq) out.ppq = cellText(ppq[1]);
    const ag = settingsRow(B, "Assignment Group"); if (ag && cellText(ag[1])) out.agroup = cellText(ag[1]);
    const sh = settingsRow(B, "Shuffle Answers"); if (sh) out.shuffle = !/^no/i.test(cellText(sh[1]));
    if ("quiz_type.practice_quiz" in checks) out.quizType = checks["quiz_type.practice_quiz"] ? "practice" : "graded";
    if ("question_display.show_one_question_at_a_time" in checks) out.oneAtATime = !!checks["question_display.show_one_question_at_a_time"];
  }
  return out;
}

/* Instructor reading: Heading 2 sections; a section's Heading 3 "Knowledge Check" holds its question */
function parseReading(B) {
  const out = { overview:"", terms:[], topics:[], conclusion:"", references:"", aiUsed:false };
  let sec = null, buf = [];
  const flush = () => {
    if (!sec) return;
    const ps = buf.filter(b => b.t === "p" && b.text);
    if (sec === "Overview") out.overview = toMd(ps.map(p => /^Heading3$/.test(p.style) ? Object.assign({}, p, { md:"## " + p.text, list:false }) : p));
    else if (sec === "Key Terms") out.terms = ps.map(p => { const m = p.md.match(/^\*\*(.+?):?\*\*:?\s*(.*)$/) || p.text.match(/^([^:]{1,80}):\s*(.*)$/); return m ? { term:m[1].replace(/:$/, "").trim(), definition:m[2].trim() } : { term:p.text, definition:"" }; });
    else if (sec === "Conclusion") out.conclusion = toMd(ps);
    else if (sec === "References") out.references = ps.map(p => p.text).join("\n");
    else if (sec === "Use of AI") out.aiUsed = true;
    else {
      const t = { heading:sec, body:"", video:"", check:"", checkChoices:"", checkWhy:"" }, body = [];
      let inCheck = false;
      for (const p of ps) {
        let m;
        if (/^Heading3$/.test(p.style) && /^knowledge check$/i.test(p.text)) { inCheck = true; continue; }
        if (inCheck) {
          if ((m = p.text.match(/^([A-H])[.)]\s+(.*)$/))) { const ok = /\(correct\)\s*$/i.test(m[2]); t.checkChoices += (t.checkChoices ? "\n" : "") + (ok ? "* " : "") + m[2].replace(/\s*\(correct\)\s*$/i, "").trim(); }
          else if ((m = p.text.match(/^Answer:\s*(.*)$/i))) t.checkWhy = m[1].trim();
          else if (/^Heading3$/.test(p.style)) { inCheck = false; body.push(Object.assign({}, p, { md:"## " + p.text, list:false })); }
          else if (!t.checkChoices) t.check = (t.check ? t.check + " " : "") + p.text;
          else body.push(p);
          continue;
        }
        if ((m = p.text.match(/^Video:\s*(.*)$/i)) && /^\*\*Video:?\*\*/.test(p.md)) { t.video = m[1].trim(); continue; }
        body.push(/^Heading3$/.test(p.style) ? Object.assign({}, p, { md:"## " + p.text, list:false }) : p);
      }
      t.body = toMd(body); out.topics.push(t);
    }
  };
  for (const b of B) {
    if (b.t === "p" && b.style === "Heading1") continue;
    if (b.t === "p" && b.style === "Heading2") { flush(); sec = b.text; buf = []; continue; }
    if (sec) buf.push(b);
  }
  flush();
  return out;
}

/* Getting Started: Heading 2 sections in a fixed order */
function parseGettingStarted(B) {
  const out = {}, CONTACT = { "professor":"profName", "email":"email", "phone":"phone", "virtual office hours":"hours", "teaching assistant":"taName", "ta email":"taEmail", "ta virtual office hours":"taHours" };
  let sec = null, buf = [];
  const flush = () => {
    if (!sec) return;
    const ps = buf.filter(b => b.t === "p" && b.text), s = sec.trim().toLowerCase(), all = ps.map(p => p.text).join(" ");
    if (s === "welcome message") out.welcome = toMd(ps);
    else if (s === "about the instructor") out.instructorIntro = toMd(ps);
    else if (s === "contact information") { Object.values(CONTACT).forEach(k => out[k] = ""); ps.forEach(p => { const m = p.text.match(/^([^:]{2,40}):\s*(.*)$/), k = m && CONTACT[m[1].trim().toLowerCase()]; if (k) out[k] = m[2].trim(); }); }
    else if (s === "course materials") out.materials = ps.map(p => p.text.trim()).join("\n");
    else if (s === "class introductions") { if (/standard introduction prompt/i.test(all)) out.introFirst = true; else { out.introFirst = false; out.introPrompt = toMd(ps); } }
    else if (s === "general q&a") out.includeQA = !/:\s*no\b/i.test(all);
    else if (/syllabus/.test(s)) {
      const list = []; let cur = null;
      for (const p of ps) {
        let m;
        if ((m = p.text.match(/^Question\s+\d+\s*[:.]\s*(.*)$/i))) { cur = { q:m[1].trim(), choices:[], correct:0, feedback:"" }; list.push(cur); }
        else if (cur && (m = p.text.match(/^([A-Ha-h])[.)]\s+(.*)$/))) { let c = m[2]; if (/\(correct\)\s*$/i.test(c)) { c = c.replace(/\s*\(correct\)\s*$/i, ""); cur.correct = cur.choices.length; } cur.choices.push(c.trim()); }
        else if (cur && (m = p.text.match(/^Feedback:\s*(.*)$/i))) cur.feedback = m[1].trim();
        else if (cur && !cur.choices.length) cur.q += " " + p.text;
      }
      out.questions = list;
    }
  };
  for (const b of B) {
    if (b.t === "p" && b.style === "Heading1") continue;
    if (b.t === "p" && b.style === "Heading2") { flush(); sec = b.text; buf = []; continue; }
    if (sec) buf.push(b);
  }
  flush();
  return out;
}

/* Which fields differ between the Word document and Course Development's saved work */
const CV_FIELDS = {
  assignment:[["overview", "Overview"], ["note", "Note"], ["instructions", "Guidelines"], ["format", "Format"], ["submission", "Submission details"], ["rubric", "Rubric"], ["settings", "Canvas settings"]],
  thirdparty:[["tool", "Tool"], ["overview", "Overview"], ["instructions", "Guidelines"], ["submission", "Submission details"], ["rubric", "Rubric"], ["settings", "Canvas settings"]],
  discussion:[["overview", "Overview"], ["prompt", "Prompt"], ["replies", "Replies required"], ["graded", "Graded"], ["points", "Points"], ["rubric", "Rubric"], ["settings", "Canvas settings"]],
  gettingstarted:[["welcome", "Welcome message"], ["instructorIntro", "About the instructor"], ["profName", "Professor"], ["email", "Email"], ["phone", "Phone"], ["hours", "Office hours"], ["taName", "Teaching assistant"], ["taEmail", "TA email"], ["taHours", "TA office hours"], ["materials", "Assigned materials"], ["introFirst", "Class Introductions version"], ["introPrompt", "Introduction prompt"], ["includeQA", "General Q&A"], ["questions", "Syllabus quiz questions"]],
  reading:[["overview", "Overview"], ["terms", "Key terms"], ["topics", "Sections"], ["conclusion", "Conclusion"], ["references", "References"], ["aiUsed", "Use of AI statement"]],
  quiz:[["focus", "What to study"], ["openBook", "Open-book"], ["questions", "Questions"], ["attempts", "Attempts"], ["keep", "Score kept"], ["minutes", "Time limit"], ["showAnswers", "Show answers"], ["ppq", "Points per question"], ["agroup", "Assignment group"], ["shuffle", "Shuffle"], ["quizType", "Quiz type"]]
};
const cvNormText = s => String(s ?? "").replace(/\*\*/g, "").replace(/^\s*([-*•]|\d+[.)])\s+/gm, "").replace(/[“”]/g, '"').replace(/[‘’]/g, "'").replace(/\s+/g, " ").trim().toLowerCase();
function cvNorm(k, v, it) {
  if (k === "terms") return JSON.stringify((v || []).filter(t => t && (String(t.term || "").trim() || String(t.definition || "").trim())).map(t => [cvNormText(t.term), cvNormText(t.definition)]));
  if (k === "topics") return JSON.stringify((v || []).filter(Boolean).map(t => [cvNormText(t.heading), cvNormText(t.body), cvNormText(t.video), cvNormText(t.check), linesOf(t.checkChoices).map(c => (/^\*/.test(c) ? "*" : "") + cvNormText(c.replace(/^\*\s*/, ""))), cvNormText(t.checkWhy)]));
  if (k === "aiUsed") return String(!!v);
  if (k === "rubric") return JSON.stringify((v || []).filter(r => r && (r.criterion || r.excellent)).map(r => ["criterion", "points", "excellent", "sufficient", "minimal", "unacceptable"].map(f => cvNormText(r[f]))));
  if (k === "questions") return JSON.stringify((v || []).filter(q => q && String(q.q || "").trim()).map(q => { const cs = (q.choices || []).map((c, j) => [cvNormText(c), j === (Number(q.correct) || 0)]).filter(([c]) => c); return [cvNormText(q.q), cs.map(c => c[0]), cs.findIndex(c => c[1]), cvNormText(q.feedback)]; }));
  if (k === "introFirst") return String(!!v);
  if (k === "includeQA") return String(v !== false);
  if (k === "settings") { const s = v || {}; return JSON.stringify([(s.submission || []).slice().sort(), s.attempts || "limited", s.attempts === "unlimited" ? "" : String(s.attemptsNum || "2"), s.plagiarism || "none", !!s.group, !!s.peer, s.anonymous || "", s.mustPost !== false]); }
  if (k === "graded" || k === "openBook" || k === "shuffle" || k === "oneAtATime") return String(v !== false);
  if (k === "minutes" || k === "ppq") return String(v || "").trim();
  if (k === "focus") return cvNormText(v || "the assigned module materials");
  return cvNormText(v);
}
function cvDiff(it, parsed) {
  const kind = it.kind === "activity" ? "assignment" : it.kind;
  return (CV_FIELDS[kind] || []).filter(([k]) => k in parsed && cvNorm(k, parsed[k], it) !== cvNorm(k, it.data[k], it)).map(([k, l]) => ({ k, label:l }));
}

/* SRC[itemId]: what the saved document says. state: same | edited | stale | missing | unsaved | unreadable */
const SRC = {};
let CV_SCAN = { at:0, busy:false, how:"" };
async function readSavedFile(h, sf) { let d = h; for (const p of sf.path) d = await d.getDirectoryHandle(p); return await (await d.getFileHandle(sf.name)).getFile(); }
async function cvScan(interactive, picked) {
  if (CV_SCAN.busy) return;
  const h = picked ? null : await folderHandle(!!interactive);
  if (!h && !picked) { CV_SCAN.how = FS_OK && P.folderName ? "permission" : "nofolder"; CV_SCAN.at = 0; if (interactive && FS_OK && P.folderName) toast("The folder couldn't be opened. Choose the course folder again."); return; }
  CV_SCAN.busy = true;
  try {
    for (const it of live().filter(cvScannable)) {
      const sf = (it.savedFiles || [])[0];
      if (!sf) { SRC[it.id] = { state:"unsaved" }; continue; }
      let file = null;
      try { file = picked ? picked.get(sf.name.toLowerCase()) : await readSavedFile(h, sf); } catch (e) { file = null; }
      if (!file) { SRC[it.id] = { state:picked ? "notpicked" : "missing", name:sf.name, path:sf.path }; continue; }
      try {
        const parsed = await parseSavedDoc(it, await file.arrayBuffer());
        const changed = cvDiff(it, parsed);
        const titleDiff = parsed.title && norm(parsed.title) !== norm(bareTitle(it.title)) ? parsed.title : "";
        const newer = file.lastModified > (it.savedAt || 0) + 5000;
        SRC[it.id] = { state:!changed.length ? "same" : newer || it.status === "saved" ? "edited" : "stale", parsed, changed, titleDiff, modified:file.lastModified, name:sf.name, path:sf.path };
      } catch (e) { SRC[it.id] = { state:"unreadable", err:e.message, name:sf.name, path:sf.path }; }
    }
    CV_SCAN.at = Date.now(); CV_SCAN.how = picked ? "files" : "folder";
  } finally { CV_SCAN.busy = false; }
}
/* the content a page is built from: the Word document when faculty edited it there */
function cvData(it) {
  const s = SRC[it.id];
  if (!s || s.state !== "edited") return it.data;
  const d = Object.assign(clone(it.data), clone(s.parsed));
  delete d.title;
  if (s.parsed.settings) d.settings = Object.assign({}, it.data.settings || {}, s.parsed.settings);
  return d;
}

/* ============================================================
   Page builders. Each returns { html, issues }.
   issues: { level:"gap" | "warn", text }. Gaps block the copy button.
   ============================================================ */
/* APA format labels in square brackets are real citation text, not placeholders */
const CV_APA = /^\[(video|audio|audiobook|podcast|podcast episode|data set|dataset|infographic|image|photograph|slides|powerpoint slides|lecture notes|tweet|blog post|fact sheet|brochure|report|online course|computer software|software|interview|webinar|film|motion picture|television series|tv series|special issue|editorial|letter to the editor|abstract|white paper|press release|map|chart|table|figure|case study)( episode| series)?\]$/i;
function cvLint(fields, issues) {
  for (const [label, val] of fields) {
    const t = String(val ?? "");
    const cites = t.match(/\[(cite|source|citation)[^\]\n]{0,40}\]/gi); if (cites) issues.push({ level:"gap", text:`${label} has ${cites.length} leftover AI citation ${cites.length === 1 ? "marker" : "markers"} such as ${cites[0]}. Remove ${cites.length === 1 ? "it" : "them"}.` });
    const ph = (t.match(/\[[^\]\n]{2,90}\]/g) || []).filter(x => !CV_APA.test(x) && !/^\[(cite|source|citation)/i.test(x)); if (ph.length) [...new Set(ph)].slice(0, 3).forEach(x => issues.push({ level:"gap", text:`${label} still has the placeholder ${x}. Replace it with the real detail.` }));
    const br = t.match(/(?:^|[\s("])([B-HJ-Z]) ([a-z]{3,})/g); if (br) issues.push({ level:"warn", text:`${label} may have a broken word: "${br[0].trim()}". This usually comes from copying out of Word.` });
    if (/Third-Party Tool|\[Title\]|Insert (an |the )?(assignment|overview)|Provide (general|specific|any)|enter module title/i.test(t)) issues.push({ level:"gap", text:`${label} still has template instructions in it.` });
  }
}
const cvNeed = (issues, val, label) => { if (!String(val ?? "").trim()) issues.push({ level:"gap", text:`${label} is empty.` }); };
function cvSubmitLine(s) {
  const sub = s.submission || ["file_uploads"];
  if (sub.includes("file_uploads")) return 'Click on "Start Assignment" to upload a document.';
  if (sub.includes("text_entry")) return 'Click on "Start Assignment" to type your response.';
  if (sub.includes("website_url")) return 'Click on "Start Assignment" to submit a link.';
  if (sub.includes("media_recordings")) return 'Click on "Start Assignment" to record or upload your media.';
  if (sub.includes("student_annotation")) return 'Click on "Start Assignment" to open the document and add your annotations.';
  if (sub.includes("none") || sub.includes("paper")) return "You don't need to submit anything in Canvas for this assignment.";
  return 'Click on "Start Assignment" to submit your work.';
}
const cvRubricRows = r => (r || []).filter(x => x && (x.criterion || x.excellent));
function cvAssignment(it, d) {
  const s = d.settings || {}, issues = [], fmt = cvLines(d.format);
  cvNeed(issues, d.overview, "Overview"); cvNeed(issues, d.instructions, "Guidelines");
  cvLint([["Overview", d.overview], ["Note", d.note], ["Guidelines", d.instructions], ["Format", d.format], ["Submission details", d.submission]], issues);
  if (!cvRubricRows(d.rubric).length) issues.push({ level:"warn", text:"There's no rubric. The page leaves out the Rubrics section." });
  let h = cvOpen(bareTitle(it.title)) + cvStatus(`This is ${s.group ? "a group" : "an individual"} assignment.`)
    + cvH3("fas fa-info-circle", "Overview") + cvBlocks(d.overview);
  if (String(d.note || "").trim()) h += cvCard(cvBlocks(d.note, 'style="font-size: 15px; line-height: 1.7; color: #333; margin: 0;"'), "Note:");
  h += cvH3("fas fa-compass", "Guidelines") + cvBlocks(d.instructions);
  if (fmt.length) h += `<p>Format:</p>\n<ul>\n${fmt.map(f => `<li>${cvInline(f)}</li>`).join("\n")}\n</ul>\n`;
  h += cvSubLabel("fas fa-paper-plane", "Submission") + `<p>${esc(cvSubmitLine(s))}${String(d.submission || "").trim() ? " " + cvInline(d.submission) : ""}</p>\n`;
  if (cvRubricRows(d.rubric).length) h += cvH3("fas fa-clipboard-list", "Rubrics") + `<p><span>See below for the rubric associated with this assignment.</span></p>\n`;
  h += cvH3("fas fa-headset", "Technical Support") + `<p>Need help using Canvas Assignments? If so, please review the following guide:</p>\n` + cvButton(CV_GUIDE.assignment, "Canvas Student Guide - Assignments") + cvClose();
  return { html:h, issues };
}
function cvThirdParty(it, d) {
  const s = d.settings || {}, tool = d.tool || "", issues = [], T = esc(tool || "the tool");
  if (!tool) issues.push({ level:"gap", text:"No tool is chosen for this assignment." });
  cvLint([["Overview", d.overview], ["Guidelines", d.instructions], ["Submission details", d.submission]], issues);
  const ov = String(d.overview || "").trim() ? cvBlocks(d.overview) : `<p>This assignment uses <strong>${T}</strong>, an interactive learning platform. Select the button at the bottom of this page to enter the <strong>${T}</strong> portal. In the <strong>${T}</strong> assignment, you will read the instructions and complete the assignment.</p>\n`;
  const gl = String(d.instructions || "").trim() ? cvBlocks(d.instructions) : `<p><strong>${T}</strong> assignments are graded automatically within the tool site. Please refer to the assignment in <strong>${T}</strong> for more detailed guidelines. Note that you will not need to click any "submit" or "complete" button in Canvas to show you are done with the assignment. Anything you do within the <strong>${T}</strong> assignment before the due date will count towards your grade. However, there will be no visible sign of completion or submission in Canvas until after the due date. Please click the link below to access the assignment.</p>\n`;
  let h = cvOpen(bareTitle(it.title)) + cvStatus(`This is ${s.group ? "a group" : "an individual"} assignment.`)
    + cvH3("fas fa-info-circle", "Overview") + ov + cvH3("fas fa-compass", "Guidelines") + gl
    + cvSubLabel("fas fa-paper-plane", "Submission") + `<p>Click on the "Load ${esc(cvTitle(it))} in a new window" button below to begin.${String(d.submission || "").trim() ? " " + cvInline(d.submission) : ""}</p>\n`;
  if (cvRubricRows(d.rubric).length) h += cvH3("fas fa-clipboard-list", "Rubrics") + `<p>See below for the rubric associated with this assignment, outlining the point components. For the actual assignment weight, please refer to the syllabus.</p>\n`;
  h += cvH3("fas fa-headset", "Technical Support") + `<p>Need help using <strong>${T}</strong>? If so, please review the following resource:</p>\n`;
  if (CV_HELP[tool]) h += cvButton(CV_HELP[tool], `${tool} - Help Desk`);
  else issues.push({ level:"warn", text:`The template has no help desk button for ${tool || "this tool"}. Add a link to its student help page in Canvas.` });
  return { html:h + cvClose(), issues };
}
function cvDiscussion(it, d) {
  const s = d.settings || {}, issues = [], graded = d.graded !== false;
  cvNeed(issues, d.overview, "Overview"); cvNeed(issues, d.prompt, "Prompt");
  cvLint([["Overview", d.overview], ["Prompt", d.prompt]], issues);
  let h = cvOpen(bareTitle(it.title)) + cvStatus(`This is a ${graded ? "graded" : "non-graded"} discussion.`)
    + cvH3("fas fa-info-circle", "Overview") + cvBlocks(d.overview)
    + cvCard(cvBlocks(d.prompt, 'style="font-size: 15px; line-height: 1.7; color: #333; margin: 0;"'), "Prompt")
    + cvH3("fas fa-compass", "Guidelines") + cvSubLabel("far fa-comment-dots cp-out-dp-primary", "Initial Post and Comments")
    + `<ul style="color: #000000;">\n<li>Submit a substantive post in response to the prompt above. This post is due <strong>Wednesday</strong> at <strong>11:59 p.m. CT</strong>.</li>\n<li>Reply to at least ${esc(d.replies || "two")} classmates' posts (i.e., reflect on their response, ask questions, etc.). These are due <strong>Sunday</strong> at <strong>11:59 p.m. CT</strong>.</li>\n<li>Remember to be respectful of others' opinions.</li>\n<li>All comments must adhere to the <a class="inline_disabled" style="color: #500000; text-decoration: underline;" href="https://aggiehonor.tamu.edu/rules-procedures/sr20.html#2012-honor-system" target="_blank">Aggie Honor Code</a>.</li>\n</ul>\n`
    + cvSubLabel("fas fa-paper-plane", "Submission")
    + `<ul style="color: #000000;">\n<li>Click on "Reply" below and post your initial response.${s.mustPost !== false ? " You will not be able to view others' posts until you have submitted your initial post." : ""}</li>\n<li>Respond to your classmates' posts by clicking on "Reply" below their initial post.</li>\n</ul>\n`;
  if (graded) h += cvH3("fas fa-clipboard-list", "Rubrics") + `<p>To view the rubric for this discussion, click on the <strong>Options Button</strong> (three dots located at the top-right side of the page) and select <strong>Show Rubric</strong>.</p>\n`;
  if (graded && !cvRubricRows(d.rubric).length) issues.push({ level:"warn", text:"This graded discussion has no rubric yet, but the page tells students to open one." });
  h += cvH3("fas fa-headset", "Technical Support") + `<p>Need help using Canvas Discussions? If so, please review the following guide:</p>\n` + cvButton(CV_GUIDE.discussion, "Canvas Student Guide - Discussions") + cvClose();
  return { html:h, issues };
}
function cvQuiz(it, d) {
  const qs = d.questions || [], issues = [], att = String(d.attempts || "2"), multi = att !== "1";
  if (!qs.length) issues.push({ level:"gap", text:"This quiz has no questions yet." });
  qs.forEach((q, k) => { if ((q.choices || []).filter(c => String(c).trim()).length < 2) issues.push({ level:"gap", text:`Question ${k + 1} needs at least two answer choices.` }); });
  cvLint([["What to study", d.focus], ["Assigned text", d.assigned]].concat(qs.map((q, k) => [`Question ${k + 1}`, [q.q].concat(q.choices || [], q.feedback || "").join("\n")])), issues);
  const n = CV_NUM[att] || att, keep = d.keep === "latest" ? "latest" : d.keep === "average" ? "average" : "highest", ans = d.showAnswers || "last";
  const li = [
    multi ? `<li><strong>Multiple Attempts:&nbsp;</strong>You will have <strong>${att === "unlimited" ? "unlimited" : esc(n)} attempts</strong> for this quiz, with your ${keep} score being recorded in the grade book.</li>` : `<li><strong>Attempts:&nbsp;</strong>You will have <strong>one attempt</strong> for this quiz.</li>`,
    `<li><strong>Time Limit:&nbsp;</strong>${d.minutes ? `You must complete each of your attempts in one sitting. You are allotted <strong>${esc(d.minutes)} minutes</strong> to complete each attempt.` : "There is no time limit for this quiz."}</li>`,
    `<li><strong>Answers:&nbsp;</strong>${ans === "never" ? "Correct answers will not be shown after you submit." : ans === "each" ? "After you have submitted your attempt, you will be able to view the correct answers." : "After your last attempt, you will be able to view the correct answers."}</li>`
  ];
  if (String(d.assigned || "").trim()) li.push(`<li><strong>Assigned Text:</strong>&nbsp;${cvInline(d.assigned)}</li>`);
  const review = `<div class="dp-card card cp-bg-dp-gray dp-border-dir-tblr dp-border-style-solid" style="border-color: #003c71; background-color: #bfbfbf; color: #000000; border-left-width: 6px; border-right-width: 6px;">\n<div class="card-body" style="background-color: #f7f7f7; color: #000000;">\n<h4 class="dp-has-icon"><i class="icon-note-light icon-Solid" style="color: #000000;"><span class="dp-icon-content" style="display: none;">&nbsp;</span></i><span style="font-size: 18pt; color: #500000;"> Review</span></h4>\n<p>Keep the following in mind:</p>\n<ul>\n${li.join("\n")}\n</ul>\n<p style="color: #000000;"><strong>To start, click the&nbsp;“Take the Quiz”&nbsp;button. When finished, click the&nbsp;“Submit Quiz”&nbsp;button.</strong></p>\n</div>\n</div>\n`;
  const h = cvOpen(bareTitle(it.title)) + cvStatus(d.openBook === false ? "This quiz is closed-book." : "This quiz is open-book. You may use your notes and the module materials.")
    + cvH3("fas fa-info-circle", "Guidelines") + `<p>This quiz consists of <strong>${qs.length} questions</strong>. To be successful in this quiz, thoroughly read the module material, paying particular attention to <strong>${cvInline(d.focus || "the assigned module materials")}</strong>.</p>\n`
    + review + `<p style="background-color: #f7f7f7; color: #000000; border-left: 4px solid #003c71; border-right: 4px solid #003c71;">&nbsp;&nbsp;<span style="font-size: 14pt; color: #500000;"><strong><i class="fas fa-thumbs-up"><span class="dp-icon-content" style="display: none;">&nbsp;</span></i> Good Luck!</strong></span></p>\n` + cvClose();
  return { html:h, issues };
}
function cvItemPage(it) {
  const d = cvData(it);
  if (it.kind === "discussion") return cvDiscussion(it, d);
  if (it.kind === "quiz") return cvQuiz(it, d);
  if (it.kind === "thirdparty") return cvThirdParty(it, d);
  return cvAssignment(it, d);
}

/* ---------- Learning Materials page ---------- */
const andList = a => a.length < 2 ? (a[0] || "") : a.slice(0, -1).join(", ") + " and " + a[a.length - 1];
/* topic fragments go mid-sentence: lower the first letter unless the word is an acronym or name-like (Excel, SQL) */
const midSentence = t => /^[A-Z][a-z]/.test(t) && !/^(I|Excel|Python|Tableau|Power|Microsoft|Google|Amazon|Walmart|Apple|AI)\b/.test(t) ? t[0].toLowerCase() + t.slice(1) : t;
const cvOverviewVideo = m => live().find(i => i.module === m && i.kind === "video" && REQ.overview.test(i.title) && !REQ.intro.test(i.title));
const cvModuleVideos = m => { const ov = cvOverviewVideo(m); return live().filter(i => i.module === m && i.kind === "video" && i !== ov && !REQ.intro.test(i.title)); };
const cvIntroVideo = () => live().find(i => i.kind === "video" && REQ.intro.test(i.title) && !/instructor/i.test(i.title));
const cvInstructorVideo = () => live().find(i => i.kind === "video" && /instructor/i.test(i.title));
function cvDue(m, wed) { const w = weekOf(m); if (!w) return null; const d = wed ? w.wed : w.sun; return `${DAYS[d.getDay()]}, ${MONTHS[d.getMonth()]} ${d.getDate()} at 11:59 p.m. CT`; }
function cvCohortWhen(m) {
  const C = cvState(), w = weekOf(m); if (!w || C.cohortDay === "" || C.cohortDay == null || !String(C.cohortTime || "").trim()) return null;
  let d = w.start; for (let k = 0; k < 7 && d.getDay() !== Number(C.cohortDay); k++) d = addDays(d, 1);
  return { day:DAYS[d.getDay()], date:`${MONTHS[d.getMonth()]} ${d.getDate()}`, time:String(C.cohortTime).trim() };
}
function lmDefaults(m) {
  const mod = P.plan.modules[m - 1] || {}, topics = cvLines(mod.topics);
  const mats = linesOf(mod.materials).filter(l => !READING_RE.test(l));
  return {
    overview:`${topics.length ? `In this module, you will study ${andList(topics.map(t => midSentence(t.replace(/\.$/, ""))))}. ` : ""}Take a moment to watch the video below for an introduction to the module.`,
    objectives:(mod.clos || []).map(id => (P.plan.clos.find(c => c.id === id) || {}).text || "").filter(Boolean).join("\n"),
    readings:mats.filter(l => !/\b(optional|supplement)/i.test(l)).join("\n"),
    supplemental:mats.filter(l => /\b(optional|supplement)/i.test(l)).map(l => l.replace(/\s*\((optional|supplemental)\)/i, "").trim()).join("\n"),
    questions:"", extraTodo:""
  };
}
function cvPage(key) {
  const C = cvState(); C.pages[key] = C.pages[key] || {};
  const m = +key.split(":")[1], def = key === "welcome" ? welcomeDefaults() : key.startsWith("lm:") ? lmDefaults(m) : sumDefaults(m), pg = C.pages[key];
  const get = k => pg[k] !== undefined ? pg[k] : def[k];
  return { pg, def, get };
}
const cvLink = id => String((cvState().links || {})[id] || "").trim();
function cvReadingLine(l) {
  const m = l.match(/^([A-Z][A-Za-z ]{1,24}):\s*(.*)$/);
  return m ? `<li><span><span style="color: #003c71;"><strong>${esc(m[1])}:</strong> </span>${cvInline(m[2])}</span></li>` : `<li><span>${cvInline(l)}</span></li>`;
}
function cvMaterials(m) {
  const mod = P.plan.modules[m - 1] || {}, { get } = cvPage(`lm:${m}`), issues = [];
  const its = live().filter(i => i.module === m), acts = cvActivities(m), ov = cvOverviewVideo(m), vids = cvModuleVideos(m);
  const instr = its.filter(i => i.kind === "reading"), cohort = its.find(i => i.kind === "cohort");
  const due = cvDue(m), wed = cvDue(m, true);
  if (!due) issues.push({ level:"warn", text:"Due dates are missing. Add the session start date on Setup in Course Development." });
  cvLint([["Overview", get("overview")], ["Objectives", get("objectives")], ["Readings", get("readings")], ["Supplemental readings", get("supplemental")], ["Video questions", get("questions")], ["Extra to-do items", get("extraTodo")]], issues);
  cvNeed(issues, get("overview"), "Overview"); cvNeed(issues, get("objectives"), "Objectives");
  /* videos are embedded in Canvas; the page carries the template's placeholder box where each one goes */
  const embed = (v, label) => cvVideoBox(label);
  const vlen = v => { const l = videoLengthLabel(v).replace(/^About\s*/, ""); return l ? ` (${l})` : ""; };
  const dueTxt = (x, d) => d ? `, <strong>due ${esc(d)}</strong>` : "";
  const tabs = [];
  // Overview
  let o = `<p class="paragraph ng-attr-widget"><span>Welcome to Module ${m}, <strong>${esc(mod.title || "")}</strong>. ${cvInline(get("overview"))}</span></p>\n`;
  if (ov) o += `<p class="paragraph ng-attr-widget"><span><strong>Video:</strong> ${esc(/^module\s*\d*\s*overview$/i.test(bareTitle(ov.title)) ? `Module ${m} Overview` : bareTitle(ov.title))}${vlen(ov)}</span></p>\n` + embed(ov, /^module\s*\d*\s*overview$/i.test(bareTitle(ov.title)) ? `Module ${m} Overview` : bareTitle(ov.title));
  const obj = cvLines(get("objectives"));
  if (obj.length) o += cvCard(`<p><span style="color: #003c71;"><strong>By the end of this module, you will be able to:</strong></span></p>\n<ul>\n${obj.map(x => `<li><span>${cvInline(x)}</span></li>`).join("\n")}\n</ul>\n`);
  tabs.push({ name:"Overview", icon:"fas fa-binoculars", body:o });
  // To-Do
  const todo = [];
  const reqR = cvLines(get("readings"));
  if (reqR.length || instr.length) todo.push(`<li><span>Complete the Readings${dueTxt(0, due)}</span></li>`);
  if (vids.length || ov) todo.push(`<li><span>Watch the Videos${dueTxt(0, due)}</span></li>`);
  acts.filter(i => i.kind === "discussion").forEach(i => todo.push(`<li><span>Engage in the Discussion: ${esc(bareTitle(i.title))}</span>\n<ul>\n<li><span>Initial post${dueTxt(0, wed)}</span></li>\n<li><span>Replies${dueTxt(0, due)}</span></li>\n</ul>\n</li>`));
  if (cohort) { const w = cvCohortWhen(m); todo.push(`<li><span>Participate in the Cohort Session${w ? ` <strong>on ${esc(w.day)}, ${esc(w.date)} at ${esc(w.time)} CT</strong>` : ""}</span></li>`); }
  acts.filter(i => i.kind === "assignment" || i.kind === "activity").forEach(i => todo.push(`<li><span>Complete the ${i.kind === "activity" ? "Cohort Session Assignment" : "Assignment"}: ${esc(bareTitle(i.title))}${dueTxt(0, due)}</span></li>`));
  acts.filter(i => i.kind === "thirdparty").forEach(i => todo.push(`<li><span>Complete the ${esc(i.data.tool || "")} Assignment: ${esc(bareTitle(i.title))}${dueTxt(0, due)}</span></li>`));
  acts.filter(i => i.kind === "quiz").forEach(i => todo.push(`<li><span>Take the Quiz: ${esc(bareTitle(i.title))}${dueTxt(0, due)}</span></li>`));
  cvLines(get("extraTodo")).forEach(x => todo.push(`<li><span>${cvInline(x)}</span></li>`));
  tabs.push({ name:"To-Do", icon:"fas fa-clipboard-list", body:`<p>To successfully complete this module, do the following:</p>\n<div class="dp-card card cp-bg-dp-gray dp-border-dir-tblr dp-border-style-solid dp-padding-direction-all" style="border-color: #003c71; background-color: #f7f7f7; color: #000000; border-left-width: 1px; padding: 20px;">\n<ol>\n${todo.join("\n")}\n</ol>\n</div>\n` });
  // Readings
  const instrLis = instr.map(i => { const u = cvLink(i.id); if (!u) issues.push({ level:"warn", text:`Add the Canvas link for the Interactive Reading page "${bareTitle(i.title)}".` });
    return `<li><span><span style="color: #003c71;"><strong>Reading:</strong> </span>${u ? `<a class="inline_disabled" href="${esc(u)}" target="_blank">${esc(bareTitle(i.title))}</a>` : `${esc(bareTitle(i.title))} <strong>[add link]</strong>`}</span></li>`; });
  const sup = cvLines(get("supplemental"));
  if (reqR.length || instrLis.length || sup.length) {
    let r = `<p><span>The materials below are required reading for this module's topics and activities.</span></p>\n` + cvCard(`<ul>\n${instrLis.concat(reqR.map(cvReadingLine)).join("\n")}\n</ul>\n`);
    if (sup.length) r += `<p><span><strong>Supplemental Resources</strong> (Optional)</span></p>\n` + cvCard(`<ul>\n${sup.map(cvReadingLine).join("\n")}\n</ul>\n`);
    tabs.push({ name:"Readings", icon:"fas fa-book-reader", body:r });
  }
  // Videos
  if (vids.length) {
    let v = `<p><span>The videos below are required media for this module's topics and activities.</span></p>\n`;
    const qs = cvLines(get("questions"));
    if (qs.length) v += `<p class="paragraph ng-attr-widget"><span>As you review the videos, consider the following questions:</span></p>\n<ol>\n${qs.map(q => `<li class="paragraph ng-attr-widget"><span>${cvInline(q)}</span></li>`).join("\n")}\n</ol>\n`;
    if (vids.length <= 2) v += vids.map(x => `<p><span style="font-size: 14pt; color: #000000;"><strong>Video: </strong>${esc(bareTitle(x.title))}${vlen(x)}</span></p>\n` + embed(x, bareTitle(x.title))).join("");
    else v += `<div class="dp-card card cp-bg-dp-secondary mx-auto d-block dp-border-dir-tblr dp-border-style-solid text-start dp-shadow-b3" style="border-color: #003c71; border-left-width: 9px; font-size: 16px; background-color: #f7f7f7; color: #000000; border-right-width: 9px;">\n<div class="card-body dp-border-dir-tblr dp-margin-direction-tblr dp-padding-direction-tblr dp-border-style-none" style="padding: 8px; background-color: #f7f7f7; color: #000000;">\n<p class="card-text" style="text-align: center;"><span style="font-size: 12pt;"><strong style="color: #000000;">${cvIcon("fas fa-info-circle")} <em>Expand each section to watch all assigned videos.</em></strong></span></p>\n</div>\n</div>\n`
      + `<div class="${CV_SNIP.expander}">\n${vids.map(x => `<div class="dp-panel-group">\n<h5 class="dp-panel-heading cp-bg-dp-primary"><strong>Video:</strong> ${esc(bareTitle(x.title))}${vlen(x)}</h5>\n<div class="dp-panel-content">\n${embed(x, bareTitle(x.title))}</div>\n</div>`).join("\n")}\n</div>\n`;
    tabs.push({ name:"Videos", icon:"fas fa-play-circle", body:v });
  }
  // Cohort Session
  if (cohort) {
    const w = cvCohortWhen(m); if (!w) issues.push({ level:"warn", text:"Add the cohort session day and time on Setup." });
    const t = bareTitle(cohort.data.sessionTitle || "") || `Module ${m}`;
    const lk = (id, label) => { const u = cvLink(id); if (!u) issues.push({ level:"warn", text:`Add the Canvas link for the ${label}.` }); return u ? `<a class="inline_disabled" href="${esc(u)}" target="_blank">${esc(label)}</a>` : `${esc(label)} <strong>[add link]</strong>`; };
    const ca = acts.filter(i => i.kind === "activity");
    let c = `<p><span>A cohort session is a live, virtual meeting between the instructor and the students. While sessions are not mandatory, the information discussed and the mentorship provided are valuable to student learning. Each session is recorded for those unable to attend. To learn more about cohort sessions, please watch this <a class="inline_disabled" href="https://www.youtube.com/watch?v=z5b9nlXUpeY" target="_blank">Introduction to Cohort Sessions video</a>.</span></p>\n`
      + `<p><span>If you are new to Zoom or need a refresher, please watch this <a class="inline_disabled" href="https://www.youtube.com/watch?si=COdurXlOfpH2rc4D&amp;v=60xAamJlVfM&amp;feature=youtu.be" target="_blank">Introduction to Zoom video</a>. Below is the outline for this module's session.</span></p>\n`
      + `<p><span>This week's cohort session will be on <strong>${w ? esc(w.day) : "[day]"}</strong>, <strong>${w ? esc(w.date) : "[date]"}</strong> at <strong>${w ? esc(w.time) : "[time]"}</strong> CT. The link to access cohort sessions can be found in the Zoom tab on the course navigation bar.</span></p>\n`;
    const lis = [`<li><span><span style="color: #003c71;"><strong>Session Outline:</strong></span> ${lk(cohort.id + ":outline", `Module ${m} Cohort Session Outline`)}</span></li>`];
    if ((cohort.data.slides || []).length || String(cohort.data.slideOutline || "").trim()) lis.push(`<li><span><span style="color: #003c71;"><strong>Slides:</strong></span> ${lk(cohort.id + ":slides", `Module ${m} Cohort Session Slides`)}</span></li>`);
    if (ca.length) lis.push(`<li><span style="color: #003c71;"><strong>Cohort Session Assignment(s):</strong></span>\n<ul>\n${ca.map(i => `<li>${lk(i.id, cvTitle(i))}</li>`).join("\n")}\n</ul>\n</li>`);
    c += cvCard(`<ul>\n${lis.join("\n")}\n</ul>\n`);
    tabs.push({ name:"Cohort Session", icon:"fas fa-chalkboard-teacher", body:c, title:t });
  }
  const nextBtn = n => `<p style="text-align: right;">&nbsp;</p>\n<p style="text-align: right;"><span><em><strong>Click on the button below to go to the next tab.</strong></em></span></p>\n<p style="text-align: right;"><span><em><strong> <a class="btn btn-dp-accent cph-bg-dp-gray btn-sm dp-course-link cp-bg-dp-primary" href="#tab${n}">Next Tab</a> </strong></em></span></p>\n`;
  const last = `<p style="text-align: right;">&nbsp;</p>\n<p style="text-align: right;"><strong><span><em>You have finished reading all of the tabs. Click Next (below) to progress through the course.</em></span></strong></p>\n`;
  const h = cvOpen(mod.title || `Module ${m}`)
    + `<div class="dp-card card cp-bg-dp-secondary mx-auto d-block dp-border-dir-tblr dp-border-style-solid text-start dp-shadow-b3" style="border-color: #003c71; border-left-width: 9px; font-size: 16px; background-color: #f7f7f7; color: #000000; border-right-width: 9px;">\n<div class="card-body dp-border-dir-tblr dp-margin-direction-tblr dp-padding-direction-tblr dp-border-style-none" style="padding: 8px; border-right-width: 0px;">\n<p class="card-text" style="text-align: center;"><em><strong><span class="dp-icon fas fa-info-circle"><span class="dp-icon-content d-none">&nbsp;</span></span> Select each tab below to review all the information on this page.</strong></em></p>\n</div>\n</div>\n`
    + `<div class="${CV_SNIP.panels}">\n` + tabs.map((t, k) => `<div id="tab${k + 1}" class="dp-panel-group">\n<h3 class="dp-panel-heading${k ? "" : " active"}">${t.name}</h3>\n<div class="dp-panel-content${k ? "" : " active"}">\n<h4 class="paragraph ng-attr-widget dp-has-icon">${cvIcon(t.icon)} <strong>${t.name}</strong></h4>\n${t.body}${k < tabs.length - 1 ? nextBtn(k + 2) : last}</div>\n</div>\n`).join("") + `</div>\n`
    + `<div class="dp-banner-image"><img role="presentation" src="${CV_FOOTER_URL}" alt="" loading="lazy"></div>\n</div>`;
  return { html:h, issues };
}

/* ---------- Welcome page (Getting Started), filled into the template's own markup ---------- */
function welcomeDefaults() {
  const books = [], seen = new Set();
  P.plan.modules.forEach(m => linesOf(m.materials).filter(l => /^\s*textbook\b/i.test(l)).forEach(l => { const k = norm(l.replace(/chapters?\s*[\d\-–, ]+\.?\s*$/i, "")); if (!seen.has(k)) { seen.add(k); books.push(l.replace(/\s*,?\s*chapters?\s*[\d\-–, ]+\.?\s*$/i, ".").replace(/\.\.$/, ".")); } }));
  return { welcome:"", instructorIntro:"", profName:P.setup.instructor || "", email:"Contact me using the Canvas Inbox in the toolbar.", phone:"", hours:"", taName:"", taEmail:"", taHours:"",
    description:P.plan.description || "", objectives:(P.plan.clos || []).map(c => c.text).filter(Boolean).join("\n"), materials:books.join("\n"), courseUrl:"" };
}
function cvCourseBase(u) { const m = String(u || "").trim().match(/^(https?:\/\/[^/\s]+)\/courses\/(\d+)/i); return m ? `${m[1]}/courses/${m[2]}` : ""; }
function cvWelcome() {
  const { get:pageGet } = cvPage("welcome"), g = cvGsData(), issues = [];
  const get = k => GS_KEYS.includes(k) ? g[k] : pageGet(k);
  const doc = new DOMParser().parseFromString(`<!doctype html><html><body>${CV_SNIP.welcome}</body></html>`, "text/html"), body = doc.body;
  const frag = h => { const t = doc.createElement("template"); t.innerHTML = h; return t.content; };
  /* the innermost paragraph, list item or block that holds the text (descendants come after ancestors) */
  const paraWith = txt => [...body.querySelectorAll("p, div, li")].filter(el => el.textContent.includes(txt)).pop();
  const replace = (el, html) => { if (el) el.replaceWith(frag(html)); };
  const t = body.querySelector(".dp-header-title"); if (t) t.textContent = courseTitle() || "Course Title";
  const ban = body.querySelector(".dp-banner-image img"); if (ban) { ban.removeAttribute("width"); ban.removeAttribute("height"); }
  // Welcome tab
  cvNeed(issues, get("welcome"), "The Getting Started document's welcome message");
  replace(paraWith("[Insert a customized welcome message.]"), cvBlocks("Welcome to the course! " + String(get("welcome") || "").trim()));
  const iv = cvIntroVideo();
  replace(paraWith("[Insert the course introduction video here.]"), cvVideoBox(iv ? bareTitle(iv.title) : "Course Introduction"));
  if (!iv) issues.push({ level:"warn", text:"There's no course introduction video script in Course Development. The page keeps a placeholder for it." });
  const syl = body.querySelector('a[title="View Syllabus"]'), base = cvCourseBase(get("courseUrl"));
  if (syl) { if (base) syl.setAttribute("href", `${base}/external_tools/2042`); else { syl.setAttribute("href", "#"); issues.push({ level:"warn", text:"Add the Canvas course link so the View Syllabus button works." }); } }
  // Instructor tab
  cvNeed(issues, get("instructorIntro"), "The Getting Started document's About you section"); cvNeed(issues, get("profName"), "The professor's name");
  replace(paraWith("[Insert an introduction to the instructor."), cvBlocks(get("instructorIntro")));
  const ins = cvInstructorVideo(), insP = paraWith("[Insert the instructor video here");
  if (ins) replace(insP, cvVideoBox(bareTitle(ins.title)));
  else { const lab = insP && insP.previousElementSibling; if (lab && /Instructor Video/.test(lab.textContent)) lab.remove(); if (insP) insP.remove(); }
  const card = paraWith("Professor:") && paraWith("Professor:").closest(".card-body");
  if (card) {
    const row = (label, val) => `<div><span> <strong>${label}:</strong>&nbsp;${cvInline(val)}</span></div>`;
    let h = `<div><span> <strong>Professor: ${esc(get("profName") || "")}</strong> </span></div>\n` + row("Email", get("email") || "Contact me using the Canvas Inbox in the toolbar.");
    if (String(get("phone") || "").trim()) h += "\n" + row("Phone", get("phone"));
    h += `\n<div><span> <strong>Virtual Office Hours</strong>: ${cvInline(get("hours") || "")}${String(get("hours") || "").trim() ? " " : ""}Session information and links can be found via the&nbsp;<em>Zoom</em>&nbsp;tab in Course Navigation.</span></div>`;
    if (!String(get("hours") || "").trim()) issues.push({ level:"warn", text:"The Getting Started document has no virtual office hours for the professor." });
    if (String(get("taName") || "").trim()) h += `\n<div><hr class="dp-hr-solid-light"></div>\n` + row("Teaching Assistant", get("taName")) + "\n" + row("Email", get("taEmail") || "") + "\n" + row("Virtual Office Hours", get("taHours") || "");
    card.innerHTML = h;
  }
  // Course Information tab
  cvNeed(issues, get("description"), "Course description");
  replace(paraWith("[Insert the course description from the syllabus]"), cvBlocks(get("description")));
  const objUl = paraWith("[Learning Objective 1]") && paraWith("[Learning Objective 1]").closest("ul");
  if (objUl) objUl.innerHTML = cvLines(get("objectives")).map(o => `<li><span>${cvInline(o)}</span></li>`).join("\n");
  const matUl = paraWith("[Textbook 1 in APA or MLA format]") && paraWith("[Textbook 1 in APA or MLA format]").closest("ul");
  if (matUl) matUl.innerHTML = cvLines(get("materials")).map(cvReadingLine).join("\n");
  if (!cvLines(get("materials")).length) issues.push({ level:"warn", text:"The Getting Started document lists no assigned materials. List the course textbook or say that all materials are provided in Canvas." });
  // Course Structure tab
  const n = modCount(), word = CV_NUM[n] || String(n);
  const org = paraWith("[eight weeks]"); if (org) org.innerHTML = org.innerHTML.replace("[eight]", word).replace("[eight weeks]", `${word} ${n === 1 ? "week" : "weeks"}`);
  const idNote = paraWith("Instructional Designers: Be sure to review"); if (idNote) idNote.remove();
  cvLint([["Welcome message", get("welcome")], ["About the instructor", get("instructorIntro")], ["Course description", get("description")], ["Course learning objectives", get("objectives")], ["Assigned materials", get("materials")]], issues);
  // anything the template still asks someone to fill in
  const left = (body.textContent.match(/\[[^\]\n]{2,120}\]/g) || []).filter(x => !/^\[Video Placeholder/.test(x) && !CV_APA.test(x));
  [...new Set(left)].slice(0, 4).forEach(x => issues.push({ level:"gap", text:`The page still has template text: ${x.length > 90 ? x.slice(0, 90) + "…]" : x}` }));
  return { html:body.innerHTML.trim(), issues };
}

/* ---------- Getting Started: announcement, General Q&A, Class Introductions, Syllabus Acknowledgement Quiz ---------- */
function cvLeftover(html, issues) {
  const txt = html.replace(/<[^>]+>/g, " ");
  const left = (txt.match(/\[[^\]\n]{2,120}\]/g) || []).filter(x => !/^\[Video Placeholder/.test(x) && !CV_APA.test(x));
  [...new Set(left)].slice(0, 4).forEach(x => issues.push({ level:"gap", text:`The page still has template text: ${x.length > 90 ? x.slice(0, 90) + "…]" : x}` }));
}
function cvAnnounce() {
  const g = cvGsData(), issues = [];
  cvNeed(issues, g.welcome, "The Getting Started document's welcome message");
  const msg = [cvBlocks(g.welcome), cvBlocks(g.instructorIntro), g.profName ? `<p>${esc(g.profName)}</p>\n` : ""].join("").trim();
  let h = CV_SNIP.gsAnnounce.replace("[insert course name]", esc(courseTitle() || "the course"));
  h = h.replace(/<p><span[^>]*>\[insert faculty welcome and introduction message\]<\/span><\/p>/, msg || "<p>[insert faculty welcome and introduction message]</p>");
  cvLint([["Welcome message", g.welcome], ["About you", g.instructorIntro]], issues);
  cvLeftover(h, issues);
  return { html:h, issues };
}
function cvGsQA() { return { html:CV_SNIP.gsQA, issues:[] }; }
function cvGsIntro() {
  const g = cvGsData(), issues = [];
  if (g.introFirst) return { html:CV_SNIP.gsIntroFirst, issues };
  cvNeed(issues, g.introPrompt, "The Getting Started document's introduction prompt");
  const h = CV_SNIP.gsIntroOther.replace("<p>[Insert a discussion prompt and any related links to articles, websites, or videos.]</p>", cvBlocks(g.introPrompt) || "<p>[Insert a discussion prompt and any related links to articles, websites, or videos.]</p>");
  cvLint([["Introduction prompt", g.introPrompt]], issues);
  cvLeftover(h, issues);
  return { html:h, issues };
}
/* the syllabus quiz as a quiz item, with the template's fixed settings */
function cvGsQuizItem() {
  const g = cvGsData();
  return { id:"gs:quiz", kind:"quiz", module:0, title:"Syllabus Acknowledgement Quiz", clos:[], data:{ questions:(g.questions || []).filter(q => q && String(q.q || "").trim()), attempts:"2", keep:"highest", minutes:"30", showAnswers:"each", shuffle:false, quizType:"graded", ppq:"1", oneAtATime:false, agroup:"" } };
}
function cvGsQuiz() {
  const qs = cvGsQuizItem().data.questions, issues = [];
  if (!qs.length) issues.push({ level:"gap", text:"The Getting Started document has no syllabus quiz questions yet." });
  else if (qs.length !== 5) issues.push({ level:"warn", text:`The syllabus quiz has ${qs.length} ${qs.length === 1 ? "question" : "questions"}. The template calls for 5.` });
  qs.forEach((q, k) => { if ((q.choices || []).filter(c => String(c).trim()).length < 2) issues.push({ level:"gap", text:`Question ${k + 1} needs at least two answer choices.` }); });
  cvLint(qs.map((q, k) => [`Question ${k + 1}`, [q.q].concat(q.choices || [], q.feedback || "").join("\n")]), issues);
  return { html:CV_SNIP.gsQuiz.replace("This quiz consists of <strong>5</strong>", `This quiz consists of <strong>${qs.length || 5}</strong>`), issues };
}
/* What a Getting Started page takes from the document, shown read-only next to its HTML */
function cvGsBox(parts) {
  const g = cvGsData(), it = cvGsItem();
  const row = (label, v) => `<div class="cv-gs-row"><b>${label}</b><div>${String(v || "").trim() ? esc(v).replace(/\n/g, "<br>") : `<span class="sub">Not written yet</span>`}</div></div>`;
  const R = {
    welcome:() => row("Welcome message", g.welcome),
    instructorIntro:() => row("About the instructor", g.instructorIntro),
    contact:() => row("Contact", [g.profName && `Professor: ${g.profName}`, g.email && `Email: ${g.email}`, g.phone && `Phone: ${g.phone}`, g.hours && `Virtual office hours: ${g.hours}`, g.taName && `Teaching assistant: ${g.taName}${g.taEmail ? ", " + g.taEmail : ""}${g.taHours ? ", " + g.taHours : ""}`].filter(Boolean).join("\n")),
    materials:() => row("Assigned materials", g.materials),
    intro:() => row("Class Introductions", g.introFirst ? "The standard prompt for students' first course in the program" : g.introPrompt)
  };
  return `<div class="cv-gs"><p class="sub">From the Getting Started document. To change it, edit the document in Course Development and save it again, or edit the Word document and check the documents again.${it ? ` <button class="btn link small" data-action="cvOpenDev" data-arg="${it.id}">Open it in Course Development</button>` : ""}</p>${parts.map(k => R[k]()).join("")}</div>`;
}

/* ---------- Interactive Reading page (from an instructor-authored reading) ---------- */
const cvChoices = t => linesOf(t).map(c => ({ ok:/^\*/.test(c), text:c.replace(/^\*\s*/, "") }));
function cvFlipCards(terms) {
  const card = t => `<div class="col-lg-6 col-md-6 col-12 d-flex justify-content-center">\n<div class="dp-flip-card dp-flip-card-fast dp-flip-card-show-both mx-auto d-block" aria-label="Flip Card">\n<div class="dp-flip-card-inner">\n<div class="dp-front-card">\n<div class="dp-card card h-100">\n<div class="card-body">\n<h5 class="card-title dp-ignore-theme">${esc(t.term)}</h5>\n</div>\n</div>\n</div>\n<div class="dp-back-card">\n<div class="dp-card card h-100">\n<div class="card-body">\n<p>${cvInline(t.definition)}</p>\n</div>\n</div>\n</div>\n</div>\n</div>\n</div>`;
  let h = `<p><em><strong><i class="dp-icon far fa-hand-point-right"><span class="dp-icon-content" style="display: none;">&nbsp;</span></i> Flip each card to see its definition.</strong></em></p>\n<div class="dp-column-container container-fluid">\n`;
  for (let k = 0; k < terms.length; k += 2) h += `<div class="row dp-col-2-eq">\n${terms.slice(k, k + 2).map(card).join("\n")}\n</div>\n`;
  return h + `</div>\n`;
}
function cvCheck(t) {
  const ch = cvChoices(t.checkChoices), L = "ABCDEFGH", ok = ch.findIndex(c => c.ok);
  return `<div class="dp-card card cp-bg-dp-gray dp-border-dir-tblr dp-border-style-solid" style="border-left-color: #500000; background-color: #bfbfbf; color: #000; border-left-width: 6px; border-right-width: 6px; border-right-color: #500000; margin-top: 16px;">\n<div class="card-body" style="background: #e8e8e8;">\n`
    + `<p><strong>Knowledge Check:</strong> ${cvInline(t.check)}</p>\n<p>${ch.map((c, k) => `${L[k]}. ${cvInline(c.text)}`).join("<br>")}</p>\n`
    + `<details style="margin-top: 8px;">\n<summary>Show answer</summary>\n<em>Correct: ${ok >= 0 ? `${L[ok]}. ${cvInline(ch[ok].text)}.` : ""}</em>${String(t.checkWhy || "").trim() ? " " + cvInline(t.checkWhy) : ""}</details>\n</div>\n</div>\n`;
}
function cvReading(it) {
  const d = cvData(it), issues = [];
  const terms = (d.terms || []).filter(t => t && String(t.term || "").trim());
  const topics = (d.topics || []).filter(t => t && (String(t.heading || "").trim() || String(t.body || "").trim()));
  cvNeed(issues, d.overview, "Overview");
  if (!topics.length) issues.push({ level:"gap", text:"The reading has no sections yet. Each section becomes a tab." });
  cvLint([["Overview", d.overview], ["Conclusion", d.conclusion], ["References", d.references]].concat(terms.map(t => [`Key term "${t.term}"`, t.definition]), topics.map((t, k) => [`Section ${k + 1}`, [t.heading, t.body, t.check, t.checkChoices, t.checkWhy].join("\n")])), issues);
  terms.filter(t => !String(t.definition || "").trim()).forEach(t => issues.push({ level:"warn", text:`Key term "${t.term}" has no definition, so its flip card is blank on the back.` }));
  topics.forEach((t, k) => {
    if (!String(t.check || "").trim()) return;
    const ch = cvChoices(t.checkChoices);
    if (ch.length < 2) issues.push({ level:"gap", text:`The knowledge check in section ${k + 1} needs at least two answer choices.` });
    else if (ch.filter(c => c.ok).length !== 1) issues.push({ level:"gap", text:`Mark exactly one correct answer with * in the section ${k + 1} knowledge check.` });
  });
  if (topics.length && !topics.some(t => String(t.check || "").trim())) issues.push({ level:"warn", text:"No section has a knowledge check. The template ends each tab with one." });
  const tabs = [];
  let intro = cvBlocks(d.overview);
  if (terms.length) intro += cvFlipCards(terms);
  tabs.push({ name:"Introduction", h4:"Overview", icon:"fas fa-binoculars", body:intro });
  topics.forEach(t => {
    let b = cvBlocks(t.body);
    if (String(t.video || "").trim()) b += `<p><span style="font-size: 14pt; color: #000000;"><strong>Video: </strong>${esc(t.video)}</span></p>\n` + cvVideoBox(t.video);
    if (String(t.check || "").trim()) b += cvCheck(t);
    tabs.push({ name:String(t.heading || "Section").trim(), h4:String(t.heading || "Section").trim(), icon:"fas fa-laptop", body:b });
  });
  let wrap = cvBlocks(d.conclusion);
  if (String(d.references || "").trim()) wrap += `<p><strong>References</strong></p>\n` + cvLines(d.references).map(r => `<p style="padding-left: 40px; text-indent: -40px;">${cvInline(r)}</p>`).join("\n") + "\n";
  if (d.aiUsed) wrap += `<p><strong>Use of AI</strong></p>\n<p>In keeping with my commitment to leverage advanced technology for enhanced efficiency and accuracy in my work, I used generative artificial intelligence tools to assist in drafting this reading.</p>\n`;
  if (String(d.conclusion || "").trim() || String(d.references || "").trim() || d.aiUsed) tabs.push({ name:"Wrap-Up", h4:"Conclusion", icon:"fas fa-flag-checkered", body:wrap });
  const nextBtn = n => `<p style="text-align: right;">&nbsp;</p>\n<p style="text-align: right;"><span><em><strong>Click on the button below to go to the next tab.</strong></em></span></p>\n<p style="text-align: right;"><span><em><strong> <a class="btn btn-dp-accent cph-bg-dp-gray btn-sm dp-course-link cp-bg-dp-primary" href="#tab${n}">Next Tab</a> </strong></em></span></p>\n`;
  const last = `<p style="text-align: right;">&nbsp;</p>\n<p style="text-align: right;"><strong><span><em>You have finished reading all of the tabs. Click Next (below) to progress through the course.</em></span></strong></p>\n`;
  const h = cvOpen(bareTitle(it.title))
    + `<div class="dp-card card cp-bg-dp-secondary mx-auto d-block dp-border-dir-tblr dp-border-style-solid text-start dp-shadow-b3" style="border-color: #003c71; border-left-width: 9px; font-size: 16px; background-color: #f7f7f7; color: #000000; border-right-width: 9px;">\n<div class="card-body dp-border-dir-tblr dp-margin-direction-tblr dp-padding-direction-tblr dp-border-style-none" style="padding: 8px; border-right-width: 0px;">\n<p class="card-text" style="text-align: center;"><em><strong><span class="dp-icon fas fa-info-circle"><span class="dp-icon-content d-none">&nbsp;</span></span> Select each tab below to review the interactive reading. Complete any or all knowledge checks.</strong></em></p>\n</div>\n</div>\n`
    + `<div class="${CV_SNIP.panels}">\n` + tabs.map((t, k) => `<div id="tab${k + 1}" class="dp-panel-group">\n<h3 class="dp-panel-heading${k ? "" : " active"}">${esc(t.name)}</h3>\n<div class="dp-panel-content${k ? "" : " active"}">\n<h4 class="paragraph ng-attr-widget dp-has-icon">${cvIcon(t.icon)} <strong>${esc(t.h4)}</strong></h4>\n${t.body}${k < tabs.length - 1 ? nextBtn(k + 2) : last}</div>\n</div>\n`).join("") + `</div>\n`
    + `<div class="dp-banner-image"><img role="presentation" src="${CV_FOOTER_URL}" alt="" loading="lazy"></div>\n</div>`;
  return { html:h, issues };
}

/* ---------- Module Summary page ---------- */
function sumDefaults(m) {
  const mod = P.plan.modules[m - 1] || {}, next = P.plan.modules[m] || null, topics = cvLines(mod.topics).map(t => midSentence(t.replace(/\.$/, "")));
  return {
    summary:topics.length ? `During this module, you studied ${andList(topics)}.` : `During this module, you studied ${mod.title || "the module topics"}.`,
    review:"Revisit the key concepts from this module and note how you could apply them in your own work.",
    next:next ? "" : "Share your feedback in the Student Course Evaluation so future sessions of this course keep improving."
  };
}
function cvSummary(m) {
  const mod = P.plan.modules[m - 1] || {}, next = P.plan.modules[m] || null, { get } = cvPage(`sum:${m}`), issues = [];
  cvNeed(issues, get("summary"), "Summary");
  cvLint([["Summary", get("summary")], ["Review your notes", get("review")], ["Next module", get("next")]], issues);
  const cohort = live().some(i => i.module === m && i.kind === "cohort");
  const lis = [`<li><strong>Review Your Notes</strong>: ${cvInline(get("review"))}</li>`];
  if (next) lis.push(`<li><strong>Prepare for the Next Module</strong>: In the next module, we will explore <strong>${esc(next.title || `Module ${m + 1}`)}</strong>.${String(get("next")).trim() ? " " + cvInline(get("next")) : ""}</li>`);
  else lis.push(`<li><strong>Complete the Course Evaluation</strong>: ${cvInline(get("next") || "")}</li>`);
  const h = cvOpen("Module Summary")
    + `<p>Congratulations on completing <strong>Module ${m}</strong>!${cohort ? " You now have access to this week's cohort session recording through the Zoom tab." : ""} ${cvInline(get("summary"))}</p>\n`
    + `<p><strong>Next Steps:</strong></p>\n<ul>\n${lis.join("\n")}\n</ul>\n` + cvClose();
  return { html:h, issues };
}
function cvBuildEntry(e) { return e.type === "announce" ? cvAnnounce() : e.type === "gsqa" ? cvGsQA() : e.type === "gsintro" ? cvGsIntro() : e.type === "gsquiz" ? cvGsQuiz() : e.type === "welcome" ? cvWelcome() : e.type === "materials" ? cvMaterials(e.m) : e.type === "summary" ? cvSummary(e.m) : e.type === "reading" ? cvReading(e.it) : cvItemPage(e.it); }

/* ============================================================
   Canvas settings, rubric and quiz questions for each item
   ============================================================ */
function cvSettings(it) {
  const d = cvData(it), s = d.settings || {}, dt = datesFor(it.module), rows = [];
  const pts = cvRubricRows(d.rubric).reduce((a, r) => a + (parseFloat(r.points) || 0), 0);
  const add = (label, value, where) => rows.push({ label, value:String(value), where:where || "" });
  if (it.kind === "quiz") {
    const n = (d.questions || []).length, ppq = parseFloat(d.ppq) || 1;
    add("Quiz type", d.quizType === "practice" ? "Practice Quiz" : "Graded Quiz");
    add("Assignment group", d.agroup || "Choose the group the syllabus uses");
    add("Shuffle answers", d.shuffle === false ? "Off" : "On");
    add("Time limit", d.minutes ? `${d.minutes} minutes` : "Off");
    const att = String(d.attempts || "2");
    add("Allow multiple attempts", att === "1" ? "Off" : `On · ${att === "unlimited" ? "unlimited" : att + " attempts"} · keep ${d.keep || "highest"} score`);
    add("Let students see their responses", d.showAnswers === "never" ? "Off" : d.showAnswers === "each" ? "On, once after each attempt" : "On, only after their last attempt");
    add("Let students see the correct answers", d.showAnswers === "never" ? "Off" : d.showAnswers === "each" ? "On" : "On, only after their last attempt");
    add("Show one question at a time", d.oneAtATime ? "On" : "Off");
    add("Points", `${n * ppq} (${n} questions at ${ppq} ${ppq === 1 ? "point" : "points"} each)`, "Set by the questions");
  } else if (it.kind === "discussion") {
    add("Graded", d.graded === false ? "No" : "Yes");
    if (d.graded !== false) { add("Points possible", d.points || pts || 100); add("Assignment group", d.agroup || "Discussions"); add("Display grade as", "Points"); }
    add("Anonymous discussion", s.anonymous === "full" ? "Full" : s.anonymous === "partial" ? "Partial" : "Off");
    add("Participants must respond to the topic before viewing other replies", s.mustPost !== false ? "On" : "Off");
    add("Disallow threaded replies", s.noThreads ? "On" : "Off");
    add("Allow liking", s.liking ? "On" : "Off");
    add("This is a group discussion", s.group ? "On" : "Off");
    add("Peer review", s.peer === "manual" ? "Assign manually" : s.peer === "auto" ? "Automatically assign" : "Off");
  } else {
    const ext = it.kind === "thirdparty";
    add("Points", pts || d.points || "Use the points in the syllabus");
    add("Display grade as", "Points");
    const sub = ext ? ["external"] : (s.submission || ["file_uploads"]);
    const lab = { file_uploads:"File uploads", text_entry:"Text entry", website_url:"Website URL", media_recordings:"Media recordings", student_annotation:"Student annotation" };
    if (ext) { add("Submission type", `External Tool: find ${d.tool || "the tool"}`); add("Load this tool in a new tab", "On"); }
    else add("Submission type", sub.includes("none") ? "No submission" : sub.includes("paper") ? "On paper" : "Online: " + sub.filter(k => lab[k]).map(k => lab[k]).join(", "));
    if (!ext) { add("Submission attempts", s.attempts === "unlimited" ? "Unlimited" : `Limited: ${s.attemptsNum || 2}`); add("Plagiarism review", s.plagiarism === "turnitin" ? "Turnitin" : "None"); }
    add("Group assignment", s.group ? `On${s.groupIndividual ? ", assign grades to each student individually" : ""}` : "Off");
    add("Require peer reviews", s.peer ? `On, ${s.peerHow === "manual" ? "manually" : "automatically"} assigned${s.peerAnon ? ", anonymous" : ""}` : "Off");
  }
  add("Assign to", "Everyone");
  if (it.kind === "discussion") add("Due", `${dt.due} (replies; initial posts are due ${dt.wed})`);
  else add("Due", dt.due);
  add("Available from", dt.avail);
  add("Until", dt.until);
  if (cvRubricRows(d.rubric).length && it.kind !== "quiz") add("Rubric", "Add the rubric below and choose Use this rubric for assignment grading", "After you save");
  return rows;
}

function cvGsSettings(e) {
  const dt = datesFor(0), rows = [], add = (label, value, where) => rows.push({ label, value:String(value), where:where || "" });
  if (e.type === "gsquiz") return cvSettings(cvGsQuizItem());
  if (e.type === "gsintro") {
    add("Graded", "Yes, with the points the syllabus gives it"); add("Rubric", "Already attached in the template. Check that it's there.");
    add("Participants must respond to the topic before viewing other replies", "On");
    add("Assign to", "Everyone"); add("Due", `${dt.due} (replies; initial posts are due ${dt.wed})`); add("Available from", dt.avail); add("Until", dt.until);
  }
  if (e.type === "announce") add("Delay posting", `On, until ${dt.avail}`);
  return rows;
}

/* QTI 1.2 package in the format Canvas exports quizzes in, so Import Course Content > QTI .zip reads it */
const cvHex = () => "g" + Array.from(crypto.getRandomValues(new Uint8Array(16)), b => b.toString(16).padStart(2, "0")).join("");
function cvQti(it) {
  const d = cvData(it), qs = (d.questions || []).filter(q => String(q.q || "").trim()), id = cvHex(), ppq = parseFloat(d.ppq) || 1, title = cvTitle(it);
  const att = String(d.attempts || "2"), used = new Set();
  const aid = () => { let n; do n = 1000 + Math.floor(Math.random() * 9000); while (used.has(n)); used.add(n); return n; };
  const items = qs.map((q, k) => {
    const choices = (q.choices || []).filter(c => String(c).trim()), ids = choices.map(aid), corr = ids[Math.min(Number(q.correct) || 0, ids.length - 1)];
    const fb = String(q.feedback || "").trim();
    return `      <item ident="${cvHex()}" title="Question ${k + 1}">
        <itemmetadata>
          <qtimetadata>
            <qtimetadatafield><fieldlabel>question_type</fieldlabel><fieldentry>multiple_choice_question</fieldentry></qtimetadatafield>
            <qtimetadatafield><fieldlabel>points_possible</fieldlabel><fieldentry>${ppq}</fieldentry></qtimetadatafield>
            <qtimetadatafield><fieldlabel>original_answer_ids</fieldlabel><fieldentry>${ids.join(",")}</fieldentry></qtimetadatafield>
            <qtimetadatafield><fieldlabel>assessment_question_identifierref</fieldlabel><fieldentry>${cvHex()}</fieldentry></qtimetadatafield>
          </qtimetadata>
        </itemmetadata>
        <presentation>
          <material><mattext texttype="text/html">${XE(`<div><p>${esc(q.q)}</p></div>`)}</mattext></material>
          <response_lid ident="response1" rcardinality="Single">
            <render_choice>
${choices.map((c, j) => `              <response_label ident="${ids[j]}"><material><mattext texttype="text/plain">${XE(c)}</mattext></material></response_label>`).join("\n")}
            </render_choice>
          </response_lid>
        </presentation>
        <resprocessing>
          <outcomes><decvar maxvalue="100" minvalue="0" varname="SCORE" vartype="Decimal"/></outcomes>
${fb ? `          <respcondition continue="Yes"><conditionvar><other/></conditionvar><displayfeedback feedbacktype="Response" linkrefid="general_fb"/></respcondition>\n` : ""}          <respcondition continue="No"><conditionvar><varequal respident="response1">${corr}</varequal></conditionvar><setvar action="Set" varname="SCORE">100</setvar></respcondition>
        </resprocessing>
${fb ? `        <itemfeedback ident="general_fb"><flow_mat><material><mattext texttype="text/html">${XE(`<p>${esc(fb)}</p>`)}</mattext></material></flow_mat></itemfeedback>\n` : ""}      </item>`;
  }).join("\n");
  const qti = `<?xml version="1.0" encoding="UTF-8"?>
<questestinterop xmlns="http://www.imsglobal.org/xsd/ims_qtiasiv1p2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.imsglobal.org/xsd/ims_qtiasiv1p2 http://www.imsglobal.org/xsd/ims_qtiasiv1p2p1.xsd">
  <assessment ident="${id}" title="${XE(title)}">
    <qtimetadata>
      <qtimetadatafield><fieldlabel>cc_maxattempts</fieldlabel><fieldentry>${att === "unlimited" ? "unlimited" : att}</fieldentry></qtimetadatafield>
    </qtimetadata>
    <section ident="root_section">
${items}
    </section>
  </assessment>
</questestinterop>
`;
  const ans = d.showAnswers || "last";
  const meta = `<?xml version="1.0" encoding="UTF-8"?>
<quiz identifier="${id}" xmlns="http://canvas.instructure.com/xsd/cccv1p0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://canvas.instructure.com/xsd/cccv1p0 https://canvas.instructure.com/xsd/cccv1p0.xsd">
  <title>${XE(title)}</title>
  <description>${XE(it.id === "gs:quiz" ? cvGsQuiz().html : cvQuiz(it, d).html)}</description>
  <shuffle_answers>${d.shuffle === false ? "false" : "true"}</shuffle_answers>
  <scoring_policy>keep_${d.keep === "latest" ? "latest" : d.keep === "average" ? "average" : "highest"}</scoring_policy>
  <hide_results>${ans === "never" ? "always" : ""}</hide_results>
  <quiz_type>${d.quizType === "practice" ? "practice_quiz" : "assignment"}</quiz_type>
  <points_possible>${qs.length * ppq}</points_possible>
  <show_correct_answers>${ans === "never" ? "false" : "true"}</show_correct_answers>
  <show_correct_answers_last_attempt>${ans === "last" ? "true" : "false"}</show_correct_answers_last_attempt>
  <allowed_attempts>${att === "unlimited" ? "-1" : att}</allowed_attempts>
  ${d.minutes ? `<time_limit>${parseInt(d.minutes, 10)}</time_limit>` : "<time_limit/>"}
  <one_question_at_a_time>${d.oneAtATime ? "true" : "false"}</one_question_at_a_time>
  <cant_go_back>false</cant_go_back>
  <available>false</available>
</quiz>
`;
  const manifest = `<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="${cvHex()}" xmlns="http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1 http://www.imsglobal.org/xsd/imscp_v1p1.xsd">
  <metadata>
    <schema>IMS Content</schema>
    <schemaversion>1.1.3</schemaversion>
  </metadata>
  <organizations/>
  <resources>
    <resource identifier="${id}" type="imsqti_xmlv1p2">
      <file href="${id}/${id}.xml"/>
      <dependency identifierref="${id}_meta"/>
    </resource>
    <resource identifier="${id}_meta" type="associatedcontent/imscc_xmlv1p1/learning-application-resource" href="${id}/assessment_meta.xml">
      <file href="${id}/assessment_meta.xml"/>
    </resource>
  </resources>
</manifest>
`;
  return { name:safeName(title.replace(/\|/g, "-")) + " (QTI).zip", entries:[storedEntry("imsmanifest.xml", manifest), storedEntry(`${id}/${id}.xml`, qti), storedEntry(`${id}/assessment_meta.xml`, meta)], count:qs.length };
}

/* ============================================================
   Screens
   ============================================================ */
const CV_SCREENS = [
  { id:"setup", eyebrow:"Step 1", title:"Setup" },
  { id:"build", eyebrow:"Step 2", title:"Build pages in Canvas" },
  { id:"finish", eyebrow:"Step 3", title:"Finish" }
];
let CVCOPY = [];
const cvCopyBtn = (text, label = "Copy", cls = "sec small") => { CVCOPY.push(String(text ?? "")); return `<button class="btn ${cls} cv-copy" data-action="cvCopy" data-arg="${CVCOPY.length - 1}" title="Copy to the clipboard">${esc(label)}</button>`; };
function cvGo(screen, sel) { const C = cvState(); C.screen = screen; if (sel !== undefined) C.sel = sel; save(); render(); window.scrollTo(0, 0); }
function canvasNav() {
  const C = cvState(), ents = cvEntries(), done = ents.filter(e => cvStat(e.key) === "done").length;
  const ok = { setup:!!CV_SCAN.at, build:ents.length && done === ents.length, finish:cvFinishDone() };
  $("#steps").innerHTML = CV_SCREENS.map((s, k) => `<button class="step-btn ${C.screen === s.id ? "active" : ""} ${ok[s.id] ? "done" : ""}" data-action="cvGo" data-arg="${s.id}">
    <span class="step-num">${ok[s.id] ? "✓" : k + 1}</span><span><span class="step-eyebrow">${s.eyebrow}</span><br><span class="step-title">${s.title}</span></span></button>`).join("")
    + `<div class="nav-note"><b>${done} of ${ents.length}</b> Canvas items built.<br>${(n => n ? `${n} ${n === 1 ? "document was" : "documents were"} edited in Word.` : CV_SCAN.at ? "Documents checked." : "Documents not checked yet.")(Object.values(SRC).filter(s => s.state === "edited").length)}</div>`;
  $("#courseLabel").textContent = courseTitle() || "No plan opened yet";
}
function canvasRender() {
  CVCOPY = [];
  canvasNav();
  const C = cvState();
  $("#main").innerHTML = C.screen === "build" ? cvBuildScreen() : C.screen === "finish" ? cvFinishScreen() : cvSetupScreen();
  if (C.screen === "build") cvAfterPanel();
}

function cvDocSummary() {
  const vals = live().filter(cvScannable).map(it => [it, SRC[it.id]]);
  const n = s => vals.filter(([, x]) => x && x.state === s);
  const edited = n("edited"), stale = n("stale"), missing = n("missing").concat(n("notpicked")), unsaved = n("unsaved"), bad = n("unreadable"), same = n("same");
  if (!CV_SCAN.at) return `<p class="sub">${CV_SCAN.how === "nofolder" ? (FS_OK ? "Connect the course folder so the tool can read the saved Word documents." : "This browser can't open folders. Choose the saved Word documents instead.") : CV_SCAN.how === "permission" ? `The course folder, <b>${esc(P.folderName)}</b>, needs to be opened again. Choose <b>Check the documents</b> and allow access. If this is a different computer or browser, choose the course folder again.` : "Checking the documents in your course folder…"}</p>`;
  const total = vals.length;
  const li = (arr, cls, label, why) => arr.length ? `<li><span class="pill ${cls}">${label}</span><span><b>${arr.length} of ${total}</b> ${why}${arr.length <= 8 ? `<br><span class="sub">${arr.map(([it]) => esc(cvTitle(it))).join(" · ")}</span>` : ""}</span></li>` : "";
  const lead = same.length === total ? `<p class="cv-src ok" style="margin:0 0 6px">✓ All ${total} documents match what was saved in Course Development.</p>` : `<p class="sub" style="margin:0 0 6px"><b>${same.length} of ${total}</b> documents match what was saved in Course Development. The rest are listed below.</p>`;
  return lead + `<ul class="checks">
    ${li(same, "b-ok", "OK", same.length === 1 ? "matches what was saved in Course Development." : "match what was saved in Course Development.")}
    ${li(edited, "b-warn", "EDITED", `${edited.length === 1 ? "was" : "were"} changed in Word after saving. ${edited.length === 1 ? "Its page uses" : "Their pages use"} the Word version.`)}
    ${li(stale, "b-warn", "CHECK", `${stale.length === 1 ? "has" : "have"} newer edits in Course Development that weren't saved to Word. ${stale.length === 1 ? "Its page uses" : "Their pages use"} the Course Development version.`)}
    ${li(unsaved, "b-gap", "NOT SAVED", `${unsaved.length === 1 ? "hasn't" : "haven't"} been saved in Course Development yet. ${unsaved.length === 1 ? "Its page uses" : "Their pages use"} the current draft.`)}
    ${li(missing, "b-gap", "MISSING", CV_SCAN.how === "files" ? `${missing.length === 1 ? "wasn't" : "weren't"} among the files you chose.` : `${missing.length === 1 ? "wasn't" : "weren't"} found in the course folder. ${missing.length === 1 ? "It may have" : "They may have"} been moved or renamed.`)}
    ${li(bad, "b-gap", "UNREADABLE", `couldn't be read as ${bad.length === 1 ? "a Word document" : "Word documents"}.`)}
  </ul><p class="sub">Only documents that become Canvas pages are read, so video scripts and cohort session files aren't counted. Checked ${new Date(CV_SCAN.at).toLocaleTimeString([], { hour:"numeric", minute:"2-digit" })}${CV_SCAN.how === "files" ? " from the files you chose" : " in your course folder"}.</p>`;
}
function cvDocButtons() {
  if (FS_OK && P.folderName) return `<button class="btn sec small" data-action="cvScan">${CV_SCAN.at ? "Check again" : "Check the documents"}</button>${CV_SCAN.how === "permission" ? `<button class="btn link small" data-action="cvFolder">Choose the course folder again</button>` : ""}`;
  if (FS_OK) return `<button class="btn small" data-action="cvFolder">Choose course folder</button><button class="btn link small" data-action="cvPick">Or choose the Word files</button>`;
  return `<button class="btn small" data-action="cvPick">Choose the Word files</button>`;
}
function cvSetupScreen() {
  const C = cvState(), hasCohort = live().some(i => i.kind === "cohort");
  const mods = Array.from({ length:modCount() }, (_, k) => `Module ${k + 1}: ${(P.plan.modules[k] || {}).title || ""}`);
  return `<div class="eyebrow">Canvas Build · Step 1</div>
  <h1>Build the course in Canvas</h1>
  <p class="lede">This phase helps whoever builds the Canvas course, usually the instructional designer. For each page you get the HTML in the Mays template format, ready to paste, and a checklist of the settings Canvas keeps outside the page. Content comes from the saved Word documents, so any edits made in Word are included.</p>
  <div class="card"><div class="card-head"><div><h2>Saved documents</h2><p class="sub">The Getting Started document, assignments, discussions, quizzes and third-party tool assignments are read from the Word documents in 03 - Learning Activities, and instructor readings from 04 - Learning Materials.</p></div><span class="row">${cvDocButtons()}</span></div>
    ${cvDocSummary()}
    <input type="file" id="cvFiles" accept=".docx" multiple hidden></div>
  ${hasCohort ? `<div class="card"><h2>Cohort sessions</h2><p class="sub">Used on each module's Learning Materials page and To-Do list.</p>
    <div class="grid2" style="margin-top:8px"><div class="field"><label for="cvDay">Day of the week</label><select id="cvDay" data-cv="cohortDay"><option value="">Choose a day</option>${DAYS.map((d, k) => `<option value="${k}" ${String(C.cohortDay) === String(k) ? "selected" : ""}>${d}</option>`).join("")}</select></div>
    <div class="field"><label for="cvTime">Time (Central)</label><input type="text" id="cvTime" data-cv="cohortTime" value="${esc(C.cohortTime || "")}" placeholder="For example: 6:00 p.m."></div></div></div>` : ""}
  <div class="card"><h2>Set up the modules first</h2>
    <p class="sub" style="margin-bottom:6px">The list starts with <b>Getting Started</b>, which the course shell already has. Its Welcome page, Welcome announcement, Class Introductions discussion and Syllabus Acknowledgement Quiz are filled from the faculty member's Getting Started document. The Welcome page carries the course introduction video.</p>
    <p class="sub">Student Resources is in the course shell too. Add one Canvas module for each of these, in this order. <b>Copy title</b> copies just the module's title, ready to paste when you create the module. In each one, put the Learning Materials page first, then a text header named <b>Learning Activities</b>, then the activities, then the Module Summary page.</p>
    <ul class="cv-mods">${mods.map(t => `<li><span>${esc(t)}</span>${cvCopyBtn(t, "Copy title")}</li>`).join("")}</ul></div>
  <div class="card"><h2>How pasting works</h2>
    <ol class="cv-how"><li>In Canvas, open the page, assignment, discussion or quiz and choose <b>Edit</b>.</li>
      <li>In the editor toolbar, select the <b>HTML Editor</b> button (it looks like <code>&lt;/&gt;</code>, in the lower right of the editor).</li>
      <li>Select everything in the HTML box, then paste the HTML copied from this tool.</li>
      <li>Switch back to the regular editor to check it, then <b>Save</b>.</li></ol>
    <p class="sub">Pasting into the regular editor drops the DesignPLUS formatting, so always paste into the HTML Editor.</p></div>
  <div class="stepnav"><span></span><button class="btn" data-action="cvGo" data-arg="build">Start building →</button></div>`;
}

function cvBuildScreen() {
  const C = cvState(), ents = cvEntries();
  if (!C.sel || !ents.some(e => e.key === C.sel)) C.sel = (ents.find(e => cvStat(e.key) !== "done") || ents[0] || {}).key;
  const e = ents.find(x => x.key === C.sel);
  let rail = "", cur = -1;
  for (const x of ents) {
    if (x.m !== cur) { if (cur >= 0) rail += `</div>`; cur = x.m; rail += `<div class="cv-mod"><div class="cv-mod-h">${x.m ? `Module ${x.m}` : "Getting Started"}<span>${esc(x.m ? (P.plan.modules[x.m - 1] || {}).title || "" : "Orientation, before Module 1")}</span></div>`; }
    const st = cvStat(x.key), src = x.it ? SRC[x.it.id] : null;
    rail += `<button class="cv-entry ${x.key === C.sel ? "on" : ""} cs-${st}" data-action="cvSel" data-arg="${x.key}" title="${esc(CV_STATUS[st])}"><span class="cv-dot" aria-hidden="true"></span><span class="cv-et">${esc(x.title.replace(/^(M\d+|GS):\s*/, ""))}${x.type === "announce" ? ` <span class="cv-tag">Announcement</span>` : ""}${src && src.state === "edited" ? ` <span class="cv-tag">Edited in Word</span>` : ""}</span></button>`;
    const nx = ents[ents.indexOf(x) + 1];
    if (!CV_GS_ACT[x.type] && nx && nx.m === x.m && CV_GS_ACT[nx.type]) rail += `<div class="cv-hdr">Text header: Learning Activities</div>`;
  }
  rail += cur >= 0 ? `</div>` : "";
  return `<div class="eyebrow">Canvas Build · Step 2</div><h1 class="cv-h1">Build pages in Canvas</h1>
  <div class="cv-layout"><nav class="cv-rail" aria-label="Canvas items in module order">${rail}</nav>
  <section class="cv-panel" id="cvPanel">${e ? cvPanel(e) : `<p class="sub">Nothing to build yet.</p>`}</section></div>`;
}

function cvSourceNote(it) {
  const s = SRC[it.id];
  const open = `<button class="btn link small" data-action="cvOpenDev" data-arg="${it.id}">Open it in Course Development</button>`;
  if (!s) return CV_SCAN.at ? "" : `<div class="flag warn">The saved Word document hasn't been checked yet. ${cvDocButtons()}</div>`;
  if (s.state === "same") return `<p class="cv-src ok">✓ Matches the saved Word document, <code>${esc(s.name)}</code>.</p>`;
  if (s.state === "edited") return `<div class="flag warn"><b>Edited in Word after it was saved.</b> This page uses the Word version. Changed: ${s.changed.map(c => esc(c.label)).join(", ")}.
      <div class="row" style="margin-top:6px"><button class="btn sec small" data-action="cvAdopt" data-arg="${it.id}">Bring these edits into Course Development</button></div></div>${s.titleDiff ? cvTitleNote(it, s) : ""}`;
  if (s.state === "stale") return `<div class="flag warn"><b>Course Development has newer edits that weren't saved to Word.</b> This page uses the Course Development version (${s.changed.map(c => esc(c.label)).join(", ")}). Save it there so the Word document matches. ${open}</div>`;
  if (s.state === "unsaved") return `<div class="flag"><b>Not saved in Course Development yet.</b> This page is built from the current draft. ${open}</div>`;
  if (s.state === "missing") return `<div class="flag"><b>The Word document wasn't found</b> at <code>${esc((s.path || []).join(" / "))} / ${esc(s.name)}</code>. The page uses what was saved in Course Development.</div>`;
  if (s.state === "notpicked") return `<div class="flag warn"><code>${esc(s.name)}</code> wasn't among the files you chose, so the page uses what was saved in Course Development.</div>`;
  return `<div class="flag"><b>The Word document couldn't be read</b> (${esc(s.err || "")}). The page uses what was saved in Course Development.</div>`;
}
const cvTitleNote = (it, s) => `<div class="flag warn">The Word document's title is <b>${esc(s.titleDiff)}</b>. Canvas uses the title from Course Development, <b>${esc(bareTitle(it.title))}</b>. If the Word title is right, rename the item in Course Development so the plan stays in step.</div>`;
function cvSteps(e) {
  const g = e.m === 0 ? cvGsData() : null, dt = datesFor(0);
  if (e.type === "announce") return ["In <b>Announcements</b>, open <b>Welcome!</b>, which came with the course shell, and choose <b>Edit</b>. If it isn't there, add a new announcement titled <b>Welcome!</b>.", "Replace everything in the HTML Editor with the HTML below.", `Turn on <b>Delay posting</b> and set it to ${esc(dt.avail)} so it posts when the course opens, then save.`];
  if (e.type === "gsqa") return ["In the Getting Started module, open <b>[Template] GS: General Q&amp;A [Optional]</b> and choose <b>Edit</b>.", `Rename it <b>${esc(e.title)}</b>.`, "Replace everything in the HTML Editor with the HTML below and save. The template's wording is used as is."];
  if (e.type === "gsintro") { const use = g.introFirst ? "First Course in the Program" : "All Other Courses in the Program", drop = g.introFirst ? "All Other Courses in the Program" : "First Course in the Program";
    return [`In the Getting Started module, open <b>[Template] GS: Discussion | Class Introductions [Use for ${use}]</b> and choose <b>Edit</b>.`, `Rename it <b>${esc(e.title)}</b>.`, g.introFirst ? "Replace everything in the HTML Editor with the HTML below. It's the template's standard prompt." : "Replace everything in the HTML Editor with the HTML below. It carries the faculty member's prompt.", "Set the options in the settings checklist and save.", `Delete the other version, <b>[Template] GS: Discussion | Class Introductions [Use for ${drop}]</b>.`].concat(g.includeQA === false ? ["The faculty member chose not to use General Q&amp;A, so delete <b>[Template] GS: General Q&amp;A [Optional]</b> too."] : []); }
  if (e.type === "gsquiz") return ["Download the QTI file below, then in Canvas go to <b>Settings › Import Course Content</b>, choose <b>QTI .zip file</b>, and import it. Canvas creates the quiz with these questions, the template's instructions and its settings.", `In the Getting Started module, delete the template's empty <b>${esc(e.title)}</b> and add the imported quiz in its place, after Class Introductions.`, "Open the quiz and check the settings below. Set the dates and save."];
  if (e.type === "welcome") return ["In the Getting Started module, open the template page <b>[Template] Welcome to [Course Title]</b> that came with the course shell.", `Rename it <b>${esc(e.title)}</b> and choose <b>Edit</b>.`, "Replace everything in the HTML Editor with the HTML below and save.", "Replace the video placeholder box with the course introduction video, then save again.", "Check each tab in the student view, including the View Syllabus button."];
  if (e.type === "reading") return [`In Module ${e.m}, right after the Learning Materials page, add a new <b>Page</b> named <b>${esc(e.title)}</b>.`, "Paste the HTML below into the HTML Editor and save.", ...(cvData(e.it).topics || []).some(t => t && String(t.video || "").trim()) ? ["Replace each video placeholder box with its embedded video, then save again."] : [], "Copy the page's address and paste it into the reading link on this module's Learning Materials page.", "Check each tab and knowledge check in the student view."];
  if (e.type === "materials") return [`In Module ${e.m}, add a new <b>Page</b> named <b>${esc(e.title)}</b>.`, "Paste the HTML below into the HTML Editor and save.", "Replace each video placeholder box with its embedded video, then save again.", "Check each tab in the student view."];
  if (e.type === "summary") return [`At the end of Module ${e.m}, add a new <b>Page</b> named <b>${esc(e.title)}</b>.`, "Paste the HTML below into the HTML Editor and save."];
  const it = e.it;
  const where = e.m ? `Module ${e.m}` : "the Getting Started module";
  if (it.kind === "quiz") return [`Download the QTI file below, then in Canvas go to <b>Settings › Import Course Content</b>, choose <b>QTI .zip file</b>, and import it. Canvas creates the quiz <b>${esc(e.title)}</b> with its questions and a question bank of the same name.`,
    `Add the quiz to ${where}. If the course shell already has a template quiz in that spot, either delete it or open it and use <b>Find Questions</b> to pull from the new question bank.`,
    "Open the quiz, choose <b>Edit</b>, and paste the HTML below into the quiz instructions with the HTML Editor.", "Check the settings below, set the dates, and save."];
  const what = it.kind === "discussion" ? "Discussion" : "Assignment";
  const out = [`In ${where}, under Learning Activities, add a new <b>${what}</b> named <b>${esc(e.title)}</b>.`, `Paste the HTML below into the ${what === "Discussion" ? "discussion" : "assignment"} description with the HTML Editor.`, "Set each option in the settings checklist, then save."];
  if (cvRubricRows(cvData(it).rubric).length) out.push("After saving, add the rubric shown below.");
  return out;
}
function cvPageFields(e) {
  const key = e.key, { get } = cvPage(key), ta = (k, label, hint, rows = 3) => `<div class="field"><label for="cvf_${k}">${label}</label>${hint ? `<div class="hint">${hint}</div>` : ""}<textarea id="cvf_${k}" rows="${rows}" data-cv="pages.${key}.${k}">${esc(get(k) ?? "")}</textarea></div>`;
  const ai = `<div class="row" style="margin:0 0 10px"><button class="btn sec small ai" data-action="cvAi" data-arg="${key}" ${aiReady() ? "" : "disabled"}>Draft this page's text with AI</button><span id="cvAiStatus" class="sub">${aiReady() ? "" : "Connect AI in AI settings to draft with it."}</span></div>`;
  if (e.type === "welcome") {
    const tx = (k, label, hint, ph) => `<div class="field"><label for="cvf_${k}">${label}</label>${hint ? `<div class="hint">${hint}</div>` : ""}<input type="text" id="cvf_${k}" data-cv="pages.${key}.${k}" value="${esc(get(k) ?? "")}" placeholder="${esc(ph || "")}"></div>`;
    return `<h3 class="section-title">Welcome and Instructor tabs</h3>` + cvGsBox(["welcome", "instructorIntro", "contact", "materials"])
      + `<p class="hint">The course introduction video gets a placeholder box on the Welcome tab. Assigned materials go on the Course Information tab.</p>`
      + `<h3 class="section-title">Course Information tab</h3>` + ta("description", "Course description", "From the syllabus. Starts from the catalog description in the plan.", 3)
      + ta("objectives", "Course learning objectives", "One per line. Starts from the plan's course objectives.", 3)
      + `<h3 class="section-title">Syllabus button</h3>` + tx("courseUrl", "Canvas course link", "The address of the course home page. The View Syllabus button points to the syllabus tool in this course.", "https://canvas.tamu.edu/courses/12345");
  }
  if (e.type === "summary") return ai + ta("summary", "Summary", "Follows: Congratulations on completing Module " + e.m + "!", 3) + ta("review", "Review your notes", "", 2) + ta("next", P.plan.modules[e.m] ? "Prepare for the next module" : "Course evaluation", P.plan.modules[e.m] ? `Follows: In the next module, we will explore ${esc(P.plan.modules[e.m].title || "")}.` : "", 2);
  const m = e.m, ov = cvOverviewVideo(m), vids = cvModuleVideos(m);
  const its = live().filter(i => i.module === m), instr = its.filter(i => i.kind === "reading"), cohort = its.find(i => i.kind === "cohort"), ca = cvActivities(m).filter(i => i.kind === "activity");
  const link = (id, label) => `<div class="field"><label for="cvl_${id.replace(/\W/g, "_")}">${esc(label)}</label><input type="text" id="cvl_${id.replace(/\W/g, "_")}" data-cv="links.${id}" value="${esc(cvLink(id))}" placeholder="https://canvas.tamu.edu/courses/…"></div>`;
  let h = ai + `<h3 class="section-title">Overview tab</h3>` + ta("overview", "Overview", `Follows: Welcome to Module ${m}, ${esc((P.plan.modules[m - 1] || {}).title || "")}.`, 3)
    + ta("objectives", "Module objectives", "One per line. Starts from the course objectives this module meets.", 3)
    + `<h3 class="section-title">To-Do tab</h3><p class="hint">Built from the module's activities and due dates.</p>` + ta("extraTodo", "Other to-do items (optional)", "One per line.", 2)
    + `<h3 class="section-title">Readings tab</h3>` + ta("readings", "Required readings", "One per line, in APA style. Start with a label such as Textbook: or Article: to match the template.", 3) + ta("supplemental", "Supplemental resources (optional)", "One per line.", 2)
    + instr.map(i => link(i.id, `Canvas link for the Interactive Reading page: ${bareTitle(i.title)}`)).join("");
  if (vids.length) h += `<h3 class="section-title">Videos tab</h3>` + ta("questions", "Questions to consider while watching (optional)", "One per line.", 2) + `<p class="hint">Each video gets a placeholder box on the page. Embed the videos in Canvas after you paste the HTML.</p>`;
  if (cohort) h += `<h3 class="section-title">Cohort Session tab</h3><p class="hint">Upload the outline and slides from 05 - Cohort Sessions to the course Files, then paste each file's Canvas link here.</p>`
    + link(cohort.id + ":outline", "Canvas link for the session outline") + (((cohort.data.slides || []).length || String(cohort.data.slideOutline || "").trim()) ? link(cohort.id + ":slides", "Canvas link for the slides") : "")
    + ca.map(i => link(i.id, `Canvas link for ${cvTitle(i)}`)).join("");
  return h;
}
function cvIssuesHtml(issues) {
  if (!issues.length) return `<p class="cv-src ok">✓ No problems found in this page.</p>`;
  return `<ul class="checks cv-issues">${issues.map(i => `<li><span class="pill ${i.level === "gap" ? "b-gap" : "b-warn"}">${i.level === "gap" ? "FIX" : "CHECK"}</span><span>${esc(i.text)}</span></li>`).join("")}</ul>`;
}
let CV_LAST = null;
function cvPanel(e) {
  const C = cvState(), st = cvStat(e.key), built = cvBuildEntry(e), gaps = built.issues.filter(i => i.level === "gap").length;
  CV_LAST = { key:e.key, html:built.html };
  const ents = cvEntries(), k = ents.findIndex(x => x.key === e.key), next = ents[k + 1];
  const it = e.it, d = it ? cvData(it) : null;
  const kindTxt = e.type === "announce" ? "Announcement" : e.type === "gsqa" ? "Ungraded discussion" : e.type === "gsintro" ? "Graded discussion" : e.type === "gsquiz" ? "Quiz" : e.type === "welcome" ? "Welcome page" : e.type === "reading" ? "Interactive Reading page" : e.type === "materials" ? "Learning Materials page" : e.type === "summary" ? "Module Summary page" : it.kind === "activity" ? "Graded cohort activity" : it.kind === "thirdparty" ? `${it.data.tool || "Third-party"} assignment` : KINDS[it.kind].label;
  let h = `<div class="eyebrow">${e.m ? `Module ${e.m}` : "Getting Started"} · ${esc(kindTxt)}</div>
    <div class="cv-title"><h2>${esc(e.title)}</h2>${cvCopyBtn(e.title, "Copy title")}<span class="status cv-st cs-${st}">${CV_STATUS[st]}</span></div>
    ${it ? cvSourceNote(it) : ""}
    <div class="card cv-card"><h3>In Canvas</h3><ol class="cv-how">${cvSteps(e).map(s => `<li>${s}</li>`).join("")}</ol></div>`;
  if ((it && e.type === "item" && it.kind === "quiz") || e.type === "gsquiz") {
      const qit = e.type === "gsquiz" ? cvGsQuizItem() : it, qs = (qit.data && e.type === "gsquiz" ? qit.data.questions : d.questions || []).filter(q => String(q.q || "").trim());
      h += `<div class="card cv-card"><div class="card-head" style="margin-bottom:6px"><div><h3 style="margin:0">Quiz questions</h3><p class="sub">${qs.length} multiple-choice ${qs.length === 1 ? "question" : "questions"}, each with its answer feedback. The QTI file also carries the quiz settings and these instructions, so check them after the import.</p></div>
        <button class="btn small" data-action="cvQti" data-arg="${qit.id}" ${qs.length ? "" : "disabled"}>Download QTI file</button></div>
        <details><summary class="sub" style="cursor:pointer">See the questions</summary><ol class="cv-qs">${qs.map(q => `<li><b>${esc(q.q)}</b><ul>${(q.choices || []).map((c, j) => `<li${j === Number(q.correct) ? ` class="ok"` : ""}>${esc(c)}${j === Number(q.correct) ? " ✓" : ""}</li>`).join("")}</ul>${q.feedback ? `<div class="sub">Feedback: ${esc(q.feedback)}</div>` : ""}</li>`).join("")}</ol></details></div>`;
    }
  if (e.type === "announce" || e.type === "gsintro") h += `<div class="card cv-card"><h3>Page text</h3>${cvGsBox(e.type === "announce" ? ["welcome", "instructorIntro"] : ["intro"])}</div>`;
  if (e.type === "materials" || e.type === "summary" || e.type === "welcome") h += `<div class="card cv-card"><h3>Page text</h3><p class="sub" style="margin-bottom:8px">Changes here update the HTML below. They're saved with this course but don't change any Word document.</p>${cvPageFields(e)}</div>`;
  h += `<div class="card cv-card"><div class="card-head" style="margin-bottom:6px"><h3 style="margin:0">Page HTML</h3>
      <span class="row"><button class="btn sec small" data-action="cvToggleCode">${C.showCode ? "Show preview" : "Show HTML"}</button>
      <button class="btn small" id="cvCopyHtml" data-action="cvCopyHtml" ${gaps ? "disabled" : ""}>Copy HTML</button></span></div>
    <div id="cvChecks">${cvIssuesHtml(built.issues)}${gaps ? `<p class="sub">Fix the items marked FIX to turn on Copy HTML, or <button class="btn link small" data-action="cvCopyHtml" data-arg="force">copy it anyway</button>.</p>` : ""}</div>
    <div id="cvView">${C.showCode ? `<textarea class="cv-code" readonly rows="16" aria-label="Page HTML">${esc(built.html)}</textarea>` : `<iframe class="cv-frame" id="cvFrame" title="Page preview" sandbox=""></iframe><p class="hint">The preview is close to Canvas but not exact. DesignPLUS applies the final styling, icons and tabs once the page is saved in Canvas.</p>`}</div></div>`;
  const setRows = it && e.type === "item" ? cvSettings(it) : e.m === 0 && e.type !== "welcome" ? cvGsSettings(e) : [];
  if (setRows.length) {
    const rows = setRows, ticks = C.ticks[e.key] || {}, isQuiz = e.type === "gsquiz" || (it && e.type === "item" && it.kind === "quiz");
    h += `<div class="card cv-card"><h3>Settings checklist</h3><p class="sub" style="margin-bottom:8px">Set these on the ${isQuiz ? "quiz's Details tab" : "edit screen"} in Canvas. Tick each one as you go.</p>
      <ul class="cv-set">${rows.map((r, j) => `<li><label class="checkline"><input type="checkbox" data-cvtick="${e.key}" data-n="${j}" ${ticks[j] ? "checked" : ""}><span class="cv-row"><b>${esc(r.label)}</b><span class="cv-val">${esc(r.value)}${r.where ? `<span class="hint"> · ${esc(r.where)}</span>` : ""}</span></span></label></li>`).join("")}</ul></div>`;
    const rub = it && e.type === "item" ? cvRubricRows(d.rubric) : [];
    if (rub.length && it.kind !== "quiz") {
      const tot = rub.reduce((a, r) => a + (parseFloat(r.points) || 0), 0);
      h += `<div class="card cv-card"><div class="card-head" style="margin-bottom:6px"><div><h3 style="margin:0">Rubric</h3><p class="sub">In Canvas, choose <b>+ Rubric</b> below the ${it.kind === "discussion" ? "discussion" : "assignment"}. Add one criterion per row with four ratings: Excellent, Sufficient, Minimal and Unacceptable. Excellent carries the criterion's full points. Total: ${tot} points.</p></div></div>
        <div class="scroll-x"><table class="cv-rub"><thead><tr><th>Criterion</th><th>Excellent</th><th>Sufficient</th><th>Minimal</th><th>Unacceptable</th></tr></thead><tbody>
        ${rub.map(r => `<tr><td><b>${esc(r.criterion)}</b>${r.points ? `<div class="sub">${esc(r.points)} points</div>` : ""}${cvCopyBtn(r.criterion, "Copy")}</td>${["excellent", "sufficient", "minimal", "unacceptable"].map(f => `<td>${esc(r[f])}${String(r[f] || "").trim() ? cvCopyBtn(r[f], "Copy") : ""}</td>`).join("")}</tr>`).join("")}
        </tbody></table></div></div>`;
    }
  }
  h += `<div class="cv-foot"><span class="row">${st === "done" ? `<button class="btn sec small" data-action="cvMark" data-arg="todo">Mark as not built</button>` : `<button class="btn" data-action="cvMark" data-arg="done">Mark as built in Canvas</button>`}</span><span class="spacer"></span>${next ? `<button class="btn sec" data-action="cvSel" data-arg="${next.key}">Next: ${esc(next.title)} →</button>` : `<button class="btn sec" data-action="cvGo" data-arg="finish">Finish →</button>`}</div>`;
  return h;
}
const CV_PREVIEW_CSS = `body{margin:0;padding:18px;font:15px/1.6 "Lato","Helvetica Neue",Arial,sans-serif;color:#000;background:#fff}
a{color:#500000}img{max-width:100%}
.dp-header{border-top:2px solid #500000;text-align:center;padding:8px 0;margin:0 0 6px}
.dp-heading{margin:0;font-size:26px;color:#500000}
.dp-banner-image img{display:block;width:100%;height:110px;object-fit:cover;border-radius:4px;background:#d8d2cc}
h3.dp-has-icon,h3.paragraph{color:#500000;border-bottom:2px solid #500000;padding-bottom:4px;margin:24px 0 10px;font-size:19px}
h4{margin:8px 0}
.dp-icon{display:inline-block;width:20px;height:20px;border-radius:50%;background:#500000;vertical-align:-4px;margin-right:2px}
.dp-card{border-style:solid;border-color:#003c71;border-width:1px;border-radius:4px;margin:12px 0}
.card-body{padding:10px 14px}
.dp-panels-wrapper{margin:12px 0}
.dp-panel-group{border:1px solid #cfc8c0;border-radius:6px;margin:10px 0;overflow:hidden}
h3.dp-panel-heading{margin:0;padding:8px 12px;background:#003c71;color:#fff;font-size:16px;border:0}
.dp-panel-content{padding:4px 14px 10px}
h5.dp-panel-heading{margin:0;padding:6px 10px;background:#500000;color:#fff;font-size:14px}
.btn{display:inline-block;background:#500000;color:#fff!important;padding:4px 12px;border-radius:4px;text-decoration:none;font-size:13px}
.dp-embed-wrapper{background:#eee;padding:10px;text-align:center}
.row{display:flex;flex-wrap:wrap;gap:12px;margin:8px 0}.row>div{flex:1 1 45%}
.dp-flip-card .dp-card{margin:0;border-color:#cfc8c0}.dp-front-card .card-body{background:#f3efea;border-radius:4px 4px 0 0}.dp-front-card h5{margin:0;font-size:15px}
.dp-back-card .card-body{font-size:14px;border-top:1px dashed #b9b0a7}.dp-back-card p{margin:0}
details summary{cursor:pointer;color:#500000;font-weight:600}`;
function cvAfterPanel() {
  const f = $("#cvFrame"); if (f && CV_LAST) f.srcdoc = `<!doctype html><html><head><meta charset="utf-8"><style>${CV_PREVIEW_CSS}</style></head><body>${CV_LAST.html}</body></html>`;
  const p = $("#cvPanel"); if (p) p.scrollTop = 0;
}
let CV_T;
function cvRefresh() {
  clearTimeout(CV_T);
  CV_T = setTimeout(() => {
    const C = cvState(), e = cvEntries().find(x => x.key === C.sel); if (!e || !$("#cvChecks")) return;
    const built = cvBuildEntry(e), gaps = built.issues.filter(i => i.level === "gap").length;
    CV_LAST = { key:e.key, html:built.html };
    $("#cvChecks").innerHTML = cvIssuesHtml(built.issues) + (gaps ? `<p class="sub">Fix the items marked FIX to turn on Copy HTML, or <button class="btn link small" data-action="cvCopyHtml" data-arg="force">copy it anyway</button>.</p>` : "");
    $("#cvCopyHtml").disabled = !!gaps;
    const code = $(".cv-code"); if (code) code.value = built.html; else cvAfterPanel();
  }, 250);
}

/* Canvas Build Step 3 checks off when its Finish list is done */
function cvMissingLinks() {
  const out = [];
  for (let m = 1; m <= modCount(); m++) out.push(...cvMaterials(m).issues.filter(i => /Canvas link/.test(i.text)).map(i => `Module ${m}: ${i.text}`));
  return out;
}
function cvFinishDone() {
  const ents = cvEntries();
  return ents.length > 0 && ents.every(e => cvStat(e.key) === "done") && !cvMissingLinks().length && !live().some(i => SRC[i.id] && SRC[i.id].state === "edited");
}
function cvFinishScreen() {
  const ents = cvEntries(), left = ents.filter(e => cvStat(e.key) !== "done");
  const edited = live().filter(i => SRC[i.id] && SRC[i.id].state === "edited");
  const li = (ok, b, t) => `<li class="${ok ? "ok" : ""}"><span class="tick">${ok ? "✓" : ""}</span><span><b>${b}</b> ${t}</span></li>`;
  const missingLinks = cvMissingLinks();
  return `<div class="eyebrow">Canvas Build · Step 3</div><h1>Finish</h1>
  <div class="card finish ${!left.length ? "all-done" : ""}"><h2>${left.length ? "What's left" : "Every page is built"}</h2>
    <ul class="finish-list">
      ${li(!left.length, "Canvas items.", left.length ? `${left.length} of ${ents.length} still to build: ${left.slice(0, 6).map(e => `<button class="btn link small" data-action="cvSelGo" data-arg="${e.key}">${esc(e.title)}</button>`).join(", ")}${left.length > 6 ? "…" : ""}` : `All ${ents.length} are marked as built.`)}
      ${li(!missingLinks.length, "File links.", missingLinks.length ? `${missingLinks.length} still need a Canvas link.<br><span class="sub">${missingLinks.slice(0, 5).map(esc).join("<br>")}${missingLinks.length > 5 ? "<br>…" : ""}</span>` : "Every file link is filled in.")}
      ${li(!edited.length, "Word edits.", edited.length ? `${edited.length} ${edited.length === 1 ? "document was" : "documents were"} edited in Word. Bring the edits into Course Development so the saved work matches Canvas: ${edited.map(i => `<button class="btn link small" data-action="cvSelGo" data-arg="${i.kind === "gettingstarted" ? "welcome" : i.id}">${esc(cvTitle(i))}</button>`).join(", ")}` : "Course Development matches the Word documents.")}
    </ul></div>
  <div class="card"><h2>Before the course opens</h2>
    <p>Embed each video in the placeholder boxes on the Learning Materials pages. Then check each module in Student View, including every Learning Materials tab and the links inside them. Then ask another instructional designer to run the course through quality review.</p></div>`;
}

/* ---------- AI help for the two pages that have no Word document ---------- */
async function cvAi(key) {
  const m = +key.split(":")[1], mod = P.plan.modules[m - 1] || {}, next = P.plan.modules[m] || null, st = $("#cvAiStatus");
  const acts = live().filter(i => i.module === m).map(i => `${kindLabel(i)}: ${bareTitle(i.title)}`).join("; ");
  const clos = (mod.clos || []).map(id => (P.plan.clos.find(c => c.id === id) || {}).text).filter(Boolean).join("; ");
  const isLm = key.startsWith("lm:");
  const user = `Course: ${courseTitle()}\nModule ${m}: ${mod.title || ""}\nTopics: ${cvLines(mod.topics).join("; ")}\nCourse objectives this module meets: ${clos}\nActivities: ${acts}\n${next ? `Next module: ${next.title}\nNext module topics: ${cvLines(next.topics).join("; ")}` : "This is the last module of the course."}\n\n`
    + (isLm ? `Write the text for this module's Learning Materials page in Canvas. Return JSON: {"overview": "2 or 3 sentences that follow 'Welcome to Module ${m}, ${mod.title || ""}.' and say what students will study and do this week, ending by pointing them to the overview video below", "objectives": "3 or 4 module objectives, one per line, each completing 'By the end of this module, you will be able to:' and starting with a measurable verb", "questions": "2 or 3 questions for students to consider while watching the module videos, one per line, or an empty string if the module has no videos besides the overview"}`
      : `Write the text for this module's Module Summary page in Canvas. Return JSON: {"summary": "2 sentences that follow 'Congratulations on completing Module ${m}!' and name what students learned", "review": "1 sentence telling students what to revisit from their notes and how to apply it at work", "next": "${next ? `1 sentence previewing what the next module adds, following 'In the next module, we will explore ${next.title}.'` : "1 sentence asking students to complete the Student Course Evaluation"}"}`);
  $$("[data-action=cvAi]").forEach(b => b.disabled = true); if (st) st.innerHTML = `<span class="spin"></span>Drafting…`;
  try {
    let reply = await callClaude({ system:SYSTEM, messages:[{ role:"user", content:user }], maxTokens:1200 });
    let j = extractJSON(reply);
    if (!j) throw new Error("The AI's reply couldn't be read. Try again.");
    const pg = cvState().pages[key] = cvState().pages[key] || {};
    (isLm ? ["overview", "objectives", "questions"] : ["summary", "review", "next"]).forEach(k => { if (k in j) pg[k] = Array.isArray(j[k]) ? j[k].join("\n") : String(j[k] ?? ""); });
    save(); render(); toast("Draft ready. Read it over before you paste.");
  } catch (e) { if (st) st.innerHTML = `<span class="ai-err">${esc(e.message)}</span>`; $$("[data-action=cvAi]").forEach(b => b.disabled = false); }
}

async function cvCopyText(t) {
  try { await navigator.clipboard.writeText(t); return true; }
  catch (e) { const ta = document.createElement("textarea"); ta.value = t; ta.style.position = "fixed"; ta.style.opacity = "0"; document.body.appendChild(ta); ta.select(); let ok = false; try { ok = document.execCommand("copy"); } catch (x) {} ta.remove(); return ok; }
}
function cvAdopt(id) {
  const it = itemById(id), s = SRC[id]; if (!it || !s || s.state !== "edited") return;
  it.data = cvData(it); it.savedText = bareTitle(it.title) + " " + flatText(it.data); it.savedAt = Math.max(it.savedAt || 0, s.modified || Date.now());
  if (it.status === "review" || it.status === "draft") { it.status = "saved"; it.review = ""; }
  SRC[id] = Object.assign({}, s, { state:"same", changed:[] });
  save(); render(); toast("Course Development now matches the Word document.");
}
Object.assign(ACTIONS, {
  cvGo: a => cvGo(a),
  cvSel: a => { cvState().sel = a; save(); render(); const p = $("#cvPanel"); if (p) p.scrollIntoView({ block:"start", behavior:"smooth" }); },
  cvSelGo: a => cvGo("build", a),
  cvCopy: async a => { if (await cvCopyText(CVCOPY[+a] || "")) toast("Copied"); else toast("Couldn't copy. Select the text and copy it yourself."); },
  cvCopyHtml: async a => {
    const C = cvState(), e = cvEntries().find(x => x.key === C.sel); if (!e) return;
    const built = cvBuildEntry(e);
    if (a === "force" && !confirm("This page still has items marked FIX. Copy it anyway?")) return;
    if (!(await cvCopyText(built.html))) { C.showCode = true; render(); toast("Couldn't reach the clipboard. Select the HTML in the box and copy it."); return; }
    if (cvStat(e.key) === "todo") { C.status[e.key] = "pasted"; save(); render(); }
    toast("HTML copied. Paste it into the HTML Editor in Canvas.");
  },
  cvToggleCode: () => { const C = cvState(); C.showCode = !C.showCode; save(); render(); },
  cvMark: a => {
    const C = cvState(), e = cvEntries().find(x => x.key === C.sel); if (!e) return;
    if (a === "done" && (e.type === "item" || e.type === "gsintro" || e.type === "gsquiz" || e.type === "announce")) { const n = (e.type === "item" ? cvSettings(e.it) : cvGsSettings(e)).length, t = C.ticks[e.key] || {}; const left = n - Object.values(t).filter(Boolean).length; if (left > 0 && !confirm(`${left} ${left === 1 ? "setting isn't" : "settings aren't"} ticked yet. Mark it as built anyway?`)) return; }
    if (a === "todo") delete C.status[e.key]; else C.status[e.key] = a;
    save(); render();
  },
  cvScan: async () => { await cvScan(true); render(); },
  cvFolder: async () => { if (await chooseFolder()) { await cvScan(true); render(); } },
  cvPick: () => { const f = $("#cvFiles"); if (f) f.click(); },
  cvAdopt: a => cvAdopt(a),
  cvOpenDev: a => { S.view = "dev"; planSave(); COHORT_PART = "plan"; P.view = { screen:"item", itemId:a }; save(); renderAll(); window.scrollTo(0, 0); },
  cvQti: a => { const it = a === "gs:quiz" ? cvGsQuizItem() : itemById(a); if (!it) return; const q = cvQti(it); download(new Blob(zipBytes(q.entries), { type:"application/zip" }), q.name); toast(`Downloaded the QTI file with ${q.count} questions`); },
  cvAi: a => cvAi(a),
  toCanvas: () => openCanvas()
});
document.addEventListener("input", e => {
  const el = e.target; if (!el.dataset || !el.dataset.cv || S.view !== "canvas") return;
  setPath(cvState(), el.dataset.cv, el.value); save();
  if (el.tagName === "SELECT" || el.dataset.cv === "cohortTime") canvasNav(); else cvRefresh();
});
document.addEventListener("change", async e => {
  const el = e.target; if (S.view !== "canvas" || !el.dataset) return;
  if (el.dataset.cvtick) { const C = cvState(); const t = C.ticks[el.dataset.cvtick] = C.ticks[el.dataset.cvtick] || {}; t[el.dataset.n] = el.checked; save(); return; }
  if (el.id === "cvFiles" && el.files && el.files.length) { const map = new Map([...el.files].map(f => [f.name.toLowerCase(), f])); await cvScan(false, map); render(); toast(`Read ${el.files.length} ${el.files.length === 1 ? "file" : "files"}`); }
});
async function openCanvas() {
  if (S.phase !== "dev") { toast("Canvas Build opens once Course Development has started."); return; }
  select(); S.view = "canvas"; planSave(); cvState(); renderAll(); window.scrollTo(0, 0);
  if (!CV_SCAN.at) { await cvScan(false); render(); }
}
