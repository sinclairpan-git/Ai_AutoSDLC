param(
  [string]$VenvPath = ".venv",
  [string]$PackageSpec = "ai-sdlc",
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
  Write-Host "  $StatusEn"
  Write-Host ""
  Write-Host "Next"
  Write-Host "  $Command"
  Write-Host "  $Purpose"
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

function Add-DirectoryToUserPath {
  param([string]$Directory)

  $resolvedDirectory = (Resolve-Path -LiteralPath $Directory).Path
  $currentUserPath = [Environment]::GetEnvironmentVariable("Path", "User")
  if (-not $currentUserPath) {
    $currentUserPath = ""
  }
  $entries = @($currentUserPath -split [IO.Path]::PathSeparator | Where-Object { $_ })
  $alreadyPresent = $false
  foreach ($entry in $entries) {
    if ($entry.TrimEnd('\') -ieq $resolvedDirectory.TrimEnd('\')) {
      $alreadyPresent = $true
      break
    }
  }
  if (-not $alreadyPresent) {
    $updatedPath = if ($currentUserPath) {
      $currentUserPath + [IO.Path]::PathSeparator + $resolvedDirectory
    } else {
      $resolvedDirectory
    }
    [Environment]::SetEnvironmentVariable("Path", $updatedPath, "User")
  }
  $sessionEntries = @($env:Path -split [IO.Path]::PathSeparator | Where-Object { $_ })
  $sessionPresent = $false
  foreach ($entry in $sessionEntries) {
    if ($entry.TrimEnd('\') -ieq $resolvedDirectory.TrimEnd('\')) {
      $sessionPresent = $true
      break
    }
  }
  if (-not $sessionPresent) {
    $env:Path = $resolvedDirectory + [IO.Path]::PathSeparator + $env:Path
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
    -Status "Python 3.11+ was not detected, and online auto-install could not be completed on this host." `
    -StatusEn "Python 3.11+ was not detected, and online auto-install could not be completed on this host." `
    -Command ".\packaging\install_online.ps1" `
    -Purpose "Rerun this script on a host with winget or choco available." `
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
$cliExe = Join-Path $VenvPath "Scripts\ai-sdlc.exe"
$resolvedCliExe = (Resolve-Path -LiteralPath $cliExe).Path
$cliDir = Split-Path -Parent $resolvedCliExe
$callOperator = [char]38
$doubleQuote = [char]34
$directInitCommand = 'cd YOUR_PROJECT_PATH; {0} {1}{2}{1} init .' -f $callOperator, $doubleQuote, $resolvedCliExe
if ($AddToPath) {
  Add-DirectoryToUserPath $cliDir
  $nextCommand = $directInitCommand
} else {
  $nextCommand = 'cd YOUR_PROJECT_PATH; Start-Process -Wait -NoNewWindow -FilePath {0}{1}{0} -ArgumentList ''-m'', ''ai_sdlc'', ''init'', ''.''' -f $doubleQuote, $resolvedVenvPython
}

Write-Host ""
Write-BilingualStatus `
  -Status "Online installation completed. The installer created the runtime and installed AI-SDLC." `
  -StatusEn "Online installation completed. The installer created the runtime and installed AI-SDLC." `
  -Command $nextCommand `
  -Purpose "Enter your project and initialize it; init will automatically run the required checks and safe rehearsal." `
  -PurposeEn "Enter your project and initialize it; init will automatically run the required checks and safe rehearsal."
Write-Host ""
if ($AddToPath) {
  Write-Host "PATH consent:"
  Write-Host "  -AddToPath was provided, so the installer wrote User PATH for future terminals."
  Write-Host "  The current parent terminal may still resolve an older ai-sdlc command."
  Write-Host "PATH entry added:"
  Write-Host "  $cliDir"
  Write-Host "Check resolved command before using bare ai-sdlc:"
  Write-Host "  Get-Command ai-sdlc | Select-Object Source"
} else {
  Write-Host "PATH was not changed. Rerun with -AddToPath to enable bare ai-sdlc commands."
}
Write-Host "Direct shim:"
Write-Host ('  {0} {1}{2}{1} init .' -f $callOperator, $doubleQuote, $resolvedCliExe)
Write-Host ('  {0} {1}{2}{1} --help' -f $callOperator, $doubleQuote, $resolvedCliExe)
Write-Host ('  {0} {1}{2}{1} -m ai_sdlc --help' -f $callOperator, $doubleQuote, $resolvedVenvPython)
