# 功能规格：Linked Work Item Resume Working Set

**功能编号**：`198-linked-wi-resume`
**创建日期**：2026-07-13
**状态**：设计候选，待同哈希双 Agent 门禁
**父项**：WI-196 `GAP-08 / T52`
**基线**：`origin/main@4802596f9ef2fda8c27717c25d6760ed09136811`

## 1. 问题与范围

`active_work_item_id(checkpoint)` 已明确让非空 `checkpoint.linked_wi_id` 优先于历史 `checkpoint.feature.id`。`build_resume_pack()` 因而会按 linked WI 读取 scoped runtime、latest summary 与可选 `working-set.yaml`，但私有 filesystem fallback `_build_resume_working_set_from_filesystem()` 仍只从 `checkpoint.feature.spec_dir` 派生 `spec.md / plan.md / tasks.md`。

当 checkpoint 保留历史 feature、再通过 `workitem link` 关联新 WI，且新 WI 尚无 `working-set.yaml` 时，root/scoped resume-pack 与 handoff 会标记新的 active WI，却继续携带历史 WI 的三件套路径。`recover` 在 pack 缺失、损坏或 stale 时也会从 checkpoint 重建出同一错误工作集。

本项统一 active WI 的 filesystem working-set 与 branch fail-closed 派生，并让升级前已生成但 fingerprint 仍 fresh 的历史错误 pack 自动重建；不修改 checkpoint schema、历史 feature/stage、workitem link 写入合同或 resume-pack schema。

## 2. 冻结现状与期望

### 2.1 Observed

给定：

- `checkpoint.feature.id/spec_dir = 197 / specs/197-adapter-preflight-order`；
- `checkpoint.linked_wi_id = 198-linked-wi-resume`；
- 两个 spec 目录均有 canonical `spec.md / plan.md / tasks.md`；
- `.ai-sdlc/work-items/198-linked-wi-resume/working-set.yaml` 不存在。

当前 `build_resume_pack()` 的 active work item 是 `198-linked-wi-resume`，但 `working_set_snapshot.spec_path / plan_path / tasks_path` 仍指向 `specs/197-adapter-preflight-order/`。

若该错误 pack 由旧版本生成且 checkpoint fingerprint、更新时间以及 root/scoped 内容均一致，当前 `load_resume_pack()` 会继续把它当作 fresh；`handoff update` 只更新 summary 后原样保存。linked runtime 不存在时，`current_branch` 也继续回退到历史 feature branch。

### 2.2 Expected

- 非空 linked WI 存在时，filesystem fallback 必须从 `specs/<linked_wi_id>/` 派生三件套。
- linked 目录或单个 canonical 文件缺失时，对应字段保持空；不得静默回退到历史 `feature.spec_dir`。
- linked WI 的 persisted `working-set.yaml` 若存在，仍按现有语义用其非空字段覆盖 filesystem fallback。
- `linked_wi_id` 为空白/缺失时，继续使用 `checkpoint.feature.spec_dir`，包括历史非标准 spec 路径。
- linked runtime 有非空 branch 时继续优先使用该值；linked runtime 缺失/branch 为空时 `current_branch` 必须为空，不得泄漏历史 feature branch。无 linked WI 时仍沿用历史 feature branch。
- 升级前已生成、fingerprint 仍 fresh 但 working-set 路径或 branch 不符合上述 active linked WI + persisted artifact 语义的 root/scoped pack，首次 load/handoff/recover 必须判定 stale 并原子重建。
- root resume-pack、linked scoped resume-pack、canonical/scoped handoff 与 recover rebuild 必须对同一 active WI 工作集达成一致。

## 3. 用户场景与独立验收

### US-01：linked WI 工作集优先（P0）

作为恢复流程使用者，我希望 active linked WI 的 resume-pack 指向其 canonical docs，以便中断后不会回到历史工作项。

**独立验收**：构造历史 feature + 新 linked WI，调用 `build_resume_pack()`，断言 active WI 的 spec/plan/tasks 全部来自 `specs/<linked>/`，且测试在修复前稳定 RED。

### US-02：handoff 与 recover 一致（P0）

作为长任务维护者，我希望 handoff 更新与 recover 重建共享同一 active working set，以便 canonical/scoped 状态不会各指向不同工作项。

**独立验收**：在 resume-pack 缺失、常规 stale，以及旧版本生成但结构上仍 fresh 的 linked fixture 中分别执行 handoff update 与 recover；root pack、linked scoped pack 和 handoff 的 work item/path 全部指向 linked WI；无 linked runtime 时 branch 不回退历史 feature。

### US-03：历史 checkpoint 兼容（P0）

作为既有项目用户，我希望没有 linked WI 时的 checkpoint.feature 行为完全不变，以便旧项目、非标准 spec_dir 与恢复错误合同不受影响。

**独立验收**：既有无 linked checkpoint 的 build/load/recover/handoff 回归全绿；stage、batch、branch、docs baseline、fingerprint、错误文本和写入边界没有 diff。

## 4. 边界情况

- `linked_wi_id` 为 `None`、空串或仅空白：视为未关联，使用 `feature.spec_dir`。
- linked spec 目录不存在：spec/plan/tasks 字段均为空，不读取历史 feature docs。
- linked 目录只存在部分 canonical 文件：只填充真实存在的字段。
- linked WI 已有部分或完整 `working-set.yaml`：仅其非空字段按既有 overlay 语义覆盖 fallback；`active_files`、`context_summary` 规则不变。
- linked runtime 存在且 branch 非空：沿用 runtime branch；linked runtime 缺失/branch 为空：branch fail-closed 为空。
- legacy fresh pack 与按当前 linked filesystem + persisted working-set/runtime 重算结果一致时不得误判 stale；只有 spec/plan/tasks/current_branch 语义不一致才重建。
- 仅为 semantic 校验而读取的 optional working-set/runtime/latest-summary 若损坏、编码无效或不可读，必须保留旧版“fresh pack 直接返回”的成功合同，不新增异常；待 optional artifact 可读或 checkpoint/root-scoped 本身 stale 后再按既有路径处理。
- checkpoint.feature 为空或无 spec_dir 的 strict 校验合同不在本项改变；本项不放宽 `load_resume_pack(strict=True)`。
- Windows/macOS/Linux 路径均使用 `pathlib.Path`，不拼接平台分隔符字符串。

## 5. 非减重变更合同

| 合同 | 冻结内容 |
|---|---|
| NC-01 | observed/expected 与基线 revision 按 §2 冻结 |
| NC-02 | 受影响 CC 为 CC-03、CC-04、CC-06、CC-07；只触及 `state.py` 的 resume build/load、working-set 私有派生与对应 tests |
| NC-03 | 产品净新增 ≤20 LOC，测试新增 ≤140 LOC；0 个新产品/测试文件、0 个公共抽象、0 个依赖/配置/schema |
| NC-04 | 严格 RED→GREEN；unit、handoff、recover、全量、ruff、constraints、diff check 全绿 |
| NC-05 | mainline/发布回退整个 PR/版本；未合并分支按 GREEN 与对应 RED test 成对撤销，owner 为 framework maintainer |
| NC-06 | 不混入结构减重、checkpoint 迁移、历史 stage 修复、GAP-09～GAP-11 或无关 truth 清仓 |

### 5.1 兼容契约

- **CC-03**：resume-pack/working-set schema、字段类型、序列化顺序与既有错误文本不变；approved delta 仅为 linked WI 三件套路径由历史 feature 改为 linked target，以及 linked 无 runtime branch 时由历史 branch 改为空。
- **CC-04**：active work item 仍由 `active_work_item_id()` 决定；不改 checkpoint、feature、linked_wi_id 或 stage 状态迁移。
- **CC-06**：pack missing/corrupted/checkpoint-stale/legacy-semantic-stale rebuild、handoff refresh、recover/status load path 和 persisted overlay 仍幂等；四条入口对 linked working set 一致，升级前错误 fresh pack 可自愈。
- **CC-07**：实现只使用既有 `Path` 语义，并由现有跨平台 CI 覆盖。

## 6. 方案裁决

### 方案 A：把已解析 active WI 传入现有私有 fallback（采用）

`_build_resume_working_set()` 已拥有 `work_item_id`。将该值传给 `_build_resume_working_set_from_filesystem()`；仅当 checkpoint 存在非空 linked id 时使用 `root / "specs" / work_item_id`，否则沿用 `root / checkpoint.feature.spec_dir`。load 时至多构建一次同源 expected pack，窄比较 spec/plan/tasks/current_branch，使旧版本错误 fresh pack 进入既有 stale rebuild并复用该 expected pack；仅 semantic 校验读取 optional artifact 出现 `YamlStoreError`、`UnicodeError` 或 `OSError` 时跳过迁移，保留旧错误合同。branch 继续优先 active runtime，linked 无 runtime branch 时为空。不得新增公共 helper，保留 persisted working-set overlay。

### 方案 B：`workitem link` 时同步改写 checkpoint.feature（拒绝）

会改变历史 checkpoint 身份、branch/docs baseline 与状态迁移语义，扩大到 CC-04/schema migration 风险，违反 T52 非目标。

### 方案 C：从 program-manifest 或目录 glob 解析 linked spec（拒绝）

引入第二个 active-WI 真值源和额外 I/O；manifest 缺失/漂移时行为不确定，复杂度高于 canonical `specs/<WI>` 合同。

## 7. 功能需求

- **FR-198-01**：非空 `linked_wi_id` 必须优先决定 filesystem fallback 的 canonical spec 目录。
- **FR-198-02**：无 linked WI 时必须继续使用 `checkpoint.feature.spec_dir`，不得假设 `specs/<feature.id>`。
- **FR-198-03**：linked target 缺失或不完整时不得回退历史 feature docs。
- **FR-198-04**：active WI persisted `working-set.yaml` 的既有非空字段 overlay、active_files 与 context_summary 语义保持。
- **FR-198-05**：build/save/load、handoff update 与 recover rebuild 必须对 linked spec/plan/tasks 达成一致，scoped artifacts 必须位于 linked work-item 目录。
- **FR-198-06**：linked runtime branch 非空时优先；linked 无 runtime branch 时 fail-closed 为空；无 linked WI 时保留 feature branch。不得改变 checkpoint/resume/working-set 模型、fingerprint、stage/batch/docs baseline、异常或 CLI surface。
- **FR-198-07**：升级前生成且 fingerprint 仍 fresh 的错误 linked pack必须按 spec/plan/tasks/current_branch 语义判 stale 并重建；正确 pack 与 persisted artifact 不得误判。仅 semantic 校验遇到损坏、无效编码或不可读 optional artifact 时不得新增异常。
- **FR-198-08**：新增 unit + handoff + recover characterization；至少一项在生产修复前因历史路径或 branch 泄漏稳定 RED。
- **FR-198-09**：交付必须包含 fresh full suite、跨平台 CI、规范化 artifact before/after、回退与父项 GAP Evidence Index 证据。

## 8. 成功标准

- **SC-198-01**：历史 feature + linked WI fixture 的 RED 明确显示三件套仍指向历史 feature。
- **SC-198-02**：GREEN 后 build/handoff/recover 的 root/scoped 工作集全部只指向 linked WI。
- **SC-198-03**：旧版本错误 fresh pack 自动重建；linked 无 runtime branch 为空；无 linked、linked 缺目录、partial docs 与 persisted overlay 回归均通过。
- **SC-198-04**：产品净新增 ≤20 LOC，测试新增 ≤140 LOC；无新文件、公共抽象、依赖、配置或 schema。
- **SC-198-05**：focused、full pytest、ruff、constraints、diff check 与新 HEAD CI 全绿。
- **SC-198-06**：兼容安全与精简效率 Agent 对同一 `spec.md + plan.md + tasks.md` 哈希均 PASS，最终 branch review 无可操作 finding。
- **SC-198-07**：PR 合并后 mainline targeted/truth 复核通过，WI-196 GAP-08/T52 关闭。

## 9. 停止与回退

出现以下任一情况立即停止并重新做影响分析：需要改 checkpoint/resume schema、改写历史 feature/stage、引入 manifest/glob fallback、新公共抽象、超出 NC-03 或出现未批准 CLI/error delta。

mainline/发布回退整个 PR/版本；未合并源码分支必须将 GREEN 与对应 RED test 成对撤销，不得留下必失败测试。
