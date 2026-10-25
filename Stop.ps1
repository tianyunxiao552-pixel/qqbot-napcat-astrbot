foreach ($name in @('astrbot', 'napcat', 'gpt_sovits')) {
    $pidFile = Join-Path $PSScriptRoot "logs\$name.pid"
    if (Test-Path -LiteralPath $pidFile) {
        $servicePid = [int](Get-Content -LiteralPath $pidFile)
        $service = Get-CimInstance Win32_Process -Filter "ProcessId=$servicePid" -ErrorAction SilentlyContinue
        if ($service -and $service.ExecutablePath -and $service.ExecutablePath.StartsWith($PSScriptRoot, [StringComparison]::OrdinalIgnoreCase)) {
            taskkill.exe /PID $servicePid /T /F
        }
    }
}
