---
related_plan: "specs/196-ai-sdlc-lean-code-self-reduction-governance/plan.md"
related_doc:
  - "specs/196-ai-sdlc-lean-code-self-reduction-governance/spec.md"
---
# 任务分解：Adapter Mutation 与 Workitem Preflight 顺序修复

**编号**：`197-adapter-preflight-order` | **父项**：WI-196 `GAP-07 / T51`

## Batch 1：设计与 admission

### T11 冻结正式合同

- [x] 创建 canonical 四件套并登记 WI-197。
- [x] 冻结 revision、observed/expected、NC-01～NC-06、受影响 CC、预算和回退。
- [x] 落盘 GAP-10 fail-closed impact analysis。
- [x] 记录未改代码 focused baseline：`9 passed`。
- [x] 记录未改代码 full baseline：`3145 passed, 3 skipped`。

### T12 同哈希双 Agent 设计评审

- [x] 计算 `spec.md + plan.md + tasks.md` 组合 SHA-256。
- [x] 兼容安全 Agent 对该哈希明确 PASS。
- [x] 精简效率 Agent 对同一哈希明确 PASS。
- [x] 所有成立 findings 已修订；目标变化后旧 PASS 失效并重跑。

## Batch 2：TDD 实现

### T21 编写 RED characterization

- [x] 扩展 `tests/integration/test_cli_workitem_init.py` 的 root/group/init hook 隔离范围。
- [x] 新增 `adapter_before_clean_tree_preflight`，并增强脏树→干净重试 proof 场景。
- [x] 增强既有 duplicate-init 用例，证明第二次调用不消费 adapter 且不重建 proof。
- [x] 新增缺失 `--title` 零 adapter 场景与非 `init` handler 前一次场景。
- [x] 运行测试并确认因 self-dirty 或无效调用先执行 adapter 而 RED，不接受 fixture/patch 错误。
- [x] 把 RED 命令与关键输出写入 execution log。

### T22 实现最小 GREEN

- [x] `src/ai_sdlc/cli/main.py` 把 `workitem` 组委托给子应用，不读取 `sys.argv`。
- [x] `workitem_app` callback 对非 `init` 在 handler 前执行 hook；`init` 在 preflight 成功后执行。
- [x] `WorkitemScaffolder.preview_work_item_id` 用私有 canonical 文件名清单拒绝重复目标，`scaffold` 复用同一清单，不复制 CLI 校验。
- [x] 合法路径 adapter 恰好一次；脏树/无效 `init` 为零次，干净重试正常持久化 proof。
- [x] 不修改其他顶层 command、proof 校验/schema、输出或退出码。
- [x] 单测试与三个 focused 文件全部 GREEN。

### T23 预算和兼容复核

- [x] 产品新增 LOC ≤25，测试新增 LOC ≤80。
- [x] 新增产品文件=0、公共抽象=0、依赖=0。
- [x] GAP-10 proof carrier、digest/path 校验和 release blocker 无 diff。
- [x] CC-01/02/05/06/07 证据齐全。

## Batch 3：验证与交付

### T31 完整验证

- [x] `uv run pytest tests/integration/test_cli_workitem_init.py tests/unit/test_cli_hooks.py tests/unit/test_workitem_scaffold.py -q`。
- [x] `uv run pytest -q`。
- [x] `uv run ruff check src tests`。
- [x] `uv run ai-sdlc verify constraints`。
- [x] `git diff --check`。
- [x] 测试副作用未混入提交。

### T32 独立代码评审

- [x] 实现者自审完成并提交一个逻辑 commit。
- [x] task reviewer 给出 spec compliant + task quality approved。
- [x] 完整 branch reviewer 给出 ready to merge。
- [x] Critical/Important findings 全部修复并复审通过。

### T33 PR、mainline 与关闭

- [x] 推送分支并创建 PR。
- [ ] 请求 Codex review，并每约五分钟监控 review/checks。
- [ ] review 无可操作问题且 required checks 全绿后合并 main。
- [ ] main 上复核 targeted tests、truth snapshot fresh 与 GAP-07 关闭证据。
- [ ] 更新 WI-196 Gap Evidence Index/handoff，T51 标记关闭。

## 追踪矩阵

| 合同 | 任务 |
|---|---|
| GAP-07 / T51 | T11～T33 |
| NC-01～NC-03 | T11、T23 |
| NC-04 | T21、T22、T31 |
| NC-05～NC-06 | T11、T23、T33 |
| CC-01/02/05/06/07 | T21～T23、T31 |
| FR-197-01～04 | T21、T22 |
| FR-197-05～08 | T23、T31～T33 |
| SC-197-01～04 | T21～T23 |
| SC-197-05～07 | T12、T31～T33 |
