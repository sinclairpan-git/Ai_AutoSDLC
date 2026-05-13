param(
  [string]$VenvPath = ".venv",
  [string]$PackageSpec = "ai-sdlc"
)

$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
try {
  $utf8 = [System.Text.UTF8Encoding]::new($false)
  [Console]::InputEncoding = $utf8
  [Console]::OutputEncoding = $utf8
  $OutputEncoding = $utf8
} catch {
  Write-Warning "Unable to force UTF-8 console encoding: $_"
}

function Write-BilingualStatus {
  param(
    [string]$StatusZh,
    [string]$StatusEn,
    [string]$Command,
    [string]$PurposeZh,
    [string]$PurposeEn
  )

  Write-Host "当前结果 / Result"
  Write-Host "  $StatusZh"
  Write-Host "  $StatusEn"
  Write-Host ""
  Write-Host "下一步 / Next"
  Write-Host "  $Command"
  Write-Host "  $PurposeZh"
  Write-Host "  $PurposeEn"
}

function Assert-LastExitCode {
  param(
    [string]$Operation
  )

  if ($LASTEXITCODE -ne 0) {
    throw "$Operation failed with exit code $LASTEXITCODE."
  }
}

function Get-PythonCommand {
  $candidates = @(
    @{ Command = "py"; Args = @("-3") },
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
    return $true
  }
  if (Get-Command choco -ErrorAction SilentlyContinue) {
    choco install python311 -y
    return $true
  }
  return $false
}

$python = Get-PythonCommand
if (-not $python) {
  Write-Host "No Python 3.11+ detected. Attempting online installation..."
  $installAttempted = $false
  try {
    $installAttempted = Install-PythonOnline
  } catch {
    Write-Host "Automatic Python installation failed: $_"
  }
  if (-not $installAttempted) {
    Write-Host "Automatic Python installation could not be completed on this host."
  }
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
Assert-LastExitCode "python -m venv"

$venvPython = Join-Path $VenvPath "Scripts\python.exe"
& $venvPython -m pip install --upgrade pip | Out-Null
Assert-LastExitCode "pip install --upgrade pip"
& $venvPython -m pip install $PackageSpec
Assert-LastExitCode "pip install $PackageSpec"

$resolvedVenvPython = (Resolve-Path -LiteralPath $venvPython).Path
$doubleQuote = [char]34
$nextCommand = 'cd YOUR_PROJECT_PATH; Start-Process -Wait -NoNewWindow -FilePath {0}{1}{0} -ArgumentList ''-m'', ''ai_sdlc'', ''init'', ''.''' -f $doubleQuote, $resolvedVenvPython

Write-Host ""
Write-BilingualStatus `
  -StatusZh "在线安装完成。安装脚本已创建运行环境并安装 AI-SDLC。" `
  -StatusEn "Online installation completed. The installer created the runtime and installed AI-SDLC." `
  -Command $nextCommand `
  -PurposeZh "进入你的项目后执行初始化；init 会自动完成必要检查和安全预演。" `
  -PurposeEn "Enter your project and initialize it; init will automatically run the required checks and safe rehearsal."
