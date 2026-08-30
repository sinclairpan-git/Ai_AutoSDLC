---
related_plan: "docs/FRAMEWORK_ROADMAP.zh-CN.md"
---
# 实施计划：跨平台首次用户十二路线证据合同

**编号**：`222-first-user-twelve-route-e2e-contract`
**日期**：2026-08-30
**规格**：`specs/222-first-user-twelve-route-e2e-contract/spec.md`
**阶段**：P3-A formal/admission；runtime 未授权

## 1. 概述

本计划只完成十二路线合同、现有证据普查、ROI/止损决策和 Program Truth 对齐。它将 P3 从宽泛路线图事项收敛成可逐路验收的 formal 输入，但不会修改 runtime、workflow、安装器、用户指南或发布状态。

## 2. 技术背景

**文档语言**：简体中文 Markdown/YAML
**主要依赖**：现有 `USER_GUIDE.zh-CN.md`、三类 GitHub workflow、release/tag/checksum 记录、ProgramService 真值库存
**存储**：无新持久化状态；仅复用 `specs/`、`program-manifest.yaml` 与现有 roadmap
**测试**：AI-SDLC constraints/plan/truth 验证与仓库 Program Manifest 固定库存回归
**目标平台**：合同覆盖 Windows AMD64、macOS arm64、Linux AMD64；本 formal 批次不运行平台 E2E
**约束**：绑定 `origin/main@2e507df62c65cdd6d3137764bb492dc445a82074`；忽略本地材料/产品站分支；保留 D2 的 16 个 blocker；不得进入 execute

本工作项没有 runtime 数据模型、API 或迁移，因此不另建 `research.md`、`data-model.md` 或第二套计划目录。路线实体与证据字段已直接定义在 canonical `spec.md` 中，避免文档膨胀和双轨真值。

## 3. 宪章与 ROI 门禁

| 门禁 | 计划响应 |
|---|---|
| 用户价值优先 | 以首次用户可完成安装/接入/恢复为唯一核心价值，不以 LOC、工件数量或 close 计数作为成功标准 |
| 真值可复核 | 所有结论绑定远端主线、正式 release/tag、workflow/run 或仓库路径；间接 evidence 不升级为 `proven` |
| 阶段隔离 | 当前只完成 formal/admission；runtime/workflow/release 需新的 execute 授权 |
| 防膨胀 | 12 条路线共用 1 份合同和至多 6 个共性缺口；后续只提出 1 个最小薄片 |
| 有界对抗评审 | 本批进行一次独立 formal/ROI 评审；只修 P0/P1 或直接影响真值的 P2，不为细枝末节无限迭代 |
| 历史真值保护 | 不删除 16 个 Program Truth blocker，不回填历史执行日志，不创建 `development-summary.md` 美化 close 层 |
| 单批原子提交 | formal 文档、roadmap、manifest、库存期望和 execution log 作为一个语义批次提交 |

## 4. 文件范围

### 4.1 允许修改

```text
specs/222-first-user-twelve-route-e2e-contract/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md

docs/FRAMEWORK_ROADMAP.zh-CN.md
program-manifest.yaml
.ai-sdlc/project/config/project-state.yaml
tests/integration/test_repo_program_manifest.py  # 仅固定库存期望
.ai-sdlc/state/codex-handoff.md                  # continuity
.ai-sdlc/state/resume-pack.yaml                  # continuity
.ai-sdlc/work-items/222-first-user-twelve-route-e2e-contract/
├── codex-handoff.md                             # scoped continuity
└── resume-pack.yaml                             # scoped continuity
```

只通过 `workitem link` 更新 checkpoint 的可选 `linked_wi_id / linked_plan_uri`；不得为了 scoped continuity 篡改旧 `current_stage` 或历史 feature。

### 4.2 禁止修改

```text
src/
.github/workflows/
USER_GUIDE.zh-CN.md
scripts/installer/
docs/releases/
既有 specs/*/task-execution-log.md
Program Truth 分类器与 16 个 blocker
```

## 5. 阶段计划

### Phase 0：基线冻结

**目标**：记录精确远端 main、当前正式 release/tag、现有 Program Truth 基线和排除范围。
**产物**：`spec.md` 的真值基线、范围和状态语义。
**验证**：`git rev-parse HEAD`、`git diff --check`、远端/发布证据对账。
**回退**：删除 WI222 formal 批次即可恢复，不影响 runtime。

### Phase 1：十二路线合同与证据普查

**目标**：定义 R01–R12 和每路线 12 个字段；把现有指南、workflow 与 release evidence 逐路映射。
**产物**：`spec.md` 的路线表、状态表、6 个共性缺口。
**验证**：R01–R12 各出现且仅有一条状态记录；`proven/partial/missing` 语义可独立复核。
**回退**：若证据不足则降级状态，不得补写推测性 evidence。

### Phase 2：对抗 ROI 与最小薄片决策

**目标**：验证 P3 是否值得继续，限制后续实现体量，并只保留一个可独立验收的薄片。
**产物**：formal ROI、Go/No-Go、退出条件和后续建议。
**验证**：建议不引入第二套状态机/ledger，不复制 12 套 workflow，不越过 runtime 授权。
**回退**：评审发现 ROI 不成立时，把 P3 标记为 No-Go/needs_user，不以“已经写了文档”为继续理由。

### Phase 3：真值同步与 formal 收口

**目标**：同步 roadmap、Program Truth 清单、固定库存测试和 continuity，完成独立 formal 评审。
**产物**：roadmap 状态、manifest snapshot、execution log、handoff。
**验证**：下列命令全部通过；评审无可操作问题后才提交/PR。
**回退**：仅回退本批记录与固定库存期望，不影响既有工作项和发布。

## 6. 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|---|---|---|
| 十二路线完整性 | 对 R01–R12 表格计数与唯一性复核 | `rg` 检查 route ID 与状态 |
| 无假 `proven` | 逐路核对 12 字段和现有 workflow 能力 | 独立只读 formal 评审 |
| 防实现膨胀 | 文件范围 diff + 共性缺口/薄片计数 | constraints 与评审止损 |
| Program Truth 稳定 | `program truth sync --dry-run` 后执行同步并核对库存 | `test_repo_program_manifest.py` |
| 既有发布/历史保护 | diff 确认无 runtime/workflow/release/历史 log 改动 | `program validate` 与 `verify constraints` |

## 7. 验证命令

验证 profile 为 `code-change`，原因仅是固定库存回归期望随新增 WI222 变化；产品 runtime 和测试逻辑保持不变。

```powershell
uv run ai-sdlc verify constraints
uv run ai-sdlc workitem plan-check --wi specs/222-first-user-twelve-route-e2e-contract
uv run ai-sdlc program validate
uv run ai-sdlc program truth sync --dry-run
uv run ai-sdlc program truth sync --execute --yes
uv run pytest tests/integration/test_repo_program_manifest.py -q
uv run pytest tests/integration/test_github_workflows.py -q
uv run ruff check tests/integration/test_repo_program_manifest.py
git diff --check
```

若 CLI 子命令参数与当前源码帮助不一致，以 `uv run ai-sdlc <command> --help` 的实际 schema 为准，并在 execution log 记录替代命令，不自行发明参数。

## 8. 开放问题与阶段门

| 问题 | 当前结论 | 阻塞阶段 |
|---|---|---|
| 是否立即实现完整 12 路 workflow | 否；先 formal/admission，再单独批准最小薄片 | runtime execute |
| D2 是否先补 5 个历史能力缺口 | 否；维持 11/16 与 16 blockers，除非用户明确优先 v0.9.9 | v0.9.9 |
| 是否用新增 ledger/状态机管理路线证据 | No-Go；先复用现有 workflow/run/release evidence | design/execute |
| 是否补写 WI222 development summary | No-Go；formal 未执行 runtime，不能虚增 close materialization | close |

## 9. 后续最小薄片（未授权执行）

在本 formal 通过后，只建议一个候选：**复用现有 release artifact smoke，定义最小 route receipt，并先让 R02（Windows AMD64 / 已有项目 / 在线）在正式 release event 中满足 12 字段**。R02 已有 `init/adopt`、`Result / Next` 和业务文件保留基础，新增价值集中在正式 asset SHA256、主动恢复和版本绑定，复用率最高。

薄片完成后立即进行半天 Lean/ROI 复核：若 receipt 可被 macOS/Linux 与离线路线复用且新增维护面有界，再扩展矩阵；否则 No-Go 或重新定界。未获得新的 execute 批准前，本计划停在 formal 收口。
