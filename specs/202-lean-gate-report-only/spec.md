---
related_plan: "specs/196-ai-sdlc-lean-code-self-reduction-governance/plan.md"
related_doc:
  - "specs/196-ai-sdlc-lean-code-self-reduction-governance/spec.md"
lean_contract:
  schema_version: "lean-contract/v1"
  package_id: "WP-02"
  task_id: "T62A"
  risk_level: "L1"
  base_revision: "d19c8b7df66ca43e4fa55a99a6d05fa2d1219586"
  contract_source: "specs/196-ai-sdlc-lean-code-self-reduction-governance/spec.md#6.3"
  target_slice: "changed Python code metrics plus Lean Contract admission evidence"
  applicable_nc: []
  applicable_cc: ["CC-01", "CC-02", "CC-03", "CC-05", "CC-06", "CC-07"]
  applicable_rc: ["RC-01", "RC-02", "RC-03", "RC-06", "RC-07", "RC-09", "RC-10"]
  expected_delta_path: "specs/202-lean-gate-report-only/expected-delta.json"
  predicted_deletion_loc: 1400
  max_protection_loc: 350
  max_product_loc: 210
  max_test_harness_normalizer_loc: 140
  entry_conditions:
    - "T61A baseline captured at the exact base revision"
    - "same-hash compatibility and lean reviewers both pass"
  stop_conditions:
    - "protection cost exceeds 350 added physical lines"
    - "existing gate telemetry state config or reviewer behavior must change"
  rollback_owner: "framework-maintainers"
  rollback_command: "git revert <WI-202 merge commit>"
  evidence_uris:
    - "specs/202-lean-gate-report-only/task-execution-log.md"
    - "specs/202-lean-gate-report-only/expected-delta.json"
  waivers: []
---
# 功能规格：Lean Gate Report-Only 基线

**功能编号**：`202-lean-gate-report-only`
**创建日期**：2026-07-14
**状态**：formal admission review
**父项**：WI-196 / GAP-01 / GAP-02 / WP-01A / WP-02 / T61A / T62A
**风险等级**：L1；一旦触碰现有 gate、telemetry、状态机、配置或执行授权，立即升级为 L2 并停止本方案。

## 1. 目标与范围

在不改变任何现有验证、执行或 reviewer 决策的前提下，完成两件事：

1. 捕获 `verify constraints` 的目标切片旧行为和副作用基线（WP-01A / T61A）。
2. 新增显式调用的 `verify lean-report`，对两个精确 Git revision 之间的 Python 变更和指定 work item 的 Lean Contract 产生中性、确定、只读报告（WP-02 / T62A）。

首期只覆盖：

- `src/ai_sdlc/**/*.py` 的手写产品代码；
- `tests/**/*.py` 的 test / harness / normalizer；
- 指定 work item 的 `spec.md` frontmatter、`plan.md`、`tasks.md` 和 versioned expected delta；
- vendored、generated、fixture/snapshot、governance/docs、other 的独立分类和 unavailable 证据。

## 2. 明确非目标

- 不实现 T62B warning、T62C blocking、waiver schema、waiver suppression、配置开关或 admission `active + verified`。
- 不接入 `verify constraints`、`run`、`close-check`、reviewer gate、state machine、checkpoint、telemetry、数据库或默认 CI。
- 不扫描或追补全仓历史债务，不读取 dirty/untracked 内容，不访问网络，不自动猜 base、candidate 或 active work item。
- 不修改 `ConstraintReport`、其 digest/locator、现有 stdout/JSON/exit code 或 telemetry 写集。
- 不新建通用 Policy/Rule/Engine/Registry/DTO/schema/DSL/executor，不为不足三个当前调用者创建公共抽象。
- 不实施预算赞助候选本身；该候选必须在后续独立 WP-07 work item 中重新通过完整 RC、T61A/T61B 和 PR 门禁。

## 3. T61A 旧行为基线

基线 revision 为 `d19c8b7df66ca43e4fa55a99a6d05fa2d1219586`，在独立 shared clone 中以该精确 commit 捕获：

| 表面 | 冻结事实 |
|---|---|
| `verify --help` | exit `0`；唯一子命令为 `constraints` |
| `verify constraints` | exit `0`；stdout 精确为 `verify constraints: no BLOCKERs.`；stderr 为空 |
| `verify constraints --json` | exit `0`；顶层 key 为 `advisories, blockers, frontend_contract_runtime_attachment, frontend_contract_verification, frontend_gate_verification, governance, ok, root, telemetry, verification_gate`；`ok=true`、`blockers=[]`、`advisories=[]` |
| JSON 子结构 | `verification_gate` key 为 `check_objects, coverage_gaps, name, release_gate, source_name, sources`；`governance` key 为 `advisories, audit_summary, gate_decision_payload`；`telemetry` key 为 `evaluation_id, event_id, evidence_id, goal_session_id, report_digest, report_locator, violation_id` |
| 写集 | 每次约束验证写一个 session 的 `events.ndjson`、`evidence.ndjson`、一个 evaluation JSON，并创建或更新 telemetry manifest 与三个 indexes；当前无 violation 文件 |
| tracked tree | 命令执行后 `git status --short` 为空 |

绝对 root、时间、随机 telemetry ID 以及由 root 派生的 digest/locator 是 normalizer allowlist；除这些字段外不允许差异。T62A 只允许 `expected-delta.json` 明列的新增命令表面，不能借“确定性”解释其他变化。

## 4. RC-06 预算准入

### 4.1 具体赞助候选

候选 `WP07-FINALIZATION-COMMAND-FAMILY-01` 在同一基线包含以下 10 个精确符号：

`program_cross_spec_writeback`、`program_guarded_registry`、`program_broader_governance`、`program_final_governance`、`program_writeback_persistence`、`program_persisted_write_proof`、`program_final_proof_publication`、`program_final_proof_closure`、`program_final_proof_archive`、`program_final_proof_archive_thread_archive`。

AST 物理跨度合计为 2,254 行，其中公共 Typer 签名为 220 行、函数体为 2,034 行。预算模型保留全部 220 行签名，给一个私有共用实现最多 400 行，并给 10 个命令各保留最多 20 行适配体：

`2254 - 220 - 400 - (10 × 20) = 1434`。

为抵消估算误差，只将 1,400 行记为经评审的预计净删除量。双 Agent 对本 formal 同哈希 PASS 后，该候选才成为 RC-06 分母；PASS 前允许保护 LOC 为 0。

### 4.2 WI-202 成本上限

`floor(1400 × 25%) = 350`。路线图此前 WP-01/WP-02 已使用成本为 0，因此本项冻结：

| 成本项 | 上限 |
|---|---:|
| 手写产品代码（core + CLI） | 210 LOC |
| test / harness / normalizer | 140 LOC |
| 合计 | 350 LOC |
| 新产品文件 / 新测试文件 | 1 / 1 |
| 新公共抽象 / 新依赖 / schema / fixture / snapshot | 0 |

计费采用 `git diff --numstat <base>..<candidate>` 的新增物理行；修改既有文件的新增行同样计费，删除行不得抵扣保护成本。任一分项或合计超限、任一新函数超过 50 行、任一新文件超过 400 行，立即 No-Go，不得扩大分母。

如果后续赞助候选被取消或预计净删除量降到实际保护成本四倍以下，owner 必须在路线图关闭前以新的已评审具体候选替换分母，或 revert WI-202；不得把保护代码留作无收益的永久膨胀。

## 5. 度量与分类口径

- revision 必须由调用者显式提供完整或可解析 ref；报告记录解析后的 40 位 commit SHA。比较只读取 commit blob。
- 路径由 `git diff --name-status -z --find-renames` 获取，统一为 repo-relative POSIX；输入的 Windows `\\` 只在 `--wi` 参数边界归一化。
- 分类优先级固定为 `vendored → generated → fixture_snapshot → test_harness_normalizer → handwritten_product → governance_docs → other`。
- `src/ai_sdlc/generators/` 是手写生成器源码，不因目录名被误分为 generated；generated 仅识别明确生成目录、`.generated.py` 或生成标记。
- 文件物理行使用 UTF-8 文本的 `splitlines()`；空行、注释和 docstring 均计入。
- 函数跨度从最早 decorator（如有）到 `end_lineno`，同步覆盖 function、async function、method 和嵌套函数。
- `new` 为 candidate 存在而 base 不存在；`modified` 为同路径/rename 对应 blob 不同；`changed_function` 为同 qualified name 的源码 hash 不同或 base 不存在。
- `significantly_modified` 为 new function，或规范化非空源码行的增删总量至少 10 行，或候选跨度相对基线变化至少 20%。
- 新文件从 `≤400` 跨到 `>400` 产生 file finding；历史 `>400` 文件未跨阈值只列 historical debt。候选中 `>50` 的 changed function 产生中性 finding；未改历史超长函数只列 historical debt。
- rename 保留 old/new path 关系；delete 只计分类，不追债。binary、非 UTF-8、symlink、submodule、缺 blob、缺 revision 和 shallow-history 不回退全仓扫描，只报告 `unavailable/unknown`。
- dirty/untracked 工作树不参与计算；报告显式给出 `working_tree_in_scope=false` 和是否检测到未提交内容，不因此改变精确 commit comparison 的结果。

## 6. Lean Contract 报告口径

`verify lean-report` 读取 candidate revision 中指定 WI 的 `spec.md` frontmatter：

1. `lean_contract.schema_version` 必须为 `lean-contract/v1`。
2. `package_id` 从 `contract_source` 指向的父规格 §6.3 取得适用矩阵；不得在产品代码复制另一份矩阵。
3. declared NC/CC/RC 与父表解析出的 expected 集合逐项比较，缺失、额外、重复或非法 token 均只形成 neutral finding。
4. `base_revision`、expected-delta 路径、风险等级、预算、回退 owner/命令和 evidence URI 必须可见；source unavailable 独立报告。
5. 任意 `waivers` 文本均输出 `waiver_effect=none`，不能消除 finding、改变 exit 或替代 CC-05/CC-06、安全、兼容与 reviewer 边界。
6. code-metric 与 contract-admission 两个规则族分别记录 `complete/unavailable`，任一族失败不吞掉另一族证据。

## 7. 功能需求

- **FR-202-01**：新增 `uv run ai-sdlc verify lean-report --base-ref <ref> --candidate-ref <ref> --wi <repo-relative-dir> [--json]`；三个定位参数均显式必填。
- **FR-202-02**：命令必须解析精确 commits、NUL 分隔 diff、rename 和分类，并按 §5 生成确定排序的代码度量证据。
- **FR-202-03**：命令必须按 §6 报告 Lean Contract declared/expected/gaps、budget evidence 和 `waiver_effect=none`。
- **FR-202-04**：JSON 固定包含 `schema_version=lean-gate-report/v1`、`enforcement=report_only`、`decision=not_enforced`、`scope`、`classification`、`code_metrics`、`contract_evidence`、`budget_evidence`、`findings`；禁止出现 `blockers`、`warnings`、`advisories`。
- **FR-202-05**：plain 输出必须 findings-first、无黄色/红色 gate 语义，并明确 `not enforced`；JSON 与 plain 对同一报告一致。
- **FR-202-06**：合法调用无论发现超限、合同缺口或 source unavailable 均 exit `0`；仅 Typer 缺参数或非法 repo-relative WI path 使用标准 usage error。
- **FR-202-07**：命令不得写 telemetry、checkpoint、config、manifest、artifact、Git、网络或工作树；运行前后除解释器缓存外文件集合与内容 hash 不变。
- **FR-202-08**：现有 `verify constraints` 的 plain/JSON/exit、ConstraintReport digest 语义、telemetry 写集、Program Truth 和 adapter/config 行为必须保持零未批准差异。
- **FR-202-09**：同一 base/candidate/WI 重复执行的规范化 JSON 必须字节一致，路径在 Windows/macOS/Linux 统一为 POSIX。
- **FR-202-10**：实现成本必须满足 §4.2；超限自动停止，不得以 helper、fixture 或未来扩展点豁免。

## 8. 验收场景

1. 新增 401 行产品文件或 51 行函数时，报告 neutral finding 且 exit `0`。
2. 历史 401 行文件/51 行函数未改时，只列 historical debt；修改历史超长函数时，只报告 changed span，不把整文件变成追债范围。
3. vendored/generated/fixture/test/handwritten/docs 分类样本得到固定分类；空格、Unicode、CRLF、Windows WI path 与 rename 均稳定。
4. binary、symlink、submodule、非 UTF-8、缺 base 或 shallow-history 只产生 unavailable evidence，不触发全仓 fallback。
5. Lean Contract 缺字段、重复/非法 token 或包含 waiver 时仍 exit `0`，且 waiver 不抑制 finding。
6. code rule unavailable 时 contract rule 仍产出，反之亦然。
7. 原 `verify constraints` characterization 全部通过，新增命令前后零新增写集。
8. exact base/candidate 报告满足 350 LOC 预算并可由后续 commit 重放。

## 9. 成功、停止与回退

### 成功标准

- **SC-202-01**：formal 四件套和 expected delta 无占位或矛盾，并由兼容安全、精简效率两个 agent 对同一 hash 明确 PASS。
- **SC-202-02**：FR-202-01～FR-202-10 和八个验收场景均有自动化测试或精确命令证据。
- **SC-202-03**：新增命令 findings 存在仍 exit `0`，且不存在 warning/blocker/advisory/execute/reviewer 状态变化。
- **SC-202-04**：现有 verify surface、telemetry、Program Truth、全量测试和跨平台 CI 无未批准差异。
- **SC-202-05**：保护成本不超过 350 LOC，新文件/函数满足 400/50，公共抽象和依赖增量为 0。
- **SC-202-06**：PR 经 Codex review、所有 required checks 全绿并合并，mainline exact-tree targeted smoke 重放成功。

### 停止条件

满足任一项即停止或回退当前设计：需要修改现有 gate/telemetry/state/config；需要猜 ref/WI 或扫描 dirty tree；合法 findings 导致非零 exit；分类样本存在不可解释误判；保护成本超过 350 LOC；现有兼容表面出现未批准差异；waiver 获得 suppression；预算赞助候选不再足额。

### 回退

owner 为 `framework-maintainers`。合并前删除独立模块、CLI 注册和对应测试即可；合并后使用 `git revert <WI-202 merge commit>`。本项无数据库、artifact migration、配置或状态恢复步骤。回退后重跑原 `verify constraints` characterization、全量测试、constraints 和 Program Truth audit。
