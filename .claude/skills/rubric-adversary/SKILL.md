---
name: rubric-adversary
description: Adversarial pre-submission review of the LAAO / device-related-thrombus lab (DRT_LAAO_Case3) against the professors' grading rubric — segmentation (3), LA meshes (2), simulation (2), DRT report (3), device segmentation (+1). Runs deterministic checks on the .nrrd/.stl/.bdf/.pdf deliverables, then sends one hostile "grader" subagent per criterion to hunt for every lost point, a defence pass that tries to refute each finding, and writes a dated scorecard with the fixes worth doing before the deadline. Use this whenever the user asks to review, audit, grade, red-team, stress-test or "check against the rubric / criteria" any part of the lab deliverable, asks "what would the professor take points off for", "is this ready to submit", or wants a mock grade — even if they only name one criterion (e.g. "is my mesh OK for the rubric?").
---

# Rubric adversary — LAAO lab (Case 3)

You are running a mock grading by a strict examiner who wants to take points off. The point is to find what a real grader would penalise *before* the deadline (20/11/2026 23:59), with evidence, so the student can fix what is cheap and be ready to defend the rest. A review that only confirms the work is fine is worthless; a review full of invented problems is worse. Every finding needs a file, a number or an image behind it.

The project rules in `CLAUDE.md` still apply. In particular this review is **read-only**: do not edit, move or overwrite anything in `1_segmentation/`, `2_mesh/`, `3_simulation/`, `4_postprocessing/`, `5_report/`, `6_paraview_package/` or `data/`; do not start Fluent; do not upload or describe the CT beyond anonymous metadata. Scratch files (scripts, renders, JSON) go to the session scratchpad. The only file you write in the project is the final review (step 6).

## Arguments
- No argument → full review, all five criteria.
- A criterion number or name (`2`, `mesh`, `report`, `device`…) → only that criterion; skip the subagents whose criterion is not asked and keep the defence pass.
- `quick` → no subagents: run the checks and walk the checklist in [references/rubric.md](references/rubric.md) yourself. Use this when the user wants a fast look or the budget is tight.

## Workflow

### 1. Read the project state (yourself, ~2 min)
Read `docs/agents/STATUS.md` (top entries), `docs/agents/06-submission-criteria.md`, and the READMEs of the current deliverables (`2_mesh/mv_aligned_03112026/README.md`, `4_postprocessing/run6/README.md`, `6_paraview_package/README.md`). From them, write down the **submission set**: which single file the student intends to hand in for each rubric item (LA segmentation .nrrd, surface .stl, volume .bdf, ParaView files, report PDF, device .stl). Where the notes leave this ambiguous — e.g. several LA STLs or BDFs, several device segmentations — that ambiguity is itself a finding (a grader opening the wrong file grades the wrong file), so record it rather than resolving it silently.

### 2. Run the deterministic checks
```bash
../mcp/.venv/Scripts/python.exe -W ignore .claude/skills/rubric-adversary/scripts/deliverable_checks.py --root . --case-id 3 --out <scratchpad>/checks.json
```
(~1 min; run from the project folder.) It recomputes, without trusting the project's own check files: file inventory, NRRD names vs case id, header keys that look like patient data, label volumes and stray islands, LA–device voxel overlap, STL open/non-manifold edges and closed volume, number of regions after a 30° angle separation (what Fluent's *Separate by angle* would give), BDF tetra count, negative volumes and equivolume skewness, PDF page count and where the references start. Read the JSON before spawning anyone; the numbers are the backbone of the review.

### 3. Spawn the adversaries (parallel, one message)
One `general-purpose` subagent per criterion in scope, all in the same message so they run concurrently. Build each prompt from [references/adversary-brief.md](references/adversary-brief.md) (the shared role and rules) plus that criterion's section of [references/rubric.md](references/rubric.md), the submission set from step 1, and the path to `checks.json`. Each one returns its findings as text (subagents are blocked from writing report files); save each reply yourself as `<scratchpad>/findings_c<N>.md` as it arrives, so the defence pass can read them. Criteria 1 and 5 both need the CT; that is fine, they read it independently.

Why separate agents: each one is anchored only on its own criterion and on finding faults, so it digs deeper than a single reviewer spreading attention over five topics.

### 4. Defence pass
When all adversaries are back, spawn **one** `general-purpose` subagent as the defence: give it every findings file and ask it to try to refute each finding from the evidence in the project (a number in a JSON, a sentence in `main.tex`, a figure, a slide). For each finding it returns `CONFIRMED`, `WEAKENED` (real but smaller than claimed — say why) or `REFUTED` (with the evidence). It must not invent new findings; it may note that a finding was mis-assigned to the wrong criterion. This is what keeps the review honest: adversaries are told to be harsh, so some of what they report will be overreach.

In `quick` mode, do the defence yourself: re-check each finding against its evidence before keeping it.

### 5. Score
For each criterion, start from full marks and subtract per confirmed or weakened finding, using the severity guide in [references/rubric.md](references/rubric.md). Give a *likely* score and a *harsh* score (what a grader in a bad mood gives). Refuted findings cost nothing but are listed so the student knows they were considered. Do not average away a hard-fail condition: e.g. a report over two pages, or a bare yes/no in criterion 4, is called out at the top regardless of the arithmetic.

### 6. Write the review
Save to `docs/agents/reviews/rubric_review_<DDMMYYYY>.md` (create the folder if needed; if the file exists, add `_2`, `_3`… — never overwrite). Use this structure:

```markdown
# Rubric review — DD/MM/YYYY
Submission set reviewed: <table: rubric item → file>
## Scorecard
| Criterion | Max | Likely | Harsh | Main reason |
## Blocking issues (fix before submitting)
## Findings by criterion
### 1. Segmentation
- [CONFIRMED|WEAKENED] <finding> — evidence: <file:line / number / image> — cost: <points> — fix: <what, how long>
...
## Refuted findings (no action)
## Fix plan before 20/11/2026
<ordered by points recovered per hour of work; mark which ones need Fluent or a re-run>
## Things to defend rather than fix
<limitations a grader may raise that are reasonable to keep, with the one-sentence justification to put in the report>
```

Then give the user, in chat, the scorecard and the top three fixes, and link the file. Remind them that this is a mock grade written by an AI from the rubric text; the real professors may weigh things differently, and the decisions on what to change are theirs.

Update `docs/agents/STATUS.md` with one dated line pointing to the review (the project asks every session to do so).

## What makes a good finding
- **Specific and checkable**: "`Device.seg.nrrd` has 16 connected components, 15 of them < 50 voxels (stray islands outside the frame)" — not "the device segmentation could be cleaner".
- **Tied to rubric wording**: quote the rubric line it violates. A problem the rubric does not care about (e.g. code style of the scripts) is at most a note.
- **Priced**: how many points it plausibly costs, and why.
- **Fixable or defensible**: say what would fix it and roughly how long it takes, or why it is better defended than fixed.
