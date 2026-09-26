export const meta = {
  name: 'bigin-adjudicate',
  description: 'Bigin adjudication: one code-adjudicator referee per conflict/held Signal Log row of a feature (second judge for P0/security rows), verdicts applied by bigin apply',
  whenToUse: 'Code-grounded vaults (project.md grounding: codebase|both). args: {run, vault, plugin_root, feature, p0_panel}',
  phases: [
    { title: 'Worklist', detail: 'conflict + held rows with their related rows' },
    { title: 'Referee', detail: 'one code-adjudicator per row; P0/security rows get a second judge' },
    { title: 'Apply', detail: 'bigin apply on every agreed verdict' },
  ],
}

const A = args || {}
const BIN = `${A.plugin_root}/bin/bigin`
const TASKS = `_runs/${A.run}/tasks`
const VAULT = A.vault || '.'
if (!A.run || !A.plugin_root || !A.feature) throw new Error('args need {run, plugin_root, feature}')

const RUNNER = { type: 'object', properties: { ok: { type: 'boolean' }, data: { type: 'object' }, error: { type: 'string' } }, required: ['ok'] }
const TASK = { type: 'object', properties: { status: { enum: ['OK', 'BLOCKED'] }, out: { type: 'string' }, outcome: { type: 'string' }, winner: { type: 'string' }, reason: { type: 'string' } }, required: ['status'] }

function engine(label, phase, cmds) {
  return agent(`You are the Bigin engine runner. From the vault root \`${VAULT}\`, run with Bash, in order, exactly:\n` +
    cmds.map((c, i) => `${i + 1}. ${c}`).join('\n') +
    `\nStop at the first non-zero exit and return {ok:false, error:<last 15 lines>}; else {ok:true, data:<last stdout as JSON, or {text}>}.`,
    { label, phase, schema: RUNNER, model: 'haiku', effort: 'low' })
}

phase('Worklist')
const inW = `${TASKS}/${A.feature}.adjudicate.in.json`
const w = await engine(`worklist ${A.feature}`, 'Worklist', [`${BIN} worklist adjudicate ${A.feature} --out ${inW}`, `cat ${inW}`])
const rows = (w && w.ok && w.data && w.data.rows) || []
if (!rows.length) {
  log(`${A.feature}: no conflict/held rows`)
  return { feature: A.feature, rows: 0 }
}
log(`${A.feature}: ${rows.length} row(s) to referee`)

const isP0 = r => /\bP0\b|security|auth|permission|credential|payment/i.test(`${r.signal} ${r.notes}`)

const verdicts = await pipeline(
  rows,
  async (r) => {
    const out = `${TASKS}/${A.feature}.adj-${r.row}.out.json`
    const ask = (suffix, label) => agent(
      `Read your card \`${A.plugin_root}/cards/adjudicator.md\`, then the worklist \`${inW}\` (vault root \`${VAULT}\`). ` +
      `Referee ONLY Signal Log row #${r.row} (and the rows it names). Read code only at the paths the rows cite, in the repos ` +
      `the worklist lists — they are read-only. Write one adjudication JSON (schema \`adjudication\`, one verdict) to \`${out}${suffix}\`. ` +
      `Return {status, out, outcome, winner}.`,
      { label, phase: 'Referee', schema: TASK, agentType: 'bigin-ba-workflow-plugin:code-adjudicator' })
    const first = await ask('', `referee #${r.row}`)
    if (!first || first.status !== 'OK') return { row: r.row, applied: false, reason: first && first.reason }
    if (A.p0_panel && isP0(r)) {
      // second, independent judge for P0/security rows (extract-rules P0 panel); disagree → leave for a human
      const second = await ask('.second', `second judge #${r.row}`)
      if (!second || second.outcome !== first.outcome || String(second.winner || '') !== String(first.winner || '')) {
        return { row: r.row, applied: false, reason: 'P0 panel disagreed — left for a human' }
      }
    }
    return { row: r.row, out, outcome: first.outcome }
  },
  async (v) => {
    if (!v || !v.out) return v
    const a = await engine(`apply #${v.row}`, 'Apply', [`${BIN} --json ingest ${v.out} --kind adjudication --run ${A.run}`,
      `${BIN} --json apply ${v.out} --run ${A.run}`])
    return { ...v, applied: !!(a && a.ok) }
  },
)
const vs = verdicts.filter(Boolean)
return { feature: A.feature, rows: rows.length, settled: vs.filter(v => v.outcome === 'settled' && v.applied).length,
         left: vs.filter(v => !v.applied).map(v => ({ row: v.row, reason: v.reason || v.outcome })) }
