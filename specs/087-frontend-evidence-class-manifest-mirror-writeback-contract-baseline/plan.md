# 执行计划：Frontend Evidence Class Manifest Mirror Writeback Contract Baseline

**功能编号**：`087-frontend-evidence-class-manifest-mirror-writeback-contract-baseline`  
**创建日期**：2026-04-09  
**状态**：docs-only prospective writeback contract

## 1. 目标与定位

`087` 的目标是把 `frontend_evidence_class` 的 future manifest mirror generation/writeback 规则单独冻结成 baseline：明确 mirror writer 属于哪一类 command family、必须满足哪些前置条件、允许改 manifest 的哪一小块、哪些 read-only surfaces 永远不得 opportunistic write。它不实现 runtime，不决定具体子命令名，也不推进 status 或 close-stage resurfacing。

## 2. 范围

### 2.1 In Scope

- 创建 `087` formal docs 与 execution log
- 推进 `.ai-sdlc/project/config/project-state.yaml` 到 `87`
- 冻结 mirror writeback 的 owning family 与 write intent
- 冻结 write preconditions、allowed write modes、mutation scope
- 冻结 refresh timing、idempotency / overwrite semantics
- 冻结 forbidden write surfaces

### 2.2 Out Of Scope

- 修改 `src/` / `tests/`
- 修改 `program-manifest.yaml`
- 冻结具体 CLI 子命令名、flags 或 payload
- 修改 `program validate` 的 drift semantics
- 修改 `program status`、`status --json`、`workitem close-check`
- retroactively 改义 `068` ~ `071`

## 3. 变更文件面

当前批次只允许改以下文件面：

- `specs/087-frontend-evidence-class-manifest-mirror-writeback-contract-baseline/spec.md`
- `specs/087-frontend-evidence-class-manifest-mirror-writeback-contract-baseline/plan.md`
- `specs/087-frontend-evidence-class-manifest-mirror-writeback-contract-baseline/tasks.md`
- `specs/087-frontend-evidence-class-manifest-mirror-writeback-contract-baseline/task-execution-log.md`
- `.ai-sdlc/project/config/project-state.yaml`

## 4. Writeback Contract Rules

### 4.1 Owner and intent

- writer 唯一 owner family 是显式 `ai-sdlc program ...` write surface
- `087` 冻结 owner family，不冻结具体子命令名
- writer 不得作为 read-only command 的隐式副作用存在

### 4.2 Preconditions

- canonical source 只认 `spec.md` footer metadata
- footer truth 必须通过 `082` / `085` 已冻结的 authoring contract
- target spec 必须唯一映射到 manifest `specs[]` entry
- precondition 不成立时必须 stop，不得猜测性写入

### 4.3 Allowed write modes and scope

- 允许 `targeted sync`
- 允许 `bounded bulk sync`
- 两种模式复用同一 writer rules
- 单个 target spec 的唯一合法 mutation scope 是 `specs[] .frontend_evidence_class`

### 4.4 Refresh timing and overwrite

- stale / missing mirror 允许短暂存在，直到显式 sync 被触发
- validate / status / close-check 只负责读与报，不负责 auto-heal
- same-value sync 为 no-op
- stale-value sync 显式覆盖 canonical truth

### 4.5 Forbidden write surfaces

- `verify constraints`
- `program validate`
- `program status`
- `program plan`
- `status --json`
- `doctor`
- `workitem close-check`

## 5. 分阶段计划

### Phase 0：contract reconciliation

- 回读 `082` ~ `086`
- 回读 `docs/USER_GUIDE.zh-CN.md` 中 read-only / bounded surface 边界
- 回读 `program` / `workitem close-check` 的 CLI 与 service 落点

### Phase 1：writeback contract baseline freeze

- 新建 `087` formal docs
- 写清 owner family、preconditions、allowed write modes、mutation scope
- 写清 refresh timing、overwrite semantics 与 forbidden write surfaces

### Phase 2：verification and archive

- 运行 docs-only / read-only 验证
- 记录当前 runtime truth 仍未变化
- 归档 commit

## 6. 最小验证策略

- `uv run ai-sdlc verify constraints`
- `uv run ai-sdlc program status`
- `git diff --check -- .ai-sdlc/project/config/project-state.yaml specs/087-frontend-evidence-class-manifest-mirror-writeback-contract-baseline`

## 7. 回滚原则

- 如果 `087` 让人误以为 mirror writer 已经实现，必须回退
- 如果 `087` 允许 read-only surface opportunistic write，必须回退
- 如果 `087` 允许 writer 修改 manifest 其他字段，必须回退
- 如果本轮误改 `src/`、`tests/`、`program-manifest.yaml` 或既有 spec，必须回退
