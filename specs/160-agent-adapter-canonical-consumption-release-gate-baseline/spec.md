# 功能规格：Agent Adapter Canonical Consumption Release Gate Baseline

**功能编号**：`160-agent-adapter-canonical-consumption-release-gate-baseline`
**创建日期**：2026-04-18
**状态**：收口中
**输入**：`specs/158-*`、`specs/159-*`、`program-manifest.yaml`、`src/ai_sdlc/core/program_service.py`、`src/ai_sdlc/core/close_check.py`、`tests/unit/test_program_service.py`

## 问题定义

`159` 已经把 canonical content consumption proof 的 runtime 字段与 machine-verifiable 协议落进 adapter governance surface，但 release/program truth 还没有消费这条 proof。结果就是：

- root closure audit 已经明确 `agent-adapter-verified-host-ingress` 仍是 `partial`
- `adapter status` 可以给出 `adapter_canonical_consumption_result=unverified`
- 但 `ProgramService` 还不会把这件事折算成 release capability blocker

这会让 `160` 之前的系统出现一个结构性缺口：formal docs 已经承认 canonical content actual consumption proof 仍缺，runtime 也能输出该状态，但 release/program truth 依然可能继续表现为 ready。

## 范围

- **覆盖**：
  - 在 `ProgramService` 中让 `agent-adapter-verified-host-ingress` capability 消费 canonical consumption truth
  - 当 canonical consumption proof 未 `verified` 时，让 release/program truth 保持 `blocked`
  - 在 `program-manifest.yaml` 中补齐 capability/spec 映射，让该 gate 有正式 carrier
  - 以 TDD 补充 program truth 单元测试
- **不覆盖**：
  - 新增宿主原生 proof 协议
  - 放宽 `verified_loaded` / `adapter_verification_result` 的既有 ingress 语义
  - 重做 `159` 的 canonical proof runtime 实现

## 用户故事与验收

### US-160-1 — Maintainer 需要 release truth 真正消费 canonical proof

作为 **maintainer**，我希望 canonical consumption proof 一旦未达到 `verified`，release/program truth 就自动保持 `blocked`，而不是只在文档中说明它是剩余缺口。

**验收**：

1. **Given** `agent-adapter-verified-host-ingress` 已被映射为 release capability，**When** `adapter_canonical_consumption_result=unverified`，**Then** `ProgramService.build_truth_snapshot()` 必须把该 capability 标为 `audit_state=blocked`
2. **Given** canonical digest 与已记录 proof 一致且 `adapter_canonical_consumption_result=verified`，**When** 计算 truth snapshot，**Then** 该 gate 不再额外注入 canonical blocker

### US-160-2 — Reviewer 需要 machine-verifiable blocker 而不是文案 blocker

作为 **reviewer**，我希望 blocker 来源于 adapter governance surface 的 machine-verifiable truth，而不是人工维护的文案或 root summary。

**验收**：

1. **Given** canonical proof 未 `verified`，**When** 读取 capability blocker，**Then** 能看到稳定 reason code `adapter_canonical_consumption:<result>`
2. **Given** root summary 文案发生变化但 canonical proof 状态不变，**When** 重新计算 truth，**Then** blocker 结论不受 summary 文案影响

## 功能需求

- **FR-160-001**：系统必须把 `agent-adapter-verified-host-ingress` 作为 release capability 正式登记到 `program-manifest.yaml`
- **FR-160-002**：系统必须让 `ProgramService` 基于 adapter governance surface 的 canonical consumption truth 计算该 capability 的 gate blocker
- **FR-160-003**：当 canonical consumption result 不是 `verified` 时，系统必须产生 `adapter_canonical_consumption:<result>` blocker
- **FR-160-004**：当 canonical consumption result 为 `verified` 时，系统不得继续保留该 blocker
- **FR-160-005**：`160` 只消费 `159` 已提供的 runtime proof，不得反向篡改 ingress verdict 或伪造宿主 proof

## 成功标准

- **SC-160-001**：`tests/unit/test_program_service.py` 新增的 canonical gate 测试通过
- **SC-160-002**：`program-manifest.yaml` 中存在 `agent-adapter-verified-host-ingress` release capability 与 `160` carrier 映射
- **SC-160-003**：执行 `python -m ai_sdlc run --dry-run` 时，当前仓库仍能完成安全预演
