"""Canvas Build with a connected course folder (real File System Access handles via the browser's private file system)."""
import json, os, sys, time, zipfile, io, base64
from playwright.sync_api import sync_playwright
APP = "http://127.0.0.1:8765/Course%20Creator%203.6.html"
ROOT = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(ROOT, "out_folder"); os.makedirs(OUT, exist_ok=True)
exec(open(os.path.join(ROOT, "flow.py")).read().split("def log")[0].split("errors = []")[1])  # RUBRIC and FILL
errors = []
def log(*a): print(*a, flush=True)
INIT = """try{localStorage.setItem('fodw-welcomed','1');localStorage.setItem('fodw-setup-skipped','1');
window.showDirectoryPicker = async () => { const r = await navigator.storage.getDirectory(); return await r.getDirectoryHandle('ISTM 643 Course Folder', { create:true }); };}catch(e){}"""
JS_READ = """async ([dir, name]) => { let d = await (await navigator.storage.getDirectory()).getDirectoryHandle('ISTM 643 Course Folder');
  for (const p of dir) d = await d.getDirectoryHandle(p); const f = await (await d.getFileHandle(name)).getFile();
  const b = new Uint8Array(await f.arrayBuffer()); let s = ''; for (const x of b) s += String.fromCharCode(x); return [btoa(s), f.lastModified]; }"""
JS_WRITE = """async ([dir, name, b64]) => { let d = await (await navigator.storage.getDirectory()).getDirectoryHandle('ISTM 643 Course Folder');
  for (const p of dir) d = await d.getDirectoryHandle(p); const fh = await d.getFileHandle(name);
  const bin = atob(b64), u = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i);
  const w = await fh.createWritable(); await w.write(u); await w.close(); return (await fh.getFile()).lastModified; }"""
JS_TREE = """async () => { const out = []; async function walk(d, p) { for await (const [n, h] of d.entries()) { if (h.kind === 'directory') await walk(h, p + n + '/'); else out.push(p + n); } }
  await walk(await (await navigator.storage.getDirectory()).getDirectoryHandle('ISTM 643 Course Folder'), ''); return out.sort(); }"""

with sync_playwright() as pw:
    b = pw.chromium.launch(); ctx = b.new_context(viewport={"width":1440, "height":1000}); ctx.add_init_script(INIT)
    def fresh():
        p = ctx.new_page(); p.on("pageerror", lambda e: errors.append(str(e))); p.on("dialog", lambda d: d.accept()); p.goto(APP); p.wait_for_timeout(900); return p
    pg = ctx.new_page(); pg.on("crash", lambda p: print("CRASH")); pg.on("close", lambda p: print("CLOSED")); pg.on("console", lambda m: m.type=="error" and print("CONSOLE", m.text)); pg.on("pageerror", lambda e: errors.append(str(e))); pg.on("dialog", lambda d: d.accept())
    pg.goto(APP); pg.wait_for_timeout(500)
    assert pg.evaluate("typeof window.showDirectoryPicker") == "function"
    pg.set_input_files("#fileInput", os.path.join(ROOT, "plan2.json")); pg.wait_for_timeout(600)
    pg.click("#phDev"); pg.wait_for_timeout(300); pg.click("[data-action=startNow]"); pg.wait_for_timeout(600)
    lib = json.loads(pg.evaluate("localStorage.getItem('fodw-course-build-v1')")); P = lib["projects"][lib["active"]]
    P["setup"]["start"] = "2027-01-11"; targets = []
    for it in P["items"]:
        k = it["kind"]
        if (it["module"] == 2 and k in ("discussion", "quiz", "activity")) or (it["module"] == 1 and k == "assignment"):
            it["data"].update(json.loads(json.dumps(FILL[k]))); targets.append(it["id"])
    pg.evaluate("v => localStorage.setItem('fodw-course-build-v1', v)", json.dumps(lib))
    pg.reload(); pg.wait_for_timeout(800)
    pg.click("[data-action=go][data-arg=start]"); pg.wait_for_timeout(300)
    pg.click("[data-action=chooseFolder]"); pg.wait_for_timeout(800)
    log("folder card:", pg.inner_text(".folder-ok").replace("\n", " ") if pg.query_selector(".folder-ok") else "NOT CONNECTED")
    pg.click("[data-action=go][data-arg=build]"); pg.wait_for_timeout(300)
    for tid in targets:
        pg.click(f"[data-action=openItem][data-arg='{tid}']"); pg.wait_for_timeout(300)
        pg.click(f"[data-action=acceptSave][data-arg='{tid}']"); pg.wait_for_timeout(900)
        log("  save:", pg.inner_text("#toast"))
        pg.click("[data-action=go][data-arg=build]"); pg.wait_for_timeout(200)
    log("folder contents:", pg.evaluate(JS_TREE))

    # faculty edits two documents in Word: the discussion overview and a quiz answer's feedback
    time.sleep(6)
    lib = json.loads(pg.evaluate("localStorage.getItem('fodw-course-build-v1')")); P = lib["projects"][lib["active"]]
    def edit(kind, old, new):
        it = next(i for i in P["items"] if i["kind"] == kind and i["module"] == 2); sf = it["savedFiles"][0]
        b64, _ = pg.evaluate(JS_READ, [sf["path"], sf["name"]])
        z = zipfile.ZipFile(io.BytesIO(base64.b64decode(b64))); files = {n: z.read(n) for n in z.namelist()}
        x = files["word/document.xml"].decode(); assert old in x, old; files["word/document.xml"] = x.replace(old, new).encode()
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z2:
            for n, v in files.items(): z2.writestr(n, v)
        pg.evaluate(JS_WRITE, [sf["path"], sf["name"], base64.b64encode(buf.getvalue()).decode()])
    edit("discussion", "Requirements fail more often than code does.", "Most failed projects trace back to requirements, not code.")
    edit("quiz", "Load time describes how the system performs, not what it does.", "Load time is a quality of the system, not a feature.")

    pg.click("#phCanvas"); pg.wait_for_timeout(1500)
    summary = pg.inner_text(".card:has(h2:text('Saved documents'))")
    log("SUMMARY:\n" + summary)
    pg.screenshot(path=os.path.join(OUT, "setup.png"), full_page=True)
    assert "EDITED" in summary and "2\nwere changed" in summary.replace("2 were", "2\nwere") or "were changed" in summary
    pg.click("[data-action=cvGo][data-arg=build]"); pg.wait_for_timeout(400)
    ents = pg.eval_on_selector_all(".cv-entry", "els => els.map(e => [e.dataset.arg, e.innerText])")
    k = next(k for k, l in ents if l.startswith("Quiz"))
    pg.click(f".cv-entry[data-arg='{k}']"); pg.wait_for_timeout(300)
    log("quiz note:", pg.inner_text(".cv-panel .flag").split("\n")[0][:200])
    pg.click("details summary:text('See the questions')"); pg.wait_for_timeout(100)
    qtext = pg.inner_text(".cv-qs"); log("uses Word feedback:", "quality of the system" in qtext)
    pg.screenshot(path=os.path.join(OUT, "quiz.png"), full_page=True)
    # Check again after bringing edits into Course Development
    pg.click("[data-action=cvAdopt]"); pg.wait_for_timeout(800)
    pg.click("[data-action=cvGo][data-arg=setup]"); pg.wait_for_timeout(300)
    pg.click("[data-action=cvScan]"); pg.wait_for_timeout(1500)
    log("AFTER ADOPT + CHECK AGAIN:\n" + pg.inner_text(".card:has(h2:text('Saved documents'))"))
    # a moved document shows as missing
    lib = json.loads(pg.evaluate("localStorage.getItem('fodw-course-build-v1')")); P = lib["projects"][lib["active"]]
    a = next(i for i in P["items"] if i["kind"] == "assignment" and i["module"] == 1)["savedFiles"][0]
    pg.evaluate("""async ([dir, name]) => { let d = await (await navigator.storage.getDirectory()).getDirectoryHandle('ISTM 643 Course Folder'); for (const p of dir) d = await d.getDirectoryHandle(p); await d.removeEntry(name); }""", [a["path"], a["name"]])
    pg.click("[data-action=cvScan]"); pg.wait_for_timeout(1500)
    log("AFTER REMOVING A FILE:\n" + pg.inner_text(".card:has(h2:text('Saved documents'))"))
    # another computer or browser: the folder name is remembered but the browser has no handle for it
    pg.evaluate("() => new Promise(r => { const q = indexedDB.deleteDatabase('course-build-generator'); q.onsuccess = q.onerror = q.onblocked = () => r(1); })")
    old = pg; old.close(); pg = fresh()
    pg.click("#phCanvas"); pg.wait_for_timeout(1200)
    log("NO HANDLE:\n" + pg.inner_text(".card:has(h2:text('Saved documents'))"))
    pg.click("[data-action=cvScan]"); pg.wait_for_timeout(500); log("toast:", pg.inner_text("#toast"))
    pg.click("[data-action=cvFolder]"); pg.wait_for_timeout(1500)
    log("RECONNECTED:\n" + pg.inner_text(".card:has(h2:text('Saved documents'))"))
    pg.screenshot(path=os.path.join(OUT, "reconnected.png"), full_page=True)
    b.close()
log("PAGE ERRORS:", errors); sys.exit(1 if errors else 0)
