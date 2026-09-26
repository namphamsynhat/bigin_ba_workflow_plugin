export const meta = {
  name: 'bigin-extract',
  description: 'Bigin extract (communication mode): per note signal-extractor → signal-auditor when owed → bigin note write-signals; then serial signal-filer per note → bigin file apply → lint --full',
  whenToUse: 'Called by /extract-signal or /bigin-run. args: {run, vault, plugin_root, notes: [INT-###]}. Codebase-mode notes are imported by `bigin intake codebase` and never come here.',
  phases: [
    { title: 'Extract', detail: 'signal-extractor per note (line-range reads)' },
    { title: 'Audit', detail: 'signal-auditor only where the audit is owed' },
    { title: 'File', detail: 'signal-filer per note, serially; bigin file apply' },
    { title: 'Close', detail: 'lint --full, coverage' },
  ],
}

const A = args || {}
const BIN = `${A.plugin_root}/bin/bigin`
const TASKS = `_runs/${A.run}/tasks`
const VAULT = A.vault || '.'
if (!A.run || !A.plugin_root || !Array.isArray(A.notes)) throw new Error('args need {run, plugin_root, notes: [INT-###]}')

const RUNNER = { type: 'object', properties: { ok: { type: 'boolean' }, data: { type: 'object' }, error: { type: 'string' } }, required: ['ok'] }
const TASK = { type: 'object', properties: { status: { enum: ['OK', 'BLOCKED'] }, out: { type: 'string' }, audit_owed: { type: 'boolean' }, counts: { type: 'object' }, reason: { type: 'string' } }, required: ['status'] }

function engine(label, phase, cmds) {
  return agent(`You are the Bigin engine runner. From the vault root \`${VAULT}\`, run with Bash, in order, exactly:\n` +
    cmds.map((c, i) => `${i + 1}. ${c}`).join('\n') +
    `\nStop at the first non-zero exit and return {ok:false, error:<last 15 lines>}; else {ok:true, data:<last stdout as JSON, or {text}>}.`,
    { label, phase, schema: RUNNER, model: 'haiku', effort: 'low' })
}
function judge(agentType, card, input, output, label, phase, extra) {
  return agent(`Read your card \`${A.plugin_root}/cards/${card}\`, then the task input \`${input}\` (vault root \`${VAULT}\`). ` +
    `Do what the card says. Write your JSON result to \`${output}\` and nothing else. ${extra || ''} ` +
    `Return {status:"OK", out, counts, audit_owed?} or {status:"BLOCKED", reason}.`,
    { label, phase, schema: TASK, agentType })
}

const doneR = await engine('run: done tasks', 'Extract', [`${BIN} run done ${A.run}`])
const done = new Set(((doneR && doneR.data && doneR.data.text) || '').split('\n'))

const extracted = await pipeline(
  A.notes.filter(n => !done.has(`extracted:${n}`)),
  async (nid) => {
    const inE = `${TASKS}/${nid}.extract.in.json`
    const w = await engine(`worklist ${nid}`, 'Extract', [`${BIN} worklist extract ${nid} --out ${inE}`])
    if (!w || !w.ok) return { nid, error: 'worklist' }
    const outE = `${TASKS}/${nid}.signals.out.json`
    const r = await judge('bigin-ba-workflow-plugin:signal-extractor', 'extractor.md', inE, outE, `extract ${nid}`, 'Extract')
    if (!r || r.status !== 'OK') return { nid, error: r && r.reason }
    const a = await engine(`write ${nid}`, 'Extract', [`${BIN} --json ingest ${outE} --kind signals --run ${A.run}`,
      `${BIN} --json note write-signals ${outE}`])
    if (!a || !a.ok) return { nid, error: a && a.error }
    return { nid, owed: !!r.audit_owed || !!(a.data && a.data.audit_owed) }
  },
  async (s) => {
    if (!s || s.error || !s.owed) return s
    const inA = `${TASKS}/${s.nid}.audit.in.json`
    await engine(`worklist audit ${s.nid}`, 'Audit', [`${BIN} worklist audit ${s.nid} --out ${inA}`])
    const outA = `${TASKS}/${s.nid}.audit.out.json`
    const r = await judge('bigin-ba-workflow-plugin:signal-auditor', 'auditor.md', inA, outA, `audit ${s.nid}`, 'Audit')
    if (!r || r.status !== 'OK') return { ...s, error: r && r.reason }
    const a = await engine(`repair ${s.nid}`, 'Audit', [`${BIN} --json ingest ${outA} --kind audit --run ${A.run}`,
      `${BIN} --json note audit-apply ${outA}`])
    return { ...s, audited: !!(a && a.ok) }
  },
  async (s) => {
    if (s && !s.error) await engine(`record ${s.nid}`, 'Extract', [`${BIN} run record ${A.run} --task extracted:${s.nid} --status ok`])
    return s
  },
)

// filing is SERIAL by design: a later note's themes may extend a row an earlier note just filed
phase('File')
const filed = []
const toFile = A.notes.filter(n => !done.has(`filed:${n}`) && !extracted.some(e => e && e.nid === n && e.error))
for (const nid of toFile) {
  const inF = `${TASKS}/${nid}.file.in.json`
  await engine(`worklist file ${nid}`, 'File', [`${BIN} worklist file ${nid} --out ${inF}`])
  const outF = `${TASKS}/${nid}.filing.out.json`
  const r = await judge('bigin-ba-workflow-plugin:signal-filer', 'filer.md', inF, outF, `file ${nid}`, 'File')
  if (!r || r.status !== 'OK') { filed.push({ nid, error: r && r.reason }); continue }
  const a = await engine(`file apply ${nid}`, 'File', [`${BIN} --json ingest ${outF} --kind filing --run ${A.run}`,
    `${BIN} --json file apply ${outF}`, `${BIN} run record ${A.run} --task filed:${nid} --status ok`])
  filed.push({ nid, ok: !!(a && a.ok), error: a && !a.ok ? a.error : null })
}

const close = await engine('lint + coverage', 'Close', [`${BIN} lint --full || true`, `${BIN} --json coverage --stage file || true`])
return {
  run: A.run,
  extracted: extracted.filter(Boolean).map(e => ({ note: e.nid, audited: !!e.audited, error: e.error || null })),
  filed,
  coverage_missing: close && close.data && close.data.missing ? close.data.missing.length : null,
  next: `bigin run summary ${A.run}`,
}
