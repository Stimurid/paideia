# Полный деплой Paideia на VM 81.26.176.248 одной командой.
# Запуск в PowerShell из корня репо:
#     cd C:\projects\paideia-app
#     deploy\bootstrap.ps1
#
# Параметры через env-переменные (опц.):
#     $env:PAIDEIA_PASSWORD = "мой_пароль_для_basic_auth"
#     $env:PAIDEIA_VM       = "deploy@81.26.176.248"
#     $env:PAIDEIA_DOMAIN   = "paideia.mindkampf.ru"

$ErrorActionPreference = "Stop"
$ProjectRoot = (Get-Item $PSScriptRoot).Parent.FullName

$VM       = if ($env:PAIDEIA_VM)       { $env:PAIDEIA_VM }       else { "deploy@81.26.176.248" }
$Domain   = if ($env:PAIDEIA_DOMAIN)   { $env:PAIDEIA_DOMAIN }   else { "paideia.mindkampf.ru" }
$Instance = "paideia"
$Port     = 8082

Write-Host "==> Paideia deploy" -ForegroundColor Cyan
Write-Host "    VM:     $VM"
Write-Host "    Domain: $Domain"
Write-Host "    Source: $ProjectRoot"
Write-Host ""

# 1. Достаём LLM_PRIMARY_API_KEY из локального .env
$envFile = Join-Path $ProjectRoot ".env"
if (-not (Test-Path $envFile)) {
    Write-Host "ERR: $envFile не найден. Положи туда LLM_PRIMARY_API_KEY=sk-..." -ForegroundColor Red
    exit 1
}
$llmKey = (Get-Content $envFile | Where-Object { $_ -match '^LLM_PRIMARY_API_KEY=' } | Select-Object -First 1) -replace '^LLM_PRIMARY_API_KEY=', ''
if (-not $llmKey) {
    Write-Host "ERR: LLM_PRIMARY_API_KEY в .env не найден" -ForegroundColor Red
    exit 1
}
Write-Host "  ✓ LLM key найден"

# 2. Пароль для basic_auth
$basicPwd = if ($env:PAIDEIA_PASSWORD) {
    $env:PAIDEIA_PASSWORD
} else {
    $secure = Read-Host "Пароль для basic_auth (Enter = без auth)" -AsSecureString
    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
    $plain = [Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
    $plain
}
if ($basicPwd) {
    Write-Host "  ✓ basic_auth активирован"
} else {
    Write-Host "  · basic_auth выключен — поддомен будет публичным"
}

# 3. Собираем свежий tarball
Write-Host ""
Write-Host "==> Сборка архива" -ForegroundColor Cyan
$tarball = Join-Path $env:TEMP "paideia-deploy.tar.gz"
Push-Location $ProjectRoot
try {
    & tar -czf $tarball `
        --exclude=.venv --exclude=.git --exclude=__pycache__ `
        --exclude='db/*.db' --exclude='db/*.db-shm' --exclude='db/*.db-wal' `
        --exclude='db/_extract_cache_*.json' `
        --exclude='.pytest_cache' --exclude='*.log' `
        --exclude='.env' `
        .
    if ($LASTEXITCODE -ne 0) { throw "tar упал" }
} finally {
    Pop-Location
}
$size = (Get-Item $tarball).Length / 1KB
Write-Host ("  ✓ {0:N0} KB → {1}" -f $size, $tarball)

# 4. Заливаем на VM
Write-Host ""
Write-Host "==> scp на VM" -ForegroundColor Cyan
& scp -q $tarball "${VM}:/tmp/paideia-deploy.tar.gz"
if ($LASTEXITCODE -ne 0) { throw "scp упал — проверь ssh-доступ к $VM" }
& scp -q (Join-Path $PSScriptRoot "install_on_vm.sh") "${VM}:/tmp/install_on_vm.sh"
if ($LASTEXITCODE -ne 0) { throw "scp install_on_vm.sh упал" }
Write-Host "  ✓ архив + скрипт залиты"

# 5. Запускаем установку на VM
Write-Host ""
Write-Host "==> Установка на VM" -ForegroundColor Cyan
$remoteCmd = @"
chmod +x /tmp/install_on_vm.sh && \
sudo \
    LLM_PRIMARY_API_KEY='$llmKey' \
    BASIC_AUTH_PASSWORD='$basicPwd' \
    INSTANCE='$Instance' \
    PORT='$Port' \
    DOMAIN='$Domain' \
    bash /tmp/install_on_vm.sh
"@
& ssh $VM $remoteCmd
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERR: install_on_vm.sh упал — смотри вывод выше" -ForegroundColor Red
    exit 1
}

# 6. Проверка снаружи
Write-Host ""
Write-Host "==> Проверка снаружи" -ForegroundColor Cyan
Start-Sleep 5
try {
    $code = (Invoke-WebRequest "https://$Domain/healthz" -SkipHttpErrorCheck -TimeoutSec 30).StatusCode
    if ($basicPwd) {
        if ($code -eq 401) {
            Write-Host "  ✓ без auth → 401 (ожидаемо)"
        } else {
            Write-Host "  ! без auth → $code (ожидался 401)" -ForegroundColor Yellow
        }
        $cred = New-Object PSCredential("timur", (ConvertTo-SecureString $basicPwd -AsPlainText -Force))
        $authCode = (Invoke-WebRequest "https://$Domain/healthz" -Credential $cred -AllowUnencryptedAuthentication -SkipHttpErrorCheck -TimeoutSec 30).StatusCode
        if ($authCode -eq 200) {
            Write-Host "  ✓ с auth → 200" -ForegroundColor Green
        } else {
            Write-Host "  ! с auth → $authCode" -ForegroundColor Yellow
        }
    } else {
        if ($code -eq 200) {
            Write-Host "  ✓ /healthz → 200" -ForegroundColor Green
        } else {
            Write-Host "  ! /healthz → $code" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "  ! проверка не прошла: $_" -ForegroundColor Yellow
    Write-Host "    (может быть TLS-сертификат ещё выдаётся, повтори через минуту)"
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "✓ Деплой завершён" -ForegroundColor Green
Write-Host "  https://$Domain/" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
