# 实施计划：主线真值复位与轻量 ROI 合同

**编号**：`219-mainline-truth-roi-contract`
**状态**：首轮合议 REJECT 后的 formal 整改，等待同 identity round 2
**规格**：`specs/219-mainline-truth-roi-contract/spec.md`

## 当前授权边界

当前只授权 formal 规格冻结、基线取证、Program Truth 映射、对应 root inventory tuple 的机械断言和
continuity 更新。尚未授权产品模板、特性回归测试或运行时实现。详细实施计划必须在用户审阅并批准
`spec.md` 后生成。

## 已冻结推荐方案

采用规格 §3 的方案 B：保留现有 link/handoff/reconcile 写入合同；以 behind-only remote-ref 选择与精确
formal-control allowlist 修正 truth 分类；以一个共享纯解析 helper 统一全部 active-WI status/execute/resume
消费面；以两个真实 render 路径承载同一轻量 ROI semantic set。不得建立 ROI/Lean 运行时、额外工件或
close 门禁。

## 计划生成条件

用户批准规格后，下一步必须使用正式 planning 流程，逐项冻结：

1. Track A0 的 stale-local-main/formal-only characterization RED、behind-only base 选择与精确 formal-control
   classifier GREEN；
2. Track A1 的历史 feature + 新 linked WI RED、共享纯解析 helper、全部 status 子面及 §4.1 consumer matrix；
3. Track B 的两个真实 render 路径 semantic-set RED/GREEN；
4. 三个 batch 分别可回退、分别 Go/No-Go；任一 batch 需要新状态/解析器/公共面时停止，不以另一 batch 掩盖；
5. focused/full verification、clean remote-main fixture、continuity refresh 和两轮评审边界。

批准前不得新增实现任务或修改规格 §4 允许范围内的产品/测试文件。
