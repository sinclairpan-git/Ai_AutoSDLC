# ADR-001：`pipeline` 规则「已有产物」例外 vs Runner 行为对照

**工作项**：`001-ai-sdlc-framework`  
**关联任务**：Task 6.6（仅文档）  
**日期（UTC）**：2026-03-25  
**状态**：草案（仅对照与建议，不引入产品行为变更）

---

## 背景

`src/ai_sdlc/rules/pipeline.md` 要求严格阶段顺序，并允许一种例外：

- 若 `specs/NNN/` 中**已有某阶段产物**（例如 `spec.md` 已存在），可以从下一个阶段开始，**但必须先验证已有产物的门禁条件**。

但当前实现的 Runner（`src/ai_sdlc/core/runner.py`）与 `ai-sdlc gate check <stage>`（`src/ai_sdlc/cli/sub_apps.py`）是**可按 stage 单独调用**的，这可能导致“用户只跑 execute gate”而绕过 decompose 的事实门禁。

本 ADR 的目标是做**对照表**，明确：

- 规则条文的意图
- 当前代码行为
- 潜在缺口（若存在）
- 建议如何在后续任务中对齐（例如 Batch 8 的 Task 6.9）

---

## 对照表

| 规则条文 / 约束 | 期望（意图） | 当前代码行为（观察点） | 缺口/风险 | 建议（落地任务） |
|---|---|---|---|---|
| `pipeline.md`：阶段门禁不可绕过 | 任意阶段结束都必须 gate；失败先修复再阻断 | Runner 按 `PIPELINE_STAGES` 顺序调用 gate；但 CLI 支持 `gate check execute` 单独运行 | 用户/脚本可能只跑 `execute`，未显式验证 `decompose` | 在 `ExecuteGate` 前置只读检查 decompose（Task 6.9） |
| `pipeline.md`：已有产物可从下阶段开始，但要先验证门禁 | 复用已有产物时，必须 gate 验证一致性 | `gate check <stage>` 只验证该 stage 的局部条件 | 可能跳过“已有产物的门禁条件”链路验证 | close-check / stage-run 模式可强制链式 gate（Batch 9/后续） |
| `verification.md`：无全量回归不能提交 git | 任何声称完成前必须有新鲜证据 | repo 目前依赖人为执行 `pytest/ruff` | 容易“先交付后补测”复发 | 通过 `workitem close-check` 将证据落盘并检查（Batch 9 / Task 6.12） |
| `code-review.md`：commit 前六维自审并落盘 | 每批 commit 前写审查摘要 | 当前靠执行者自觉写到 execution-log | 容易缺失或漂移 | execution-log 模板字段化 + close-check 检查（FR-092 / Batch 9） |

---

## 结论

- 本 ADR **不修改产品行为**，只确认：当前 CLI 允许用户按 stage 单独执行 gate，因此“规则上的顺序约束”需要通过后续任务（Batch 8/9）做硬化，避免被误用绕过。

---

## 后续落地（指向 tasks）

- Batch 8：Task **6.9**（`ExecuteGate` 前置只读检查）
- Batch 9：Task **6.12**（`workitem close-check` 收口检查）、Task **6.11**（模板字段化）

