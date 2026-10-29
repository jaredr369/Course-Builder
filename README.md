# Course-Builder
This is to house a tool for IDs and Faculty to assist with course building.

## Course Creator

A single-file HTML tool for building Mays Business School Flex Online courses. It runs in the browser with no install and works in three phases.

1. **Course Planning** walks a faculty member through backward design: course and learners, desired results, evidence of learning and the learning plan. It exports the Course Planning Document as a Word file, and that file can be opened again in the tool to keep working.
2. **Course Development** turns the plan into finished documents in the Mays templates: assignments, discussions, quizzes, third-party tool activities, video scripts, instructor readings, cohort session materials and the Getting Started document. Each one is saved into the course project folder.
3. **Canvas Build** reads the saved Word documents back, including edits made in Word. It gives the instructional designer each page as DesignPLUS HTML ready to paste into Canvas, plus a settings checklist, rubrics and QTI files for quizzes.

### Using it

`index.html` at the top of the repository is always the newest build. With GitHub Pages turned on, it opens at https://jaredr369.github.io/Course-Builder/

Open the latest `dist/Course Creator 3.1.x.html` in Chrome or Edge. Those browsers can save straight into a course folder. Other browsers download each document instead. AI drafting needs a TAMU AI Chat key, entered under AI settings.

### Building

`dist/` holds every released version. Each change gets a new version number, and earlier versions are never overwritten.

To build the current version:

```
python3 build.py
```

`build.py` starts from `cc35.html` (version 3.5) and applies the patches in `src/`. The Canvas Build module is `src/canvas.js` and `src/canvas.css`, and `canvas/snips.json` holds the template markup it fills in. The version number is set at the top of `build.py`.

### Tests

The end-to-end tests in `test/` use Playwright (Python) against a local server:

```
cd dist && python3 -m http.server 8765 --bind 127.0.0.1
python3 test/flow.py
python3 test/flow_reading.py
python3 test/flow_gs.py
```

Point the `APP` address at the top of each test to the version you want to check.
