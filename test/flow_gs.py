"""Getting Started in 3.1.15: planning placement, the GS document (draft, save, edit in Word), Canvas Build pages, migration."""
import json, os, re, sys, time, zipfile, shutil, io
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(ROOT, "out_gs")
shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
NEW = "http://127.0.0.1:8765/Course%20Creator%203.1.15.html"
OLD = "http://127.0.0.1:8765/Course%20Creator%203.1.14.html"
errors = []; fails = []
def log(*a): print(*a, flush=True)
def check(ok, label):
    log(("PASS " if ok else "FAIL ") + label)
    if not ok: fails.append(label)

plan = json.load(open(os.path.join(ROOT, "plan2.json")))
plan["assessments"].append({"id":"gsact1", "title":"Assignment: Professional Goals Statement", "type":"canvas", "tool":"", "module":"0", "clos":[plan["clos"][0]["id"]], "notes":"", "context":"Students set goals for the program."})
PLAN = os.path.join(OUT, "plan_gs.json"); json.dump(plan, open(PLAN, "w"))

DRAFT = {"welcome":"This course shows you how leaders turn business questions into information systems.\nYou'll work through eight modules, with live cohort sessions from Module 2 on.",
  "instructorIntro":"I spent twelve years running IT planning at a regional bank before I came to Mays.",
  "introPrompt":"Tell us about a time a project at work stalled because nobody agreed on what to build.",
  "questions":[{"q":f"Syllabus question {k}?", "choices":["Alpha","Bravo","Charlie","Delta"], "correct":0, "feedback":f"Because of rule {k}."} for k in range(1, 6)]}

def lib(pg):
    L = json.loads(pg.evaluate("localStorage.getItem('fodw-course-build-v1')")); return L["projects"][L["active"]]
def paras(path):
    x = zipfile.ZipFile(path).read("word/document.xml").decode(); out = []
    for p in re.findall(r"<w:p[ >].*?</w:p>", x, re.S):
        st = re.search(r'<w:pStyle w:val="([^"]+)"', p); t = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p))
        if t.strip(): out.append(f"[{st.group(1) if st else ''}] {t}")
    return x, out

with sync_playwright() as pw:
    b = pw.chromium.launch()
    init = """try{Object.defineProperty(window,'showDirectoryPicker',{value:undefined,configurable:true});
      localStorage.setItem('fodw-welcomed','1');localStorage.setItem('fodw-setup-skipped','1');
      localStorage.setItem('fodw-ai-settings-v1', JSON.stringify({provider:'tamu', apiKey:'sk-test'}));}catch(e){}"""
    ctx = b.new_context(accept_downloads=True, viewport={"width":1440, "height":1000}); ctx.add_init_script(init)
    pg = ctx.new_page(); pg.on("pageerror", lambda e: errors.append(str(e))); pg.on("dialog", lambda d: d.accept())
    pg.goto(NEW); pg.wait_for_timeout(500)
    pg.evaluate("d => { window.callClaude = async () => JSON.stringify(d); }", DRAFT)
    pg.set_input_files("#fileInput", PLAN); pg.wait_for_timeout(500)

    # planning: the activity's module menu offers Getting Started
    opts = pg.evaluate("""() => { const s = document.querySelector('#mod_gsact1'); return s ? [...s.options].map(o => [o.value, o.textContent, o.selected]) : null; }""")
    if opts is None:
        for k in range(6):
            btns = pg.query_selector_all("#steps .step-btn")
            if k < len(btns): btns[k].click(); pg.wait_for_timeout(250)
            opts = pg.evaluate("""() => { const s = document.querySelector('#mod_gsact1'); return s ? [...s.options].map(o => [o.value, o.textContent, o.selected]) : null; }""")
            if opts: break
    log("planning module menu:", opts[:3] if opts else None)
    check(bool(opts) and opts[0][0] == "0" and opts[0][1] == "Getting Started" and opts[0][2], "planning activity can be placed in Getting Started")

    # development
    pg.click("#phDev"); pg.wait_for_timeout(200); pg.click("[data-action=startNow]"); pg.wait_for_timeout(500)
    pg.click("[data-action=go][data-arg=build]"); pg.wait_for_timeout(300)
    P = lib(pg)
    gs_items = [(i["kind"], i["title"]) for i in P["items"] if i["module"] == 0]
    log("Getting Started items:", gs_items)
    check(("gettingstarted", "Getting Started") in gs_items, "GS document item exists")
    check(any(k == "video" and "Introduction" in t for k, t in gs_items), "course introduction video sits in Getting Started")
    check(any(t == "Assignment: Professional Goals Statement" for k, t in gs_items), "planned GS activity sits in Getting Started")
    check(not any(i["module"] == 1 and i["kind"] == "video" and "Introduction" in i["title"] for i in P["items"]), "Module 1 no longer holds the course introduction")
    card = pg.inner_text("#mod0"); log("GS card:", " | ".join(l for l in card.split("\n") if l.strip())[:400])
    check("Change" not in pg.inner_text("#mod0 .item-row:has(.k-gettingstarted)"), "GS document row has no Change button")
    pg.click("[data-action=go][data-arg=checks]"); pg.wait_for_timeout(300)
    chk = pg.inner_text(".checks"); check("course introduction" not in chk.lower(), "no missing-introduction gap")
    check("Module 0" not in pg.inner_text("#main"), "no 'Module 0' text on Alignment")
    pg.click("[data-action=go][data-arg=build]"); pg.wait_for_timeout(300)

    gs = next(i for i in P["items"] if i["kind"] == "gettingstarted")
    pg.click(f"[data-action=openItem][data-arg='{gs['id']}']"); pg.wait_for_timeout(400)
    log("eyebrow:", pg.inner_text("#main .eyebrow"))
    check("Module 0" not in pg.inner_text("#main"), "no 'Module 0' text in the GS editor")
    pg.fill("[data-path='data.hours']", "Tuesdays, 5:00 to 6:00 p.m. CT")
    pg.click("[data-action=aiDraft]"); pg.wait_for_timeout(800)
    check(pg.input_value("[data-path='data.welcome']").startswith("This course shows"), "AI draft fills the welcome message")
    check(len(pg.query_selector_all("[data-path$='.q']")) == 5, "AI draft writes 5 quiz questions")
    log("quiz count note:", pg.inner_text(".count"))
    pg.screenshot(path=os.path.join(OUT, "01-gs-editor.png"), full_page=True)
    with pg.expect_download() as dl:
        pg.click(f"[data-action=acceptSave][data-arg='{gs['id']}']")
    path = os.path.join(OUT, dl.value.suggested_filename); dl.value.save_as(path); log("saved:", os.path.basename(path))
    check(os.path.basename(path) == "GS Getting Started.docx", "file name is GS Getting Started.docx")
    x, ps = paras(path); log("WORD DOC:\n  " + "\n  ".join(ps))

    # faculty edit the Word document: a new welcome line, B becomes correct on question 1
    time.sleep(1)
    z = zipfile.ZipFile(path); files = {n: z.read(n) for n in z.namelist()}; z.close()
    x2 = x.replace("with live cohort sessions from Module 2 on.", "with live cohort sessions from Module 2 on. I look forward to meeting you.")
    x2 = re.sub(r"(A\. Alpha)</w:t>(.*?)<w:t[^>]*>\s*\(correct\)</w:t>", r"\1</w:t>\2<w:t></w:t>", x2, count=1, flags=re.S)
    x2 = x2.replace("B. Bravo</w:t>", "B. Bravo (correct)</w:t>", 1)
    check(x2 != x, "test edit applied to the Word XML")
    files["word/document.xml"] = x2.encode()
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z2:
        for n, v in files.items(): z2.writestr(n, v)
    t = time.time() + 120; os.utime(path, (t, t))

    # Canvas Build
    pg.click("#phCanvas"); pg.wait_for_timeout(500)
    pg.set_input_files("#cvFiles", [path]); pg.wait_for_timeout(1000)
    summ = pg.inner_text(".card:has(h2:text('Saved documents'))"); log("SUMMARY:", " | ".join(l for l in summ.split("\n") if l.strip())[:500])
    check("EDITED" in summ and "Getting Started document" in summ, "GS document read back and flagged as edited")
    pg.click("[data-action=cvGo][data-arg=build]"); pg.wait_for_timeout(400)
    rail = pg.eval_on_selector_all(".cv-mod:first-child .cv-entry, .cv-mod:first-child .cv-hdr, .cv-mod:first-child .cv-mod-h", "e=>e.map(x=>x.innerText.replace(/\\n/g,' '))")
    log("GS RAIL:", rail)
    def html_of(key):
        pg.click(f".cv-entry[data-arg='{key}']"); pg.wait_for_timeout(350)
        pg.click("[data-action=cvToggleCode]"); pg.wait_for_timeout(150)
        h = pg.input_value(".cv-code"); pg.click("[data-action=cvToggleCode]"); pg.wait_for_timeout(150); return h
    w = html_of("welcome"); open(os.path.join(OUT, "welcome.html"), "w").write(w)
    check("I look forward to meeting you." in w, "Welcome page uses the Word edit")
    check("Tuesdays, 5:00 to 6:00 p.m. CT" in w and "twelve years" in w, "Welcome page has office hours and instructor intro")
    log("welcome issues:", pg.inner_text("#cvChecks")[:300])
    log("welcome page text card:", pg.inner_text(".cv-gs")[:300])
    a = html_of("gs:announce"); open(os.path.join(OUT, "announce.html"), "w").write(a)
    check("[insert" not in a and "Corporate Information Planning" in a and "twelve years" in a, "announcement filled")
    check('class="inline_disabled" href="https://youtu.be' in a, "announcement YouTube link has inline_disabled")
    i = html_of("gs:intro"); open(os.path.join(OUT, "intro.html"), "w").write(i)
    check("stalled because nobody agreed" in i and "[Insert a discussion prompt" not in i, "Class Introductions carries the prompt")
    log("intro steps:", pg.inner_text(".cv-how")[:600])
    log("intro settings:", pg.inner_text(".cv-set")[:400])
    q = html_of("gs:quiz"); check("This quiz consists of <strong>5</strong>" in q, "quiz page states 5 questions")
    with pg.expect_download() as dl2:
        pg.click("[data-action=cvQti][data-arg='gs:quiz']")
    qp = os.path.join(OUT, dl2.value.suggested_filename); dl2.value.save_as(qp); log("QTI:", os.path.basename(qp))
    zq = zipfile.ZipFile(qp); names = zq.namelist(); qx = next(zq.read(n).decode() for n in names if n.endswith(".xml") and "/" in n and "meta" not in n)
    meta = next(zq.read(n).decode() for n in names if n.endswith("assessment_meta.xml"))
    check(qx.count("<item ") == 5, "QTI holds 5 questions")
    first = qx.split("<item ")[1]; ids = re.findall(r'response_label ident="(\d+)"', first); corr = re.search(r'<varequal respident="response1">(\d+)<', first).group(1)
    check(ids.index(corr) == 1, "QTI question 1 correct answer is B after the Word edit")
    check("<allowed_attempts>2</allowed_attempts>" in meta and "<time_limit>30</time_limit>" in meta and "<shuffle_answers>false</shuffle_answers>" in meta, "QTI carries template quiz settings")
    check("GS: Quiz | Syllabus Acknowledgement Quiz" in meta, "QTI title")
    log("quiz settings:", pg.inner_text(".cv-set")[:500])
    pg.click(".cv-entry[data-arg='gs:qa']"); pg.wait_for_timeout(300)
    check(pg.query_selector("#cvCopyHtml") and pg.is_enabled("#cvCopyHtml"), "General Q&A ready to copy")
    act = next(i for i in lib(pg)["items"] if i["title"] == "Assignment: Professional Goals Statement")
    pg.click(f".cv-entry[data-arg='{act['id']}']"); pg.wait_for_timeout(300)
    log("GS activity title:", pg.inner_text(".cv-title h2"), "| steps:", pg.inner_text(".cv-how")[:200])
    check(pg.inner_text(".cv-title h2").startswith("GS: Assignment |"), "GS activity titled with GS: prefix")
    check("Getting Started module" in pg.inner_text(".cv-how"), "GS activity steps name the Getting Started module")
    pg.click(".cv-entry[data-arg='gs:intro']"); pg.wait_for_timeout(300)
    pg.screenshot(path=os.path.join(OUT, "02-canvas-intro.png"), full_page=True)
    # phone width
    pg.set_viewport_size({"width":390, "height":844}); pg.wait_for_timeout(300)
    sw = pg.evaluate("document.documentElement.scrollWidth"); check(sw <= 392, f"no horizontal scroll at phone width ({sw})")
    pg.screenshot(path=os.path.join(OUT, "03-phone.png"), full_page=True)
    pg.set_viewport_size({"width":1440, "height":1000})
    # adopt the Word edits
    pg.click(".cv-entry[data-arg='welcome']"); pg.wait_for_timeout(300)
    pg.click("[data-action=cvAdopt]"); pg.wait_for_timeout(500)
    d = next(i for i in lib(pg)["items"] if i["kind"] == "gettingstarted")["data"]
    check("I look forward" in d["welcome"] and d["questions"][0]["correct"] == 1, "Word edits brought into Course Development")
    ctx.close()

    # migration: a course that started development in 3.1.14, with Welcome page text typed in Canvas Build
    ctx2 = b.new_context(accept_downloads=True, viewport={"width":1440, "height":1000}); ctx2.add_init_script(init)
    p2 = ctx2.new_page(); p2.on("pageerror", lambda e: errors.append("old/migrated: " + str(e))); p2.on("dialog", lambda d: d.accept())
    p2.goto(OLD); p2.wait_for_timeout(500)
    p2.set_input_files("#fileInput", os.path.join(ROOT, "plan2.json")); p2.wait_for_timeout(500)
    p2.click("#phDev"); p2.wait_for_timeout(200); p2.click("[data-action=startNow]"); p2.wait_for_timeout(500)
    L = json.loads(p2.evaluate("localStorage.getItem('fodw-course-build-v1')")); pr = next(x for x in L["projects"].values() if x.get("plan"))
    log("old build intro module:", [i["module"] for i in pr["items"] if i["kind"] == "video" and "Introduction" in i["title"]])
    pr["canvas"] = {"screen":"build", "sel":"welcome", "status":{}, "ticks":{}, "links":{}, "pages":{"welcome":{"welcome":"Carried over welcome.", "hours":"Mondays at noon", "courseUrl":"https://canvas.tamu.edu/courses/123"}}}
    p2.evaluate("v => localStorage.setItem('fodw-course-build-v1', v)", json.dumps(L))
    p2.goto(NEW); p2.wait_for_timeout(800)
    p2.click("#phDev"); p2.wait_for_timeout(400)
    L = json.loads(p2.evaluate("localStorage.getItem('fodw-course-build-v1')")); pr = next(x for x in L["projects"].values() if x.get("plan"))
    g = [i for i in pr["items"] if i["kind"] == "gettingstarted"]
    check(len(g) == 1, "migration adds one GS document")
    check(g and g[0]["data"]["welcome"] == "Carried over welcome." and g[0]["data"]["hours"] == "Mondays at noon", "migration carries Canvas Build welcome text into the GS document")
    check(all(i["module"] == 0 for i in pr["items"] if i["kind"] == "video" and "Course Introduction" in i["title"]), "migration moves the introduction video to Getting Started")
    p2.goto(NEW); p2.wait_for_timeout(600)
    L = json.loads(p2.evaluate("localStorage.getItem('fodw-course-build-v1')")); pr = next(x for x in L["projects"].values() if x.get("plan"))
    check(len([i for i in pr["items"] if i["kind"] == "gettingstarted"]) == 1, "reload doesn't add a second GS document")
    p2.click("#phCanvas"); p2.wait_for_timeout(600)
    p2.click("[data-action=cvGo][data-arg=build]") if p2.query_selector("[data-action=cvGo][data-arg=build]") else None; p2.wait_for_timeout(300)
    p2.click(".cv-entry[data-arg='welcome']"); p2.wait_for_timeout(300)
    p2.click("[data-action=cvToggleCode]"); p2.wait_for_timeout(150)
    wh = p2.input_value(".cv-code")
    check("Carried over welcome." in wh and "courses/123/external_tools/2042" in wh, "migrated Welcome page keeps text and course link")
    ctx2.close(); b.close()
log("PAGE ERRORS:", errors); log("FAILS:", fails)
sys.exit(1 if errors or fails else 0)
