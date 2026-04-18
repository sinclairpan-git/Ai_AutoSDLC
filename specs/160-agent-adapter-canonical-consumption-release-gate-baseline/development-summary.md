# 开发总结：160-agent-adapter-canonical-consumption-release-gate-baseline

**功能编号**：`160-agent-adapter-canonical-consumption-release-gate-baseline`
**收口状态**：`gate-implemented / carrier-synced`

## 交付摘要

- `160` 把 `159` 已输出的 canonical consumption proof 正式接入 release/program truth gate。
- `ProgramService` 现在会在 `agent-adapter-verified-host-ingress` 上消费 adapter governance surface；当 canonical proof 不是 `verified` 时，稳定给出 `adapter_canonical_consumption:<result>` blocker。
- `program-manifest.yaml` 已补上该 release capability 与 `160` carrier 映射，避免 gate 只存在于代码里。
