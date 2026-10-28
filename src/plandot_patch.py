# Download course plan button: a green dot when the current plan has been downloaded, red when it hasn't
# or when the plan changed after the last download. Only the plan's content counts, not where you are in it.
sub('<button id="btnSave" title="Download your plan as a Word document. You can open it here later to keep working.">Download course plan</button>',
    '<button id="btnSave" title="Download your plan as a Word document. You can open it here later to keep working."><span class="ai-dot" id="planDot"></span>Download course plan</button>')
sub('function saveNow() { clearTimeout(saveTimer); LIB.plans[S.id]', r'''const planSig = s => JSON.stringify([s.course, s.learners, s.description, s.plos, s.vision, s.clos, s.assessments, s.modules]);
function updatePlanDot() {
  const dot = document.getElementById("planDot"), btn = document.getElementById("btnSave"); if (!dot || !btn || !S) return;
  const ok = !!S.exportedSig && S.exportedSig === planSig(S);
  dot.classList.toggle("on", ok);
  btn.title = ok ? "Downloaded: this version of the plan is saved as a Word document. Click to download it again."
    : S.exportedSig ? "Not downloaded: the plan has changed since your last download. Click to download the current version."
    : "Not downloaded: the plan isn't saved as a Word document yet. Click to download it. You can open the file here later to keep working.";
}
function saveNow() { updatePlanDot(); clearTimeout(saveTimer); LIB.plans[S.id]''')
sub('saveTimer = setTimeout(writeLib, 300);', 'saveTimer = setTimeout(() => { writeLib(); updatePlanDot(); }, 300);')
sub('''  const was = S.exported; S.exported = true; // recorded inside the file too, so reopening it keeps the check''',
    '''  const was = S.exported, wasSig = S.exportedSig; S.exported = true; S.exportedSig = planSig(S); // recorded inside the file too, so reopening it keeps the check''')
sub('''  } catch (e) { S.exported = was; console.error(e);''', '''  } catch (e) { S.exported = was; S.exportedSig = wasSig; updatePlanDot(); console.error(e);''')
sub('$("#btnSave").onclick = () => saveFile();', '$("#btnSave").onclick = () => saveFile();\nupdatePlanDot();')
sub('$("#courseMenuBtn").title = Object.keys(LIB.plans).length > 1', 'updatePlanDot(); $("#courseMenuBtn").title = Object.keys(LIB.plans).length > 1')

# downloading the plan from Course Development or Canvas Build leaves that phase's sidebar alone
sub('function refreshFinish() { renderNav();', 'function refreshFinish() { if (phaseOf() !== "plan") return; renderNav();')

# AI settings: the same status wording on hover
sub('function updateAiDot() { $("#aiDot").classList.toggle("on", aiReady()); }', r'''function updateAiDot() {
  const on = aiReady(), prov = getSettings().provider === "bedrock" ? "AWS Bedrock" : "TAMU AI Chat";
  $("#aiDot").classList.toggle("on", on);
  $("#btnSettings").title = on ? `Connected: AI drafting and suggestions use ${prov}. Click to change AI settings.` : "Not connected: AI drafting and suggestions are off. Click to add your TAMU AI Chat key.";
}''')
