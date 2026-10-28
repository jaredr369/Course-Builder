# Suggest all for a module includes cohort session activities (never for Module 1).
# Run by build.py with its sub() helper in scope.

sub('''Use the template's style: "Assignment: Title", "Perusall: Article Review", "Recorded Video: Topic".\\n\\nReturn only JSON: {"topics":["..."],"practice":["Assignment: ..."],"thirdParty":["Perusall: ..."],"materials":["..."],"media":["Recorded Video: ..."]}`,''',
    '''Use the template's style: "Assignment: Title", "Perusall: Article Review", "Recorded Video: Topic".${i === 0 ? " Module 1 has no cohort session, so suggest no cohort activities." : ` Also suggest 2 or 3 active-learning activities for the 90-minute live cohort session, each written as "Short title: what students do", that connect to this module's learning activities.`}\\n\\nReturn only JSON: {"topics":["..."],"practice":["Assignment: ..."],"thirdParty":["Perusall: ..."],"materials":["..."],"media":["Recorded Video: ..."]${i === 0 ? "" : `,"cohort":["Short title: what students do"]`}}`,''')

sub('''    items: (d, i) => [["topics","Module topics"],["practice","Other Canvas assignments"],["thirdParty","Third-party tool activities"],["materials","Learning materials"],["media","Learning media"]]
      .filter(([k]) => d[k] && d[k].length)''',
    '''    items: (d, i) => [["topics","Module topics"],["practice","Other Canvas assignments"],["thirdParty","Third-party tool activities"],["materials","Learning materials"],["media","Learning media"],["cohort","Cohort session activities"]]
      .filter(([k]) => d[k] && d[k].length && (k !== "cohort" || i > 0))''')
