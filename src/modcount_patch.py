# Courses can have 1 to 16 modules. Getting Started is module 0 and isn't counted.
sub('const opts = [4,5,6,7,8].map(n =>', 'const opts = Array.from({ length:16 }, (_, k) => k + 1).map(n =>')
sub('<div class="field"><label for="modCount">Number of modules</label><select id="modCount" data-action-change="modcount">${opts}</select></div>',
    '<div class="field"><label for="modCount">Number of modules</label><div class="hint">1 to 16. Getting Started comes before Module 1 and isn\'t counted.</div><select id="modCount" data-action-change="modcount">${opts}</select></div>')
# the development coach no longer assumes eight modules
sub('Courses are graduate level and fully online: eight weekly modules in Canvas plus', 'Courses are graduate level and fully online: weekly modules in Canvas (the course below gives how many) plus')
sub('return `COURSE: ${courseTitle()}${P.plan.course.program ? ` (${P.plan.course.program})` : ""}', 'return `COURSE: ${courseTitle()}${P.plan.course.program ? ` (${P.plan.course.program})` : ""}, ${modCount()} weekly ${modCount() === 1 ? "module" : "modules"} after Getting Started')
