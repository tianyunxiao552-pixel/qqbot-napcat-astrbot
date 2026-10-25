$ErrorActionPreference = 'Stop'
$botRoot = $PSScriptRoot
New-Item -ItemType Directory -Force -Path (Join-Path $botRoot 'logs') | Out-Null
$serviceConfigPath = Join-Path $botRoot 'runtime\gpt-sovits-service.json'
if (-not (Test-Path -LiteralPath $serviceConfigPath)) { return }
$voiceConfig = Get-Content -LiteralPath $serviceConfigPath -Raw -Encoding UTF8 | ConvertFrom-Json
if (-not $voiceConfig.enabled) { return }
$connection = [System.Net.Sockets.TcpClient]::new()
try { $connection.Connect('127.0.0.1', [int]$voiceConfig.port); return }
catch { }
finally { $connection.Dispose() }
if (-not (Test-Path -LiteralPath $voiceConfig.python)) { throw 'GPT-SoVITS Python runtime is missing.' }
if (-not (Test-Path -LiteralPath (Join-Path $voiceConfig.program_dir 'api_v2.py'))) { throw 'GPT-SoVITS API program is missing.' }
$env:PYTHONUTF8 = '1'
$env:PYTHONUNBUFFERED = '1'
$env:PATH = (Split-Path -Parent $voiceConfig.python) + ';' + $voiceConfig.program_dir + ';' + $env:PATH
$env:HF_HOME = Join-Path $botRoot 'runtime\hf-cache'
$env:TORCH_HOME = Join-Path $botRoot 'runtime\torch-cache'
$voiceTemp = Join-Path $botRoot 'runtime\voice-temp'
New-Item -ItemType Directory -Force -Path $voiceTemp | Out-Null
$env:TEMP = $voiceTemp
$env:TMP = $voiceTemp
$apiArguments = @('-X','utf8','-u','api_v2.py','-a','127.0.0.1','-p',[string]$voiceConfig.port,'-c',('"' + $voiceConfig.infer_config + '"'))
$process = Start-Process -FilePath $voiceConfig.python -ArgumentList $apiArguments -WorkingDirectory $voiceConfig.program_dir -WindowStyle Hidden -RedirectStandardOutput (Join-Path $botRoot 'logs\gpt_sovits.stdout.log') -RedirectStandardError (Join-Path $botRoot 'logs\gpt_sovits.stderr.log') -PassThru
$process.Id | Set-Content -LiteralPath (Join-Path $botRoot 'logs\gpt_sovits.pid')
Write-Host ('GPT-SoVITS starting: http://127.0.0.1:' + $voiceConfig.port)
