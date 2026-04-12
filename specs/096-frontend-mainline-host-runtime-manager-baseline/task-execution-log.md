# 执行记录：Frontend Mainline Host Runtime Manager Baseline

## Batch 2026-04-12-001 | 状态检查与计划续接

### 1. 范围

- 对账当前仓库状态、spec 落点与 work item 序号；
- 判断当前应继续 `095` 还是 `096`；
- 为 `096` 补齐执行骨架：`plan.md`、`tasks.md`、`task-execution-log.md`。

### 2. 事实记录

- `project-state.yaml` 当前 `next_work_item_seq: 97`，说明 `096` 已编号但未进入实现闭环。
- `specs/093-*` 到 `specs/096-*` 目录当前都只有 `spec.md`，尚未补充计划与执行记录。
- `095` 是母规格；`096` 明确声明自己是 `095.Host Readiness` 的第一块 implementable slice。
- `src/ai_sdlc/cli/main.py` 当前只承载 CLI 装配，没有 Host Runtime Manager 对应命令面。
- `packaging/offline/install_offline.sh` 与 `packaging/offline/install_offline.ps1` 仍是人工可读安装入口，尚未进入 `host_runtime_plan` 契约。

### 3. 本批输出

- 新增 [`plan.md`](./plan.md)，固定 `096` 的目标、边界、批次与验证命令；
- 新增 [`tasks.md`](./tasks.md)，把实现拆成可勾选批次；
- 建立本执行记录，保存状态续接依据，便于后续批次直接衔接。

### 4. 决策

- 当前继续目标确定为 `096`，而不是直接把 `095` 展开为完整实现；
- 原因：`096` 的范围清晰、依赖明确，且与仓库现状匹配；`095` 目前仍应作为后续汇总契约存在。

### 5. 验证命令

```bash
git diff --check -- specs/096-frontend-mainline-host-runtime-manager-baseline/plan.md specs/096-frontend-mainline-host-runtime-manager-baseline/tasks.md specs/096-frontend-mainline-host-runtime-manager-baseline/task-execution-log.md
```

### 6. 验证结果

- `git diff --check -- specs/096-frontend-mainline-host-runtime-manager-baseline/plan.md specs/096-frontend-mainline-host-runtime-manager-baseline/tasks.md specs/096-frontend-mainline-host-runtime-manager-baseline/task-execution-log.md`：通过。
- `uv run ai-sdlc verify constraints`：通过，输出 `verify constraints: no BLOCKERs.`。

### 7. 当前结论

- `096` 已从“只有规格”推进到“可直接进入实现批次”的状态；
- 下一步应按 `Batch 1` 进入 TDD，先固定 `host_runtime_plan` 的契约与 fail-closed 语义；
- 本批没有引入功能代码，也没有改变运行时行为。

## Batch 2026-04-12-002 | 对抗 review 合同清补

### 1. 范围

- 复核 reviewer 提出的 `.bat` 离线入口缺口是否已真正闭环；
- 清理 `InstallerProfileRef` 段内部仍残留的 profile 命名不一致。

### 2. 事实记录

- `.bat` 入口已经进入 `096` 的模型层说明、FR-096-012 与验收准则，不再是缺失项；
- 但 `InstallerProfileRef` 的 v1 reality 列表仍写成 `offline_bundle_posix`，而同文档的 FR-096-012 与执行计划使用 `offline_bundle_posix_shell`；
- 仓库内没有其他正式 baseline 或实现代码引用 `offline_bundle_posix`，因此这属于 `096` 内部合同命名未完全统一，而不是跨文件兼容约束。

### 3. 本批输出

- 将 `InstallerProfileRef` 段的 POSIX profile 名称统一为 `offline_bundle_posix_shell`；
- 保持 Windows PowerShell / `.bat launcher` 的二层语义不变：`.bat` 是受控 launcher alias，不另造执行语义。

### 4. 验证命令

```bash
git diff --check -- specs/096-frontend-mainline-host-runtime-manager-baseline/spec.md specs/096-frontend-mainline-host-runtime-manager-baseline/task-execution-log.md
```

### 5. 验证结果

- `git diff --check -- specs/096-frontend-mainline-host-runtime-manager-baseline/spec.md specs/096-frontend-mainline-host-runtime-manager-baseline/plan.md specs/096-frontend-mainline-host-runtime-manager-baseline/task-execution-log.md`：通过。
- `uv run ai-sdlc verify constraints`：通过，输出 `verify constraints: no BLOCKERs.`。

### 6. 当前结论

- reviewer 指出的 `.bat` profile 合同缺口已收口到同一命名体系；
- `096` 目前不存在“模型层漏掉 `.bat` / FR 层承认 `.bat`”这类自相矛盾。
