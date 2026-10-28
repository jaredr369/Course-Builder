"""Interactive Reading: draft (stubbed AI), save Word, edit in Word, build the Canvas page."""
import json, os, re, sys, time, zipfile, shutil
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(ROOT, "out_reading")
shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
APP = "http://127.0.0.1:8765/Course%20Creator%203.1.5.html"
errors = []
def log(*a): print(*a, flush=True)
DRAFT = {
  "overview": "Leaders fund requirements documents they can act on.\nThis reading shows you how to write one.",
  "terms": [{"term": "Functional requirement", "definition": "What the system must do, stated so it can be tested."},
            {"term": "Nonfunctional requirement", "definition": "How well the system must perform, such as speed or security."},
            {"term": "Stakeholder", "definition": "Anyone whose work the system changes."}],
  "topics": [
    {"heading": "Start With the Decision", "body": "Every request hides a decision.\n## Ask what changes\n- Who acts on the report?\n- What do they do next?",
     "video": "Finding the Decision Behind the Request", "check": "What should you identify first?",
     "checkChoices": "The database schema\n* The decision the leader needs to make\nThe report layout\nThe vendor", "checkWhy": "Requirements follow from the decision."},
    {"heading": "Write Testable Requirements", "body": "A requirement you can't test is a wish.", "video": "", "check": "", "checkChoices": "", "checkWhy": ""}],
  "conclusion": "Start with the decision, then write requirements someone can test.",
  "references": "Wiegers, K., & Beatty, J. (2013). Software requirements (3rd ed.). Microsoft Press."
}
with sync_playwright() as pw:
    b = pw.chromium.launch(); ctx = b.new_context(accept_downloads=True, viewport={"width":1440, "height":1000})
    ctx.add_init_script("""try{Object.defineProperty(window,'showDirectoryPicker',{value:undefined,configurable:true});
      localStorage.setItem('fodw-welcomed','1');localStorage.setItem('fodw-setup-skipped','1');
      localStorage.setItem('fodw-ai-settings-v1', JSON.stringify({provider:'tamu', apiKey:'sk-test'}));}catch(e){}""")
    pg = ctx.new_page(); pg.on("pageerror", lambda e: errors.append(str(e))); pg.on("dialog", lambda d: d.accept())
    pg.goto(APP); pg.wait_for_timeout(500)
    pg.evaluate("d => { window.callClaude = async () => JSON.stringify(d); }", DRAFT)
    pg.set_input_files("#fileInput", os.path.join(ROOT, "plan2.json")); pg.wait_for_timeout(500)
    pg.click("#phDev"); pg.wait_for_timeout(200); pg.click("[data-action=startNow]"); pg.wait_for_timeout(500)
    pg.click("[data-action=go][data-arg=build]"); pg.wait_for_timeout(300)
    lib = json.loads(pg.evaluate("localStorage.getItem('fodw-course-build-v1')")); P = lib["projects"][lib["active"]]
    rd = next(i for i in P["items"] if i["kind"] == "reading"); log("reading item:", rd["module"], rd["title"])
    pg.click(f"[data-action=openItem][data-arg='{rd['id']}']"); pg.wait_for_timeout(400)
    log("editor sections:", [t for t in pg.eval_on_selector_all("#fields .section-title", "e=>e.map(x=>x.textContent)")])
    pg.click("[data-action=aiDraft]"); pg.wait_for_timeout(800)
    n_terms = len(pg.query_selector_all("[data-path^='data.terms.'][data-path$='.term']"))
    log("after AI draft: terms", n_terms, "| section 1 check:", pg.input_value("[data-path='data.topics.0.check']"), "| video:", pg.input_value("[data-path='data.topics.0.video']"))
    log("preview has knowledge check:", "Knowledge Check" in pg.inner_text("#preview"), "| key terms:", "Key Terms" in pg.inner_text("#preview"))
    pg.screenshot(path=os.path.join(OUT, "01-editor.png"), full_page=True)
    # add a term by hand to test the list button
    pg.click("[data-action=listAdd][data-arg='data.terms']"); pg.wait_for_timeout(300)
    pg.fill("[data-path='data.terms.3.term']", "Scope creep"); pg.fill("[data-path='data.terms.3.definition']", "Requirements that grow after work starts."); pg.wait_for_timeout(400)
    with pg.expect_download() as dl:
        pg.click(f"[data-action=acceptSave][data-arg='{rd['id']}']")
    path = os.path.join(OUT, dl.value.suggested_filename); dl.value.save_as(path); log("saved:", os.path.basename(path))
    x = zipfile.ZipFile(path).read("word/document.xml").decode()
    paras = []
    for p in re.findall(r"<w:p[ >].*?</w:p>", x, re.S):
        st = re.search(r'<w:pStyle w:val="([^"]+)"', p); t = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p))
        if t.strip(): paras.append(f"[{st.group(1) if st else ''}] {t}")
    log("WORD DOC:\n  " + "\n  ".join(paras))
    # faculty edits in Word: a definition, the correct answer, and a leftover AI citation
    time.sleep(1)
    z = zipfile.ZipFile(path); files = {n: z.read(n) for n in z.namelist()}; z.close()
    x = x.replace("Anyone whose work the system changes.", "Anyone whose work or decisions the system changes.")
    x = x.replace("A requirement you can&apos;t test is a wish.", "A requirement you can&apos;t test is a wish [cite: 8].").replace("A requirement you can't test is a wish.", "A requirement you can't test is a wish [cite: 8].")
    assert "[cite: 8]" in x
    files["word/document.xml"] = x.encode()
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z2:
        for n, v in files.items(): z2.writestr(n, v)
    t = time.time() + 120; os.utime(path, (t, t))
    # Canvas Build
    pg.click("#phCanvas"); pg.wait_for_timeout(500)
    pg.set_input_files("#cvFiles", [path]); pg.wait_for_timeout(1000)
    log("SUMMARY:", " | ".join(l for l in pg.inner_text(".card:has(h2:text('Saved documents'))").split("\n") if l.strip())[:600])
    pg.click("[data-action=cvGo][data-arg=build]"); pg.wait_for_timeout(400)
    rail = pg.eval_on_selector_all(".cv-mod:nth-child(2) .cv-entry, .cv-mod:nth-child(2) .cv-hdr", "e=>e.map(x=>x.innerText.replace(/\\n/g,' '))")
    log("MODULE 2 RAIL:", rail)
    pg.click(f".cv-entry[data-arg='{rd['id']}']"); pg.wait_for_timeout(400)
    log("PANEL NOTE:", pg.inner_text(".cv-panel .flag").split("\n")[0][:220])
    log("STEPS:", pg.inner_text(".cv-how"))
    log("ISSUES:", pg.inner_text("#cvChecks"))
    log("copy enabled:", pg.is_enabled("#cvCopyHtml"))
    pg.screenshot(path=os.path.join(OUT, "02-panel.png"), full_page=True)
    pg.click("[data-action=cvToggleCode]"); pg.wait_for_timeout(200)
    html = pg.input_value(".cv-code"); open(os.path.join(OUT, "reading.html"), "w").write(html)
    log("tabs:", re.findall(r'<h3 class="dp-panel-heading[^"]*">([^<]*)', html))
    log("flip cards:", html.count('class="dp-flip-card '), "| knowledge checks:", html.count("<summary>Show answer</summary>"), "| video boxes:", html.count("[Video Placeholder"), "| divs balanced:", html.count("<div") == html.count("</div>"))
    log("edited definition used:", "work or decisions" in html, "| answer:", re.search(r"<em>Correct: ([^<]*)</em>", html).group(1))
    # adopt the Word edits; settings checklist must not appear for a page
    log("settings card shown:", pg.query_selector("text=Settings checklist") is not None)
    pg.click("[data-action=cvToggleCode]"); pg.wait_for_timeout(200)
    pg.click("[data-action=cvAdopt]"); pg.wait_for_timeout(800)
    lib = json.loads(pg.evaluate("localStorage.getItem('fodw-course-build-v1')")); P = lib["projects"][lib["active"]]
    d = next(i for i in P["items"] if i["id"] == rd["id"])["data"]
    log("after adopt: term =", d["terms"][2]["definition"], "| body:", d["topics"][1]["body"], "| choices:", d["topics"][0]["checkChoices"].split("\n")[1])
    # mark built works without the settings prompt
    pg.click("[data-action=cvMark][data-arg=done]"); pg.wait_for_timeout(300); log("status:", pg.inner_text(".cv-st"))
    # Learning Materials M2 now links to the Interactive Reading page
    pg.click(".cv-entry[data-arg='lm:2']"); pg.wait_for_timeout(300)
    log("LM link field:", pg.inner_text("label:has-text('Interactive Reading page')"))
    b.close()
log("PAGE ERRORS:", errors); sys.exit(1 if errors else 0)
