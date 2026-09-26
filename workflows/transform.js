export const meta = {
  name: 'bigin-transform',
  description: 'Bigin transform: per feature route (uc-router A) → mint → draft change sets (uc-router B) → bigin apply → adjudicate (code-grounded) → hub refresh + coverage',
  whenToUse: 'Called by /bigin-transform-signal or /bigin-run for one or more feature slugs. args: {run, vault, plugin_root, features: [slug], rows?: {slug: [row#]}, grounding, max_agents}',
  phases: [
    { title: 'Route', detail: 'worklist + uc-router Phase A per feature' },
    { title: 'Draft', detail: 'mint new UCs, uc-router Phase B → change sets' },
    { title: 'Apply', detail: 'bigin ingest + apply (one write per artifact)' },
    { title: 'Adjudicate', detail: 'code-adjudicator per conflict/held row (code-grounded vaults only)' },
    { title: 'Close', detail: 'hub refresh, coverage, lint' },
  ],
}

// ---------------------------------------------------------------------------------------------
// Orchestration lives HERE, not in the coordinator's context (restructure plan Phase 3).
// Workflow scripts have no shell, so every engine step runs through a cheap "engine runner" agent
// that executes exactly the given bin/bigin commands and returns their result as JSON.
// Judgement agents (uc-router, code-adjudicator) read their card + a compact .in.json and write
// one .out.json; the engine validates it. Nothing here reads a transcript or a prose report.
// ---------------------------------------------------------------------------------------------

const A = args || {}
const RUN = A.run
const VAULT = A.vault || '.'
const BIN = `${A.plugin_root}/bin/bigin`
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

// one engine step: run commands in order, stop at the first non-zero exit; `data` = parsed stdout
// of the LAST command when it printed JSON (every command below uses --json where it matters)
function engine(label, phase, cmds) {
  const list = cmds.map((c, i) => `${i + 1}. ${c}`).join('\n')
  return agent(
    `You are the Bigin engine runner. From the vault root \`${VAULT}\`, run these shell commands in order with Bash, ` +
    `exactly as written, and nothing else — no reading files, no edits, no retries except once on "changed on disk".\n${list}\n` +
    `Stop at the first command that exits non-zero and return {ok:false, error:<its last 15 lines>}. ` +
    `Otherwise return {ok:true, data:<the last command's stdout parsed as JSON, or {text:<stdout>} if it is not JSON>}.`,
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

async function ingestOrRetry(file, kind, agentType, card, input, label, phase) {
  let r = await engine(`ingest ${label}`, phase, [`${BIN} --json ingest ${file} --kind ${kind} --run ${RUN}`])
  if (r && r.ok && r.data && r.data.ok !== false) return true
  // one repair round: the same judge fixes its own output against the schema errors
  const errs = (r && (r.error || JSON.stringify((r.data || {}).errors || []))) || 'unknown'
  await judge(agentType, card, input, file, `${label} (repair)`, phase,
    `Your previous ${file} failed schema validation: ${errs.slice(0, 1500)}. Rewrite it so it validates.`)
  r = await engine(`ingest ${label} #2`, phase, [`${BIN} --json ingest ${file} --kind ${kind} --run ${RUN}`])
  return !!(r && r.ok && r.data && r.data.ok !== false)
}

// resume: features whose close step already recorded ok in results.jsonl are skipped
const doneR = await engine('run: done tasks', 'Route', [`${BIN} run done ${RUN}`])
const done = new Set(((doneR && doneR.data && doneR.data.text) || '').split('\n'))
const todo = A.features.filter(f => !done.has(`close:${f}`))
if (todo.length < A.features.length) log(`resume: skipping ${A.features.length - todo.length} finished feature(s)`)

const results = await pipeline(
  todo,
  // 1 — worklist + Phase A
  async (slug) => {
    const inA = `${TASKS}/${slug}.route.in.json`
    const rowsArg = A.rows && A.rows[slug] ? ` --rows ${A.rows[slug].join(',')}` : ''  // Stage 2's qualified rows
    const w = await engine(`worklist ${slug}`, 'Route', [`${BIN} worklist route ${slug}${rowsArg} --out ${inA}`,
      `${BIN} --json run record ${RUN} --task worklist:${slug} --status ok`])
    if (!w || !w.ok) return { slug, stage: 'worklist', error: w && w.error }
    const outA = `${TASKS}/${slug}.route.out.json`
    const r = await judge('bigin-ba-workflow-plugin:uc-router', 'router.md', inA, outA, `route ${slug}`, 'Route',
      'This is PHASE A: output schema `route` (lib/bigin/schema/route.json). Route every row/clause; propose new UCs only as `new` entries with a key.')
    if (!r || r.status !== 'OK') return { slug, stage: 'route', error: r && r.reason }
    const ok = await ingestOrRetry(outA, 'route', 'bigin-ba-workflow-plugin:uc-router', 'router.md', inA, `route ${slug}`, 'Route')
    return ok ? { slug, inA, outA } : { slug, stage: 'route-ingest', error: 'route.json invalid after one repair' }
  },
  // 2 — mint (engine, locked) + Phase B
  async (s) => {
    if (!s || s.error) return s
    const m = await engine(`mint ${s.slug}`, 'Draft', [`${BIN} --json mint route --spec ${s.outA}`])
    if (!m || !m.ok) return { ...s, stage: 'mint', error: m && m.error }
    const outB = `${TASKS}/${s.slug}.changesets.out.json`
    const minted = s.outA.replace(/\.json$/, '.minted.json')
    const r = await judge('bigin-ba-workflow-plugin:uc-router', 'router.md', s.inA, outB, `draft ${s.slug}`, 'Draft',
      `This is PHASE B: your Phase A routing is \`${s.outA}\`, minted ids for its new UCs are \`${minted}\` (key → UC id; ` +
      `absent file = nothing minted). Output schema \`changesets\`: every qualified row becomes final-text change sets with ` +
      `trace {int, note_rows, hub, hub_rows, xr?}; use anchors (ref + sha) exactly as the worklist shows them.`)
    if (!r || r.status !== 'OK') return { ...s, stage: 'draft', error: r && r.reason }
    const ok = await ingestOrRetry(outB, 'changesets', 'bigin-ba-workflow-plugin:uc-router', 'router.md', s.inA, `draft ${s.slug}`, 'Draft')
    return ok ? { ...s, outB } : { ...s, stage: 'draft-ingest', error: 'changesets invalid after one repair' }
  },
  // 3 — apply
  async (s) => {
    if (!s || s.error) return s
    const a = await engine(`apply ${s.slug}`, 'Apply', [`${BIN} --json apply ${s.outB} --run ${RUN}`])
    if (!a || !a.ok) return { ...s, stage: 'apply', error: a && a.error }
    const d = a.data || {}
    const n = k => (Array.isArray(d[k]) ? d[k].length : 0)
    return { ...s, applied: n('applied'), already: n('already'), gated: n('gated'), drift: n('drift'),
             invalid: n('invalid') + n('rejected'), review: d.review || [] }
  },
  // 4 — adjudicate (code-grounded only): one referee per conflict/held row, verdicts applied by the engine
  async (s) => {
    if (!s || s.error || !CODE) return s
    const res = await workflow({ scriptPath: `${A.plugin_root}/workflows/adjudicate.js` },
      { run: RUN, vault: VAULT, plugin_root: A.plugin_root, feature: s.slug, p0_panel: A.p0_panel !== false })
    return { ...s, adjudicated: res }
  },
  // 5 — close: derived tables, coverage, record
  async (s) => {
    if (!s || s.error) {
      if (s) await engine(`record ${s.slug}`, 'Close', [`${BIN} run record ${RUN} --task close:${s.slug} --status failed --note "${(s.stage || '')}"`])
      return s
    }
    const c = await engine(`close ${s.slug}`, 'Close', [
      `${BIN} hub refresh ${s.slug}`,
      `${BIN} run record ${RUN} --task close:${s.slug} --status ok`,
      `${BIN} --json coverage --stage transform || true`])
    return { ...s, coverage: c && c.data ? { missing: (c.data.missing || []).length, parked: c.data.parked } : null }
  },
)

const lint = await engine('lint --full', 'Close', [`${BIN} lint --full || true`])
const out = results.filter(Boolean)
return {
  run: RUN,
  features: out.map(r => ({ feature: r.slug, error: r.error || null, stage: r.error ? r.stage : 'done',
    applied: r.applied || 0, gated: r.gated || 0, drift: r.drift || 0, invalid: r.invalid || 0,
    review: r.review || [], coverage: r.coverage || null, adjudicated: r.adjudicated || null })),
  lint: lint && lint.data ? (lint.data.text || '').split('\n')[0] : 'not run',
  next: `bigin run summary ${RUN}`,
}
