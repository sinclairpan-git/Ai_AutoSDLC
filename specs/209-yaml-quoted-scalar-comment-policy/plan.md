# 实施计划：YAML quoted-scalar comment-policy 精确识别

**编号**：`209-yaml-quoted-scalar-comment-policy` | **日期**：2026-07-17
**规格**：`specs/209-yaml-quoted-scalar-comment-policy/spec.md`
**风险**：L2；验证 blocker 的窄语法修复

## 1. 交付策略

先用 docs PR 冻结 false-positive 边界、预算和回退；formal 合并后创建独立 implementation 分支，按
RED→GREEN→全量→双审→PR→fresh-main 推进。任何内容变化都会使之前的双 PASS 失效。

## 2. 技术背景

- Python 3.11+；现有依赖 `pyyaml>=6.0`。
- 当前入口：`collect_comment_deletion_blockers()` → `_git_diff(--unified=0)` →
  `collect_removed_comment_findings()` → `_is_comment_line()`。
- 当前纯函数只知道 path 和 diff text，不知道 hunk old/new 行号对应的 YAML 语法位置。
- 基线全量证据继承 `main@85bdedac`：PR #143 fresh-main `3230 passed, 3 skipped`；PR #144
  10/10 checks 成功且 closure fresh-main governance 通过。

## 3. 设计冻结

### D1：保持零上下文 diff

继续使用 `git diff --unified=0 HEAD --`。解析 `@@ -old[,count] +new[,count] @@`，context 同时推进
两侧，removed 只推进 old，added 只推进 new；每个 hunk 重置起点。

### D2：独立 old/new path 与 source map

从 `---` / `+++` 分别解析 old/new path；覆盖 rename、`/dev/null`、traversal 与 Git C-quoted 空格/非
ASCII 路径。展示路径优先 new、删除时用 old；解码失败仍使用安全占位保留 finding。工作树 YAML
读取前逐组件 `lstat`，拒绝 symlink、Windows reparse/junction、特殊文件和 root 外解析结果；不跟随目标。
旧侧只用 `git show HEAD:<old>`。每路径每版本最多读取一次。

### D3：复用 PyYAML token span

扫描每个可用版本，只收集 style 为 `'` / `"` 且跨行的 `ScalarToken`。token mark 为 0-based；转换为
1-based 后，只把 `start_line < target_line <= end_line` 视为候选 quoted 内容。目标位于 closing line 时，
从当前 `end_mark.column` 后扫描，并跳过同一行后续 quoted token 的 column intervals；任一处于行首或前一
字符为空白的 `#` 都是真实 comment。flow sequence/mapping 中间 token 不能掩盖尾注释。

### D4：removed/added 对称过滤

removed 可确认 quoted 内容不进入 `removed_comments`；added 可确认 quoted 内容不进入 `added_comments`。
其余可信 comment 才进入既有 flush/数量配对；顺序和 blocker 文本完全沿用现有实现。

### D5：失败保守

失败按侧不对称保守：removed YAML 不可信时回落 `_is_comment_line()` 并报告；added 侧 path/source/
语法/行号任一不可信时，候选 `#` 不得作为 replacement。只有确认非 YAML 才保持旧行为。非法 hunk
清空两侧位置，不能沿用上一 hunk。

### D6：最小实现形态

允许 hunk regex、可选 source context 参数和最多 5 个 private helper；禁止新增模块、数据类、
公共 parser API 或对 `verify_constraints.py` 的条件分支。

### D7：唯一 formal review identity

formal review target 固定为父/子各 `spec.md + plan.md + tasks.md` 六文件，并唯一引用父计划 §9 的
per-file SHA row recipe。WI209 不定义第二套 hash 算法；任一六文件变化使双方 PASS 同时失效。

## 4. 文件边界

| 阶段 | 文件 | 允许变更 |
|---|---|---|
| formal | child 五件套、父 WI196 台账/计划/任务/日志/summary、manifest/project-state/root exact test、continuity | 文档真值与机械 inventory 值 |
| RED/GREEN | `src/ai_sdlc/core/comment_policy.py` | hunk 行号、source 读取、quoted token span、对称过滤 |
| RED/GREEN | `tests/unit/test_comment_policy.py` | 参数化 token/path/hunk 矩阵和真实 Git diff 回归 |
| CLI 回归 | `tests/integration/test_cli_verify_constraints.py` | quoted exit 0、真实 comment/added-side exit 1 与完整 blocker 文本 |
| 禁止 | 其他 `src/`、其他 tests、CLI/rules/workflows | 必须另立项 |

## 5. 测试矩阵

| 组 | 场景 | 核心断言 |
|---|---|---|
| RED-1 | `.yaml/.yml` single + double multiline removed continuation | 基线有 finding；实现后为空 |
| SAFE-1 | 真实 YAML comment、Python/Markdown 同形、literal/folded/plain | finding 保留 |
| SAFE-2 | removed 真实 comment + added quoted `#` 内容 | 仍有 1 个真实 finding |
| EDGE-1 | closing line 无尾注释/直接尾注释/flow sequence 或 mapping 中间 token 后尾注释 | token intervals 后 comment 安全 |
| EDGE-2 | 多 hunk、old/new 不同行号、省略 count、zero count、suffix、no-newline marker | 两侧位置不串线 |
| PATH-1 | rename/delete/create、空格/非 ASCII Git quoted path、traversal | old/new source 与展示路径正确 |
| PATH-2 | `old.yaml→new.py`、`old.py→new.yaml`、`.yaml↔.yml`、大小写扩展名 | 严格分侧语义 |
| READ-1 | final/parent symlink、特殊文件、root 外目标 | 不读取；added untrusted |
| READ-2 | Windows reparse/junction（真实可建则 real，否则模拟 file attributes） | no-follow；跨平台确定 |
| FAIL-1 | malformed YAML、HEAD blob/working file 缺失、scanner exception | removed 报告；added 不作 replacement |
| FAIL-2 | 非法 hunk/path header | 不复用旧状态、不丢 finding |
| REG-1 | 现有 replacement count、execution-log reason | 既有行为/文本不变 |
| INT-1 | 临时 Git repo + `collect_comment_deletion_blockers` | 真实 `git diff` 路径通过 |
| CLI-1 | Typer `verify constraints` 真实入口 | quoted exit 0；真实/added-side exit 1，完整文本不变 |

测试优先参数化复用现有 `_init_git_repo()`，不为每个形态复制 repository fixture。

## 6. 阶段计划

### Phase 0：formal truth

1. 初始化 WI209 canonical 五件套，登记父 GAP-14/T57 和 manifest。
2. 冻结 observed/expected、矩阵、NC/CC、预算、停止/回退。
3. 运行双对抗评审：Pascal 负责直接性/预算/防膨胀，Confucius 负责安全/兼容/fail-closed。
4. 两者对同一 combined hash PASS 后才提交 formal PR；Codex/current-head/checks/merge 完成后进入代码。

### Phase 1：TDD RED

1. 只修改两个批准测试文件，增加最小 single/double 参数化 RED、added-side safety guard 与 CLI exit/text。
2. 记录 RED 的 node id、退出码和失败断言；确认失败来自现有前缀判断而非 fixture 错误。
3. RED commit 与 GREEN 分开，便于回退审计。

### Phase 2：最小 GREEN

1. 实现 D1～D5；不提前抽象。
2. 跑 RED nodes 和 `tests/unit/test_comment_policy.py`。
3. 复算 raw/Ruff-normalized 产品/测试 LOC；超预算即停止并缩小。

### Phase 3：回归与治理

```powershell
uv run pytest tests/unit/test_comment_policy.py -q
uv run pytest tests/integration/test_cli_verify_constraints.py -q
uv run pytest -q
uv run ruff check src/ai_sdlc/core/comment_policy.py tests/unit/test_comment_policy.py tests/integration/test_cli_verify_constraints.py
uv run ruff format --check src/ai_sdlc/core/comment_policy.py tests/unit/test_comment_policy.py tests/integration/test_cli_verify_constraints.py
uv run ai-sdlc verify constraints
uv run ai-sdlc program validate
uv run ai-sdlc program truth audit
uv run pytest tests/integration/test_repo_program_manifest.py -q
git diff --check
```

full 前后记录 HEAD/tree、tracked resume、root/scoped handoff、status；验证命令不得污染产品或治理状态。

### Phase 4：回退、双审、PR 与 fresh-main

1. 在 disposable worktree 逐提交 revert 到 formal merge tree并按原顺序 reapply，要求两端 tree 精确一致。
2. 冻结 final HEAD/tree、binary diff、name-status 和 formal combined hash。
3. 两个 reviewer 均 PASS 后 push/PR/request Codex，约五分钟 heartbeat 直到 review/checks 全绿。
4. 合并后 fresh detached main 复跑 focused/full/Ruff/constraints/truth/clean guard；只在此后关闭 GAP-14/T57。

## 7. 预算与直接性门禁

- 产品净新增 ≤130 行；两个测试文件合计净新增 ≤200 行；raw 和 Ruff-normalized 都必须满足。
- 产品/测试新增文件 0；公共抽象 0；private helper ≤5，单函数 ≤50 行。
- raw 以 formal merge base 的 `256/134/1799` 为基线；normalized 在 disposable copies 上对 base/candidate
  同一组三文件执行 Ruff format 后计数，不得格式化 tracked target 来制造减行。
- 不允许把 PyYAML token 转换成第二套 AST，不允许全文件 diff，不允许 cache class 或策略层。
- 若最小实现超过预算，优先减少重复测试/合并 helper，不删除安全场景；仍超限则回到 formal。

## 8. 回退与恢复

- 代码回退：revert implementation commit/PR；owner 为 AI-SDLC framework maintainer。
- 数据恢复：无；本项不写 artifact/schema/state。
- formal 回退：revert WI209 docs PR，会移除 WI209 mapping 并把 parent T57 恢复为 queued。
- 若实现 PR 合并但 fresh-main 失败，GAP-14 保持开放，在同一 implementation 分支做聚焦 repair PR，
  不启动新的减重候选。
