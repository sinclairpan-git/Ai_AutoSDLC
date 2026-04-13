# 功能规格：Frontend Contract Sample Source Selfcheck Baseline

**功能编号**：`065-frontend-contract-sample-source-selfcheck-baseline`  
**创建日期**：2026-04-06  
**状态**：已冻结（formal baseline）  
**输入**：用户确认的 child work item 设计结论；[`../012-frontend-contract-verify-integration/spec.md`](../012-frontend-contract-verify-integration/spec.md)、[`../013-frontend-contract-observation-provider-baseline/spec.md`](../013-frontend-contract-observation-provider-baseline/spec.md)、[`../014-frontend-contract-runtime-attachment-baseline/spec.md`](../014-frontend-contract-runtime-attachment-baseline/spec.md)

> 口径：本 work item 是 `014-frontend-contract-runtime-attachment-baseline` 下游的 child work item，用于把“框架仓库内置 sample frontend source tree 作为显式 self-check 输入源”冻结成单一 formal truth。它不是 runtime fallback，不是默认 remediation，不是新的 provider 类型，也不改写 `012` verify truth、`013` provider/export truth 或 `014` runtime attachment truth。

## 问题定义

`012`、`013`、`014` 已经分别冻结了：

- contract-aware verify 对 canonical observation artifact 的消费语义
- scanner/export surface 与 canonical `frontend-contract-observations.json` 合同
- runtime attachment 对 active `spec_dir` artifact 的 read-mostly 消费边界

当前仍缺少一层独立 formal truth，用来回答下面这个问题：

- 当框架仓库自身需要做 `demo / smoke / self-check` 时，如何在**不依赖外部前端项目**的前提下，仍然保留 `source tree -> canonical artifact -> verify` 这条真实链路

如果不把这层边界单独冻结，后续实现很容易滑向两种错误方向：

- 为了让仓库“自包含”，在 `verify`、`program status`、`program plan` 或 `program integrate --dry-run` 里偷偷加 sample fallback，污染 production semantics
- 为了避免依赖外部仓库，直接提交手写 artifact 夹具，只证明 loader/consumer 可用，却绕过 scanner/mainline

因此，本 work item 需要先冻结的不是“再发明一个新命令”或“引入新的 provider registry”，而是：

- sample frontend source tree 的唯一合法落点是什么
- sample source 在框架中的角色是什么
- scanner/export、artifact、verify/program 之间的 truth order 如何保持单一
- invalid source root、empty observations、drift 与 missing artifact 之间的语义边界如何区分
- runtime remediation wording 如何保持诚实，不把仓库根目录误暗示成默认前端源码树

## 范围

- **覆盖**：
  - 将 sample frontend source tree 正式定义为框架仓库用于显式 self-check 的可选输入源
  - 锁定 sample source 的唯一合法落点为测试夹具路径，而不是运行时默认路径
  - 锁定 scanner/export 仍然必须要求显式 `source_root`
  - 锁定 `verify constraints`、`program status`、`program plan`、`program integrate --dry-run` 与 remediation helper 的 honesty 边界
  - 锁定 invalid source root、empty observations、drift、missing artifact 的正式语义
  - 锁定仓库内最小自包含验证矩阵，确保 `pass / drift / gap` 三类语义都可被独立演示
- **不覆盖**：
  - 新增顶层 CLI 命令
  - 让 `verify`、`run`、`program` 自动 fallback 到 sample fixture
  - 引入新的 observation provider registry、plugin system 或 runtime provider 类型
  - 自动发现外部前端仓库路径
  - 改写 canonical `frontend-contract-observations.json` schema
  - 把 sample source 提升为默认输入、默认 remediation 路径或 runtime attachment 默认行为

## 已锁定决策

- sample source 是框架仓库用于显式 self-check 的**可选输入源**，不是运行时默认依赖
- canonical artifact 仍然是唯一中间真值；`verify` 与 `program` 只消费 artifact，不感知 sample fixture
- sample fixture 只能位于 `tests/fixtures/frontend-contract-sample-src/**` 或等价测试夹具路径；运行时代码不得写死该路径
- scanner/export surface 必须继续要求显式 `source_root`；任何 helper、CLI、service 都不得在缺省情况下自动补 sample 路径
- invalid / nonexistent `source_root` 必须显式失败；valid `source_root` 但无标注文件必须成功生成稳定空 artifact；artifact 存在但与 contract 不匹配必须进入 drift，而不是退化成 gap
- runtime remediation 和 `recommended_commands` 只能使用 `<frontend-source-root>` 占位符；fixture 路径只允许出现在测试和文档示例中

## 用户故事与验收

### US-065-1 — Framework Maintainer 需要仓库自包含的真实 self-check 输入源

作为**框架维护者**，我希望仓库内存在一套最小 sample frontend source tree，且它只能通过显式 `source_root` 被扫描，以便在没有外部前端项目时仍能自包含演示真实的 scanner mainline。

**验收**：

1. Given 我显式执行 `uv run ai-sdlc scan <sample-source-root> --frontend-contract-spec-dir <spec-dir>`，When `<sample-source-root>` 指向 sample fixture，Then 会生成 canonical `frontend-contract-observations.json`
2. Given 我查看 `065` formal docs，When 我审阅 sample source 边界，Then 可以明确读到 sample fixture 只能位于测试夹具路径，且不是运行时默认输入

### US-065-2 — Operator 需要 gap / empty / drift 语义诚实且不混淆

作为**operator**，我希望 invalid source root、empty observations、missing artifact 与 drift 有清晰边界，以便在自检和真实项目接入时不会把“没有输入”和“有输入但不匹配”混成一个状态。

**验收**：

1. Given `source_root` 无效或不存在，When 我运行 `scan` export，Then 命令显式失败
2. Given `source_root` 有效但没有任何 observation 标注，When 我运行 `scan` export，Then 命令成功并生成稳定空 artifact
3. Given canonical artifact 已存在但 observations 与 contract 不匹配，When 我运行 `verify constraints`，Then 结果是 drift/mismatch blocker，而不是 `frontend_contract_observations` gap

### US-065-3 — Program Author 需要 verify/program honesty 不被 sample 特判污染

作为**program author**，我希望 `verify`、`program status`、`program plan`、`program integrate --dry-run` 与 remediation helper 完全不知道 sample fixture 的存在，以便仓库内 self-check 不会改写 production truth model。

**验收**：

1. Given 仓库里存在 sample fixture，但目标 `spec_dir` 还没有 artifact，When 我运行 `verify constraints` 或 `program status`，Then 仍然暴露 `frontend_contract_observations` gap
2. Given frontend remediation surface 需要提示下一步，When 我查看 `recommended_commands`，Then 命令必须使用 `<frontend-source-root>` 占位符，而不是 `scan .`
3. Given 我阅读 `065` formal docs，When 我确认 non-goals，Then 可以明确读到 program 层不得隐式触发 scan/materialization

## 功能需求

### Sample Source Role And Locality

| ID | 需求 |
|----|------|
| FR-065-001 | `065` 必须作为 `014` 下游的独立 child work item 被正式定义，而不是把 sample-source self-check 语义继续混回 `013` 或 `014` |
| FR-065-002 | `065` 必须明确 sample frontend source tree 只允许位于 `tests/fixtures/frontend-contract-sample-src/**` 或等价测试夹具路径 |
| FR-065-003 | `065` 必须明确运行时代码不得对 `tests/fixtures/frontend-contract-sample-src/**` 建立任何默认路径依赖 |
| FR-065-004 | `065` 必须明确 sample source 是框架仓库用于显式 self-check 的可选输入源，而不是 runtime fallback 或默认 remediation 输入 |
| FR-065-005 | `065` 必须明确 canonical `frontend-contract-observations.json` 仍然是唯一中间真值，sample source 只负责显式生成该 artifact |
| FR-065-006 | `065` 不得引入新的 provider 类型、registry contract 或 runtime attachment 私有格式；sample self-check 只能复用 `013` 已冻结的 scanner/provider/export truth |

### Explicit Scan Contract And Failure Semantics

| ID | 需求 |
|----|------|
| FR-065-007 | scanner/export surface 必须始终要求显式 `source_root`；任何 CLI、service、helper 都不得在缺省情况下自动补 sample 路径 |
| FR-065-008 | invalid 或 nonexistent `source_root` 必须显式失败，不得静默成功或偷偷回退到 sample fixture |
| FR-065-009 | valid `source_root` 但无任何标注文件时，scan/export 必须成功生成稳定空 artifact，且 envelope 结构保持一致 |
| FR-065-010 | valid `source_root` 有标注且生成 artifact 后，若 observations 与 contract 不匹配，后续 `verify constraints` 必须进入 drift/mismatch blocker，而不是 `frontend_contract_observations` gap |
| FR-065-011 | empty observations、missing artifact 与 drift 必须保持三个独立语义，不得互相折叠 |
| FR-065-012 | sample fixture 只允许作为显式 `source_root` 输入出现；不得参与任何 implicit materialization |

### Verify And Program Honesty

| ID | 需求 |
|----|------|
| FR-065-013 | `verify constraints`、`program status`、`program plan`、`program integrate --dry-run` 与 remediation helper 必须完全不知道 sample fixture 的存在，只认目标 `spec_dir` 中的 canonical artifact |
| FR-065-014 | 运行时 presence of sample fixture 不得改变 `verify/program` 的 truth model；当 artifact 不存在时，`frontend_contract_observations` 仍然必须作为 gap 暴露 |
| FR-065-015 | `program` 相关 surface 不得隐式触发 scan，不得隐式 materialize artifact，也不得因为 sample fixture 存在而自动转绿 |
| FR-065-016 | remediation `recommended_commands` 必须使用 `uv run ai-sdlc scan <frontend-source-root> --frontend-contract-spec-dir <spec-dir>` 这一占位口径，不得继续使用 `scan .` |
| FR-065-017 | fixture 路径示例只允许出现在测试和文档示例中；运行时 `suggested_actions`、`recommended_commands` 与 runtime status surface 不得泄漏 sample fixture 实际路径 |

### Stable Output And Self-Check Matrix

| ID | 需求 |
|----|------|
| FR-065-018 | sample-source self-check 相关单测必须覆盖稳定排序与稳定空结果语义，包括 `observations == ()`、`matched_files == ()` 与 artifact envelope 一致性 |
| FR-065-019 | sample fixture 集合至少要覆盖一个标准正例、一个多观察点页面、一个最小 drift 反例，以及一个 valid-but-empty source root |
| FR-065-020 | CLI 集成测试必须覆盖 `pass / drift / gap` 三类正式语义，其中 `gap` 通过“未生成 artifact”体现，而不是通过坏样本伪造 |
| FR-065-021 | program 集成测试必须明确断言 `program status / plan / integrate --dry-run` 不得隐式触发 scan/materialization |
| FR-065-022 | 仓库内 sample self-check 必须与真实外部前端接入共用同一后半段链路：区别只允许是 `source_root` 不同，不允许更换 verify 逻辑 |

## 关键实体

- **Sample Frontend Source Root**：位于测试夹具路径中的最小前端源码树，用于显式 self-check 的扫描输入
- **Sample Observation Fixture Set**：由 `match / drift / empty` 等子目录组成的最小样本集合，用于覆盖 `pass / drift / empty` 语义
- **Canonical Observation Artifact**：由 `scan` export 写入目标 `spec_dir` 的 `frontend-contract-observations.json`
- **Self-Check Verification Matrix**：仓库内用于证明 `source tree -> artifact -> verify` 主线的最小验证集合
- **Runtime Remediation Hint**：`program` surface 给 operator 的诚实提示，只允许表达 `<frontend-source-root>` 占位符，而不是默认 sample 路径

## 成功标准

- **SC-065-001**：`065` formal docs 能独立表达 sample source 的角色、合法落点、truth order 与 non-goals，而无需回到对话或实现细节临时推断
- **SC-065-002**：框架仓库在没有任何外部前端项目时，仍可通过内置 sample source fixture 自包含完成 `pass / drift / gap` 三类 self-check 演示
- **SC-065-003**：`verify constraints` 与 `program` surface 的 production semantics 不因 sample fixture 的存在而改变；缺 artifact 时仍稳定暴露 `frontend_contract_observations`
- **SC-065-004**：runtime remediation wording 不再暗示 `scan .`，而是稳定要求显式 `<frontend-source-root>`
- **SC-065-005**：后续实现团队能够从 `065` 直接读出 fixture 路径、推荐文件面、测试矩阵与“不允许 implicit materialization”的 guardrail

---
related_doc:
  - "specs/108-frontend-legacy-framework-evidence-class-backfill-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
