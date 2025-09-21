# Starts Django dev server using the project's virtual environment
param(
    [int]$Port = 8000
)

$ErrorActionPreference = 'Stop'

# Go to project root (this script is in scripts/)
Set-Location (Split-Path -Parent $PSScriptRoot)

# Activate venv (allow script execution for this session)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass | Out-Null
. .\.venv\Scripts\Activate.ps1

# Ensure dependencies are present (no-op if already installed)
# Use python -m pip consistently to avoid pip alias issues
python -m pip install --quiet --disable-pip-version-check -r requirements.txt requests 2>$null | Out-Null

# Apply migrations and runserver
python manage.py migrate
python manage.py runserver $Port
