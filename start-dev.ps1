$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot

$backend = @"
Set-Location '$root\backend'
. .\.venv\Scripts\Activate.ps1
python wsgi.py
"@

$frontend = @"
Set-Location '$root\frontend'
npm run dev
"@

Start-Process powershell -ArgumentList '-NoExit', '-Command', $backend
Start-Sleep -Seconds 2
Start-Process powershell -ArgumentList '-NoExit', '-Command', $frontend

# Wait for the SvelteKit dev server to start responding, then open browser
Write-Host 'Waiting for http://localhost:5173/ ...'
$deadline = (Get-Date).AddSeconds(45)
$opened = $false
while ((Get-Date) -lt $deadline) {
    try {
        $null = Invoke-WebRequest -Uri 'http://localhost:5173/' -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        Start-Process 'http://localhost:5173/'
        $opened = $true
        break
    } catch {
        Start-Sleep -Seconds 1
    }
}
if (-not $opened) {
    Write-Host 'Frontend did not respond within 45s. Open http://localhost:5173/ manually once the dev server finishes starting.'
}
