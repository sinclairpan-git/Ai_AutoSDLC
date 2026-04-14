# 实施计划：Program Manifest Root Census Backfill Baseline

**功能编号**：`141-program-manifest-root-census-backfill-baseline`
**日期**：2026-04-14
**规格**：`specs/141-program-manifest-root-census-backfill-baseline/spec.md`

## 概述

`141` 是一个窄范围的根索引修复 tranche。目标不是处理 `frontend-mainline-delivery` 的 runtime blocker，而是先把根级 `program-manifest.yaml` 中启动时缺失的 37 个历史 spec entries 补齐；由于本 tranche 在执行中新增了 `141` 自身 formal docs，实际回填写集会扩成 38 个 entries。完成后，truth ledger 不再把“历史未纳管目录”与“真实 release blocker”混在一起。

推荐实现顺序是：先做 census 和 metadata freeze，再回填 manifest，随后补 repo-level 回归测试，最后重跑 `program truth sync` / `program truth audit` 固定收敛结果。

## 技术背景

**语言/版本**：Python 3.11  
**主要依赖**：`program-manifest.yaml`、`ProgramService.validate_manifest()`、`program truth sync`、`program truth audit`、pytest  
**测试**：focused unit/integration + repo-level regression  
**目标平台**：根级 program truth ledger  
**约束**：

- 不在本 tranche 内修 `095/096/098/099/100/101/102/103/104/105/123/124/125/126`
- 不发明新的 capability、role 或依赖真值来“填满表格”
- `frontend_evidence_class` 只能镜像 canonical footer
- 非 release-scope 新回填 entry 保持 `roles: []` 与 `capability_refs: []`
- 回归校验必须进入现有 pytest 测试面，不能是孤立脚本；本 tranche 的最终 focused verification 必须显式运行它

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| 单一真值 | 只修根 manifest，不引入第二份 census 文档或 registry |
| 流程诚实 | 只清除“缺 entry 导致的 migration cause”，不把 release blocker 伪装成已关闭 |
| 最小改动面 | 优先做 manifest 数据回填与回归测试，不改 release audit 逻辑 |
| 历史兼容 | 允许历史 spec 先以 `depends_on: []`、空 `roles/capability_refs` 被纳管，避免伪真值 |

## 实施批次

### Phase 0：Formal freeze 与对抗评审

1. 起草 `spec.md`
2. 由 Avicenna 与 Russell 做两轮对抗评审
3. 收口 `branch_slug`、`depends_on`、`roles/capability_refs` 与 repo-level regression 的边界
4. 评审收敛后再进入 plan/tasks/实现

### Phase 1：Root census metadata freeze

1. 盘点当前所有带 `spec.md` 的 `specs/*` 目录
2. 计算 manifest 当前缺失的 entries：启动时 37 个历史缺口，加上本 tranche `141` 自身 entry 后的实际写集
3. 为每个缺失 entry 冻结最小 metadata：
   - `id`: 精确目录名
   - `path`: `specs/<dir>`
   - `depends_on`: 默认 `[]`；仅在已有 machine-readable 来源时填已知依赖
   - `branch_slug`: 若 `id` 符合 `<数字>-<slug>` 则取 `<slug>`，否则留空
   - `owner`: `team-frontend-governance`
   - `frontend_evidence_class`: 仅按 canonical footer 镜像；无 footer 则留空
4. 对新回填的非 release-scope entries 明确保持 `roles: []` 与 `capability_refs: []`
5. 特别核对 `066` 双目录共存场景，确保两个目录都被纳管

### Phase 2：Manifest backfill

1. 在 `program-manifest.yaml` 中按稳定顺序回填启动时缺失的 37 个历史 entries，并补上 `141` 自身 entry
2. 保持现有 release target / capability / closure audit authoring intent 不变
3. 避免改动既有已纳管 spec 的 capability mapping，除非 manifest 自身存在精确路径错误
4. 确认 `validate_manifest()` 对根 census 不再产生 missing-entry migration warnings

### Phase 3：Regression guard

1. 新增一条 repo-level pytest 回归测试，直接在当前仓库根目录加载 `program-manifest.yaml`
2. 断言所有带 `spec.md` 的 `specs/*` 目录都已被纳入 manifest
3. 断言不再存在 `migration_pending: manifest entry missing for specs/...`
4. 该测试必须放进默认 pytest 收集路径，并纳入本 tranche 的 focused verification 命令集；本 tranche 的最终 tests evidence 必须实际运行到这条测试

### Phase 4：Truth ledger resync 与结果固定

1. 运行 `uv run ai-sdlc program validate`
2. 运行 `uv run ai-sdlc program truth sync --dry-run`
3. 仅当 dry-run 与 repo-level regression 均表明 missing-entry cause 已清零时，才运行 `uv run ai-sdlc program truth sync --execute --yes`
4. 运行 `uv run ai-sdlc program truth audit`
4. 记录回填后的真实状态：
   - missing-entry migration cause 是否清零
   - `migration_pending_count` 是否为 `0`，或仅剩其他已知真实 migration cause
   - `truth_snapshot.state` 是否按当前仓库基线收敛为 `blocked`
   - `frontend-mainline-delivery` blocker 是否原样保留
5. 更新 `task-execution-log.md` / `development-summary.md`

### Phase 5：第二 tranche 交接

1. 基于回填后的 truth audit 结果，创建下一 tranche 的 formal docs
2. 该 tranche 只处理 `frontend-mainline-delivery` 的真实 blocker：
   - `095/096/098/099/100/101/102/103/104/105/123/124/125/126`
3. 交接必须带上以下 machine-readable 证据口径：
   - `release_capabilities`
   - `blocking_refs`
   - `migration_pending_count`
   - `migration_pending_specs`
4. 在交接口径中明确：`141` 只清 migration noise，不宣称 release-ready

## 风险与回退

- **风险 1：把历史 spec 的空依赖误读成真实无依赖**
  - 回避：spec/plan/tasks 中明确 `depends_on: []` 仅表示“根 manifest 尚未编制依赖真值”
- **风险 2：把非 release-scope 历史 spec 误纳入 capability audit**
  - 回避：新回填 entry 保持空 `roles/capability_refs`，不修改 release target membership
- **风险 3：以后新增 spec 目录再次漏纳管**
  - 回避：增加 repo-level pytest regression，直接对当前仓库根目录做 census
- **风险 4：回填后仍残留其他 migration cause**
  - 回避：验收时区分“missing-entry cause 已清零”和“是否还有其他剩余 migration cause”

## 验证策略

最小验收命令集：

- `python -m ai_sdlc adapter status`
- `python -m ai_sdlc run --dry-run`
- `uv run pytest tests/unit/test_program_service.py -q`
- `uv run pytest <repo-level census regression test> -q`
- `uv run ai-sdlc program validate`
- `uv run ai-sdlc program truth sync --dry-run`
- `uv run ai-sdlc program truth sync --execute --yes`（仅在 dry-run 与 repo-level census regression 均通过后执行）
- `uv run ai-sdlc program truth audit`

## 退出条件

1. `141` 的 spec/plan 完成两轮对抗评审并收敛
2. 根 manifest 的历史 missing spec entry 数量从 `37` 降到 `0`，当前工作树总 missing spec entry 也降到 `0`
3. repo-level 回归测试能阻断未来再次漏纳管
4. truth ledger 不再混入 “manifest entry missing” 这一类 migration cause
5. 第二 tranche 的 formal docs 已建立，并只聚焦真实 release blocker
