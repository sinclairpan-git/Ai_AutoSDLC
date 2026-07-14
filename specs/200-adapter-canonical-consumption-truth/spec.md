# 功能规格：Adapter Canonical Consumption Truth Separation

**功能编号**：`200-adapter-canonical-consumption-truth`
**创建日期**：2026-07-14
**状态**：设计评审中
**基线 revision**：`origin/main@208a34c82da0474a3cf51f3758934a188758b33d`
**关联治理项**：`GAP-10 / T53B`，父项 `196-ai-sdlc-lean-code-self-reduction-governance`

## 1. 问题定义（NC-01）

### 1.1 Observed

1. repository release truth 在 `ProgramService._release_gate_adapter_blockers()` 中读取 `build_adapter_governance_surface()`；该 surface 又依赖本机环境与被 `.gitignore` 排除的 `.ai-sdlc/project/config/project-config.yaml`。
2. 同一 commit 在保存过本机 proof 的工作树中可为 `ready`，在 fresh checkout 中则回到 `adapter_canonical_consumption:unverified`；仓库真值因此不可重复。
3. `adapter exec` 自己读取 canonical 文件、计算 digest、注入子进程环境；下游仅把同一 digest 与同一文件比较后即返回 `adapter_canonical_consumption_result=verified`。该闭环只能证明 digest transport 一致，不能证明宿主或当前会话消费了内容。
4. 2026-07-14 现场使用 Codex CLI `0.137.0` 的 `codex debug prompt-input`，可观察到当前 `AGENTS.md` 全文出现在新 invocation 的 model-visible input；该慢探针能作为一次性验收，但不能证明已经运行中的父会话，也不适合进入默认 truth/status 路径。

### 1.2 Expected

- repository capability truth 只由 Git 可重放的 formal/close/verify evidence 决定，不读取 ignored config、父 shell 或当前宿主环境。
- per-session adapter consumption 继续在 `adapter status` 中独立表达；没有宿主提供的不可自证 attestation 时必须保持 `unverified`。
- digest/path 匹配只表达 transport match，不得升级为 repository capability 或 current-session consumption `verified`。

## 2. 范围与非目标

### 2.1 覆盖范围

- 将 `agent-adapter-verified-host-ingress` 的 repository capability gate 从本机 adapter 状态迁移到 tracked work-item evidence。
- 删除 `ProgramService` 中依赖本机 canonical consumption 状态的 release blocker 与专用提示分支。
- 将 `AI_SDLC_ADAPTER_CANONICAL_SHA256` / `AI_SDLC_ADAPTER_CANONICAL_PATH` 匹配降级为非权威 transport evidence；旧的本机 `verified` 记录不得继续被保留为可信 consumption proof。
- 保留 `adapter exec` 命令、参数、超时、环境透传、退出码和子进程行为。
- 用一次性脱敏 `codex debug prompt-input` 结果验证 Codex canonical path；不得提交完整 prompt。

### 2.2 明确非目标

- 不新增 receipt、schema、cache、探针命令、provider 抽象或第二套 evidence registry。
- 不在 `program truth audit`、`status`、`run --dry-run` 中启动 Codex、网络或慢探针。
- 不把官方契约或可伪造的宿主环境变量单独叙述为当前会话消费证明。
- 不删除或改名公共 `adapter exec`；其弃用/删除若需要，必须另立 L4 工作项。
- 不处理 GAP-11 source inventory，不混入结构减重或其他 truth 清仓。

## 3. 用户故事与验收

### US-200-1 — Maintainer 获得确定性的仓库能力真值（P0）

作为维护者，我希望同一 commit 的 adapter capability 在不同 fresh checkout 中得出相同结论，以便 release truth 可审计、可重复。

**验收场景**：

1. **Given** tracked required evidence 全部通过且本机 config 不存在，**When** 构建 truth snapshot，**Then** capability 为 `closed + ready`，且无 `adapter_canonical_consumption:*` blocker。
2. **Given** 分别存在本机 `verified` 与 `unverified` 配置，**When** 对同一 commit 构建 snapshot，**Then** computed capability、blocking refs 和 snapshot hash 不受本机状态影响。

### US-200-2 — Operator 不再收到自证的 consumption verified（P0）

作为操作者，我希望 transport digest 匹配仍可诊断，但不会被误报为宿主已经消费 canonical 内容。

**验收场景**：

1. **Given** digest/path 与当前 canonical 文件匹配，**When** 运行 `adapter status --json`，**Then** result 仍为 `unverified`，evidence 为非权威 transport evidence，`consumed_at` 为空。
2. **Given** 旧 config 保存了 `adapter_canonical_consumption_result=verified`，**When** 无独立宿主 attestation 重新查询，**Then** 旧值不再被保留为可信结果。
3. **Given** 通过 `adapter exec` 启动子命令，**When** 子命令查询 adapter status，**Then** 命令仍成功执行，但不得得到 consumption `verified`。

### US-200-3 — Reviewer 能区分 repository capability 与 runtime admission（P0）

作为 reviewer，我希望 tracked evidence 只证明框架合同已交付，而 runtime status 只表达当前会话可观察事实，避免两个状态面互相授予权限。

**验收场景**：

1. repository capability ready 不得让本机 `adapter status` 从 `unverified` 变为 `verified`。
2. transport evidence 不得授予 mutate 权限，也不得清除或创建 repository release blocker。

## 4. 功能需求

- **FR-200-001**：repository capability 计算不得读取 adapter local config 或宿主环境生成 canonical consumption blocker。
- **FR-200-002**：capability ID 保持 `agent-adapter-verified-host-ingress`，但 goal 必须明确其表示 tracked adapter proof/runtime contract 已交付，不代表当前会话消费。
- **FR-200-003**：required evidence 必须使用 `121/122/159/200` 的 truth-check 与 close-check；`160-163` 仅保留为 `spec_refs` provenance，不形成重复 gate。
- **FR-200-004**：env digest/path 匹配时，`adapter_canonical_consumption_result` 必须为 `unverified`；允许输出 `transport:env:AI_SDLC_ADAPTER_CANONICAL_SHA256` 作为诊断 evidence，但 `adapter_canonical_consumed_at` 必须为空。detail 必须精确等于 `Canonical adapter digest transport matched the current file; this does not prove that the host or current session consumed the canonical content.`，且不得出现旧的肯定式 `Canonical adapter content consumption is recorded from machine-verifiable evidence`。
- **FR-200-005**：旧 persisted `verified` consumption 状态不得跨查询保留为可信结果。
- **FR-200-006**：`adapter exec` 的命令面、参数、透传、timeout 和 exit code 必须保持兼容。
- **FR-200-007**：默认 CLI/truth/status 路径不得启动 `codex debug prompt-input`，不得持久化完整 model-visible prompt。
- **FR-200-008**：WI200 必须记录一次脱敏 Codex prompt-input probe：布尔 match、canonical digest、Codex version、exit code、耗时；不得记录 prompt 原文。

## 5. 历史合同修正

WI200 以证据真实性为由 supersede 以下历史语义，但不改写历史执行日志：

- WI159 `FR-003` 中“env digest/path 匹配即可记录 consumption verified”的结论；
- WI162 `US-162-1` / `SC-162-003` 中“carrier 子进程可见 consumption verified”的结论；
- WI163 基于 ignored local config 形成的 repository truth closure 假设。

保留的兼容面是 transport 协议与公共命令；被修正的是错误的可信度等级。

## 6. 影响分析与兼容合同（NC-02）

| 合同 | 影响 | 验证 |
|---|---|---|
| CC-01 公共 CLI | 命令名、参数、退出码不变 | adapter CLI integration |
| CC-02 JSON/状态语义 | `verified` → `unverified` 为获准 truth correction | unit + integration exact assertions |
| CC-03 artifact/schema | 字段与 schema 不变 | payload key assertions |
| CC-05 telemetry/truth | repo snapshot 不再读取 local state | ProgramService unit + truth audit |
| CC-06 配置/环境优先级 | ignored config 与 env 不能影响 repo capability | verified/unverified/missing matrix |
| CC-07 跨平台 | 不新增 path/进程逻辑；保留现有 carrier 平台测试 | full CI / Windows jobs |
| CC-08 共享 CLI | 发布后做全局 CLI 与 sibling smoke | release smoke |

不确定或缺失证据一律 fail closed；只有 repository capability 与 runtime admission 已被测试证明隔离后才可关闭 GAP-10。

## 7. 预算、停止与回退（NC-03 / NC-05 / NC-06）

- 手写产品代码：新增不超过 12 LOC，净变化至少 `-15 LOC`；产品文件最多 2 个；公共抽象 0。
- 测试：新增不超过 30 LOC，受影响测试切片净 LOC 不增长；测试文件最多 4 个；不新增 fixture/snapshot。
- 允许的产品文件：`src/ai_sdlc/core/program_service.py`、`src/ai_sdlc/integrations/ide_adapter.py`。
- 允许的测试文件：`tests/unit/test_program_service.py`、`tests/unit/test_ide_adapter.py`、`tests/integration/test_cli_adapter.py`、`tests/integration/test_repo_program_manifest.py`。
- 若需要新状态模型、receipt、cache、probe registry、公共命令或超出预算，立即停止并重新评审。
- runtime truth correction 与 repository gate separation 必须使用两个独立提交：先提交不可自证的 runtime 安全底线（A），再提交 repository 分层（B）。
- 回退 owner：WI200 实施者。B 可独立 revert；由于 A 仍强制 consumption `unverified`，回退后 repository capability 只能稳定恢复为 blocked。A 不得整体 revert 回自证 `verified`；若 A 本身回归，使用 forward fix 或仅回退非安全机械部分，同时保留 hard `unverified` 语义。
- truth artifact 用 `program truth sync --execute --yes` 从选择性回退后的 tracked evidence 重建；本机旧 config 不作为恢复源。execution log 必须保留一次 B 选择性回退演练，证明结果为 runtime unverified + repository blocked。

## 8. 成功标准（NC-04）

- **SC-200-001**：先出现可归因的 RED，再以最小实现转 GREEN。
- **SC-200-002**：fresh checkout 与 local config matrix 下 repository capability 稳定为 `closed + ready`。
- **SC-200-003**：env/carrier match 不再产生 consumption `verified`，旧 persisted verified 不再保留，detail 不再声称 machine-verifiable host/current-session consumption。
- **SC-200-004**：`adapter exec` 公共 surface 和 runtime admission 行为无未批准差异。
- **SC-200-005**：targeted、全量 pytest、Ruff、constraints、program validate/truth audit、mainline fresh smoke 全部通过。
- **SC-200-006**：两个对抗 agent 对同一 formal hash 与最终实现 hash 均明确 PASS。
