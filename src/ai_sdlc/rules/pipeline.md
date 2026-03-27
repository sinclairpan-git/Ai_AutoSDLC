# 流水线总控规则

> 本规则在执行 SDLC 流水线的任何阶段时生效。

## 产出语言（默认）

凡由本流水线**生成或写入**、**面向人阅读**的 Markdown（包括 `specs/**` 下 spec/plan/tasks、`.ai-sdlc/memory/**` 宪章与基线、项目 README、产品说明等），**正文与章节标题须使用简体中文**；路径、命令、代码标识符、HTTP 方法、JSON 字段名、接口名等保持原样。可参考仓库 `templates/constitution-template.zh.md`、`templates/readme-template.zh.md` 的结构与语气。

## 强制行为

1. **宪章至上**：在任何阶段生成任何产物之前，必须先读取 `.ai-sdlc/memory/constitution.md` 并确保产物符合宪章所有 MUST 规则。宪章违规是 CRITICAL 级别问题，不允许自动跳过。

2. **阶段门禁不可绕过**：每个阶段结束后必须检查门禁条件。门禁失败时必须先尝试自动修复，修复失败才阻断。绝不允许"先跳过门禁，后面再补"。

3. **产物可追溯**：所有产出文件必须能追溯到 PRD 中的具体条目。如果生成了无法映射到 PRD 的内容，视为范围蔓延。

4. **配置优先于硬编码**：技术栈信息从 `tech-stack.yml` 读取，歧义从 `decisions.yml` 查询，阶段定义从 `pipeline.yml` 读取。不允许在命令执行过程中硬编码这些信息。

5. **归档先于继续**：完成一个阶段或批次后，必须先完成归档（写 execution-log），再进入下一阶段/批次。不允许"先做完再一起归档"。

6. **执行模式必须尊重**：每个阶段门禁通过后，必须检查 `pipeline.yml` 的 `execution_mode` 和 `stage_overrides`（以及运行时覆盖）。如果当前阶段为 `confirm` 模式，必须输出确认卡并暂停等待用户指令。绝不允许在 `confirm` 模式下跳过人工确认直接进入下一阶段。用户可以在任何时刻通过发送消息打断 auto 模式切换为 confirm，也可以在确认卡中选择「自动」切回 auto。

7. **状态面板必须输出**：当 `status_dashboard.enabled = true` 时，在每个阶段入口、关键步骤完成、门禁通过/失败时输出状态面板。面板格式见 `autopilot.md`「实时状态面板」章节。

8. **PRD 引导必须完成**：流水线启动前，必须执行 PRD 引导协议（`rules/prd-guidance.md`）。只有用户明确确认 PRD 已完善并选择启动后，才能进入 Stage 0。断点恢复和增量 Feature 可跳过或简化引导。

9. **调试必须系统化**：EXECUTE 阶段的任何测试失败或异常行为，必须遵循 `rules/debugging.md` 的四阶段流程（根因调查 → 模式分析 → 假设验证 → 实现修复）。禁止跳过根因调查直接尝试修复。

10. **代码审查必须执行**：EXECUTE 阶段每个批次 commit 前，必须执行 `rules/code-review.md` 的六维度自审。审查未通过的 Critical 问题必须修复后才能 commit。

11. **完成前必须验证**：声称任何完成状态（批次完成、阶段完成、流水线完成）之前，必须执行 `rules/verification.md` 的门函数。没有新鲜的验证证据，不能声称完成。

12. **分支策略必须遵守**：Stage 1-4 在 `design/NNN` 分支执行，Stage 5-6 在 `feature/NNN` 分支执行。切换分支前必须 commit 所有变更；切换分支后必须校验基线完整性。详见 `rules/git-branch.md`。

13. **多 Agent 并行必须安全**：当启用多 Agent 并行时，必须遵循 `rules/multi-agent.md` 的文件隔离、接口隔离、数据隔离要求。合并前必须通过冲突检测、构建验证、全量回归和逻辑一致性检查。发现问题时自动降级为串行。

14. **场景路由必须遵守**：入口须区分标准 SDLC、线上热修复短路径与开发中范围变更（见 `rules/scenario-routing.md`）。热修复不得被完整 PRD 流程不必要阻塞；范围变更在 EXECUTE 中必须通过上升流程更新设计产物，禁止仅在 feature 分支私自改写 spec/plan。

15. **存量工程认知基线必须优先**：在已有业务代码的仓库上走标准 SDLC 时，须先完成 `rules/brownfield-corpus.md` 要求的 `.ai-sdlc/memory/engineering-corpus.md`，再进入 Stage 1。探索须分层有界（Tier 1/2/3，深度与变更范围挂钩），禁止用无预算的通读全仓库代替。corpus 已存在时，Step 0 须验证 §2 仓库地图与实际一级目录的一致性。

16. **宿主规划与仓库阶段区分**：任意 IDE/Agent 宿主环境中的「实施规划」或对话内方案**不等于**仓库内流水线阶段已完成。规划收敛后的法定下一步是 **decompose**（如更新 `specs/<WI>/tasks.md`），再 **verify**，再 **execute**；禁止将「计划已定」直接等同于可以修改产品源代码。

17. **框架缺陷 / 违约转待办**：当出现以下任一情形时，须在 `docs/framework-defect-backlog.zh-CN.md` 追加一条结构化 backlog：① 用户明确要求记录该缺陷/违约；② `gate` / `verify` / `close-check` 等门禁因框架缺口、状态漂移、规则矛盾而阻断；③ 自检或回顾发现曾跳过本文件或宪章中的强制顺序。即使该违约已被门禁、review 或自检及时拦下，并在当前迭代内修复，只要它真实出现过且暴露出框架缺口，仍必须登记，不得因“已修复”而省略。条目至少包含：现象、触发场景、影响范围、根因分类、建议改动层级、`prompt / context`、`rule / policy`、`middleware`、`workflow`、`tool`、`eval`、风险等级、可验证成功标准、是否需要回归测试补充；其中 `rule / policy`、`middleware`、`workflow`、`tool`、`eval` 应明确写出未来杜绝同类问题的方案。历史兼容来源见 `rules/agent-skip-registry.zh.md`。该登记作为框架演进输入，**不替代** `verification.md` 与自动化测试。

18. **close 前工作项与计划对账**：进入 **close** 阶段前，须核对 `specs/<WI>/tasks.md` 中任务完成情况与（若存在）`related_plan` 指向的外部计划之待办状态是否已与 Git 事实一致，或已登记延期原因；与「归档先于继续」一致。

## 阶段执行顺序

严格按以下顺序执行，不允许跳阶段：

```
init → refine → design → decompose → verify → execute → close
```

唯一例外：如果 `specs/NNN/` 中已有某阶段的产物（如 spec.md 已存在），可以从下一个阶段开始，但必须先验证已有产物的门禁条件。

> **与 Runner 对齐（Task 6.6）**：`SDLCRunner` 以 `checkpoint.yml` 中的 `current_stage` 为起点顺序执行门禁，**不会**仅依据「磁盘上已有 spec/plan/tasks」自动推断应处于哪一阶段。将「已有产物」落实为合法下一阶段的常规做法是：更新断点 / 经 `init`·`recover` 等路径使 checkpoint 与事实一致，并通过对应阶段门禁。对照表见 `specs/001-ai-sdlc-framework/research-pipeline-vs-runner.md`。

## 上下文传递

每个阶段启动时必须读取的上下文：

| 阶段 | 必读 | 选读 |
|------|------|------|
| init | PRD, presets/*.yml；存量项目时须 `rules/brownfield-corpus.md` 并产出 `memory/engineering-corpus.md` | 项目根目录 .md 参考文档 |
| refine | PRD, constitution, templates/spec-template.md；若 `memory/engineering-corpus.md` 存在则必读 | decisions.yml |
| design | spec.md, constitution, tech-stack.yml, templates/plan-template.md；若 `memory/engineering-corpus.md` 存在则必读 | decisions.yml, PRD |
| decompose | spec.md, plan.md, data-model.md, contracts/, templates/tasks-template.md | research.md, quickstart.md, `memory/engineering-corpus.md`（任务路径应落在 corpus 已映射区域） |
| verify | spec.md, plan.md, tasks.md | constitution |
| execute | tasks.md, PRD, constitution, templates/execution-log-template.md | decisions.yml |
| close | task-execution-log.md, tasks.md, templates/summary-template.md | spec.md, plan.md, `memory/engineering-corpus.md`（若存在则增量刷新） |

## 禁止行为

- 禁止在没有读取宪章的情况下生成任何设计或代码产物
- 禁止修改宪章（宪章只能在 Stage 0 建立）
- 禁止在 EXECUTE 阶段修改 spec.md 或 plan.md（发现设计问题应阻断并记录）
- 禁止生成没有文件路径的任务
- 禁止在测试未通过的情况下标记任务为已完成
- 禁止在没有运行全量回归的情况下提交 git
