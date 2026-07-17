# WI-208 Development Summary

**状态**：Round 7 exact target 已冻结；fresh 双审修订中
**父项**：WI-196 GAP-13/T56

WI208 修复 relocated/detached worktree 中 resume-pack 重建的绝对路径和 continuity 字段丢失。根因已
收敛到共同 builder：filesystem fallback 写当前 worktree 绝对路径；active linked WI 没有 optional
runtime/working-set/latest-summary 时，expected pack 也没有 branch/active/context。

冻结方案不信任旧 pack、不改 schema：checkpoint 锚定 active WI/fingerprint/docs baseline/execute
fallback，active-WI runtime 继续优先提供 stage/batch/task；WI-182 matching canonical handoff 为所有 active
WI 补 context，只以非 `HEAD`/`none`/历史 fallback 的 eligible Branch 补 linked branch；active files 只来自
working-set 或 `STAGE_FILES`。`none` sentinel 与 summary 拼接沿用现有 wire grammar；所有 repo-internal path
统一 portable relative。status/recover/handoff 继续复用一个 builder 和现有 crash-convergent staged
root/scoped write。handoff reader 保留 WI-198 的 semantic-only 三态边界；两份 pack 同时比较 model 与 raw
bytes，model-equal/bytes-different 也必须收敛。该 byte-only 首次 repair 只复用既有 event 序列与 rebuild
timestamp；模型语义/checkpoint/event 文本不变，第二次 load 无写入/无 event。

WI-207 GAP-12 已由 PR #139 产品修复、PR #141 test-isolation repair及 fresh-main clean acceptance 关闭。
WI-209 GAP-14 仍 queued。本项是可靠性缺陷，不计减重收益；formal 与 final implementation 都必须取得
Pascal/精简直接性和 Confucius/兼容安全性对同一精确目标的双 PASS。

Formal Round 5 exact combined
`4edae999905c32ad4d0e5caf6a04c5ad65aba922d9ecdf46d608211e592f68d1` 已由 Pascal 与 Confucius 分别
从零复算 start/end 并双 PASS；两者均未发现 actionable finding，target drift=`NO`。首次 staged
`git diff --cached --check` 随后发现 untracked child 新文件的 Markdown 行尾空格；修复使 child 三件套
变化，Round 5 PASS 按合同失效。Round 6 combined
`aab82d2601bbeb097331865e022b6c2458133bfae62f3afa9c5fc4a1496a18aa` 曾由 Pascal/Confucius 双 PASS，
但 Codex 随后发现 T21～T24 仍保留过期等待/pending 状态；两位本地 reviewer 均确认 finding actionable，
因此 Round 6 已退役。

Round 7 只将上述四个状态行改为 WI207 同型的 latest-execution-log receipt 模式；T25 仍 `pending`、T31
仍 `blocked by T25`。当前 canonical combined=
`a91b6d3541e755e604ec7ee376bd0db5b8a037cc5e2c71e94e800ab768860b39`，其余五个 formal 文件未变。

Round 7 target 冻结后 terminal pre-pass 已取得 truth sync/audit=`ready/fresh`、inventory `1096/1096`、
unmapped/missing=`0/0`、constraints no BLOCKER、program validate PASS、manifest exact `1 passed`。本摘要
对齐后仍须 final truth/gates 与同一 immutable HEAD 双审；最终回执放在 commit/PR 外部证据。
