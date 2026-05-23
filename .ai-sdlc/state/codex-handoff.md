# Continuity Handoff

- Updated: 2026-05-23T17:12:00+00:00
- Reason: Batch 6 二轮对抗复审通过后收口
- Goal: 落实生产反馈：任务守卫、注释规范、中文编码和半途接入优化
- State: Batch 6 T61-T66 已按 UX 与 AI-native 对抗评审完成二次修订，focused tests、ruff、verify constraints 通过，两个对抗 agent 均通过并同意进入 Batch 7。
- Stage: implement
- Work Item: 183-production-feedback-guard-adoption
- Branch: feature/183-production-feedback-guard-adoption-docs

## Changed Files
- M AGENTS.md
- M src/ai_sdlc/adapters/codex/AI-SDLC.md
- M src/ai_sdlc/adapters/vscode/AI-SDLC.md
- M src/ai_sdlc/adapters/claude_code/AI-SDLC.md
- M src/ai_sdlc/adapters/cursor/rules/ai-sdlc.md
- M src/ai_sdlc/adapters/generic/ide-hint.md
- M src/ai_sdlc/core/comment_policy.py
- M src/ai_sdlc/core/text_quality.py
- M src/ai_sdlc/core/verify_constraints.py
- M rules/code-review.md
- M src/ai_sdlc/rules/code-review.md
- M templates/tasks-template.md
- M tests/unit/test_comment_policy.py
- M tests/unit/test_text_quality.py
- M src/ai_sdlc/core/adoption.py
- M src/ai_sdlc/cli/adopt_cmd.py
- M src/ai_sdlc/cli/main.py
- M src/ai_sdlc/__main__.py
- M USER_GUIDE.zh-CN.md
- M tests/unit/test_adoption.py
- M tests/integration/test_cli_adopt.py
- M tests/unit/test_command_names.py
- M specs/183-production-feedback-guard-adoption/tasks.md
- M specs/183-production-feedback-guard-adoption/task-execution-log.md

## Key Decisions
- 注释语言约束必须进入真实 adapter prompt / AGENTS，不只停留在 helper。
- 原注释删除保护进入 `verify constraints`；删除原注释需同 hunk 替代说明，或在 execution log / handoff 记录删除原因。
- 文本质量检查改为 tracked diff 新增行 + untracked 新文件内容；tracked 历史非 UTF-8 不阻塞当前干净改动，untracked 新文件仍整文件 UTF-8 解码。
- 原注释删除原因记录必须逐条对应路径和被删注释摘要，不能用全局关键词豁免所有删除。
- 删除原因匹配已支持自然空格写法；blocker 文案提示必须记录文件路径和被删注释摘要。
- Brownfield adopt 主路径为 `ai-sdlc adopt .`，生成 `.ai-sdlc/adoption/` 桥接产物，不覆盖用户原 JSON/Markdown 任务源。
- 用户可用 `--prefer "支付回调"` 做自然语言纠偏；非 git 项目自动降级为文件/结构证据。
- 候选识别已支持中文文件名、README、内容 sniff、git branch/diff、test structure、updated_at、AI-SDLC task id 和 checkpoint candidate。
- 扫描改为可剪枝 `os.walk`，避免进入 `node_modules` 等大目录。
- 目录预算超过后会停止深层遍历；继续点推荐已考虑 dependencies / blockers；Markdown 支持 `待办：`、`任务：`、`进行中：` 自然写法。
- `T61`-`T66` 已在第二轮复审通过后标记 done。
- 乱码示例通过 allowlist 支持，繁体项目通过显式参数例外，不把学习压力转给普通用户主路径。
- `T51`、`T52`、`T53` 已在第三轮复审通过后标记 done。

## Commands / Tests
- `uv run pytest tests/unit/test_comment_policy.py tests/unit/test_text_quality.py -q`: 18 passed
- `uv run pytest tests/integration/test_cli_verify_constraints.py -q`: 46 passed
- `uv run ruff check src/ai_sdlc/core/comment_policy.py src/ai_sdlc/core/text_quality.py src/ai_sdlc/core/verify_constraints.py tests/unit/test_comment_policy.py tests/unit/test_text_quality.py`: All checks passed
- `uv run ai-sdlc verify constraints`: no BLOCKERs
- `uv run pytest tests/unit/test_adoption.py tests/integration/test_cli_adopt.py tests/unit/test_command_names.py -q`: 15 passed
- `uv run ruff check src/ai_sdlc/core/adoption.py src/ai_sdlc/cli/adopt_cmd.py src/ai_sdlc/cli/main.py src/ai_sdlc/__main__.py tests/unit/test_adoption.py tests/integration/test_cli_adopt.py tests/unit/test_command_names.py`: All checks passed

## Blockers / Risks
- none

## Exact Next Steps
- 提交 Batch 6。
- 进入 Batch 7：运行更广验证、提交 PR、处理 review/checks、发布补丁版本。
