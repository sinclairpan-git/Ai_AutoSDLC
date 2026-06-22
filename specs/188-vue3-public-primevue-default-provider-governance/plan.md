# 实施计划：Vue3 public-primevue default provider governance

**功能编号**：`188-vue3-public-primevue-default-provider-governance`  
**输入**：`spec.md`、`docs/vue3-public-primevue-default-provider-prd.zh-CN.md`  
**阶段**：设计冻结草案  

## 技术背景

当前前端治理已具备 `enterprise-vue2` 和 `public-primevue` 两条 provider 语义路径，但默认推荐仍倾向企业 Vue2。`public-primevue` 已具备 provider manifest、provider profile、PrimeVue package truth、style-support、runtime adapter、managed delivery 和 verify constraints 周边能力。本工作项在既有能力上调整默认选择与模板/验证闭环，不引入新的前端栈。

## 技术决策

### TD-188-001 默认 provider 切换

默认 recommendation 改为 `vue3/public-primevue/modern-saas`。`enterprise_provider_eligible` 只影响显式企业 Vue2 请求的诊断，不再作为普通默认推荐分支的决定因素。

### TD-188-002 企业 Vue2 兼容

保留 `enterprise-vue2` 的显式选择路径、安装策略、availability/preflight 诊断和 fallback 确认。所有新默认逻辑必须有回归测试证明未破坏企业显式路径。

### TD-188-003 依赖分层

依赖分为三层：

1. provider core packages：`primevue`、`@primeuix/themes`。
2. template runtime dependencies：`vue-router`、`pinia`、`axios`、`vue-i18n`、`@vueuse/core`、`dayjs`。
3. template dev dependencies：`typescript`、`vite`、`unocss`、`vitest`。

`primeicons` 不进入本轮默认必选依赖。

### TD-188-004 模板治理

Vue3 模板必须具备：

1. Vite 可运行入口。
2. PrimeVue plugin/theme 初始化。
3. UnoCSS plugin 和 `uno.config.ts`。
4. `src/styles/variables.css` 与 `main.css` / `primevue.css`。
5. `components/base/` 和业务层目录。
6. 默认页面或验证页覆盖 Button、Table、Dialog、Form 基础组件。

### TD-188-005 Import 边界

业务层 `views/` 与 `components/business/` 不直接 import `primevue/*`。首版通过 import scan 或 AST scan 输出 warning，后续可升级 targeted blocker。

### TD-188-006 Web/视觉验证

Web smoke 是 blocker，视觉和基础 a11y 是 warning evidence。首版不使用严格 pixel diff 作为 blocker，但截图与元数据格式必须稳定，便于后续建立 baseline。

## 实施批次

### Batch 1：formal baseline

冻结 PRD 拆解，形成 spec/plan/tasks/task-execution-log，并把默认 provider、依赖分层、验证等级和 Web/视觉测试规划作为后续实现合同。

### Batch 2：solution confirmation default switch

调整推荐逻辑与 CLI 输出，使未显式选择 provider 时默认推荐 `vue3/public-primevue/modern-saas`。保留显式企业 Vue2 路径。

### Batch 3：provider/template dependency and generation

调整 provider/install/template dependency truth，更新 managed delivery 输出，生成 UnoCSS、CSS Variables、PrimeVue 初始化、目录结构和 Base/Ui 层。

### Batch 4：governance validation

增加默认推荐、企业兼容、依赖分层、模板文件、PrimeVue import 边界、文档一致性的验证与测试。

### Batch 5：Web smoke blocker

建立 Web smoke 入口，证明生成前端可启动、可访问、非白屏、无 fatal console error，且 PrimeVue/UnoCSS/CSS Variables 生效。

### Batch 6：visual and a11y evidence

生成桌面/移动截图与元数据，输出视觉结构 warning 和基础交互/a11y warning。

### Batch 7：documentation and release truth

更新用户指南、release notes、provider 文档和迁移说明，明确默认 provider 变更与显式 `enterprise-vue2` 使用方式。

## 验证策略

### 单元测试

- solution confirmation 默认推荐和显式企业 Vue2。
- 依赖分层和 provider core packages。
- import scan / AST scan。
- verify constraints attachment report。

### 集成测试

- managed delivery 生成模板文件集。
- Vue3 生成快照包含 PrimeVue、UnoCSS、CSS Variables。
- Web smoke runner 对生成前端执行启动和页面检查。

### 视觉与浏览器证据

- 桌面截图：`1440x900`。
- 移动截图：`390x844`。
- 元数据：provider、style pack、viewport、timestamp、generation entry、smoke result。
- warning：空白、主内容不可见、明显重叠、焦点态、Dialog、label/aria。

## 风险与缓解

| 风险 | 缓解 |
| --- | --- |
| 默认切换影响企业用户 | 保留显式 `enterprise-vue2`，文档和 CLI 输出说明选择方式 |
| UnoCSS 默认引入增加复杂度 | 以模板内置方式降低用户配置成本，普通 CSS 保留逃逸口 |
| Web smoke 在 CI 环境不稳定 | 将 Vite 启动和页面检查做成 bounded runner，输出明确 diagnostic |
| 视觉 diff 误报 | 首版仅要求截图和结构化 warning，不做严格 pixel blocker |
| Base/Ui 封装不足 | 先以 import scan 暴露风险，再逐步升级 targeted blocker |

## 待确认项

1. Web smoke 使用现有 frontend browser gate runner 扩展，还是新增专用 public-primevue smoke runner。
2. 视觉证据归档路径沿用现有 browser gate artifacts，还是建立 Vue3 default provider 专用 evidence path。
3. import scan 首版采用简单 import parser 还是 TypeScript AST。
