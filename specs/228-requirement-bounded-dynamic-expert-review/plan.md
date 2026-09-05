---
related_plan: "docs/FRAMEWORK_ROADMAP.zh-CN.md"
---
# 实施计划：Requirement Loop 有界动态专家评审纵向薄片

**编号**：`228-requirement-bounded-dynamic-expert-review` | **日期**：2026-09-05
**规格**：`specs/228-requirement-bounded-dynamic-expert-review/spec.md`
**状态**：G1 formal/admission；实现等待双专家一致 PASS

## 1. 概述

本计划先归档 Requirement-only 动态专家合同，再用一个独立候选完成只读 review 输入、严格临时 execution、最多两个角色、两轮上限和 freeze 漂移保护。实现后必须用三个盲测价值回放作 Go/No-Go；未证明增量价值时不合并 runtime，也不扩展其余 Loop。

## 2. 技术背景

**语言/版本**：Python 3.11+、Typer、Pydantic
**现有承载**：`RequirementIntake`、`LoopRun/LoopRound`、`LoopPolicyProfile.max_rounds`、`LoopArtifactStore`、Requirement CLI namespace
**存储**：复用 requirement 现有 artifact；review input/roles 为瞬时返回值，execution 为宿主临时文件，freeze 只记 digest/roles/time
**测试**：unit + CLI integration + three isolated blind value replays + full regression
**目标平台**：macOS/Linux/Windows；命令兼容 `ai-sdlc` 与 `python -m ai_sdlc`
**约束**：Requirement-only、1–2 roles、最多 2 rounds、一个 terminal PR、`src/ai_sdlc/**` gross additions ≤600

## 3. 宪章检查

| 宪章门禁 | 计划响应 |
|---|---|
| MUST-1 MVP/范围严控 | 只做 Requirement 薄片；其余四类 Loop 均不接线 |
| MUST-2 关键路径可验证 | 以 execution completeness、role cap、no-write、digest drift、round cap 和三个盲测回放验证 |
| MUST-3 范围/验证/回退 | review 能力集中且无新持久化；No-Go 时可整体 revert |
| MUST-4 状态落盘 | 只由现有 LoopRun/LoopRound/intake/freeze writer 落盘；临时 execution 不冒充持久状态或 authority |
| MUST-5 用户保留关闭权 | reviewer 只读，只有显式 user confirmation 的原 freeze writer 能关闭 |
| 代码纯洁/精简 | 不复制参赛版通用平台；不为未来四 Loop 抽象；gross additions 超过 600 行即 No-Go |

## 4. 冻结设计

### 4.1 公共命令

```text
ai-sdlc loop requirement review --loop-id <id> [--json]
ai-sdlc loop requirement freeze --loop-id <id> --review-result-file <path> --yes
```

- `review` 是纯读取命令，不调用 writer adapter，不落盘；输出包含 canonical projection、摘要、当前轮、风险信号、角色、execution schema 和宿主下一步。
- active agent 为每个必需角色启动独立只读上下文，并生成一个大小受限的普通非 symlink 临时 execution 文件。
- `freeze` 在任何写入前重建同一输入，要求 execution 的 digest/round 与当前值一致、角色集合精确、全部 completed 且没有 `blocker/required` finding。
- 新 loop 强制新合同；legacy open/closed loop 保持旧 freeze 兼容并明确提示，不批量迁移。

### 4.2 输入摘要

摘要使用 canonical JSON + SHA-256，字段冻结为：

```text
schema version + loop id + loop type + current round
+ RequirementIntake 的 work item/source kind/source path/raw text/summary/questions/acceptance/review_required
```

同一 canonical projection 直接出现在 review 输出中，reviewer 不再打开摘要之外的 Markdown 内容；artifact paths 只作定位信息。不纳入时间戳、AI-SDLC 版本或渲染 Markdown 的重复字节；不绑定 Git HEAD，因为 Requirement 可能在非 Git 新项目中运行。读取复用现有固定 Requirement 路径和模型校验，并交叉检查 loop/intake identity。freeze 在最终写入前重建 projection；本薄片只保证单 active-writer 下的顺序漂移检测，不宣称解决任意多进程 TOCTOU。

### 4.3 临时 execution 合同

`RequirementReviewExecution` 绑定 `input_digest` 与 `round_number`，每个 selected role 恰有一个结果：`role_id`、`completed|failed`、结构化 findings。finding 只允许 `blocker|required|advisory`、位置、说明和建议。freeze 对失败、缺角色、重复角色、未知角色或 actionable finding 一律拒绝；`advisory` 不转为关闭 authority。临时文件不进入 Loop 目录、不写 history，`RequirementFreeze` 只记录最终 digest、实际角色和 review 时间。该合同是本地结构化流程证据，不是密码学身份、签名或远端 attestation。

### 4.4 角色路由

- Primary：始终为 Requirement quality expert，关注目标、边界、验收可判定性和隐含假设。
- Cross-risk：只从小型有序白名单选择一个，初始族限定为：
  1. security/privacy/authorization；
  2. data integrity/migration/compatibility；
  3. concurrency/reliability；
  4. public API/integration；
  5. frontend/accessibility。
- 规范化冻结为 NFKC + casefold、英文 token 边界与中文完整短语；命中多个族时只取最高优先级，不评分、不学习、不路由 provider/model。
- 该表只是“是否需要第二视角”的 heuristic，不证明风险已被完整识别；primary 仍审全部需求。无法识别时只返回 primary。

### 4.5 两轮、澄清与幂等

- 新 loop 创建 `review_required=true`；旧 artifact 缺字段时为 false。
- 首次 idea 及 `needs_user` 阶段补 acceptance/澄清均留在 round 1；幂等输入不增轮。
- `needs_review` 后修改必须同时提供当前 completed execution；若 canonical 内容变化且当前为 round 1，append 现有 `LoopRound` 形成 round 2。failed/缺失 execution 不能驱动修订。
- round 2 后任何基于评审的第三个实质版本返回 `needs_user` 且不写 round 3；freeze 关闭实际 `current_round`，不能强制回写 1。

## 5. 目标源码结构与预算

```text
src/ai_sdlc/core/requirement_review.py       # 瞬时模型、摘要、风险/角色选择
src/ai_sdlc/core/requirement_loop.py         # 新旧合同、复用轮次、execution 校验
src/ai_sdlc/cli/loop_cmd.py                  # review 与 result-file 参数接线
src/ai_sdlc/core/loop_status.py              # 当前下一步命令文本
src/ai_sdlc/core/design_contract_loop.py     # 未冻结 requirement 的迁移提示
src/ai_sdlc/core/verify_constraints.py       # 必需命令 token
src/ai_sdlc/rules/pipeline.md                # 平台无关的 active-agent 执行规则
tests/unit/test_requirement_review.py
tests/unit/test_requirement_loop.py
tests/integration/test_cli_loop.py
README.md
USER_GUIDE.zh-CN.md                          # 最短迁移与使用路径
```

产品源码 allowlist 冻结为以上 7 个 `src/ai_sdlc/**` 路径：只有前三个可含新行为，后三个 Python 文件只允许同步命令/约束文本，pipeline 只允许平台无关调度规则。测试与两份用户文档不计入 600 行，但必须逐项对应验收矩阵。用 `git diff --numstat <formal-merge-base>...HEAD -- src/ai_sdlc` 计算 gross added lines；大于 600 或修改 allowlist 外产品源码即 No-Go。

## 6. 阶段计划

### Phase 0：Formal 冻结与双专家评审

**目标**：冻结问题、最小方案、兼容选择、投入和 No-Go。
**产物**：spec/plan/tasks/log、Program Truth、continuity。
**验证**：constraints、plan-check、manifest regression、两位对抗专家最多两轮达成一致。
**回退**：revert formal PR；无 runtime 影响。

### Phase 1：核心薄片（独立 implementation PR）

**目标**：先用红灯测试固定瞬时 input/execution、role cap、digest drift、legacy compatibility 与 round cap，再实现最小代码。
**产物**：冻结文件集内的 Python、测试与用户文档。
**验证**：定向 unit/integration、no-write 快照、execution 负向矩阵、legacy/new freeze、现有 requirement 回归。
**回退**：整体 revert implementation PR；无 schema migration 或遗留 review artifact。

### Phase 2：真实回放与 Go/No-Go

**目标**：在三个全新隔离项目中先冻结 baseline writer 输出，再把隐藏 seed/预期答案的输入交给独立专家；至少一个是 clean 负向对照。
**产物**：task-execution-log 内的命令、输入规模、耗时、exit code、baseline、专家原始输出、独立裁决、修订与终态回执。
**验证**：路由合同测试不计 ROI；有效增量 finding 必须同时满足 baseline 未覆盖、事实正确、影响验收或风险边界、可执行、经独立裁决。至少两个样例通过，clean 对照及全体样例均无错误 actionable finding。
**回退**：不满足阈值即 No-Go，候选 runtime 不得合并，停止 P4 扩展且不新建立项继续优化。

### Phase 3：实现评审与合并

**目标**：由产品/ROI 与架构/代码纯洁两个身份对抗评审，最多一轮整改复审后形成一致终态。
**产物**：恰好一个 terminal PR；Go 时包含 runtime 与闭环记录，No-Go 时移除候选 runtime 后只归档终止事实，不再创建后续 records PR。
**验证**：Ruff、全量 pytest、constraints、program validate、exact-head Codex review 与 required checks。
**回退**：仍有 Critical/Important、回归或边界违约即 No-Go，不创建第二实现 PR。

## 7. 关键路径验证矩阵

| 关键路径 | 主验证 | 次验证 |
|---|---|---|
| 始终一个 primary、至多一个 cross-risk | unit 参数化 | 三类真实回放 |
| review 全程只读 | 文件树/hash 前后快照 | Git status + 隔离项目检查 |
| execution 确实完整 | 缺失/失败/角色/actionable finding 负向矩阵 | 盲测原始输出 |
| 输入变化使旧 execution 失效 | core + CLI integration | 真实回放 stale freeze |
| 两轮上限与澄清幂等 | requirement loop unit | needs_user 澄清 + round 1→2→拒绝 3 |
| 原 freeze writer 唯一关闭 | 现有回归 + 新 CLI 测试 | artifact 终态检查 |
| 新旧兼容 | legacy open/closed/new 参数化测试 | 旧 fixture + 新隔离项目 |
| 跨平台/打包可用 | full suite + required checks | source/wheel smoke（若触发发布） |

## 8. 开放问题与冻结答案

| 问题 | 冻结答案 | 阻塞阶段 |
|---|---|---|
| 是否让旧 `freeze --yes` 静默绕过 review？ | 旧 intake 缺 `review_required` 时显式走 legacy compatibility；新 loop 强制 execution | 实现 |
| 如何证明评审而不造 authority？ | freeze 同次消费严格临时 execution；它是结构化本地证据，不是密码学证明 | 实现 |
| 是否持久化 findings/PASS？ | 不保存完整结果/history；freeze 只记最终 digest/roles/time | 无 |
| 是否现在抽通用五 Loop kernel？ | 否；Requirement ROI 通过后另做独立 Go/No-Go | 无 |
| 三次盲测未达到价值阈值怎么办？ | runtime 不合并；terminal PR 只归档 No-Go，停止扩展 | 验收 |

## 9. 实施顺序

1. Formal 双专家评审一致 PASS 并合入 main。
2. 从 fresh main 创建唯一 implementation branch/PR，以测试先行冻结合同。
3. 实现 Requirement 专属薄片并控制 production LOC/文件预算。
4. 运行三个真实回放，记录增量 finding 与 No-Go 判据。
5. 完成双专家实现评审、Codex exact-head review、required checks；PASS 才合并。
