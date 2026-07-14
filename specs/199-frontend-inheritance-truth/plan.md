---
related_plan: "specs/196-ai-sdlc-lean-code-self-reduction-governance/plan.md"
related_doc:
  - "specs/199-frontend-inheritance-truth/spec.md"
  - "specs/196-ai-sdlc-lean-code-self-reduction-governance/tasks.md"
---
# 实施计划：Frontend Inheritance Truth Closure

**编号**：`199-frontend-inheritance-truth` | **日期**：2026-07-13 | **风险**：L2

## 1. 技术裁决

`frontend-mainline-delivery` 是框架能力发布目标，其 16 个 carrier 当前都显式声明 `framework_capability`。requirement helper 必须逐 ref 直接解析 spec footer，并与 manifest mirror 精确比较：全量明确且一致时，项目实例 inheritance requirement 可审计豁免；footer missing/empty/malformed、mirror 不一致或消费采用分类继续走项目实例 fail-closed 路径。其他 capability 不计算该 requirement。

waiver 不是发布豁免：`ProgramService` 还必须独立加载 generation/quality artifact。generation 校验 page schema 精确集合、provider manifest、declared install strategy/provider/packages、非空 delivery entry 与 adapter；quality 调用 `frontend_quality_platform.py` 新提取的私有 internal-coherence helper。公开 project validator 继续强制 snapshot 并叠加 effective-style 检查，不能形成通用 bypass。artifact 不健康时产生专用 framework artifact blocker，并把 family/path/reason 放入 truth guidance。

## 2. 边界与结构

```text
src/ai_sdlc/core/program_service.py
  _frontend_inheritance_requirement_for_capability(...)  # 仅 frontend-mainline，直接对账 footer+mirror
  _frontend_framework_artifact_blockers(...)              # snapshot-independent health
  _build_truth_capability_state(...)                      # gate 消费 requirement
  _truth_ledger_frontend_capability_user_guidance(...)    # waiver 时不输出伪 remediation
  build_truth_ledger_surface(...)                         # 输出 requirement 证据

src/ai_sdlc/core/frontend_quality_platform.py
  _validate_frontend_quality_platform_internal(...)  # 私有内部一致性
  validate_frontend_quality_platform(...)            # 继续强制 project snapshot

tests/unit/test_program_service.py
  framework health / consumer states / missing / mixed / mirror conflict / raw status

tests/unit/test_frontend_quality_platform.py
  public validator 的 `None` 负向禁止合同 + 既有 project validator 非回归

tests/integration/test_cli_status.py
  consumer generation/quality 非 inherited blocker 的 status JSON 精确集合

specs/199-frontend-inheritance-truth/
  spec.md / plan.md / tasks.md / task-execution-log.md / development-summary.md
```

允许按实现必要性调整私有 helper 名称，但不得扩展到新文件、公共 API、schema 或 registry。

## 3. 宪章与合同响应

| 门禁 | 计划响应 |
|---|---|
| 单一真值 | requirement 直接读取 canonical footer 并对账 mirror；不解析 slug、不建第二表 |
| Fail closed | 只有 frontend-mainline 的 footer/mirror 全量肯定且 schema/semantic artifacts 健康时放行；consumer 非 inherited 状态全部阻断 |
| 用户前端确认 | 本项不选择前端方案、不 execute solution-confirm、不生成前端实现 |
| 兼容优先 | 原始 handoff/status 与 consumer blocker 合同冻结，先 RED 后 GREEN |
| 精简治理 | 两个既有产品文件内窄改动，55/160 LOC 上限，无新模块/依赖/config/schema |
| 可回退 | 整个 WI closure revert、父项 reopen、truth resync；无迁移和不可逆副作用 |

## 4. 阶段计划

### Phase 0：事实冻结与设计 admission

- 记录修复前 handoff、truth blocker、16 个 canonical evidence class 与既有 waiver 先例。
- 冻结 alternative A/B/C、scope、NC/CC、预算、rollback。
- 对 `spec.md + plan.md + tasks.md` 计算稳定 SHA-256。
- 兼容安全与精简效率两个只读 Agent 独立复算同一 hash；任一 finding 成立即修订、重算并双重评审，直到同哈希双 PASS。

### Phase 1：TDD RED

- 新增 framework-only 无 snapshot 且 artifacts 健康 fixture，期待 release audit 不含两个 inheritance blockers 且公开 waiver。
- 新增 generation/quality missing/malformed/cross-ref 损坏 fixture，并至少覆盖 schema-valid 的 generation page schema 或 provider/packages semantic drift及 delivery entry empty，期待专用 framework artifact blocker 与含 path/reason 的 truth guidance。
- 新增 public quality validator 传 `None` 必须失败的负向用例，确保私有 helper 提取不产生运行时旁路。
- 将现有 drift fixture 明确改成 `consumer_adoption`，并覆盖 unknown/not-inherited/blocked 都 release-blocked。
- 新增缺失 ref、混合分类、canonical footer missing/empty/malformed、mirror conflict fail-closed 与 raw inheritance status 不变断言。
- 更新既有 CLI status consumer fixture 的精确 blocker 集合，使其同时包含 quality `not_inherited`；不得改 fixture 为 framework waiver 来规避安全收紧。
- 仅测试变更时运行定向命令，确认失败原因来自缺失 requirement 判定而非 fixture 错误。

### Phase 2：最小 GREEN

- 在 `ProgramService` 增加一个仅限 frontend-mainline、直接读取 footer+mirror 的私有全称判定 helper，以及一个复用既有 loaders/validator/provider/install strategy 的 framework artifact health helper。
- `frontend_quality_platform.py` 从现有 public validator 提取私有 internal-coherence helper；public signature 与 snapshot 强制条件不变。
- release blocker、guidance 与 surface 使用同一 requirement；禁止复制三套分类逻辑。consumer 状态只有 `inherited` 放行。
- waiver 只跳过不适用的项目实例 inheritance gate，不跳过 framework artifact health 或其他 required evidence。
- 达到 GREEN 后立即核对 LOC、allowlist 与副作用。

### Phase 3：验证、truth closure 与最终评审

- 定向：`uv run pytest tests/unit/test_program_service.py tests/unit/test_frontend_quality_platform.py -q`；必要时加 blocker map integration test。
- CLI status：`uv run pytest tests/integration/test_cli_status.py::test_status_json_blocks_frontend_inheritance_drift_in_truth_ledger -q`。
- 全量：`uv run pytest -q`。
- 静态：`uv run ruff check src tests`、`uv run ai-sdlc verify constraints`、`git diff --check`。
- truth：在目标 commit 上执行 sync/audit，记录 snapshot 三元组、exact blocker delta、GAP-10/GAP-11 保留状态。
- 两个 Agent 对同一最终 HEAD 分别从兼容安全与精简效率复审；任一 FAIL 回到 RED/GREEN。

### Phase 4：PR 与 mainline

- 推送独立分支并创建 PR，`@codex review`，约五分钟 heartbeat 监控 review/checks。
- actionable finding 在同分支最小修复，重跑相关验证、双 Agent 复审、重新请求 Codex。
- review 无问题且 checks 全绿后 squash merge；在 `origin/main` 等价 worktree 重跑定向测试与 truth audit。

## 5. 关键路径与证据

| 关键路径 | 主证据 | 失败判定 |
|---|---|---|
| framework-only waiver | unit fixture + schema/semantic artifact health + truth refs | 任一 GAP-09 blocker仍存在、未公开 requirement 或 artifact 漂移被放行 |
| consumer protection | unknown/not-inherited/blocked fixtures | 任一非 inherited 状态不阻断或 next action 丢失 |
| fail-closed classification | ref/footer missing、footer malformed、mixed、mirror conflict | 获得 waiver 或 surface 同时显示错误 waiver |
| raw handoff compatibility | status/handoff assertions | missing snapshot 被伪造成 inherited/unknown |
| repo truth closure | fresh snapshot + audit exact delta | 新 blocker、validation error、GAP-10/11 被误改 |
| lean budget | numstat/allowlist | 产品 >55、测试 >160 或新增模块/依赖/schema |

## 6. 停止与回退

- 需要执行任何 frontend solution confirmation/apply 时立即停止；该路径超出本项授权。
- classification 不能仅靠现有 manifest/spec truth 安全判定时停止，不用默认值放行。
- framework artifact blocker 不提供自动修复：`uv run ai-sdlc program truth audit` 必须直接输出 artifact family、canonical path 与校验 reason；仅允许按该证据从对应 owning work item 或 revert 恢复已知良好 artifact，再重跑同一 audit。无 snapshot 时禁止 materialize 命令回落默认 provider。
- 超预算先删重复测试/逻辑；仍超预算则重新设计，不建立通用 waiver framework。
- 回退整个 WI-199 closure，重开父项 GAP-09，再运行 truth sync/audit；两个 GAP-09 blocker 应恢复且 closure 文档不得继续声称 closed。若未恢复，视为回退失败并阻断交付。

## 7. 当前开放问题

无需要用户裁决的问题。前端技术栈 dry-run 仅用于证明执行边界，本项不进入前端实现，因此不需要请求方案确认。
