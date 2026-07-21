# 开发摘要：ProgramService artifact loader 精确重复族减重

**状态**：formal authoring；implementation 未授权。
**基线**：fresh-main `b4d2ce5a5bc27b72549dcdf394f277cfbd6a124d`。

## 已确认

- 13 个 private frontend YAML loader 构成403 physical / branch39 的精确重复族。
- 12 个普通 loader 各一个内部 caller且无代码/测试 consumer；cleanup loader 有六个 caller和唯一额外的
  persisted warning normalization。
- Clean isolated spike 只改 product/test 两文件：product `+48/-406`、proof `+48`、terminal=`44/4`；
  16个新增proof与422个ProgramService unit全绿。
- RC-06含最多2行机械truth为98/101；product净删358。第一棵 formatter-polluted spike已排除，不进入账本。
- Pascal/LEAN 与 Confucius/SAFETY Round 4 均对同一 clean evidence
  `APPROVE A/findings=0`。

## 冻结方案

- 一个 `_load_frontend_artifact_payload(path, *, artifact_label)` 私有 helper。
- 12个ordinary caller显式传exact label并删除其单调用wrapper。
- 保留project-cleanup wrapper与六个caller，valid mapping时继续规范化warnings。
- 不新增模块、public abstraction、依赖、registry、reflection、DSL、selector或第二重复族。

## 状态边界

- 本 formal branch 不含 `src/**` 或产品测试逻辑；formal fresh-main 通过前不得创建 implementation branch。
- 本项属于 WI196/WP-03/T63/GAP-05；只关闭一个 family，不关闭 GAP-03/T66、GAP-05、WI196、RC-08或release。
- 任一语义差异、预算超限、formatter churn、回退失败或双review未统一时，implementation保持NO-GO并保留
  legacy。

## 下一硬门

1. 完成 parent/manifest/truth/handoff formal scope并提交clean identity。
2. LEAN/SAFETY 对同一 HEAD/tree/formal-six PASS0/findings=0。
3. Formal required checks、merge与detached fresh-main验收通过。
4. 从新的fresh-main创建独立implementation worktree，按T61A RED→GREEN执行。
