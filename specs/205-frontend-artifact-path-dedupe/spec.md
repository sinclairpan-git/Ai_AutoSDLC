# 功能规格：Frontend Artifact Path Dedupe Reduction

**功能编号**：`205-frontend-artifact-path-dedupe`\
**创建日期**：2026-07-15\
**状态**：formal review candidate\
**父项**：WI-196 `T63 / WP-03 / GAP-05`\
**基线 revision**：`e4f395e3b2247c0968d61aebd53814b1602f7845`

## 1. 问题与事实基线

`src/ai_sdlc/generators/` 下 12 个 frontend artifact generator 各自定义了一份完全同形的
`_dedupe_paths(paths: list[Path]) -> list[Path]`。以
`sha256(ast.dump(ast.Module(body=node.body), include_attributes=False))` 计算的完整 body digest 均为
`fc689b7af4ea63842b5f23af0e85b3e1d71d9255606baabb679fded9b83be9b4`；每份 9 个非空产品 LOC，
共 108 LOC，现有 13 个调用点。

这 12 份实现均使用 `Path` 的原生 hash/equality 去重，保留首次出现顺序，不访问文件系统，
也不做 `resolve()`、字符串转换、大小写折叠或错误包装。重复位于以下 artifact module：

- `frontend_contract_artifacts.py`
- `frontend_cross_provider_consistency_artifacts.py`
- `frontend_gate_policy_artifacts.py`
- `frontend_generation_constraint_artifacts.py`
- `frontend_page_ui_schema_artifacts.py`
- `frontend_provider_expansion_artifacts.py`
- `frontend_provider_profile_artifacts.py`
- `frontend_provider_runtime_adapter_artifacts.py`
- `frontend_quality_platform_artifacts.py`
- `frontend_solution_confirmation_artifacts.py`
- `frontend_theme_token_governance_artifacts.py`
- `frontend_ui_kernel_artifacts.py`

现有 14 个 materialize/path-dedupe 测试覆盖全部 12 个 generator，精确为 280 raw / 239 non-empty
LOC；但它们
把 writer 替换为同一个重复路径，只证明结果无重复，不能证明两个不同 `Path` 的首次出现顺序。
12-module targeted 基线为 76 tests，固定环境五次采样为 0.74/0.73/0.73/0.73/0.73 秒，median=0.73、
p95=0.74；frontend CLI/Program surface 为 broad slice 67 passed/208 deselected，加 rules 9 tests 与
solution-confirm 2 个精确 nodeid，共 78 passed。T61A 只允许在既有 dedupe test function 内增加两行
direct-binding 顺序断言；不得新增 test function/file、fixture 或通用 harness。

完整 scope ledger：12 个产品 module 为 2,602 raw / 2,275 non-empty LOC；目标 helper slice 为
108 raw / 108 non-empty LOC。12 个 artifact test file 为 2,723 raw / 2,317 non-empty LOC；其中
14 个 dedupe symbols 为 280 raw / 239 non-empty LOC。11 个精确 CLI materialize tests 为
414 raw / 392 non-empty LOC，另有 broad frontend slice 67 tests。

## 2. 目标、范围与非目标

### 2.1 目标

1. 将 12 份本地实现收敛为 `src/ai_sdlc/generators/_artifact_paths.py` 中唯一一份私有
   `_dedupe_paths`。
2. 保持 13 个调用点的函数名、返回顺序、`Path` 相等性、异常类型和 artifact 写入结果不变。
3. AST/non-empty 算法切片从 108 LOC 降为 9 LOC；固定 13 个产品文件的 raw diff additions≤24、
   deletions≥108、net≤-84；产品与 test source raw additions 合计≤26，低于 RC-06 cap 27。

### 2.2 范围

- 新增一个私有 helper module；不通过 `generators.__init__` re-export。
- 12 个 generator 仅增加一条私有 import，并删除本地 `_dedupe_paths` body。
- 在一个既有 dedupe test function 内增加两行最小顺序 characterization，复用全部现有 tests
  完成 T61A/T61B、回退和跨平台验证。
- 更新 WI-205 execution log、父 WI-196 Gap Evidence Index/continuity 与 Program Truth。

### 2.3 非目标

- 不合并 `_dedupe_text_items`、`_dedupe_mapping_items`、Pydantic validator 或 DTO。
- 不修改 artifact schema、YAML/JSON payload、路径名、字段顺序、CLI 或 public import surface。
- 不引入通用 `utils`、泛型、策略、配置、path normalization 或 filesystem probing。
- 不修改 frontend 技术栈、provider、主题、页面、组件或浏览器行为；因此本项不触发 frontend
  solution-confirm gate。
- 不顺带执行 WP-04、WP-05 或 ProgramService/Program Stage 减重。

## 3. 方案比较与冻结决策

### 方案 A：单个私有 helper module（采用）

在 `_artifact_paths.py` 保留一份当前算法，12 个 module 显式导入同名私有 helper。它有
13 个现有调用点，满足 LP-02；不需要 public API、配置或 adapter。固定 13 个产品文件的 raw
diff 冻结为 raw additions≤24、deletions≥108、net≤-84。

### 方案 B：12 个调用点内联 `list(dict.fromkeys(paths))`（拒绝）

虽然行数更少，但仍保留 12 份去重语义真值，并把异常/顺序合同隐藏在表达式中；后续变更仍需
同步 12 处，未实现“重复族 100% 收敛”。

### 方案 C：跨类型通用 dedupe utility（拒绝）

text/mapping/model/path 的转换、空值、hashability 和错误语义不同。泛型或配置化 helper 会扩大
CC-01/02/03/06 影响面，并违反 LP-03 与本项 RC-06 预算。

## 4. Compatibility 与 Reduction Contract

### 4.1 受影响兼容合同

- **CC-03**：materialize 返回路径的值、数量、首次出现顺序和 artifact tree 不变。
- **CC-05**：不增加写入、读盘、网络、子进程或授权副作用。
- **CC-06**：相同输入保持确定性、幂等与同一异常传播。
- **CC-07**：Windows/macOS/Linux 继续使用 `pathlib.Path` 原生 equality/hash；现有三平台 full pytest
  必须包含强化后的顺序 test 与 76 个 artifact tests，不引入平台规范化。
- **CC-01**：若路径集合进入 CLI 渲染，现有 stdout/JSON tests 必须保持零差异。

### 4.2 GAP-09～GAP-11 防回归影响分析

- GAP-09 frontend inheritance truth：不改 model/provider/governance artifact 内容，只收敛返回路径
  list helper；framework/consumer 分类不变。
- GAP-10 adapter consumption truth：不触碰 adapter、digest、transport 或 repository truth。
- GAP-11 source inventory：新增 tracked source 必须在 Program Truth 中映射，最终 inventory 保持
  complete、unmapped=0、missing=0。

### 4.3 RC 账本

| 合同 | 冻结值 / 门槛 |
|---|---|
| RC-01 | 12 个本地 `_dedupe_paths` body 与 13 个现有调用点 |
| RC-02 | 产品 modules=2602 raw/2275 non-empty；算法=108/108、complexity 36、12 defs、13 calls、syntactic fan-out 36/internal fan-out 0；tests=2723 raw/2317 non-empty，14 dedupe=280/239；targeted=76，median .73s/p95 .74s；CLI/Program=78 |
| RC-03 | 固定 13 产品文件 raw additions≤24；新增产品文件=1；公共抽象=0 |
| RC-04 | AST 算法 108→9（-91.7%）、complexity 36→3、fan-out 36→3；产品 raw deletions≥108、net≤-84 |
| RC-05 | 不允许 shadow 双实现；单提交替换；产品 raw additions≤24 |
| RC-06 | 产品 raw additions≤24 + 既有 test function raw additions=2 + handwritten harness/normalizer source=0；source 合计≤26≤27；唯一 generated receipt <2 MiB，不计 handwritten source LOC |
| RC-07 | 新文件 <400；唯一函数 <50；13 个现有调用点；无 public export |
| RC-09 | 需要选项/路径规范化/类型分支、新 test function/file/custom harness，test additions≠2、source additions>26、产品 additions>24、Git tree baseline 不稳定或需非空 allowlist 时停止 |
| RC-10 | before/after LOC、AST family count、RED/GREEN、differential、rollback 与 full/platform evidence |

### 4.4 T61A/T61B 复用证据与 truth 合同

- surface manifest 为 12 个 module、12 个 direct public materialize callers、1 个 indirect public
  built-in provider wrapper、1 个 private `_write_page_contract` caller 和 13 个 direct call sites；
  其中 10/12 module materializer 有 rules/Program 生产 CLI caller，contract 与 ui-kernel 只有 public
  re-export/库调用面。本项不新增或删除 CLI 命令/参数/public export。

| module | public / production surface |
|---|---|
| contract | package re-export；`public_library_only`；root consumers 为 frontend gate/verify/contract tests，CLI/Program callers=0 |
| ui-kernel | package re-export；`public_library_only`；production root/materializer callers=0 |
| provider-profile | package re-export；Program solution-confirm 经 built-in wrapper 间接调用 |
| cross-provider / gate-policy / generation-constraint / page-ui-schema | package re-export；rules 或 Program 生产 caller |
| provider-expansion / provider-runtime-adapter / quality-platform | package re-export；rules 或 Program 生产 caller |
| solution-confirmation / theme-token-governance | package re-export；rules 或 Program 生产 caller |

- direct symbol call fan-in 分布为 contract=2、其余 11 modules=1；candidate 必须保持 symbol call
  fan-in=13，并新增恰好 12 条 module import fan-in。每个 helper 的 syntactic fan-out 为
  `set/seen.add/unique.append` 三个 container operations，project-internal fan-out=0。
- 版本化 raw Golden normalizer 固定为 `wi205-git-tree-v1`：只调用现有标准 Git object database，
  用 tree object identity 比较相对路径、raw blob bytes、file mode 与 symlink target；不得新增 Python/
  PowerShell 遍历、过滤、序列化或 hashing source，`allowlist=[]`，`core.autocrlf=false`。运行时必须
  设置 `GIT_ATTR_NOSYSTEM=1`、将 `core.attributesFile` 指向仓库/basetemp 外的空文件，并在每个
  sample 前 fail-closed 证明 basetemp 内无 `.gitattributes` 且 fresh Git dir 的 `info/attributes` 为空。
- baseline 两次与 candidate 必须在本地 T61A/B target platform、同 Git/toolchain、同一绝对 shared
  `--basetemp` 顺序运行；
  Git dir/index 位于仓库与 basetemp 外且每次 sample 使用 fresh index。记录 Git version、object format、
  `core.filemode`、`core.symlinks`、absolute basetemp、entry count 与 tree OID。审前本机探针均为
  463 entries（418 regular +45 mode-120000 symlinks），且各自在同一 absolute basetemp 内两次
  OID 相同；不同 absolute basetemp 的 symlink target bytes 会使 OID 合理不同。权威 GoldenSnapshot
  只由 T61A paired run 生成；本地 T61B 要求 baseline/candidate 相等，不跨 basetemp 或 OS 比较
  OID/entry count。CC-07 跨平台证据由现有三平台 full pytest 提供，不要求 CI paired tree。
- 12 个 expected-file-set tests 继续覆盖 94 条 canonical paths，11 个 `_read_yaml` 与 1 个
  `_read_json` parser helper 支撑 payload/schema semantic assertions。tree OID 不同则用
  `git diff-tree --binary` 诊断并 fail-closed，不得扩大 allowlist。
- 唯一 durable evidence 为
  `.ai-sdlc/work-items/205-frontend-artifact-path-dedupe/t61-differential-rollback-receipt.json`；一个
  generated JSON 同时承载 versioned surface manifest、baseline/candidate `GoldenSnapshot`、
  `DifferentialResult` 与 rollback receipt。它计 1 个 snapshot/receipt 和实际体积，不计 handwritten
  product/test/harness/normalizer LOC；execution log 记录 evidence URI 与 SHA-256。
- 13 个调用全部位于 writer 执行后的直接 `return _dedupe_paths(...)`；T61B 的 exact source diff 必须
  证明 writer body、writer 调用顺序、artifact serialization 和 call expression 未改。因此本项不把
  parsed payload assertions 夸大为 raw-byte equality，也不为未触碰的 writer 再造 raw-byte harness。
- Path/order/error 由既有 test 内两行顺序断言、完整 AST body digest、14 个既有 dedupe tests 与
  unchanged-writer diff 共同保护；CLI/Program 使用 78 个既有 semantic assertion tests，不把
  substring/count/parsed-payload assertions 夸大为 raw stdout/stderr equality；renderer 代码未改。
- 目标 commit/PR 的 Program Truth 必须记录动态 `repo_revision + generated_at + snapshot_hash`，且
  `snapshot_state=fresh`、整体 `state=ready`、exit=0、zero blocker、inventory unmapped=0/missing=0；
  capability/blocking-ref exact set 必须落日志。GAP-09～GAP-11 blocker 或 source debt 再现即
  fail-closed 并重开对应 GAP。

## 5. 用户故事与验收

### US-1：维护唯一去重真值（P0）

作为框架维护者，我希望 frontend artifact generator 共用一份最小 path 去重实现，以便修复或审计
顺序语义时不再同步 12 份镜像代码。

**独立验收**：AST/文本复算只剩 `_artifact_paths.py` 一份实现，12 个 generator 均无本地定义，
全部现有 materialize path-dedupe tests 通过。

### US-2：保持 artifact 与错误合同（P0）

作为 CLI/生成器使用者，我希望减重前后的返回路径、顺序、写入集合和错误传播完全一致，以便升级
不改变任何既有工作流。

**独立验收**：既有 test 内两行顺序 characterization 能捕获 mutation RED；candidate 的 76 个
artifact tests、94 条 expected paths、payload assertions、78 个 CLI/Program tests 与 baseline
一致，且 exact diff 证明 writer/serialization 未改。

## 6. 功能需求

- **FR-01**：系统必须只保留一份 `_dedupe_paths` 算法实现，并由全部 13 个现有调用点复用。
- **FR-02**：helper 必须按首次出现顺序返回唯一 `Path`，且只使用当前 `Path` hash/equality。
- **FR-03**：helper 不得访问文件系统、规范化路径、转换类型、吞异常或包装异常。
- **FR-04**：12 个 generator 的 public 函数签名、artifact payload/bytes/tree 和返回路径不变。
- **FR-05**：T61A 必须在现有 materialize dedupe test function 中通过
  `frontend_contract_artifacts` 模块 private binding 增加两行多 `Path` 顺序断言，再用可恢复
  `reverse(unique_output)` mutation 证明该测试因 first-seen order 变化而 RED；实现收敛后同一
  binding 指向 canonical helper，断言无需改写。
- **FR-06**：T61B 必须绑定 candidate tree/hash，以 `wi205-git-tree-v1` 证明 raw tree identity，
  证明重复族清零、LOC 达标、全部复用证据通过、writer/call expression 零未批准差异和可回退，
  并生成 scoped structured receipt。
- **FR-07**：代码改动不得超出冻结的 helper + 12 imports/local-body deletion + 既有 test function
  两行断言；truth/continuity 与唯一 generated scoped receipt 除外。
- **FR-08**：formal 与最终树均由兼容安全、精简效率两个独立 Agent 对同一 hash 明确 PASS。
- **FR-09**：PR 必须完成 Codex review、required checks、heartbeat、merge 与 fresh-main 复验。

## 7. 边界与停止条件

- 空 list 返回空 list；重复项只保留第一次；全唯一输入保持原顺序。
- 相对/绝对、大小写、`.`/`..`、不同 drive/anchor 的判断完全交给 `Path` 原生语义。
- 运行时非 `Path` 可哈希对象沿用当前动态行为；不可哈希值继续抛原生 `TypeError`。
- 任一 artifact path/order/bytes、异常类型、CLI 输出或平台 smoke 发生未批准差异即停止并回退。
- `wi205-git-tree-v1` 本地两次 baseline 不稳定、candidate tree/entry count 不同、Git/attribute
  隔离漂移或需要排除任意 path 时停止；不得把 pytest `*current` symlink 隐藏在 allowlist。
- helper 出现选项、分支、协议、类或 public export，产品 raw additions>24，产品+test source raw
  additions>26，或顺序保护不是既有 function 内精确两行/出现新 test function/file/harness，即按
  RC-09 No-Go。

## 8. 成功标准

- **SC-01**：12 份实现收敛为 1 份，13 个调用点全部复用 canonical helper。
- **SC-02**：AST 算法 108→9、complexity 36→3、fan-out 36→3；固定 13 产品文件 raw
  additions≤24、deletions≥108、net≤-84；产品+test source additions≤26。
- **SC-03**：14 个既有 path-dedupe tests（其中一个增加两行顺序断言）、76-test targeted、
  94-path/payload assertions、78-test CLI/Program surface 与 full suite 通过；本地 paired Git tree OID/
  entry count 相等、现有三平台 full pytest 通过、writer exact diff clean、scoped receipt 完整。
- **SC-04**：Ruff、verify constraints、Program validate/truth、git diff-check 全部 PASS。
- **SC-05**：GAP-09～GAP-11 不回归，inventory complete 且 unmapped/missing=0。
- **SC-06**：formal hash 与 final-tree hash 均获得 Pascal/Confucius 一致 PASS，无可操作 finding。
- **SC-07**：PR 合入 main 后 fresh clone 重跑 targeted/full/truth，结果与候选一致。
