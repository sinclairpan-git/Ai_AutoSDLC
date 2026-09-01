# 实施计划：两轮评审终局 Sponsor 决策收敛合同

**编号**：`225-review-terminal-sponsor-convergence` | **日期**：2026-08-31
**规格**：`specs/225-review-terminal-sponsor-convergence/spec.md`
**状态**：formal/admission；规则实现未授权

## 1. 概述

本计划只完成 G1 的主线证据审计、方案对比、ROI admission 和 formal 真值收口。结论只允许产生一个后续规则候选，不在 WI225 内修改 `AGENTS.md` 或任何 runtime。

## 2. 技术背景

**语言/版本**：Formal Markdown；候选仓库为 Python 3.11+ / Typer CLI，但本批不改 Python
**现有承载**：根 `AGENTS.md`、`LoopRun / LoopRound`、`needs_user`、`finding-history.json`、final report、attestation
**存储**：复用现有 Git 工作项文档与 review artifact；不新增持久化模型
**测试**：`code-change` 验证画像；唯一测试变更只同步固定库存 expectation，不改变测试逻辑
**目标平台**：本 Ai_AutoSDLC 仓库的自开发 PR/heartbeat 流程
**约束**：只读主线证据、半天 formal 预算、一个候选、没有 execute 授权

## 3. 宪章检查

| 宪章门禁 | 计划响应 |
|---|---|
| MUST-1 MVP/范围严控 | 只保留一个 repo-local 规则候选；runtime/schema 方向 No-Go |
| MUST-2 关键路径可验证 | 用 exact-main、源码行、truth/manifest/constraints 与独立评审验证 |
| MUST-3 范围/验证/回退 | formal 作为一个语义提交；可整体 revert |
| MUST-4 状态落盘 | spec/plan/tasks/log、Program Truth 和 handoff 均落盘；roadmap/defect 保持只读输入 |
| MUST-5 产品/开发框架隔离 | 候选只属于本仓库 Local Repository PR Protocol，不复制到普通用户 runtime |

## 4. 方案与决策

### 4.1 推荐：repo-local 协议补强

只在未来获批的独立规则实现批次中修改根 `AGENTS.md`：两轮后暂停 heartbeat，Sponsor 只做一次 stop/approve 决策；approve 必须同时冻结唯一 delta、投入上限和终止结果。该方案直接覆盖真实复发层，预计不超过 0.5 人日。

### 4.2 拒绝：Local PR Review runtime 改造

虽然本地服务存在 `increase --max-rounds` 的不一致提示，但它没有控制本次 GitHub heartbeat 循环。当前修改它会增加 Python/CLI/测试投入而不能直接解决复发，因此本 work item 不授权。

### 4.3 拒绝：新 SponsorDecision artifact

新 artifact/schema 会带来命令、迁移、验证与生命周期，违反本次不新增治理系统的边界。

## 5. Formal 阶段计划

### Phase 0：精确基线与证据审计

**目标**：确定复发层、可复用机制和真实缺口。

**产物**：`spec.md` 的现状证据与方案比较。

**验证方式**：

- `git rev-parse origin/main`
- `rg` 核对 `AGENTS.md`、roadmap、loop models、PR review service 与测试。
- `uv run ai-sdlc verify constraints`

**回退方式**：删除 WI225 formal carrier；不影响产品代码或 WI224。

### Phase 1：Admission 与停止条件冻结

**目标**：形成唯一候选、投入上限和 No-Go 触发器。

**产物**：`spec.md / plan.md / tasks.md / task-execution-log.md` 内的完整 admission 决策；不修改 roadmap 或 defect backlog。

**验证方式**：对账 FR/SC、占位符扫描、`workitem plan-check`、独立 formal/ROI 评审。

**回退方式**：整体 revert formal 提交；路线图与 defect backlog 不需要回退。

### Phase 2：Formal 真值与 PR 收口

**目标**：让 WI225 以 `formal_freeze_only / execution_started=false` 进入主线；不得借收口进入规则实现。

**产物**：Program Truth snapshot、库存期望、canonical/scoped handoff、formal PR。

**验证方式**：

- `uv run ai-sdlc program validate`
- `uv run ai-sdlc program truth sync --dry-run`
- `uv run ai-sdlc program truth sync --execute --yes`
- `uv run ai-sdlc program truth audit`
- `uv run pytest tests/integration/test_repo_program_manifest.py -q`
- `uv run ai-sdlc workitem plan-check --wi specs/225-review-terminal-sponsor-convergence`
- `git diff --check`

**回退方式**：revert formal PR；不需要 runtime/数据迁移。

## 6. 后续唯一实现候选（未授权）

若本 formal 合入后用户明确批准 execute，另起一个 bounded rules-only 批次：

1. 只修改根 `AGENTS.md` 的 Local Repository PR Protocol。
2. 两轮后必须暂停 heartbeat；不得继续普通修复轮次。
3. Sponsor 批准必须同时给出 `unique_delta / effort_cap / terminal_outcome`。
4. 终局动作只允许一个规则/代码 delta；终局复核后无论 PASS、known-blocked 或 No-Go 都结束，不再申请第二个例外。
5. 最小验证为 `rules-only` profile、`uv run ai-sdlc verify constraints`、针对规则标记的可复核检查和独立对抗评审。
6. 只用一个实现 PR；不创建 post-merge records-only PR。

## 7. No-Go 与退出

- 候选需要修改第二个实现文件、产品 runtime、review schema、状态机或新 artifact。
- 总投入预计超过 0.5 人日。
- 需要第二个修复 PR、第二次 sponsor 例外或 post-merge records PR。
- 规则无法直接覆盖 heartbeat/PR 实际执行，或只能重复 roadmap 已有文字而无新增约束入口。
- 独立评审证明该规则会屏蔽新安全/隐私/数据/发布完整性 BLOCKER。

任一触发即把后续候选改为 No-Go；WI225 formal 仍可真实合入作为审计结论。
