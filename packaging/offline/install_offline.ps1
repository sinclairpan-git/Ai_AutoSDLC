param(
  [string]$VenvPath = ".venv",
  [string]$PythonExe = "python"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Wheels = Join-Path $Root "wheels"

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

Write-Host "Creating venv: $VenvPath"
& $PythonExe -m venv $VenvPath

$venvPython = Join-Path $VenvPath "Scripts\\python.exe"
if (-not (Test-Path $venvPython)) {
  throw "failed to create venv Python at $venvPython"
}

& $venvPython -m pip install --upgrade pip | Out-Null
Write-Host "Installing ai-sdlc (offline)..."
& $venvPython -m pip install --no-index --find-links "$Wheels" "$mainWheel"

Write-Host ""
Write-Host "OK. Verify:"
Write-Host "  $VenvPath\\Scripts\\Activate.ps1"
Write-Host "  ai-sdlc --help"
Write-Host "  cd C:\\your-project ; ai-sdlc init ."
