# Script de PowerShell para iniciar la aplicación de IA
Write-Host "🤖 Iniciando Aplicación de IA con Agentes..." -ForegroundColor Cyan
Write-Host ""

# Cambiar al directorio del proyecto
Set-Location "c:\Users\Kevin Arauz\Documents\Proyectos IA"

# Ejecutar la aplicación
& "C:/Users/Kevin Arauz/AppData/Local/Programs/Python/Python313/python.exe" app.py

Write-Host ""
Write-Host "Presiona cualquier tecla para continuar..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
