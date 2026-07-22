# 产品需求文档：消费项目与框架约束隔离

**功能编号**：`218-consumer-framework-constraint-isolation`
**创建日期**：2026-07-21
**状态**：formal review candidate
**类型**：production_issue
**基线**：`origin/main@1de1c3269a76e8ca885a940bd561f32cc7612534`
**父项**：无；本项是正常缺陷修复，不属于已关闭的 WI196 减重路线

## 1. 问题与用户价值

`verify constraints` 当前把框架发布、文档、离线包、adapter template、历史 feature-contract
附件和普通消费项目约束装配在同一条路径。Agent Store 这类已经接入 AI-SDLC 的普通项目只因存在
`README.md`、`USER_GUIDE.zh-CN.md`、`AGENTS.md` 或局部 `src/ai_sdlc/rules/*`，就会被要求满足
Ai_AutoSDLC 自身的版本、发布与规则 parity。

当前 main 的纯函数复现对 Agent Store 稳定产生 17 条 blocker：10 条 release/version/offline、3 条
beginner guide、1 条 frontend instruction、3 条 framework rule/checklist。历史证据表明该问题至少从
v0.7.9 延续到 v0.9.6。

本需求要让普通项目只承担自身治理约束，同时保证 Ai_AutoSDLC 的框架自验证门禁不减少、不静默降级，
并以最少的新代码完成隔离。

## 2. 目标与非目标

### 2.1 P0 目标

1. 普通消费项目不再收到 AI-SDLC 框架发布、框架文档、adapter template、规则 parity 或内部 WI 附件 blocker。
2. Ai_AutoSDLC checkout 继续执行当前全部 framework-only 检查。
3. consumer 的 constitution、活动 spec、tasks acceptance、doc-first、branch lifecycle、frontend evidence、
   comment/text quality 等通用门禁保持有效。
4. collect、structured report、verification gate context 三条路径使用同一仓库范围判定。
5. 修复保持私有、机械、可回退；不引入新的身份子系统或规则引擎。

### 2.2 明确非目标

- 不处理 `verify constraints` 默认写 telemetry 的独立问题。
- 不更新 AI-SDLC 版本、发布文档、adapter 模板或用户项目 AGENTS 内容。
- 不修改 Agent Store 产品代码或其主动配置的项目规则。
- 不处理用户明确要求复制规则的参赛仓库。
- 不重构 4,900+ 行 `verify_constraints.py`，不迁移附件系统，不建立 capability registry。
- 不新增减重 work item，不重新开启 WI196 路线。

## 3. 冻结设计

### 3.1 仓库范围判定

新增一个私有 helper，读取两个稳定信号：

1. `pyproject.toml` 的 `project.name` 等于 `ai-sdlc`；
2. `src/ai_sdlc/__init__.py` 存在。

判定合同：

| project.name | package sentinel | 结果 |
|---|---|---|
| 命中 | 存在 | framework；执行 common + framework-only |
| 不命中/缺失 | 不存在 | consumer；只执行 common |
| 命中 | 不存在 | identity blocker；只执行 common |
| 不命中/缺失 | 存在 | identity blocker；只执行 common |

XOR 状态必须 fail closed，但不得倾倒整组 framework blocker。判定不得依赖 README、USER_GUIDE、
目录名、Git remote、`.git`、当前分支或用户本机配置。

`pyproject.toml` 读取失败、TOML 语法错误、`project` 非 mapping、`name` 非字符串或空白时，name 信号按
未命中处理且 helper 不得抛出异常：sentinel 不存在时按 consumer 只跑 common；sentinel 存在时产生唯一
identity blocker并只跑 common。

### 3.2 检查所有权

Common 至少保留：

- constitution presence；
- `_formal_artifact_target_blockers`；
- `collect_comment_deletion_blockers` / `collect_text_quality_blockers`；
- checkpoint `spec_dir`、tasks acceptance、doc-first task scope；
- `_frontend_evidence_class_blockers`；
- `_skip_registry_mapping_blockers`；
- `_branch_lifecycle_blockers`。
- `_frontend_public_primevue_import_boundary_report` 及其 check object、source 和 context payload；
- verification governance 与 phase-1 provenance 等不依赖内部 WI 身份的基础 context 字段。

Framework-only 至少包含：

- framework defect backlog / backlog breach reference；
- release version/docs、README/USER_GUIDE/beginner CLI truth；
- root AGENTS、adapter templates、pipeline instruction parity；
- reconcile smoke、doc-first framework surfaces、verification profiles、framework regression guards；
- framework feature-contract registry、release-gate surface；
- 仅由内部 WI `003/012/014/018/073/148/149/150/151/153/189–195` 驱动的附件、coverage、check objects、
  verification sources 和 context payload。

Consumer 不执行静态 adapter/template 全文 token parity；adapter 安装与 canonical 内容漂移继续由现有
`adapter status` 职责处理。consumer 的实际 solution-confirm、frontend evidence 和当前工作项验收门禁
不得因此关闭。

### 3.3 三入口一致性

同一个私有判定 helper 必须被以下三处复用：

- `collect_constraint_blockers()`；
- `build_constraint_report()`；
- `build_verification_gate_context()`。

consumer report/context 只能声明实际执行过的 check objects、coverage gaps、release surface 和 verification
sources。不得仅过滤 blocker 而保留虚假的框架检查元数据。

## 4. 代码纯洁性合同

| 合同 | 硬约束 |
|---|---|
| LC-01 | implementation 产品代码只允许修改 `src/ai_sdlc/core/verify_constraints.py` |
| LC-02 | implementation 新行为断言只允许修改 `tests/unit/test_verify_constraints.py`；两个既有 integration 文件仅可补显式 framework identity fixture setup |
| LC-03 | 不新增产品模块、配置、依赖、公开 API、Enum、dataclass、role model、plan/registry/dispatcher |
| LC-04 | 新增私有 helper 不超过 2 个；目标为 1 个 `_repository_scope` |
| LC-05 | 产品 raw additions 硬上限 80 行；预计 55–77 行；超限必须停止并重新压缩设计 |
| LC-06 | 不做无关格式化、命名清理、telemetry 修改或附件重构 |
| LC-07 | 优先重排现有调用并复用常量，生产净增应尽量接近零 |
| LC-08 | formal 只允许 canonical records、manifest/state/handoff 和 `tests/integration/test_repo_program_manifest.py` 机械计数 |

测试代码不计入 runtime 负担，但不得复制 Agent Store 全仓或建立第二套 integration harness。
LC-02 的 integration 例外仅限 `tests/integration/test_cli_verify_constraints.py` 与
`tests/integration/test_cli_index_gate.py`：对明确验证 framework-only `003/012/018/073` 或 framework
backlog/profile/doc-first surfaces 的 fixture，只可创建 `pyproject.toml`（`[project].name = "ai-sdlc"`）和
`src/ai_sdlc/__init__.py`。不得修改断言或预期输出，不得使用 module/global autouse；downstream/relinked
`003` 以及 consumer `003/012` 编号碰撞 fixture 必须保持无 framework identity。

## 5. 功能需求

- **FR-218-001**：系统必须用 §3.1 双信号判定 framework/consumer/XOR。
- **FR-218-002**：XOR 必须产生唯一、可诊断的 identity blocker，且不得执行 framework-only 检查。
- **FR-218-003**：consumer 的 collect/report/context 不得包含 framework-only blocker、attachment、coverage、
  check object、release surface 或 verification source。
- **FR-218-004**：framework 的现有 framework-only 检查结果必须保持不变。
- **FR-218-005**：consumer 通用治理门禁必须保持有效，不能以“隔离”为名整体跳过约束验证。
- **FR-218-006**：consumer 内部 WI 编号碰撞不得激活 Ai_AutoSDLC 历史附件或 release gate。
- **FR-218-007**：legacy/custom AGENTS 不得因缺少当前框架全文 token 被 `verify constraints` 强制升级。
- **FR-218-008**：实现与 formal 必须满足 LC-01～LC-08；任何代码预算或范围超限均阻断合入。
- **FR-218-009**：无效 pyproject 不得导致异常退出；必须按 §3.1 的 sentinel 二态语义处理。
- **FR-218-010**：consumer 必须保留 PrimeVue import-boundary 与基础 governance/provenance context。

## 6. 用户故事与验收场景

### US-1：普通项目获得项目级验证（P0）

作为 Agent Store 维护者，我希望 `verify constraints` 只验证本项目应承担的治理规则，避免为了通过门禁
复制 AI-SDLC 发布文档、版本号、离线 workflow 或内部规则文件。

**独立验收**：使用 Agent Store-shaped fixture，普通 README/USER_GUIDE/legacy AGENTS/局部 rules 不产生
任何 framework-only finding。

### US-2：框架自身门禁不降级（P0）

作为 AI-SDLC 维护者，我希望同一命令在框架源码仓继续检查 release/docs/offline/templates/rules，避免
隔离修复成为绕过框架自验证的开关。

**独立验收**：当前框架 fixture 保持通过；逐项破坏既有框架真值时，原测试仍精确阻断。

### US-3：报告与执行事实一致（P0）

作为审计者，我希望 report/context 只声明实际执行的检查，避免 consumer 虽无 blocker 却仍声称完成
framework checks。

**独立验收**：consumer 的 structured report 与 gate context 不含 framework-only objects/sources/payload。

## 7. 成功标准

- **SC-218-001**：Agent Store-shaped fixture 的 framework-only findings 从 17 降为 0。
- **SC-218-002**：双信号 `both/neither/name-only/sentinel-only` 四态测试全部通过。
- **SC-218-003**：routing-census 证明 consumer 三入口调用全部 common、零 framework helper；framework 调用
  两组；XOR 只产生一个 identity blocker。`003` fixture 非空覆盖 feature coverage/release surface，`012`
  fixture 非空覆盖 attachment/check object/source/context；consumer 均无框架污染。
- **SC-218-004**：consumer 人为制造一个 common blocker 时仍被阻断；现有 PrimeVue consumer
  report/context 回归保持通过。
- **SC-218-005**：当前 `tests/unit/test_verify_constraints.py` 全绿，框架发布/附件既有测试无回归。
- **SC-218-006**：生产代码满足 LC-01～LC-07；raw additions ≤80，新增 helper ≤2。
- **SC-218-007**：Ruff、完整 pytest、`uv run ai-sdlc verify constraints`、program validate/truth 和
  required CI 全绿。
- **SC-218-008**：两位本地对抗 reviewer 对同一 committed+clean identity 均 `PASS0/findings=0`。
- **SC-218-009**：malformed/non-string pyproject × sentinel present/absent 参数化测试符合 §3.1 且不崩溃。
- **SC-218-010**：真实 Agent Store current-source 纯函数连续两次结果相同，framework-only findings 为0，
  且运行前后 status、tracked diff 与所有 dirty-path 内容指纹不变。

## 8. 风险与回退

- 双信号同时被协调修改时可能降级为 consumer；本项用真实 framework checkout 身份不变量测试防止意外，
  不宣称抵抗同时篡改实现与测试。
- 合法 vendored 完整 `src/ai_sdlc` 但项目名不同会得到一个 identity blocker；错误文案必须展示两个信号。
- legacy consumer 不追溯强制当前 adapter instruction token，这是兼容性选择；实际行为门禁仍保留。
- 实现只允许一个原子产品/测试 commit；`git revert` 必须完整恢复修复前行为和测试基线。
