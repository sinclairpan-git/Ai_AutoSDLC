# 功能规格：Frontend Solution Confirm Continue Apply Orchestration Baseline

**功能编号**：`165-frontend-solution-confirm-continue-apply-orchestration-baseline`  
**状态**：已实现（2026-04-19）  
**创建日期**：`2026-04-19`

## 1. 背景

当前 `program solution-confirm --execute --yes` 只会物化 `solution_snapshot` 与 provider/style artifacts，不会自动进入 managed delivery apply。与此同时，`managed-delivery-apply` 已经拥有独立的 request / execute / artifact truth，但它和 `solution-confirm` 之间缺少一条显式、诚实、可审计的组合编排链。

现有实现问题：

1. 用户容易把“确认方案”误读为“已经接入/已经安装”。
2. `requested_*` 与 `effective_*` 存在偏差时，缺少强制性的二次确认语义。
3. apply 结果真值和 solution snapshot 真值仍然靠人工心智分层，没有统一入口。
4. `program managed-delivery-apply` 在省略 `--request`、直接从 current truth 物化 request 时，必须继承同样的 effective-change 二次确认门槛，不能绕开组合流已建立的确认标准。

## 2. 目标

为 `program solution-confirm` 增加一个显式组合流：

`program solution-confirm --execute --continue --yes`

该组合流必须：

1. 先持久化 solution confirmation truth；
2. 再显式进入 managed delivery apply；
3. 将 apply 结果写入独立 artifact；
4. 对 `requested_* != effective_*` 的情况要求额外确认；
5. 保持 `solution-confirm --execute` 的默认语义不变。

## 3. 非目标

本基线不做以下事项：

1. 不把 `solution-confirm --execute` 静默升级为默认 mutation 命令；
2. 不把 apply 结果回写进 `FrontendSolutionSnapshot`；
3. 不把 `adapter_packages` 从显式空列表升级为独立 adapter package truth；
4. 不新增 browser gate、workspace integration 默认开启或 root takeover 语义；
5. 不把固定对抗代理工作流写入框架版本内容。

## 4. 关键决策

### 4.1 真值分层

- `FrontendSolutionSnapshot` 继续只表达确认真值；
- `frontend-managed-delivery/latest.yaml` 继续表达 apply request 真值；
- `frontend-managed-delivery-apply/latest.yaml` 继续表达 apply result 真值。

三者必须通过 source linkage 串联，不得混写。

### 4.2 二次确认语义

当 `requested_*` 与 `effective_*` 任一字段不一致时，`--continue` 不足以授权进入 apply。

必须显式提供：

`--ack-effective-change`

该 flag 的语义是：用户确认接受 `effective_*` 与 `requested_*` 的差异本身，而不是只确认发生了 fallback。

### 4.3 adapter truth 边界

当前层仍保持：

- `install_strategy.packages` 是唯一正式安装包真值；
- `provider_theme_adapter_config.adapter_id` 是正式 bridge truth；
- `adapter_packages` 继续显式为空列表。

理由：`152` 已将独立 adapter package 放到 `2+ project validation` 之后，当前层不得提前把 adapter package 抬升成 install truth。

## 5. 功能需求

| ID | 需求 |
|----|------|
| FR-165-001 | 系统必须提供 `program solution-confirm --execute --continue --yes` 组合流，在 solution confirmation 成功后显式进入 managed delivery apply |
| FR-165-002 | 组合流必须先持久化 `solution_snapshot`，再物化 apply request，再执行 apply，再写 apply artifact |
| FR-165-003 | `solution-confirm --execute` 在未提供 `--continue` 时必须保持现有行为不变 |
| FR-165-004 | 当 `requested_* != effective_*` 时，未提供 `--ack-effective-change` 不得继续进入 apply |
| FR-165-005 | 组合流必须复用现有 managed delivery apply request/executor/artifact 链路，不得在 `solution-confirm` 内重写 executor |
| FR-165-006 | CLI 必须显式区分“方案确认已落盘”和“apply 已执行”的输出文案，不得把两者混成单一完成态 |
| FR-165-007 | apply blocked / pending-browser-gate / manual-recovery 等结果必须继续写入独立 apply artifact，并以诚实状态返回给 CLI |
| FR-165-008 | 本基线不得把 `adapter_packages` 从空数组升级为独立 package 安装真值；相关 future work 必须留给后续 runtime carrier baseline |
| FR-165-009 | 当 `program managed-delivery-apply` 省略 `--request`、从 current truth 自动物化 request 且 `requested_* != effective_*` 时，系统必须要求 `--ack-effective-change` 后才允许 execute |
| FR-165-010 | `FR-165-009` 只适用于 truth-derived request 入口；显式提供 `--request` 的回放路径不得被额外注入新确认门槛 |

## 6. 验收场景

1. **Given** 用户执行 `program solution-confirm --execute --yes`，**When** 未提供 `--continue`，**Then** 系统只写 solution confirmation artifacts，不进入 apply。
2. **Given** 用户执行 `program solution-confirm --enterprise-provider-ineligible --execute --continue --yes`，**When** requested/effective 无差异且 host/apply prerequisites 满足，**Then** 系统写出 solution artifact 与 apply artifact，并返回 apply result。
3. **Given** 用户执行 `program solution-confirm --execute --continue --yes` 且 `requested_* != effective_*`，**When** 未提供 `--ack-effective-change`，**Then** 系统只写 solution artifact，并以明确文案阻止进入 apply。
4. **Given** 用户执行 `program solution-confirm --execute --continue --yes` 且 enterprise registry prerequisite 缺失，**When** solution confirmation 已成功，**Then** 系统必须写出独立 apply artifact 并诚实返回 blocked 状态，而不是伪装成已完成接入。
5. **Given** 用户执行 `program managed-delivery-apply --execute --yes` 且省略 `--request`，**When** current truth 中 `requested_* != effective_*`，**Then** 系统必须要求 `--ack-effective-change`，不得静默执行。

## 7. 影响文件

- `src/ai_sdlc/cli/program_cmd.py`
- `src/ai_sdlc/core/program_service.py`
- `tests/integration/test_cli_program.py`
- `tests/unit/test_program_service.py`

---
related_doc:
  - "src/ai_sdlc/cli/program_cmd.py"
  - "src/ai_sdlc/core/program_service.py"
  - "tests/integration/test_cli_program.py"
  - "tests/unit/test_program_service.py"
  - "specs/073-frontend-p2-provider-style-solution-baseline/spec.md"
  - "specs/099-frontend-mainline-delivery-registry-resolver-baseline/spec.md"
  - "specs/101-frontend-mainline-managed-delivery-apply-runtime-baseline/spec.md"
  - "specs/123-frontend-mainline-managed-delivery-apply-runtime-implementation-baseline/spec.md"
  - "specs/152-frontend-p3-modern-provider-runtime-adapter-expansion-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
