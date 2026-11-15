'use strict';

// Project adapter: refresh linked records; acceptance and closure use the Skill runner.
const fs = require('node:fs');
const path = require('node:path');
const cp = require('node:child_process');

function requireThat(condition, message) {
  if (!condition) throw new Error(message);
}

function validatePlan(plan, repository, branch) {
  requireThat(plan.schema_version === 1 && plan.repository === repository && plan.target_branch === branch,
    'Record plan repository or branch does not match this run');
  requireThat(/^[a-f0-9]{40}$/.test(plan.evidence_commit), 'Full evidence SHA required');
  requireThat(plan.approval_reference && Array.isArray(plan.records) && plan.records.length,
    'Approved nonempty record plan required');
  const numbers = new Set();
  for (const record of plan.records) {
    requireThat(Number.isInteger(record.issue_number) && record.issue_number > 0 && !numbers.has(record.issue_number),
      'Issue identifiers must be unique positive integers');
    numbers.add(record.issue_number);
    requireThat(record.expected_state === 'open' && record.local_file && record.summary && record.local_status,
      'Record sync requires an open Issue and explicit local scope');
    requireThat(/^outputs\/vsm-michigan-steel-baseline\/[A-Za-z0-9_./-]+\.md$/.test(record.local_file) &&
      !record.local_file.split('/').includes('..'), 'Invalid local source path');
    requireThat(fs.statSync(record.local_file).isFile(), 'Local source file missing');
    cp.execFileSync('git', ['cat-file', '-e', `${plan.evidence_commit}:${record.local_file}`]);
  }
  cp.execFileSync('git', ['merge-base', '--is-ancestor', plan.evidence_commit, 'HEAD']);
  return plan;
}

async function run({ github, context, core, planPath: requestedPlanPath }) {
  const planPath = requestedPlanPath || '.github/issue-records/i1-pre07-sync.json';
  // Future closure requests must not reapply this historical body refresh.
  if (context.eventName !== 'push') return;
  const changed = cp.execFileSync('git', ['diff', '--name-only', '--diff-filter=AM', context.payload.before, context.sha],
    { encoding: 'utf8' }).trim().split(/\r?\n/);
  if (!changed.includes(planPath)) return;
  const repository = `${context.repo.owner}/${context.repo.repo}`;
  const branch = context.ref.replace(/^refs\/heads\//, '');
  requireThat(branch === context.payload.repository.default_branch, 'Only the default branch may apply this plan');
  const plan = validatePlan(JSON.parse(fs.readFileSync(planPath, 'utf8')), repository, branch);
  const originals = [];
  // Validate the entire batch before updating any body.
  for (const record of plan.records) {
    const issue = (await github.rest.issues.get({ ...context.repo, issue_number: record.issue_number })).data;
    requireThat(!issue.pull_request && issue.state === record.expected_state, `Unexpected Issue #${record.issue_number} identity/state`);
    originals.push(issue);
  }
  const receipts = [];
  for (const record of plan.records) {
    const marker = `<!-- simulation-record-sync:${repository}:${record.issue_number}:${plan.evidence_commit} -->`;
    const source = `https://github.com/${repository}/blob/${plan.evidence_commit}/${record.local_file}`;
    const body = `${marker}\n## 当前受控记录\n\n- Iteration: I1\n- Local status: ${record.local_status}\n- Decision owner: Wu\n- Business reviewer: Wu\n- Evidence commit: ${plan.evidence_commit}\n\n${record.summary}\n\n目标、依赖、设计、验收条件和详细结果以[受控文件](${source})为准，避免复制两份规范。\n\n[本轮同步审计](https://github.com/${repository}/blob/${plan.evidence_commit}/outputs/vsm-michigan-steel-baseline/issue01-06-sync-audit.md)。历史正文另存于该审计的原始回读文件。\n\n批准依据：${plan.approval_reference}\n\n本步骤只刷新记录；关闭状态由已批准的闭环请求和线上验收回读确定。I1、B0/B1继续HOLD。`;
    await github.rest.issues.update({ ...context.repo, issue_number: record.issue_number, body });
    let commentUrl = null;
    if (record.progress_comment) {
      const comments = await github.paginate(github.rest.issues.listComments,
        { ...context.repo, issue_number: record.issue_number, per_page: 100 });
      const existing = comments.find(x => (x.body || '').includes(marker));
      const comment = existing || (await github.rest.issues.createComment({ ...context.repo,
        issue_number: record.issue_number, body: `${marker}\n${record.progress_comment}\n\n[受控记录](${source})；证据提交 ${plan.evidence_commit}。` })).data;
      commentUrl = comment.html_url;
    }
    const readback = (await github.rest.issues.get({ ...context.repo, issue_number: record.issue_number })).data;
    const original = originals.find(x => x.number === record.issue_number);
    requireThat(readback.body === body && readback.state === original.state && readback.state_reason === original.state_reason,
      `Issue #${record.issue_number} record readback failed`);
    requireThat(JSON.stringify(readback.labels.map(x => x.name).sort()) ===
      JSON.stringify(original.labels.map(x => x.name).sort()), 'Record adapter unexpectedly changed labels');
    receipts.push({ number: record.issue_number, state: readback.state, comment_url: commentUrl, body_verified: true });
  }
  const reportDir = path.join(process.env.RUNNER_TEMP, 'issue-sync-receipts');
  fs.mkdirSync(reportDir, { recursive: true });
  fs.writeFileSync(path.join(reportDir, 'linked-record-sync.json'), JSON.stringify({
    captured_at_utc: new Date().toISOString(), evidence_commit: plan.evidence_commit, receipts
  }, null, 2));
  await core.summary.addHeading('Linked Issue records synchronized').addRaw(JSON.stringify(receipts, null, 2)).write();
}

module.exports = { run, validatePlan };
