# 实施计划：Frontend Delivery Registry Runtime Handoff Baseline

**编号**：`166-frontend-delivery-registry-runtime-handoff-baseline` | **日期**：2026-04-19 | **规格**：[`spec.md`](./spec.md)

## 1. 目标

在不扩张到真实安装执行器的前提下，把 `099` 的 docs-only resolver contract 接成最小 runtime handoff，让 `ProgramService` / CLI 能对外暴露稳定的 delivery registry truth。

## 2. 范围

### In Scope

- 新增 `ProgramFrontendDeliveryRegistryHandoff` runtime surface
- 新增 `program delivery-registry-handoff`
- 复用当前 solution snapshot、provider manifest、style-support、install strategy truth 组装 handoff
- 为 public / enterprise 两条内置路径补测试
- 更新用户指南命令表

### Out Of Scope

- 不实现 delivery registry artifact writer
- 不执行 `pnpm/npm` 安装
- 不接纳 arbitrary npm URL / private registry URL 输入
- 不抬升 `adapter_packages`

## 3. 实施步骤

1. 先补 unit / integration 红灯测试，锁住 handoff 与 CLI 期望输出；
2. 在 `ProgramService` 增加 delivery registry handoff dataclass 与 builder；
3. 在 CLI 暴露 `program delivery-registry-handoff`；
4. 更新 `USER_GUIDE.zh-CN.md`；
5. 跑定向测试与 diff hygiene。

## 4. 验证

- `uv run pytest tests/unit/test_program_service.py -k "delivery_registry_handoff" -q`
- `uv run pytest tests/integration/test_cli_program.py -k "delivery_registry_handoff" -q`
- `uv run ruff check src/ai_sdlc/cli/program_cmd.py src/ai_sdlc/core/program_service.py tests/integration/test_cli_program.py tests/unit/test_program_service.py`
- `uv run ai-sdlc verify constraints`
- `git diff --check`

## 5. 回滚原则

- 如果 handoff 把 private registry prerequisite gap 误报成 entry 不存在，必须回退；
- 如果 handoff 允许任意 npm URL / 私有源地址进入 framework truth，必须回退；
- 如果 handoff 把 `adapter_packages` 从空数组改成猜测值，必须回退。
