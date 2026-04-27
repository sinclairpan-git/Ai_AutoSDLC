# AI-SDLC Experience Studio

这是一个独立静态 Web 培训材料目录，可整体移动到其他位置，不依赖本仓库框架运行路径。

## 打开方式

推荐用本地静态服务打开：

```bash
cd deliverables/ai-sdlc-training-experience
python3 -m http.server 4177
```

然后访问：

```text
http://127.0.0.1:4177
```

也可以直接双击 `index.html` 打开。

## 操作

- `ArrowRight` / `PageDown` / `Space`: 下一页
- `ArrowLeft` / `PageUp`: 上一页
- `Home`: 第一页
- `End`: 最后一页
- 左侧章节可点击跳转，底部圆点显示当前页位置

## 内容结构

- 前半段面向入门使用者：是什么、为什么比 vibe coding 或 spec-kit+superpowers 更稳、怎么用、能获得什么。
- 后半段面向专业开发：架构、组件、流水线、Agent 调度、约束、监测、自迭代、前端治理。
- `assets/` 中包含本材料使用的 AI 生成视觉资产，页面不依赖外网图片。

## 边界

本目录只包含培训材料，不修改 `src/`、`managed/frontend/`、`specs/`、`.ai-sdlc/`。
