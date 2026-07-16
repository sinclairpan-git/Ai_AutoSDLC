# 任务分解：Frontend Artifact Path Dedupe Reduction

**编号**：`205-frontend-artifact-path-dedupe`\
**日期**：2026-07-15\
**来源**：`spec.md + plan.md`\
**父任务**：WI-196 `T63 / WP-03`

## Batch 1：formal、基线与对抗评审

### T11 创建 canonical WI 与隔离工作区

- **状态**：已完成
- **验收**：WI-205 四件套位于 canonical `specs/205-*`；branch/worktree 基于 exact
  `e4f395e3`；父项/manifest/sequence 已登记。

### T12 冻结 T61A/RC/CC/GAP 合同

- **状态**：已完成，待同哈希双审
- **依赖**：T11
- **验收**：Appendix A 复算 product modules=2602 raw/2275 non-empty、test files=2723/2317；
  12 defs/13 calls、AST 108 LOC、complexity/syntactic fan-out=36、internal fan-out=0、完整 digest 与
  fan-in distribution；14 dedupe tests=280/239；targeted=76、median=.73s/p95=.74s；CLI/Program=78；
  固定 13 产品文件 raw ledger、两行顺序断言、Golden/truth/CC/GAP/RC 均有精确口径；无占位。

### T14 刷新 root inventory truth expectation

- **状态**：已完成，待同哈希双审
- **依赖**：T12
- **验收**：WI-205 五件套使 inventory 1076→1081、close layer 204→205；只把
  `test_root_program_manifest_covers_specs_and_host_ingress_canonical_evidence` 的既有 expected tuple
  更新为 1081/1081/0/0 与 205/205；该 test 从两个 sequential exact RED 恢复 GREEN，无新
  test/function/file。

### T13 formal 双 Agent 对抗评审

- **状态**：待执行
- **依赖**：T14
- **验收**：Pascal/精简直接性与 Confucius/兼容证明性对同一
  `spec.md + plan.md + tasks.md` hash 都为 PASS；findings 全部处置；内容变化后重审。

## Batch 2：T61A characterization 与 RED

### T21 记录未改代码 baseline

- **状态**：待执行
- **依赖**：T13
- **验收**：绑定 revision、Python/OS/toolchain，12-module suite 五次采样、full baseline；
  Appendix A 冻结 product/test LOC、complexity、duplicate family、完整 digest、fan-in/out；
  `wi205-git-tree-v1` 在同一 shared basetemp、fresh index、`allowlist=[]` 下 baseline 两次稳定；
  审前本机 fixed-root probes 均为 463 entries（418 regular +45 symlinks）且各自两次 OID 相同；
  T61A 冻结本地 paired-run root/OID/count 与 attribute isolation；测试副作用从工作树恢复。

### T22 强化既有 test 并证明 mutation RED

- **状态**：待执行
- **依赖**：T21
- **验收**：在既有 materialize dedupe test function 内增加精确两行：构造
  `[Path("first"), Path("second"), Path("first")]` 并通过现有 module private binding 断言前两项；
  不新增 test function/file/fixture/helper。临时 `reverse(unique_output)` 后必须出现
  `[first, second]` vs `[second, first]` 的稳定 assertion failure；不是 reverse(input)、import 或
  fixture error。实现收敛后同一 binding 必须覆盖 canonical helper，不允许 local wrapper。

### T23 恢复 mutation 并复核 GREEN

- **状态**：待执行
- **依赖**：T22
- **验收**：只用 `apply_patch` 恢复临时产品 mutation；被强化 test 与 76-test targeted 重新通过；
  产品工作树等于基线，测试 diff 精确为 order `+2/0` 与已冻结的 root truth `+2/-2`；
  RED/GREEN 输出写入 execution log。

## Batch 3：最小产品减重

### T31 新增唯一 private helper

- **状态**：待执行
- **依赖**：T23
- **文件**：`src/ai_sdlc/generators/_artifact_paths.py`
- **验收**：保留 typed `Path` 合同并把反向 continue 等价简化为 8 LOC 正向 membership 算法；
  无 public export、选项、类型转换、路径规范化、读盘或错误包装；函数 <50 LOC、文件 <400 LOC。

### T32 删除 12 个本地 body 并复用 helper

- **状态**：待执行
- **依赖**：T31
- **文件**：spec §1 的 12 个 artifact module
- **验收**：各 module 只增加一条 import 并删除 local body；调用名不变；实现数 12→1，
  call sites=13；除冻结的 order `+2/0` 与 root truth `+2/-2` 外，无其他测试、payload 或代码变更。

### T33 复算 Reduction Contract

- **状态**：待执行
- **依赖**：T32
- **验收**：Appendix A 输出 defs 12→1、calls=13、AST 108→8、complexity/fan-out 36→3，
  baseline/candidate digest 分别为 `fc689b7a...be9b4`/`aec166ee...8c91`；candidate commit 的 raw ledger
  显示产品 additions≤23、deletions≥108、net≤-85，order test additions=2/deletions=0、
  inventory/close replacements additions=2/deletions=2，纳入 RC-06 的 product/test source
  additions≤27；formal/truth/continuity 文档不计入该代码预算；13 产品 changed-file set 精确、新增产品文件=1、
  无新 test function/file/harness/fixture/normalizer source、公共抽象=0。任一不满足即 RC-09 No-Go。

## Batch 4：T61B differential、回退与全量验收

### T41 运行 12 module targeted 与 CLI/Program slice

- **状态**：待执行
- **依赖**：T33
- **验收**：14 个既有 dedupe tests（一个强化两行）及 76-test artifact suite 通过；隔离 candidate
  的 12 个 expected-file-set tests 继续覆盖 94 paths，`wi205-git-tree-v1` 的同平台 candidate
  tree OID/entry count 与稳定 baseline 相同，allowlist 为空，system/global/worktree/info attributes
  均被 fail-closed 隔离；78 个 frontend CLI/Program
  tests 的 path/count/parsed payload/可见文本无未批准差异；不宣称 raw stdout/stderr equality。

### T42 执行 rollback rehearsal

- **状态**：待执行
- **依赖**：T41
- **验收**：在 disposable clone revert candidate implementation commit 后 targeted/Golden tree 恢复
  baseline；再恢复 candidate 后 targeted/Golden tree 重新 GREEN；生成
  `.ai-sdlc/work-items/205-frontend-artifact-path-dedupe/t61-differential-rollback-receipt.json`，一个
  generated 文件同时记录 GoldenSnapshot、DifferentialResult 与 rollback；主 worktree 不做
  destructive reset/checkout。

### T43 全量与治理验证

- **状态**：待执行
- **依赖**：T42
- **验收**：full pytest、Ruff、constraints、Program validate/truth、diff-check 全绿；目标 commit
  `repo_revision/generated_at/snapshot_hash` 落日志，snapshot fresh、state ready、exit 0、zero blocker；
  capability/blocking-ref exact set 与 inventory complete/unmapped=0/missing=0；GAP-09～11 blocker
  或 source debt 再现则 fail-closed/reopen；execution log 记录 structured receipt URI/SHA-256，工作树
  只含 changed-file allowlist；现有三平台 full pytest（包含顺序 test 与 76 artifact tests）通过，
  不要求 workflow 生成 paired-tree evidence。

## Batch 5：final review、PR、CI 与 mainline

### T51 final tree 双 Agent 复审

- **状态**：待执行
- **依赖**：T43
- **验收**：两个维度对同一 final tree/diff hash 均 PASS，无 Critical/Important/可操作 finding。

### T52 提交、推送、PR 与 Codex review heartbeat

- **状态**：待执行
- **依赖**：T51
- **验收**：逻辑提交清晰；branch pushed；ready PR 创建并请求 `@codex review`；每约五分钟
  监控 review/check；finding 修复后重跑相关门禁并重新 review。

### T53 merge 与 fresh-main acceptance

- **状态**：待执行
- **依赖**：T52
- **验收**：Codex 无可操作问题、required checks 全绿、PR merged；fresh main clone 重跑
  targeted/Golden tree/full/truth，fresh-main truth 同样满足 fresh/ready/exit 0/zero blocker/exact sets；
  WI-205/T63 关闭证据同步，但 WI-196 仍按剩余 WP 状态如实保持 active。

## 追踪矩阵

| 规格 | 任务 |
|---|---|
| FR-01～FR-04 | T21～T23、T31～T32、T41 |
| FR-05～FR-06 | T21～T23、T33、T41～T43 |
| FR-07 | T14、T31～T33、T43 |
| FR-08 | T13、T51 |
| FR-09 | T52～T53 |
| SC-01～SC-02 | T32～T33 |
| SC-03～SC-05 | T41～T43、T53 |
| SC-06 | T13、T51 |
| SC-07 | T53 |
| CC-03/05/06/07 | T21～T23、T41～T43 |
| RC-01～07/09/10 | T12、T14、T21～T23、T31～T43 |
