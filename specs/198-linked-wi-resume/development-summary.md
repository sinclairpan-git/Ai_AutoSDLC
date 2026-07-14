# Development Summary：WI-198 Linked Work Item Resume Working Set

**状态**：merged，mainline evidence passed
**父项**：WI-196 `GAP-08 / T52`
**设计哈希**：`8ac337e615eb0f1f6bc626515a9be72fec1acb379ab01994611be4cbe0cd5118`

## 当前结论

- 根因是 resume pack 已按 `linked_wi_id` 选择 runtime/summary/artifact，却仍按历史 `feature.spec_dir` 构建 filesystem working set，导致 active WI 与 spec/plan/tasks、branch 分裂；旧版生成但 fingerprint 仍 fresh 的错误 pack 也不会自愈。
- 修复只修改 `src/ai_sdlc/context/state.py`：linked WI 使用 `specs/<linked>`，缺失/部分文档 fail-closed；linked runtime branch 优先，无 runtime branch 为空；无 linked 严格保留既有 `feature.spec_dir` 与 feature branch。
- fresh legacy pack 通过同源 expected pack 比较 spec/plan/tasks/current_branch 后复用既有 stale rebuild；expected pack 至多构建一次。semantic-only 探测对 `YamlStoreError`、`UnicodeError`、`OSError` 保持旧成功合同，真正 missing/corrupt/stale rebuild 的既有错误行为不变。
- 产品 diff 为 `+19/-3`、净新增 16 LOC；三个既有测试文件合计 `+140/-1`。未新增产品/测试文件、公共抽象、依赖、配置或 schema。
- TDD 证据：最终 RED 为 `4 failed, 34 passed`；GREEN 后三个直接测试文件 `38 passed`，五个 focused 文件 `94 passed`；full suite `3156 passed, 3 skipped`，Ruff、constraints、diff check 均 PASS。
- root/scoped resume pack 字节相等，canonical/scoped handoff 字节相等；AFTER pack 的三件套均指向 WI-198，linked 无 runtime branch 为明确空值。
- RED reviewer、GREEN reviewer均给出 spec compliant/quality approved；兼容安全与精简效率 final branch Agent 对同一 HEAD 均给出 PASS，未发现可操作问题。
- mainline/发布回退必须 revert 整个 PR/版本；分支源码回退必须将 characterization tests 与对应 GREEN 成对回退，禁止只撤 runtime 留下必失败测试。

## Mainline closure

- PR `#122` 在当前 HEAD Codex review 无问题、22 项 required checks 全绿后 squash merge；merge commit 为 `68150d3f5ba128c0e4b44b11b13bc8ad60cc0d63`。
- Codex 曾发现 `development-summary.md` 已存在但 program truth snapshot 仍记为 `exists=false`；修复提交 `8150a1b7534a2b5aefd09dc9722d616f26769b1a` 同步 canonical truth 后，两名 Agent 对该 HEAD 均复审 PASS。
- 合并前 branch 与 `origin/main` tree hash 均为 `6acaf28f22c6c59c4e751b5900387fd4478e1389`；mainline-equivalent targeted 为 `94 passed in 34.44s`。
- mainline truth audit 的 snapshot 为 fresh，inventory 为 `1018/1051 mapped`、`33 unmapped`、`11 missing`；只保留已登记 GAP-09～GAP-11 debt，GAP-08/T52 已关闭。
