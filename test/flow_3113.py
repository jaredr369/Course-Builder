"""End-to-end test of Canvas Build in Course Creator 3.6."""
import json, os, sys, time, zipfile, re, shutil
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
APP = "http://127.0.0.1:8765/Course%20Creator%203.1.13.html"
DOCS = os.path.join(ROOT, "docs"); OUT = os.path.join(ROOT, "out")
shutil.rmtree(DOCS, ignore_errors=True); shutil.rmtree(OUT, ignore_errors=True); os.makedirs(DOCS); os.makedirs(OUT)
errors = []

RUBRIC = [
  {"criterion":"Analysis of the request", "points":"40", "excellent":"Names the decision the leader needs to make and the information that supports it.", "sufficient":"Names the decision with partial support.", "minimal":"Restates the request.", "unacceptable":"Missing."},
  {"criterion":"Requirements quality", "points":"40", "excellent":"Each requirement is testable and tied to a stakeholder.", "sufficient":"Most requirements are testable.", "minimal":"Few are testable.", "unacceptable":"Missing."},
  {"criterion":"Writing", "points":"20", "excellent":"Clear and ready for an executive reader.", "sufficient":"Mostly clear.", "minimal":"Hard to follow.", "unacceptable":"Unreadable."}]
FILL = {
  "assignment": {"overview":"In this assignment, you will turn a vague leadership request into a set of requirements a project team can act on.\nYou'll practice the same move you make at work when a VP asks for \"a dashboard.\"",
    "note":"Use the case company from the interactive lesson, not your own employer.",
    "instructions":"Read the request from the CFO in the case file.\n- Interview notes are in the Files area.\n- List the decisions the CFO needs to make.\nWrite five to eight requirements.",
    "format":"Upload a Word document or PDF\n2 to 3 pages\nAPA referencing style", "submission":"Submit one file.", "rubric":RUBRIC,
    "settings":{"submission":["file_uploads"], "attempts":"limited", "attemptsNum":"2", "plagiarism":"turnitin"}},
  "discussion": {"overview":"Requirements fail more often than code does. This discussion asks you to look for that pattern in your own organization.",
    "prompt":"Describe a project at your organization where the requirements missed something important.\n- What was missed?\n- Who could have caught it?", "replies":"two", "points":"20", "rubric":RUBRIC[:2]},
  "quiz": {"focus":"the Chapter 3 reading and the elicitation video", "minutes":"30", "ppq":"2",
    "questions":[{"q":"Which requirement is nonfunctional?", "choices":["The report shows sales by region","The page loads in under two seconds","Users can export to Excel","Managers approve requests"], "correct":1, "feedback":"Load time describes how the system performs, not what it does."},
                 {"q":"What is the main purpose of stakeholder elicitation?", "choices":["To gather the information needs of people affected by the system","To choose a vendor","To write code","To test the system"], "correct":0, "feedback":"Elicitation draws out what stakeholders need before design starts."}]},
  "thirdparty": {"submission":"Complete three peer reviews by Sunday.", "rubric":[]},
  "activity": {"graded":True, "overview":"During the cohort session, your group will triage a stack of conflicting requirements.", "instructions":"Before the session, read the case.\n- During the session, sort the requirements by value and risk.\nAfter the session, one member submits the group's ranking.",
    "format":"Upload the completed template", "submission":"One submission per group.", "rubric":RUBRIC[:1],
    "settings":{"submission":["file_uploads"], "attempts":"limited", "attemptsNum":"1", "plagiarism":"none", "group":True}}
}

def log(*a): print(*a, flush=True)

with sync_playwright() as pw:
    b = pw.chromium.launch()
    ctx = b.new_context(accept_downloads=True, viewport={"width":1440, "height":1000})
    ctx.add_init_script("try{Object.defineProperty(window,'showDirectoryPicker',{value:undefined,configurable:true});localStorage.setItem('fodw-welcomed','1');localStorage.setItem('fodw-setup-skipped','1');}catch(e){}")
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.on("dialog", lambda d: d.accept())
    pg.goto(APP); pg.wait_for_timeout(500)
    pg.set_input_files("#fileInput", os.path.join(ROOT, "plan2.json")); pg.wait_for_timeout(600)
    # Canvas tab before development: should only toast
    pg.click("#phCanvas"); pg.wait_for_timeout(300)
    assert "Canvas Build opens once" in pg.inner_text("#toast"), pg.inner_text("#toast")
    pg.click("#phDev"); pg.wait_for_timeout(300)
    pg.click("[data-action=startNow]"); pg.wait_for_timeout(600)

    # fill content straight into saved work, then reload
    lib = json.loads(pg.evaluate("localStorage.getItem('fodw-course-build-v1')"))
    P = lib["projects"][lib["active"]]
    P["setup"]["start"] = "2027-01-11"; P["setup"]["instructor"] = "Jordan Rivera"
    targets = []
    for it in P["items"]:
        k = it["kind"]
        if it["module"] == 2 and k in ("discussion", "quiz", "activity"):
            it["data"].update(json.loads(json.dumps(FILL[k]))); targets.append(it["id"])
        if it["module"] == 1 and k == "assignment":
            it["data"].update(json.loads(json.dumps(FILL[k]))); targets.append(it["id"])
        if it["kind"] == "thirdparty" and it["module"] == 3:
            it["data"].update(FILL["thirdparty"]); targets.append(it["id"])
    log("items:", len(P["items"]), "targets:", len(targets), [ (i["kind"], i["module"], i["title"]) for i in P["items"] if i["id"] in targets])
    pg.evaluate("v => localStorage.setItem('fodw-course-build-v1', v)", json.dumps(lib))
    pg.reload(); pg.wait_for_timeout(700)
    pg.screenshot(path=os.path.join(OUT, "00-after-reload.png"))
    log("after reload:", pg.title(), pg.inner_text("#main")[:300])
    pg.click("[data-action=go][data-arg=build]"); pg.wait_for_timeout(300)

    # save each document through the real Accept and save button (downloads, since no folder access)
    saved = {}
    for tid in targets:
        pg.click(f"[data-action=openItem][data-arg='{tid}']"); pg.wait_for_timeout(400)
        n = 0
        with pg.expect_download() as dl:
            pg.click(f"[data-action=acceptSave][data-arg='{tid}']")
        d = dl.value; path = os.path.join(DOCS, d.suggested_filename); d.save_as(path); saved[tid] = path
        pg.wait_for_timeout(300)
        pg.click("[data-action=go][data-arg=build]"); pg.wait_for_timeout(200)
    log("saved:", [os.path.basename(p) for p in saved.values()])

    # faculty edits the discussion in Word: new overview sentence and an extra prompt line
    lib = json.loads(pg.evaluate("localStorage.getItem('fodw-course-build-v1')")); P = lib["projects"][lib["active"]]
    disc = next(i for i in P["items"] if i["kind"] == "discussion" and i["module"] == 2)
    dpath = saved[disc["id"]]
    z = zipfile.ZipFile(dpath); files = {n: z.read(n) for n in z.namelist()}; z.close()
    x = files["word/document.xml"].decode()
    assert "Requirements fail more often than code does." in x
    x = x.replace("Requirements fail more often than code does.", "Most failed projects trace back to requirements, not code.")
    files["word/document.xml"] = x.encode()
    with zipfile.ZipFile(dpath, "w", zipfile.ZIP_DEFLATED) as z2:
        for n, v in files.items(): z2.writestr(n, v)
    t = time.time() + 120; os.utime(dpath, (t, t))

    # Canvas Build
    pg.click("#phCanvas"); pg.wait_for_timeout(600)
    assert pg.is_visible("text=Build the course in Canvas"), "setup screen"
    pg.screenshot(path=os.path.join(OUT, "01-setup-before.png"), full_page=True)
    pg.set_input_files("#cvFiles", list(saved.values())); pg.wait_for_timeout(1200)
    summary = pg.inner_text(".card:has(h2:text('Saved documents'))")
    log("SUMMARY:\n" + summary)
    assert "EDITED" in summary
    pg.select_option("#cvDay", "4"); pg.fill("#cvTime", "6:00 p.m."); pg.wait_for_timeout(200)
    pg.screenshot(path=os.path.join(OUT, "02-setup-after.png"), full_page=True)
    pg.click("[data-action=cvGo][data-arg=build]"); pg.wait_for_timeout(500)

    entries = pg.eval_on_selector_all(".cv-entry", "els => els.map(e => [e.dataset.arg, e.innerText])")
    log("rail entries:", len(entries))
    results = {}
    for key, label in entries:
        pg.click(f".cv-entry[data-arg='{key}']"); pg.wait_for_timeout(250)
        title = pg.inner_text(".cv-title h2")
        issues = pg.inner_text("#cvChecks")
        if not pg.is_visible(".cv-code"): pg.click("[data-action=cvToggleCode]"); pg.wait_for_timeout(150)
        html = pg.input_value(".cv-code")
        results[title] = {"issues":issues, "html":html, "src":pg.inner_text(".cv-panel .flag, .cv-panel .cv-src") if pg.query_selector(".cv-panel .flag, .cv-panel .cv-src") else ""}
        pg.click("[data-action=cvToggleCode]"); pg.wait_for_timeout(100)
    json.dump(results, open(os.path.join(OUT, "results.json"), "w"), indent=1)
    for t, r in results.items():
        if r["html"].count("<div") != r["html"].count("</div>"): errors.append(f"unbalanced divs in {t}")

    # screenshots of key panels
    def shot(key_sub, name):
        k = next(k for k, l in entries if key_sub in l)
        pg.click(f".cv-entry[data-arg='{k}']"); pg.wait_for_timeout(500)
        pg.screenshot(path=os.path.join(OUT, name), full_page=True)
    shot("Discussion", "03-discussion.png")
    shot("Learning Materials", "04-materials.png")

    # Learning Materials M2: fill links and embeds, then check the issue list shrinks
    k = next(k for k, l in entries if l.startswith("Learning Materials") and k == "lm:2")
    pg.click(f".cv-entry[data-arg='{k}']"); pg.wait_for_timeout(300)
    before = pg.inner_text("#cvChecks")
    for el in pg.query_selector_all("input[data-cv^='links.']"): el.fill("https://canvas.tamu.edu/courses/1/files/2")
    for el in pg.query_selector_all("textarea[data-cv*='.embeds.']"): el.fill('<iframe src="https://www.youtube.com/embed/x" width="560" height="315"></iframe>')
    pg.wait_for_timeout(600)
    after = pg.inner_text("#cvChecks")
    log("LM2 before:\n" + before + "\nLM2 after:\n" + after)
    pg.screenshot(path=os.path.join(OUT, "05-materials-filled.png"), full_page=True)

    # quiz: QTI download
    k = next(k for k, l in entries if l.startswith("Quiz"))
    pg.click(f".cv-entry[data-arg='{k}']"); pg.wait_for_timeout(300)
    with pg.expect_download() as dl:
        pg.click("[data-action=cvQti]")
    qpath = os.path.join(OUT, dl.value.suggested_filename); dl.value.save_as(qpath)
    log("QTI:", os.path.basename(qpath))
    pg.screenshot(path=os.path.join(OUT, "06-quiz.png"), full_page=True)

    # copy HTML marks pasted; settings ticks and mark as built
    ctx.grant_permissions(["clipboard-read", "clipboard-write"])
    k = next(k for k, l in entries if l.startswith("Assignment"))
    pg.click(f".cv-entry[data-arg='{k}']"); pg.wait_for_timeout(300)
    if pg.is_enabled("#cvCopyHtml"): pg.click("#cvCopyHtml")
    else: pg.click("[data-action=cvCopyHtml][data-arg=force]")
    pg.wait_for_timeout(300)
    log("status after copy:", pg.inner_text(".cv-st"))
    for cb in pg.query_selector_all("[data-cvtick]"): cb.check()
    pg.click("[data-action=cvMark][data-arg=done]"); pg.wait_for_timeout(300)
    log("status after mark:", pg.inner_text(".cv-st"), "| nav:", pg.inner_text(".nav-note"))
    pg.screenshot(path=os.path.join(OUT, "07-assignment.png"), full_page=True)

    # adopt the Word edits
    k = next(k for k, l in entries if l.startswith("Discussion"))
    pg.click(f".cv-entry[data-arg='{k}']"); pg.wait_for_timeout(300)
    pg.click("[data-action=cvAdopt]"); pg.wait_for_timeout(1000)
    log("after adopt:", pg.inner_text(".cv-panel .cv-src"))
    lib = json.loads(pg.evaluate("localStorage.getItem('fodw-course-build-v1')")); P = lib["projects"][lib["active"]]
    disc = next(i for i in P["items"] if i["kind"] == "discussion" and i["module"] == 2)
    assert disc["data"]["overview"].startswith("Most failed projects"), disc["data"]["overview"]

    # finish screen, dev finish hand-off, and phase switching
    pg.click("[data-action=cvGo][data-arg=finish]"); pg.wait_for_timeout(300)
    pg.screenshot(path=os.path.join(OUT, "08-finish.png"), full_page=True)
    pg.click("#phDev"); pg.wait_for_timeout(300)
    pg.click("[data-action=go][data-arg=finish]"); pg.wait_for_timeout(300)
    assert pg.is_visible("text=Move on to Canvas Build")
    pg.click("[data-action=toCanvas]"); pg.wait_for_timeout(400)
    assert pg.get_attribute("#phCanvas", "aria-selected") == "true"
    pg.reload(); pg.wait_for_timeout(600)
    assert pg.get_attribute("#phCanvas", "aria-selected") == "true", "stays on Canvas Build after reload"
    pg.click("#phPlan"); pg.wait_for_timeout(300)
    log("title on plan:", pg.title())
    # narrow screen
    pg.click("#phCanvas"); pg.wait_for_timeout(300)
    pg.set_viewport_size({"width":420, "height":900}); pg.click("[data-action=cvGo][data-arg=build]"); pg.wait_for_timeout(400)
    sw = pg.evaluate("document.documentElement.scrollWidth")
    log("phone scrollWidth:", sw)
    pg.screenshot(path=os.path.join(OUT, "09-phone.png"))
    b.close()

log("PAGE ERRORS:", errors)
sys.exit(1 if errors else 0)
