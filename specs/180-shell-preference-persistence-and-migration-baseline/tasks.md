# 任务分解：跨平台 Shell 偏好持久化与迁移基线

**编号**：`180-shell-preference-persistence-and-migration-baseline`  
**日期**：2026-04-27  
**来源**：[`spec.md`](./spec.md) + [`plan.md`](./plan.md)

## 执行清单

- [x] T180-01 Shell 偏好配置模型与推荐策略
- [x] T180-02 Init 交互式 shell 选择与持久化
- [x] T180-03 独立 shell 重选命令
- [x] T180-04 Adapter 模板消费 shell 偏好并物化
- [x] T180-05 Status/Doctor 老项目迁移提示
- [x] T180-06 跨平台回归与文档收口

## Batch 1：配置模型和初始化入口

### T180-01 Shell 偏好配置模型与推荐策略

- **优先级**：P0
- **依赖**：无
- **文件**：`src/ai_sdlc/models/project.py`、`src/ai_sdlc/core/config.py`、相关 unit tests
- **验收标准**：
  1. `ProjectConfig` 支持 shell 偏好字段
  2. 支持 `powershell`、`bash`、`zsh`、`cmd`、`auto`
  3. 宿主推荐策略覆盖 Windows/macOS/Linux
- **验证**：project config unit tests + recommendation helper tests

### T180-02 Init 交互式 shell 选择与持久化

- **优先级**：P0
- **依赖**：T180-01
- **文件**：`src/ai_sdlc/cli/commands.py`、初始化相关 helper/tests
- **验收标准**：
  1. 交互式 `init` 允许选择 shell
  2. 非交互式路径保留兼容行为
  3. 选择结果写入 `project-config.yaml`
- **验证**：CLI init integration tests

## Batch 2：重选命令和 adapter 文案落地

### T180-03 独立 shell 重选命令

- **优先级**：P0
- **依赖**：T180-01
- **文件**：新增或扩展 shell/config/adapter CLI 命令、相关 integration tests
- **验收标准**：
  1. 已初始化项目无需重新 `init` 即可更新 shell 偏好
  2. 命令幂等
  3. 命令输出给出已应用结果
- **验证**：CLI command tests + config writeback tests

### T180-04 Adapter 模板消费 shell 偏好并物化

- **优先级**：P0
- **依赖**：T180-03
- **文件**：`src/ai_sdlc/integrations/ide_adapter.py`、`src/ai_sdlc/adapters/*`、相关 tests
- **验收标准**：
  1. Codex adapter 文案明确当前 shell 和命令语法约束
  2. 其他 adapter 若有终端约定，也使用同一配置源
  3. shell 更新后重新物化文档
- **验证**：adapter materialization tests + snapshot tests

## Batch 3：迁移提示、回归和收口

### T180-05 Status/Doctor 老项目迁移提示

- **优先级**：P0
- **依赖**：T180-01、T180-03
- **文件**：`src/ai_sdlc/cli/adapter_cmd.py`、`src/ai_sdlc/cli/doctor_cmd.py`、状态面/提示测试
- **验收标准**：
  1. 缺失 shell 偏好的已初始化项目显示迁移提示
  2. 输出推荐值和可复制命令
  3. `run --dry-run` 不阻断
- **验证**：status/doctor integration tests + dry-run compatibility tests

### T180-06 跨平台回归与文档收口

- **优先级**：P1
- **依赖**：T180-02、T180-04、T180-05
- **文件**：README/用户指南、CLI/module invocation tests、必要文档
- **验收标准**：
  1. Windows/macOS/Linux 推荐值均有回归
  2. 老项目迁移路径与重选命令有文档说明
  3. source checkout 下 `python -m ai_sdlc` 入口不回退到旧包
- **验证**：focused integration suite + doc consistency check

## 2026-04-27 Execution Update

- [x] T180-01 completed in code and tests
- [x] T180-02 completed in code and tests
- [x] T180-03 completed in code and tests
- [x] T180-04 completed in code and tests
- [x] T180-05 completed in code and tests
- [x] T180-06 completed with Windows git-client regression fix, focused tests, checkpoint reconciliation, and dry-run close-gate follow-up
