# Terraform configuration for Portal AI Music application
# This template creates a complete Azure infrastructure for AI-powered music generation

terraform {
  required_version = ">= 1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }

  backend "azurerm" {
    # Configuration will be provided via backend config file
  }
}

# Configure the Microsoft Azure Provider
provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy = true
    }
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
}

provider "azuread" {
  # Configuration will be provided via environment variables
}

# Data sources
data "azurerm_client_config" "current" {}

# Local values for consistent naming and tagging
locals {
  app_name = "portal-ai-music"
  
  # Naming convention: {service}-{app}-{env}-{region}
  naming_convention = {
    resource_group = "rg-${local.app_name}-${var.environment}"
    container_app  = "ca-${local.app_name}-${var.environment}-${var.location_short}"
    acr           = "acr${replace(local.app_name, "-", "")}${var.environment}${var.location_short}"
    key_vault     = "kv-${local.app_name}-${var.environment}-${var.location_short}"
    sql_server    = "sql-${local.app_name}-${var.environment}-${var.location_short}"
    storage       = "st${replace(local.app_name, "-", "")}${var.environment}${var.location_short}"
    redis         = "redis-${local.app_name}-${var.environment}-${var.location_short}"
    cognitive     = "cog-${local.app_name}-${var.environment}-${var.location_short}"
    openai        = "openai-${local.app_name}-${var.environment}-${var.location_short}"
    speech        = "speech-${local.app_name}-${var.environment}-${var.location_short}"
    ml_workspace  = "mlw-${local.app_name}-${var.environment}-${var.location_short}"
    search        = "srch-${local.app_name}-${var.environment}-${var.location_short}"
    log_analytics = "log-${local.app_name}-${var.environment}-${var.location_short}"
    app_insights  = "appi-${local.app_name}-${var.environment}-${var.location_short}"
    action_group  = "ag-${local.app_name}-${var.environment}-${var.location_short}"
  }

  # Common tags applied to all resources
  common_tags = {
    Project          = "Portal AI Music"
    Environment      = var.environment
    Owner           = var.resource_owner
    CostCenter      = var.cost_center
    ManagedBy       = "Terraform"
    CreatedDate     = timestamp()
    Compliance      = "SOC2-GDPR"
    BackupPolicy    = "Required"
    MonitoringLevel = "Critical"
    DataClassification = "Confidential"
  }
}

# Random string for unique resource names
resource "random_string" "unique_suffix" {
  length  = 6
  special = false
  upper   = false
}

# Primary Resource Group
resource "azurerm_resource_group" "main" {
  name     = local.naming_convention.resource_group
  location = var.location
  tags     = local.common_tags
}

# Virtual Network for private connectivity
resource "azurerm_virtual_network" "main" {
  name                = "vnet-${local.app_name}-${var.environment}"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tags                = local.common_tags
}

# Subnets
resource "azurerm_subnet" "container_app" {
  name                 = "snet-container-app"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.1.0/24"]
  
  delegation {
    name = "Microsoft.App/environments"
    service_delegation {
      name = "Microsoft.App/environments"
    }
  }
}

resource "azurerm_subnet" "private_endpoints" {
  name                 = "snet-private-endpoints"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.2.0/24"]
  
  private_endpoint_network_policies_enabled = false
}

# Monitoring (needs to be created first for other modules)
module "monitoring" {
  source = "./modules/monitoring"
  
  log_analytics_name      = local.naming_convention.log_analytics
  application_insights_name = local.naming_convention.app_insights
  action_group_name       = local.naming_convention.action_group
  action_group_short_name = "aimusic"
  
  resource_group_name = azurerm_resource_group.main.name
  location           = azurerm_resource_group.main.location
  subscription_id    = data.azurerm_client_config.current.subscription_id
  
  key_vault_id = module.key_vault.key_vault_id
  
  email_receivers = var.monitoring_email_receivers
  tags           = local.common_tags
  
  depends_on = [azurerm_resource_group.main, module.key_vault]
}

# Container App Environment
resource "azurerm_container_app_environment" "main" {
  name                       = "cae-${local.app_name}-${var.environment}"
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  log_analytics_workspace_id = module.monitoring.log_analytics_workspace_id
  infrastructure_subnet_id   = azurerm_subnet.container_app.id
  tags                      = local.common_tags
}

# Container App
module "container_app" {
  source = "./modules/container-app"
  
  resource_group_name = azurerm_resource_group.main.name
  location           = azurerm_resource_group.main.location
  app_name           = local.app_name
  environment        = var.environment
  naming_convention  = local.naming_convention
  common_tags        = local.common_tags
  
  container_app_environment_id = azurerm_container_app_environment.main.id
  log_analytics_workspace_id   = module.monitoring.log_analytics_workspace_id
  
  # Container App specific configuration
  min_replicas = var.container_app_min_replicas
  max_replicas = var.container_app_max_replicas
  cpu_requests = var.container_app_cpu_requests
  memory_requests = var.container_app_memory_requests
  cpu_limits = var.container_app_cpu_limits
  memory_limits = var.container_app_memory_limits
  
  depends_on = [azurerm_resource_group.main, azurerm_container_app_environment.main]
}

# Container Registry
module "container_registry" {
  source = "./modules/container-registry"
  
  resource_group_name = azurerm_resource_group.main.name
  location           = azurerm_resource_group.main.location
  naming_convention  = local.naming_convention
  common_tags        = local.common_tags
  
  log_analytics_workspace_id = module.monitoring.log_analytics_workspace_id
  
  # ACR specific configuration
  sku = "Premium"
  admin_enabled = false
  
  depends_on = [azurerm_resource_group.main, module.monitoring]
}

# Key Vault for secrets management
module "key_vault" {
  source = "./modules/key-vault"
  
  resource_group_name = azurerm_resource_group.main.name
  location           = azurerm_resource_group.main.location
  naming_convention  = local.naming_convention
  common_tags        = local.common_tags
  
  tenant_id = data.azurerm_client_config.current.tenant_id
  object_id = data.azurerm_client_config.current.object_id
  
  depends_on = [azurerm_resource_group.main]
}

# Storage Account
module "storage" {
  source = "./modules/storage"
  
  storage_account_name = local.naming_convention.storage
  resource_group_name  = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  
  log_analytics_workspace_id = module.monitoring.log_analytics_workspace_id
  
  # Storage configuration
  replication_type = "ZRS"
  public_access_enabled = false
  enable_private_endpoint = true
  private_endpoint_subnet_id = azurerm_subnet.private_endpoints.id
  
  allowed_subnet_ids = [azurerm_subnet.container_app.id]
  
  tags = local.common_tags
  
  depends_on = [azurerm_resource_group.main, module.monitoring]
}

# Redis Cache
module "redis" {
  source = "./modules/redis"
  
  redis_name          = local.naming_convention.redis
  resource_group_name = azurerm_resource_group.main.name
  location           = azurerm_resource_group.main.location
  
  log_analytics_workspace_id = module.monitoring.log_analytics_workspace_id
  key_vault_id               = module.key_vault.key_vault_id
  
  # Redis configuration
  sku_name = "Premium"
  capacity = 1
  backup_enabled = true
  backup_storage_connection_string = module.storage.primary_connection_string
  
  # Network security
  public_access_enabled = false
  enable_private_endpoint = true
  private_endpoint_subnet_id = azurerm_subnet.private_endpoints.id
  
  tags = local.common_tags
  
  depends_on = [azurerm_resource_group.main, module.monitoring, module.key_vault, module.storage]
}

# Azure SQL Database
module "sql_database" {
  source = "./modules/sql-database"
  
  resource_group_name = azurerm_resource_group.main.name
  location           = azurerm_resource_group.main.location
  naming_convention  = local.naming_convention
  common_tags        = local.common_tags
  
  key_vault_id               = module.key_vault.key_vault_id
  log_analytics_workspace_id = module.monitoring.log_analytics_workspace_id
  
  # SQL configuration
  enable_private_endpoint = true
  private_endpoint_subnet_id = azurerm_subnet.private_endpoints.id
  allowed_subnet_ids = [azurerm_subnet.container_app.id]
  
  depends_on = [azurerm_resource_group.main, module.key_vault, module.monitoring]
}

# AI Services
module "ai_services" {
  source = "./modules/ai-services"
  
  cognitive_services_name = local.naming_convention.cognitive
  openai_name            = local.naming_convention.openai
  speech_service_name    = local.naming_convention.speech
  ml_workspace_name      = local.naming_convention.ml_workspace
  search_service_name    = local.naming_convention.search
  
  resource_group_name = azurerm_resource_group.main.name
  location           = azurerm_resource_group.main.location
  openai_location    = var.openai_location
  
  key_vault_id                   = module.key_vault.key_vault_id
  storage_account_id             = module.storage.storage_account_id
  container_registry_id          = module.container_registry.registry_id
  application_insights_id        = module.monitoring.application_insights_id
  log_analytics_workspace_id     = module.monitoring.log_analytics_workspace_id
  application_principal_id       = module.container_app.identity_principal_id
  
  # Network security
  public_access_enabled = false
  enable_private_endpoint = true
  private_endpoint_subnet_id = azurerm_subnet.private_endpoints.id
  
  tags = local.common_tags
  
  depends_on = [azurerm_resource_group.main, module.key_vault, module.storage, module.container_registry, module.monitoring, module.container_app]
}

# Azure AD B2C
module "azure_ad_b2c" {
  source = "./modules/azure-ad-b2c"
  
  application_name = "${local.app_name}-${var.environment}"
  
  redirect_uris = [
    "https://${module.container_app.fqdn}/auth/callback",
    "https://${var.custom_domain}/auth/callback"
  ]
  
  spa_redirect_uris = [
    "https://${module.container_app.fqdn}",
    "https://${var.custom_domain}"
  ]
  
  key_vault_id = module.key_vault.key_vault_id
  
  trusted_ip_ranges = var.trusted_ip_ranges
  
  tags = local.common_tags
  
  depends_on = [azurerm_resource_group.main, module.key_vault, module.container_app]
}
