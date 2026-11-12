export const meta = {
  name: 'bigin-extract',
  description: 'Bigin extract (communication mode): per note signal-extractor → signal-auditor when owed → bigin note write-signals; then serial signal-filer per note → bigin file apply; then intake-analyst per note → bigin note analysis-apply → lint --full',
  whenToUse: 'Called by /extract-signal or /bigin-run. args: {run, vault, plugin_root, notes: [INT-###], bin?}. Codebase-mode notes are imported by `bigin intake codebase` and never come here.',
  phases: [
    { title: 'Extract', detail: 'signal-extractor per note (line-range reads); a Why repair where `not stated` runs high' },
    { title: 'Audit', detail: 'signal-auditor only where the audit is owed' },
    { title: 'File', detail: 'signal-filer per note, serially; bigin file apply' },
    { title: 'Analyze', detail: 'intake-analyst per filed note (parallel reads, serial apply): affected UCs, conflicts, questions' },
    { title: 'Close', detail: 'lint --full, coverage' },
  ],
}

const A = args || {}
// One path for every shell: sh/Git Bash run the scripts/bigin sh shim (it picks python3/python);
// cmd.exe resolves the extensionless name to scripts/bigin.cmd via PATHEXT. `args.bin` overrides.
const BIN = A.bin || `"${A.plugin_root}/scripts/bigin"`
const TASKS = `_runs/${A.run}/tasks`
const VAULT = A.vault || '.'
if (!A.run || !A.plugin_root || !Array.isArray(A.notes)) throw new Error('args need {run, plugin_root, notes: [INT-###]}')

const RUNNER = { type: 'object', properties: { ok: { type: 'boolean' }, data: { type: 'object' }, error: { type: 'string' } }, required: ['ok'] }
const TASK = { type: 'object', properties: { status: { enum: ['OK', 'BLOCKED'] }, out: { type: 'string' }, counts: { type: 'object' }, reason: { type: 'string' } }, required: ['status'] }

// ONE runner per transition, not per command: every spawn pays a fresh agent's fixed cost to run a few
// shell lines, so each call carries everything up to the next judgement. `pick` names the command whose
// stdout is the result (default: the last one).
function engine(label, phase, cmds, pick) {
  const k = pick || cmds.length
  return agent(`You are the Bigin engine runner. From the vault root \`${VAULT}\`, run with Bash, in order, exactly:\n` +
    cmds.map((c, i) => `${i + 1}. ${c}`).join('\n') +
    `\nStop at the first non-zero exit and return {ok:false, error:<last 15 lines>}; else {ok:true, data:<the stdout of command ${k} parsed as JSON, or {text} if it is not JSON>}.`,
    { label, phase, schema: RUNNER, model: 'haiku', effort: 'low' })
}
function judge(agentType, card, input, output, label, phase, extra) {
  return agent(`Read your card \`${A.plugin_root}/cards/${card}\`, then the task input \`${input}\` (vault root \`${VAULT}\`). ` +
    `Do what the card says. Write your JSON result to \`${output}\` and nothing else. ${extra || ''} ` +
    `Return {status:"OK", out, counts} or {status:"BLOCKED", reason}.`,
    { label, phase, schema: TASK, agentType })
}
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

const EXTRACTOR = 'bigin-ba-workflow-plugin:signal-extractor'
const AUDITOR = { agentType: 'bigin-ba-workflow-plugin:signal-auditor', card: 'auditor.md' }
const FILER = { agentType: 'bigin-ba-workflow-plugin:signal-filer', card: 'filer.md' }
const ANALYST = { agentType: 'bigin-ba-workflow-plugin:intake-analyst', card: 'analyst.md' }
const XTR = { agentType: EXTRACTOR, card: 'extractor.md' }
const inOf = (nid, kind) => `${TASKS}/${nid}.${kind}.in.json`

const doneR = await engine('run: done tasks', 'Extract', [`${BIN} run done ${A.run}`])
const done = new Set(((doneR && doneR.data && doneR.data.text) || '').split(/\r?\n/).map(s => s.trim()).filter(Boolean))

// every extract worklist in one runner (`|| true`: one unreadable note must not stop the others — its
// extractor then reports BLOCKED on the missing input)
const toExtract = A.notes.filter(n => !done.has(`extracted:${n}`))
if (toExtract.length) {
  await engine('worklists: extract', 'Extract', toExtract.map(n => `${BIN} worklist extract ${n} --out ${inOf(n, 'extract')} || true`))
}

const extracted = await pipeline(
  toExtract,
  async (nid) => {
    const inE = inOf(nid, 'extract')
    const outE = `${TASKS}/${nid}.signals.out.json`
    const r = await judge(EXTRACTOR, 'extractor.md', inE, outE, `extract ${nid}`, 'Extract')
    if (!r || r.status !== 'OK') return { nid, error: r && r.reason }
    // validate + write the table + record `extracted:` (and `audit-owed:`) + build the audit input — one runner.
    // The ENGINE decides whether the audit is owed (write-signals → audit_owed, audit_reasons).
    const a = await ingestThen([`${BIN} --json ingest ${outE} --kind signals --run ${A.run}`,
      `${BIN} --json note write-signals ${outE} --run ${A.run}`,
      `${BIN} worklist audit ${nid} --out ${inOf(nid, 'audit')}`], 2, outE, inE, `write ${nid}`, 'Extract', XTR)
    if (!a || !a.ok) return { nid, error: a && a.error }
    const d = a.data || {}
    return { nid, owed: !!d.audit_owed, reasons: d.audit_reasons || [], whyRepair: d.why_repair || [],
      unverified: d.unverified || [], uncovered: d.uncovered || [] }
  },
  // `not stated` over 30%: the same extractor redoes the Why search on exactly those rows. An auditor
  // cannot make a missing reason appear, so this is not an audit trigger (2b-audit.md).
  async (s) => {
    if (!s || s.error || !s.whyRepair.length) return s
    const outR = `${TASKS}/${s.nid}.whyrepair.out.json`
    const r = await judge(EXTRACTOR, 'extractor.md', inOf(s.nid, 'extract'), outR, `why repair ${s.nid}`, 'Extract',
      `REPAIR run (\`mode: "repair"\`): rows #${s.whyRepair.join(', #')} of the note's ## Extracted signals have Why \`not stated\`. ` +
      `Redo the Why search for each (the ±20 lines around its cite). Output ONLY the rows whose Why you found, each with its \`n\`, ` +
      `unchanged type/signal/source and the new why; an empty rows list is a valid answer.`)
    if (!r || r.status !== 'OK') return { ...s, whyRepaired: false }
    const a = await engine(`why repair ${s.nid}`, 'Extract', [`${BIN} --json ingest ${outR} --kind signals --run ${A.run}`,
      `${BIN} --json note write-signals ${outR}`, `${BIN} metrics quality-add --run ${A.run} --kind repair_round:why --task ${s.nid}`])
    return { ...s, whyRepaired: !!(a && a.ok) }
  },
  // quote grounding (W1): rows whose quote the engine could not find in ## Raw, and runs of source no verified
  // quote came near. ONE round, the same extractor: fix or leave out the flagged rows, extract the unread runs
  // or return no rows. Rows with `n` are repaired in place; rows without `n` (each with a quote) are appended.
  async (s) => {
    if (!s || s.error || (!s.unverified.length && !s.uncovered.length)) return s
    const outQ = `${TASKS}/${s.nid}.quoterepair.out.json`
    const ranges = s.uncovered.map(u => `${u.src} lines ${u.lines[0]}-${u.lines[1]}`).join('; ')
    const r = await judge(EXTRACTOR, 'extractor.md', inOf(s.nid, 'extract'), outQ, `quote repair ${s.nid}`, 'Extract',
      `REPAIR run (\`mode: "repair"\`): ` +
      (s.unverified.length ? `rows #${s.unverified.join(', #')} carry a quote the engine could not find in the note's ## Raw. ` +
        `For each, output the row with its \`n\`, unchanged type/signal/source and a corrected verbatim \`quote\`; leave a row out if the source does not support it. ` : '') +
      (ranges ? `No row came from these runs of source: ${ranges}. Read exactly those lines; for each claim found output a NEW row (no \`n\`) with its \`quote\`. ` : '') +
      `An empty rows list is a valid answer. One round only.`)
    if (!r || r.status !== 'OK') return { ...s, quoteRepaired: false }
    const a = await engine(`quote repair ${s.nid}`, 'Extract', [`${BIN} --json ingest ${outQ} --kind signals --run ${A.run}`,
      `${BIN} --json note write-signals ${outQ}`, `${BIN} worklist audit ${s.nid} --out ${inOf(s.nid, 'audit')}`,
      `${BIN} metrics quality-add --run ${A.run} --kind repair_round:quote --task ${s.nid}`], 2)
    return { ...s, quoteRepaired: !!(a && a.ok) }
  },
)

// audit: owed by this run's verdict, or still owed from a run that stopped before it (resume)
phase('Audit')
const verdict = new Map(extracted.filter(Boolean).map(e => [e.nid, e]))
const toAudit = A.notes.filter(n => !done.has(`audited:${n}`) && !done.has(`filed:${n}`) &&
  ((verdict.get(n) && !verdict.get(n).error && verdict.get(n).owed) || (!verdict.has(n) && done.has(`audit-owed:${n}`))))
const audited = await parallel(toAudit.map(nid => async () => {
  const outA = `${TASKS}/${nid}.audit.out.json`
  const r = await judge('bigin-ba-workflow-plugin:signal-auditor', 'auditor.md', inOf(nid, 'audit'), outA, `audit ${nid}`, 'Audit')
  if (!r || r.status !== 'OK') return { nid, error: r && r.reason }
  const a = await ingestThen([`${BIN} --json ingest ${outA} --kind audit --run ${A.run}`,
    `${BIN} --json note audit-apply ${outA} --run ${A.run}`, `${BIN} run record ${A.run} --task audited:${nid} --status ok`], 2, outA, inOf(nid, 'audit'), `repair ${nid}`, 'Audit', AUDITOR)
  return { nid, ok: !!(a && a.ok), error: a && !a.ok ? a.error : null }
}))
const auditOf = new Map(audited.filter(Boolean).map(a => [a.nid, a]))

// filing is SERIAL by design: a later note's themes may extend a row an earlier note just filed — so each
// note's worklist is built only after the previous note is filed, by the SAME runner that files it
phase('File')
const filed = []
const toFile = A.notes.filter(n => !done.has(`filed:${n}`) && !(verdict.get(n) && verdict.get(n).error) &&
  !(auditOf.get(n) && auditOf.get(n).error))
let ready = null   // the note whose file worklist the previous runner already built
for (let i = 0; i < toFile.length; i++) {
  const nid = toFile[i], next = toFile[i + 1]
  const inF = inOf(nid, 'file')
  if (ready !== nid) await engine(`worklist file ${nid}`, 'File', [`${BIN} worklist file ${nid} --out ${inF}`])
  const outF = `${TASKS}/${nid}.filing.out.json`
  const r = await judge('bigin-ba-workflow-plugin:signal-filer', 'filer.md', inF, outF, `file ${nid}`, 'File')
  if (!r || r.status !== 'OK') { filed.push({ nid, error: r && r.reason }); continue }
  const cmds = [`${BIN} --json ingest ${outF} --kind filing --run ${A.run}`, `${BIN} --json file apply ${outF}`,
    `${BIN} run record ${A.run} --task filed:${nid} --status ok`]
  if (next) cmds.push(`${BIN} worklist file ${next} --out ${inOf(next, 'file')}`)
  const a = await ingestThen(cmds, 2, outF, inF, `file apply ${nid}`, 'File', FILER)
  if (a && a.ok && next) ready = next
  filed.push({ nid, ok: !!(a && a.ok), error: a && !a.ok ? a.error : null })
}

// analysis: read the filed note against the current spec — worklists in one runner once ALL filing is done
// (a later note's rows are an earlier note's `pending`), reads in parallel, applies serially
// (a blocking conflict flips hub rows, and two notes can share a hub)
phase('Analyze')
const toAnalyze = A.notes.filter(n => !done.has(`analysed:${n}`) &&
  (done.has(`filed:${n}`) || filed.some(f => f.nid === n && f.ok)))
if (toAnalyze.length) {
  await engine('worklists: analyze', 'Analyze', toAnalyze.map(n => `${BIN} worklist analyze ${n} --out ${inOf(n, 'analyze')} || true`))
}
const judged = await parallel(toAnalyze.map(nid => async () => {
  const outN = `${TASKS}/${nid}.analysis.out.json`
  const r = await judge('bigin-ba-workflow-plugin:intake-analyst', 'analyst.md', inOf(nid, 'analyze'), outN, `analyze ${nid}`, 'Analyze')
  return r && r.status === 'OK' ? { nid, out: outN } : { nid, error: r && r.reason }
}))
const analysed = []
for (const j of judged.filter(Boolean)) {
  if (j.error) { analysed.push(j); continue }
  const a = await ingestThen([`${BIN} --json ingest ${j.out} --kind analysis --run ${A.run}`,
    `${BIN} --json note analysis-apply ${j.out}`, `${BIN} run record ${A.run} --task analysed:${j.nid} --status ok`],
    2, j.out, inOf(j.nid, 'analyze'), `analysis apply ${j.nid}`, 'Analyze', ANALYST)
  analysed.push({ nid: j.nid, ok: !!(a && a.ok), result: a && a.data, error: a && !a.ok ? a.error : null })
}

const close = await engine('lint + coverage', 'Close', [`${BIN} lint --full || true`, `${BIN} --json coverage --stage file || true`])
return {
  run: A.run,
  extracted: extracted.filter(Boolean).map(e => ({ note: e.nid, error: e.error || null,
    audit: e.error ? null : (e.owed ? `independent (${e.reasons.join('; ')})` : 'self'),
    audited: !!(auditOf.get(e.nid) && auditOf.get(e.nid).ok),
    why_repair: e.whyRepair && e.whyRepair.length ? { rows: e.whyRepair.length, done: !!e.whyRepaired } : null,
    quote_repair: (e.unverified || []).length || (e.uncovered || []).length
      ? { unverified: (e.unverified || []).length, uncovered: (e.uncovered || []).length, done: !!e.quoteRepaired } : null })),
  audited: audited.filter(Boolean),
  filed,
  analysed,
  coverage_missing: close && close.data && close.data.missing ? close.data.missing.length : null,
  next: `bigin run summary ${A.run}`,
}
