# Outputs for Portal AI Music Azure Infrastructure

# Resource Group Information
output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.main.name
}

output "resource_group_location" {
  description = "Location of the resource group"
  value       = azurerm_resource_group.main.location
}

# Network Information
output "virtual_network_id" {
  description = "Virtual network ID"
  value       = azurerm_virtual_network.main.id
}

output "container_app_subnet_id" {
  description = "Container app subnet ID"
  value       = azurerm_subnet.container_app.id
}

output "private_endpoints_subnet_id" {
  description = "Private endpoints subnet ID"
  value       = azurerm_subnet.private_endpoints.id
}

# Container App Information
output "container_app_fqdn" {
  description = "Fully qualified domain name of the container app"
  value       = module.container_app.fqdn
}

output "container_app_url" {
  description = "URL of the container app"
  value       = "https://${module.container_app.fqdn}"
}

output "container_app_environment_id" {
  description = "ID of the container app environment"
  value       = azurerm_container_app_environment.main.id
}

output "container_app_identity_principal_id" {
  description = "Container app managed identity principal ID"
  value       = module.container_app.identity_principal_id
}

# Container Registry Information
output "container_registry_name" {
  description = "Name of the container registry"
  value       = module.container_registry.registry_name
}

output "container_registry_login_server" {
  description = "Login server of the container registry"
  value       = module.container_registry.login_server
}

output "container_registry_id" {
  description = "Container registry resource ID"
  value       = module.container_registry.registry_id
}

# Key Vault Information
output "key_vault_name" {
  description = "Name of the Key Vault"
  value       = module.key_vault.key_vault_name
}

output "key_vault_uri" {
  description = "URI of the Key Vault"
  value       = module.key_vault.key_vault_uri
}

output "key_vault_id" {
  description = "ID of the Key Vault"
  value       = module.key_vault.key_vault_id
}

# Storage Information
output "storage_account_name" {
  description = "Storage account name"
  value       = module.storage.storage_account_name
}

output "storage_blob_endpoint" {
  description = "Storage blob endpoint"
  value       = module.storage.primary_blob_endpoint
}

output "storage_containers" {
  description = "Created storage containers"
  value       = module.storage.containers
}

# Redis Cache Information
output "redis_hostname" {
  description = "Redis cache hostname"
  value       = module.redis.redis_hostname
}

output "redis_port" {
  description = "Redis cache port"
  value       = module.redis.redis_port
}

output "redis_ssl_port" {
  description = "Redis cache SSL port"
  value       = module.redis.redis_ssl_port
}

# SQL Database Information
output "sql_server_name" {
  description = "Name of the SQL Server"
  value       = module.sql_database.server_name
}

output "sql_database_name" {
  description = "Name of the SQL Database"
  value       = module.sql_database.database_name
}

output "sql_server_fqdn" {
  description = "SQL Server FQDN"
  value       = module.sql_database.server_fqdn
}

# AI Services Information
output "openai_endpoint" {
  description = "OpenAI service endpoint"
  value       = module.ai_services.openai_endpoint
}

output "cognitive_services_endpoint" {
  description = "Cognitive Services endpoint"
  value       = module.ai_services.cognitive_services_endpoint
}

output "speech_service_endpoint" {
  description = "Speech service endpoint"
  value       = module.ai_services.speech_service_endpoint
}

output "search_service_url" {
  description = "Search service URL"
  value       = module.ai_services.search_service_url
}

output "ml_workspace_name" {
  description = "Machine Learning workspace name"
  value       = module.ai_services.ml_workspace_name
}

output "openai_deployments" {
  description = "OpenAI model deployments"
  value       = module.ai_services.openai_deployments
}

# Azure AD B2C Information
output "b2c_application_id" {
  description = "B2C application (client) ID"
  value       = module.azure_ad_b2c.application_id
}

output "b2c_configuration" {
  description = "B2C configuration for application"
  value       = module.azure_ad_b2c.b2c_configuration
}

output "b2c_groups" {
  description = "B2C security groups"
  value       = module.azure_ad_b2c.groups
}

# Monitoring Information
output "log_analytics_workspace_id" {
  description = "Log Analytics workspace ID"
  value       = module.monitoring.log_analytics_workspace_id
}

output "application_insights_instrumentation_key" {
  description = "Application Insights instrumentation key"
  value       = module.monitoring.application_insights_instrumentation_key
  sensitive   = true
}

output "application_insights_connection_string" {
  description = "Application Insights connection string"
  value       = module.monitoring.application_insights_connection_string
  sensitive   = true
}

output "monitoring_dashboard_url" {
  description = "Monitoring dashboard URL"
  value       = module.monitoring.monitoring_endpoints.dashboard_url
}

# Deployment Information
output "deployment_info" {
  description = "Deployment information and endpoints"
  value = {
    environment     = var.environment
    location       = var.location
    resource_group = azurerm_resource_group.main.name
    app_url        = "https://${module.container_app.fqdn}"
    admin_portal   = module.monitoring.monitoring_endpoints.application_insights_portal_url
    created_at     = timestamp()
  }
}

# Cost Estimation
output "estimated_monthly_costs" {
  description = "Estimated monthly costs for all resources"
  value = {
    container_app      = module.container_app.estimated_monthly_cost_usd
    container_registry = module.container_registry.estimated_monthly_cost_usd
    key_vault         = module.key_vault.estimated_monthly_cost_usd
    sql_database      = module.sql_database.estimated_monthly_cost_usd
    storage           = module.storage.estimated_monthly_cost_usd
    redis            = module.redis.estimated_monthly_cost_usd
    ai_services      = module.ai_services.estimated_monthly_cost_usd
    azure_ad_b2c     = module.azure_ad_b2c.estimated_monthly_cost_usd
    monitoring       = module.monitoring.estimated_monthly_cost_usd
    
    total_estimated = (
      module.container_app.estimated_monthly_cost_usd.total +
      module.container_registry.estimated_monthly_cost_usd.total +
      module.key_vault.estimated_monthly_cost_usd.total +
      module.sql_database.estimated_monthly_cost_usd.total +
      module.storage.estimated_monthly_cost_usd.total +
      module.redis.estimated_monthly_cost_usd.total +
      module.ai_services.estimated_monthly_cost_usd.total +
      module.azure_ad_b2c.estimated_monthly_cost_usd.total +
      module.monitoring.estimated_monthly_cost_usd.total
    )
  }
}

# Compliance and Security Information
output "compliance_features" {
  description = "Enabled compliance and security features"
  value = {
    soc2_compliance = {
      audit_logging = var.enable_audit_logging
      data_encryption = true
      access_controls = true
      monitoring = true
    }
    gdpr_compliance = {
      data_retention_years = var.data_retention_years
      data_export_capabilities = true
      consent_management = module.azure_ad_b2c.compliance_features.gdpr_consent_tracking
      right_to_erasure = true
    }
    security_features = {
      private_endpoints = var.enable_private_endpoints
      advanced_threat_protection = var.enable_advanced_threat_protection
      azure_defender = var.enable_azure_defender
      mfa_enabled = true
      conditional_access = true
    }
  }
}

# Connection Strings and Keys (Sensitive)
output "connection_secrets" {
  description = "Connection strings and keys stored in Key Vault"
  value = {
    key_vault_uri = module.key_vault.key_vault_uri
    secret_names = [
      "sql-connection-string",
      "storage-connection-string",
      "redis-connection-string",
      "application-insights-connection-string",
      "openai-key",
      "cognitive-services-key",
      "speech-key",
      "search-key",
      "b2c-client-id",
      "b2c-client-secret"
    ]
  }
  sensitive = true
}
