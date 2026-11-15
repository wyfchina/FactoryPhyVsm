'use strict';

// Project-specific closure request for the accepted deterministic scope of Issue 08.
const fs = require('node:fs');
const crypto = require('node:crypto');
const cp = require('node:child_process');
const requestPath = 'outputs/vsm-michigan-steel-baseline/evidence/issue08-closure-request.json';
const base = 'outputs/vsm-michigan-steel-baseline/';

function requireThat(condition, message) {
  if (!condition) throw new Error(message);
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

function validateLocalRequest() {
  const request = readJson(requestPath);
  requireThat(request.schema_version === 1, 'Unsupported request schema');
  requireThat(request.repository === 'wyfchina/FactoryPhyVsm', 'Unexpected repository');
  requireThat(request.branch === 'codex/vsm-v04-github-ready', 'Unexpected branch');
  requireThat(request.issue_number === 8, 'Only Issue 08 may be closed');
  requireThat(/^[a-f0-9]{40}$/.test(request.evidence_commit), 'Full evidence SHA required');
  requireThat(request.decision_owner === 'Wu' && request.business_reviewer === 'Wu' && request.business_review_confirmed === true,
    'Missing Wu business review');
  requireThat(request.local_status === 'Passed（确定性验证与守恒范围）', 'Unexpected local acceptance scope');
  requireThat(request.expected_status_label === 'status:passed', 'Unexpected status label');
  requireThat(Array.isArray(request.evidence_paths) && request.evidence_paths.length >= 6, 'Evidence paths are incomplete');
  requireThat(request.acceptance_comment.includes(request.evidence_commit) &&
    request.acceptance_comment.includes('Local status: Passed') &&
    request.acceptance_comment.includes('Decision owner: Wu') &&
    request.acceptance_comment.includes('Business reviewer: Wu') &&
    request.acceptance_comment.includes('Issue 09'), 'Acceptance comment is incomplete');

  const issueRecord = fs.readFileSync(base + 'iterations/I1/08.md', 'utf8');
  requireThat(issueRecord.includes('Passed（确定性验证与守恒范围）'), 'Local Issue 08 is not Passed');
  const closureEvidence = fs.readFileSync(base + 'issue08-closure-evidence.md', 'utf8');
  requireThat(closureEvidence.includes('Passed（确定性验证与守恒范围）'), 'Closure evidence has no Passed decision');

  for (const path of request.evidence_paths) {
    requireThat(path.startsWith(base) && !path.split('/').includes('..'), `Invalid evidence path: ${path}`);
    requireThat(fs.statSync(path).isFile(), `Missing evidence file: ${path}`);
    cp.execFileSync('git', ['cat-file', '-e', `${request.evidence_commit}:${path}`]);
  }
  cp.execFileSync('git', ['merge-base', '--is-ancestor', request.evidence_commit, 'HEAD']);

  const savedReadback = readJson(base + 'evidence/issue06-persistence-readback.json');
  const acceptance = readJson(base + 'evidence/issue06-acceptance-summary.json');
  const aggregation = readJson(base + 'evidence/issue06-aggregation-comparison.json');
  const modelBytes = cp.execFileSync('git', ['show', `${request.evidence_commit}:${request.model_path}`]);
  const modelSha = crypto.createHash('sha256').update(modelBytes).digest('hex');
  requireThat(modelSha === request.model_sha256.toLowerCase(), 'V0.12 model hash mismatch');
  requireThat(savedReadback.modelSHA256.toLowerCase() === modelSha && savedReadback.outputsMatchPreSave === true,
    'Saved/reloaded model identity or output readback mismatch');
  requireThat(savedReadback.diagnostics.errorCount === 0, 'Native model diagnostics are not clean');
  requireThat(acceptance.repeatIdentical === true && acceptance.checks.native.Balance === '0',
    'Deterministic repeat or quantity balance evidence failed');
  requireThat(acceptance.checks.outputRows.VSM_Out_WIPSnapshot === 1890, 'Expected 1,890 WIP snapshots');
  const q20 = aggregation.find(x => x.q === 20);
  const q1 = aggregation.find(x => x.q === 1);
  requireThat(q20 && q1 && q20.demand.OnTime === q1.demand.OnTime && q20.demand.LateByHorizon === q1.demand.LateByHorizon,
    'q20/q1 demand reference mismatch');
  requireThat(q20.completedNewUnits === 6640 && q1.completedNewUnits === 6655,
    'q20/q1 manufacturing timing difference changed; review the accepted scope');
  return request;
}

async function run({ github, context, core }) {
  const request = validateLocalRequest();
  requireThat(context.eventName === 'push' && context.actor === 'wyfchina', 'Only owner pushes can execute this request');
  requireThat(context.ref === `refs/heads/${request.branch}`, 'Unexpected push ref');
  requireThat(`${context.repo.owner}/${context.repo.repo}` === request.repository, 'Unexpected runtime repository');
  const repo = { owner: context.repo.owner, repo: context.repo.repo };
  const marker = `<!-- issue08-closure:${request.evidence_commit} -->`;
  const comparison = await github.rest.repos.compareCommitsWithBasehead({
    ...repo,
    basehead: `${request.evidence_commit}...${context.sha}`
  });
  requireThat(['ahead', 'identical'].includes(comparison.data.status), 'Evidence commit is not an ancestor of this run');

  for (const path of request.evidence_paths) {
    cp.execFileSync('git', ['cat-file', '-e', `${request.evidence_commit}:${path}`]);
    await github.rest.repos.getContent({ ...repo, path, ref: request.evidence_commit });
  }
  const issueRecordAtEvidence = await github.rest.repos.getContent({
    ...repo,
    path: base + 'iterations/I1/08.md',
    ref: request.evidence_commit
  });
  requireThat(Buffer.from(issueRecordAtEvidence.data.content, 'base64').toString('utf8')
    .includes('Passed（确定性验证与守恒范围）'), 'Committed Issue 08 has no Passed acceptance');

  const issue = (await github.rest.issues.get({ ...repo, issue_number: 8 })).data;
  requireThat(!issue.pull_request && issue.milestone && issue.milestone.title === 'I1 - Michigan Steel VSM Baseline',
    'Unexpected Issue 08 identity');
  const labels = issue.labels.map(x => typeof x === 'string' ? x : x.name);
  const statuses = labels.filter(x => x.startsWith('status:'));
  requireThat(statuses.length <= 1, 'Issue 08 has conflicting status labels');

  async function addOnce() {
    const comments = await github.paginate(github.rest.issues.listComments, { ...repo, issue_number: 8, per_page: 100 });
    return comments.find(x => x.body && x.body.includes(marker)) ||
      (await github.rest.issues.createComment({ ...repo, issue_number: 8, body: request.acceptance_comment })).data;
  }

  if (issue.state === 'closed') {
    requireThat(issue.state_reason === 'completed', 'Issue 08 is already closed for a different reason');
    const comments = await github.paginate(github.rest.issues.listComments, { ...repo, issue_number: 8, per_page: 100 });
    requireThat(comments.some(x => x.body && x.body.includes(marker)), 'Issue 08 was closed without this evidence marker');
  } else {
    requireThat(issue.state === 'open', 'Unexpected Issue 08 state');
    await addOnce();
    try {
      await github.rest.issues.getLabel({ ...repo, name: request.expected_status_label });
    } catch (error) {
      if (error.status !== 404) throw error;
      await github.rest.issues.createLabel({
        ...repo,
        name: request.expected_status_label,
        color: '0e8a16',
        description: 'Passed within the stated acceptance scope'
      });
    }
    const cleanLabels = labels.filter(x => !x.startsWith('status:'));
    const sourceUrl = `https://github.com/${request.repository}/blob/${request.evidence_commit}/`;
    const body = `Parent: #1\nIteration: I1 / I1.5\nCore work package: 08\n\n# 确定性验证与守恒\n\n**状态：Passed（V0.12确定性验证与守恒范围），以 completed 关闭。**\n\n已验收：15个来源在6个位置、21个时点形成1,890条动态快照，来源/位置守恒差为0；F01–F07及有效工时、同刻和第20日终点、换型、故障续作、资源释放和保存重载回归通过；诊断0 errors、运行警告0。q20/q1发运与按期需求结果一致，但制造完成量相差15件、已完成CT加权均值相差14.7333分钟，不宣称逐件时序等价。\n\nR1独立随机复制、95% CI、目标可用率观测、随机流/种子映射、20件聚合适用性和作者结果对照不属于本次关闭条件，转由#9后续研究/基线验收。I1、B0/B1和#9仍保持HOLD/BLOCKED。\n\n详细验收与证据：[受控 Issue 08 记录](${sourceUrl}${base}iterations/I1/08.md)、[闭环证据](${sourceUrl}${base}issue08-closure-evidence.md)、[验证计划](${sourceUrl}${base}05-verification-plan.md)。\n\n证据提交：${request.evidence_commit}。决策责任人：Wu；业务评审人：Wu。`;
    await github.rest.issues.update({
      ...repo,
      issue_number: 8,
      body,
      labels: [...cleanLabels, request.expected_status_label],
      state: 'closed',
      state_reason: 'completed'
    });
  }

  const confirmed = (await github.rest.issues.get({ ...repo, issue_number: 8 })).data;
  const comments = await github.paginate(github.rest.issues.listComments, { ...repo, issue_number: 8, per_page: 100 });
  requireThat(confirmed.state === 'closed' && confirmed.state_reason === 'completed', 'Closed/completed readback failed');
  requireThat(confirmed.labels.some(x => x.name === request.expected_status_label) &&
    !confirmed.labels.some(x => x.name === 'status:partial'), 'Status label readback failed');
  const acceptance = comments.find(x => x.body && x.body.includes(marker));
  requireThat(acceptance && acceptance.body.includes(request.evidence_commit), 'Acceptance comment readback failed');
  await core.summary.addHeading('I1 Issue 08 closure verified')
    .addRaw(`Evidence: ${request.evidence_commit}\n\n[Acceptance comment](${acceptance.html_url})\n\nState: closed/completed; label: status:passed. Issue 09 retains R1 statistics, aggregation applicability and author comparison; I1/B0/B1 remain HOLD.`)
    .write();
}

module.exports = { run, validateLocalRequest };
if (require.main === module) {
  validateLocalRequest();
  process.stdout.write('Local Issue 08 closure request validated; no GitHub writes performed.\n');
}
