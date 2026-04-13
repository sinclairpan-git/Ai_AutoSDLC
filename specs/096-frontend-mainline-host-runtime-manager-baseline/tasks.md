# 任务清单：Frontend Mainline Host Runtime Manager Baseline

来源：[`plan.md`](./plan.md) + [`spec.md`](./spec.md)（`FR-096-001` ~ `FR-096-044`，`SC-096-001` ~ `SC-096-006`）

## Batch 0：状态续接

- [x] 确认当前仓库状态与 work item 序号。
- [x] 对账 `095` / `096` 的关系，确定本次续做目标为 `096`。
- [x] 补齐 `096` 的 `plan.md`、`tasks.md`、`task-execution-log.md`。

## Batch 1：契约与证据模型

- [x] 定义 `host_runtime_plan` 顶层结构与 JSON 序列化约定。
- [x] 定义 `readiness` / `bootstrap_acquisition` / `remediation_fragment` 的数据模型。
- [x] 固定 `reason_codes`、`will_download`、`will_install`、`will_modify`、`will_not_touch` 字段。
- [x] 为未知平台、未知 runtime、未绑定 surface 建立 fail-closed 单元测试。

## Batch 2：最小宿主判定

- [x] 实现 OS / arch / Python 版本判定。
- [x] 实现 AI-SDLC runtime 可验证性判定。
- [x] 实现 surface binding 判定，覆盖 `source`、`uv`、`python -m`、IDE 等非绑定入口。
- [x] 在最小宿主不成立时输出 acquisition handoff，而不是 remediation。

## Batch 3：离线 profile 与主线缺口诊断

- [x] 建立离线 bundle profile 映射。
- [ ] 识别 bundle / platform / arch / permission / disk 等阻断因素并落 reason code。
- [x] 在最小宿主成立时诊断 Node / package manager / Playwright browser 缺口。
- [x] 将上述缺口表达为 `mainline_remediable`，不执行修复。

## Batch 4：CLI 与文档

- [ ] 在 CLI 中增加只读 `host_runtime_plan` 输出入口。
- [ ] 增加 CLI 集成测试，固定 JSON 输出与退出语义。
- [ ] 更新 `USER_GUIDE.zh-CN.md`，说明显式确认前不会发生修改。
- [ ] 回写执行记录与验证结果。

## 收尾验证

- [ ] 运行针对性 `pytest`。
- [ ] 运行针对性 `ruff check`。
- [ ] 运行 `uv run ai-sdlc verify constraints`。
- [ ] 运行 `git diff --check`。
