# Connecting a course folder finds documents already saved in it. A document that this copy of the tool
# hasn't saved is marked as saved when its file is there, and its text is read back from Word when the tool can.
sub('''async function dirAt(root, parts) {''', r'''let FOLDER_NOTE = "";
async function fileIn(root, parts, name) {
  try { let d = root; for (const p of parts) d = await d.getDirectoryHandle(p); return await (await d.getFileHandle(name)).getFile(); } catch (e) { return null; }
}
async function findSavedInFolder(h) {
  let found = 0, filled = 0;
  for (const it of live().filter(i => (i.status || "todo") === "todo")) {
    const outs = outputsFor(it), files = [];
    for (const o of outs) files.push(await fileIn(h, FOLDERS[o.folder], o.name));
    if (!files[0]) continue;
    const have = outs.filter((o, k) => files[k]);
    it.savedFiles = have.map(o => ({ path:FOLDERS[o.folder], name:o.name }));
    it.savedAt = Math.max(...have.map((o, k) => files[outs.indexOf(o)].lastModified));
    let read = false;
    if (typeof cvScannable === "function" && cvScannable(it)) {
      try {
        const parsed = await parseSavedDoc(it, await files[0].arrayBuffer()); delete parsed.title;
        const d = Object.assign(clone(it.data), parsed); if (parsed.settings) d.settings = Object.assign({}, it.data.settings || {}, parsed.settings);
        it.data = d; read = true; filled++;
      } catch (e) {}
    }
    it.status = "saved"; it.review = ""; it.fromFolder = !read;
    it.savedText = bareTitle(it.title) + " " + flatText(it.data);
    found++;
  }
  if (found) { save(); FOLDER_NOTE = `Found ${found} ${found === 1 ? "document" : "documents"} already saved in this folder and marked ${found === 1 ? "it" : "them"} as saved.${found - filled ? (found - filled === 1 ? " One of them is a video script or cohort session file, so edit it in Word." : ` ${found - filled} of them are video scripts or cohort session files, so edit those in Word.`) : ""}`; }
  return found;
}
async function dirAt(root, parts) {''')
sub('''  if (names.includes("02 - Planning Documents")) await tryRestore(h);
  return h;''', '''  if (names.includes("02 - Planning Documents")) await tryRestore(h);
  FOLDER_NOTE = ""; await findSavedInFolder(h);
  return h;''')
sub('$("#btnFolder").onclick = async () => { if (await chooseFolder()) { toast("Course folder connected"); render(); } };',
    '$("#btnFolder").onclick = async () => { if (await chooseFolder()) { toast(FOLDER_NOTE || "Course folder connected"); render(); } };')
sub('chooseFolder: async () => { if (await chooseFolder()) { toast("Course folder connected"); render(); } },',
    'chooseFolder: async () => { if (await chooseFolder()) { toast(FOLDER_NOTE || "Course folder connected"); render(); } },')
# a document found in the folder whose text this copy doesn't have: say so, and don't overwrite the file by accident
sub('''  ${it.status === "review" ? `<div class="flag"><b>Needs another look.</b>''', '''  ${it.fromFolder ? `<div class="flag warn"><b>This document is already in your course folder</b>, but this copy of the tool doesn't have its text. Edit it in Word. Saving here replaces the Word file with what's on this page.</div>` : ""}
  ${it.status === "review" ? `<div class="flag"><b>Needs another look.</b>''')
sub('''  if (!hasContent(it) && !confirm("This document is still mostly empty. Save it anyway?")) return;''',
    '''  if (it.fromFolder && !confirm("This replaces the Word file in your course folder with what's on this page, and the page doesn't have the Word file's text. Replace it?")) return;
  if (!it.fromFolder && !hasContent(it) && !confirm("This document is still mostly empty. Save it anyway?")) return;''')
sub('''    it.savedFiles = files.map(f => ({ path:f.path, name:f.name })); it.status = "saved"; it.review = ""; it.savedAt = Date.now();''',
    '''    it.savedFiles = files.map(f => ({ path:f.path, name:f.name })); it.status = "saved"; it.review = ""; it.savedAt = Date.now(); delete it.fromFolder;''')

# Cohort session files carry the session title, which a new copy may not have yet:
# match them by module and file type, and take the session title from the file name
sub('''    const outs = outputsFor(it), files = [];
    for (const o of outs) files.push(await fileIn(h, FOLDERS[o.folder], o.name));
    if (!files[0]) continue;''', '''    let outs = outputsFor(it), files = [];
    for (const o of outs) files.push(await fileIn(h, FOLDERS[o.folder], o.name));
    if (!files[0] && it.kind === "cohort") {
      const names = await namesIn(h, FOLDERS.cohort), m = MT(it.module);
      const plan = names.find(n => n.startsWith(`${m} Cohort Lesson Plan-`) && /\\.docx$/i.test(n));
      if (plan) {
        const title = plan.slice(`${m} Cohort Lesson Plan-`.length).replace(/\\.docx$/i, "");
        const oldTitle = it.data.sessionTitle; it.data.sessionTitle = title;
        const want = [plan, names.find(n => n === safeName(`${m} Cohort Outline-${title}`) + ".docx"), names.find(n => n === safeName(`${m} Cohort Slides-${title}`) + ".pptx")];
        outs = [{ part:"plan", folder:"cohort", name:plan }, { part:"outline", folder:"cohort", name:safeName(`${m} Cohort Outline-${title}`) + ".docx" }, { part:"slides", folder:"cohort", name:safeName(`${m} Cohort Slides-${title}`) + ".pptx" }].filter((o, k) => want[k]);
        files = []; for (const o of outs) files.push(await fileIn(h, FOLDERS[o.folder], o.name));
        if (!files[0]) it.data.sessionTitle = oldTitle;
      }
    }
    if (!files[0]) continue;''')
sub('''async function findSavedInFolder(h) {''', '''async function namesIn(root, parts) {
  const out = [];
  try { let d = root; for (const p of parts) d = await d.getDirectoryHandle(p); for await (const [n, x] of d.entries()) if (!x || x.kind !== "directory") out.push(n); } catch (e) {}
  return out;
}
async function findSavedInFolder(h) {''')
