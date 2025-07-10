# Container App Module for Portal AI Music

# Log Analytics Workspace for Container App Environment
resource "azurerm_log_analytics_workspace" "container_app" {
  name                = "${var.naming_convention.app_insights}-logs"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = var.common_tags
}

# Container App Environment
resource "azurerm_container_app_environment" "main" {
  name                       = "${var.naming_convention.container_app}-env"
  location                  = var.location
  resource_group_name       = var.resource_group_name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.container_app.id
  tags                      = var.common_tags
}

# User Assigned Managed Identity for Container App
resource "azurerm_user_assigned_identity" "container_app" {
  name                = "${var.naming_convention.container_app}-identity"
  location            = var.location
  resource_group_name = var.resource_group_name
  tags                = var.common_tags
}

# Container App
resource "azurerm_container_app" "main" {
  name                         = var.naming_convention.container_app
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name         = var.resource_group_name
  revision_mode               = "Single"
  tags                        = var.common_tags

  # Managed Identity Configuration
  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.container_app.id]
  }

  # Template Configuration
  template {
    # Scaling Configuration
    min_replicas = var.min_replicas
    max_replicas = var.max_replicas

    # Container Configuration
    container {
      name   = "portal-ai-music"
      image  = "mcr.microsoft.com/azuredocs/containerapps-helloworld:latest" # Placeholder image
      cpu    = var.cpu_requests
      memory = var.memory_requests

      # Resource Limits
      liveness_probe {
        http_get {
          path = "/api/health"
          port = 3000
        }
        initial_delay_seconds = 30
        period_seconds        = 30
        timeout_seconds       = 10
        failure_threshold     = 3
      }

      readiness_probe {
        http_get {
          path = "/api/health"
          port = 3000
        }
        initial_delay_seconds = 10
        period_seconds        = 10
        timeout_seconds       = 5
        failure_threshold     = 3
      }

      # Environment Variables (will be updated via CI/CD)
      env {
        name  = "NODE_ENV"
        value = "production"
      }

      env {
        name  = "PORT"
        value = "3000"
      }

      env {
        name        = "DATABASE_URL"
        secret_name = "database-url"
      }

      env {
        name        = "REDIS_CONNECTION_STRING"
        secret_name = "redis-connection-string"
      }

      env {
        name        = "AZURE_STORAGE_CONNECTION_STRING"
        secret_name = "storage-connection-string"
      }

      env {
        name        = "APPLICATIONINSIGHTS_CONNECTION_STRING"
        secret_name = "appinsights-connection-string"
      }

      env {
        name        = "OPENAI_API_KEY"
        secret_name = "openai-api-key"
      }
    }

    # Auto-scaling Rules
    http_scale_rule {
      name                = "http-requests"
      concurrent_requests = 30 # Scale up when more than 30 concurrent requests
    }

    cpu_scale_rule {
      name         = "cpu-usage"
      cpu_usage    = 70 # Scale up when CPU usage exceeds 70%
    }
  }

  # Ingress Configuration
  ingress {
    allow_insecure_connections = false
    external_enabled          = true
    target_port               = 3000

    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  # Secrets (will be populated by Key Vault or CI/CD)
  secret {
    name  = "database-url"
    value = "placeholder" # Will be updated by deployment pipeline
  }

  secret {
    name  = "redis-connection-string"
    value = "placeholder"
  }

  secret {
    name  = "storage-connection-string"
    value = "placeholder"
  }

  secret {
    name  = "appinsights-connection-string"
    value = "placeholder"
  }

  secret {
    name  = "openai-api-key"
    value = "placeholder"
  }

  lifecycle {
    ignore_changes = [
      template[0].container[0].image, # Image will be updated by CI/CD
      secret, # Secrets will be managed by deployment pipeline
    ]
  }
}

# Custom Domain (optional)
resource "azurerm_container_app_custom_domain" "main" {
  count = var.custom_domain != null ? 1 : 0

  name             = var.custom_domain
  container_app_id = azurerm_container_app.main.id
  certificate_binding_type = "SniEnabled"
}

# Diagnostic Settings for Container App
resource "azurerm_monitor_diagnostic_setting" "container_app" {
  name                       = "${var.naming_convention.container_app}-diagnostics"
  target_resource_id         = azurerm_container_app.main.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.container_app.id

  log {
    category = "ContainerAppConsoleLogs"
    enabled  = true

    retention_policy {
      enabled = true
      days    = 30
    }
  }

  log {
    category = "ContainerAppSystemLogs"
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
