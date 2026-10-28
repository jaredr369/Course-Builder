"""Build Course Creator 3.7 from 3.5 plus the Canvas Build phase."""
import json, re, sys

src = open('cc35.html', encoding='utf8').read()
snips = json.load(open('canvas/snips.json'))
snips['wrap'] = re.sub(r'data-nav-class="[^"]*"', 'data-nav-class=""', snips['wrap'])
canvas_js = open('src/canvas.js', encoding='utf8').read().replace('/*__CV_SNIPS__*/{}', json.dumps(snips))
canvas_css = open('src/canvas.css', encoding='utf8').read()

def sub(old, new, count=1):
    global src
    n = src.count(old)
    if n != count:
        sys.exit(f'expected {count} match(es), found {n}: {old[:90]!r}')
    src = src.replace(old, new)

# version
sub('title="Version 3.5">3.5<', 'title="Version 3.7">3.7<')
sub('<title>Course Creator 3.5</title>', '<title>Course Creator 3.7</title>')
sub('" · Course Creator 3.5";', '" · Course Creator 3.7";')

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
sub('document.title = (ph === "dev" ? "Course Development" : "Course Planning") + " · Course Creator 3.7";',
    'document.title = (cv ? "Canvas Build" : ph === "dev" ? "Course Development" : "Course Planning") + " · Course Creator 3.7";')

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

open('dist/Course Creator 3.7.html', 'w', encoding='utf8').write(src)
print('built', len(src))
