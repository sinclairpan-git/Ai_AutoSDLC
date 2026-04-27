# 实施计划：跨平台 Shell 偏好持久化与迁移基线

**编号**：`180-shell-preference-persistence-and-migration-baseline`  
**日期**：2026-04-27  
**规格**：[`spec.md`](./spec.md)

## 1. 目标

把“项目首选 shell”从文档建议升级为项目级正式配置，并在首版同时打通新项目初始化、老项目迁移提示、独立重选命令、adapter 文档物化和状态面展示。

## 2. 宪章响应

| 宪章门禁 | 计划响应 |
|----------|----------|
| MUST-1 MVP 优先 | 首版直接覆盖新项目与老项目，不把升级用户关键路径延期到后续版本 |
| MUST-2 关键路径必须可验证 | 每条宿主推荐逻辑、配置写入、adapter 文案落地、状态提示和重选命令均要求 unit/integration 证据 |
| MUST-3 每次改动声明范围、验证与回退 | `tasks.md` 每个任务声明影响文件、验证命令和幂等/回退策略 |
| MUST-4 状态落盘 | shell 偏好必须进入 `project-config.yaml`，并在状态面可见 |
| MUST-5 产品代码与开发框架隔离 | 仅新增项目配置和 adapter/CLI 展示，不改变业务 work item 或前端执行主链 |

## 3. 阶段计划

### Phase 0：配置模型与迁移口径冻结

- 定义 shell 偏好枚举和宿主推荐策略
- 明确字段写入位置与读取优先级
- 明确老项目缺失配置时的非阻断迁移语义

### Phase 1：项目配置持久化与初始化接入

- 扩展 `ProjectConfig`
- 在 `init` 交互式路径接入 shell 选择
- 处理非交互式初始化的推荐值或 `auto` 兜底

### Phase 2：独立重选命令与 adapter 文案物化

- 增加 shell 重选命令
- 命令更新配置后重新物化 adapter 文档
- adapter 模板消费 shell 偏好并生成明确命令语法约束

### Phase 3：老项目迁移提示与状态面补齐

- `status` / `doctor` 输出缺失 shell 偏好的迁移提示
- 输出推荐值和可复制命令
- 验证对 `run --dry-run` 等非配置命令的非阻断效果

### Phase 4：跨平台回归与文档收口

- 覆盖 Windows/macOS/Linux 推荐值测试
- 覆盖重选命令和 adapter 更新回归
- 更新 README / 使用说明中与 shell 有关的约定

## 4. 影响范围

- `src/ai_sdlc/models/project.py`
- `src/ai_sdlc/core/config.py`
- `src/ai_sdlc/cli/commands.py`
- `src/ai_sdlc/cli/adapter_cmd.py`
- `src/ai_sdlc/cli/doctor_cmd.py`
- `src/ai_sdlc/integrations/ide_adapter.py`
- `src/ai_sdlc/adapters/codex/AI-SDLC.md`
- `src/ai_sdlc/adapters/cursor/rules/ai-sdlc.md`
- `src/ai_sdlc/adapters/vscode/AI-SDLC.md`
- `src/ai_sdlc/adapters/claude_code/AI-SDLC.md`
- `tests/unit/*`
- `tests/integration/*`
- `README.md` 或相关用户指南（如需）

## 5. 验证策略

- 单元测试：
  - shell 枚举和值校验
  - 宿主 OS 到推荐 shell 的映射
  - 缺失配置时的状态面提示生成
- 集成测试：
  - `init` 写入 shell 偏好
  - 重选命令更新配置并刷新 adapter 文案
  - 老项目缺失 shell 偏好时 `status` / `doctor` 输出迁移提示
- CLI 测试：
  - `python -m ai_sdlc ...` 在 source checkout 中仍命中本地源码
  - `run --dry-run` 在缺失 shell 偏好时不阻断

## 6. 回退策略

- shell 偏好字段以增量方式加入 `ProjectConfig`，缺失字段保持向后兼容
- adapter 文案变更与 CLI 状态提示分批提交，可独立回退
- 重选命令只更新本地配置和 adapter 文档，不触碰执行状态机

## 7. 风险

- 交互式 `init` 增加一个选择项，必须避免破坏现有非交互流程
- 各 adapter 模板若文案结构差异较大，容易产生消费 shell 偏好时的漂移
- 需要明确 `auto` 只是兜底模式，否则用户可能误以为它等价于强约束 shell
