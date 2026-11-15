'use strict';

// This is a project-specific closure request, not a general automatic acceptance rule.
const fs = require('node:fs');
const crypto = require('node:crypto');
const requestPath = 'outputs/vsm-michigan-steel-baseline/evidence/issue07-closure-request.json';
const base = 'outputs/vsm-michigan-steel-baseline/';

function requireThat(condition, message) {
  if (!condition) throw new Error(message);
}

function validateLocalRequest() {
  const request = JSON.parse(fs.readFileSync(requestPath, 'utf8'));
  requireThat(request.repository === 'wyfchina/FactoryPhyVsm', 'Unexpected repository');
  requireThat(request.branch === 'codex/vsm-v04-github-ready', 'Unexpected branch');
  requireThat(request.issue_number === 7, 'Only Issue 07 may be closed');
  requireThat(request.evidence_commit === 'f821e0044453146a4eff350307bcc4240f5552c7', 'Unexpected evidence commit');
  requireThat(request.decision_owner === 'Wu' && request.business_reviewer === 'Wu' && request.business_review_confirmed === true, 'Missing Wu approval');
  requireThat(request.acceptance_comment.includes(request.evidence_commit) && request.acceptance_comment.includes('Passed'), 'Missing acceptance/evidence comment');
  requireThat(request.handoffs.map(x => x.issue_number).join(',') === '6,8,9', 'Unexpected handoff targets');
  for (const path of request.evidence_paths) requireThat(path.startsWith(base) && !path.includes('..') && fs.statSync(path).isFile(), `Missing evidence: ${path}`);
  const localIssue = fs.readFileSync(base + 'iterations/I1/07.md', 'utf8');
  requireThat(/^状态:\s*Passed\s*$/m.test(localIssue), 'Local Issue 07 is not Passed');
  const hash = crypto.createHash('sha256').update(fs.readFileSync(request.model_path)).digest('hex').toUpperCase();
  requireThat(hash === request.model_sha256, 'V0.11 model hash mismatch');
  const csv = fs.readFileSync(base + 'data/demand-due-calendar.csv', 'utf8').trim().split(/\r?\n/);
  requireThat(csv.length === 21, 'Demand table must have 20 rows');
  let left = 0, right = 0;
  csv.slice(1).forEach((line, i) => {
    const [day, seconds, hours, l, r, total] = line.split(',').map(Number);
    requireThat(day === i + 1 && seconds === 55200 * day, 'Demand day/deadline mismatch');
    requireThat(l === 600 && r === 320 && total === 920, 'Demand quantity mismatch');
    requireThat(Math.abs(hours * 3600 - seconds) < 1e-6, 'Demand time conversion mismatch');
    left += l; right += r;
  });
  requireThat(left === 12000 && right === 6400, 'Monthly demand mismatch');
  return request;
}

async function run({ github, context, core }) {
  const request = validateLocalRequest();
  requireThat(context.eventName === 'push' && context.actor === 'wyfchina', 'Only owner pushes can execute this request');
  requireThat(context.ref === `refs/heads/${request.branch}`, 'Unexpected push ref');
  requireThat(`${context.repo.owner}/${context.repo.repo}` === request.repository, 'Unexpected runtime repository');
  const repo = { owner: context.repo.owner, repo: context.repo.repo };
  const marker = `<!-- issue07-closure:${request.evidence_commit} -->`;
  const comparison = await github.rest.repos.compareCommitsWithBasehead({ ...repo, basehead: `${request.evidence_commit}...${context.sha}` });
  requireThat(['ahead', 'identical'].includes(comparison.data.status), 'Evidence commit is not an ancestor of this run');
  const remoteEvidence = await github.rest.repos.getContent({ ...repo, path: base + 'iterations/I1/07.md', ref: request.evidence_commit });
  requireThat(/^状态:\s*Passed\s*$/m.test(Buffer.from(remoteEvidence.data.content, 'base64').toString('utf8')), 'Committed Issue 07 has no Passed acceptance');
  const issue = (await github.rest.issues.get({ ...repo, issue_number: 7 })).data;
  requireThat(!issue.pull_request && issue.milestone && issue.milestone.title === 'I1 - Michigan Steel VSM Baseline', 'Unexpected issue identity');
  // Idempotence prevents duplicate comments when the same workflow is retried.
  async function addOnce(number, body) {
    const comments = await github.paginate(github.rest.issues.listComments, { ...repo, issue_number: number, per_page: 100 });
    const existing = comments.find(x => x.body && x.body.includes(marker));
    return existing || (await github.rest.issues.createComment({ ...repo, issue_number: number, body: `${marker}\n${body}` })).data;
  }
  // Validate all handoff targets before any mutation; do not change their states.
  for (const handoff of request.handoffs) {
    const target = (await github.rest.issues.get({ ...repo, issue_number: handoff.issue_number })).data;
    requireThat(!target.pull_request && target.state === 'open', `Handoff target #${handoff.issue_number} needs review`);
  }
  const acceptance = await addOnce(7, request.acceptance_comment);
  for (const handoff of request.handoffs) await addOnce(handoff.issue_number, handoff.body);
  try {
    await github.rest.issues.getLabel({ ...repo, name: 'status:passed' });
  } catch (error) {
    if (error.status !== 404) throw error;
    await github.rest.issues.createLabel({ ...repo, name: 'status:passed', color: '0e8a16', description: 'Passed within the stated acceptance scope' });
  }
  const labels = issue.labels.map(x => typeof x === 'string' ? x : x.name).filter(x => !x.startsWith('status:'));
  const body = `Parent: #1\nIteration: I1 / I1.5\nCore work package: 07\n\n# 指标与统计框架\n\n**状态：Passed（指标与统计规范），以 completed 关闭。**\n\n目标：冻结可审计的指标、单位、总体、删失与复制规范。依赖：#1、#2、#3；实现与运行消费者为#6、#8，作者对照为#9。\n\n已验收：CT为Stamping进入至Assembly #2离开；初始WIP剩余时间单列；生产批次P1-L/P1-R/P2-L/P2-R；R1有限20工作日、无预热、初始30独立随机复制、95%CI；方案A每日末L600/R320按产品FIFO/部分交付；仅计有效工时55,200秒/日。\n\n验收结论只涵盖规范。CT/FG/需求/批次挂钩、原生小例、随机复制和作者算法映射仍由#6/#8/#9承接。I1与B0/B1仍HOLD。\n\n规范与全部验收条件：[受控07.md](https://github.com/${request.repository}/blob/${request.evidence_commit}/${base}iterations/I1/07.md)。\n\n证据提交：${request.evidence_commit}；[验收评论](${acceptance.html_url})。Wu为决策责任人和业务评审人，已明确授权本次闭环。此前开单版本：[原始07.md](https://github.com/${request.repository}/blob/b6ad8634b7dae89c999918a9cd95f85357d9166b/${base}iterations/I1/07.md)，不把旧版Partial当作当前结论。`;
  await github.rest.issues.update({ ...repo, issue_number: 7, body, labels: [...labels, 'status:passed'], state: 'closed', state_reason: 'completed' });
  const confirmed = (await github.rest.issues.get({ ...repo, issue_number: 7 })).data;
  const comments = await github.paginate(github.rest.issues.listComments, { ...repo, issue_number: 7, per_page: 100 });
  requireThat(confirmed.state === 'closed' && confirmed.state_reason === 'completed', 'Closed/completed readback failed');
  requireThat(confirmed.labels.some(x => x.name === 'status:passed') && !confirmed.labels.some(x => x.name === 'status:partial'), 'Label readback failed');
  requireThat(comments.some(x => x.body && x.body.includes(marker) && x.body.includes(request.evidence_commit)), 'Acceptance comment readback failed');
  await core.summary.addHeading('I1 Issue 07 closure verified').addRaw(`Evidence: ${request.evidence_commit}\n\n[Acceptance comment](${acceptance.html_url})\n\nState: closed/completed; label: status:passed. Native implementation/tests remain in #6/#8/#9; I1 remains HOLD.`).write();
}

module.exports = { run, validateLocalRequest };
if (require.main === module) {
  validateLocalRequest();
  process.stdout.write('Local closure request validated; no GitHub writes performed.\n');
}
