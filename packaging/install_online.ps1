param(
  [string]$VenvPath = ".venv",
  [string]$PackageSpec = "ai-sdlc"
)

$ErrorActionPreference = "Stop"

function Write-BilingualStatus {
  param(
    [string]$StatusZh,
    [string]$StatusEn,
    [string]$Command,
    [string]$PurposeZh,
    [string]$PurposeEn
  )

  Write-Host "当前状态 / Current status"
  Write-Host "  $StatusZh"
  Write-Host "  $StatusEn"
  Write-Host ""
  Write-Host "下一步命令 / Next command"
  Write-Host "  $Command"
  Write-Host ""
  Write-Host "命令作用 / What this command does"
  Write-Host "  $PurposeZh"
  Write-Host "  $PurposeEn"
}

function Get-PythonCommand {
  $candidates = @(
    @{ Command = "py"; Args = @("-3.11") },
    @{ Command = "python"; Args = @() }
  )

  foreach ($candidate in $candidates) {
    if (Get-Command $candidate.Command -ErrorAction SilentlyContinue) {
      & $candidate.Command @($candidate.Args + @("-c", "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)"))
      if ($LASTEXITCODE -eq 0) {
        return $candidate
      }
    }
  }
  return $null
}

function Install-PythonOnline {
  if (Get-Command winget -ErrorAction SilentlyContinue) {
    winget install --id Python.Python.3.11 -e --accept-package-agreements --accept-source-agreements
    return
  }
  if (Get-Command choco -ErrorAction SilentlyContinue) {
    choco install python311 -y
    return
  }
  throw "No supported Windows package manager found for automatic Python installation."
}

$python = Get-PythonCommand
if (-not $python) {
  Write-Host "No Python 3.11+ detected. Attempting online installation..."
  Install-PythonOnline
  $python = Get-PythonCommand
}

if (-not $python) {
  Write-BilingualStatus `
    -StatusZh "当前主机未检测到 Python 3.11+，且无法自动完成在线安装。" `
    -StatusEn "Python 3.11+ was not detected, and online auto-install could not be completed on this host." `
    -Command ".\packaging\install_online.ps1" `
    -PurposeZh "在具备 winget 或 choco 的环境中重新执行此脚本。" `
    -PurposeEn "Rerun this script on a host with winget or choco available."
  exit 1
}

Write-Host ("Using Python runtime: {0} {1}" -f $python.Command, ($python.Args -join " "))
& $python.Command @($python.Args + @("-m", "venv", $VenvPath))

$venvPython = Join-Path $VenvPath "Scripts\python.exe"
& $venvPython -m pip install --upgrade pip | Out-Null
& $venvPython -m pip install $PackageSpec

Write-Host ""
Write-BilingualStatus `
  -StatusZh "在线安装完成，可以进入项目检查 adapter 接入真值并执行安全预演。" `
  -StatusEn "Online installation completed. Enter your project, inspect adapter ingress truth, and run the safe rehearsal." `
  -Command "& '$VenvPath\Scripts\Activate.ps1'; ai-sdlc adapter status; ai-sdlc run --dry-run" `
  -PurposeZh "激活 venv，检查 adapter 接入真值，再执行安全预演；run --dry-run 只证明 CLI 预演成功，不证明治理已激活。" `
  -PurposeEn "Activate the venv, inspect adapter ingress truth, then run the safe rehearsal; run --dry-run only proves the CLI rehearsal succeeded, not governance activation."

