param(
  [switch]$SkipTests
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

if (-not (Test-Path .\.venv\Scripts\python.exe)) {
  Write-Host "Create venv first: python -m venv .venv"
  exit 1
}

.\.venv\Scripts\python.exe -m pip install -U pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"

.\.venv\Scripts\ruff.exe check .
.\.venv\Scripts\ruff.exe format --check .

if (-not $SkipTests) {
  .\.venv\Scripts\pytest.exe -m "not integration"
}

Write-Host "Launch app with: .\.venv\Scripts\python.exe -m app.main"
