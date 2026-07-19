# 任务执行日志：AI-SDLC 精益减重候选选择

**功能编号**：`212-reduction-candidate-selection`
**创建日期**：2026-07-19
**当前状态**：current formal identity 已冻结；等待双方对 current identity 复审；产品实现未授权

## 1. 固定边界

- 本 WI 只允许 formal、父路线窄修、truth、continuity 与 project-state。
- 任一 `src/workflow/provider/runtime rule` 或测试逻辑/LOC 变化均为 blocker；test 唯一例外为
  manifest inventory/close 两值 `+2/-2` 等量替换。
- 所有历史 candidate/claim 只作证据，不得恢复。
- Parent+child formal-six 任一文件变化使两个对抗 Agent 的既有 PASS 同时失效。
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
| `_write_yaml` | 11 / 72 | 121 | 110 | RC-09 No-Go；product31+proof31=62>cap30 |
| `ProgramService.__post_init__` | 15 / constructor path | 120 | 112 | 本轮 No-Go；继承/构造语义风险高 |
| `_find_duplicates` | 11 / 45 | 88 | 80 | RC-09 No-Go；product21+proof22=43>cap22 |
| core `_dedupe_text_items` | 7 / 69 | 63 | 54 | RC-09 No-Go；product18+proof15=33>cap15 |
| CLI/gate list variant | 6 / 11 | 54 | 45 | RC-09 No-Go；product17+proof13=30>cap13 |

92 个两行 Pydantic validator 的 AST body 相同，但 decorator 的字段集合不同；不计作直接可删除的 182 行 family。

T64 Loop Store 的完全一致切片仍只有 39 LOC；基线无实质变化，既有 RC-06 No-Go 保持。

### 3.2 T65 builder inventory

| builder | file:line | physical LOC | product calls/files | test calls/files |
|---|---|---:|---:|---:|
| `build_p2_frontend_page_ui_schema_baseline` | `frontend_page_ui_schema.py:252` | 317 | 7/7 | 33/9 |
| `build_p2_frontend_theme_token_governance_baseline` | `frontend_theme_token_governance.py:265` | 128 | 5/5 | 24/7 |
| `build_p2_frontend_quality_platform_baseline` | `frontend_quality_platform.py:351` | 172 | 3/3 | 25/7 |
| `build_p3_frontend_provider_expansion_baseline` | `frontend_provider_expansion.py:346` | 89 | 6/5 | 14/6 |
| `build_p3_target_project_adapter_scaffold_baseline` | `frontend_provider_runtime_adapter.py:265` | 77 | 5/4 | 13/6 |
| `build_p2_frontend_cross_provider_consistency_baseline` | `frontend_cross_provider_consistency.py:549` | 242 | 4/4 | 14/5 |

六项按 exclude-default 的正常多行 YAML 复算第二真值和最小 loader/resource/guard 成本：

| builder | current raw/non-empty | YAML 或最小实现成本 | 预测 disposition |
|---|---:|---:|---|
| Page/UI schema | 317/315 | candidate约227单独已>RC-06 cap79；proof建议上限60只会扩大超支 | 预测 RC-09 No-Go；不得先写 resource/loader/spike |
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
- 27 个 public callable 的 physical/executable 为 2,928/2,703，必须保留的签名/header 共 225 行。
- 预备终态≤`225+81+5+380=691`，净删≥2,947；新增/替换 product+proof≤686≤RC-06 cap736；
  shadow≤466≤545。
- 既有 receipt 不重开，但路线累计按父 RC-06 当前 product+proof 合并口径保守计费：WI205/WI206/
  WI210/WI211 上限分别为 27/54/49/54，合计 184；本候选按上限纳入后≤870≤1,500。下一 formal WI
  仍须对 current main 重算实际消耗与余额。

## 5. 候选排序决策

独立扫描 Agent 仅按收益/风险比首选 T63 `_find_duplicates`，并把 product≤21、proof≤22 分开与预算
比较；Round 2 reviewer 依据父 RC-06 证明二者必须合并，`43>floor(88×25%)=22`。同理
`_write_yaml` 为 `62>30`，两个 `_dedupe_text_items` 为 `33>15` / `30>13`，truth/model/git family
也超 cap。因此独立扫描的 Go 建议作为已退役证据保留，T63 当前全部 RC-09 No-Go，而不是因收益小
才 Deferred。Page/UI 的乐观 candidate227 单独即超过 cap79，再加 proof 只会扩大超支，当前预测 No-Go。

唯一 Conditional Go：T66 bounded-stage ProgramService domain。该结论只授权下一 formal WI，不授权本分支产品修改。

预算自检把候选期与 deletion 终态分开计费：candidate+legacy 共存时，新 private module≤380、最终
public header225 原位保留；facade body≤81、import/selector glue≤5、新 module≤380，合计 shadow
additions≤466≤545。删除 legacy body/private 定义后目标切片≤691、产品净删≥2,947；
product+proof≤686≤`floor(2947×25%)=736`，余量≥50。

## 6. 当前待完成

- 对 finding 修订后的 current identity 执行双 Agent 对抗评审，直到同 identity 双 PASS。
- 完成 truth/continuity/closure、PR、Codex/CI 与 detached fresh-main 验收。

## 7. Batch 2026-07-19-004：pre-close manifest exact 预期失败

- authoring commit `46860df3` 上 constraints no BLOCKER、program validate PASS；truth current recompute
  complete=`1116/1116`、unmapped=0、唯一 active-child summary missing=1、close=`211/212`，snapshot stale。
- manifest exact 按旧 main 期望 `1111/1111/0/0`、close=`211/211` 运行，得到 `1 failed`；这是未生成
  child `development-summary.md` 前的预期 RED，不是通过证据。
- 该 RED 同时暴露 child formal 把 `tests/**` 全禁、与父 FR-12 允许两处机械真值替换的矛盾。Round 1
  review identity 已立即中止并退役；正式修订只允许 terminal inventory/close 两值 `+2/-2` 等量替换，
  不增加测试逻辑或 LOC。新 formal-six identity 必须由两位 reviewer 从零复算。

## 8. Batch 2026-07-19-005：Round 2 双 FAIL 处置

- Round 2 exact HEAD/tree=`6c1c9b35`/`c64c438b`，canonical formal-six=
  `104c020b3fe1b16896eb88dd1e06e08c86c6d010c6d99320a8a6031631350774`；Pascal FAIL 5、
  Confucius FAIL 4，双方 verdict 随本修订退役。
- 共同 finding 已接受：T66 补回 225 行 public header，统一终态691/净删2947/PS净减3327/RC-06
  cap736；manifest test 例外统一到 MUST/日志；恢复入口改为 Round 3。
- Pascal 的 T63/T65 合并成本 finding 已接受，所有当前 T63 与六个 T65 都处置为预测 RC-09 No-Go；
  不运行 disposable implementation spike。Confucius 的累计 finding 已接受：既有 receipt 不重开，
  但按当前合并口径将 WI211 product23 纳入，历史保守 subtotal=184、含 T66≤870。
- 新建 WI212 root/scoped byte-identical handoff，并清除 child 新增行尾空格；任何 formal 六文件变化都
  要求 Pascal/Confucius 对 Round 3 新 identity 从零复审。

## 9. Batch 2026-07-19-006：Round 3 split verdict

- exact HEAD/tree=`5d2279a1`/`79e28268`，formal-six=
  `a125dc311c86673d557853d1f2d1aca6affc20602652d7b4b9411179059495cb`；Pascal PASS0、
  Confucius FAIL2，内容修订使双方 verdict 同时退役。
- 两项 finding 均接受：T12 不再把已 fail-closed 的 T63 写成 Deferred；当前状态和待完成动作改为复审
  已冻结 identity，而不是重复生成 identity。候选矩阵、预算、测试例外、稳定周期和产品 scope 不变。
- tasks 属于 formal-six；本次最小修订后 Pascal/Confucius 必须对新 canonical identity 从零复审。

## 10. Batch 2026-07-19-007：Round 4 split verdict

- exact HEAD/tree=`9579fac0`/`61ac2a70`，formal-six=
  `f7c38d07bb969690698586ac1d81bce8b97d5a622a9235b06e1fed96c27b593c`；Pascal PASS0、
  Confucius FAIL2，任一内容修订使双方 verdict 同时退役。
- 两项 finding 均接受：execution 固定边界从错误的“三文件”统一为 parent+child formal-six；两份
  handoff 的阻断与下一步改为 round-agnostic current identity，不再指向已退役 Round 3。
- formal-six 本轮不变，但 HEAD/tree/diff 与 continuity 变化；为满足用户“意见统一且通过”，两位 reviewer
  仍必须对相同新 current identity 从零复审，不能保留 Pascal 旧 PASS。

## 11. Batch 2026-07-19-008：Round 5 双 FAIL 同一 finding

- exact HEAD/tree=`306f768e`/`d8772c98`，formal-six 保持
  `f7c38d07bb969690698586ac1d81bce8b97d5a622a9235b06e1fed96c27b593c`；Pascal/Confucius 均
  FAIL1，唯一共同 finding 为顶层 current state 仍写死已退役 Round 3。
- finding 已接受：顶层状态改为 round-agnostic 的“current identity 已冻结、等待双方复审”；历史 round
  只保留在 batch receipt，不再驱动恢复动作。内容变化后双方旧 FAIL identity 退役，须复审新 HEAD。
