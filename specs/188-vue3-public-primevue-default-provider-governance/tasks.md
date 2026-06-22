---
related_doc:
  - "docs/vue3-public-primevue-default-provider-prd.zh-CN.md"
  - "docs/Vue3企业级前端开发规范方案.md"
---
# 任务分解：Vue3 public-primevue default provider governance

**编号**：`188-vue3-public-primevue-default-provider-governance` | **日期**：2026-06-22  
**来源**：plan.md + spec.md + PRD

## Batch 1：formal baseline and PRD decomposition

### Task 1.1 Freeze Vue3 default provider governance formal docs

- task_id: T11
- status: done
- scope:
  - docs/vue3-public-primevue-default-provider-prd.zh-CN.md
  - specs/188-vue3-public-primevue-default-provider-governance/spec.md
  - specs/188-vue3-public-primevue-default-provider-governance/plan.md
  - specs/188-vue3-public-primevue-default-provider-governance/tasks.md
  - specs/188-vue3-public-primevue-default-provider-governance/task-execution-log.md
- acceptance:
  - PRD is decomposed into formal spec, implementation plan, executable tasks, and execution log.
  - Formal docs preserve the three adversarial review conclusions.
  - No implementation code is changed in Batch 1.
- verify:
  - git diff --check
  - uv run ai-sdlc handoff update

## Batch 2：solution confirmation default switch

### Task 2.1 Switch default recommendation to vue3/public-primevue

- task_id: T21
- status: done
- depends:
  - T11
- scope:
  - src/ai_sdlc/core/program_service.py
  - src/ai_sdlc/models/frontend_solution_confirmation.py
  - src/ai_sdlc/cli/program_cmd.py
  - tests/unit/test_frontend_solution_confirmation_artifacts.py
  - tests/unit/test_verify_constraints.py
  - tests/integration/test_cli_program.py
- acceptance:
  - Default solution confirmation recommends `frontend_stack=vue3`, `provider_id=public-primevue`, `style_pack_id=modern-saas`.
  - `enterprise_provider_eligible=True` does not switch ordinary default recommendation back to `enterprise-vue2`.
  - `enterprise_provider_eligible=False` remains compatible with the same Vue3 default.
  - Explicit `enterprise-vue2` request preserves `vue2/enterprise-vue2` and availability/preflight diagnostics.
- verify:
  - uv run pytest tests/unit/test_frontend_solution_confirmation_artifacts.py tests/integration/test_cli_program.py -q
  - uv run pytest tests/unit/test_verify_constraints.py -q

## Batch 3：Vue3 template dependency and generation baseline

### Task 3.1 Split provider core packages and template dependencies

- task_id: T31
- status: done
- depends:
  - T21
- scope:
  - src/ai_sdlc/models/frontend_solution_confirmation.py
  - src/ai_sdlc/core/program_service.py
  - providers/frontend/public-primevue/provider.manifest.yaml
  - tests/unit/test_managed_delivery_apply.py
  - tests/unit/test_frontend_solution_confirmation_artifacts.py
- acceptance:
  - Provider core packages remain `primevue` and `@primeuix/themes`.
  - Template runtime dependencies include `vue-router`, `pinia`, `axios`, `vue-i18n`, `@vueuse/core`, `dayjs`.
  - Template dev dependencies include `typescript`, `vite`, `unocss`, `vitest`.
  - `primeicons` is not treated as a default required dependency in this work item.
- verify:
  - uv run pytest tests/unit/test_managed_delivery_apply.py tests/unit/test_frontend_solution_confirmation_artifacts.py -q

### Task 3.2 Generate PrimeVue + UnoCSS + CSS Variables template

- task_id: T32
- status: done
- depends:
  - T31
- scope:
  - src/ai_sdlc/core/program_service.py
  - src/frontend-governance/runtime/providers/public-primevue/ProviderAdapter.tsx
  - providers/frontend/public-primevue/mappings.yaml
  - providers/frontend/public-primevue/whitelist.yaml
  - tests/unit/test_managed_delivery_apply.py
  - tests/fixtures/
- acceptance:
  - Generated Vue3 frontend includes Vite entry, PrimeVue plugin/theme initialization, `uno.config.ts`, `src/styles/variables.css`, `src/styles/primevue.css`, and `src/styles/main.css`.
  - Generated structure includes `api/`, `components/base/`, `components/business/`, `components/layout/`, `composables/`, `router/modules/`, `stores/`, `styles/`, `types/`, `utils/`, `views/`.
  - Generated smoke page or validation page covers Button, Table, Dialog, and Form through Ui/Base components.
- verify:
  - uv run pytest tests/unit/test_managed_delivery_apply.py -q
  - uv run ruff check src/ai_sdlc/core/program_service.py tests/unit/test_managed_delivery_apply.py

## Batch 4：governance validation and import boundary

### Task 4.1 Add public-primevue import boundary verification

- task_id: T41
- status: done
- depends:
  - T32
- scope:
  - src/ai_sdlc/core/verify_constraints.py
  - src/ai_sdlc/core/program_service.py
  - tests/unit/test_verify_constraints.py
  - tests/fixtures/frontend-contract-sample-src/
- acceptance:
  - `src/views/` and `src/components/business/` direct `primevue/*` imports are detected.
  - Provider adapter, theme bridge, `components/base/`, and marked provider fixtures are allowed.
  - First version reports this boundary as warning or equivalent non-blocking evidence.
- verify:
  - uv run pytest tests/unit/test_verify_constraints.py -q
  - uv run ai-sdlc verify constraints

### Task 4.2 Add validation level reporting for Vue3 default provider

- task_id: T42
- status: done
- depends:
  - T41
- scope:
  - src/ai_sdlc/core/verify_constraints.py
  - src/ai_sdlc/core/program_service.py
  - tests/unit/test_verify_constraints.py
- acceptance:
  - Default provider drift, explicit enterprise Vue2 silent switch, generation mismatch, and missing key template files are blocker.
  - Import boundary, visual structure, and basic a11y findings are warning.
  - ESLint/Prettier/Playwright/husky/lint-staged/commitlint missing configuration remains advisory for this work item.
- verify:
  - uv run pytest tests/unit/test_verify_constraints.py -q
  - uv run ai-sdlc verify constraints

## Batch 5：Web smoke blocker

### Task 5.1 Implement Vue3 public-primevue Web smoke runner

- task_id: T51
- status: done
- depends:
  - T42
- scope:
  - src/ai_sdlc/core/program_service.py
  - src/ai_sdlc/core/frontend_browser_gate_runtime.py
  - tests/integration/
  - tests/unit/test_managed_delivery_apply.py
- acceptance:
  - Generated Vue3 frontend can start a Vite dev server in smoke mode.
  - Smoke opens root route or default route and verifies nonblank render.
  - Smoke captures fatal console errors and treats them as blocker.
  - Smoke proves PrimeVue, UnoCSS, and CSS Variables are active in the rendered page.
- verify:
  - uv run pytest tests/unit/test_managed_delivery_apply.py -q
  - uv run pytest tests/integration -k "frontend and smoke" -q

## Batch 6：visual and accessibility evidence

### Task 6.1 Produce desktop/mobile visual evidence

- task_id: T61
- status: done
- depends:
  - T51
- scope:
  - src/ai_sdlc/core/frontend_browser_gate_runtime.py
  - src/ai_sdlc/core/program_service.py
  - tests/integration/
  - governance/frontend/
- acceptance:
  - Visual evidence includes screenshots for `1440x900` and `390x844`.
  - Metadata includes provider, style pack, viewport, timestamp, generation entry, and smoke result.
  - Blank screenshot, missing main content, obvious overlap, or severe clipping is warning in first version.
  - Evidence format can support future pixel diff or visual structure diff blocker.
- verify:
  - uv run pytest tests/integration -k "visual or browser_gate" -q

### Task 6.2 Capture basic interaction and accessibility warning evidence

- task_id: T62
- status: done
- depends:
  - T61
- scope:
  - src/ai_sdlc/core/frontend_browser_gate_runtime.py
  - tests/integration/
  - governance/frontend/
- acceptance:
  - Button, Input, Select, Dialog, Form smoke checks produce structured warning evidence.
  - Dialog open/close and focus return issues are reported.
  - Missing label or aria equivalent for form controls is reported.
  - Keyboard focus visibility issues are reported.
- verify:
  - uv run pytest tests/integration -k "a11y or browser_gate" -q

## Batch 7：documentation and release truth

### Task 7.1 Align docs, release notes, and user guidance

- task_id: T71
- status: done
- depends:
  - T62
- scope:
  - README.md
  - USER_GUIDE.zh-CN.md
  - docs/releases/
  - docs/vue3-public-primevue-default-provider-prd.zh-CN.md
  - docs/Vue3企业级前端开发规范方案.md
  - src/ai_sdlc/rules/pipeline.md
  - tests/unit/test_verify_constraints.py
- acceptance:
  - User-facing docs say default Vue3 provider is `public-primevue`.
  - Docs explain how to explicitly choose `enterprise-vue2`.
  - Docs explain Web smoke blocker and visual/a11y warning evidence.
  - Release notes identify default provider switch as user-visible behavior.
- verify:
  - uv run ai-sdlc verify constraints
  - uv run ruff check src tests

## Close criteria

- All blocker-level tests pass.
- Web smoke evidence exists for generated Vue3 default frontend.
- Visual and accessibility warnings are structured and non-silent.
- `enterprise-vue2` explicit path remains tested.
- Handoff and task-execution-log include commands, results, risks, and exact next steps.

## Close-out evidence

- status: complete
- PR: https://github.com/sinclairpan-git/Ai_AutoSDLC/pull/84
- merge_commit: `e97c10c583c5208ecb780bc7d7d88fce37e97489`
- merged_at: 2026-06-22T10:45:08Z
- final_review: Codex review on head `4c15536` reported no major issues.
- final_checks: GitHub Compatibility Gate, Cross Platform Validation, Upgrade, Windows Shell Smoke, core-smoke, smoke, and verify checks passed.
- closeout_note: Batch 1-7 tasks are complete; no remaining implementation task is open under this work item.
