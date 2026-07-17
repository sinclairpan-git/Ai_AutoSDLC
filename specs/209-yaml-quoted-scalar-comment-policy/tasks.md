# 任务分解：YAML quoted-scalar comment-policy 精确识别

**编号**：`209-yaml-quoted-scalar-comment-policy` | **父任务**：GAP-14 / T57
**规则**：每批单独提交；formal、implementation、acceptance 使用独立分支/PR；内容变化使双 PASS 失效。

## Batch 1：formal truth

### T11 初始化与基线复现（completed）

- **依赖**：WI208 closure PR #144 已合并为 `85bdedac`。
- **文件**：child 五件套、project-state、program manifest、root exact test。
- **验收**：WI209 路径唯一；baseline revision/LOC、single/double 当前 1 finding 和 PyYAML token span 有可执行证据。
- **验证**：只读 Python spike、`git diff --check`、路径白名单。

### T12 冻结 NC/CC、设计和对抗评审（completed）

- **依赖**：T11。
- **验收**：FR/SC/矩阵、old/new path/line、分侧 fail-closed、预算、停止/回退均闭合；Pascal 与 Confucius 按父计划 §9 唯一 recipe，对父/子各 `spec+plan+tasks` 六文件同一 combined hash 均 PASS。
- **停止**：任一 reviewer 有 finding 时修正文档、重算哈希并重开两位评审，直到一致 PASS。

### T13 formal 治理、PR 与合并（in progress）

- **依赖**：T12 双 PASS。
- **验收**：父 GAP-14/T57 标为 formal ready；manifest truth `ready/fresh`，root exact、constraints、validate、diff-check 通过；formal PR current-head Codex clean 且 checks 全绿后合并。
- **非目标**：`src/ai_sdlc/` 零差异；除 root exact inventory/close 数值外测试零差异。

## Batch 2：TDD 与最小实现

### T21 提交真实 RED characterization（queued）

- **依赖**：T13 formal merge；从新 main 创建独立 implementation 分支。
- **文件**：`tests/unit/test_comment_policy.py`、`tests/integration/test_cli_verify_constraints.py`。
- **验收**：single/double removed continuation 至少一个参数化 node 在基线失败；added quoted/不可确认 YAML 内容不能替代真实 comment；CLI exit/text 已冻结。
- **验证**：记录精确 pytest node、失败断言和退出码；RED 只含测试。

### T22 实现 path/syntax-aware GREEN（queued）

- **依赖**：T21。
- **文件**：`src/ai_sdlc/core/comment_policy.py`。
- **验收**：保留 `--unified=0`；old/new path/行号、HEAD/worktree sources、PyYAML quoted token span/end column 和分侧保守过滤生效。
- **验证**：RED nodes GREEN；`tests/unit/test_comment_policy.py` 全绿。

### T23 安全矩阵与预算（queued）

- **依赖**：T22。
- **验收**：真实 YAML/Python/Markdown comments、plain/literal/folded、malformed、mixed-extension rename/quoted path、no-follow symlink/reparse/containment、标准 hunk 边界、closing flow suffix/escape、replacement reason 与 CLI exit/text 全部通过；以 `256/134/1799` 为 raw 基线，产品 ≤130、两测试合计 ≤200，三文件 Ruff-normalized 一致满足。
- **停止**：新增模块/公共抽象、预算超限或 blocker 文本变化即回到 T22/设计。

## Batch 3：终态证明

### T31 全量与治理门禁（queued）

- **依赖**：T23。
- **验收**：comment-policy、verify-constraints、full、Ruff、constraints、validate、truth、manifest、diff-check 全绿；full 前后 HEAD/tree、resume/handoff/status 无漂移。

### T32 回退演练和双对抗终审（queued）

- **依赖**：T31。
- **验收**：逐提交 revert 精确回到 formal merge tree、reapply 精确回到 candidate tree；Pascal/Confucius 对同一 final identity 均 PASS，无未处置 finding。

## Batch 4：交付与关闭

### T41 implementation PR（queued）

- **依赖**：T32。
- **验收**：push/PR/@codex review/heartbeat；Codex 对 current HEAD clean、所有 required checks success 后 merge。

### T42 fresh-main acceptance（queued）

- **依赖**：T41 merge。
- **验收**：fresh detached `origin/main` 复跑 focused/full/Ruff/constraints/truth/clean guard；父 GAP-14/T57 只在此后关闭，回退 implementation PR 会重开。

### T43 恢复下一原子减重选择（queued）

- **依赖**：T42 closure PR merge。
- **验收**：只从 T63/T65/WP-06/WP-07 中按依赖/收益选择一个独立候选；不得把 WI209 计入 RC-08 减重。

## 追踪矩阵

| 合同 | 任务 |
|---|---|
| FR-209-01～08 | T21～T23 |
| FR-209-09～11 | T23、T31 |
| FR-209-12 | T13、T21、T41、T42 |
| NC-01～03 | T11、T12、T23 |
| NC-04～06 | T21、T31、T32、T42 |
| SC-209-01～04 | T23、T31 |
| SC-209-05～06 | T12、T32、T41、T42 |
