<#
==============================================================================
MINEGUARD (SIH 2026 - Team RED HACK)
Microsoft Azure Automated Deployment Script
Deploys FastAPI Backend + Azure Database for PostgreSQL (Flexible Server)
under Azure for Students Low-Cost Tier ($0 - $25/mo budget)
==============================================================================
#>

param (
    [string]$ResourceGroupName = "mineguard-sih-rg",
    [string]$Location = "centralindia",
    [string]$AppName = "mineguard-sih",
    [string]$DbAdminUser = "mineguardadmin",
    [string]$DbAdminPassword = "MineSafety2026!Azure"
)

Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host "       MINEGUARD SIH 2026 — AZURE CLOUD DEPLOYMENT WIZARD" -ForegroundColor Cyan
Write-Host "===================================================================" -ForegroundColor Cyan

# 1. Check Azure CLI
if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Azure CLI ('az') is not installed on PATH." -ForegroundColor Red
    Write-Host "Please install Azure CLI from: https://aka.ms/installazurecliwindows" -ForegroundColor Yellow
    Write-Host "After installation, run 'az login' and rerun this script." -ForegroundColor Yellow
    Exit 1
}

# 2. Check Azure Account Login
Write-Host "`n[1/4] Checking Azure login status..." -ForegroundColor Yellow
$account = az account show --output json | ConvertFrom-Json
if (-not $account) {
    Write-Host "Please log in to your Azure subscription..." -ForegroundColor Yellow
    az login
} else {
    Write-Host "Connected to Azure Subscription: $($account.name) ($($account.id))" -ForegroundColor Green
}

# 3. Create Resource Group
Write-Host "`n[2/4] Creating Resource Group: $ResourceGroupName in $Location..." -ForegroundColor Yellow
az group create --name $ResourceGroupName --location $Location --output table

# 4. Deploy Bicep Infrastructure
Write-Host "`n[3/4] Provisioning Azure PostgreSQL (B1ms Burstable) & App Service (B1 Linux)..." -ForegroundColor Yellow
$deployResult = az deployment group create `
    --resource-group $ResourceGroupName `
    --template-file "./deploy/azure/main.bicep" `
    --parameters appName=$AppName dbAdminUser=$DbAdminUser dbAdminPassword=$DbAdminPassword location=$Location `
    --output json | ConvertFrom-Json

$backendUrl = $deployResult.properties.outputs.backendApiUrl.value
$dbHost = $deployResult.properties.outputs.postgresFqdn.value

Write-Host "`n[4/4] Azure Cloud Provisioning Complete!" -ForegroundColor Green
Write-Host "-------------------------------------------------------------------" -ForegroundColor Cyan
Write-Host "Backend API URL:       $backendUrl" -ForegroundColor White
Write-Host "PostgreSQL Host:       $dbHost" -ForegroundColor White
Write-Host "Swagger Documentation: $backendUrl/docs" -ForegroundColor White
Write-Host "-------------------------------------------------------------------" -ForegroundColor Cyan
Write-Host "`nNext Step: Set your Flutter API Base URL in 'flutter_app/lib/core/constants/api_constants.dart' to: $backendUrl/api" -ForegroundColor Yellow
