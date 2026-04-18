---
related_spec: specs/162-agent-adapter-canonical-consumption-proof-carrier-baseline/spec.md
related_plan: specs/162-agent-adapter-canonical-consumption-proof-carrier-baseline/plan.md
---

# 162 Tasks

## 批次策略

### Batch 1: formal freeze

- 回填 `162` formal docs，替换脚手架占位内容。
- 复核 manifest/project-state 派生改动是否与新工单一致。

### Batch 2: carrier red-green

- 先补 proof carrier 红灯测试。
- 再以最小实现补齐 `adapter exec -- <command>`。
- 用 unit + integration 双层验证锁死 fail-closed 与 proof 注入语义。

### Batch 3: repo verification

- 在当前仓库验证普通命令仍 `unverified`、carrier 子命令可见 `verified`。
- 回填执行归档，并确认 release/program truth 不再把 canonical proof 缺失当成唯一 blocker。

## 任务清单

- [x] T11 formal docs freeze
  - 优先级: P0
  - 依赖: 无
  - 文件: `specs/162-agent-adapter-canonical-consumption-proof-carrier-baseline/`
  - 验收: `162` 不再保留 direct-formal scaffold 占位文案，范围/命令面/边界已冻结
  - 验证: `uv run ai-sdlc verify constraints`

- [x] T21 proof carrier unit red
  - 优先级: P0
  - 依赖: T11
  - 文件: `tests/unit/test_ide_adapter.py` 或等价 unit 测试文件
  - 验收: 当前代码库在命令为空、canonical 缺失或 target 不支持时的 carrier 行为被失败测试锁定
  - 验证: `uv run pytest tests/unit/test_ide_adapter.py -k "canonical_proof_carrier" -q`

- [x] T22 proof carrier CLI integration red
  - 优先级: P0
  - 依赖: T21
  - 文件: `tests/integration/test_cli_adapter.py`
  - 验收: 当前 CLI 不存在 `adapter exec -- <command>` proof carrier 时，集成测试明确失败
  - 验证: `uv run pytest tests/integration/test_cli_adapter.py -k "canonical_proof_carrier" -q`

- [x] T23 implement adapter exec carrier
  - 优先级: P0
  - 依赖: T22
  - 文件: `src/ai_sdlc/cli/adapter_cmd.py`、必要 helper 所在模块
  - 验收: carrier 能注入 canonical digest/path 到子命令环境，并对非法输入 fail closed
  - 验证: `uv run pytest tests/unit/test_ide_adapter.py tests/integration/test_cli_adapter.py -k "canonical_proof_carrier" -q`

- [x] T24 repo verification and formal sync
  - 优先级: P1
  - 依赖: T23
  - 文件: `specs/162-agent-adapter-canonical-consumption-proof-carrier-baseline/`、必要时 `.ai-sdlc/project/config/project-state.yaml`、`program-manifest.yaml`
  - 验收: 执行日志记录普通路径与 carrier 路径的差异，并完成框架入口验证
  - 验证: `python -m ai_sdlc adapter status`、`python -m ai_sdlc adapter exec -- python -m ai_sdlc adapter status --json`
