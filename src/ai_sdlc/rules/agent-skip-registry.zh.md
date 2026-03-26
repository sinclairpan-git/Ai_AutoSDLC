# 代理执行偏离登记（人机共读）

> 目的：当 **自动化代理或协作者在回顾中发现曾跳过** `pipeline.md` / 宪章中的强制顺序或真值约定时，**立即落盘一条记录**，避免只在对话里消散。登记用于驱动 **正在开发的框架**（CLI、门禁、preflight、文档）持续硬化，**不替代** MUST-2 下的自动化测试。

> 历史兼容说明：自 2026-03-26 起，新增的“框架缺陷 / 违约 -> backlog”主入口迁移到 [`docs/framework-defect-backlog.zh-CN.md`](../../docs/framework-defect-backlog.zh-CN.md)。本文件保留历史审计语义、legacy 根因归类与迁移来源；如需继续推进旧条目，请在新 backlog 中追加结构化条目，并回填 `legacy_ref`。

## 使用方式

1. **何时写**：自检、代码审查、或用户指出「未按约束执行」之后 **48 小时内**（或同一迭代内）追加一行登记表。
2. **写什么**：跳过的事实、根因归类、对框架的建议（优先可机器验证项）。
3. **不写**：与具体商业项目无关的人身评价；重复条目可合并为「再次出现 +1」。

## 根因归类（便于统计）

- **A**：隐性目标（求快、求一次答完）压过强制顺序  
- **B**：软约束（仅 Markdown）无失败即停的硬闸门  
- **C**：词汇碰撞（如 *plan* 指宿主提纲 vs `specs/.../plan.md`）  
- **D**：工具语义误解（如 `stage run` vs `run`）  
- **E**：多真值来源下选错依据（checkpoint vs 手写 YAML）  
- **F**：宿主平台专有流程被当成通用规范  
- **G**：其他（注明）
- **H**：**计划/任务状态未与仓库事实同步**（例如：开发已完成但 `.cursor/plans/*.md` 的 `todos` 仍为 `pending`，或 `tasks.md` 未更新却合并 PR）

## 现象：计划待办与实现事实不对齐（2026-03-24 复盘）

| 维度 | 说明 |
|------|------|
| **现象** | 仓库中规则、用户指南、适配器模板等**已变更**且测试曾通过，但 **IDE 计划文件** frontmatter 中多条 todo 仍为 `pending`，与事实不一致；与「checkpoint vs project-state」类似，属于 **第二套元数据未对齐**。 |
| **原因** | **H** + **A/B**：无「合并前必须更新计划状态」的硬闸门；完成度默认记在对话/脑中；**MUST-4** 未覆盖「外部计划文件」这一条目。 |
| **已采取办法（文档/流程）** | ① 本登记本条；② **spec FR-085～087** 与 **tasks Task 6.2** 将「对账」纳入 P1 需求与设计；③ **plan** frontmatter **已与事实同步** `status`（`completed` / `in_progress` / `pending`）。 |
| **框架侧长期杜绝（不替代测试）** | **FR-087** 可选只读 CLI 对账；**FR-085** DoD；**related_plan** 契约；CI/PR 模板提醒。 |

## 工程纪律复盘（2026-03-26）— 映射 SDLC 与杜绝方式

| 维度 | 说明 |
|------|------|
| **现在** | 用户明确要求「先按工程框架约束、需求落盘再动手」时，执行侧仍易**下意识先改代码**，再补文档与测试证据。 |
| **问题** | 违背 `pipeline.md` 阶段顺序与 `batch-protocol.md` **Step 1 预读**、**文档契约先行**（Batch 9 已写死 6.11→6.12）；把「会话内完成感」当成「仓库内法定完成」。 |
| **根因** | **A**（求快压过顺序）+ **B**（Markdown 规则无硬闸时仅靠自觉）+ **C**（把「继续下一项」误解为可直接进入 EXECUTE）。 |
| **映射到本框架阶段** | 正确顺序应为 **decompose**（`tasks.md` 含 AC）→ **verify**（门函数/测试设计）→ **execute**（实现）；需求细化属于 **design/decompose** 产出，不应在 **execute** 中边想边写。 |
| **杜绝（流程）** | ① 用户指令含「仅文档 / 先 spec-plan-tasks」时，**禁止**修改 `src/`、`tests/`（除非任务本身为代码任务且 `tasks.md` 已勾选就绪）；② 先追加或更新 `spec.md` / `plan.md` / `tasks.md`，再进入实现批次；③ 将「规则过重/作用域过大」类反馈**先记入 spec（FR）与 tasks**，再开实现 PR。 |
| **杜绝（产品化）** | 见本仓库 `spec.md` **FR-095～FR-098** 与 `tasks.md` **Batch 10**（规则作用域收敛、归档噪音、命令真值来源）。 |

## 登记表

| 日期 (UTC) | 发现阶段 | 跳过内容摘要 | 根因 | 框架强化建议 | wi_id | 状态 |
|------------|----------|--------------|------|--------------|-------|------|
| 2026-03-24 | 对话/规划 | 在 design 未落到 `tasks.md`（decompose）前催促「执行」直改产品代码 | A, C | `pipeline.md` 已增条款 16–17；推进 `preflight` / execute 前校验 `tasks.md` |  | 已记录 |
| 2026-03-24 | 对话/规划 | 用「退出 plan mode」等 **单平台** 表述描述通用下一动作 | F | 计划与文档改为「verify 就绪后 / execute 阶段」等中性表述；T10 全仓审计 |  | 已关闭 |
| 2026-03-24 | 执行/回顾 | **未先跑全量 pytest、未完成 Task 6.1 verify 全项收口**即合并多文件规则/文档/适配器变更并声称交付 | A, B | CI 或 preflight 强制 `pytest`（全量或仓库约定子集）；文档-only 变更也要求落盘 verify 证据路径；`portability-audit-T10.md` 与 tasks 对齐 |  | 已补测+已对齐记录 |
| 2026-03-24 | 执行/回顾 | **计划文件 `todos[].status` 未随开发进度更新**，与仓库事实长期错位 | H, A | **FR-085～087** + **Task 6.2**（DoD、`related_plan`、可选 `plan-check`）；合并前模板；plan frontmatter 已与事实同步 |  | 已记录+已入 spec |
| 2026-03-25 | 执行/回顾 | 实现 **FR-087/088/089**（`workitem plan-check`、`workitem link`、`verify constraints`）过程中，**未同步**按 `pipeline.md` 做「批次归档 execution-log + 六维 code-review 落盘」、**未 git commit/push** 收口；用户手册 §2.1 仍写「plan-check 未实现」与事实漂移 | A, B, H | ① 交付后立刻更新 `USER_GUIDE.zh-CN.md` / PR 清单，避免「未实现」残留；② 合并前跑 `pytest`+`ruff`+`verify constraints`+（如有）`plan-check`；③ Agent 会话内将「声称完成」与「归档/commit」拆成显式 checklist；④ 本条登记 |  | 已补文档+已登记 |
| 2026-03-26 | 回顾 | 用户要求「先按框架约束把优化项转为需求/plan/tasks 再考虑是否动手」时，仍易**先默认进入编码**；与「归档先于继续」「契约先于实现」冲突 | A, B, C | 见本节表「工程纪律复盘」；需求落盘 **FR-095～098**、`tasks.md` **Batch 10**；执行前强制核对当前任务是否为 **仅文档** | `001-ai-sdlc-framework` | 已记录 |

（后续行由上表续写。）

## 与产品路径的对应

- **规范真值**：CLI、`checkpoint.yml`、`src/ai_sdlc/rules/`、用户指南；各 IDE 目录下文件为**可选适配**。  
- **执行顺序**：`init → refine → design → decompose → verify → execute → close`（见 `pipeline.md`）。
