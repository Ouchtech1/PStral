# Script de démarrage pour Ministral SQL Assistant
# Usage: .\start.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Ministral SQL Assistant - Démarrage" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier si Docker est en cours d'exécution
Write-Host "[1/4] Vérification de Docker Desktop..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Docker n'est pas accessible"
    }
    Write-Host "  ✓ Docker détecté: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Erreur: Docker Desktop n'est pas démarré ou installé" -ForegroundColor Red
    Write-Host "  Veuillez démarrer Docker Desktop et réessayer." -ForegroundColor Red
    exit 1
}

# Vérifier si le fichier .env existe
Write-Host "[2/4] Vérification du fichier .env..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host "  ⚠ Fichier .env non trouvé" -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Write-Host "  → Copie de .env.example vers .env..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
        Write-Host "  ✓ Fichier .env créé. Veuillez le modifier si nécessaire." -ForegroundColor Green
    } else {
        Write-Host "  ✗ Erreur: .env.example non trouvé" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  ✓ Fichier .env trouvé" -ForegroundColor Green
}

# Vérifier si Ollama est accessible
Write-Host "[3/4] Vérification d'Ollama..." -ForegroundColor Yellow
try {
    $ollamaCheck = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
    $models = ($ollamaCheck.Content | ConvertFrom-Json).models
    $modelNames = $models | ForEach-Object { $_.name }
    
    if ($modelNames -contains "ministral-3:3b") {
        Write-Host "  ✓ Ollama accessible - Modèle ministral-3:3b trouvé" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Ollama accessible mais modèle ministral-3:3b non trouvé" -ForegroundColor Yellow
        Write-Host "  → Exécutez: ollama pull ministral-3:3b" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ⚠ Ollama non accessible sur localhost:11434" -ForegroundColor Yellow
    Write-Host "  → Assurez-vous qu'Ollama est démarré (ollama serve)" -ForegroundColor Yellow
}

# Vérifier les ports
Write-Host "[4/4] Vérification des ports..." -ForegroundColor Yellow
$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
$port5173 = Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue

if ($port8000) {
    Write-Host "  ⚠ Port 8000 déjà utilisé" -ForegroundColor Yellow
} else {
    Write-Host "  ✓ Port 8000 disponible" -ForegroundColor Green
}

if ($port5173) {
    Write-Host "  ⚠ Port 5173 déjà utilisé" -ForegroundColor Yellow
} else {
    Write-Host "  ✓ Port 5173 disponible" -ForegroundColor Green
}

Write-Host ""
Write-Host "Démarrage des conteneurs Docker..." -ForegroundColor Cyan
Write-Host ""

# Lancer docker-compose
docker-compose up --build

