export const meta = {
  name: 'bigin-eval',
  description: 'Golden-set eval: run the real signal-extractor (and uc-router where a case has a route worklist) on each tests/evals case, then grade the outputs in code (bigin eval grade) — recall, precision, type accuracy, inversions, routing lane/target',
  whenToUse: 'By hand, before releasing any card, schema or model change; record the scores in the release note. args: {run, vault, plugin_root, cases?, bin?}. `bigin run new --stage eval` first.',
  phases: [
    { title: 'Prepare', detail: 'bigin eval prepare — stage each case under the run' },
    { title: 'Run', detail: 'extractor (and router) per case, in parallel' },
    { title: 'Grade', detail: 'bigin eval grade — code only' },
  ],
}

const A = args || {}
const BIN = A.bin || `"${A.plugin_root}/scripts/bigin"`
const TASKS = `_runs/${A.run}/tasks`
const VAULT = A.vault || '.'
if (!A.run || !A.plugin_root) throw new Error('args need {run, plugin_root}')
const CASES = A.cases ? ` --cases "${A.cases}"` : ''

const RUNNER = { type: 'object', properties: { ok: { type: 'boolean' }, data: { type: ['object', 'array'] }, error: { type: 'string' } }, required: ['ok'] }
const TASK = { type: 'object', properties: { status: { enum: ['OK', 'BLOCKED'] }, out: { type: 'string' }, reason: { type: 'string' } }, required: ['status'] }

function engine(label, phase, cmd) {
  return agent(`You are the Bigin engine runner. From the vault root \`${VAULT}\`, run with Bash exactly:\n1. ${cmd}\n` +
    `Return {ok:false, error:<last 15 lines>} on a non-zero exit; else {ok:true, data:<stdout parsed as JSON>}.`,
    { label, phase, schema: RUNNER, model: 'haiku', effort: 'low' })
}
function judge(agentType, card, input, output, label, phase) {
  return agent(`Read your card \`${A.plugin_root}/cards/${card}\`, then the task input \`${input}\` (vault root \`${VAULT}\`). ` +
    `Do what the card says. Write your JSON result to \`${output}\` and nothing else. Return {status:"OK", out} or {status:"BLOCKED", reason}.`,
    { label, phase, schema: TASK, agentType })
}

phase('Prepare')
const prep = await engine('eval prepare', 'Prepare', `${BIN} --json eval prepare ${A.run}${CASES}`)
if (!prep || !prep.ok) throw new Error('eval prepare failed: ' + (prep && prep.error))

phase('Run')
const ran = await parallel((prep.data || []).map(c => async () => {
  const x = await judge('bigin-ba-workflow-plugin:signal-extractor', 'extractor.md', c.extract_in,
    `${TASKS}/${c.case}.signals.out.json`, `extract ${c.case}`, 'Run')
  let r = null
  if (c.route_in) {
    r = await judge('bigin-ba-workflow-plugin:uc-router', 'router.md', c.route_in,
      `${TASKS}/${c.case}.route.out.json`, `route ${c.case}`, 'Run')
  }
  return { case: c.case, extract: x && x.status, route: r ? r.status : null }
}))

phase('Grade')
const graded = await engine('eval grade', 'Grade', `${BIN} --json eval grade ${A.run}${CASES}`)
return { run: A.run, ran: ran.filter(Boolean), grade: graded && graded.ok ? graded.data : { error: graded && graded.error } }
