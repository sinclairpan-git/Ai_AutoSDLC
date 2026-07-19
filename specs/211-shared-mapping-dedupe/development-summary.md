# 开发摘要：共享 Mapping 去重重复族减重

**功能编号**：`211-shared-mapping-dedupe`
**状态**：completed_reduction；closure PR 待交付

## 交付结果

- Formal PR #151 合并为 `25de0823b5412affa9a2b165b74dc0e4e7335157`；consumer 证据口径修订
  PR #152 合并为 `96908f2c207dd8e03411d8acd489b2101a5787cf`。
- Implementation PR #153 合并为 `cd64d8aad415853102cf3c8dc647af34759ad197`；Codex current-head
  review 两次均未发现 major issue，22/22 checks success。
- 10 个 exact private mapping-dedupe body 收敛为 `utils/helpers.py` 中 1 个共享实现和 10 个模块局部
  alias；23 个调用表达式不变。产品 raw `+25/-147/net -122`，non-empty `+23/-127/net -104`。
- 未新增产品/测试文件、公共导出、wrapper、配置或 suppression；唯一 identity characterization 在既有
  测试文件增加 4 个 non-empty lines。

## 等价与回退证据

- Python 3.11 的 4-case JSONL 为 4 rows / 502 bytes，SHA-256=
  `8c6d3e21ef597673c767e39a3919864242daed6014d13b1400a95eafabdb54e0`；baseline、candidate、revert、
  reapply 逐字节相等。Python 3.12 同解释器 AST payload 也相等。
- direct baseline/candidate 为 103/104，impact 为 1162/1163；72 个 cold imports 无失败或输出。
- rollback tree 精确回到 `0fca3830e7b3faa5773e9e8b677cdb4d62d4eadd`，reapply tree 精确回到
  `cbacdd4d271327b06ff28d04a1ee03e342b91a9f`。唯一结构化 receipt 为
  `.ai-sdlc/work-items/211-shared-mapping-dedupe/t61-differential-rollback-receipt.json`。
- Pascal 与 Confucius 对最终 implementation evidence head `fbfb07e7` 均 PASS、findings=none。

## Fresh-main acceptance

在 detached `main@cd64d8aa`、Python 3.11.15 上，4-case/identity 结构通过，direct
`104 passed in 1.13s`、impact `1163 passed in 99.78s`、full
`3277 passed, 3 skipped in 728.11s`；Ruff、constraints、program validate、truth `ready/fresh`、
manifest exact、reviewed blob/ledger 与 clean-state 均通过。

本项以 `completed_reduction` 关闭一个 T63/WP-03 family。它不关闭 GAP-05、WI-196、RC-08 或版本
发布，也不恢复无 sponsor 的 T62A；回退 PR #153 会重开本 family。
