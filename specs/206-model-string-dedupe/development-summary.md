# WI-206 Development Summary

**状态**：`completed_reduction`；PR #137 已合并并通过 fresh-main acceptance

WI-206 是 WI-196 `T63 / WP-03 / GAP-05` 的第二个原子重复族候选。初始 formal Round 1 补发现
`state.py::_dedupe_string_items` 属于同一顶层算法族，并计划把18个models helper收敛到一个 private
helper；当时预测产品 +≤33/-≥216/net≤-183。该组数字仅是 amendment 前的历史预算，已被实现探针
证明少算 4 条 Ruff 分隔空行；当前唯一有效门禁是下文的 +≤37/-≥216/net≤-179、source≤43≤54。

当前交付只冻结范围、兼容合同、Reduction Contract、T61、停止/回退和双 Agent 评审规则。Round 1
为双FAIL，已修订测试映射、event corpus、FunctionDef/inspect gate与tree-OID rollback；Round 2 的
精简评审PASS、兼容评审发现两个次要问题，已补齐有限 introspection allowlist 和五件套一致性；
Round 3 又发现实施顺序引用旧轮次及“100 个 validator 调用”的事实误称，已改为与轮次解耦的
当前 target 门禁和“100 个现有调用表达式”。Round 4 在同一 exact hashes 上取得 Pascal/精简效率与
Confucius/兼容安全共同 `PASS`，无可操作 finding。它不表示 helper 已创建、18 个 legacy body 已删除、测试已完成、
工作项已关闭或版本已发布。只有 formal receipt 合入 main 后，后续独立 implementation branch 才能进入
T61A/TDD。

Formal 本地门禁已通过：19-file `281 passed, 2 skipped`、root truth `1 passed`、Program Truth
ready/fresh 1086/1086、validate PASS、constraints 无 BLOCKER。暂存检查随后发现脚手架 Markdown 行尾
双空格会使 cached diff-check 失败；纯格式清理后的 Round 5 已在同一 hashes 上取得双 Agent `PASS`，
working/cached diff-check 均通过，当前进入 formal PR mainline receipt。

Formal PR #135 合并后的 implementation 探针发现旧预算少算 4 条 Ruff `I001` 必需 import-block 分隔
空行。算法与范围不变，预算保守修订为 product +≤37/-≥216/net≤-179、source≤43≤54；implementation
已暂停。amendment Round 1 双方一致指出必须显式禁止 late import/noqa 等规避手段；规则已补为标准
顶层 first-party import、无 lint suppression。Round 2 已在 combined
`d0e29ec47fbf3582c275e6a0ca6f7ee94acb2ac3efc5669291d70ac619930566` 取得双 Agent `PASS`，进入
最终本地门禁与 mainline PR。

Amendment PR #136 已合并，implementation commit `6c52f03` 已把18个 helper 收敛为一个私有叶子
helper。实际 product `+37/-246/net -209`、test +2；probe/corpus、Ruff、19-file、reverse mutation、
exact rollback/reapply 与 candidate full `3220 passed, 3 skipped` 全绿。唯一 receipt SHA-256 为
`bb654c134fb4460d163f771b7d36da1e58dc898c5631032dcaa206d2e0d7abd8`；待 final governance 与双 Agent
final tree review 后进入 implementation PR。

T43 final governance 已完成：root Program Truth `1 passed`、Ruff、diff-check、validate、constraints
均通过，truth 为 ready/fresh、inventory 1086/1086。治理命令误刷的 Cursor rule 已精确恢复，
resume-pack 继续使用 repo-relative path；精确 snapshot/hash 与可变 signal counts 只以最终
`program-manifest.yaml` 为准。

T51 Round 1 中，Pascal 与 Confucius 一致 `FAIL` 于 authoring 证据自引用：把 pre-final snapshot/hash
写回 truth 输入后，下一次 sync 必然产生不同当前值。产品代码、预算、测试、corpus 与 rollback 均无
finding。现已删除当前精确值的重复声明，并规定 manifest 为唯一真值；终态 sync 后重新冻结 Round 2。

Round 2 中 Confucius `PASS`，Pascal `FAIL` 于 stale continuity next step：handoff/resume-pack 在终态
sync 已完成后仍要求恢复者再次 sync。现已改为稳定门禁：当前冻结目标仅做同哈希双审，双 PASS 后
不改树直接 push/PR，只有 FAIL 才修订、sync、refreeze。产品与所有证明证据仍无变化，进入 Round 3。

Round 3 terminal target 在 HEAD `5046f62597` / tree `35fa6f37ad4` 上取得 Pascal 与 Confucius 同哈希
双 PASS。PR #137 经 Codex review 和21项 required checks 后 merge 为 `506e950dee`；fresh-main 19-file、
结构/binding、Ruff、root truth 与 full `3220 passed, 3 skipped` 全绿，worktree clean。

最终实际 product `+37/-246/net -209`、test +2，18个 helper→1、calls=100、complexity72→4；receipt
SHA-256 保持 `bb654c134fb4460d163f771b7d36da1e58dc898c5631032dcaa206d2e0d7abd8`。
WI206 只关闭一个 T63 family。WI-205 已完成 artifact path family；WI-202、WI-204 保持 RC-09 No-Go；
GAP-05、WI-196 与 RC-08 在其余原子项完成前保持 open。
