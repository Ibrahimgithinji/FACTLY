$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = "C:\Users\DELL\OneDrive\Desktop\Factly\backend\venv\Scripts\python.exe"
$psi.Arguments = "manage.py runserver 0.0.0.0:8000"
$psi.WorkingDirectory = "C:\Users\DELL\OneDrive\Desktop\Factly\backend"
$psi.UseShellExecute = $false
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$psi.CreateNoWindow = $true
$psi.EnvironmentVariables["ALLOW_MEMORY_DB"] = "True"
$p = [System.Diagnostics.Process]::Start($psi)
Write-Output "Backend started with PID $($p.Id)"
