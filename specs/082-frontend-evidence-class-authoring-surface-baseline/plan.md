# 执行计划：Frontend Evidence Class Authoring Surface Baseline

**功能编号**：`082-frontend-evidence-class-authoring-surface-baseline`  
**创建日期**：2026-04-08  
**状态**：docs-only prospective authoring surface

## 1. 目标与定位

`082` 的目标是把 `081` 中“future item 必须声明 evidence class”的抽象 contract，进一步落成一个唯一、固定、可被 future parser 读取的 authoring surface。它只冻结 authoring truth，不改变当前 runtime。

## 2. 范围

### 2.1 In Scope

- 创建 `082` formal docs 与 execution log
- 推进 `.ai-sdlc/project/config/project-state.yaml` 到 `82`
- 冻结 canonical key 为 `frontend_evidence_class`
- 冻结 declaration location 为 `spec.md` footer metadata
- 冻结 allowed values、invalid cases、mirror priority

### 2.2 Out Of Scope

- 修改 `program-manifest.yaml` 或模板
- 为既有 spec 回填 `frontend_evidence_class`
- 修改 `src/` / `tests/` 或实现 parser / validator
- 修改 `frontend-program-branch-rollout-plan.md`
- retroactively 改义 `068` ~ `071`

## 3. 变更文件面

当前批次只允许改以下文件面：

- `specs/082-frontend-evidence-class-authoring-surface-baseline/spec.md`
- `specs/082-frontend-evidence-class-authoring-surface-baseline/plan.md`
- `specs/082-frontend-evidence-class-authoring-surface-baseline/tasks.md`
- `specs/082-frontend-evidence-class-authoring-surface-baseline/task-execution-log.md`
- `.ai-sdlc/project/config/project-state.yaml`

## 4. Contract Rules

### 4.1 Canonical surface

- future frontend item 必须在 `spec.md` footer metadata 中声明 `frontend_evidence_class`
- body prose、plan、tasks、execution log 中的文本不构成正式声明

### 4.2 Allowed values

- `framework_capability`
- `consumer_adoption`

### 4.3 Invalid authoring cases

- 缺失键
- 空值
- 非法值
- 大小写 / 分隔符变体
- 重复键
- footer 与正文冲突

### 4.4 Source-of-truth rule

- `spec.md` footer 是 primary truth
- future manifest field 若出现，只能是 mirror
- mirror 与 spec footer 冲突时，spec footer 优先

## 5. 分阶段计划

### Phase 0：truth alignment

- 回读 `081`
- 只读检查 `program-manifest.yaml` 与模板，确认当前没有现成字段可复用
- 选择最小 authoring surface 为 spec-local footer metadata

### Phase 1：authoring contract freeze

- 新建 `082` formal docs
- 写清 declaration location、key 名、allowed values 与 authoring error semantics
- 写清 manifest mirror 与 spec footer 的优先级

### Phase 2：verification and archive

- 运行 docs-only / read-only 验证
- 记录当前 runtime truth 未发生变化
- 归档 commit

## 6. 最小验证策略

- `uv run ai-sdlc verify constraints`
- `uv run ai-sdlc program status`
- `git diff --check -- .ai-sdlc/project/config/project-state.yaml specs/082-frontend-evidence-class-authoring-surface-baseline`

## 7. 回滚原则

- 如果 `082` 让人误以为当前 runtime 已经读取 `frontend_evidence_class`，必须回退
- 如果 `082` 让人误以为 manifest 已是 source of truth，必须回退
- 如果本轮误改 `program-manifest.yaml`、`src/`、`tests/` 或既有 spec，必须回退
