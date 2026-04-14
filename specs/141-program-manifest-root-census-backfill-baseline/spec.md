# 功能规格：Program Manifest Root Census Backfill Baseline

**功能编号**：`141-program-manifest-root-census-backfill-baseline`
**创建日期**：2026-04-14
**状态**：formal baseline 起草中（待两轮对抗评审）
**输入**：[`../119-capability-closure-truth-baseline/spec.md`](../119-capability-closure-truth-baseline/spec.md)、[`../140-program-truth-ledger-release-audit-baseline/spec.md`](../140-program-truth-ledger-release-audit-baseline/spec.md)、[`../../program-manifest.yaml`](../../program-manifest.yaml)、[`../../src/ai_sdlc/models/program.py`](../../src/ai_sdlc/models/program.py)、[`../../src/ai_sdlc/core/program_service.py`](../../src/ai_sdlc/core/program_service.py)、[`../../src/ai_sdlc/cli/program_cmd.py`](../../src/ai_sdlc/cli/program_cmd.py)

> 口径：`141` 先解决根级 `program-manifest.yaml` 中既存的 37 个历史缺失 `specs/*/spec.md` entries；在本 tranche formal docs 创建后，`141` 自身也必须被根 manifest 纳管，因此最终实际回填写集会变成 38 个 entries。它不修复 `frontend-mainline-delivery` 的 runtime/close-check blocker；它的职责是先把根索引补齐，让 `program truth audit` 只剩真实 blocker，而不再夹带 `migration_pending`。

## 问题定义

`140` 已经把 program-level truth ledger、release audit 与 migration contract 冻结下来，但当前根 manifest 仍未覆盖所有带 `spec.md` 的 `specs/*` 目录。

当前已确认的缺口包括：

- 根级 manifest 在本 tranche 启动时仍缺少 37 个历史目录 entry，主要落在 `001-008`、`010`、`072/074/075/076`、`079-081`、`116-122`、`128-140` 等 tranche；当 `141` formal docs 创建后，当前工作树中的实际缺口增至 38 个
- `066` 还存在历史漂移：仓库里同时存在 `066-frontend-p1-experience-stability-planning-baseline` 与 `066-frontend-verification-diagnostics-contract-baseline` 两个目录，而 manifest 目前只纳管了前者
- `program truth audit` 因而继续把全仓状态判成 `migration_pending`，使 operator 无法区分“还没纳管的历史 spec”与“已经纳管但真实未闭环的 release blocker”
- 在这种状态下，即使 release blocker 没有变化，truth ledger 仍会持续提示全仓 migration pending，导致 close/release 口径不够干净，也会让后续 tranche 难以聚焦真正的能力缺口

因此必须先做一次 root census backfill，把根 manifest 与目录真值对齐，再进入第二个 tranche 专门处理 `095/096/098/099/100/101/102/103/104/105/123/124/125/126` 的真实 blocker。

## 范围

- **覆盖**：
  - 对根级 `program-manifest.yaml` 做一次完整 census，确保每个 `specs/*/spec.md` 目录都有且只有一个精确 entry
  - 回填启动时缺失的 37 个历史 spec entries，并把当前 tranche `141` 自身 entry 一并纳入根 manifest
  - 对 `066` 这类“同编号但不同目录”的历史情况，以目录全名为精确 spec id 回填，不再因为数字前缀相同而漏纳管
  - 为新回填 entries 补齐最小 authoring intent：`id`、`path`、`depends_on`、`branch_slug`、`owner`、`frontend_evidence_class`
  - 对存在 canonical footer 的 spec，按 canonical source 回填 `frontend_evidence_class`；无 canonical footer 的保持空值，不伪造 mirror
  - 回填完成后重跑 `program truth sync --execute --yes` 与 `program truth audit`
  - 让 truth ledger 去掉 `migration_pending`，只保留真实 release blocker / closure blocker
- **不覆盖**：
  - 不在本 tranche 内修复 `frontend-mainline-delivery` 的 close-check/runtime blocker
  - 不新增第二份 manifest、registry 或外部盘点文档
  - 不在没有 machine-verifiable 依据时，为历史 spec 臆造 capability membership、release role 或依赖链
  - 不改写 `140` 已冻结的 release audit 判定逻辑
  - 不把 `migration_pending` 消失错误解释为“全仓已 release-ready”

## 已锁定决策

- 根 census 以 **目录真值** 为准：凡是 `specs/*` 下存在 `spec.md` 的目录，都必须在根 manifest 里拥有一个精确匹配的 `specs[]` entry
- `spec.id` 以目录全名为准，而不是仅取数字前缀；因此 `066-frontend-p1-experience-stability-planning-baseline` 与 `066-frontend-verification-diagnostics-contract-baseline` 必须作为两个独立 spec entries 共存
- `branch_slug` 默认由 `spec.id` 去掉数字前缀后得到，保持与目录名一致；若 `spec.id` 不符合 `<数字>-<slug>` 模式，则必须保持空值，不得伪造 slug
- `owner` 在本 tranche 内继续沿用当前根 manifest 的单一 owner 口径 `team-frontend-governance`，不在这一步引入新的 owner taxonomy
- `depends_on` 只在已有根 manifest 或明确 machine-readable source 可支撑时填写；缺少可靠来源的历史 spec 必须显式写成空列表 `[]`，表示“根 manifest 尚未编制依赖真值”，而不是伪造独立性证明
- `frontend_evidence_class` 只能镜像 canonical footer：有 canonical 值则回填，无 canonical 值则保持空值；不得为了“看起来齐全”而统一填 `framework_capability`
- 根 census backfill 不得新增非 release-scope 的 `roles` / `capability_refs` 要求；对本 tranche 新回填的非 release-scope 历史 spec，`roles` 与 `capability_refs` 必须保持空列表，直到后续 capability tranche 明确编制
- 根 census backfill 不得让非 release-scope 历史 spec 因回填动作本身被误纳入 release audit gating
- 本 tranche 完成后的目标是先清掉“缺 manifest entry”这一类 migration cause：
  - `program validate` 对根 census 不再产生 `migration_pending: manifest entry missing for specs/...`
  - 若仓库不存在其他 migration cause，则 `program truth audit`/`truth_snapshot` 应从 `migration_pending` 收敛为只反映真实 blocker 的状态（按当前仓库基线，预期为 `blocked`）
  - 若仍存在其他 migration cause，则必须只保留剩余真实 migration cause，不得再混入 root census 漏项
  - `frontend-mainline-delivery` 的 blocker 明确保留，留待下一 tranche 处理

## 功能需求

| ID | 需求 |
|----|------|
| FR-141-001 | 系统必须确保所有带 `spec.md` 的 `specs/*` 目录都在根 `program-manifest.yaml` 中拥有精确 entry |
| FR-141-002 | 对启动时缺失的 37 个历史目录以及当前 tranche `141` 自身目录，根 manifest 必须逐一回填，不得再以 `migration_pending` 暂存 |
| FR-141-003 | 当多个目录共享同一数字前缀但目录全名不同（如 `066`）时，manifest 必须以完整目录名作为唯一 spec id 共存纳管 |
| FR-141-004 | 新回填 entry 至少必须包含 `id`、`path`、`depends_on`、`branch_slug`、`owner`、`frontend_evidence_class` 六类字段；其中未编制依赖真值的历史 spec 必须显式写 `depends_on: []` |
| FR-141-005 | `frontend_evidence_class` 仅允许按 canonical footer 回填；canonical 缺失时必须保持空值而不是伪造 mirror |
| FR-141-006 | 回填不得把非 release-scope spec 擅自纳入 `frontend-mainline-delivery` 或其他 capability；本 tranche 新回填的非 release-scope entries 必须保持 `roles: []` 与 `capability_refs: []` |
| FR-141-007 | 回填完成后，`program truth sync --execute --yes` 必须刷新根 `truth_snapshot`；缺失 manifest entry 这一类 migration cause 必须消失，剩余状态只允许来自其他真实 migration cause 或真实 blocker |
| FR-141-008 | 回填完成后，`program truth audit` 必须只暴露真实 blocker 与剩余真实 migration cause；若 release blocker 仍存在，必须继续 fail-closed |
| FR-141-009 | 仓库必须补一条 repo-level 自动化回归校验，直接以当前仓库根目录运行，验证所有 `specs/*/spec.md` 目录都已纳入根 manifest；该校验必须作为 pytest 测试纳入现有测试套件，而不是孤立脚本 |

## Exit Criteria

- **SC-141-001**：根 manifest 覆盖所有当前带 `spec.md` 的 `specs/*` 目录；历史缺失 entry 从 `37` 降为 `0`，当前工作树总缺失 entry 也降为 `0`
- **SC-141-002**：`program validate`/`program truth audit` 不再报告 `migration_pending: manifest entry missing for specs/...`
- **SC-141-003**：若根 census 漏项是当前唯一 migration cause，则 `truth_snapshot.state` 不再是 `migration_pending`；按当前仓库基线，预期收敛为 `blocked`，且 release blocker 仍按真实状态保留
- **SC-141-004**：`066` 的双目录历史漂移被明确纳管，不再因前缀冲突造成根索引漏项
- **SC-141-005**：新增回归测试能够在未来根 manifest 再次遗漏 spec 目录时直接失败

---
related_doc:
  - "specs/119-capability-closure-truth-baseline/spec.md"
  - "specs/140-program-truth-ledger-release-audit-baseline/spec.md"
  - "program-manifest.yaml"
  - "src/ai_sdlc/models/program.py"
  - "src/ai_sdlc/core/program_service.py"
  - "src/ai_sdlc/cli/program_cmd.py"
frontend_evidence_class: "framework_capability"
---
