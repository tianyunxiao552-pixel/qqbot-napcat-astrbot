param([string]$BotQQ = $env:QQBOT_ACCOUNT)
$ErrorActionPreference = 'Stop'
$botRoot = $PSScriptRoot
$workDir = Join-Path $botRoot 'logs'
New-Item -ItemType Directory -Force -Path $workDir | Out-Null
$env:PYTHONUTF8 = '1'
$env:PYTHONUNBUFFERED = '1'

function Test-LocalPort([int]$Port) {
    $client = [System.Net.Sockets.TcpClient]::new()
    try { $client.Connect('127.0.0.1', $Port); return $true }
    catch { return $false }
    finally { $client.Dispose() }
}

if (Test-Path -LiteralPath (Join-Path $botRoot 'Start-Voice.ps1')) {
    & (Join-Path $botRoot 'Start-Voice.ps1')
}

if (-not (Test-LocalPort 6185)) {
    $appDir = Join-Path $botRoot 'AstrBot'
    $webDir = Join-Path $botRoot 'runtime\dashboard\dist'
    $astrArgs = @('-X','utf8','-u','main.py')
    if (Test-Path -LiteralPath $webDir) { $astrArgs += @('--webui-dir', ('"' + $webDir + '"')) }
    $p = Start-Process -FilePath (Join-Path $appDir '.venv\Scripts\python.exe') -ArgumentList $astrArgs -WorkingDirectory $appDir -WindowStyle Hidden -RedirectStandardOutput (Join-Path $workDir 'astrbot.stdout.log') -RedirectStandardError (Join-Path $workDir 'astrbot.stderr.log') -PassThru
    $p.Id | Set-Content -LiteralPath (Join-Path $workDir 'astrbot.pid')
    Write-Host 'AstrBot starting: http://127.0.0.1:6185'
}
if (-not (Test-LocalPort 6099)) {
    $napDir = Join-Path $botRoot 'NapCat'
    $napArgs = @('index.js')
    if ($BotQQ) { $napArgs += @('-q', $BotQQ) }
    $p = Start-Process -FilePath (Join-Path $napDir 'node.exe') -ArgumentList $napArgs -WorkingDirectory $napDir -WindowStyle Hidden -RedirectStandardOutput (Join-Path $workDir 'napcat.stdout.log') -RedirectStandardError (Join-Path $workDir 'napcat.stderr.log') -PassThru
    $p.Id | Set-Content -LiteralPath (Join-Path $workDir 'napcat.pid')
    Write-Host 'NapCat starting: http://127.0.0.1:6099/webui'
}
Write-Host 'Local services are ready or starting. Open AstrBot on port 6185 or NapCat on port 6099.'
