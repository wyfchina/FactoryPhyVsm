# GitHub 闭环同步 Skill 升级验收

- 日期：2026-11-15。
- Skill：supply-chain-simulation-planning，版本2026.11.15.1。
- 维护源：[工作区Skill](../../skills/supply-chain-simulation-planning/SKILL.md)。
- 维护源提交：9be8e15ab98af5119f16d5166f1995e31f7243ff。
- 生效安装目录：C:/Users/吴一帆/.codex/skills/supply-chain-simulation-planning。
- 判定：升级与安装验收通过。通用Action模板已交付，未在业务仓库启用新的通用写入工作流；实际线上写入路径的检验边界见下。

## 修复与复用范围

1. 通用检查脚本要求closed/completed、status:passed且无冲突状态标签，并逐条核对证据路径确实位于完整证据提交SHA中；本地文件存在和提交存在不再足以通过。
2. 明确PreClose检查、显式Apply、强制PostClose回读、本地状态回填和回执保存；记录业务评审依据、验收范围及已批准转交事项。
3. 增加参数化请求、通用Action模板和workflow runner，不固定仓库名、Issue编号、评审人或证据SHA。脚本统一放scripts，模板放assets/templates，规范放references。
4. 明确gh、REST、Connector及仓库Action的可用通道、权限失败处理、部分成功后的回读续办；快照审计与真实线上审计分开标记，快照禁止Apply。
5. 合并维护源与已安装副本的有效差异，保留平台实现边界及案例引用修正，完成逐文件安装核对。以后以本工作区维护源提交为本包升级来源；安装目录作为使用副本。

以上处置对应[上一轮检验发现](../vsm-michigan-steel-baseline/issue07-skill-sync-audit.md)。旧报告和原始结果保留，不能把旧版漏检结果改写为新版通过。

## 实际验证

| 验证 | 结果与证据 |
|---|---|
| 三项原漏检 | 非completed关闭、冲突状态标签、未提交证据路径均被拒绝，退出2 |
| 合成数据与隔离模拟回归 | 22/22通过；包含16项审计/输入测试、2项幂等及中断恢复测试、4项workflow审计/应用与身份校验测试。见[逐项结果](regression-results.json) |
| 写入测试的外部影响 | 使用子进程内的本地HTTP替身，无真实GitHub写入；不能把模拟测试表述为新通用Action已在线应用成功 |
| PowerShell语法、工作流YAML与请求JSON | 通过；请求默认audit、业务确认false；模板权限为contents:read与issues:write |
| 官方quick_validate.py | 工作区维护源及生效安装副本均输出Skill is valid!。所需PyYAML 6.0.2仅安装于本任务tmp隔离目录，未修改系统Python环境 |
| Skill内本地Markdown链接 | 检查通过，无缺失目标；模板占位符按模板含义保留 |
| 完整安装一致性 | 33个文件逐一SHA-256完全一致，无仅安装目录存在的额外文件；见[安装清单](installation-verification.json) |
| 新版已安装脚本真实线上审计 | 对FactoryPhyVsm #7执行默认只读PostClose，18项检查通过，result=Passed、actions=0；见[真实线上回执](issue07-live-postclose-audit.json) |

线上审计实际读取了f821e0044453146a4eff350307bcc4240f5552c7及其四条证据路径、#7及验收评论。关闭状态为closed/completed，只有status:passed状态标签，评审人和证据SHA绑定正确。本机无gh/token时，本次通过公共REST只读通道完成，不需要修改Connector授权或重新关闭Issue。

## 使用边界

通用规则要求代理在GitHub管理的Issue本地验收准备闭环时主动启动检查，Skill本身不是后台监听器。Action接入仍须复制模板和两个生产脚本、登记本仓库分支与真实批准请求；单独升级Skill不会自动给所有仓库安装工作流。

本轮未修改Simio模型、VSM业务契约或已有#7验收结论，未重新开关业务Issue；I1及B0/B1的原有阶段门不因工具升级改变。
