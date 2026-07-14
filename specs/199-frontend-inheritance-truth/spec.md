# 功能规格：Frontend Inheritance Truth Closure

**功能编号**：`199-frontend-inheritance-truth`
**创建日期**：2026-07-13
**状态**：设计评审中
**父任务**：WI-196 GAP-09 / T53A

## 1. 目标与根因

关闭 `frontend-mainline-delivery` 上误报的 `frontend_inheritance:generation` 与 `frontend_inheritance:quality` 发布 blocker，同时保留真实消费项目的继承门禁。

已核验根因：该 release capability 的 16 个 `spec_refs` 均在规范 footer 与 `program-manifest.yaml` 中显式声明 `frontend_evidence_class: framework_capability`，但 `_release_gate_frontend_inheritance_blockers()` 仍用当前仓库是否存在前端 solution snapshot 判断发布状态。框架仓库没有选择某个项目级前端方案，因此两个只适用于消费项目实例的继承状态被错误提升为框架能力发布 blocker。

## 2. 范围与非目标

### 2.1 范围

- 只为 `frontend-mainline-delivery` 增加 fail-closed 的继承需求判定：只有 capability 存在、`spec_refs` 非空、每个 ref 都能映射到 manifest spec，并且每个 canonical spec footer 与 manifest mirror 都能直接解析且精确等于 `framework_capability` 时，才允许以 `waived_for_framework_capability` 标识项目实例继承要求不适用；footer missing/empty/malformed、mirror 冲突或其他 capability 一律不豁免。
- waiver 生效前必须独立于 solution snapshot 校验 generation/quality framework artifacts：generation 全套 artifact 必须可加载并通过模型 schema，`page_schema_ids` 必须精确对应已加载 page schema，provider manifest/declared install strategy 必须存在且 provider/packages 一致，delivery entry 与 theme adapter 必须非空；quality、page schema 与 theme governance 必须可加载，quality matrix/flow/verdict 跨引用必须通过同文件私有 internal-coherence validator 校验。公开 project validator 仍强制 solution snapshot。
- waiver 只影响 release truth 对项目实例 inheritance blocker 与对应 remediation guidance 的使用；原始 generation/quality handoff、状态计算、消费项目 fail-closed 语义不变。
- truth surface 必须公开 waiver 原因，不能把 `blocked` 静默改成 `unknown`，也不能伪造 `inherited`。
- 更新 truth snapshot，并证明只移除 GAP-09 对应的两个 blocker。

### 2.2 非目标

- 不运行 `program solution-confirm --execute --yes`，不为框架仓库伪造前端 solution snapshot。
- 不生成前端代码，不运行 managed delivery apply，不选择或变更 Vue/React/provider/style pack。
- 不修改 generation/quality artifact schema、handoff command、质量平台或浏览器门禁。
- 不关闭 GAP-10 adapter blocker 或 GAP-11 source inventory 债务。
- 不新增公共抽象、模块、依赖、配置项、schema 或通用 waiver DSL。

## 3. 冻结方案

### 3.1 采用：基于 canonical evidence class 的 release-scope waiver

框架能力的 truth/close/verify refs 已承担框架可发布性的机器证据；项目 solution snapshot 只证明具体消费项目采用了哪套前端方案。release gate 必须区分这两类证据：

1. `frontend-mainline-delivery` 的每个 canonical footer 与 manifest mirror 都直接解析为 `framework_capability`：发布 truth 记录 `waived_for_framework_capability`，不附加项目实例 inheritance blocker/guidance；validation blocker 仍独立参与 audit。
2. waiver 场景的 generation/quality framework artifact 分别做 snapshot-independent schema + semantic health 检查；generation 至少校验 page schema 精确集合、provider manifest、declared install strategy/provider/packages、非空 delivery entry 与 theme adapter；缺失、不可读、malformed 或跨引用失败时使用 `frontend_framework_artifact:generation|quality` 阻断，不能被 waiver 掩盖。
3. 任一 `consumer_adoption`、空值、缺失映射、混合分类、canonical/mirror 冲突或未知 capability：requirement 为 `project_instance_required`；`unknown`、`not_inherited`、`blocked` 均使用既有 `frontend_inheritance:generation|quality` 阻断，只有 `inherited` 放行。
4. 其他 release capability 不进入该判定，不输出 frontend inheritance requirement；现有 validate/constraints blocker 始终保留。

### 3.2 拒绝方案

- **给框架仓库落 solution snapshot**：把框架能力仓库错误绑定为一个 Vue3/PrimeVue 消费项目，并触发前端方案确认与后续项目级 artifact 维护。
- **将无 snapshot 状态改成 `unknown`**：会利用当前“只阻断 blocked”实现细节静默绕过门禁，不能证明证据适用性。
- **直接删除 inheritance release gate**：会使真实消费项目的 provider、library、quality 继承漂移失去 fail-closed 保护。

## 4. 用户故事与验收场景

### US-01：框架能力发布真值不依赖消费项目快照（P0）

作为框架维护者，我希望框架能力由正式 spec、truth-check、close-check 与 constraints 证明，而不是被迫为仓库选择一个项目级前端方案。

1. **Given** `frontend-mainline-delivery` 的全部 canonical footer 与 mirrors 均直接解析为 `framework_capability` 且 framework artifacts schema/semantic health 通过，**When** 计算 release truth，**Then** inheritance requirement 为 `waived_for_framework_capability`，且不产生两个 GAP-09 blocker。
2. **Given** generation/quality manifests 存在但 solution snapshot 缺失，**When** 单独运行两个 handoff/status surface，**Then** 保留当前 blocked/missing-snapshot 诊断，不伪造 inherited。
3. **Given** framework generation 或 quality artifact 缺失、malformed、page/provider/package 语义漂移、delivery entry missing/empty 或跨引用损坏，**When** 计算 release truth，**Then** 产生对应 `frontend_framework_artifact:*` blocker，即使 evidence class 全部为 framework capability 也不得发布。

### US-02：消费项目继承保护不降级（P0）

作为使用 AI-SDLC 的项目团队，我希望前端 generation/quality 必须继续继承已确认方案，缺失或漂移时仍阻断。

1. **Given** capability 含 `consumer_adoption` spec，且对应状态为 `unknown`、`not_inherited` 或 `blocked`，**When** 计算 release truth，**Then** 均产生对应 inheritance blocker；只有 `inherited` 放行。
2. **Given** spec ref 缺失、分类为空或混合，**When** 计算 release truth，**Then** 不得获得 waiver。
3. **Given** canonical footer missing/empty/malformed 或与 manifest mirror 漂移，**When** 计算 requirement 与 validate/constraints，**Then** requirement 为 `project_instance_required`，validation blocker若存在仍可见且不能同时公开错误 waiver。

### US-03：关闭结果可审计且可回退（P0）

1. **Given** 修复前 truth snapshot，**When** 同步并审计修复后 snapshot，**Then** `snapshot_state=fresh`，只移除 `frontend_inheritance:generation` 与 `frontend_inheritance:quality`。
2. **Given** GAP-10/GAP-11 尚未关闭，**When** GAP-09 合并，**Then** adapter blocker 与 source inventory 精确计数保持不变或由独立证据解释，不能借本项清仓。
3. **Given** 回退整个 WI-199 closure、重开父项 GAP-09 并重跑 truth sync/audit，**Then** 两个 GAP-09 blocker 可重现且 closure 文档不再声称 closed，证明回退边界独立。

## 5. 需求与兼容合同

- **FR-01**：系统必须只对 `PROGRAM_FRONTEND_MAINLINE_DELIVERY_CAPABILITY_ID` 逐 ref 直接解析 canonical footer 与 manifest `frontend_evidence_class`，二者都等于 `framework_capability` 才判定 release-scope waiver。
- **FR-02**：waiver 必须满足全称条件；空 capability、空 refs、缺失 ref、空值、未知值、`consumer_adoption` 或混合分类一律不豁免。
- **FR-03**：waiver 必须作为结构化 truth surface 字段公开，值固定为 `waived_for_framework_capability`；需要项目继承时固定为 `project_instance_required`。
- **FR-04**：waiver 生效且 framework artifacts 健康时不得附加 inheritance blocking refs 或建议用户运行无法修复框架仓库状态的两个 handoff command；artifact 不健康时必须附加 `frontend_framework_artifact:*` blocker，并在 truth audit explain/next step 中公开 family、canonical artifact path 与具体校验原因。不得自动 materialize；安全处置固定为按该路径从 owning work item/revert 恢复已知良好 artifact，再运行 truth audit。
- **FR-05**：原始 `build_frontend_inheritance_status_surface()`、generation handoff、quality handoff 的状态和错误合同不得改变。
- **FR-06**：消费项目原始状态判定与 next action 不得改变；release gate 必须把 `unknown`、`not_inherited`、`blocked` 都视为未满足，仅 `inherited` 放行。
- **FR-07**：现有 truth-check、close-check、verify refs、capability closure 与 manifest validation 仍必须全部参与 release audit。
- **FR-08**：实现必须复用 `ProgramManifest` / `ProgramCapabilityRef` / `ProgramSpecRef`，不得新增第二 evidence registry。
- **FR-09**：`frontend_quality_platform.py` 必须提取私有 internal-coherence helper，覆盖 matrix/page/style/browser/viewport/flow/verdict；公开 `validate_frontend_quality_platform()` 继续要求非空 solution snapshot 并叠加 effective-style 检查，不能暴露 framework bypass API。只有已确认 waiver 的 `ProgramService` 私有路径可调用 internal helper。
- **FR-10**：generation framework health 必须校验完整 artifact load、page schema ID 精确集合、provider manifest 与 install strategy provider/packages 一致、delivery entry 非空且 theme adapter 非空；不得硬编码 provider/entry、猜 suffix 或新建映射表。至少一个 schema-valid semantic drift fixture必须阻断。

### 兼容与非回归合同

- **CC-01**：CLI/JSON 既有字段形状保持兼容，仅新增可选 requirement 字段。安全兼容例外：consumer `unknown` / `not_inherited` 从未满足但可能 exit 0 收紧为 release blocker，truth audit 预期可从 0 变 1；`inherited`、framework healthy 与非前端 capability 场景退出行为不变。
- **CC-02**：真实 `consumer_adoption` 的 unknown/not-inherited/blocked fixtures 必须全部 release-blocked。
- **CC-03**：分类无法肯定时 fail-closed；helper 必须直接解析 canonical footer，不允许推断、slug 猜测、只信 mirror、仅依赖 active-WI constraints 或默认 waiver。
- **CC-04**：不触发 solution confirmation、managed apply、文件下载、host mutation 或浏览器副作用；公开 quality validator 不接受 `None`，消费项目不存在新的校验旁路。
- **CC-05**：GAP-10/GAP-11 truth 不得被本项修改为 ready。
- **CC-06**：所有 CLI 产生的非授权 adapter 文件副作用必须核对并精确恢复。

## 6. 预算、停止与回退

- 风险等级：L2（发布真值语义修复，无外部运行时 API 变更）。
- 产品 allowlist：`src/ai_sdlc/core/program_service.py`、`src/ai_sdlc/core/frontend_quality_platform.py`；合计净新增不超过 55 LOC。
- 测试 allowlist：`tests/unit/test_program_service.py`、`tests/unit/test_frontend_quality_platform.py`；后者只新增一个负向用例，断言 public validator 传 `None` 必须失败，用于锁死禁止合同而非支持 bypass。如 repo-level truth map 必须调整，可增加 `tests/integration/test_frontend_mainline_blocker_execution_map.py`；合计新增不超过 160 LOC。
- 禁止新增产品/测试文件；文档、manifest truth 与 handoff 不计产品 LOC，但必须可追踪。
- 若需要 frontend solution execute、改 schema、改 handoff 语义、增加公共模块，或无法在预算内保持 consumer fail-closed，则停止并重新设计。
- 回退：revert 整个 WI-199 closure（产品、测试、manifest snapshot 与本项/父项 closure 文档），将 WI-196 GAP-09 重新标为 open，再同步/audit truth；不依赖数据迁移、双写或 feature flag。

## 7. 成功标准

- **SC-01**：设计与最终分支各由兼容安全 Agent、精简效率 Agent 对同一 hash/HEAD 独立评审，均明确 `PASS` 且无可操作问题。
- **SC-02**：定向测试证明 framework-only 分类加 schema/semantic health、framework artifact 损坏阻断、consumer 三种非 inherited 状态、canonical footer missing/empty/malformed、mirror conflict 与 missing/mixed fail-closed、原始 handoff 状态不变。
- **SC-03**：完整 pytest、Ruff、constraints、`git diff --check` 全部通过。
- **SC-04**：truth snapshot fresh；frontend release capability 不再包含两个 GAP-09 refs，且没有新增 blocker/validation error。
- **SC-05**：产品净新增 ≤55 LOC、测试新增 ≤160 LOC，无新模块/依赖/config/schema。
- **SC-06**：PR Codex review 无可操作问题，required checks 全绿，合并后在 `origin/main` 重跑定向测试与 truth audit。

---
related_doc:
  - "specs/196-ai-sdlc-lean-code-self-reduction-governance/spec.md"
  - "specs/168-frontend-generation-constraints-delivery-context-binding-baseline/spec.md"
  - "specs/169-frontend-quality-platform-delivery-context-binding-baseline/spec.md"
  - "src/ai_sdlc/core/frontend_gate_verification.py"
  - "src/ai_sdlc/core/program_service.py"
frontend_evidence_class: "framework_capability"
---
