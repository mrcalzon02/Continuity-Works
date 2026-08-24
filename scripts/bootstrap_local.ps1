$ErrorActionPreference = "Stop"
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m unittest discover -s tests -v
Write-Host "Ready. Run: .\.venv\Scripts\Activate.ps1; structure-capability serve"
