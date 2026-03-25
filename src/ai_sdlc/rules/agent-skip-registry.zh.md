# 代理执行偏离登记（人机共读）

> 目的：当 **自动化代理或协作者在回顾中发现曾跳过** `pipeline.md` / 宪章中的强制顺序或真值约定时，**立即落盘一条记录**，避免只在对话里消散。登记用于驱动 **正在开发的框架**（CLI、门禁、preflight、文档）持续硬化，**不替代** MUST-2 下的自动化测试。

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

## 登记表

| 日期 (UTC) | 发现阶段 | 跳过内容摘要 | 根因 | 框架强化建议 | 状态 |
|------------|----------|--------------|------|--------------|------|
| 2026-03-24 | 对话/规划 | 在 design 未落到 `tasks.md`（decompose）前催促「执行」直改产品代码 | A, C | `pipeline.md` 已增条款 16–17；推进 `preflight` / execute 前校验 `tasks.md` | 已记录 |
| 2026-03-24 | 对话/规划 | 用「退出 plan mode」等 **单平台** 表述描述通用下一动作 | F | 计划与文档改为「verify 就绪后 / execute 阶段」等中性表述；T10 全仓审计 | WIP |
| 2026-03-24 | 执行/回顾 | **未先跑全量 pytest、未完成 Task 6.1 verify 全项收口**即合并多文件规则/文档/适配器变更并声称交付 | A, B | CI 或 preflight 强制 `pytest`（全量或仓库约定子集）；文档-only 变更也要求落盘 verify 证据路径；`portability-audit-T10.md` 与 tasks 对齐 | 已补测+已对齐记录 |
| 2026-03-24 | 执行/回顾 | **计划文件 `todos[].status` 未随开发进度更新**，与仓库事实长期错位 | H, A | **FR-085～087** + **Task 6.2**（DoD、`related_plan`、可选 `plan-check`）；合并前模板；plan frontmatter 已与事实同步 | 已记录+已入 spec |
| 2026-03-25 | 执行/回顾 | 实现 **FR-087/088/089**（`workitem plan-check`、`workitem link`、`verify constraints`）过程中，**未同步**按 `pipeline.md` 做「批次归档 execution-log + 六维 code-review 落盘」、**未 git commit/push** 收口；用户手册 §2.1 仍写「plan-check 未实现」与事实漂移 | A, B, H | ① 交付后立刻更新 `USER_GUIDE.zh-CN.md` / PR 清单，避免「未实现」残留；② 合并前跑 `pytest`+`ruff`+`verify constraints`+（如有）`plan-check`；③ Agent 会话内将「声称完成」与「归档/commit」拆成显式 checklist；④ 本条登记 | 已补文档+已登记 |

（后续行由上表续写。）

## 与产品路径的对应

- **规范真值**：CLI、`checkpoint.yml`、`src/ai_sdlc/rules/`、用户指南；各 IDE 目录下文件为**可选适配**。  
- **执行顺序**：`init → refine → design → decompose → verify → execute → close`（见 `pipeline.md`）。
