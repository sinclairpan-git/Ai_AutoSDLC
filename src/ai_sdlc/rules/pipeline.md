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

16. **宿主规划与仓库阶段区分**：任意 IDE/Agent 宿主环境中的「实施规划」或对话内方案**不等于**仓库内流水线阶段已完成。规划收敛后的法定下一步是 **design/decompose**（如直接在 `specs/<WI>/` 下初始化或更新 `spec.md` / `plan.md` / `tasks.md`），再 **verify**，再 **execute**。当用户明确要求「**先文档 / 先需求 / 先 spec-plan-tasks**」时，默认动作必须停在 **design/decompose**，不得直接改产品代码；禁止将「计划已定」直接等同于可以修改产品源代码。对新 framework capability 而言，canonical 入口应优先是 direct-formal work item（例如在仓库已完成 `ai-sdlc init .` 的 formal bootstrap 前提下，再执行 `ai-sdlc workitem init` 直接生成 `specs/<WI>/spec.md + plan.md + tasks.md`）；若仓库只有历史 `.ai-sdlc` 痕迹但缺 `.ai-sdlc/project/config/project-state.yaml`，必须先补 formal bootstrap，不得把缺文件状态误解成可直接进入 direct-formal。`docs/superpowers/specs/*.md` 与 `docs/superpowers/plans/*.md` 若存在，只属于 design input / auxiliary reference，不属于法定执行真值，也不是必须先写的一套 canonical 文档。在 `specs/<WI>/tasks.md` 落成前，不得把 superpowers plan 表述为“可直接进入实施”的入口。若当前对话内容无法被当前仓库中的 canonical artifact、active work item、规则对象或用户明确指定路径稳定映射，默认动作必须收缩为**停写 + 边界澄清 + 只读核对工作区**：先确认未落盘，再说明“当前内容不属于本项目或尚未证明归属”，不得为了继续推进而自行补出写入目标。禁止把 `docs/superpowers/*`、历史设计稿目录或其他语义相似路径当成归属不明内容的 fallback write target；这些路径即使存在，也只允许作为 `related_doc / related_plan / auxiliary reference`。进一步地，宿主 skills / workflow 的 terminal state、`plan complete and saved` 一类提示、以及 `Inline Execution / Subagent-Driven` 等执行选项，都只代表**宿主工作流提示**，不构成 execute 授权；若用户仍在 review spec/plan、补文档反馈或讨论流程约束，默认动作必须继续停在文档/规则层，而不是把编码表述成自然下一步。只有同时满足 **用户明确要求进入实现** 与 **仓库 execute 前置已满足** 时，才允许从 plan/review 状态进入开发编码；若宿主 workflow 与仓库阶段真值冲突，必须以仓库真值为准并显式说明“尚未获得 execute 授权”。

17. **框架缺陷 / 违约转待办**：当出现以下任一情形时，须在 `docs/framework-defect-backlog.zh-CN.md` 追加一条结构化 backlog：① 用户明确要求记录该缺陷/违约；② `gate` / `verify` / `close-check` 等门禁因框架缺口、状态漂移、规则矛盾而阻断；③ 自检或回顾发现曾跳过本文件或宪章中的强制顺序。即使该违约已被门禁、review 或自检及时拦下，并在当前迭代内修复，只要它真实出现过且暴露出框架缺口，仍必须登记，不得因“已修复”而省略。顺序固定为：`识别违约 -> 写 backlog 条目 -> 只读校验 -> 再讨论补正/修复/计划`，不得继续停留在口头承认或等待用户二次提醒。条目至少包含：现象、触发场景、影响范围、根因分类、`未来杜绝方案摘要`、建议改动层级、`prompt / context`、`rule / policy`、`middleware`、`workflow`、`tool`、`eval`、风险等级、可验证成功标准、是否需要回归测试补充；其中 `未来杜绝方案摘要` 负责概括防复发方案，而 `rule / policy`、`middleware`、`workflow`、`tool`、`eval` 应明确写出未来杜绝同类问题的具体落点。历史兼容来源见 `rules/agent-skip-registry.zh.md`。该登记作为框架演进输入，**不替代** `verification.md` 与自动化测试。

18. **平台实现与框架契约必须分层**：`src/ai_sdlc/rules/*`、`templates/*`、`presets/*` 以及其他框架通用产物，只允许表达平台无关的 SDLC 契约，例如阶段门禁、审查要求、验证要求、trace/evidence 约束与 canonical artifact 规则。不得把 GitHub 专有流程或命令（如 Pull Request、GitHub Actions、`gh pr`、`@codex review`、GitHub merge 语义）写成框架通用要求。GitHub、GitLab、公司内代码仓、内部 CI、外部 review 服务等平台实现细节，只允许落在仓库本地工程层配置或该仓库的自迭代文档中；若在框架文档里举例，必须明确标注为“宿主平台示例”且保持可替换为等价实现。

19. **close 前工作项、计划与分支处置对账**：进入 **close** 阶段前，须核对 `specs/<WI>/tasks.md` 中任务完成情况、（若存在）`related_plan` 指向的外部计划之待办状态，以及与当前 work item 明确关联的 branch/worktree disposition 是否已与 Git 事实一致，或已登记延期/保留原因；与「归档先于继续」一致。若当前 work item 仍有关联 scratch/worktree 分支相对 `main` 存在未处置偏离，不得把 close 表述为已完整收口。

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
- 禁止把 GitHub / Pull Request / GitHub Actions / `@codex review` / `gh pr` 等宿主平台专有流程写成框架通用规则、模板默认值或预设要求
