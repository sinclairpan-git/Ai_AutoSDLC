# 功能规格：AI-SDLC 精益减重候选选择

**功能编号**：`212-reduction-candidate-selection`
**创建日期**：2026-07-19
**状态**：只读候选决策；未授权产品实现
**类型**：WI-196 / T63～T67 候选选择与 L3 路线缺口修正

## 1. 背景与基线

本工作项基于 fresh main `32742a25ef0c8d0f5a5480e0dcc9fcb105e2c45b`。当前可复算基线：

- `src/ai_sdlc/**/*.py`：217 个文件、107,321 行；相对 WI-196 基线 107,482 行仅净减 161 行。
- RC-08 的 10% 终态上限为 96,733 行，当前仍至少需要净减 10,588 行。
- `program_service.py` 为 17,474 行，`program_cmd.py` 为 7,057 行，均远高于 400 行。
- GAP-05、GAP-06、GAP-03、GAP-04、WI-196、RC-08 与版本发布仍保持 open。
- T62A 没有新 sponsor；WI-202/WI-204 的 revoked claim 均为 0，不得复活、转移或冒充新候选授权。

行数和相似度只用于筛选。任何 Go 都必须继续满足 WI-196 的 LP、CC、RC 与 T61A/B，不能以净删行数替代行为等价证明。

## 2. 范围与非目标

### 2.1 本工作项范围

1. 在同一 fresh-main revision 上复算 T63、T64、T65、T66、T67 候选。
2. 对每类候选记录真实定义、调用者、保守删除下限、保护成本、风险和 Go/No-Go/Deferred。
3. 只选择一个高收益、可原子实施的下一候选，并冻结其预备 Reduction Contract。
4. 修正父路线中“L3 需要稳定发布后删旧”与“RC-08 前禁止发布版本”的流程死锁，并消除 RC-06
   文字仅指 WP-01/WP-02、适用矩阵却覆盖 WP-03～WP-07 的矛盾。
5. 由两个独立只读 Agent 对同一 child/parent `spec.md + plan.md + tasks.md` 六文件身份评审到 findings=0。

### 2.2 明确非目标

- 不修改 `src/`、测试逻辑、workflow、provider、runtime rule 或发布配置。唯一测试例外是父 FR-12
  允许的 `test_repo_program_manifest.py` inventory/close 两个精确值等量替换，不增加逻辑或 LOC。
- 不实现候选、不新增 harness、不切换路由、不删除 legacy、不发布版本。
- 不恢复旧 spike、旧 candidate hash、WI-203/WI-204 sponsor 或 WI-202 claim。
- 不以本工作项关闭 GAP-03～GAP-06、WI-196 或 RC-08。
- 不把低收益重复族包装为 L3，也不为未来需求创建扩展点、DSL、schema 或通用 executor。

## 3. 候选矩阵与结论

`No-Go（本轮）`只表示不能成为当前下一实现项；T65 的正式单项关闭仍须按父路线建立独立 receipt。

| 路线 | fresh-main 证据 | 保守收益/成本 | 本轮结论 |
|---|---|---|---|
| T63 `_write_yaml` | 11 个完全相同定义/72 calls，121 行 | product additions≤31 + proof≤31 =62，超过 `floor(121×25%)=30` | RC-09 No-Go；产品净删预测不能抵消合并保护成本超限 |
| T63 `ProgramService.__post_init__` | 15 个完全相同 8 行实现，共 120 行 | 需要改变 dataclass 继承/构造边界，净收益小且语义风险高 | No-Go（本轮） |
| T63 `_find_duplicates` | 11 个完全相同定义/45 calls，共 88 行；11 模块已依赖同一 `_string_lists` | product additions≤21 + proof≤22 =43，超过 `floor(88×25%)=22` | RC-09 No-Go；独立扫描把 product/proof 分开计费的 Go 结论退役 |
| T63 core tuple `_dedupe_text_items` | 7 defs/69 calls，共 63 行 | product≤18 + proof≤15 =33，超过 `floor(63×25%)=15` | RC-09 No-Go |
| T63 CLI/gate list `_dedupe_text_items` | 6 defs/11 calls，共 54 行 | product≤17 + proof≤13 =30，超过 `floor(54×25%)=13` | RC-09 No-Go |
| T63 `_program_truth_gate_surface` | 2 defs/2 calls，共 70 行，涉及 fail-closed truth | product≤47 + proof≤16 =63，超过 `floor(70×25%)=17` | RC-09 No-Go；且保持 L2 |
| T63 `_dedupe_model_items` / `_git_text` | 分别 36/23 行 gross | product+proof 分别≤26/6，超过 cap 9/5 | RC-09 No-Go |
| T64 Loop Store | 既有 fresh-main 审计只定位 39 行完全一致切片 | helper 与恢复/损坏输入保护超过 RC-06 | RC-09 No-Go 保持；不重开 |
| T65 Page/UI builder | 317/315 raw/non-empty；正常多行 YAML 207 行 | 乐观 candidate 227 单独已超过 `floor(317×25%)=79`，再加 proof 建议上限 60 只会扩大超支 | 预测 RC-09 No-Go；不得先写 resource/loader/spike |
| T65 其余五 builder | Theme/Quality/Cross/Expansion/Runtime 为 128/172/242/89/77 raw LOC | 乐观 YAML+最小 loader 成本仍为 ≥132/166/244/91/133；四项净增，一项低于10% | 预测 No-Go；后续逐项 standalone receipt |
| T67 九个 finalization CLI handler | 当前九段源码与 WI-203 baseline 逐字一致，2,020 行；旧预测净删至少 1,501 行 | WI-204 已实证可信保护最低为 222/356 行，旧 hard cap 180，sponsor revoked、claim=0 | Deferred；不得复用旧 formal，且应在 T66 改变重叠 service baseline 后重新扫描 |
| **T66 bounded-stage ProgramService domain** | 九阶段 45 个方法，物理 3,638 行、可执行职责 3,305 行；详见 §4 | 预测产品净删至少 2,947 行；现有 165 个相关 service/CLI 测试可复用 | **Conditional Go：唯一下一候选** |

T63 的两行 Pydantic validator wrapper 不视为可直接删除的 exact family：装饰器绑定的字段集合和模型失败语义不同，不能按 92×2 行把字段级契约误算为重复收益。

## 4. 选中候选：T66 bounded-stage domain

### 4.1 精确目标切片

九个 stage id：

`cross_spec_writeback`、`guarded_registry`、`broader_governance`、`final_governance`、`writeback_persistence`、`persisted_write_proof`、`final_proof_publication`、`final_proof_closure`、`final_proof_archive`。

每个 stage 只包含以下五个当前方法族，共 45 个方法：

1. `build_frontend_<stage>_request`
2. `execute_frontend_<stage>`
3. `write_frontend_<stage>_artifact`
4. `_build_frontend_<stage>_artifact_payload`
5. `_load_frontend_<stage>_artifact_payload`

明确排除 thread archive、project cleanup、CLI handler、renderer、Pydantic model、其他 ProgramService 领域和公共 artifact/schema 变更。

### 4.2 冻结测量

| 子族 | 方法数 | 物理 LOC | 可执行职责 LOC |
|---|---:|---:|---:|
| request builders | 9 | 961 | 898 |
| executors | 9 | 1,589 | 1,517 |
| artifact writers | 9 | 378 | 288 |
| payload builders | 9 | 431 | 359 |
| payload loaders | 9 | 279 | 243 |
| **合计** | **45** | **3,638** | **3,305** |

计量 recipe 固定为 Python AST：physical=`end_lineno-lineno+1`；executable responsibility 从函数体
第一个非 docstring statement 的 `lineno` 计到 `end_lineno`，保留其间空行但排除 decorator、函数签名
和 docstring。该 recipe 对五个子族复算为 `961/898`、`1589/1517`、`378/288`、`431/359`、
`279/243`，不得改用 non-empty LOC 混算预算。

27 个既有 request/execute/write 方法的签名和返回类型必须保留；18 个 private payload 方法仅在 `program_service.py` 内各有一个调用者，fresh-main 无外部引用。

上述 45 个方法与 WI-203 baseline `d19c8b7d...` 的对应源码逐字一致。WI-203 记录的 59 个 CLI 与 106 个 service 相关测试因此可作为 T61A reuse inventory，但必须在下一 WI 对 current head 重新执行，不能复用旧 PASS。

### 4.3 预备 Reduction Contract

以下只是下一 formal WI 的准入上限；下一 WI 必须复算并经同 identity 双审后才可写产品代码。

| 合同 | 冻结值 |
|---|---|
| RC-01 | 仅 §4.1 的 45 个方法和一个同领域 private module；27 个既有 callable 保持 |
| RC-02 | target physical=3,638；executable responsibility=3,305；`program_service.py`=17,474 |
| RC-03 | 新 private module≤380 行；27 个 public callable 的 225 行签名/header 原位保留；deletion 后 facade body 合计≤81 行；import/selector glue≤5 行；公共抽象=0；新增依赖=0 |
| RC-04 | 原文件可执行职责≥90% 收敛：3,305→≤81；目标切片终态≤691 行；产品净删≥2,947 行；九阶段镜像分支 100% 消除 |
| RC-05 | legacy 共存时新增产品≤466 行；硬上限 `min(3638×15%,1000)=545`，余量≥79 |
| RC-06 | product/test/harness/normalizer additions 合计≤686；其中新增 test/harness/normalizer≤220；`floor(2947×25%)=736`，保留≥50 行缓冲；按当前合并口径保守计入既有四项上限 27/54/49/54=184，本候选纳入后路线累计≤870≤1,500 |
| RC-07 | 新文件≤400 行；新函数≤50 行；只允许 private stage definition/engine，九个当前调用者满足 LP-02 |
| RC-09 | 任一预算超限、出现 stage-specific `if/match` 堆叠、不能复用现有测试、任一语义差异或需第二领域时立即 No-Go |
| RC-10 | before/after、AST/LOC、45-symbol map、九阶段 differential、rollback/reapply、cross-platform/install/offline/sibling smoke 全部落盘 |

预计 `program_service.py` 保留 public header 225、facade body≤81 与 glue≤5 后，本切片减少至少
3,327 行，文件从 17,474 行下降到不高于 14,147 行；全产品再计入新 module≤380 后净删至少
2,947 行。这只是一个领域切片，不代表文件或 RC-08 终态达成。

## 5. L3 稳定周期与发布禁令的统一解释

为消除父路线死锁，WI-196 的 WP-06/WP-07 与 FR-07 中“稳定发布周期”统一解释为**主线预发布稳定周期**：

1. candidate PR 合入 main 时完整 legacy 仍保留，默认 selector 切到 candidate。
2. 对精确 merge tree 完成 required cross-platform CI、构建 wheel/sdist、clean-env 安装、离线 smoke、代表性兄弟项目 smoke 和 selector rollback/reapply。
3. 上述一个完整周期无未批准差异后，才允许独立 legacy-deletion PR。
4. 该周期不创建 tag、不发布 GitHub Release/PyPI 版本、不更新全局 CLI；RC-08 前发布禁令保持不变。
5. deletion 后再次执行同等安装包与 rollback receipt；整个 candidate+deletion 仍属于同一 T66/T67 工作包，删除前不得关闭。

## 6. 功能需求

- **FR-001**：所有候选数据必须绑定 main revision、文件、符号、LOC recipe 和调用者证据。
- **FR-002**：候选排序必须同时使用预计净删除、RC-06 保护成本、风险和对 RC-08 两个大文件的贡献。
- **FR-003**：T62A、WI-203/WI-204 的旧 sponsor/claim/hash 不得复活或转移。
- **FR-004**：只允许一个 Conditional Go；其余候选必须有可审计 disposition。
- **FR-005**：本工作项不得修改产品、测试逻辑、工作流、provider、runtime rule 或发布面；唯一测试
  例外是父 FR-12 允许的 manifest inventory/close 两个精确值等量替换，不增加逻辑或 LOC。
- **FR-006**：父路线必须采用 §5 的预发布稳定周期，解除 L3 删除与版本禁令死锁，但不得放宽差分、回退或最终发布门禁。
- **FR-006A**：父 RC-06 的文字范围必须与适用矩阵一致；25%、路线累计 1,500 行及 fixture/snapshot 上限不得放宽。
- **FR-007**：两个对抗 Agent 必须对同一 child/parent formal-six identity findings=0；六文件任一内容变化使双方 PASS 同时失效。
- **FR-008**：Conditional Go 只授权创建下一独立 formal WI，不授权在本分支写产品代码。

## 7. 成功标准

- **SC-001**：候选矩阵覆盖 T63～T67，T62A 排除理由明确，无未处置候选。
- **SC-002**：T66 的 45-symbol/3,638/3,305 测量可由仓库脚本重算，预算公式无负余量或重复计费。
- **SC-003**：父路线 L3 流程不再要求在 RC-08 前发布版本，也不允许无稳定周期直接删旧；RC-06 文字范围与适用矩阵一致。
- **SC-004**：`src/`、workflow、provider、runtime rule diff 为零；test diff 精确等于 manifest
  inventory/close 两个值替换且 `+2/-2`、逻辑与 LOC 不变。
- **SC-005**：constraints、program validate、truth audit、manifest exact、diff/path/parity 门禁通过。
- **SC-006**：LEAN/YAGNI 与 SAFETY/COMPAT 两位 reviewer 对同一 identity 均 PASS、findings=0。
- **SC-007**：WI212 合并后只允许创建一个新的 T66 formal work item；发布仍被 RC-08 阻断。
