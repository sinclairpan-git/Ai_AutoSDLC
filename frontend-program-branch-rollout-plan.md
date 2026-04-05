# Frontend Program 未实现项排序与分支落地计划

**更新日期**：2026-04-05
**适用范围**：所有 `specs/0xx-frontend-*` work item
**机器真值**：根级 `program-manifest.yaml`；本文件用于说明排序口径、并行窗口与建议分支命名。

## 口径

- `program-manifest.yaml` 是后续 `program validate/status/plan/integrate` 与逐项开分支落地的唯一机器真值。
- 本文件把 manifest 的 DAG 拓扑序、人读状态口径与建议 branch slug 汇总成一张表，方便逐项执行。
- Tier 编号与 `uv run ai-sdlc program plan` 保持一致，采用 `0` 起始。
- 排序优先遵循依赖闭包；同层若无依赖关系，则按 spec 编号升序处理。

## 执行规则

- 默认一项一分支，建议命名为 `codex/<branch_slug>`。
- 只有在“有限并行窗口”中列出的 tier 内项目，才建议并行开分支；其余按主线串行推进。
- 每次分支落地前，先以根级 manifest 重新跑 `uv run ai-sdlc program plan`，确认依赖未漂移。
- docs-only baseline 也保留独立分支位次，避免把冻结基线与后续消费实现混在同一次 close-out。

## 主线分段

- 合同与观测基础：`009` -> `018`
- program orchestration / execute / remediation 主链：`019` -> `046`
- final proof archive 与 cleanup 主链：`047` -> `064`

## 有限并行窗口

- Tier 2: `012`, `015` 可并行，前提是该 tier 之前的依赖层已完成。
- Tier 3: `013`, `016` 可并行，前提是该 tier 之前的依赖层已完成。
- Tier 4: `014`, `017` 可并行，前提是该 tier 之前的依赖层已完成。

## 排序总表

- #01 | Tier 00 | `009` | branch `codex/frontend-governance-ui-kernel` | 直接依赖：无 | 状态：已冻结（formal baseline）
- #02 | Tier 01 | `011` | branch `codex/frontend-contract-authoring-baseline` | 直接依赖：`009` | 状态：已冻结（formal baseline）
- #03 | Tier 02 | `012` | branch `codex/frontend-contract-verify-integration` | 直接依赖：`009`、`011` | 状态：已冻结（formal baseline）
- #04 | Tier 03 | `013` | branch `codex/frontend-contract-observation-provider-baseline` | 直接依赖：`009`、`011`、`012` | 状态：已冻结（formal baseline）
- #05 | Tier 04 | `014` | branch `codex/frontend-contract-runtime-attachment-baseline` | 直接依赖：`009`、`011`、`012`、`013` | 状态：已冻结（formal baseline）
- #06 | Tier 02 | `015` | branch `codex/frontend-ui-kernel-standard-baseline` | 直接依赖：`009`、`011` | 状态：已冻结（formal baseline）
- #07 | Tier 03 | `016` | branch `codex/frontend-enterprise-vue2-provider-baseline` | 直接依赖：`009`、`015` | 状态：已冻结（formal baseline）
- #08 | Tier 04 | `017` | branch `codex/frontend-generation-governance-baseline` | 直接依赖：`009`、`015`、`016` | 状态：已冻结（formal baseline）
- #09 | Tier 05 | `018` | branch `codex/frontend-gate-compatibility-baseline` | 直接依赖：`009`、`017` | 状态：已冻结（formal baseline）
- #10 | Tier 06 | `019` | branch `codex/frontend-program-orchestration-baseline` | 直接依赖：`009`、`014`、`018` | 状态：已冻结（formal baseline）
- #11 | Tier 07 | `020` | branch `codex/frontend-program-execute-runtime-baseline` | 直接依赖：`009`、`014`、`018`、`019` | 状态：已冻结（formal baseline）
- #12 | Tier 08 | `021` | branch `codex/frontend-program-remediation-runtime-baseline` | 直接依赖：`018`、`019`、`020` | 状态：已冻结（formal baseline）
- #13 | Tier 09 | `022` | branch `codex/frontend-governance-materialization-runtime-baseline` | 直接依赖：`017`、`018`、`021` | 状态：已冻结（formal baseline）
- #14 | Tier 10 | `023` | branch `codex/frontend-program-bounded-remediation-execute-baseline` | 直接依赖：`021`、`022` | 状态：已冻结（formal baseline）
- #15 | Tier 11 | `024` | branch `codex/frontend-program-bounded-remediation-writeback-baseline` | 直接依赖：`023` | 状态：已冻结（formal baseline）
- #16 | Tier 12 | `025` | branch `codex/frontend-program-provider-handoff-baseline` | 直接依赖：`024` | 状态：已冻结（formal baseline）
- #17 | Tier 13 | `026` | branch `codex/frontend-program-guarded-provider-runtime-baseline` | 直接依赖：`025` | 状态：已冻结（formal baseline）
- #18 | Tier 14 | `027` | branch `codex/frontend-program-provider-runtime-artifact-baseline` | 直接依赖：`026` | 状态：已冻结（formal baseline）
- #19 | Tier 15 | `028` | branch `codex/frontend-program-provider-patch-handoff-baseline` | 直接依赖：`027` | 状态：已冻结（formal baseline）
- #20 | Tier 16 | `029` | branch `codex/frontend-program-guarded-patch-apply-baseline` | 直接依赖：`028` | 状态：已冻结（formal baseline）
- #21 | Tier 17 | `030` | branch `codex/frontend-program-provider-patch-apply-artifact-baseline` | 直接依赖：`029` | 状态：已冻结（formal baseline）
- #22 | Tier 18 | `031` | branch `codex/frontend-program-cross-spec-writeback-orchestration-baseline` | 直接依赖：`030` | 状态：已冻结（formal baseline）
- #23 | Tier 19 | `032` | branch `codex/frontend-program-cross-spec-writeback-artifact-baseline` | 直接依赖：`031` | 状态：已冻结（formal baseline）
- #24 | Tier 20 | `033` | branch `codex/frontend-program-guarded-registry-orchestration-baseline` | 直接依赖：`032` | 状态：已冻结（formal baseline）
- #25 | Tier 21 | `034` | branch `codex/frontend-program-guarded-registry-artifact-baseline` | 直接依赖：`033` | 状态：已冻结（formal baseline）
- #26 | Tier 22 | `035` | branch `codex/frontend-program-broader-governance-orchestration-baseline` | 直接依赖：`034` | 状态：已冻结（formal baseline）
- #27 | Tier 23 | `036` | branch `codex/frontend-program-broader-governance-artifact-baseline` | 直接依赖：`035` | 状态：已冻结（formal baseline）
- #28 | Tier 24 | `037` | branch `codex/frontend-program-final-governance-orchestration-baseline` | 直接依赖：`036` | 状态：已冻结（formal baseline）
- #29 | Tier 25 | `038` | branch `codex/frontend-program-final-governance-artifact-baseline` | 直接依赖：`037` | 状态：已冻结（formal baseline）
- #30 | Tier 26 | `039` | branch `codex/frontend-program-writeback-persistence-orchestration-baseline` | 直接依赖：`038` | 状态：已冻结（formal baseline）
- #31 | Tier 27 | `040` | branch `codex/frontend-program-writeback-persistence-artifact-baseline` | 直接依赖：`039` | 状态：已冻结（formal baseline）
- #32 | Tier 28 | `041` | branch `codex/frontend-program-persisted-write-proof-orchestration-baseline` | 直接依赖：`040` | 状态：已冻结（formal baseline）
- #33 | Tier 29 | `042` | branch `codex/frontend-program-persisted-write-proof-artifact-baseline` | 直接依赖：`041` | 状态：已冻结（formal baseline）
- #34 | Tier 30 | `043` | branch `codex/frontend-program-final-proof-publication-orchestration-baseline` | 直接依赖：`042` | 状态：已冻结（formal baseline）
- #35 | Tier 31 | `044` | branch `codex/frontend-program-final-proof-publication-artifact-baseline` | 直接依赖：`043` | 状态：已冻结（formal baseline）
- #36 | Tier 32 | `045` | branch `codex/frontend-program-final-proof-closure-orchestration-baseline` | 直接依赖：`044` | 状态：已冻结（formal baseline）
- #37 | Tier 33 | `046` | branch `codex/frontend-program-final-proof-closure-artifact-baseline` | 直接依赖：`045` | 状态：已冻结（formal baseline）
- #38 | Tier 34 | `047` | branch `codex/frontend-program-final-proof-archive-orchestration-baseline` | 直接依赖：`046` | 状态：已冻结（formal baseline）
- #39 | Tier 35 | `048` | branch `codex/frontend-program-final-proof-archive-artifact-baseline` | 直接依赖：`047` | 状态：已冻结（formal baseline）
- #40 | Tier 36 | `049` | branch `codex/frontend-program-final-proof-archive-thread-archive-baseline` | 直接依赖：`048` | 状态：已冻结（formal baseline）
- #41 | Tier 37 | `050` | branch `codex/frontend-program-final-proof-archive-project-cleanup-baseline` | 直接依赖：`049` | 状态：已冻结（formal baseline）
- #42 | Tier 38 | `051` | branch `codex/frontend-program-final-proof-archive-project-cleanup-mutation-baseline` | 直接依赖：`050` | 状态：已冻结（formal baseline）
- #43 | Tier 39 | `052` | branch `codex/frontend-program-final-proof-archive-explicit-cleanup-targets-baseline` | 直接依赖：`050`、`051` | 状态：已冻结（formal baseline）
- #44 | Tier 40 | `053` | branch `codex/frontend-program-final-proof-archive-cleanup-targets-consumption-baseline` | 直接依赖：`050`、`052` | 状态：已实现（consumption baseline）
- #45 | Tier 41 | `054` | branch `codex/frontend-program-final-proof-archive-cleanup-mutation-eligibility-baseline` | 直接依赖：`051`、`052`、`053` | 状态：已冻结（formal baseline）
- #46 | Tier 42 | `055` | branch `codex/frontend-program-final-proof-archive-cleanup-eligibility-consumption-baseline` | 直接依赖：`050`、`053`、`054` | 状态：已实现（eligibility consumption baseline）
- #47 | Tier 43 | `056` | branch `codex/frontend-program-final-proof-archive-project-cleanup-preview-plan-baseline` | 直接依赖：`050`、`054`、`055` | 状态：已冻结（formal baseline）
- #48 | Tier 44 | `057` | branch `codex/frontend-program-final-proof-archive-cleanup-preview-plan-consumption-baseline` | 直接依赖：`050`、`055`、`056` | 状态：已实现（preview plan consumption baseline）
- #49 | Tier 45 | `058` | branch `codex/frontend-program-final-proof-archive-cleanup-mutation-proposal-baseline` | 直接依赖：`050`、`052`、`054`、`056`、`057` | 状态：已冻结（docs-only mutation proposal baseline）
- #50 | Tier 46 | `059` | branch `codex/frontend-program-final-proof-archive-cleanup-mutation-proposal-consumption-baseline` | 直接依赖：`050`、`057`、`058` | 状态：已实现（mutation proposal consumption baseline）
- #51 | Tier 47 | `060` | branch `codex/frontend-program-final-proof-archive-cleanup-mutation-proposal-approval-baseline` | 直接依赖：`050`、`054`、`056`、`058`、`059` | 状态：已冻结（formal baseline）
- #52 | Tier 48 | `061` | branch `codex/frontend-program-final-proof-archive-cleanup-mutation-proposal-approval-consumption-baseline` | 直接依赖：`050`、`054`、`056`、`058`、`059`、`060` | 状态：已实现（mutation proposal approval consumption baseline）
- #53 | Tier 49 | `062` | branch `codex/frontend-program-final-proof-archive-cleanup-mutation-execution-gating-baseline` | 直接依赖：`050`、`054`、`056`、`058`、`060`、`061` | 状态：已冻结（formal baseline）
- #54 | Tier 50 | `063` | branch `codex/frontend-program-final-proof-archive-cleanup-mutation-execution-gating-consumption-baseline` | 直接依赖：`050`、`060`、`061`、`062` | 状态：已实现（execution gating consumption baseline）
- #55 | Tier 51 | `064` | branch `codex/frontend-program-final-proof-archive-cleanup-mutation-execution-baseline` | 直接依赖：`050`、`062`、`063` | 状态：已冻结（formal baseline）

## 备注

- `053`、`055`、`057`、`059`、`061`、`063` 属于已实现的 consumption/gating 项，后续如需补强，应仍以当前 DAG 位次为准，不要越过其 docs-only 前置项。
- `058`、`060`、`062`、`064` 目前仍是 mutation proposal / approval / gating / execution 主线上的关键冻结点，适合作为后续逐项开分支的优先补齐目标。
