# 执行计划：Frontend Contract Observation Backfill Playbook Baseline

**功能编号**：`077-frontend-contract-observation-backfill-playbook-baseline`  
**创建日期**：2026-04-08  
**状态**：docs-only external backfill playbook freeze

## 1. 目标与定位

`077` 的目标不是消除 blocker 本身，而是冻结“如何诚实消除 blocker”的执行面。当前仓库已经有：

- artifact schema / writer / loader
- scanner candidate 与 CLI export
- runtime attachment / gate failure semantics

但仍缺一份面向 operator 的 canonical playbook，来说明：

- 应该在哪个外部源码根上跑 scanner
- 目标 spec 目录怎么选
- annotation 长什么样
- 回填后如何验证，不把 empty artifact 或 drift 误判成 clean

## 2. 范围

### 2.1 In Scope

- 创建 `077` formal docs 与 execution log
- 推进 `.ai-sdlc/project/config/project-state.yaml` 到 `77`
- 冻结当前 external backfill 的 prerequisites、command surface、target list 与 validation sequence

### 2.2 Out Of Scope

- 实际接入外部 frontend 仓库并生成 artifact
- 修改 `program-manifest.yaml`、root rollout wording 或任何 active spec 正文
- 修改 `src/` / `tests/` 来扩张 scanner、CLI 或 gate 能力

## 3. 变更文件面

当前批次只允许改以下文件面：

- `specs/077-frontend-contract-observation-backfill-playbook-baseline/spec.md`
- `specs/077-frontend-contract-observation-backfill-playbook-baseline/plan.md`
- `specs/077-frontend-contract-observation-backfill-playbook-baseline/tasks.md`
- `specs/077-frontend-contract-observation-backfill-playbook-baseline/task-execution-log.md`
- `.ai-sdlc/project/config/project-state.yaml`

## 4. Canonical Playbook Freeze

### 4.1 前置条件

- 必须拿到真实 frontend implementation source root
- 该 source root 中，目标页面实现文件必须已嵌入结构化 annotation block
- operator 必须知道回填目标 spec 目录，而不是把 artifact 丢到 root 或临时目录
- `generated_at` 必须使用显式 UTC timestamp

### 4.2 Annotation 合同

当前 scanner 只接受带 marker 的结构化注释块：

```ts
/* ai-sdlc:frontend-contract-observation
{
  "page_id": "user-create",
  "recipe_id": "form-create",
  "i18n_keys": ["user.create.submit"],
  "validation_fields": ["username"],
  "new_legacy_usages": []
}
*/
```

或：

```html
<!-- ai-sdlc:frontend-contract-observation
{
  "page_id": "user-create",
  "recipe_id": "form-create",
  "i18n_keys": ["user.create.submit"],
  "validation_fields": ["username"]
}
-->
```

约束：

- `page_id` 与 `recipe_id` 必填
- 同一 source root 内 duplicate `page_id` 直接失败
- annotation payload 必须是合法 JSON object
- 支持后缀仅限 `.js/.jsx/.ts/.tsx/.vue/.mjs/.cjs`

### 4.3 标准导出命令

在本仓库根目录执行：

```bash
uv run ai-sdlc scan /ABS/FRONTEND_SOURCE_ROOT \
  --frontend-contract-spec-dir /Users/sinclairpan/project/Ai_AutoSDLC/specs/<TARGET_SPEC_DIR> \
  --frontend-contract-generated-at 2026-04-08T12:00:00Z
```

成功输出应包含：

- `Frontend contract observations exported: <n> observations -> <artifact_path>`

当前 CLI export 的事实边界：

- 会写入 canonical `frontend-contract-observations.json`
- 会携带 `provider_kind=scanner`、`provider_name=frontend_contract_scanner`
- 会生成 `source_digest`
- 当前不会通过 CLI 参数写入 `source_revision`

### 4.4 当前 first-wave target list

本轮只冻结以下 target spec：

- `specs/068-frontend-p1-page-recipe-expansion-baseline`
- `specs/069-frontend-p1-governance-diagnostics-drift-baseline`
- `specs/070-frontend-p1-recheck-remediation-feedback-baseline`
- `specs/071-frontend-p1-visual-a11y-foundation-baseline`

`077` 不判断它们各自应该对应哪一个外部 frontend 仓库目录；这一步必须由实际实现所有者按真实页面覆盖面决定。

## 5. 回填后的最小验证策略

对每个已回填 spec，最小只读验证序列为：

1. `uv run ai-sdlc verify constraints`
2. `uv run ai-sdlc program status`
3. 必要时定向查看目标 spec 下的 `frontend-contract-observations.json`

判定规则：

- 文件缺失：仍是 `missing_artifact`
- JSON / schema 非法：进入 `invalid_artifact`
- `observations` 为空：仍失败，消息为 `observation artifact attached but declared no implementation observations`
- payload 与 contract artifact 不匹配：进入 drift 语义，不是 clean

## 6. 非法捷径清单

- 不允许用 `tests/fixtures/frontend-contract-sample-src/` 充当真实业务实现来源
- 不允许手写自由 JSON 绕过 canonical scanner/provider contract
- 不允许只因为 artifact 文件存在就宣称 spec 已 unblock
- 不允许把 `077` 自己当作 root close-sync 或 implementation carrier

## 7. 分阶段计划

### Phase 0：truth and scope freeze

- 冻结 `077` 只是一份 playbook baseline
- 冻结当前 blocker 仍是外部 observation artifact gap

### Phase 1：operator checklist freeze

- 冻结前置条件、annotation 样式、导出命令与 target list
- 冻结 failure semantics 与非法捷径边界

### Phase 2：execution log and validation

- 创建 `077` canonical docs 与 execution log
- 将 `next_work_item_seq` 从 `76` 推进到 `77`
- 跑 docs-only / read-only 验证

## 8. 最小验证策略

- `uv run ai-sdlc verify constraints`
- `uv run ai-sdlc program status`
- `git diff --check`

## 9. 回滚原则

- 如果 `077` 文档把 sample fixture 写成真实 backfill 来源，必须回退
- 如果 `077` 文档把 empty observation artifact 写成可通过 gate，必须回退
- 如果本轮误改 root rollout wording、manifest、`src/` 或 `tests/`，必须回退
---
related_doc:
  - "frontend-program-branch-rollout-plan.md"
  - "specs/012-frontend-contract-verify-integration/plan.md"
  - "specs/013-frontend-contract-observation-provider-baseline/spec.md"
  - "src/ai_sdlc/core/frontend_contract_observation_provider.py"
  - "src/ai_sdlc/scanners/frontend_contract_scanner.py"
  - "src/ai_sdlc/core/frontend_contract_runtime_attachment.py"
  - "src/ai_sdlc/gates/frontend_contract_gate.py"
  - "src/ai_sdlc/cli/commands.py"
---
