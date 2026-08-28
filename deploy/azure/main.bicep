// ==============================================================================
// MINEGUARD (SIH 2026 - Team RED HACK)
// Microsoft Azure Bicep Infrastructure Deployment Template
// Target Tier: Azure for Students (Low-Cost / Student Credit Optimized)
// ==============================================================================

@description('Azure Region for resource deployment')
param location string = 'centralindia'

@description('Application name prefix')
param appName string = 'mineguard-sih'

@description('Administrator login for Azure PostgreSQL')
param dbAdminUser string = 'mineguardadmin'

@description('Administrator password for Azure PostgreSQL')
@secure()
param dbAdminPassword string

// 1. Log Analytics Workspace & Application Insights (Free 5GB/Month Ingestion)
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: '${appName}-logs'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${appName}-appinsights'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
  }
}

// 2. Azure Database for PostgreSQL Flexible Server (Burstable B1ms - Student Tier)
resource postgresServer 'Microsoft.DBforPostgreSQL/flexibleServers@2023-03-01-preview' = {
  name: '${appName}-pg'
  location: location
  sku: {
    name: 'Standard_B1ms'
    tier: 'Burstable'
  }
  properties: {
    version: '16'
    administratorLogin: dbAdminUser
    administratorLoginPassword: dbAdminPassword
    storage: {
      storageSizeGB: 32
      autoGrow: 'Disabled'
    }
    backup: {
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
    highAvailability: {
      mode: 'Disabled'
    }
  }
}

// Enable PostGIS extensions on Azure PostgreSQL
resource pgExtension 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2023-03-01-preview' = {
  parent: postgresServer
  name: 'azure.extensions'
  properties: {
    value: 'POSTGIS'
    source: 'user-override'
  }
}

// Firewall Rule: Allow Azure services to connect
resource allowAzureIps 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2023-03-01-preview' = {
  parent: postgresServer
  name: 'AllowAllAzureServicesAndResourcesWithinAzureIps'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

// 3. App Service Plan (Linux Basic B1 or Free F1)
resource appServicePlan 'Microsoft.Web/serverfarms@2022-09-01' = {
  name: '${appName}-asp'
  location: location
  kind: 'linux'
  sku: {
    name: 'B1'
    tier: 'Basic'
  }
  properties: {
    reserved: true
  }
}

// 4. FastAPI Backend App Service
resource apiApp 'Microsoft.Web/sites@2022-09-01' = {
  name: '${appName}-api'
  location: location
  kind: 'app,linux'
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      appCommandLine: 'gunicorn -k uvicorn.workers.UvicornWorker -w 2 -b 0.0.0.0:8000 main:app --chdir backend'
      appSettings: [
        {
          name: 'ENVIRONMENT'
          value: 'production'
        }
        {
          name: 'DATABASE_URL'
          value: 'postgresql+asyncpg://${dbAdminUser}:${dbAdminPassword}@${postgresServer.properties.fullyQualifiedDomainName}:5432/mine_monitoring'
        }
        {
          name: 'AZURE_POSTGRES_SSL'
          value: 'true'
        }
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: appInsights.properties.ConnectionString
        }
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'true'
        }
      ]
    }
  }
}

output backendApiUrl string = 'https://${apiApp.properties.defaultHostName}'
output postgresFqdn string = postgresServer.properties.fullyQualifiedDomainName
