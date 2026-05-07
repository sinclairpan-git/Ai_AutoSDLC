param(
  [string]$VenvPath = ".venv",
  [string]$PythonExe = "python",
  [switch]$UpgradeExisting
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
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Wheels = Join-Path $Root "wheels"
$ManifestPath = Join-Path $Root "bundle-manifest.json"
$BundledPython = Join-Path $Root "python-runtime\python.exe"

function Normalize-Architecture {
  param([string]$Value)

  $normalized = $Value.ToLowerInvariant()
  switch ($normalized) {
    "x64" { return "amd64" }
    "amd64" { return "amd64" }
    "x86_64" { return "amd64" }
    "arm64" { return "arm64" }
    "aarch64" { return "arm64" }
    default { return $normalized }
  }
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

if (-not (Test-Path $Wheels)) {
  throw "missing wheels directory next to this script"
}

$mainWheels = Get-ChildItem -Path $Wheels -Filter "ai_sdlc-*.whl" -File
if ($mainWheels.Count -eq 0) {
  throw "no ai_sdlc-*.whl found under wheels"
}
if ($mainWheels.Count -gt 1) {
  throw "multiple ai_sdlc wheels found; keep only one version in wheels"
}
$mainWheel = $mainWheels[0].FullName

if ($UpgradeExisting) {
  $aiSdlcCommand = Get-Command ai-sdlc -ErrorAction Stop
  $shimDir = Split-Path -Parent $aiSdlcCommand.Source
  $baseDir = Split-Path -Parent $shimDir
  $candidatePythons = @(
    (Join-Path $shimDir "python.exe"),
    (Join-Path $baseDir "python.exe")
  )
  $existingPython = $null
  foreach ($candidatePython in $candidatePythons) {
    if (Test-Path $candidatePython) {
      $existingPython = $candidatePython
      break
    }
  }
  if (-not $existingPython) {
    throw "cannot find the Python runtime behind the current ai-sdlc command; run normal install instead"
  }
  $PythonExe = $existingPython
  Write-Host "Using existing AI-SDLC runtime: $PythonExe"
} elseif ((-not $PSBoundParameters.ContainsKey("PythonExe")) -and (Test-Path $BundledPython)) {
  $PythonExe = $BundledPython
  Write-Host "Using bundled Python runtime: $PythonExe"
} else {
  Write-Host "Using detected Python runtime: $PythonExe"
}

& $PythonExe -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)"
if ($LASTEXITCODE -ne 0) {
  throw "Python >= 3.11 is required. Use -PythonExe to specify a correct interpreter."
}

if (Test-Path $ManifestPath) {
  $manifest = Get-Content $ManifestPath -Raw | ConvertFrom-Json
  $expectedOs = [string]$manifest.platform_os
  $expectedMachine = Normalize-Architecture ([string]$manifest.platform_machine)
  $expectedPythonVersion = [string]$manifest.wheel_python_version
  $currentOs = "windows"
  $currentMachine = Normalize-Architecture (
    [System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture.ToString()
  )
  $currentPythonVersion = (& $PythonExe -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')").Trim()
  $mismatches = @()
  if ($expectedOs -and $expectedOs.ToLowerInvariant() -ne $currentOs) {
    $mismatches += "os=$expectedOs (current=$currentOs)"
  }
  if ($expectedMachine -and $expectedMachine.ToLowerInvariant() -ne $currentMachine) {
    $mismatches += "machine=$expectedMachine (current=$currentMachine)"
  }
  if ($expectedPythonVersion -and $expectedPythonVersion -ne $currentPythonVersion) {
    $mismatches += "python=$expectedPythonVersion wheel ABI (selected=$currentPythonVersion)"
  }
  if ($mismatches.Count -gt 0) {
    throw "offline bundle platform mismatch: $($mismatches -join '; '). Rebuild the bundle on the target OS/CPU/Python ABI or use a matching archive."
  }
  Write-Host "Validated offline bundle platform manifest."
} else {
  Write-Warning "bundle-manifest.json missing; skipping platform compatibility check."
}

if ($UpgradeExisting) {
  Write-Host "Upgrading current ai-sdlc installation from this offline bundle..."
  & $PythonExe -m pip install --force-reinstall --no-index --find-links "$Wheels" "$mainWheel"
  if ($LASTEXITCODE -ne 0) {
    throw "failed to upgrade the current ai-sdlc installation"
  }
  $expectedVersion = $mainWheels[0].BaseName -replace '^ai_sdlc-', '' -replace '-.*$', ''
  $installedVersion = (& $PythonExe -c "from importlib.metadata import version; print(version('ai-sdlc'))").Trim()
  if ($installedVersion -ne $expectedVersion) {
    throw "installed version is $installedVersion, expected $expectedVersion"
  }
  & ai-sdlc self-update install --help | Out-Null
  if ($LASTEXITCODE -ne 0) {
    throw "current PATH still resolves an older ai-sdlc command after installation"
  }
  Write-Host ""
  Write-BilingualStatus `
    -StatusZh "升级完成。安装包已覆盖当前 ai-sdlc 入口对应的运行环境。" `
    -StatusEn "Upgrade completed. The package installer updated the runtime behind the current ai-sdlc command." `
    -Command "ai-sdlc --version; ai-sdlc self-update check" `
    -PurposeZh "确认版本；以后更新只执行 self-update check。" `
    -PurposeEn "Confirm the version; future updates only need self-update check."
  exit 0
}

Write-Host "Creating venv: $VenvPath"
& $PythonExe -m venv $VenvPath

$venvPython = Join-Path $VenvPath "Scripts\\python.exe"
if (-not (Test-Path $venvPython)) {
  throw "failed to create venv Python at $venvPython"
}

& $venvPython -m pip install --upgrade pip | Out-Null
Write-Host "Installing ai-sdlc (offline)..."
& $venvPython -m pip install --no-index --find-links "$Wheels" "$mainWheel"

$cliExe = Join-Path $VenvPath "Scripts\\ai-sdlc.exe"
Write-Host ""
Write-BilingualStatus `
  -StatusZh "离线安装完成。安装脚本已创建运行环境并安装 AI-SDLC。" `
  -StatusEn "Offline installation completed. The installer created the runtime and installed AI-SDLC." `
  -Command "& '$VenvPath\\Scripts\\Activate.ps1'; cd <your-project>; ai-sdlc init ." `
  -PurposeZh "进入你的项目后执行初始化；init 会自动完成必要检查和安全预演。" `
  -PurposeEn "Enter your project and initialize it; init will automatically run the required checks and safe rehearsal."
Write-Host ""
Write-Host "Direct shim / 直接调用:"
Write-Host "  & '$cliExe' --help"
Write-Host "  & '$venvPython' -m ai_sdlc --help"
