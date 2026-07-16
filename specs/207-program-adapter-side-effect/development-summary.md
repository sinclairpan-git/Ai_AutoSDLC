# WI-207 Development Summary

**状态**：formal Round 3 review candidate；尚未修改产品代码

WI207 关闭 WI196 新登记的 GAP-12：任意 `program ...` 在业务命令前隐式刷新 IDE adapter，导致
Program Truth/验证命令和 program 集成测试可能改写真实 checkout 的 tracked Cursor rule。

当前冻结的最小实现是：`src/ai_sdlc/cli/main.py` 只增加一个 `"program"` bypass member；
`tests/integration/test_cli_program.py` 增加默认 hook 隔离和显式 real-hook byte-stability。产品预算最多
1 行，不修改 adapter 实现、ProgramService、program handlers、resume-pack 或 verify telemetry。

只读证据已证明 resume-pack 绝对路径/字段丢失属于 `status/recover/handoff` 的另一条 continuity
重建链，已拆为 GAP-13 / WI208。WI207 不是减重成果，不计 `completed_reduction`；其价值是消除
减重验收过程中的无关工作树污染和测试越界写入。

进入 implementation 的前置是：child 与父路线六份 formal 文件在同一 combined hash 上取得
Pascal/精简直接性和 Confucius/兼容安全双 PASS，formal PR 合入 main。实现完成后只关闭 GAP-12；
WI208 关闭后才继续下一个原子减重候选，WI196/RC08 全部满足前不发布版本。

当前 formal truth 为 ready/fresh、inventory complete、zero blocker；root exact truth test、constraints、
validate/audit 与 diff-check 已通过。精确 snapshot/hash 和可变计数只以 terminal
`program-manifest.yaml` 为准。

Round 1 combined `f74a06ab...de75` 被 Pascal 与 Confucius 双 FAIL：父测试例外、NC 适用矩阵、
CC 编号、T56 全局恢复门禁及 continuity Exact Next 存在合同脱节。产品一行方案、测试必要性、
execute/adapter 兼容和 WI207/WI208 边界未被否定。当前按 findings 统一修订，旧 verdict 作废；新
combined hash 必须由双方从零复审。

Round 1 findings 已全部按共同合同闭环并重跑 truth/constraints/root exact/diff-check。Round 2 将使用新
combined hash；双 PASS 后不再修改 formal target，直接进入 formal PR。任何新 finding 都使 Round 2
target 作废并重新执行终态同步与复审。

Round 2 两位 reviewer 仅发现父 formal 顶层范围措辞仍落后于已经修正的 FR-12/SC-04 和当前五件套
allowlist；现已同步。Round 1 的实质合同 findings 继续保持闭环。Round 3 将复审新的六文件 hash，
旧 `f74a06ab...` 与 `262d2613...` verdict 均只保留为审计历史。
