# Course Development Step 4 checks off when the Finish list is done (CHECK items don't block it)
sub('checks:P.plan && issueCount() === 0, finish:false };', '''checks:P.plan && issueCount() === 0, finish:devFinishDone() };''')
sub('function renderNav() {\n  const cur = P.view.screen === "item" ? "build" : P.view.screen;', '''function devFinishDone() {
  if (!P.plan) return false;
  const all = live(), userChanges = P.changes.filter(c => !c.auto).length;
  return all.length > 0 && all.every(i => i.status === "saved") && !runChecks().some(c => c.level === "gap") && (!userChanges || !!P.logSaved);
}
function renderNav() {
  const cur = P.view.screen === "item" ? "build" : P.view.screen;''')
