# Development Summary

`185` 将 `093` 的 installed runtime update advisor 从 docs-only contract 落成 runtime：新增非阻断版本检测、用户级缓存、freshness/backoff、notice ack 去重、`self-update` helper machine contract，以及显式更新 instructions。

## 当前状态

- 本地实现：已完成
- 本地 focused 验证：已通过
- 全量回归：已通过（2476 passed, 2 skipped）

## 发布边界

本工作项不执行静默自升级，也不替换正在运行的 CLI。企业内部源、PyPI channel truth、IDE/AI 宿主绑定可在后续批次扩展；当前 runtime 已提供 `identity / evaluate / ack-notice` machine contract 作为唯一判断面。
