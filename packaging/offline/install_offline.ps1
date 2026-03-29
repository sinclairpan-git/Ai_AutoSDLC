param(
  [string]$VenvPath = ".venv",
  [string]$PythonExe = "python"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Wheels = Join-Path $Root "wheels"
$ManifestPath = Join-Path $Root "bundle-manifest.json"

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

& $PythonExe -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)"
if ($LASTEXITCODE -ne 0) {
  throw "Python >= 3.11 is required. Use -PythonExe to specify a correct interpreter."
}

if (Test-Path $ManifestPath) {
  $manifest = Get-Content $ManifestPath -Raw | ConvertFrom-Json
  $expectedOs = [string]$manifest.platform_os
  $expectedMachine = [string]$manifest.platform_machine
  $currentOs = "windows"
  $currentMachine = [System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture.ToString().ToLowerInvariant()
  $mismatches = @()
  if ($expectedOs -and $expectedOs.ToLowerInvariant() -ne $currentOs) {
    $mismatches += "os=$expectedOs (current=$currentOs)"
  }
  if ($expectedMachine -and $expectedMachine.ToLowerInvariant() -ne $currentMachine) {
    $mismatches += "machine=$expectedMachine (current=$currentMachine)"
  }
  if ($mismatches.Count -gt 0) {
    throw "offline bundle platform mismatch: $($mismatches -join '; '). Rebuild the bundle on the target OS/CPU or use a matching archive."
  }
  Write-Host "Validated offline bundle platform manifest."
} else {
  Write-Warning "bundle-manifest.json missing; skipping platform compatibility check."
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
Write-Host "OK. Verify (use a PowerShell session):"
Write-Host "  1) Activate venv (if Activate.ps1 is blocked, run first:"
Write-Host "       Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass"
Write-Host "  2) & '$VenvPath\\Scripts\\Activate.ps1'"
Write-Host "  3) Get-Command ai-sdlc   # optional"
Write-Host "  4) ai-sdlc --help"
Write-Host "  Or without activating PATH, call the shim directly:"
Write-Host "  & '$cliExe' --help"
Write-Host "  Or: & '$venvPython' -m ai_sdlc --help"
Write-Host "Then in your project directory:"
Write-Host "  ai-sdlc init ."
