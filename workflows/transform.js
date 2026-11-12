export const meta = {
  name: 'bigin-transform',
  description: 'Bigin transform: per feature route (uc-router A) → mint → draft change sets (uc-router B) → bigin apply → adjudicate (code-grounded) → hub refresh + coverage',
  whenToUse: 'Called by /bigin-transform-signal or /bigin-run for one or more feature slugs. args: {run, vault, plugin_root, features: [slug], rows?: {slug: [row#]}, grounding, max_agents, bin?}',
  phases: [
    { title: 'Route', detail: 'index-card worklist + uc-router Phase A per feature' },
    { title: 'Draft', detail: 'mint new UCs, full cards for the routed UCs, uc-router Phase B → change sets' },
    { title: 'Apply', detail: 'bigin ingest + apply (one write per artifact)' },
    { title: 'Adjudicate', detail: 'code-adjudicator per conflict/held row (code-grounded vaults only)' },
    { title: 'Close', detail: 'hub refresh, coverage, impact on each intake note, lint' },
  ],
}

// ---------------------------------------------------------------------------------------------
// Orchestration lives HERE, not in the coordinator's context (restructure plan Phase 3).
// Workflow scripts have no shell, so every engine step runs through a cheap "engine runner" agent
// that executes exactly the given scripts/bigin commands and returns their result as JSON.
// Judgement agents (uc-router, code-adjudicator) read their card + a compact .in.json and write
// one .out.json; the engine validates it. Nothing here reads a transcript or a prose report.
// ---------------------------------------------------------------------------------------------

const A = args || {}
const RUN = A.run
const VAULT = A.vault || '.'
// One path for every shell: sh/Git Bash run the scripts/bigin sh shim (it picks python3/python);
// cmd.exe resolves the extensionless name to scripts/bigin.cmd via PATHEXT. `args.bin` overrides.
const BIN = A.bin || `"${A.plugin_root}/scripts/bigin"`
const TASKS = `_runs/${RUN}/tasks`
const CODE = ['codebase', 'both'].includes(A.grounding || 'communication')
const MAX = A.max_agents || 6
if (!RUN || !A.plugin_root || !Array.isArray(A.features)) {
  throw new Error('args need {run, plugin_root, features: [slug]} (vault defaults to cwd)')
}

const RUNNER_SCHEMA = {
  type: 'object',
  properties: { ok: { type: 'boolean' }, data: { type: 'object' }, error: { type: 'string' } },
  required: ['ok'],
}
const TASK_SCHEMA = {
  type: 'object',
  properties: { status: { enum: ['OK', 'BLOCKED'] }, out: { type: 'string' }, counts: { type: 'object' }, reason: { type: 'string' } },
  required: ['status'],
}

// ONE runner per transition, not per command: every spawn pays a fresh agent's fixed cost to run a few
// shell lines, so each call carries everything up to the next judgement — two runners per feature
// (after Phase A, after Phase B). `pick` names the command whose stdout is the result (default: the last).
function engine(label, phase, cmds, pick) {
  const list = cmds.map((c, i) => `${i + 1}. ${c}`).join('\n')
  const k = pick || cmds.length
  return agent(
    `You are the Bigin engine runner. From the vault root \`${VAULT}\`, run these shell commands in order with Bash, ` +
    `exactly as written, and nothing else — no reading files, no edits, no retries except once on "changed on disk".\n${list}\n` +
    `Stop at the first command that exits non-zero and return {ok:false, error:<its last 15 lines>}. ` +
    `Otherwise return {ok:true, data:<the stdout of command ${k} parsed as JSON, or {text:<stdout>} if it is not JSON>}.`,
    { label, phase, schema: RUNNER_SCHEMA, model: 'haiku', effort: 'low' })
}

function judge(agentType, card, input, output, label, phase, extra) {
  return agent(
    `Read your card \`${A.plugin_root}/cards/${card}\` first, then the task input \`${input}\` (paths are vault-relative, ` +
    `vault root \`${VAULT}\`). Do exactly what the card says for this input. Write your result as JSON to \`${output}\` ` +
    `and nothing else — never edit a vault file. ${extra || ''}\nReturn {status:"OK", out:"${output}", counts:{…}} or ` +
    `{status:"BLOCKED", reason:"…"} — one line of data, no prose.`,
    { label, phase, schema: TASK_SCHEMA, agentType })
}

const ROUTER = 'bigin-ba-workflow-plugin:uc-router'
const schemaError = r => r && !r.ok && /"errors"|INVALID|not valid JSON|schema error/.test(r.error || '')

// run a transition whose first command is `ingest <file>`; a schema failure gets ONE repair round — the judge
// (`who` = {agentType, card}) fixes its own file against the errors (it is told not to re-read its inputs unless
// an error needs them). Identical in extract.js and transform.js — tests/test_workflows.py pins that.
async function ingestThen(cmds, pick, file, input, label, phase, who) {
  let r = await engine(label, phase, cmds, pick)
  if (schemaError(r)) {
    await judge(who.agentType, who.card, input, file, `${label} (repair)`, phase,
      `REPAIR: \`${file}\` — the file you wrote — failed schema validation: ${(r.error || '').slice(0, 1500)}. ` +
      `Open that file, correct only what the errors name, and write it back. Re-read the task input only if an error needs it.`)
    r = await engine(`${label} #2`, phase, cmds, pick)
    if (r) r.repaired = true
  }
  return r
}

// resume: features whose close step already recorded ok in results.jsonl are skipped
// Windows print() emits \r\n — strip so `close:slug` matches (POSIX stays \n-only).
const doneR = await engine('run: done tasks', 'Route', [`${BIN} run done ${RUN}`])
const done = new Set(((doneR && doneR.data && doneR.data.text) || '').split(/\r?\n/).map(s => s.trim()).filter(Boolean))
const todo = A.features.filter(f => !done.has(`close:${f}`))
if (todo.length < A.features.length) log(`resume: skipping ${A.features.length - todo.length} finished feature(s)`)

const rowsArg = slug => (A.rows && A.rows[slug] ? ` --rows ${A.rows[slug].join(',')}` : '')  // Stage 2's qualified rows
const inA = slug => `${TASKS}/${slug}.route.in.json`     // Phase A: index cards
const inB = slug => `${TASKS}/${slug}.draft.in.json`     // Phase B: full cards for the routed UCs only

// every Phase A worklist in one runner (`|| true`: a slug with no hub must not stop the others — its
// router then reports BLOCKED on the missing input)
if (todo.length) {
  await engine('worklists: route', 'Route', todo.map(slug => `${BIN} worklist route ${slug}${rowsArg(slug)} --phase a --out ${inA(slug)} || true`))
}

const results = await pipeline(
  todo,
  // 1 — Phase A (route on index cards), then ONE runner: validate → mint → build the Phase B worklist
  async (slug) => {
    const outA = `${TASKS}/${slug}.route.out.json`
    const r = await judge(ROUTER, 'router.md', inA(slug), outA, `route ${slug}`, 'Route',
      'This is PHASE A: output schema `route` (lib/bigin/schema/route.json). Route every row/clause; propose new UCs only as `new` entries with a key.')
    if (!r || r.status !== 'OK') return { slug, stage: 'route', error: r && r.reason }
    const m = await ingestThen([`${BIN} --json ingest ${outA} --kind route --run ${RUN}`,
      `${BIN} --json mint route --spec ${outA}`,
      `${BIN} worklist route ${slug}${rowsArg(slug)} --phase b --spec ${outA} --out ${inB(slug)}`],
      null, outA, inA(slug), `mint ${slug}`, 'Draft', { agentType: ROUTER, card: 'router.md' })
    if (!m || !m.ok) return { slug, stage: schemaError(m) ? 'route-ingest' : 'mint', error: m && m.error }
    return { slug, outA }
  },
  // 2 — Phase B (draft on full cards), then ONE runner: validate → apply (→ close, when nothing sits between)
  async (s) => {
    if (!s || s.error) return s
    const outB = `${TASKS}/${s.slug}.changesets.out.json`
    const minted = s.outA.replace(/\.json$/, '.minted.json')
    const r = await judge(ROUTER, 'router.md', inB(s.slug), outB, `draft ${s.slug}`, 'Draft',
      `This is PHASE B: your Phase A routing is \`${s.outA}\`, minted ids for its new UCs are \`${minted}\` (key → UC id; ` +
      `absent file = nothing minted). The task input now carries FULL cards (sha, open questions) for the UCs you routed to. ` +
      `Output schema \`changesets\`: every qualified row becomes final-text change sets with ` +
      `trace {int, note_rows, hub, hub_rows, xr?}; use anchors (ref + sha) exactly as the worklist shows them.`)
    if (!r || r.status !== 'OK') return { ...s, stage: 'draft', error: r && r.reason }
    const cmds = [`${BIN} --json ingest ${outB} --kind changesets --run ${RUN}`, `${BIN} --json apply ${outB} --run ${RUN}`]
    if (!CODE) cmds.push(`${BIN} hub refresh ${s.slug}`, `${BIN} run record ${RUN} --task close:${s.slug} --status ok`)
    const a = await ingestThen(cmds, 2, outB, inB(s.slug), `apply ${s.slug}`, 'Apply', { agentType: ROUTER, card: 'router.md' })
    if (!a || !a.ok) return { ...s, stage: schemaError(a) ? 'draft-ingest' : 'apply', error: a && a.error }
    const d = a.data || {}
    const n = k => (Array.isArray(d[k]) ? d[k].length : 0)
    return { ...s, outB, closed: !CODE, applied: n('applied'), already: n('already'), gated: n('gated'), drift: n('drift'),
             invalid: n('invalid') + n('rejected'), review: d.review || [], reverted: d.reverted || [], stale: d.stale || [] }
  },
  // 3 — adjudicate (code-grounded only): one referee per conflict/held row, verdicts applied by the engine;
  //     the close step then needs its own runner because adjudication sits between apply and close
  async (s) => {
    if (!s || s.error || !CODE) return s
    const res = await workflow({ scriptPath: `${VAULT}/_runs/${RUN}/workflows/adjudicate.js` },
      { run: RUN, vault: VAULT, plugin_root: A.plugin_root, feature: s.slug, p0_panel: A.p0_panel !== false })
    const c = await engine(`close ${s.slug}`, 'Close', [`${BIN} hub refresh ${s.slug}`,
      `${BIN} run record ${RUN} --task close:${s.slug} --status ok`])
    return { ...s, adjudicated: res, closed: !!(c && c.ok) }
  },
  // 4 — a failed feature is recorded so the summary names it (the only extra runner, and only on failure)
  async (s) => {
    if (s && s.error) await engine(`record ${s.slug}`, 'Close', [`${BIN} run record ${RUN} --task close:${s.slug} --status failed --note "${(s.stage || '')}"`])
    return s
  },
)

// once per run, not per feature: impact is an OUTPUT of this run (every intake note the hubs cite gets its
// ## Impact section regenerated); coverage is vault-wide; lint is the stage-boundary gate
const impact = await engine('impact', 'Close', [`${BIN} --json impact touched --write`])
const cov = await engine('coverage', 'Close', [`${BIN} --json coverage --stage transform || true`])
const lint = await engine('lint --full', 'Close', [`${BIN} lint --full || true`])
const out = results.filter(Boolean)
const coverage = cov && cov.data && !cov.data.text ? { missing: (cov.data.missing || []).length, parked: cov.data.parked } : null
return {
  run: RUN,
  features: out.map(r => ({ feature: r.slug, error: r.error || null, stage: r.error ? r.stage : 'done',
    applied: r.applied || 0, gated: r.gated || 0, drift: r.drift || 0, invalid: r.invalid || 0,
    review: r.review || [], reverted: r.reverted || [], stale: r.stale || [],
    coverage, adjudicated: r.adjudicated || null })),
  coverage,
  impact: impact && impact.ok && Array.isArray(impact.data) ? impact.data.filter(i => i.written).map(i => ({ int: i.int, ...i.summary })) : [],
  lint: lint && lint.data ? (lint.data.text || '').split(/\r?\n/)[0] : 'not run',
  next: `bigin run summary ${RUN}`,
}
