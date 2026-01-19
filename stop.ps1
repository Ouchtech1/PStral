# Script d'arrêt pour Ministral SQL Assistant
# Usage: .\stop.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Ministral SQL Assistant - Arrêt" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Arrêt des conteneurs Docker..." -ForegroundColor Yellow
docker-compose down

Write-Host ""
Write-Host "✓ Conteneurs arrêtés" -ForegroundColor Green

