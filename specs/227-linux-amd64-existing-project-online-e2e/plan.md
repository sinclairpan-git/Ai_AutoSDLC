# 实施计划：R10 Linux AMD64 已有项目在线 E2E

**编号**：`227-linux-amd64-existing-project-online-e2e`  
**规格**：`specs/227-linux-amd64-existing-project-online-e2e/spec.md`

## 方案

保留 `.github/workflows/macos-user-guide-e2e.yml` 作为现有 POSIX user-guide consumer，在唯一的 `existing-project-online-install` job 中增加 R06/R10 两行 matrix。通过 job env 将 route、OS、architecture、asset suffix、fresh shell 和 artifact 名传入同一 bash replay；除平台绑定外不改变现有生命周期与 receipt 结构。

## 文件边界

- 修改 `.github/workflows/macos-user-guide-e2e.yml`：增加两行矩阵并消除 R06/macOS 硬编码。
- 修改 `tests/integration/test_github_workflows.py`：先写 R10 matrix 与动态绑定合同测试。
- 修改 `docs/FRAMEWORK_ROADMAP.zh-CN.md`：只在真实 Ubuntu 证据取得后记录 R10 已进入主线候选，仍为 `partial`。
- 修改 `program-manifest.yaml`、`.ai-sdlc/project/config/project-state.yaml`、直接 inventory 合同测试与本 WI：登记 WI227 和真实执行证据。
- 不创建 helper/script，不修改产品代码、用户指南、producer 或 schema。

## 实施顺序

1. 冻结本 spec/plan/tasks 并提交 canonical formal baseline；同一分支随后重命名为 `feature/227-linux-amd64-existing-project-online-e2e-dev`。
2. 在 workflow 合同测试中写入 R06/R10 两行矩阵、平台变量、动态 receipt/artifact 绑定断言，并确认预期 RED。
3. 最小参数化现有 job，使直接测试与完整 workflow 测试 GREEN。
4. 完成本地 Ruff、constraints、Program validate、diff-check 和相关 pytest；更新 execution log 与 handoff。
5. 推送同一分支并打开唯一 PR；首个候选即运行真实 Ubuntu R10 路径。云端排队/网络失败只重试；确定性路径失败最多两轮聚焦修复。
6. exact HEAD required checks 与一次 Codex review 均 clean 后合并；R10 继续保持 `partial`，等待未来正常发布自然复验。

## 关键路径

| 路径 | 验证 | 失败处理 |
|---|---|---|
| 矩阵身份 | YAML 解析 + 直接 pytest | 修正当前 workflow/test |
| Linux 资产与架构 | `ubuntu-latest` 真实 job | 同路径聚焦修复；不得改 producer |
| init/adopt/恢复/文件保护 | 真实 R10 replay + artifact receipt | 同路径聚焦修复 |
| R06 回归 | macOS matrix job | 同路径参数化修复 |
| release 证明 | 下一次正常 `release.published` | 本 PR 不单独发版、不阻塞合并 |

## 回退

整个实现由单 PR 承载，可整体 revert。若触发停止条件，关闭该 PR 并保留 WI227 的 No-Go 记录，不创建替代方案。
