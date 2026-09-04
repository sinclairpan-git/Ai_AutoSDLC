# 功能规格：v0.9.9 Canonical Release

**功能编号**：`226-v0-9-9-canonical-release`
**创建日期**：2026-09-03
**状态**：`bbb39ca4` 因 `F-TRUTH-SCOPE-01` 暂停合并；同根稳定化设计已获用户批准，待书面复核
**决策来源**：原终局合议 3:0 批准方案 B；2026-09-03 对抗合议批准一次同根自动稳定化回退。

## 1. 目标与范围

以一个 canonical work item 和一个实施/发布 PR，把 `v0.9.8` 之后已经进入远端主线的改动整理为可审计、可构建、可发布的 `v0.9.9`。发布准入使用现有逐规格 Program Truth readiness；全局 Program Truth 继续如实保留 16 项历史 portfolio blocker，不以全局 `ready` 作为本次发布前置条件。

**范围内**：

- 固定发布基线 `v0.9.8@4f3e55c300dab20fb4fea93818d79394a927f77e`。
- 以初始化时的远端主线 `8f9df406e0a0a8fcb7a3da0be5ab164358918773` 作为范围审计锚点；最终 candidate head 以实施/发布 PR 的实时精确 HEAD 和发布 tag 指向的精确 SHA 为准，禁止在同一提交正文中伪造自引用 HEAD。
- WI226 在 `program-manifest.yaml` 中显式依赖 WI219、WI220、WI221、WI222、WI224、WI225；这是唯一发布范围来源。
- 在现有 `program truth audit` 上提供按 WI 审计入口，聚合 WI226 与其传递依赖的现有 per-spec readiness。
- 在 PR Checks 和 Release Build 中执行同一按 WI 审计；Release Build 必须在构建、证明和上传资产之前通过。
- 同步 `0.9.9` 版本真值、发布说明、安装入口、工作流默认值和既有一致性测试。
- 合并后按现有发布流程创建 tag、三平台资产、校验/attestation、release smoke，并验证 12-route 自然发布回执。

**范围外**：

- 不清理、不豁免、不改写 16 项历史 Program Truth blocker；D2 继续留在 portfolio backlog。
- 不新增 ledger、manifest schema、waiver、通用提交区间推断器或第二套发布状态。
- 不修改 WI222/WI224 的历史 execution log，不把 PR #200 倒灌为二者的实现完成证据。
- 不开发新的产品特性，不处理本地产品站、材料分支或其他非远端主线 worktree。
- 不恢复或继续 `e70951c3` 的通用 release-scope inference 设计。

## 2. 发布组件账本

以下是 `v0.9.8..8f9df406` 的 18 个 first-parent 主线载体；WI226 的实施/发布 PR 将作为最终第 19 个自载体，由 GitHub PR HEAD 与发布 tag 外部绑定。

| PR | 主线 SHA | 归属 | 发布口径 |
|---|---|---|---|
| #179 | `6002cd7a` | WI219 | post-v0.9.8 ROI roadmap 归档 |
| #180 | `0294bd6a` | WI219 | 历史 Program Truth provenance debt 归档 |
| #181 | `bd9cea91` | WI219 | 如实持久化 blocked Program Truth |
| #182 | `47a51c7f` | WI219 | continuity 收口 |
| #183 | `21be82b4` | WI219 | workitem truth 绑定 scoped branch evidence |
| #184 | `e70ced90` | WI219 | P1 No-Go 收口并进入 P2 |
| #185 | `32581602` | WI220 | ordinary-user single-entry 实现载体 |
| #186 | `263abb3d` | WI220 | post-merge truth closeout |
| #187 | `6e21daaa` | WI221 | release-target provenance 准入审计 |
| #188 | `2e507df6` | WI221 | mainline truth closeout |
| #189 | `024c38a4` | WI222 | 12-route evidence contract formalization |
| #190 | `49d43c45` | WI222 | formal-only post-merge truth closeout |
| #192 | `547e78fd` | WI224 | R02 native attestation formalization |
| #193 | `1f6f3eba` | WI224 | formal mainline truth closeout |
| #194 | `3155af39` | WI224 | R02 native release attestation implementation |
| #195 | `e8a73ec4` | WI224 | implementation truth closeout |
| #196 | `f0e0e4d6` | WI225 | terminal sponsor convergence formal admission |
| #200 | `8f9df406` | WI226；引用 WI222/R06 合同 | macOS existing-project online 自然发布前置组件；在 `release.published` 回执产生前保持 `partial` |

上述映射只定义本次 release composition，不改变依赖 WI 的历史终态。

## 3. 用户故事与验收

### US-1：有界发布准入（P0）

作为维护者，我希望发布门禁只检查 WI226 显式声明的依赖闭包，以便在保留全局历史债务的同时，对本次版本做可重复、不会无限扩张的判定。

**独立验收**：在全局 truth 为 `blocked` 且 blocker 全部与 WI226 依赖闭包无关时，`program truth audit --wi specs/226-v0-9-9-canonical-release` 成功；任一依赖命中 release blocker、manifest 无效或 snapshot stale 时失败。

### US-2：不可绕过的发布门禁（P0）

作为发布负责人，我希望 PR 与 tag 构建都执行相同门禁，以便本地口头结论不能替代 CI 证据。

**独立验收**：工作流测试证明 PR Checks 包含该命令，且 Release Build 中该命令位于 build、attest、upload 之前；命令失败时后续步骤不会运行。

### US-3：一致的 v0.9.9 发布真值（P1）

作为普通用户，我希望 README、用户指南、离线包、发布说明与安装/升级 smoke 都指向同一版本，以便按一个入口完成安装或升级。

**独立验收**：版本一致性测试、约束验证、全量测试、三平台 release smoke 与 12-route 自然发布回执均通过。

## 4. 功能需求

- **FR-001**：WI226 必须使用 `roles: [release_candidate]` 与显式 `depends_on`；禁止从 Git range、提交标题或历史 execution log 自动猜测范围。
- **FR-002**：`program truth audit` 不带 `--wi` 时行为、输出和退出码保持不变。
- **FR-003**：带 `--wi` 时，系统必须解析唯一 manifest spec，遍历其传递依赖，并让所有成员消费同一次 truth 评估上下文；共享上下文存在时不得再进入 persisted fast path 或重建 snapshot，也不得复制 readiness 判定规则。
- **FR-004**：根 WI 缺少 `release_candidate` role、路径未映射、依赖图无效、truth 未启用、snapshot stale 或任一闭包成员未 ready 时，按 WI 审计必须非零退出并给出有界修复动作。
- **FR-005**：闭包外的 16 项历史 blocker 不得阻止 WI226；其数量、内容和全局 `blocked` 状态不得被改写。
- **FR-006**：PR Checks 与 Release Build 必须调用同一个 `program truth audit --wi` 契约；Release Build 继续验证 tag/event/checkout 三者 SHA 一致。
- **FR-007**：所有 `0.9.8` 当前发布入口必须按既有 release consistency contract 更新为 `0.9.9`，历史叙述或明确比较项除外。
- **FR-008**：PR #200 只能在 WI226 中记为 R06 `partial` 组件；只有真实 `release.published` workflow 回执可以把对应自然发布证据判为完成。
- **FR-009**：实现限制为一个实施/发布 PR、净新增生产代码不超过 150 行、无新持久化状态、无新 public command；`--wi` 只是现有 audit 的可选参数。
- **FR-010**：若一人日内无法让 focused tests、全量测试和 constraints 同时通过，则终止本 WI 的实现并保留明确 limitation；不得现场新增第二套设计或第二个修补 PR。

## 5. 边界与失败语义

- GitHub/API 暂时不可观察属于外部状态 `unknown/pending`，可在同一精确 HEAD 上重试；不得记作 candidate 代码失败，也不得消耗代码修复轮次。
- 确定性 finding 以“不变量 + 责任边界/调用链 + 根因类别 + 可观察后果”归入 finding family；文件、行号或 reviewer 措辞变化不自动生成新 family。
- 开发分为 `discovery/stabilize` 与 `certify`：前者完成同根场景饱和审查、合并修复和全量预认证，后者才冻结 exact HEAD。二者只是本仓开发流程标签，不是新的 runtime/manifest 状态。认证阶段发现同 family、同范围且未超预算的问题时，自动退回稳定化一次，不重建 WI、设计、计划或 PR，也不再次申请 Sponsor。
- 当前只授权 `F-TRUTH-SCOPE-01` 一次稳定化 wave 和一次新的 exact-HEAD 认证。修复后同 family 仍复现、出现第二个 family、突破范围/预算或最终认证仍有 load-bearing finding 时，立即 No-Go。
- `--wi` 只接受项目内路径；零匹配、多匹配、越界路径均 fail closed。
- 同一依赖只检查一次；manifest 既有校验负责未知依赖和环检测。
- 发布后自然回执失败仅修复与本 WI 改动有直接因果关系的问题；新发现的独立产品缺陷进入 backlog，不扩展 v0.9.9。

## 6. ROI 与退出条件

- **收益**：结束“全局历史债务是否阻止当前版本”的反复争论；发布范围从口头清单变成一个可执行、CI 强制的显式依赖闭包。
- **现状证据**：远端主线包含 18 个未发布 first-parent 载体；全局 truth 如实 `blocked`，而现有 per-spec readiness 已能区分相关与无关 blocker；当前工作流尚未消费该逐规格结果。
- **最小性**：复用 manifest `roles/depends_on`、现有 readiness、现有 audit 命令和现有发布工作流；不建立 range ledger 或新状态机。
- **投入上限**：实施与测试不超过 1 人日，CI/云端评审等待不计入；生产代码净新增不超过 150 行。当前 `143/150` 不获得额外额度，稳定化必须通过简化现有新增实现容纳正确修复；以后同类工作在初始实现阶段只消费 120 行，预留 30 行稳定化储备。
- **删除/回退触发器**：如果无法在不复制 truth 逻辑的前提下实现，或需要新增 schema/waiver/ledger，则 No-Go 并整体回退该 audit 扩展；版本发布不以降级门禁继续。
- **决策**：保持 PR #201 关闭；`bbb39ca4` 作为被否决候选的冻结证据，不得改写或冒充新候选。直到本增补通过书面复核，不得产生新的 implementation candidate；复核后只允许在同一 WI、同一分支、同一 PR 内执行 `F-TRUTH-SCOPE-01` 的一次稳定化 wave。

## 7. 成功标准

- **SC-001**：按 WI 审计除既有正向、相关 blocker、stale、非 release candidate、兼容旧命令测试外，还必须覆盖：无 matched capability + 闭包外 blocker、matched capability 全 ready + 闭包外 blocker、matched capability blocked、应匹配 capability row 缺失四类状态。
- **SC-002**：PR Checks 与 Release Build 对 WI226 的门禁均不可跳过，且工作流顺序测试通过。
- **SC-003**：`uv run ai-sdlc verify constraints`、focused suite、全量 `uv run pytest -q` 均通过。
- **SC-004**：全局 Program Truth 仍为 `blocked` 且保留全部 16 项 blocker；WI226 依赖闭包单独达到 ready。
- **SC-005**：发布 tag 精确指向合并后的 `origin/main`，三平台资产、SHA256、attestation、release smoke 与 12-route 自然发布回执通过。
- **SC-006**：persisted snapshot 为 ready 或 blocked 时，七成员候选审计均只允许一次 `build_truth_snapshot()`/truth evidence 构建；只统计 `build_truth_ledger_surface()` wrapper 不构成证明。
- **SC-007**：稳定化后的 focused、全量、Ruff、constraints、program validate、diff-check、真实规模 scoped audit 和 required checks 必须绑定同一 exact HEAD；任一新提交使旧证据与认证失效。

## 8. `F-TRUTH-SCOPE-01` 最终根治增补

两个 P2 是同一根因的两种表现：`build_spec_truth_readiness()` 同时承担独立调用时的全局 truth 构建和共享上下文中的成员投影，但共享 surface 不是权威输入，造成计算生命周期泄漏与判定范围泄漏。

**唯一技术合同**：

1. 每次 release-candidate audit 只构建一个 current truth snapshot/surface，并由所有 closure member 只读消费。
2. 共享上下文存在时跳过 persisted fast path；独立 spec readiness 调用仍可保留原 fast path。
3. snapshot missing/invalid/stale、manifest/root/role/graph 无效继续 fail closed。
4. snapshot fresh 后，成员只由 matched capability rows 判定：全部存在且 ready 则 ready；任一非 ready 则只返回相关 blocker/action；应存在的 row 缺失则 fail closed；闭包外 blocker 只保留在全局 truth。
5. 生产修复只触及 `program_service.py` 与直接单测；另只允许在根 `AGENTS.md` 中把“任一 finding 终止”改为本节的两阶段规则。不修改 CLI、workflow、manifest schema、全局 snapshot/blocker、历史 execution log 或发布范围，不新增跨请求缓存、waiver、ledger 或第二套 readiness 状态机。

**治理闭包**：PR #201 只允许从 `certify` 自动回退 `stabilize` 这一次。完成上述状态矩阵和真实规模预认证后才能重新冻结 HEAD 并请求认证；冻结前只做一次必要 continuity 更新，冻结后不得再写 tracked handoff/truth。该认证 clean 且同 HEAD required checks 仍绿才允许合并。认证失败直接保留候选 No-Go，不再追加例外。
