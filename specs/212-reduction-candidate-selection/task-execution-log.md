# 任务执行日志：AI-SDLC 精益减重候选选择

**功能编号**：`212-reduction-candidate-selection`  
**创建日期**：2026-07-19  
**当前状态**：候选扫描与 formal 编制中；产品实现未授权

## 1. 固定边界

- 本 WI 只允许 formal、父路线窄修、truth、continuity 与 project-state。
- 任一 `src/tests/workflow/provider/runtime rule` 变化均为 blocker。
- 所有历史 candidate/claim 只作证据，不得恢复。
- Formal 三文件变化使两个对抗 Agent 的既有 PASS 同时失效。
- 每批完成后先验证、再更新本日志、再提交；不得预写未来提交哈希。

## 2. Batch 2026-07-19-001：fresh-main 身份与路线审计

### 2.1 身份

- base/head：`origin/main@32742a25ef0c8d0f5a5480e0dcc9fcb105e2c45b`
- tree：`c8b475b6ffddc2700835d191cb3d19817756450d`
- Python：3.11.15
- worktree：`.worktrees/212-reduction-candidate-selection`
- formal branch：`feature/212-reduction-candidate-selection-docs`
- PowerShell host 继续命中既知 .NET regex assembly 问题；本地使用仓库允许的 Python 3.11/zsh fallback，CI 仍要求 Windows pwsh/cmd。

### 2.2 主线事实

- `src/ai_sdlc/**/*.py`：217 files / 107,321 physical LOC。
- `program_service.py`：17,474；`program_cmd.py`：7,057。
- RC-08 目标上限 96,733；剩余净删下限 10,588。
- PR #155 merge=`32742a25...`；merge tree 与双审 tree 均为 `c8b475b6...`。
- truth：`ready/fresh`、1111/1111、missing/unmapped=0/0、close=211/211。
- release 仍为 v0.9.6；RC-08 前禁止新版本。

### 2.3 执行命令与结果

```text
git fetch origin main
git rev-parse origin/main^{commit} origin/main^{tree}
rg --files src/ai_sdlc -g '*.py' | xargs wc -l
wc -l src/ai_sdlc/core/program_service.py src/ai_sdlc/cli/program_cmd.py
ai-sdlc verify constraints
ai-sdlc program validate
ai-sdlc program truth audit
pytest tests/integration/test_repo_program_manifest.py -q
```

结果：constraints no BLOCKERs；validate PASS；truth ready/fresh；manifest exact `1 passed`；fresh-main clean。

## 3. Batch 2026-07-19-002：T63/T64/T65 只读扫描

### 3.1 T63 exact-body recipe

对 `src/ai_sdlc/**/*.py` 做 Python AST parse；复制 `FunctionDef`、统一函数名、移除 decorator、使用 `ast.dump(include_attributes=False)` 分组。该 recipe 只发现结构候选，不证明 decorator、字段、失败语义或调用面可合并。

当前高位 family：

| family | defs/calls | physical | duplicate-copy | disposition |
|---|---:|---:|---:|---|
| `_write_yaml` | 11 / 72 | 121 | 110 | Deferred L1；需要 generators 私有 helper 与本地 alias 兼容 |
| `ProgramService.__post_init__` | 15 / constructor path | 120 | 112 | 本轮 No-Go；继承/构造语义风险高 |
| `_find_duplicates` | 11 / 45 | 88 | 80 | Deferred L1；净收益小，不阻塞 T66 |
| core `_dedupe_text_items` | 7 / 69 | 63 | 54 | Deferred L1 |
| CLI/gate list variant | 6 / 11 | 54 | 45 | Deferred L1 |

92 个两行 Pydantic validator 的 AST body 相同，但 decorator 的字段集合不同；不计作直接可删除的 182 行 family。

T64 Loop Store 的完全一致切片仍只有 39 LOC；基线无实质变化，既有 RC-06 No-Go 保持。

### 3.2 T65 builder inventory

| builder | file:line | physical LOC | src/test refs |
|---|---|---:|---:|
| `build_p2_frontend_page_ui_schema_baseline` | `frontend_page_ui_schema.py:252` | 317 | 17/42 |
| `build_p2_frontend_theme_token_governance_baseline` | `frontend_theme_token_governance.py:265` | 128 | 12/31 |
| `build_p2_frontend_quality_platform_baseline` | `frontend_quality_platform.py:351` | 172 | 9/32 |
| `build_p3_frontend_provider_expansion_baseline` | `frontend_provider_expansion.py:346` | 89 | 14/21 |
| `build_p3_target_project_adapter_scaffold_baseline` | `frontend_provider_runtime_adapter.py:265` | 77 | 12/20 |
| `build_p2_frontend_cross_provider_consistency_baseline` | `frontend_cross_provider_consistency.py:549` | 242 | 11/20 |

六项按 exclude-default 的正常多行 YAML 复算第二真值和最小 loader/resource/guard 成本：

| builder | current raw/non-empty | YAML 或最小实现成本 | 预测 disposition |
|---|---:|---:|---|
| Page/UI schema | 317/315 | YAML 207；乐观完整候选约 227/225 | Deferred L2 Conditional Go；预测净删约 90，须独立 disposable spike，proof 建议不超过 60、hard cap 75 |
| Theme token | 128/123 | 至少 132 | No-Go；预测净增 |
| Quality platform | 172/168 | 至少 166 | No-Go；净删 6/2，低于 10% |
| Cross-provider | 242/232 | 至少 244 | No-Go；预测净增 |
| Provider expansion | 89/88 | 至少 91 | No-Go；预测净增 |
| Runtime adapter | 77/75 | 至少 133 | No-Go；预测净增 |

Page/UI 仍须证明 package resource、wheel、clean install、offline、字段/顺序/默认值和 exact behavior；
本扫描没有 T61A/receipt，不能复用旧 claim，也不冒充 standalone T65 关闭证据。其余五项只冻结
当前 baseline 的预测 No-Go，最终单项处置仍须按父路线建立原子 receipt。

## 4. Batch 2026-07-19-003：T66/T67 结构扫描

### 4.1 T67

使用 `git show d19c8b7d...:src/ai_sdlc/cli/program_cmd.py` 与 current AST source segment 比较。九个 finalization handler 全部逐字一致：2,020 physical / 1,804 executable-orchestration LOC。

WI-204 的可信 T61A 最低估算仍为 Pascal 222 / Confucius 356，旧 hard cap=180；sponsor revoked、claim=0。旧 formal、hash、receipt 均不可复用。T67 保持 Deferred，且 T66 会改变其重叠 ProgramService baseline，之后必须重新扫描。

### 4.2 T66

九 stage × 五方法族得到精确 45-method 集合：

| family | count | physical | executable |
|---|---:|---:|---:|
| build request | 9 | 961 | 898 |
| execute | 9 | 1,589 | 1,517 |
| write artifact | 9 | 378 | 288 |
| build payload | 9 | 431 | 359 |
| load payload | 9 | 279 | 243 |
| total | 45 | 3,638 | 3,305 |

复算 recipe：physical=`end_lineno-lineno+1`；executable 从第一个非 docstring body statement 到
`end_lineno`。根复算得到五子族 `961/898`、`1589/1517`、`378/288`、`431/359`、`279/243`，
总计 `45 / 3,638 / 3,305`；一次错误的 non-empty 试算得到 3,572，因口径不符已拒绝，未写入预算。

额外证据：

- 45 个方法与 WI-203 baseline 对应源码逐字一致。
- 18 个 private payload build/load 方法各只有一个 `program_service.py` 内部调用，outside-service refs=0。
- 27 个 request/execute/write callable 保持现有签名；CLI 继续通过 ProgramService facade 调用。
- WI-203 inventory 的 59 CLI + 106 service tests 可作为 current T61A reuse inventory，但必须重跑。
- 预备终态≤466，净删≥3,172；新增/替换 product+proof≤686≤RC-06 cap793；shadow≤466≤545。
- 已关闭 WI205/WI206/WI210/WI211 的 RC-06 cap 分别为 27/54/49/31，合计 161；本候选按上限
  纳入后路线累计≤847≤1,500，仍须在下一 formal WI 对 current main 重算实际消耗与余额。

## 5. 候选排序决策

独立扫描 Agent 仅按收益/风险比，首选 T63 `_find_duplicates`：11 defs/45 calls，保守净删 raw≥78、
non-empty≥80，product additions≤21、proof cap≤22；`_write_yaml` 亦为 L1 Go，保守净删 raw≥95、
non-empty≥100，product additions≤31、proof cap≤31。该建议作为独立证据保留，没有被改写成支持根结论。

根选择同时考虑 RC-08 总缺口和两个超大文件终态：上述单项只贡献约 0.7%～0.9% 的当前 10,588 行
缺口，且不推进 `program_service.py` / `program_cmd.py` 的 400 行约束。LP-07 明确“低风险先行但不
强制串行”，因此小收益 L1 保留为 Deferred，不阻塞高收益 T66。该取舍是对抗评审的显式审查点，
不是既定正确结论。

唯一 Conditional Go：T66 bounded-stage ProgramService domain。该结论只授权下一 formal WI，不授权本分支产品修改。

预算自检把候选期与 deletion 终态分开计费：candidate+legacy 共存时，新 private module≤380、最终
facade body≤81、import/selector glue≤5，合计 shadow additions≤466≤545；删除 3,638 行 legacy 后
目标切片≤466、产品净删≥3,172。product+proof≤686≤`floor(3172×25%)=793`，余量≥107。

## 6. 当前待完成

- 写回 WI-196 的 L3 pre-release stability cycle 窄修。
- 生成 formal identity，执行双 Agent 对抗评审直到同 identity 双 PASS。
- 完成 truth/continuity/closure、PR、Codex/CI 与 detached fresh-main 验收。
