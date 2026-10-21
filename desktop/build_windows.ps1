# بناء نسخة سطح المكتب محلياً على Windows (يتطلب Python 3.12 و Inno Setup 6 للمثبّت)
# الاستخدام من جذر المستودع:  powershell -ExecutionPolicy Bypass -File desktop\build_windows.ps1
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

python -m venv .venv-build
.\.venv-build\Scripts\python -m pip install --upgrade pip
.\.venv-build\Scripts\pip install -r requirements-desktop.txt
.\.venv-build\Scripts\python desktop\make_version_info.py
.\.venv-build\Scripts\pyinstaller desktop\hakam.spec --noconfirm --clean --distpath dist --workpath build

$version = (Select-String -Path version.py -Pattern '__version__ = "(.+)"').Matches[0].Groups[1].Value
$p = Start-Process dist\Hakam\Hakam.exe -ArgumentList "--smoke-test" -Wait -PassThru
if ($p.ExitCode -ne 0) { throw "Smoke test failed ($($p.ExitCode)) — see $env:APPDATA\Hakam\hakam.log" }

$iscc = @("${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe", "$env:ProgramFiles\Inno Setup 6\ISCC.exe", "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe") | Where-Object { Test-Path $_ } | Select-Object -First 1
if ($iscc) { & $iscc "/DAppVersion=$version" desktop\installer.iss } else { Write-Warning "Inno Setup غير مثبت؛ تخطّي إنشاء المثبّت (winget install JRSoftware.InnoSetup)" }

Get-ChildItem dist -File | Format-Table Name, @{n="MB";e={[math]::Round($_.Length/1MB,1)}}
