# Setup local Windows — Docker Compose
# Uso: .\scripts\setup-local.ps1

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

Write-Host "Social AI Manager — Setup local" -ForegroundColor Cyan

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Creado .env desde .env.example"
}

function New-RandomHex { -join ((1..64) | ForEach-Object { "{0:x}" -f (Get-Random -Maximum 16) }) }
function New-FernetKey {
    $b = New-Object byte[] 32
    [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($b)
    [Convert]::ToBase64String($b)
}

$envContent = Get-Content ".env" -Raw
if ($envContent -match "change-me") {
    $secret = New-RandomHex
    $jwt = New-RandomHex
    $fernet = New-FernetKey
    $envContent = $envContent -replace "SECRET_KEY=.*", "SECRET_KEY=$secret"
    $envContent = $envContent -replace "JWT_SECRET=.*", "JWT_SECRET=$jwt"
    $envContent = $envContent -replace "ENCRYPTION_KEY=.*", "ENCRYPTION_KEY=$fernet"
    $envContent | Out-File ".env" -Encoding utf8NoBOM -NoNewline
    Write-Host "Secretos generados en .env" -ForegroundColor Green
}

Write-Host "Levantando Docker Compose..."
docker compose up -d --build

Write-Host ""
Write-Host "Frontend:  http://localhost:3000"
Write-Host "Backend:   http://localhost:8000"
Write-Host "Swagger:   http://localhost:8000/docs"
Write-Host ""
Write-Host "Seed demo: `$env:RUN_SEED='true'; docker compose up -d backend"
Write-Host "Login: admin@example.com / Admin123!"
