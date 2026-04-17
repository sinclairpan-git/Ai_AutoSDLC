# 功能规格：Agent Adapter Canonical Consumption Proof Runtime Baseline

**功能编号**：`159-agent-adapter-canonical-consumption-proof-runtime-baseline`
**创建日期**：2026-04-18
**状态**：草稿
**输入**：Add a distinct machine-verifiable proof path for canonical adapter content consumption so Codex/AGENTS.md truth no longer depends on inference from host-type env signals alone.

**范围**：为 IDE adapter runtime 增加独立的 canonical content consumption proof 字段、环境变量协议与状态输出；不改变现有 `adapter_ingress_state` / `adapter_verification_result` 的判定语义，不假设宿主今天已经原生提供该证明信号。

## 用户场景与测试（必填）

### 用户故事 1 - 维护者需要把“宿主类型存在”与“canonical 内容已被消费”分离（优先级：P0）

作为框架维护者，我希望 `adapter status` 和项目配置里同时保留 host ingress truth 与 canonical consumption truth，以便 close-check / capability closure 不再把宿主环境变量误当成内容消费证明。

**优先级说明**：这是当前 agent-adapter verified host ingress cluster 的唯一剩余 partial 缺口，直接阻塞后续收口。

**独立测试**：在 Codex target 下分别验证 digest 缺失、digest 匹配、digest 不匹配三种场景，确认 ingress truth 维持原判定，而 canonical consumption result 单独变化。

**验收场景**：

1. **Given** 仓库已 materialize `AGENTS.md` 且运行在 Codex host，**When** 未提供 canonical digest proof 环境变量，**Then** `adapter_ingress_state=verified_loaded` 仍可成立，但 `adapter_canonical_consumption_result=unverified`。
2. **Given** 宿主提供的 canonical digest 与当前 canonical 文件摘要一致，且可选 path 与 canonical path 一致，**When** 重新执行 adapter select/init，**Then** 项目配置记录 `adapter_canonical_consumption_result=verified` 与 machine-verifiable evidence。
3. **Given** 宿主提供了错误 digest 或错误 canonical path，**When** 重新执行 adapter select/init，**Then** canonical consumption proof 保持 `unverified`，不会把错误信号升级为 verified。

---

### 边界情况

- canonical 文件被用户改写后，已记录 proof 只有在当前文件 digest 仍与记录值一致时才可继续视为 verified。
- generic / unsupported target 不引入虚假的 canonical consumption verified 结果；无 canonical 文件时只能输出空 digest 与 `unverified`/既有 degrade 语义。

## 需求（必填）

### 功能需求

- **FR-001**：系统必须为当前 canonical adapter 文件计算并暴露稳定的内容摘要字段 `adapter_canonical_content_digest`；当 canonical 文件不存在时，该字段必须为空字符串。
- **FR-002**：系统必须支持独立的 canonical consumption proof 协议，至少接受 `AI_SDLC_ADAPTER_CANONICAL_SHA256`，并可选接受 `AI_SDLC_ADAPTER_CANONICAL_PATH` 作为路径绑定。
- **FR-003**：只有当 canonical 文件存在、当前 digest 与 `AI_SDLC_ADAPTER_CANONICAL_SHA256` 完全一致、且 `AI_SDLC_ADAPTER_CANONICAL_PATH` 缺失或等于 canonical path 时，系统才可把 `adapter_canonical_consumption_result` 记录为 `verified`。
- **FR-004**：系统必须把 canonical consumption proof 的结果、evidence 与时间戳持久化到 project config，并在 `ai-sdlc adapter status --json` / status telemetry surface 中暴露。
- **FR-005**：系统不得因为 canonical consumption proof 缺失或不匹配而降级现有 `adapter_ingress_state` 与 `adapter_verification_result`；它们继续只表达 host ingress truth。
- **FR-006**：当已记录的 canonical consumption proof 与当前 canonical 文件 digest 不再匹配时，系统必须自动回退为 `unverified`，避免把过期 proof 当成当前真值。

### 关键实体（如涉及数据则必填）

- **Canonical Content Digest**：当前 canonical adapter 文件的 `sha256:` 摘要，来源于仓库本地文件内容。
- **Canonical Consumption Proof**：宿主或 wrapper 通过环境变量显式提供的 machine-verifiable 证明，声明当前 canonical 内容已被宿主消费。
- **Adapter Governance Surface**：`adapter status` / `status --json` 返回的统一状态面，需同时暴露 ingress truth 与 canonical consumption truth。

## 成功标准（必填）

### 可度量结果

- **SC-001**：新增单元与集成测试覆盖 digest 缺失、匹配、不匹配场景，且聚焦测试通过。
- **SC-002**：`adapter status --json` 可稳定输出 canonical digest / result / evidence / consumed_at 字段，且不会改变既有 verified ingress 行为。
