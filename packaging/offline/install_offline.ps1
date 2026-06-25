param(
  [string]$VenvPath = ".venv",
  [string]$PythonExe = "python",
  [switch]$UpgradeExisting,
  [switch]$AddToPath
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

function Get-ManifestPythonVersions {
  param($Manifest)

  $versions = @()
  if ($Manifest.PSObject.Properties.Name -contains "supported_python_versions") {
    foreach ($item in @($Manifest.supported_python_versions)) {
      $value = [string]$item
      if ($value) {
        $versions += $value
      }
    }
  }
  if (($versions.Count -eq 0) -and ($Manifest.PSObject.Properties.Name -contains "wheel_python_version")) {
    $value = [string]$Manifest.wheel_python_version
    if ($value) {
      $versions += $value
    }
  }
  return $versions
}

function Write-BilingualStatus {
  param(
    [string]$Status,
    [string]$StatusEn,
    [string]$Command,
    [string]$Purpose,
    [string]$PurposeEn
  )

  Write-Host "Result"
  Write-Host "  $Status"
  if ($StatusEn -and ($StatusEn -ne $Status)) {
    Write-Host "  $StatusEn"
  }
  Write-Host ""
  Write-Host "Next"
  Write-Host "  $Command"
  Write-Host "  $Purpose"
  if ($PurposeEn -and ($PurposeEn -ne $Purpose)) {
    Write-Host "  $PurposeEn"
  }
}

function Normalize-PathEntry {
  param([string]$Directory)

  try {
    return (Resolve-Path -LiteralPath $Directory).Path.TrimEnd('\').ToLowerInvariant()
  } catch {
    return $Directory.TrimEnd('\').ToLowerInvariant()
  }
}

function Set-PreferredAiSdlcPath {
  param(
    [string]$PathValue,
    [string]$PreferredDirectory
  )

  $preferredKey = Normalize-PathEntry $PreferredDirectory
  $result = @($PreferredDirectory)
  $seen = @{}
  $seen[$preferredKey] = $true
  foreach ($entry in @($PathValue -split [IO.Path]::PathSeparator | Where-Object { $_ })) {
    $key = Normalize-PathEntry $entry
    if ($seen.ContainsKey($key)) {
      continue
    }
    $seen[$key] = $true
    $result += $entry
  }
  return ($result -join [IO.Path]::PathSeparator)
}

function Sync-AiSdlcLauncherDirectory {
  param(
    [string]$SourceShimDirectory,
    [string]$TargetDirectory
  )

  try {
    if (-not (Test-Path $TargetDirectory)) {
      return
    }
    $sourceKey = Normalize-PathEntry $SourceShimDirectory
    $targetKey = Normalize-PathEntry $TargetDirectory
    if ($sourceKey -eq $targetKey) {
      return
    }
    $hasLauncher = $false
    foreach ($fileName in @("ai-sdlc.exe", "ai-sdlc.cmd", "ai-sdlc.ps1")) {
      if (Test-Path (Join-Path $TargetDirectory $fileName)) {
        $hasLauncher = $true
      }
    }
    if (-not $hasLauncher) {
      return
    }
    foreach ($fileName in @("ai-sdlc.exe", "ai-sdlc.cmd", "ai-sdlc-script.py", "ai-sdlc.exe.manifest", "ai-sdlc-runtime.txt")) {
      $sourcePath = Join-Path $SourceShimDirectory $fileName
      if (Test-Path $sourcePath) {
        Copy-Item -LiteralPath $sourcePath -Destination (Join-Path $TargetDirectory $fileName) -Force -ErrorAction Stop
      }
    }
    $targetPsShim = Join-Path $TargetDirectory "ai-sdlc.ps1"
    if (Test-Path $targetPsShim) {
      Remove-Item -LiteralPath $targetPsShim -Force -ErrorAction Stop
    }
  } catch {
  }
}

function Sync-AiSdlcLaunchersOnPath {
  param([string]$SourceShimDirectory)

  $seen = @{}
  foreach ($pathValue in @([Environment]::GetEnvironmentVariable("Path", "User"))) {
    foreach ($entry in @($pathValue -split [IO.Path]::PathSeparator | Where-Object { $_ })) {
      $entryKey = Normalize-PathEntry $entry
      if ($seen.ContainsKey($entryKey)) {
        continue
      }
      $seen[$entryKey] = $true
      Sync-AiSdlcLauncherDirectory -SourceShimDirectory $SourceShimDirectory -TargetDirectory $entry
    }
  }
}

function Repair-AiSdlcCommandPath {
  param([string]$Directory)

  $resolvedDirectory = (Resolve-Path -LiteralPath $Directory).Path
  $currentUserPath = [Environment]::GetEnvironmentVariable("Path", "User")
  if (-not $currentUserPath) {
    $currentUserPath = ""
  }
  $updatedPath = Set-PreferredAiSdlcPath -PathValue $currentUserPath -PreferredDirectory $resolvedDirectory
  [Environment]::SetEnvironmentVariable("Path", $updatedPath, "User")
  $env:Path = Set-PreferredAiSdlcPath -PathValue $env:Path -PreferredDirectory $resolvedDirectory
  Sync-AiSdlcLaunchersOnPath -SourceShimDirectory $resolvedDirectory
}

function Write-TextUtf8NoBom {
  param(
    [string]$Path,
    [string]$Value
  )

  $encoding = [System.Text.UTF8Encoding]::new($false)
  [System.IO.File]::WriteAllText($Path, $Value, $encoding)
}

function ConvertTo-GitBashPath {
  param([string]$PathValue)

  $resolvedPath = $PathValue
  try {
    $resolvedPath = (Resolve-Path -LiteralPath $PathValue).Path
  } catch {
    $resolvedPath = [IO.Path]::GetFullPath($PathValue)
  }
  if ($resolvedPath -match '^([A-Za-z]):\\(.*)$') {
    $drive = $matches[1].ToLowerInvariant()
    $rest = $matches[2] -replace '\\', '/'
    return "/$drive/$rest"
  }
  return ($resolvedPath -replace '\\', '/')
}

function ConvertFrom-GitBashPath {
  param([string]$PathValue)

  if ($PathValue -match '^/([A-Za-z])/(.*)$') {
    $drive = $matches[1].ToUpperInvariant()
    $rest = $matches[2] -replace '/', '\'
    return "$drive`:\$rest"
  }
  return $PathValue
}

function Get-GitBashHomeDirectory {
  $candidates = @($env:HOME, $env:USERPROFILE) | Where-Object { $_ }
  foreach ($candidate in $candidates) {
    $windowsCandidate = ConvertFrom-GitBashPath $candidate
    try {
      $fullPath = [IO.Path]::GetFullPath($windowsCandidate)
      if (Test-Path $fullPath) {
        return $fullPath
      }
    } catch {
    }
  }
  return $null
}

function Get-AiSdlcShimDirectory {
  if ($env:LOCALAPPDATA) {
    return (Join-Path $env:LOCALAPPDATA "AI-SDLC\bin")
  }
  if ($env:USERPROFILE) {
    return (Join-Path $env:USERPROFILE ".ai-sdlc\bin")
  }
  return (Join-Path $Root ".ai-sdlc-bin")
}

function Install-AiSdlcCommandShim {
  param(
    [string]$CliExe,
    [string]$RuntimePython = ""
  )

  $resolvedCliExe = (Resolve-Path -LiteralPath $CliExe).Path
  $shimDir = Get-AiSdlcShimDirectory
  New-Item -ItemType Directory -Force -Path $shimDir | Out-Null

  Copy-Item -LiteralPath $resolvedCliExe -Destination (Join-Path $shimDir "ai-sdlc.exe") -Force
  $scriptPy = Join-Path (Split-Path -Parent $resolvedCliExe) (([IO.Path]::GetFileNameWithoutExtension($resolvedCliExe)) + "-script.py")
  if (Test-Path $scriptPy) {
    Copy-Item -LiteralPath $scriptPy -Destination (Join-Path $shimDir "ai-sdlc-script.py") -Force
  }
  $manifest = "$resolvedCliExe.manifest"
  if (Test-Path $manifest) {
    Copy-Item -LiteralPath $manifest -Destination (Join-Path $shimDir "ai-sdlc.exe.manifest") -Force
  }

  $cmdShim = @(
    "@echo off",
    ('"{0}" %*' -f $resolvedCliExe),
    "exit /b %ERRORLEVEL%"
  ) -join "`r`n"
  Write-TextUtf8NoBom -Path (Join-Path $shimDir "ai-sdlc.cmd") -Value $cmdShim

  $legacyPsShim = Join-Path $shimDir "ai-sdlc.ps1"
  if (Test-Path $legacyPsShim) {
    Remove-Item -LiteralPath $legacyPsShim -Force
  }

  if (-not $RuntimePython) {
    $candidateRuntimePython = Join-Path (Split-Path -Parent $resolvedCliExe) "python.exe"
    if (Test-Path $candidateRuntimePython) {
      $RuntimePython = $candidateRuntimePython
    }
  }
  if ($RuntimePython -and (Test-Path $RuntimePython)) {
    $resolvedRuntimePython = (Resolve-Path -LiteralPath $RuntimePython).Path
    Write-TextUtf8NoBom -Path (Join-Path $shimDir "ai-sdlc-runtime.txt") -Value ($resolvedRuntimePython + "`n")
  }

  return (Resolve-Path -LiteralPath $shimDir).Path
}

function Update-GitBashProfilePath {
  param([string]$Directory)

  $gitBashHome = Get-GitBashHomeDirectory
  if (-not $gitBashHome) {
    return
  }
  $bashDirectory = ConvertTo-GitBashPath $Directory
  $begin = "# >>> AI-SDLC managed PATH >>>"
  $end = "# <<< AI-SDLC managed PATH <<<"
  $block = @(
    $begin,
    'case ":$PATH:" in',
    ('  *":{0}:"*) ;;' -f $bashDirectory),
    ('  *) export PATH="{0}:$PATH" ;;' -f $bashDirectory),
    'esac',
    'hash -r 2>/dev/null || true',
    $end
  ) -join "`n"

  $profileNames = @(".bashrc")
  $loginProfileName = $null
  foreach ($candidateProfileName in @(".bash_profile", ".bash_login", ".profile")) {
    if (Test-Path (Join-Path $gitBashHome $candidateProfileName)) {
      $loginProfileName = $candidateProfileName
      break
    }
  }
  if ($loginProfileName) {
    $profileNames += $loginProfileName
  } else {
    $profileNames += ".bash_profile"
  }

  foreach ($profileName in ($profileNames | Select-Object -Unique)) {
    $profilePath = Join-Path $gitBashHome $profileName
    $content = ""
    if (Test-Path $profilePath) {
      $content = Get-Content -LiteralPath $profilePath -Raw
    }
    $pattern = "(?s)" + [regex]::Escape($begin) + ".*?" + [regex]::Escape($end) + "\r?\n?"
    $content = [regex]::Replace($content, $pattern, "")
    $content = $content.TrimEnd()
    if ($content) {
      $content = $content + "`n"
    }
    Write-TextUtf8NoBom -Path $profilePath -Value ($content + $block + "`n")
  }
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
  $existingCommandSource = (Resolve-Path -LiteralPath $aiSdlcCommand.Source).Path
  $shimDir = Split-Path -Parent $existingCommandSource
  $stableShimRuntimePath = Join-Path $shimDir "ai-sdlc-runtime.txt"
  $baseDir = Split-Path -Parent $shimDir
  $candidatePythons = @(
    $(if (Test-Path $stableShimRuntimePath) { (Get-Content -LiteralPath $stableShimRuntimePath -Raw).Trim() }),
    (Join-Path $shimDir "python.exe"),
    (Join-Path $baseDir "python.exe")
  ) | Where-Object { $_ }
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

$usingBundledPython = $false
if ((-not $UpgradeExisting) -and (Test-Path $BundledPython)) {
  try {
    $usingBundledPython = (
      (Resolve-Path -LiteralPath $PythonExe).Path -eq
      (Resolve-Path -LiteralPath $BundledPython).Path
    )
  } catch {
    $usingBundledPython = $false
  }
}

$pythonProbe = & $PythonExe -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}'); sys.exit(0 if sys.version_info >= (3, 11) else 42)" 2>&1
$pythonProbeExit = $LASTEXITCODE
if ($pythonProbeExit -ne 0) {
  $probeText = ($pythonProbe | Out-String).Trim()
  if ($pythonProbeExit -eq 42) {
    if (-not $probeText) {
      $probeText = $PythonExe
    }
    throw "Python >= 3.11 is required (found $probeText). Use -PythonExe to specify a correct interpreter."
  }
  if ($usingBundledPython) {
    if (-not $probeText) {
      $probeText = "no output"
    }
    throw "bundled Python runtime is not executable or cannot import the standard library (selected $PythonExe); this offline bundle is invalid for this machine. Details: $probeText"
  }
  if (-not $probeText) {
    $probeText = "no output"
  }
  throw "selected Python runtime failed to start (selected $PythonExe). Details: $probeText"
}

if (Test-Path $ManifestPath) {
  $manifest = Get-Content $ManifestPath -Raw | ConvertFrom-Json
  $expectedOs = [string]$manifest.platform_os
  $expectedMachine = Normalize-Architecture ([string]$manifest.platform_machine)
  $expectedPythonVersions = @(Get-ManifestPythonVersions $manifest)
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
  if (($expectedPythonVersions.Count -gt 0) -and ($expectedPythonVersions -notcontains $currentPythonVersion)) {
    $mismatches += "python=$($expectedPythonVersions -join ',') wheel ABI (selected=$currentPythonVersion)"
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
  $existingCliCandidates = @()
  if (Test-Path $stableShimRuntimePath) {
    $existingCliCandidates += (Join-Path (Split-Path -Parent $existingPython) "ai-sdlc.exe")
  }
  $existingCliCandidates += $existingCommandSource
  $existingCliCandidates += (Join-Path $shimDir "ai-sdlc.exe")
  $existingCliCandidates += (Join-Path (Split-Path -Parent $existingPython) "ai-sdlc.exe")
  $existingCli = $null
  foreach ($existingCliCandidate in ($existingCliCandidates | Select-Object -Unique)) {
    if ($existingCliCandidate -and (Test-Path $existingCliCandidate)) {
      $existingCli = $existingCliCandidate
      break
    }
  }
  if ($existingCli -and (Test-Path $existingCli)) {
    $commandShimDir = Install-AiSdlcCommandShim -CliExe $existingCli -RuntimePython $existingPython
    Repair-AiSdlcCommandPath $commandShimDir
    Update-GitBashProfilePath $commandShimDir
  }
  $pathVersionOutput = (& ai-sdlc --version 2>$null)
  if ($LASTEXITCODE -ne 0) {
    throw "current PATH still resolves an older ai-sdlc command after installation"
  }
  $pathVersion = (($pathVersionOutput | Select-Object -Last 1) -replace '\s+', '')
  if ($pathVersion -ne $expectedVersion) {
    throw "current PATH resolves ai-sdlc $pathVersion, expected $expectedVersion"
  }
  Write-Host ""
  Write-BilingualStatus `
    -Status "Upgrade completed. The package installer updated the runtime behind the current ai-sdlc command." `
    -StatusEn "Upgrade completed. The package installer updated the runtime behind the current ai-sdlc command." `
    -Command "ai-sdlc --version; ai-sdlc self-update check" `
    -Purpose "Confirm the version; future updates only need self-update check." `
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

$resolvedVenvPython = (Resolve-Path -LiteralPath $venvPython).Path
$cliExe = Join-Path $VenvPath "Scripts\\ai-sdlc.exe"
$resolvedCliExe = (Resolve-Path -LiteralPath $cliExe).Path
$callOperator = [char]38
$doubleQuote = [char]34
$cliDir = Split-Path -Parent $resolvedCliExe
$directInitCommand = 'cd YOUR_PROJECT_PATH; {0} {1}{2}{1} init .' -f $callOperator, $doubleQuote, $resolvedCliExe
$codexPowerShellInitCommand = 'cd YOUR_PROJECT_PATH; {0} {1}{2}{1} init . --agent-target codex --shell powershell' -f $callOperator, $doubleQuote, $resolvedCliExe
if ($AddToPath) {
  $commandShimDir = Install-AiSdlcCommandShim -CliExe $resolvedCliExe -RuntimePython $resolvedVenvPython
  Repair-AiSdlcCommandPath $commandShimDir
  Update-GitBashProfilePath $commandShimDir
  $nextCommand = $directInitCommand
} else {
  $nextCommand = 'cd YOUR_PROJECT_PATH; Start-Process -Wait -NoNewWindow -FilePath {0}{1}{0} -ArgumentList ''-m'', ''ai_sdlc'', ''init'', ''.''' -f $doubleQuote, $resolvedVenvPython
}
Write-Host ""
Write-BilingualStatus `
  -Status "Offline installation completed. The installer created the runtime and installed AI-SDLC." `
  -StatusEn "Offline installation completed. The installer created the runtime and installed AI-SDLC." `
  -Command $nextCommand `
  -Purpose "Enter your project and initialize it; init will automatically run the required checks and safe rehearsal." `
  -PurposeEn "Enter your project and initialize it; init will automatically run the required checks and safe rehearsal."
Write-Host ""
if ($AddToPath) {
  Write-Host "New terminals can run ai-sdlc directly."
} else {
  Write-Host "Use the full command above, or rerun with -AddToPath for new terminals."
  Write-Host "To upgrade the existing bare ai-sdlc entrypoint, rerun with -UpgradeExisting."
}
Write-Host "Direct shim:"
Write-Host ('  {0} {1}{2}{1} init .' -f $callOperator, $doubleQuote, $resolvedCliExe)
Write-Host "Codex + PowerShell project init:"
Write-Host "  $codexPowerShellInitCommand"
Write-Host ('  {0} {1}{2}{1} --help' -f $callOperator, $doubleQuote, $resolvedCliExe)
Write-Host ('  {0} {1}{2}{1} -m ai_sdlc --help' -f $callOperator, $doubleQuote, $resolvedVenvPython)
