---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
  - "specs/071-frontend-p1-visual-a11y-foundation-baseline/spec.md"
  - "specs/137-frontend-p1-visual-a11y-runtime-foundation-closure-baseline/spec.md"
  - "specs/095-frontend-mainline-product-delivery-baseline/spec.md"
  - "specs/143-frontend-mainline-browser-gate-real-probe-runtime-baseline/spec.md"
  - "specs/144-frontend-mainline-host-remediation-and-workspace-integration-closure-baseline/spec.md"
  - "specs/147-frontend-p2-page-ui-schema-baseline/spec.md"
  - "specs/148-frontend-p2-multi-theme-token-governance-baseline/spec.md"
---
# 任务分解：Frontend P2 Quality Platform Baseline

**编号**：`149-frontend-p2-quality-platform-baseline` | **日期**：2026-04-16
**来源**：plan.md + spec.md（FR-149-001 ~ FR-149-020 / SC-149-001 ~ SC-149-006）

---

## 分批策略

```text
Batch 1: Track C capability boundary and delivered/deferred honesty freeze
Batch 2: future runtime decomposition and downstream handoff freeze
Batch 3: development summary, docs-only validation, truth handoff readiness
```

---

## 执行护栏

- `149` 当前只允许 docs-only formal baseline freeze，不得进入 `src/` / `tests/`。
- `149` 不得重做 `071/137` visual/a11y foundation，也不得把 `095/143/144` 已完成的 runtime 底座重新包装成当前缺口。
- `149` 必须直接承认 `147`、`148` 已是 Track C 的共享 schema/theme truth，不得另起第二套输入面。
- `149` 不得抢跑 `cross-provider consistency`、`provider expansion`、React exposure 或开放 style editor runtime。
- `149` 只允许引用外部 design docs，不得在 `docs/superpowers/*` 新建第二套 canonical docs。
- 只有在 `149` docs-only 门禁通过且用户继续要求推进时，才允许进入 downstream runtime implementation。
- Track C runtime 继续遵守一工单一分支；在 quality verdict/evidence contract 未冻结前，不得抢跑 Track D consistency certification。

## Batch 1：Track C capability boundary and delivered/deferred honesty freeze

### Task 1.1 冻结 Track C 的完整能力集合

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/149-frontend-p2-quality-platform-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 至少明确 `visual regression`、`complete a11y platform`、`interaction quality`、`multi-browser/multi-device matrix`
  2. `spec.md` 明确这些能力来自 `145 Track C`，不是临时会话推断
  3. 当前 capability set 不再遗漏顶层设计中明示的 Track C 内容
- **验证**：`145` 与 related docs 对账

### Task 1.2 冻结 delivered / deferred boundary honesty

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/149-frontend-p2-quality-platform-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `071/137` 已承接 foundation，`095/143/144` 已承接 runtime substrate
  2. `spec.md` 不再把 foundation/runtime substrate 误报成当前缺口
  3. delivered 与 deferred 的边界可直接被 reviewer 读取
- **验证**：相关 formal docs 对账 review

## Batch 2：future runtime decomposition and downstream handoff freeze

### Task 2.1 冻结 Track C future runtime slices

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/149-frontend-p2-quality-platform-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 明确 `models -> artifact/evidence -> validator/matrix -> ProgramService/CLI/verify -> truth refresh` 的推荐顺序
  2. `plan.md` 明确 Track C 与 `071/137/095/143/144/147/148` 的 owner boundary
  3. `plan.md` 明确哪些问题暂时不阻塞 `149`
- **验证**：runtime slice review

### Task 2.2 冻结 Track D handoff 与禁止跨层改写边界

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/149-frontend-p2-quality-platform-baseline/spec.md`, `specs/149-frontend-p2-quality-platform-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 与 `plan.md` 都明确 Track D 只消费 Track C 的 quality verdict/evidence handoff
  2. 文档中明确禁止 Track C 顺手实现 consistency certification 或 provider expansion
  3. future artifact/handoff root 与 machine-verifiable schema 有明确位置
- **验证**：formal docs consistency review

## Batch 3：development summary, docs-only validation, truth handoff readiness

### Task 3.1 初始化 execution log 与 development summary

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T22
- **文件**：`specs/149-frontend-p2-quality-platform-baseline/task-execution-log.md`, `specs/149-frontend-p2-quality-platform-baseline/development-summary.md`
- **可并行**：否
- **验收标准**：
  1. execution log 明确记录本批是 docs-only Track C planning freeze
  2. development summary 诚实声明本次收口的是 planning truth，而不是 quality runtime code
  3. 两份文档都能被后续 close-check / global truth 消费
- **验证**：execution log / development summary review

### Task 3.2 运行 docs-only 门禁并确认 close-check readiness

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`specs/149-frontend-p2-quality-platform-baseline/spec.md`, `specs/149-frontend-p2-quality-platform-baseline/plan.md`, `specs/149-frontend-p2-quality-platform-baseline/tasks.md`, `specs/149-frontend-p2-quality-platform-baseline/task-execution-log.md`, `specs/149-frontend-p2-quality-platform-baseline/development-summary.md`
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 通过
  2. `python -m ai_sdlc workitem close-check --wi specs/149-frontend-p2-quality-platform-baseline` 通过
  3. `git diff --check` 通过
- **验证**：`uv run ai-sdlc verify constraints`、`python -m ai_sdlc workitem close-check --wi specs/149-frontend-p2-quality-platform-baseline`、`git diff --check`

### Task 3.3 确认 truth handoff readiness

- **任务编号**：T33
- **优先级**：P1
- **依赖**：T32
- **文件**：`program-manifest.yaml`（如执行 truth sync）、`specs/149-frontend-p2-quality-platform-baseline/development-summary.md`
- **可并行**：否
- **验收标准**：
  1. `149` 已可作为 global truth 中“后续 Track C 主线”的 canonical planning input
  2. downstream runtime 不再需要重做 Track C capability census
  3. 当前 batch 不伪造任何 quality runtime implementation complete 结论
- **验证**：program truth refresh / docs review

## 后续进入执行前的前提

- 用户明确要求继续 `149` runtime implementation
- `149` 已通过 docs-only 门禁
- Track C runtime 仍需按照 `models -> artifact/evidence -> validator/matrix -> ProgramService/CLI/verify` 顺序推进
- `149` 之后的下一条前端主线默认遵循 `Track D -> Track E`
