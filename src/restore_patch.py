# Choosing a course folder offers its saved work whenever the course on screen is new, and says so when there's none
sub('''    const f = await (await d.getFileHandle(DATA_FILE)).getFile();
    const data = JSON.parse(await f.text());
    if (!data || !data.items) return;
    if (P.plan && data.id === P.id && data.updated <= P.updated) return;
    if (!confirm(`This folder has saved work for ${data.plan ? [data.plan.course.number, data.plan.course.name].join(" ") : "a course"}, last updated ${new Date(data.updated).toLocaleString()}.\\n\\nLoad it? ${P.plan ? "It will replace what's on screen for this course." : ""}`)) return;''',
'''    let f;
    try { f = await (await d.getFileHandle(DATA_FILE)).getFile(); } catch (e) { if (P.plan) toast("This folder doesn't have saved Course Development work yet. It will once you save a document."); return; }
    const data = JSON.parse(await f.text());
    if (!data || !data.items) return;
    // a course on screen with nothing drafted, saved or changed yet counts as empty, whatever its date
    const fresh = !P.plan || (!(P.items || []).some(i => i.status && i.status !== "todo") && !(P.changes || []).some(c => !c.auto) && !P.canvas);
    if (P.plan && data.id === P.id && data.updated === P.updated) return;
    const older = !fresh && data.updated < P.updated;
    if (!confirm(`This folder has saved work for ${data.plan ? [data.plan.course.number, data.plan.course.name].join(" ") : "a course"}, last updated ${new Date(data.updated).toLocaleString()}.${older ? "\\n\\nIt's older than the work on screen, which was last changed " + new Date(P.updated).toLocaleString() + "." : ""}\\n\\nLoad it? ${P.plan && !fresh ? "It will replace what's on screen for this course." : ""}`)) return;''')
