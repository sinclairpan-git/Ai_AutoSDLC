"""Regression checks for repository GitHub Actions workflows."""

from __future__ import annotations

from pathlib import Path

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[2]
_WORKFLOWS_DIR = _REPO_ROOT / ".github" / "workflows"


def test_github_workflows_are_valid_yaml() -> None:
    workflow_paths = sorted(_WORKFLOWS_DIR.glob("*.yml"))

    assert workflow_paths

    for workflow_path in workflow_paths:
        yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

    pr_checks = (_WORKFLOWS_DIR / "pr-checks.yml").read_text(encoding="utf-8")
    required = ("fetch-depth: 0", "persist-credentials: false", "git branch --force main HEAD^1", 'git switch --create "$GITHUB_HEAD_REF" HEAD^2')
    assert all(token in pr_checks for token in required) and pr_checks.index("Pytest smoke") < pr_checks.index(required[2]) < pr_checks.index(required[3]) < pr_checks.index("uv run ai-sdlc verify constraints")


def test_windows_offline_smoke_workflow_covers_bundle_build_install_and_cli_checks() -> None:
    workflow_path = _WORKFLOWS_DIR / "windows-offline-smoke.yml"

    assert workflow_path.is_file()

    workflow = workflow_path.read_text(encoding="utf-8")

    assert "workflow_dispatch:" in workflow
    assert "pull_request:" in workflow
    assert "windows-latest" in workflow
    assert "astral-sh/setup-uv@v7" in workflow
    assert "uv python install 3.11" in workflow
    assert "uv python find --managed-python 3.11" in workflow
    assert "AI_SDLC_OFFLINE_PYTHON_RUNTIME" in workflow
    assert 'AI_SDLC_OFFLINE_PYTHON_VERSIONS="3.11,3.12"' in workflow
    assert 'AI_SDLC_OFFLINE_TARGET_PLATFORM="win_amd64"' in workflow
    assert "build_offline_bundle.sh" in workflow
    assert "install_offline.ps1" in workflow
    assert "old-user-upgrade:" in workflow
    assert 'old-version:' in workflow
    assert '"0.7.5"' in workflow
    assert '"0.7.6"' in workflow
    assert 'python-version:' in workflow
    assert '"3.12"' in workflow
    assert (
        'pip install "git+https://github.com/sinclairpan-git/Ai_AutoSDLC.git@v${{ matrix.old-version }}"'
        in workflow
    )
    assert "scenario.txt" in workflow
    assert "old-install.txt" in workflow
    assert "from importlib.metadata import version; print(version('ai-sdlc'))" in workflow
    assert "old ai-sdlc metadata version check failed" in workflow
    assert "-NoProfile -ExecutionPolicy Bypass -File .\\install_offline.ps1 -UpgradeExisting" in workflow
    assert "ai-sdlc init . --agent-target codex --shell powershell" in workflow
    assert "当前结果 / Result" in workflow
    assert "下一步 / Next" in workflow
    assert "OPENAI_CODEX" in workflow
    assert "AI_SDLC_ADAPTER_CANONICAL_SHA256" in workflow
    assert "adapter status" in workflow
    assert "run --dry-run" in workflow
    assert "actions/upload-artifact@v7" in workflow
    assert "PYTHONUTF8" in workflow
    assert "PYTHONIOENCODING" in workflow
    assert "Console]::OutputEncoding" in workflow
    assert "UTF8Encoding" in workflow
    assert "verify_offline_bundle.py" in workflow
    assert "--require-bundled-runtime" in workflow
    assert "--install-log" in workflow
    assert "WindowsPowerShell\\v1.0\\powershell.exe" in workflow
    assert "-NoProfile -ExecutionPolicy Bypass -File .\\install_offline.ps1 -AddToPath" in workflow
    assert '$cliDir = Join-Path $bundleDir.FullName ".venv\\Scripts"' in workflow
    assert "$env:Path = $cliDir + [IO.Path]::PathSeparator + $env:Path" in workflow
    assert "Get-Command ai-sdlc" in workflow
    assert "ai-sdlc --help" in workflow
    assert "Legacy Artifact Probe" in workflow
    assert "recover --reconcile" in workflow
    assert '$upgradedVersion -notmatch "0\\.9\\.8"' in workflow
    assert '$upgradedVersion -notmatch "0\\.9\\.7"' not in workflow


def test_posix_offline_smoke_workflow_covers_macos_linux_bundle_install_and_cli_checks() -> None:
    workflow_path = _WORKFLOWS_DIR / "posix-offline-smoke.yml"

    assert workflow_path.is_file()

    workflow = workflow_path.read_text(encoding="utf-8")

    assert "workflow_dispatch:" in workflow
    assert "pull_request:" in workflow
    assert "macos-latest" in workflow
    assert "ubuntu-latest" in workflow
    assert "astral-sh/setup-uv@v7" in workflow
    assert "uv python install 3.11" in workflow
    assert "uv python find --managed-python 3.11" in workflow
    assert "build_offline_bundle.sh" in workflow
    assert "install_offline.sh" in workflow
    assert "install_offline.sh --add-to-path" in workflow
    assert "command -v ai-sdlc" in workflow
    assert "ai-sdlc --help" in workflow
    assert "OPENAI_CODEX" in workflow
    assert "AI_SDLC_ADAPTER_CANONICAL_SHA256" in workflow
    assert "adapter status" in workflow
    assert "run --dry-run" in workflow
    assert "posix-offline-smoke-evidence" in workflow
    assert "install.log" in workflow
    assert "help.txt" in workflow
    assert "adapter-status.txt" in workflow
    assert "run-dry-run.txt" in workflow
    assert "bundle-manifest.json" in workflow
    assert "upload-artifact" in workflow
    assert "PYTHONUTF8" in workflow
    assert "PYTHONIOENCODING" in workflow
    assert "verify_offline_bundle.py" in workflow
    assert "--require-bundled-runtime" in workflow
    assert "--install-log" in workflow


def test_loop_e2e_release_gate_covers_browser_probe_runner_changes() -> None:
    workflow_path = _WORKFLOWS_DIR / "loop-e2e-release-gate.yml"

    assert workflow_path.is_file()

    workflow = workflow_path.read_text(encoding="utf-8")

    assert "scripts/loop_e2e_release_gate.py" in workflow
    assert "scripts/frontend_browser_gate_probe_runner.mjs" in workflow


def test_release_artifact_smoke_workflow_installs_published_assets() -> None:
    workflow_path = _WORKFLOWS_DIR / "release-artifact-smoke.yml"

    assert workflow_path.is_file()

    workflow = workflow_path.read_text(encoding="utf-8")

    assert "workflow_dispatch:" in workflow
    assert "release:" in workflow
    assert "default: v0.9.8" in workflow
    assert "gh release download" in workflow
    assert "windows-latest" in workflow
    assert "macos-latest" in workflow
    assert "ubuntu-latest" in workflow
    assert "ai-sdlc-offline-*-windows-*.zip" in workflow
    assert "ai-sdlc-offline-*-${RELEASE_ASSET_OS}-*.tar.gz" in workflow
    assert "RELEASE_ASSET_OS" in workflow
    assert "install_offline.ps1" in workflow
    assert "./install_offline.sh" in workflow
    assert "actions/setup-python@v6" in workflow
    assert "verify_offline_bundle.py" in workflow
    assert "--require-bundled-runtime" in workflow
    assert "--install-log" in workflow
    assert "verify_offline_bundle.py failed with exit code" in workflow
    assert "adapter status" in workflow
    assert "run --dry-run" in workflow
    assert "actions/upload-artifact@v7" in workflow
    assert "WindowsPowerShell\\v1.0\\powershell.exe" in workflow
    assert "-NoProfile -ExecutionPolicy Bypass -File .\\install_offline.ps1 -AddToPath" in workflow
    assert '$cliDir = Join-Path $bundleDir.FullName ".venv\\Scripts"' in workflow
    assert "$env:Path = $cliDir + [IO.Path]::PathSeparator + $env:Path" in workflow
    assert "Get-Command ai-sdlc" in workflow
    assert "ai-sdlc --help" in workflow
    assert "install_offline.sh --add-to-path" in workflow
    assert "command -v ai-sdlc" in workflow


def test_release_build_workflow_matrix_builds_smokes_and_uploads_assets() -> None:
    workflow_path = _WORKFLOWS_DIR / "release-build.yml"

    assert workflow_path.is_file()

    workflow = workflow_path.read_text(encoding="utf-8")

    assert "workflow_dispatch:" in workflow
    assert "default: v0.9.8" in workflow
    assert "windows-latest" in workflow
    assert "macos-latest" in workflow
    assert "ubuntu-latest" in workflow
    assert "AI_SDLC_OFFLINE_ASSET_SUFFIX" in workflow
    assert "AI_SDLC_OFFLINE_PYTHON_RUNTIME" in workflow
    assert "uv python install 3.11" in workflow
    assert "uv python find --managed-python 3.11" in workflow
    assert "build_offline_bundle.sh" in workflow
    assert "install_offline.ps1" in workflow
    assert "./install_offline.sh" in workflow
    assert "verify_offline_bundle.py" in workflow
    assert "--require-bundled-runtime" in workflow
    assert "--install-log" in workflow
    assert "verify_offline_bundle.py failed with exit code" in workflow
    assert "adapter status" in workflow
    assert "run --dry-run" in workflow
    assert "actions/upload-artifact@v7" in workflow
    assert "gh release upload" in workflow
    assert "WindowsPowerShell\\v1.0\\powershell.exe" in workflow
    assert "-NoProfile -ExecutionPolicy Bypass -File .\\install_offline.ps1 -AddToPath" in workflow
    assert '$cliDir = Join-Path $bundleDir.FullName ".venv\\Scripts"' in workflow
    assert "$env:Path = $cliDir + [IO.Path]::PathSeparator + $env:Path" in workflow
    assert "Get-Command ai-sdlc" in workflow
    assert "ai-sdlc --help" in workflow
    assert "install_offline.sh --add-to-path" in workflow
    assert "command -v ai-sdlc" in workflow


def test_release_build_workflow_requires_exact_tag_checkout() -> None:
    workflow = yaml.safe_load(
        (_WORKFLOWS_DIR / "release-build.yml").read_text(encoding="utf-8")
    )
    steps = workflow["jobs"]["build-smoke-upload"]["steps"]
    checkout = next(step for step in steps if step.get("uses") == "actions/checkout@v6")

    assert checkout["with"]["ref"] == "${{ inputs.tag }}"
    assert checkout["with"]["fetch-depth"] == 0

    guard = next(step for step in steps if "git rev-parse" in step.get("run", ""))
    guard_script = guard["run"]
    build_index = next(
        index for index, step in enumerate(steps) if step.get("name") == "Build offline bundle"
    )
    assert steps.index(checkout) < steps.index(guard) < build_index
    assert "GITHUB_REF" in guard_script
    assert 'refs/tags/${RELEASE_TAG}' in guard_script
    assert '${RELEASE_TAG}^{commit}' in guard_script
    assert "GITHUB_SHA" in guard_script


def test_release_build_workflow_grants_native_attestation_permissions() -> None:
    workflow = yaml.safe_load(
        (_WORKFLOWS_DIR / "release-build.yml").read_text(encoding="utf-8")
    )

    assert workflow["permissions"] == {
        "contents": "write",
        "id-token": "write",
        "attestations": "write",
        "artifact-metadata": "write",
    }


def test_release_build_workflow_attests_and_verifies_before_release_upload() -> None:
    workflow_path = _WORKFLOWS_DIR / "release-build.yml"
    workflow_text = workflow_path.read_text(encoding="utf-8")
    workflow = yaml.safe_load(workflow_text)
    steps = workflow["jobs"]["build-smoke-upload"]["steps"]

    smoke_indexes = [
        index for index, step in enumerate(steps) if step.get("name", "").startswith("Smoke ")
    ]
    attest_index = next(
        index for index, step in enumerate(steps) if step.get("uses") == "actions/attest@v4"
    )
    verify_index = next(
        index
        for index, step in enumerate(steps)
        if "gh attestation verify" in step.get("run", "")
    )
    upload_index = next(
        index
        for index, step in enumerate(steps)
        if "gh release upload" in step.get("run", "")
    )

    assert smoke_indexes
    assert max(smoke_indexes) < attest_index < verify_index < upload_index

    verify_script = steps[verify_index]["run"]
    for required_flag in (
        "--repo",
        "--signer-workflow",
        "--source-ref",
        "--source-digest",
        "--deny-self-hosted-runners",
    ):
        assert required_flag in verify_script
    assert ".provenance.json" not in workflow_text


def test_windows_user_guide_e2e_replays_existing_project_install_path() -> None:
    workflow_path = _WORKFLOWS_DIR / "windows-user-guide-e2e.yml"

    assert workflow_path.is_file()

    workflow = workflow_path.read_text(encoding="utf-8")

    assert "workflow_dispatch:" in workflow
    assert "pull_request:" in workflow
    assert "windows-latest" in workflow
    assert "default: v0.9.8" in workflow
    assert "Build Windows offline bundle for pull request replay" in workflow
    assert "build_offline_bundle.sh" in workflow
    assert 'AI_SDLC_OFFLINE_ASSET_SUFFIX="-windows-amd64"' in workflow
    assert "pull_request_local_bundle" in workflow
    assert "USER_GUIDE.zh-CN.md Chapter 2, Scenario B" in workflow
    assert "my-existing-project" in workflow
    assert '$releaseVersion = $env:RELEASE_TAG -replace' in workflow
    assert '$BundleName = "ai-sdlc-offline-$releaseVersion-windows-amd64"' in workflow
    assert "releases/download/$env:RELEASE_TAG/$PackageName" in workflow
    assert "Invoke-WebRequest" in workflow
    assert "Expand-Archive" in workflow
    assert "-ExecutionPolicy Bypass -File .\\install_offline.ps1 -AddToPath" in workflow
    assert ".\\.venv\\Scripts\\python.exe -m ai_sdlc --help" in workflow
    assert "Direct shim" in workflow
    assert "Codex \\+ PowerShell project init" in workflow
    assert "released-package-guide-gap.txt" in workflow
    assert "& $directShim init . --agent-target codex --shell powershell" in workflow
    assert "当前结果 / Result" in workflow
    assert "下一步 / Next" in workflow
    assert "adapter ingress|materialized|unverified|host ingress" in workflow
    assert "& $directShim adopt ." in workflow
    assert "接入已有项目" in workflow
    assert "business-file-hashes-before.txt" in workflow
    assert "business-file-hashes-after.txt" in workflow
    assert "Compare-Object" in workflow
    assert "init/adopt modified existing business files" in workflow
    assert "windows-user-guide-existing-project-evidence" in workflow
    assert "actions/upload-artifact@v7" in workflow


def test_windows_user_guide_e2e_verifies_natural_release_before_install() -> None:
    workflow = yaml.safe_load(
        (_WORKFLOWS_DIR / "windows-user-guide-e2e.yml").read_text(encoding="utf-8")
    )
    events = workflow.get("on", workflow.get(True))
    job = workflow["jobs"]["existing-project-online-install"]
    steps = job["steps"]
    checkout = next(step for step in steps if step.get("uses") == "actions/checkout@v6")
    replay = next(
        step for step in steps if step.get("name") == "Replay Windows existing-project guide path"
    )["run"]

    assert events["release"]["types"] == ["published"]
    assert workflow["concurrency"] == {
        "group": "windows-user-guide-e2e-${{ github.event_name }}-${{ github.event.pull_request.number || github.event.release.tag_name || inputs.tag || github.ref }}",
        "cancel-in-progress": True,
    }
    assert "github.event.release.tag_name" in job["env"]["RELEASE_TAG"]
    assert "github.event.release.tag_name" in checkout["with"]["ref"]
    assert '$releaseVersion = $env:RELEASE_TAG -replace' in replay
    assert '$releaseRepository = if ($env:GITHUB_EVENT_NAME -eq "release")' in replay
    assert '$env:GITHUB_REPOSITORY' in replay
    assert '"sinclairpan-git/Ai_AutoSDLC"' in replay
    assert 'https://github.com/$releaseRepository/releases/download/$env:RELEASE_TAG/$PackageName' in replay
    assert "USER_GUIDE.zh-CN.md" in replay

    verify_index = replay.index("gh attestation verify")
    assert replay.index("Invoke-WebRequest") < verify_index < replay.index("Expand-Archive")
    for required_contract in (
        "--signer-workflow",
        "--source-ref",
        "--source-digest",
        "--deny-self-hosted-runners",
        "buildTrigger",
        "workflow_dispatch",
    ):
        assert required_contract in replay


def test_windows_user_guide_e2e_records_recovery_bound_r02_receipt() -> None:
    workflow = yaml.safe_load(
        (_WORKFLOWS_DIR / "windows-user-guide-e2e.yml").read_text(encoding="utf-8")
    )
    steps = workflow["jobs"]["existing-project-online-install"]["steps"]
    replay = next(
        step for step in steps if step.get("name") == "Replay Windows existing-project guide path"
    )["run"]

    assert "resume-pack.yaml" in replay
    assert "& $directShim recover" in replay
    assert '$receiptStatus = if ($env:GITHUB_EVENT_NAME -eq "release")' in replay
    assert '"proven"' in replay
    assert '"partial"' in replay
    assert "route-receipt.json" in replay
    assert '$workflowRepository = $env:GITHUB_REPOSITORY' in replay
    assert '$workflowCommit = $env:GITHUB_SHA' in replay
    assert 'git ls-remote --exit-code "https://github.com/$releaseRepository.git"' in replay
    assert 'asset = [ordered]@{ repository = $releaseRepository; tag = $env:RELEASE_TAG; commit = $assetCommit }' in replay
    assert 'workflow = [ordered]@{ repository = $workflowRepository; commit = $workflowCommit; event = $env:GITHUB_EVENT_NAME; run_id = $env:GITHUB_RUN_ID }' in replay
    for evidence_field in (
        "route_id",
        "environment",
        "project_mode",
        "acquisition_mode",
        "source_binding",
        "asset_integrity",
        "installation",
        "lifecycle",
        "result_next",
        "success_receipt",
        "fault_recovery",
        "evidence_links",
    ):
        assert evidence_field in replay


def test_macos_user_guide_e2e_verifies_natural_release_before_install() -> None:
    workflow_path = _WORKFLOWS_DIR / "macos-user-guide-e2e.yml"

    assert workflow_path.is_file()

    workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
    events = workflow.get("on", workflow.get(True))
    job = workflow["jobs"]["existing-project-online-install"]
    steps = job["steps"]
    checkout = next(step for step in steps if step.get("uses") == "actions/checkout@v6")
    architecture_guard = next(
        step for step in steps if step.get("name") == "Verify macOS arm64 runner"
    )
    replay = next(
        step for step in steps if step.get("name") == "Replay macOS existing-project guide path"
    )["run"]

    assert events["release"]["types"] == ["published"]
    assert "pyproject.toml" in events["pull_request"]["paths"]
    assert job["runs-on"] == "macos-latest"
    assert workflow["permissions"] == {"contents": "read", "attestations": "read"}
    assert "github.event.release.tag_name" in job["env"]["RELEASE_TAG"]
    assert "github.event.release.tag_name" in checkout["with"]["ref"]
    assert steps.index(architecture_guard) < next(
        index
        for index, step in enumerate(steps)
        if step.get("name") == "Build macOS offline bundle for pull request replay"
    )
    assert "uname -m" in architecture_guard["run"]
    assert "arm64|aarch64" in architecture_guard["run"]
    assert '"${direct_tag_ref}" "${peeled_tag_ref}"' in replay
    assert (
        '''release_version="$(awk -F'"' '/^version =/ {print $2; exit}' "${GITHUB_WORKSPACE}/pyproject.toml")"'''
        in replay
    )

    verify_index = replay.index("gh attestation verify")
    install_index = replay.index("bash ./install_offline.sh --add-to-path")
    assert replay.index("curl --fail --location") < verify_index < install_index
    for required_contract in (
        "--signer-workflow",
        "--source-ref",
        "--source-digest",
        "--deny-self-hosted-runners",
        "buildTrigger",
        "workflow_dispatch",
    ):
        assert required_contract in replay


def test_macos_user_guide_e2e_records_recovery_bound_r06_receipt() -> None:
    workflow = yaml.safe_load(
        (_WORKFLOWS_DIR / "macos-user-guide-e2e.yml").read_text(encoding="utf-8")
    )
    steps = workflow["jobs"]["existing-project-online-install"]["steps"]
    replay = next(
        step for step in steps if step.get("name") == "Replay macOS existing-project guide path"
    )["run"]

    assert 'route_id: "R06"' in replay
    assert 'os: "macos"' in replay
    assert 'architecture: "arm64"' in replay
    assert 'kind: "existing"' in replay
    assert "init-existing-project.txt" in replay
    assert "adopt-existing-project.txt" in replay
    assert "recover-corrupted-resume-pack.txt" in replay
    assert "business-file-hashes-before.txt" in replay
    assert "business-file-hashes-after.txt" in replay
    assert "/bin/zsh -ic 'command -v ai-sdlc && ai-sdlc --help'" in replay
    assert (
        "/bin/zsh -ic 'ai-sdlc init . --agent-target codex --shell zsh'" in replay
    )
    assert '"${direct_shim}" init .' not in replay
    assert 'grep -Fq "不用再手动执行初始化命令"' in replay
    assert 'grep -Fq "AI 对话"' in replay
    assert 'receipt_status="proven"' in replay
    assert 'receipt_status="partial"' in replay
    assert "route-receipt.json" in replay
    for evidence_field in (
        "route_id",
        "environment",
        "project_mode",
        "acquisition_mode",
        "source_binding",
        "asset_integrity",
        "installation",
        "lifecycle",
        "result_next",
        "success_receipt",
        "fault_recovery",
        "evidence_links",
    ):
        assert evidence_field in replay


def test_posix_offline_smoke_matrix_concurrency_is_job_scoped() -> None:
    workflow_path = _WORKFLOWS_DIR / "posix-offline-smoke.yml"

    workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

    assert "concurrency" not in workflow
    assert workflow["jobs"]["smoke"]["concurrency"] == {
        "group": "posix-offline-smoke-${{ github.event.pull_request.number || github.ref }}-${{ matrix.os }}",
        "cancel-in-progress": True,
    }


def test_github_workflows_use_node24_compatible_core_actions() -> None:
    legacy_actions = {
        "actions/checkout@v4",
        "actions/setup-python@v5",
    }

    for workflow_path in sorted(_WORKFLOWS_DIR.glob("*.yml")):
        workflow = workflow_path.read_text(encoding="utf-8")
        for legacy_action in legacy_actions:
            assert legacy_action not in workflow, (
                f"{workflow_path.relative_to(_REPO_ROOT)} still uses {legacy_action}"
            )
