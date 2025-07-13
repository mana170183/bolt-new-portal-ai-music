# Container Registry Module for Portal AI Music

# Azure Container Registry
resource "azurerm_container_registry" "main" {
  name                = var.naming_convention.acr
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = var.sku
  admin_enabled       = var.admin_enabled
  
  # Premium tier features
  public_network_access_enabled = true
  quarantine_policy_enabled     = var.sku == "Premium" ? true : false
  retention_policy {
    days    = 30
    enabled = var.sku == "Premium" ? true : false
  }
  
  trust_policy {
    enabled = var.sku == "Premium" ? true : false
  }
  
  # Enable vulnerability scanning
  dynamic "georeplications" {
    for_each = var.sku == "Premium" && var.enable_geo_replication ? var.geo_replication_locations : []
    content {
      location = georeplications.value
      tags     = var.common_tags
    }
  }
  
  tags = var.common_tags
}

# Vulnerability scanning webhook (Premium tier only)
resource "azurerm_container_registry_webhook" "vulnerability_scan" {
  count = var.sku == "Premium" ? 1 : 0
  
  name                = "${var.naming_convention.acr}-webhook"
  resource_group_name = var.resource_group_name
  registry_name       = azurerm_container_registry.main.name
  location            = var.location
  
  service_uri    = var.webhook_service_uri
  status         = "enabled"
  scope          = "*"
  actions        = ["push", "delete"]
  custom_headers = {
    "Content-Type" = "application/json"
  }
  
  tags = var.common_tags
}

# Role assignment for Container App managed identity to pull images
data "azurerm_user_assigned_identity" "container_app" {
  count = var.container_app_identity_id != null ? 1 : 0
  
  name                = split("/", var.container_app_identity_id)[8]
  resource_group_name = var.resource_group_name
}

resource "azurerm_role_assignment" "acr_pull" {
  count = var.container_app_identity_id != null ? 1 : 0
  
  scope                = azurerm_container_registry.main.id
  role_definition_name = "AcrPull"
  principal_id         = data.azurerm_user_assigned_identity.container_app[0].principal_id
}

# Image retention policy for cost optimization
resource "azurerm_container_registry_task" "cleanup" {
  count = var.sku == "Premium" ? 1 : 0
  
  name                  = "${var.naming_convention.acr}-cleanup-task"
  container_registry_id = azurerm_container_registry.main.id
  
  platform {
    os           = "Linux"
    architecture = "amd64"
  }
  
  docker_step {
    dockerfile_path      = "Dockerfile"
    context_path         = "https://github.com/Azure-Samples/acr-tasks.git"
    context_access_token = var.github_token
    image_names          = ["cleanup:latest"]
  }
  
  timer_trigger {
    name     = "cleanup-schedule"
    schedule = "0 2 * * *" # Run daily at 2 AM
  }
  
  tags = var.common_tags
}

# Diagnostic settings for monitoring
resource "azurerm_monitor_diagnostic_setting" "acr" {
  name                       = "${var.naming_convention.acr}-diagnostics"
  target_resource_id         = azurerm_container_registry.main.id
  log_analytics_workspace_id = var.log_analytics_workspace_id
  
  log {
    category = "ContainerRegistryRepositoryEvents"
    enabled  = true
    
    retention_policy {
      enabled = true
      days    = 30
    }
  }
  
  log {
    category = "ContainerRegistryLoginEvents"
    enabled  = true
    
    retention_policy {
      enabled = true
      days    = 30
    }
  }
  
  metric {
    category = "AllMetrics"
    enabled  = true
    
    retention_policy {
      enabled = true
      days    = 30
    }
  }
}

# Private endpoint for enhanced security (Premium tier only)
resource "azurerm_private_endpoint" "acr" {
  count = var.sku == "Premium" && var.enable_private_endpoint ? 1 : 0
  
  name                = "${var.naming_convention.acr}-pe"
  location            = var.location
  resource_group_name = var.resource_group_name
  subnet_id           = var.private_endpoint_subnet_id
  
  private_service_connection {
    name                           = "${var.naming_convention.acr}-psc"
    private_connection_resource_id = azurerm_container_registry.main.id
    subresource_names              = ["registry"]
    is_manual_connection           = false
  }
  
  tags = var.common_tags
}
