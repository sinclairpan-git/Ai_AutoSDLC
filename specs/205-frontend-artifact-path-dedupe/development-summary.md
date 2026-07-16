# Development Summary：WI-205 Frontend Artifact Path Dedupe

**状态**：formal Round 10 同哈希双 PASS；本地实现与 T61 验收完成，final 双审 / PR 待完成\
**父项**：WI-196 `T63 / WP-03`

## 当前结论

- 基线存在 12 份完全同形 `_dedupe_paths`，共 108 产品 LOC、13 个现有调用点。
- 12 个产品 module 全量为 2602 raw/2275 non-empty LOC；12 个 artifact test file 为
  2723 raw/2317 non-empty LOC；direct call fan-in 分布为 contract=2、其余 modules=1。
- 已实现单 private helper，并将反向 continue 等价简化为正向 membership：AST 108→8、
  complexity/fan-out 36→3；固定 13 个产品文件 raw additions≤23、deletions≥108、net≤-85。
- 14 个既有 dedupe tests 精确为 280 raw/239 non-empty LOC；只在其中一个既有 function 增加两行
  direct-binding 顺序断言，不新增 test function/file/fixture/harness。WI-205 五件套另要求 root
  inventory/close 两行 expectation replacements；总 source raw additions=23+2+2≤27，等于 RC-06 cap。
- 76-test targeted 五次 baseline median=0.73s/p95=0.74s；最终证据方案为零自写 source 的
  `wi205-git-tree-v1`。两个独立 fixed-root 本机探针均为 463 entries（418 regular +45 symlinks），
  各自在自己的 absolute basetemp 内两次 OID 相同，allowlist 为空；不同 root 不比 OID，各平台只
  跑现有 full pytest。本地 paired gate 进一步隔离 system/global/worktree/info attributes，避免 Git
  clean filter 把 raw 差异规范化。
- frontend CLI/Program candidate 为 broad 67 + rules/solution-confirm 11，共 78 passed；命令安装的
  managed `.cursor` rule 已用 `apply_patch` 恢复为 HEAD，最终无副作用 diff。
- candidate commit `7b96f969` 的产品 additions=23、deletions=132、net=-109；order test=`+2/0`，
  连同 formal root truth=`+2/-2` 后 RC-06 additions 精确为 27。candidate AST 只剩 1 definition、
  13 calls、12 imports、8 LOC、complexity/fan-out=3，body digest 精确为 `aec166ee...8c91`。
- baseline/candidate full suite 分别为 `3220 passed, 3 skipped in 534.72s` 与
  `3220 passed, 3 skipped in 512.20s`。冻结的 PowerShell 7.5.8 runbook 已实跑：baseline×2、
  final candidate、rollback、restored candidate 五段均为 76 passed，且同根 raw Git tree 都为
  `6e1803c9...19a1`/463；allowlist 为空。结构化 receipt SHA-256 为 `ca6a9387...1f4e`。
- Round 1～3 findings 已处置；Round 4 精简侧 PASS，兼容侧发现 Git attributes 可能掩盖 raw 差异，
  以及三平台 paired-tree 与既有 workflow 不可执行。formal 已增加 attributes fail-closed isolation，
  并把 paired tree 限定为本地 T61A/B、CC-07 复用现有三平台 full pytest。Round 5 双方共同发现
  unset `core.symlinks` 与 PowerShell native fail-fast 版本缺口，已改为 default-aware 查询并冻结
  PowerShell≥7.3。Round 8 又以反斜杠 hard break 同时保持 Markdown 分行与 whitespace gate，并曾获
  同哈希双 PASS；PR #133 的六个跨平台 full-suite jobs 随后由同一个版本敏感 root inventory assertion
  暴露旧期望仍停留在 1076/204。修复成本按 additions=2/deletions=2 纳入 RC-06 后，旧 9 LOC helper 方案总新增
  会达到 28>27，已按 No-Go 淘汰；Round 9 改用行为等价的 8 LOC 正向 membership helper，使代码预算
  回到 23+2+2=27。Round 9 两位 Agent 分别发现旧“两行 test diff”残留口径、“逐行等价”误述与
  spec digest serializer 不可复现；Round 10 已定向修复。Pascal/Confucius 已对同一最终 tuple 完整复审、
  起止复算一致并双 PASS；无可操作 finding。

## 未完成边界

- formal PR #133 已在 `a76ef8b1` 合并。T61A mutation RED/GREEN、候选产品实现、T61B
  differential、PowerShell paired-tree、rollback、full suite、Ruff 与 constraints 已完成。最终
  evidence revision 必须由 fresh/ready Program Truth 覆盖后再送 final tree 双 Agent 同目标评审；
  交付边界只剩双 PASS、implementation PR/Codex review、跨平台 CI、merge 与 fresh-main acceptance。
- 本 summary 不宣称 T63、WP-03 或 WI-196 已完成；只有 WI-205 合并并通过 fresh-main acceptance
  后，才能关闭本次重复族。
