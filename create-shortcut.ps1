$desktop = [Environment]::GetFolderPath('Desktop')
$ws = New-Object -ComObject WScript.Shell
$sc = $ws.CreateShortcut("$desktop\Start Nerval Ops.lnk")
$sc.TargetPath = 'powershell.exe'
$sc.Arguments = '-NoExit -NoProfile -ExecutionPolicy Bypass -File "C:\Users\manish\code\nerval-ops\start-dev.ps1"'
$sc.WorkingDirectory = 'C:\Users\manish\code\nerval-ops'
$sc.IconLocation = 'powershell.exe,0'
$sc.Description = 'Start Nerval Ops dashboard (backend + frontend)'
$sc.Save()
Write-Output "Shortcut created at $desktop\Start Nerval Ops.lnk"
