# 开发总结：159-agent-adapter-canonical-consumption-proof-runtime-baseline

**功能编号**：`159-agent-adapter-canonical-consumption-proof-runtime-baseline`
**收口日期**：2026-04-18
**收口状态**：`program-close-ready`

## 交付摘要

- `159` 为 IDE adapter runtime 新增了独立的 canonical content consumption proof 维度，不再把 host ingress 真值与 canonical 内容消费证明混为一谈。
- 本工单交付了 `adapter_canonical_content_digest`、`adapter_canonical_consumption_result`、`adapter_canonical_consumption_evidence`、`adapter_canonical_consumed_at` 四个持久化/状态输出字段，以及基于 `AI_SDLC_ADAPTER_CANONICAL_SHA256` 和可选 `AI_SDLC_ADAPTER_CANONICAL_PATH` 的 machine-verifiable proof 协议。
- 该实现保持既有 `adapter_ingress_state` / `adapter_verification_result` 语义不变；canonical proof 缺失、错误或过期时只会回退 canonical consumption truth，不会伪造或降级 host ingress verdict。
- 本工单已通过 focused pytest、`uv run ruff check`、`workitem close-check` 与 fresh truth sync；仓库级 `verify constraints` 仍可因外部 `158` branch lifecycle 尾项阻断，但不影响 `159` 自身 runtime baseline 的完成判定。

## 备注

- 后续若宿主原生提供更稳定的 canonical consumption proof surface，应在新的扩展工单中兼容额外协议键，而不是在 `159` 内用推断逻辑放宽 machine-verifiable 约束。
