'use strict';

// Project-specific closure request for the accepted V0.12 implementation scope of Issue 06.
const fs = require('node:fs');
const crypto = require('node:crypto');
const cp = require('node:child_process');

const requestPath = 'outputs/vsm-michigan-steel-baseline/evidence/issue06-closure-request.json';
const base = 'outputs/vsm-michigan-steel-baseline/';

function requireThat(condition, message) {
  if (!condition) throw new Error(message);
}

function readJson(path) {
  return JSON.parse(fs.readFileSync(path, 'utf8'));
}

function validateLocalRequest() {
  const request = readJson(requestPath);
  requireThat(request.schema_version === 1, 'Unsupported request schema');
  requireThat(request.repository === 'wyfchina/FactoryPhyVsm', 'Unexpected repository');
  requireThat(request.branch === 'codex/vsm-v04-github-ready', 'Unexpected branch');
  requireThat(request.issue_number === 6, 'Only Issue 06 may be closed');
  requireThat(/^[a-f0-9]{40}$/.test(request.evidence_commit), 'Evidence commit must be a full SHA');
  requireThat(request.decision_owner === 'Wu' && request.business_reviewer === 'Wu' && request.business_review_confirmed === true,
    'Wu business review is required');
  requireThat(request.local_status === 'Passed（V0.12实施与确定性实现范围）', 'Unexpected local acceptance scope');
  requireThat(request.expected_status_label === 'status:passed', 'Unexpected status label');
  requireThat(Array.isArray(request.evidence_paths) && request.evidence_paths.length >= 6, 'Evidence paths are incomplete');
  requireThat(request.acceptance_comment.includes(request.evidence_commit) &&
    request.acceptance_comment.includes('Decision owner: Wu') &&
    request.acceptance_comment.includes('Business reviewer: Wu') &&
    request.acceptance_comment.includes('Issue 09'), 'Acceptance comment is incomplete');

  const issueRecord = fs.readFileSync(base + 'iterations/I1/06.md', 'utf8');
  requireThat(issueRecord.includes('Passed（V0.12实施与确定性实现范围）'), 'Local Issue 06 is not Passed');
  const closureEvidence = fs.readFileSync(base + 'issue06-closure-evidence.md', 'utf8');
  requireThat(closureEvidence.includes('Passed（V0.12 实施与确定性实现范围）'), 'Closure evidence has no Passed decision');

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
  requireThat(savedReadback.diagnostics.errorCount === 0, 'Native diagnostics are not clean');
  requireThat(acceptance.repeatIdentical === true && acceptance.checks.native.Balance === '0',
    'Deterministic repeat or balance evidence failed');
  requireThat(acceptance.checks.outputRows.VSM_Out_WIPSnapshot === 1890, 'Expected 1,890 WIP snapshots');
  const q20 = aggregation.find(x => x.q === 20);
  const q1 = aggregation.find(x => x.q === 1);
  requireThat(q20 && q1 && q20.demand.OnTime === q1.demand.OnTime && q20.demand.LateByHorizon === q1.demand.LateByHorizon,
    'q20/q1 demand reference mismatch');
  requireThat(q20.completedNewUnits === 6640 && q1.completedNewUnits === 6655,
    'q20/q1 manufacturing timing evidence changed');
  return request;
}

async function run({ github, context, core }) {
  const request = validateLocalRequest();
  requireThat(context.eventName === 'push' && context.actor === 'wyfchina', 'Only owner pushes can execute this request');
  requireThat(context.ref === `refs/heads/${request.branch}`, 'Unexpected push ref');
  requireThat(`${context.repo.owner}/${context.repo.repo}` === request.repository, 'Unexpected repository');
  const repo = { owner: context.repo.owner, repo: context.repo.repo };
  const marker = `<!-- issue06-closure:${request.evidence_commit} -->`;
  const comparison = await github.rest.repos.compareCommitsWithBasehead({
    ...repo, basehead: `${request.evidence_commit}...${context.sha}`
  });
  requireThat(['ahead', 'identical'].includes(comparison.data.status), 'Evidence commit is not an ancestor');

  const issue = (await github.rest.issues.get({ ...repo, issue_number: 6 })).data;
  requireThat(!issue.pull_request && issue.milestone && issue.milestone.title === 'I1 - Michigan Steel VSM Baseline',
    'Unexpected Issue 06 identity');
  const labels = issue.labels.map(x => typeof x === 'string' ? x : x.name);
  requireThat(labels.filter(x => x.startsWith('status:')).length <= 1, 'Conflicting status labels exist');

  const comments = await github.paginate(github.rest.issues.listComments, { ...repo, issue_number: 6, per_page: 100 });
  if (issue.state === 'closed') {
    requireThat(issue.state_reason === 'completed', 'Issue 06 is closed for a different reason');
    requireThat(comments.some(x => x.body && x.body.includes(marker)), 'Missing Issue 06 closure marker');
  } else {
    requireThat(issue.state === 'open', 'Unexpected Issue 06 state');
    if (!comments.some(x => x.body && x.body.includes(marker))) {
      await github.rest.issues.createComment({ ...repo, issue_number: 6, body: request.acceptance_comment });
    }
    try {
      await github.rest.issues.getLabel({ ...repo, name: request.expected_status_label });
    } catch (error) {
      if (error.status !== 404) throw error;
      await github.rest.issues.createLabel({ ...repo, name: request.expected_status_label, color: '0e8a16', description: 'Passed within the stated acceptance scope' });
    }
    const cleanLabels = labels.filter(x => !x.startsWith('status:'));
    await github.rest.issues.update({
      ...repo,
      issue_number: 6,
      body: request.issue_body,
      labels: [...cleanLabels, request.expected_status_label],
      state: 'closed',
      state_reason: 'completed'
    });
  }

  const confirmed = (await github.rest.issues.get({ ...repo, issue_number: 6 })).data;
  const finalComments = await github.paginate(github.rest.issues.listComments, { ...repo, issue_number: 6, per_page: 100 });
  requireThat(confirmed.state === 'closed' && confirmed.state_reason === 'completed', 'Closed/completed readback failed');
  requireThat(confirmed.labels.some(x => x.name === request.expected_status_label) &&
    !confirmed.labels.some(x => x.name === 'status:partial'), 'Status label readback failed');
  const acceptance = finalComments.find(x => x.body && x.body.includes(marker));
  requireThat(acceptance && acceptance.body.includes(request.evidence_commit), 'Acceptance comment readback failed');
  await core.summary.addHeading('I1 Issue 06 closure verified')
    .addRaw(`Evidence: ${request.evidence_commit}\n\n[Acceptance comment](${acceptance.html_url})\n\nState: closed/completed; label: status:passed. Issue 09 retains research items; I1/B0/B1 remain HOLD.`)
    .write();
}

module.exports = { run, validateLocalRequest };
