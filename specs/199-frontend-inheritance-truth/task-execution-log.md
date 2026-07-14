# 执行日志：WI-199 Frontend Inheritance Truth Closure

## 1. Batch 2026-07-13-001：初始化、link 与 before evidence

- 基线：`origin/main@68150d3f5ba128c0e4b44b11b13bc8ad60cc0d63`。
- worktree：`.worktrees/199-frontend-inheritance-truth`。
- canonical branch：`feature/199-frontend-inheritance-truth-docs`；初始 `codex/199-frontend-inheritance-truth-docs` 被 `workitem init` 明确拒绝，未绕过框架分支合同。
- `uv run ai-sdlc workitem init ...` 创建 formal 四件套；`workitem link --wi-id 199-frontend-inheritance-truth --plan-uri specs/199-frontend-inheritance-truth/plan.md` 于 `2026-07-14T01:42:10+00:00` 完成。
- CLI 多次改写 `.cursor/rules/ai-sdlc.mdc`；均作为非授权 adapter 副作用用 `apply_patch` 精确恢复，未纳入设计范围。

### 1.1 修复前运行证据

- `uv run ai-sdlc program generation-constraints-handoff`：exit 1，state `blocked`，work item `017`，provider/delivery 为空，apply state `not_applied`，blocker `frontend_solution_snapshot_missing`。
- `uv run ai-sdlc program quality-platform-handoff`：exit 1，state `blocked`，schema `1.0`、quality artifact diagnostics 存在，blocker `frontend_solution_snapshot_missing`。
- generation manifest 已存在，声明 `public-primevue`、`vue3-public-primevue`、PrimeVue packages、theme adapter 与三个 page schemas。
- quality platform manifest 已存在，声明 schema `1.0` 与三项 matrix；框架仓库未持久化项目级 frontend solution snapshot。
- `program solution-confirm --dry-run` 只做边界预览：推荐 Vue3 / public-primevue / modern-saas，preflight ready；未运行 execute，也未生成/应用前端代码。

### 1.2 Canonical 分类证据

- `frontend-mainline-delivery` 的 16 个 `spec_refs` 在 manifest 中全部为 `frontend_evidence_class: framework_capability`，对应规范 footer 同样受 validate/constraints 镜像规则约束。
- `frontend_gate_verification.py` 已有 `waived_for_framework_capability` 先例：框架能力可免除只属于消费项目实例的 observation attachment，但 consumer adoption 不能豁免。
- 当前 `_release_gate_frontend_inheritance_blockers()` 不读取 evidence class，直接把项目实例 inheritance status 提升为 release blocker，形成 GAP-09。

## 2. Batch 2026-07-13-002：方案冻结

- 采用：仅当 capability/ref/class 全量明确且全部为 `framework_capability` 时，公开 `waived_for_framework_capability` 并跳过不适用的项目实例 inheritance release blocker/guidance。
- 拒绝：为框架仓库落 project solution snapshot；原因是会伪造消费项目身份并触发前端方案确认/维护链。
- 拒绝：把 blocked 改为 unknown 或直接删除 gate；原因是前者利用实现细节 fail-open，后者破坏真实消费项目保护。
- 冻结产品单文件 ≤35 net LOC、测试 ≤120 added LOC；不新增文件、公共 API、依赖、config、schema。
- 下一步：计算设计三件套 hash，启动兼容安全与精简效率两个对抗 Agent；同一 hash 双 PASS 前不写 RED/GREEN 实现。

## 3. Batch 2026-07-13-003：设计 Round 1 对抗评审与处置

- review target hash：`88b774a9e8c54c9924662ccd1f255efed8077969c94e1578217c8360c713cb2c`。
- 兼容安全 Agent：FAIL，4 项 finding；精简效率 Agent：FAIL，2 项 finding。双方独立复算 hash 一致。
- 成立 finding 与处置：
  1. 仅按 evidence class waiver 会掩盖 framework artifacts 损坏：增加 snapshot-independent generation/quality loaders + quality framework-context cross-ref validation，损坏使用专用 blocker。
  2. consumer `unknown/not_inherited` 当前未 release-block：冻结非 waiver 只有 `inherited` 放行，三种未满足状态全部测试。
  3. 只读 manifest mirror 会在 footer conflict 时公开错误 waiver：requirement 增加 validation-aware fail-closed 与冲突 fixture。
  4. rollback 漏 closure docs：改为回退整个 WI、重开父项 GAP-09 并 resync/audit。
  5. `ProgramCapability` 模型名错误：修正为真实 `ProgramCapabilityRef`。
  6. waiver 范围过宽：硬限制 `PROGRAM_FRONTEND_MAINLINE_DELIVERY_CAPABILITY_ID`，其他 capability 不计算/不输出字段。
- 目标三文件已变化，Round 1 verdict 全部失效；计算新 hash 后必须由两个 Agent 重审。

## 4. Batch 2026-07-13-004：设计 Round 2 对抗评审与处置

- review target hash：`45b0c42e2e14dd5c801d03033efa9cdf2a1571a68fdf5dbc8503e3673b745fdd`。
- 兼容安全 Agent：FAIL，4 项 finding；精简效率 Agent：FAIL，1 项 finding。双方独立复算 hash 一致，并确认 Round 1 findings 已实质关闭。
- 成立 finding 与处置：
  1. generation loader 不能发现 schema-valid semantic drift：补 page schema 精确集合、provider manifest、declared strategy/provider/packages、delivery entry/provider 和 adapter 非空检查与 fixture。
  2. footer missing/malformed 未被 requirement 直接确认：helper 改为逐 ref 解析 canonical footer 并与 mirror 对账，不依赖 active-WI constraints。
  3. consumer exit code 兼容承诺冲突：明确 unknown/not-inherited 变为 blocker 是安全收紧的有意兼容例外。
  4. framework artifact 自动修复不安全：禁止无 snapshot materialize；固定只读 artifact-family tests、owning-WI/revert 恢复与 truth audit。
  5. quality validator 测试漏出定向命令：RED/GREEN 与 Phase 3 定向命令均加入 `tests/unit/test_frontend_quality_platform.py`。
- 目标三文件已变化，Round 2 verdict 全部失效；新 hash 必须再次双重评审。

## 5. Batch 2026-07-13-005：设计 Round 3 对抗评审与处置

- review target hash：`50e569b47a72fc39886b4edde6b4a8c25c86127c6db0229638717d624a20047d`。
- 兼容安全 Agent：FAIL，3 项 finding；精简效率 Agent：FAIL，1 项 finding。双方独立复算 hash 一致，并确认 Round 2 findings 已基本关闭。
- 成立 finding 与处置：
  1. 公开 quality validator 接受 `None` 会形成消费旁路：改为同文件私有 internal-coherence helper；public signature/snapshot 强制不变。
  2. fixture-only tests 不能定位当前 root artifact：truth audit guidance 必须直接输出 family、canonical path、reason；按路径恢复 known-good artifact 后重跑 audit，禁止自动 materialize。
  3. FR-10 漏追踪：纳入 T21/T22/T31/T32。
  4. delivery entry/provider 无 snapshot-independent 独立真值：删除猜测性一致性要求，仅冻结 entry 非空；provider/packages 由 provider manifest + declared strategy 对账。
- 目标三文件已变化，Round 3 verdict 全部失效；新 hash 必须再次双重评审。

## 6. Batch 2026-07-13-006：设计 Round 4 对抗评审与处置

- review target hash：`105cce3e80f783606ff33e2f78dc448f47644559c0e0ca0ccf2fe25a72bd587f`。
- 精简效率 Agent：PASS，未发现可操作问题；兼容安全 Agent：FAIL，3 项 finding。目标变化后精简 PASS 自动失效。
- 成立 finding 与处置：
  1. public validator 禁止 `None` 只有文字合同：增加一个运行时负向测试，断言传 `None` 必须失败；不是支持面扩张。
  2. delivery 任意非空语义漂移无法独立证明：验收只冻结 missing/empty；不承诺检测无 canonical carrier 的错误值。
  3. rollback 用户故事残留产品-only：统一为 whole WI closure revert、父项 reopen 与 truth resync/audit。
- 目标三文件已变化，Round 4 verdict 全部失效；新 hash 必须再次双重评审。

## 7. Batch 2026-07-13-007：设计 Round 5 同哈希双 PASS

- review target：`spec.md + plan.md + tasks.md`，按三文件 SHA-256 清单排序后再次 SHA-256。
- target hash：`0db47b7b5eff9687a72e75fd896373ef49aa0c6d9fd528cd17a24ba367f632dd`。
- 兼容安全 Agent：`PASS`，未发现可操作问题；确认 Round 1～4 的 fail-closed、artifact health、public validator、诊断、前端授权与 whole-closure rollback findings 全部闭合。
- 精简效率 Agent：`PASS`，未发现可操作问题；确认私有 helper、可证明的 semantic checks、family/path/reason guidance 与单个负向测试没有形成公共 bypass、第二映射或治理膨胀，55/160 LOC 预算合理。
- 两个 Agent 独立复算 hash 与目标一致；T13 设计 admission gate 关闭，允许创建 runtime branch 并进入 T21 RED。
- 后续不修改 `spec.md + plan.md + tasks.md`；如三件套变化，本轮双 PASS 自动失效并重新评审。

## 8. Batch 2026-07-13-008：提交前 whitespace 修订与 Round 6 双 PASS

- staged `git diff --check` 发现 `spec.md` 顶部 3 处模板 Markdown 行尾双空格；为满足零 whitespace error，移除这些空格。
- 该字节变化使 Round 5 hash 失效；新 target hash 为 `2fe77e6464824383ecff9c91d1cf98ad3b23be5a461187dcd2363b4910e37067`。
- 兼容安全 Agent 与精简效率 Agent 均独立复算新 hash 并给出 `PASS`、未发现可操作问题；确认仅 whitespace 变化，全部设计合同、预算和回退语义不变。
- Round 6 为当前有效 admission 记录；后续三件套不得变化。

## 9. Batch 2026-07-13-009：T21 RED characterization

- docs baseline commit：`b9543cc4`；runtime branch：`codex/199-frontend-inheritance-truth`。
- 仅修改两个获准测试文件，无产品代码；相对 baseline 为 `+160/-42`，新增 160 LOC，等于冻结上限。
- RED 命令：`uv run pytest tests/unit/test_program_service.py tests/unit/test_frontend_quality_platform.py -q`。
- RED 结果：`16 failed, 382 passed in 31.73s`。
- 十六个失败精确覆盖：1 个 framework healthy waiver、3 个 generation/quality semantic artifact blocker/path/reason、6 个 canonical/mirror/ref/mixed 分类边界、6 个 consumer `generation/quality × unknown/not_inherited/blocked` release 映射。
- public quality validator 的 `None` 负向禁止用例在旧实现即通过，作为未来私有 helper 重构的非回归保护，不伪造 RED。
- fixture 隔离修订：semantic artifact 用例 mock 现有 truth/close/verify refs，防止无关 closure/truth debt 混入目标失败；复跑后失败集合与数量稳定。
- 独立兼容安全 RED reviewer 复核当前补丁并给出 `PASS`、未发现可操作问题；确认上轮提出的 consumer quality 维度、mirror/ref/mixed 边界、path+reason 与空 delivery entry 覆盖全部关闭，且 16 个失败均非 fixture/test API 错误。
- `uv run ruff check tests/unit/test_program_service.py tests/unit/test_frontend_quality_platform.py`：PASS；`git diff --check`：PASS。
- 下一步：提交已通过独立复审的 RED 测试基线，再实现 ≤55 net LOC 的最小 GREEN。
