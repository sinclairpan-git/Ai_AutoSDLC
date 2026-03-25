# T10 可移植性审计（主表 P1/P2 已关闭；根目录 PRD 改版已于 2026-03-25 落地）

**工作项**：001-ai-sdlc-framework · **任务**：Task 6.1  
**目的**：识别将 **Cursor 或单一 IDE** 作为**唯一**落地路径的表述或实现，改为多平台与 IDE 解耦。

## 审计表

| 路径 | 问题摘要 | 优先级 | 建议修订 | 状态 |
|------|----------|--------|----------|------|
| `cursor/rules/ai-sdlc.md`（仓库根示例） | 与包内 `adapters/cursor` 同源；description 曾暗示绑定 Cursor | P1 | 已与 `src/ai_sdlc/adapters/cursor/rules/ai-sdlc.md` 对齐为「可选适配」 | 已同步源模板 |
| `docs/USER_GUIDE.zh-CN.md` §2 | 需强调 CLI/rules 为真值 | P1 | 已增「规范入口（与 IDE 无关）」段，指向 `agent-skip-registry` 与 `pipeline` 条款 17 | 已关闭 |
| `cursor/commands/dev.autopilot.md` | description 写「Cursor 适配器」 | P2 | 已改为「可选：Cursor 命令示例」并指向 autopilot/CLI 真值 | 已关闭 |
| `tests/integration/test_cli_init.py` | 断言输出含 `cursor`（安装规则提示） | — | 保留：测试安装行为，非用户唯一路径 | 关闭 |
| `src/ai_sdlc/integrations/ide_adapter.py` | 检测 `.cursor` 等 | — | 保留：可选适配逻辑；文档侧标明非必需 | 关闭 |
| `autopilot.md` | 已声明工具无关 | — | 无改 | 关闭 |
| `rules/multi-agent.md` / `src/ai_sdlc/rules/multi-agent.md` | 列举 Cursor capability | P2 | 已补充「其他 IDE/Agent 等价能力」说明 | 已关闭 |
| 根目录 `AI-SDLC 全自动化框架 产品需求文档（PRD）.md` | 列举 Cursor 等为 Agent 示例 | P2 | §12.3 增补「示例宿主、非唯一路径」及规范真值指向 CLI/rules/用户指南 | **已关闭**（2026-03-25） |

## 检索命令（复核）

```bash
rg -i "cursor|plan mode" --glob '!**/.cursor/**' --glob '!**/node_modules/**'
```

## 宪章收口（批次 2026-03-24）

对齐 **Task 6.1** 与宪章 MUST-2 / `pipeline.md` 条款 11（完成前验证）的**补做证据**（针对本批已合并仓库的变更；**不表示** T10 审计表全部关闭）。

| 检查项 | 命令 / 说明 | 结果 |
|--------|-------------|------|
| 全量自动化测试 | `uv run pytest` | **485 passed**（约 2026-03-24） |
| 静态检查（Python） | `uv run ruff check src tests` | **All checks passed** |
| 本批变更范围 | 无 `.py` 行为语义变更；含 `pipeline.md`、`agent-skip-registry.zh.md`、Cursor 适配器 Markdown、`USER_GUIDE` 片段、`cursor/` 与 `.cursor/` 规则示例同步 | 见下方变更登记 |
| Task 6.1 验证条款 | 审计表 P1/P2 文档项已关闭；根目录 PRD 延期已登记 | **完成（文档/规则范围）** |

## 元问题：计划 frontmatter 与事实不同步（非 Cursor 专属）

| 项 | 内容 |
|----|------|
| **现象** | `.cursor/plans/*.md`（或他 IDE 计划）中 `todos` 仍为 `pending`，仓库已含对应实现或文档。 |
| **原因** | 无合并门禁；元数据第二真值未纳入 DoD；与 checkpoint/项目状态不对齐同构。 |
| **解决办法（已入 spec，实现禁止在本审计批次内执行）** | **FR-085～087**、**plan.md 增量设计**、**tasks Task 6.2**；详见 [`agent-skip-registry.zh.md`](../../src/ai_sdlc/rules/agent-skip-registry.zh.md)「现象：计划待办与实现事实不对齐」。 |

## 变更登记

- 2026-03-24：创建本文件；新增 `rules/agent-skip-registry.zh.md`、`pipeline.md` 条款 16–17；更新 Cursor 适配器模板 `adapters/cursor/rules/ai-sdlc.md`。
- 2026-03-24：**收口**：全量 pytest + ruff；本文件增加「宪章收口」节；`agent-skip-registry` 补登「先交付后补测」偏离行。
- 2026-03-24：增加「元问题：计划 frontmatter」节；spec/plan/tasks 增加 FR-085～087 与 Task 6.2；**外部计划** frontmatter 已与事实同步（见该 plan 文件 `overview`）。
- 2026-03-24：**Task 6.2 文档子产物**：`USER_GUIDE` §2.1、`tasks-template` related_plan、`docs/plan-check-cli-spec.zh.md`、`docs/pull-request-checklist.zh.md`（无实现）。
- 2026-03-24：**Task 6.1 文档类 P2 收口**：`cursor/commands/dev.autopilot.md`、`rules/multi-agent.md` 与 `src/ai_sdlc/rules/multi-agent.md`；`pipeline.md` 条款 **18**（close 前对账）；本工作项 [`tasks.md`](tasks.md) 增加 **frontmatter `related_plan`**。根目录 PRD 仍为**延期**（不纳入本批次修订）。
- 2026-03-25：按工程约束补做本任务独立收口：核验审计表状态、追加 `task-execution-log.md` 批次记录、独立 git commit（不夹带后续任务）。
- 2026-03-25：**关闭 PRD 延期行**：根目录 PRD §12.3 增加多平台示例与真值说明；与本表「已关闭」一致。
