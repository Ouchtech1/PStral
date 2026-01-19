# Script pour afficher les logs de Ministral SQL Assistant
# Usage: .\logs.ps1 [service]
#   service: backend, frontend, ou vide pour tous les services

param(
    [string]$service = ""
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Ministral SQL Assistant - Logs" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($service -eq "") {
    Write-Host "Affichage des logs de tous les services..." -ForegroundColor Yellow
    Write-Host "Appuyez sur Ctrl+C pour quitter" -ForegroundColor Gray
    Write-Host ""
    docker-compose logs -f
} else {
    Write-Host "Affichage des logs du service: $service" -ForegroundColor Yellow
    Write-Host "Appuyez sur Ctrl+C pour quitter" -ForegroundColor Gray
    Write-Host ""
    docker-compose logs -f $service
}

