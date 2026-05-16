# 离线 Python runtime 发布清单

> 适用范围：发布或分发携带 `python-runtime/` 的 AI-SDLC 离线安装包。
>
> 当前 published release：`v0.7.17`

这份清单只回答一件事：当离线 bundle 要承诺“目标机无需预装 Python 3.11+”时，发布人需要交付哪些产物、逐项确认哪些约束、保留哪些验证证据。

## 1. 发版目标

当离线包包含 `python-runtime/` 时，目标口径必须是：

- 目标机可以在 **没有系统 Python 3.11+** 的情况下完成安装
- 安装脚本优先使用 bundle 自带 runtime，而不是要求用户手动补 Python
- 若 bundle 的平台与目标机不匹配，安装必须诚实阻断

若做不到上述三点，就不要把该 bundle 宣称为“零 Python 预装”离线包。

## 2. 必备产物

发布前逐项确认离线目录 `dist-offline/ai-sdlc-offline-<version>/` 内至少包含：

- [ ] `wheels/`
- [ ] `bundle-manifest.json`
- [ ] `README_BUNDLE.txt`
- [ ] `install_offline.sh`
- [ ] `install_offline.ps1`
- [ ] `install_offline.bat`
- [ ] `python-runtime/`（若本次对外承诺“无需预装 Python”）

对应归档资产：

- [ ] `ai-sdlc-offline-<version>.tar.gz`
- [ ] `ai-sdlc-offline-<version>.zip`

## 3. `python-runtime/` 产物合同

若 bundle 内含 `python-runtime/`，必须同时满足：

- [ ] **平台匹配**：runtime 的 OS / CPU 与目标机一致；不得把 macOS runtime 装进 Windows bundle，也不得跨 CPU 架构混装
- [ ] **入口存在**：
  - POSIX 至少存在 `python-runtime/bin/python3`、`python-runtime/bin/python`，或版本化入口 `python-runtime/bin/python3.x`
  - Windows 至少存在 `python-runtime/python.exe`
- [ ] **可自举 venv**：runtime 能成功执行 `-m venv`
- [ ] **可完成 pip 安装**：runtime 创建出的 venv 能执行 `python -m pip install <wheel>`
- [ ] **无构建机绝对依赖**：macOS `otool -L` 不得出现 `/Library/Frameworks/Python.framework`、Homebrew、用户目录或 bundle 内绝对路径；Linux `ldd` 不得出现 `not found` 或构建机私有路径；Windows 必须携带匹配的 `python3xx.dll`
- [ ] **不覆盖 bundle 其他真值**：`bundle-manifest.json` 仍描述 bundle 适用平台；runtime 只是安装载体，不替代 manifest
- [ ] **manifest 已标记**：`bundle-manifest.json` 中存在 `"python_runtime_bundled": true`

若缺其中任一项，该 bundle 只能作为“需要系统 Python 3.11+”的离线包，而不能作为“零 Python 预装”离线包发布。

## 4. 构建前检查

- [ ] 版本号已对齐：`pyproject.toml`、release tag、离线 bundle 名称一致
- [ ] 当前平台就是目标平台，或已明确本次只服务某一目标平台
- [ ] 准备好的 `python-runtime/` 具有可分发许可，允许随离线包一起交付
- [ ] 已确认 `AI_SDLC_OFFLINE_PYTHON_RUNTIME` 指向的是完整 runtime 根目录，而不是某个单独解释器文件

推荐构建命令：

```bash
AI_SDLC_OFFLINE_PYTHON_RUNTIME=/path/to/python-runtime \
  ./packaging/offline/build_offline_bundle.sh
```

## 5. 构建后检查

- [ ] `bundle-manifest.json` 中 `package_version` 与本次版本一致
- [ ] `bundle-manifest.json` 中 `platform_os` / `platform_machine` 与目标平台一致
- [ ] `bundle-manifest.json` 中 `python_runtime_bundled` 为 `true`
- [ ] `wheels/` 内只有当前版本的 `ai_sdlc-<version>-*.whl`
- [ ] `python-runtime/` 已被拷入 bundle 根目录，而不是遗漏在本机构建目录
- [ ] `packaging/offline/verify_offline_bundle.py dist-offline/ai-sdlc-offline-<version> --require-bundled-runtime` 已通过
- [ ] `.tar.gz` 与 `.zip` 都已生成

可直接检查：

```bash
python - <<'PY'
import json
from pathlib import Path

manifest = json.loads(Path("dist-offline/ai-sdlc-offline-<version>/bundle-manifest.json").read_text())
print(json.dumps(manifest, indent=2, ensure_ascii=False))
PY
```

## 6. 冒烟验证

至少保留一条“目标机无系统 Python”路径的验证证据：

- [ ] **POSIX smoke**：在不暴露系统 Python 的环境中执行 `install_offline.sh`，确认脚本输出 `Using bundled Python runtime`
- [ ] **Windows smoke**：执行 `install_offline.ps1` 或 `install_offline.bat`，确认安装完成且 CLI 可调用
- [ ] 安装后执行 `ai-sdlc --help`，或用 `python -m ai_sdlc --help` 验证 CLI 可用
- [ ] 进入业务仓库后执行 `ai-sdlc init .`，确认初始化会自动完成必要检查和安全预演
- [ ] CLI 输出包含双语结果块：`当前结果 / Result`、`下一步 / Next`

跨平台 release 额外门禁：

- [ ] **Windows target gate**：运行 `.github/workflows/windows-offline-smoke.yml`，并留存 `windows-offline-smoke-evidence`
- [ ] **POSIX target gate**：运行 `.github/workflows/posix-offline-smoke.yml`，并留存 `posix-offline-smoke-evidence-*`
- [ ] `windows-offline-smoke-evidence` 与 `posix-offline-smoke-evidence-*` 均至少包含 `install.log`、`help.txt`、`adapter-status.txt`、`run-dry-run.txt`、`bundle-manifest.json`
- [ ] 若 release note 声称 Windows、macOS、Linux 或“零 Python 预装”跨平台支持，必须同时引用 Windows 与 POSIX target gate 证据

如果本次 bundle 不包含 `python-runtime/`，也必须显式记录“本次未提供零 Python 预装能力”，避免对外误导。

当手头没有 Windows 实机时，可接受的替代证据是：

- [ ] 运行 GitHub Actions 工作流 [windows-offline-smoke.yml](/Users/sinclairpan/project/Ai_AutoSDLC/.github/workflows/windows-offline-smoke.yml)
- [ ] 下载并留存 `windows-offline-smoke-evidence` artifact
- [ ] artifact 中至少包含 `install.log`、`help.txt`、`adapter-status.txt`、`run-dry-run.txt`、`bundle-manifest.json`
- [ ] release note / PR 描述明确写出“Windows 证据来自 CI runner，而非本地实机”
- [ ] 不把 CI runner 内临时构建出的 bundle 归档当成正式对外交付件；CI 在这里的职责是产出 smoke 证据，而不是替代正式发布物

当手头没有 macOS/Linux 实机时，可接受的替代证据是：

- [ ] 运行 GitHub Actions 工作流 `.github/workflows/posix-offline-smoke.yml`
- [ ] 下载并留存 `posix-offline-smoke-evidence-macos-latest` 与 `posix-offline-smoke-evidence-ubuntu-latest` artifact
- [ ] artifact 中至少包含 `install.log`、`help.txt`、`adapter-status.txt`、`run-dry-run.txt`、`bundle-manifest.json`
- [ ] release note / PR 描述明确写出“POSIX 证据来自 CI runner，而非本地实机”
- [ ] 不把 CI runner 内临时构建出的 bundle 归档当成正式对外交付件；CI 在这里的职责是产出 smoke 证据，而不是替代正式发布物

## 6.1 跨平台证据边界

- [ ] 不要把 `.zip` 已生成当作 “Windows 已验证” 的证据；`.zip` 只说明已归档，不说明其中 runtime / wheels / 安装脚本在 Windows 可用
- [ ] 不要把 macOS / Linux 上的成功安装，当作 Windows `install_offline.ps1` / `install_offline.bat` 已验证的证据
- [ ] 不要把 Windows 上的成功安装，当作 POSIX `install_offline.sh` 已验证的证据
- [ ] 若当前只在单一平台完成了真实 smoke，release note 必须明确写成“已验证的平台”与“未验证的平台”
- [ ] 若要对外同时承诺 Windows 与 POSIX 都支持“零 Python 预装”，必须分别提供对应平台构建出的 bundle，并分别保留真实 smoke 证据
- [ ] 非目标平台机器最多只能做归档内容检查、manifest 检查、脚本静态检查；这些都不能替代目标平台真实安装验证
- [ ] macOS/Linux 开发必须通过 Windows target gate；Windows 开发必须通过 POSIX target gate；任何单平台成功都不得升级为跨平台 release 结论

## 7. Release Notes / 分发文案

发布说明里必须明确写出：

- [ ] 本次离线 bundle 是否内含 `python-runtime/`
- [ ] 若内含，口径是“目标机无需预装 Python 3.11+”
- [ ] 若不内含，口径是“目标机仍需提供 Python 3.11+”
- [ ] Windows 使用 `.zip`，macOS / Linux 使用 `.tar.gz`
- [ ] 离线 bundle 需与目标机 OS / CPU 匹配
- [ ] 指向 `packaging/offline/README.md` 与本清单

## 8. 收口证据

发版或 PR 收口前，建议把以下信息写进对应的 release note、task execution log 或 PR 描述：

- [ ] bundle 名称与版本
- [ ] `python-runtime/` 来源与目标平台
- [ ] manifest 关键字段截图或文本
- [ ] 一条无系统 Python 的安装验证结果
- [ ] 一条安装后 `adapter status` / `run --dry-run` 的结果摘要

只要缺少上述证据，就不应把“离线零 Python 预装能力已发布”表述为已完成。
