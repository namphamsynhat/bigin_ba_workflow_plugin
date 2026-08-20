# PRD engines, and driving BMAD's create-PRD workflow headlessly

Read at Stage 1. Covers: which engine to use, what "headless" means for a workflow built to halt,
the step→vault-source map, what BMAD output to discard, and what to report when no engine exists.

## Engine detection

Check in order; use the first that answers.

| # | Engine | Detect | Use it for |
|---|---|---|---|
| 1 | **BMAD create-PRD** | a `bmad-create-prd` skill in this session's skill list, **or** `_bmad/` exists in the repo (its step files then live under `.claude/skills/bmad-create-prd/steps-c/`) | its 13-step elicitation checklist and its PRD quality bar |
| 2 | **another PRD/PM plugin** | a skill whose description covers product requirements documents | the same way — checklist in, `{template_prd}` out |
| 3 | **built-in** | always available | the method in `{prd_stages_dir}` alone |

Stamp `engine:` with what actually ran: `bmad`, the plugin's skill name, or `built-in`.

**No engine 1 or 2 → run the built-in method and report the install command in the closeout.** Never
halt to ask; this skill is headless and the built-in method is complete on its own:

```text
BMAD is not installed. Its PRD workflow adds a 13-step elicitation checklist:
    npx bmad-method install        (then re-run /bigin-generate-prd to use it)
This run used the built-in method — the PRD is complete either way.
```

## What "headless" means here

BMAD's workflow is built to halt. Its step files say, in every file:

```text
🛑 NEVER generate content without user input
📋 YOU ARE A FACILITATOR, not a content generator
⏸️ ALWAYS halt at menus and wait for user input
🚫 FORBIDDEN to load next step until user selects 'C'
```

Those rules exist because BMAD has exactly one source of truth: the human in the chair. **This vault
has another one** — approved use cases, business rules, entities, pain points, a design, and an
intake trail, all of which already went through a human gate at `/approve-uc`. Headless mode
substitutes that trail for the chair:

```text
BMAD's model      facilitator ⟷ human            → content
this skill        facilitator ⟷ the vault        → content, and a question when the vault is silent
```

Two rules keep the substitution honest. They are not optional — without them this is a content
generator wearing a checklist:

```text
H1  The vault answers, or nobody does. Never answer a BMAD step from your own product judgment.
    A step whose answer is not in the artifacts produces "not stated" plus an entry in § 11 Open
    Business Decisions — which is exactly what the human would have been asked.
H2  Never select 'A' or 'P' on BMAD's menus, and never let a step's facilitation prose reach the
    user as a question. Auto-continue. The one thing a halt would buy — a human's answer — is
    already unavailable in an unattended run, and asking would break every caller.
```

H1 is what makes this safe to run unattended. A BMAD step asking "what makes this product special?"
against a vault that never recorded a differentiator must produce a question, not a plausible
paragraph — the paragraph is indistinguishable from a client's own words once it is in the document.

## Driving the workflow

BMAD's activation and step-file protocol, adapted:

| BMAD activation step | Headless behaviour |
|---|---|
| resolve `customize.toml` → `workflow` block | Read it if present. Honour `persistent_facts` (a `file:` entry is real project context worth loading). Ignore `activation_steps_*` that expect a human. |
| load `_bmad/bmm/config.yaml` | Read if present, for `document_output_language` only. Absent → the vault's own language and `{project_file}`. |
| greet `{user_name}` | Skip. No greeting in a headless run. |
| `outputFile = {planning_artifacts}/prd.md` | **Override.** The output is `{prd_dir}/PRD-<NNN> <Feature>.md`, one per feature. |
| step files, one at a time, `stepsCompleted` in frontmatter | Use each step as a checklist. **Do not** write `stepsCompleted`, `inputDocuments`, or `workflowType` into our frontmatter — `{template_prd}`'s schema is what Stage 5 verifies. |

**Never copy BMAD's `templates/prd-template.md`.** It is a product-level shell with its own
frontmatter. `{template_prd}` is this vault's schema, and Stage 5's checks parse it.

## Step → vault source map

BMAD's 13 steps, answered from the vault. Left column is BMAD's; right column is where the answer
actually lives and which PRD section it lands in.

| BMAD step | Answer it from | Lands in |
|---|---|---|
| 01 init — discover input documents | Stage 1's work-list: the folded UCs, their BRs/entities/pain points, the UX spec, `{project_file}`. This **replaces** BMAD's `docs/**` discovery and its "confirm with the user" halt | frontmatter `sources:`, `uc:` |
| 02 discovery — project type, domain, greenfield/brownfield | `{project_file}` (product, new vs ongoing), the `FEATURES.md` row's Status (`built` ⇒ brownfield/CR) | § 1, and `chain:` |
| 02b vision — what makes this special | `{project_file}`'s proposal framing, plus each UC's § 1 Business Need. **Silent → "not stated"**, never invented (H1) | § 1 |
| 02c executive summary | Stage 2's § 1 assembly | § 1 |
| 03 success criteria | UC § 1 Business Need + `{pain_points_file}` + any stated metric. No measure stated → § 11 | § 3 |
| 04 user journeys | UC § 1 actors + § 2 flows. The vault's journeys are already written — do not re-narrate them, translate them | § 4, § 6 |
| 05 domain requirements (complex domains only) | a folded UC's `## 6 Special Requirements` and any compliance `BR-###`. Nothing there → skip the step | § 12, § 7 |
| 06 innovation (optional) | **Usually skip.** Only if an intake actually claims novelty. Never manufacture an innovation section | § 1 |
| 07 project-type deep dive | The design's `Platform` (`{ux_dir}` § 1) for channel; otherwise skip — its CSV drives *technical* requirements, which P1 excludes | § 12 or nothing |
| 08 scoping | Approved vs pending (Stage 1's read) is the scope boundary, already decided by `/approve-uc`. **Honour BMAD's own warning here**: never invent phasing, never de-scope what a source included | § 10 |
| 09 functional requirements | § 5 capabilities, one per folded UC — BMAD's "capability contract", worded as business capability, not `FR-###` lines | § 5 |
| 10 non-functional requirements | Only what a UC's `## 6` states. This vault has no NFR artifact, so an unstated NFR stays unstated — do not run BMAD's NFR taxonomy as a questionnaire | § 12 |
| 11 polish | Real and worth running: read the whole file, remove the duplication that progressive appends create, keep every `## Level 2` heading | all |
| 12 complete | Stage 5, not BMAD's completion step. Ignore its status-file writes and its "offer validation workflow" menu | — |

Steps 05, 06, 07, and 10 are the ones that most often produce invented content, because BMAD asks
them expecting a human with opinions. Skipping a step the vault cannot answer is the correct
outcome, and worth one line in the report.

## If BMAD's validate-PRD skill is installed

`bmad-validate-prd` is a separate skill and a useful second opinion, but it validates against BMAD's
own PRD shape — not `{template_prd}`. Do not run it as a gate: Stage 5's eight checks are the gate.
Mention in the closeout that it exists, so a human can run it by choice.

## What never comes from BMAD

```text
✗ its output path            {planning_artifacts}/prd.md — we write per-feature files
✗ its template + frontmatter stepsCompleted / inputDocuments / workflowType
✗ its halts                  every A/P/C menu is auto-continued  (H2)
✗ its facilitation voice      a "let's explore what makes this special" line in the document itself
✗ its technical sections      project-type and NFR taxonomies that P1 excludes
✓ its checklist               what a complete PRD covers, and in what order
✓ its quality bar             dense, precise, zero-fluff, no filler
✓ its polish pass             step 11, on the finished document
```
