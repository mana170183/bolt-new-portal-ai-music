# Key Vault Module for Portal AI Music

# Azure Key Vault
resource "azurerm_key_vault" "main" {
  name                       = var.naming_convention.key_vault
  location                   = var.location
  resource_group_name        = var.resource_group_name
  tenant_id                  = var.tenant_id
  sku_name                   = "premium"
  soft_delete_retention_days = 90
  purge_protection_enabled   = true
  
  # RBAC authentication
  enable_rbac_authorization = true
  
  # Network access rules
  network_acls {
    default_action = "Deny"
    bypass         = "AzureServices"
    
    # Allow access from specific IP ranges
    ip_rules = var.allowed_ip_ranges
    
    # Allow access from Container App subnet if provided
    virtual_network_subnet_ids = var.allowed_subnet_ids
  }
  
  tags = var.common_tags
}

# Role assignments for Key Vault
resource "azurerm_role_assignment" "current_user" {
  scope                = azurerm_key_vault.main.id
  role_definition_name = "Key Vault Administrator"
  principal_id         = var.object_id
}

# Role assignment for Container App managed identity
resource "azurerm_role_assignment" "container_app" {
  count = var.container_app_principal_id != null ? 1 : 0
  
  scope                = azurerm_key_vault.main.id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = var.container_app_principal_id
}

# Key Vault secrets for application configuration
resource "azurerm_key_vault_secret" "database_url" {
  name         = "database-url"
  value        = var.database_connection_string != null ? var.database_connection_string : "placeholder"
  key_vault_id = azurerm_key_vault.main.id
  
  depends_on = [azurerm_role_assignment.current_user]
}

resource "azurerm_key_vault_secret" "redis_connection_string" {
  name         = "redis-connection-string"
  value        = var.redis_connection_string != null ? var.redis_connection_string : "placeholder"
  key_vault_id = azurerm_key_vault.main.id
  
  depends_on = [azurerm_role_assignment.current_user]
}

resource "azurerm_key_vault_secret" "storage_connection_string" {
  name         = "storage-connection-string"
  value        = var.storage_connection_string != null ? var.storage_connection_string : "placeholder"
  key_vault_id = azurerm_key_vault.main.id
  
  depends_on = [azurerm_role_assignment.current_user]
}

resource "azurerm_key_vault_secret" "openai_api_key" {
  name         = "openai-api-key"
  value        = var.openai_api_key != null ? var.openai_api_key : "placeholder"
  key_vault_id = azurerm_key_vault.main.id
  
  depends_on = [azurerm_role_assignment.current_user]
}

resource "azurerm_key_vault_secret" "cognitive_services_key" {
  name         = "cognitive-services-key"
  value        = var.cognitive_services_key != null ? var.cognitive_services_key : "placeholder"
  key_vault_id = azurerm_key_vault.main.id
  
  depends_on = [azurerm_role_assignment.current_user]
}

resource "azurerm_key_vault_secret" "application_insights_connection_string" {
  name         = "application-insights-connection-string"
  value        = var.app_insights_connection_string != null ? var.app_insights_connection_string : "placeholder"
  key_vault_id = azurerm_key_vault.main.id
  
  depends_on = [azurerm_role_assignment.current_user]
}

# Key Vault key for encryption at rest
resource "azurerm_key_vault_key" "main" {
  name         = "${var.naming_convention.key_vault}-key"
  key_vault_id = azurerm_key_vault.main.id
  key_type     = "RSA"
  key_size     = 2048
  
  key_opts = [
    "decrypt",
    "encrypt",
    "sign",
    "unwrapKey",
    "verify",
    "wrapKey",
  ]
  
  depends_on = [azurerm_role_assignment.current_user]
}

# Key rotation policy
resource "azurerm_key_vault_key_rotation_policy" "main" {
  key_vault_key_id = azurerm_key_vault_key.main.id
  
  automatic {
    time_after_creation = "P90D" # Rotate after 90 days
    time_before_expiry  = "P30D" # Rotate 30 days before expiry
  }
  
  notify_before_expiry = "P30D"
}

# Diagnostic settings for Key Vault
resource "azurerm_monitor_diagnostic_setting" "key_vault" {
  name                       = "${var.naming_convention.key_vault}-diagnostics"
  target_resource_id         = azurerm_key_vault.main.id
  log_analytics_workspace_id = var.log_analytics_workspace_id
  
  log {
    category = "AuditEvent"
    enabled  = true
    
    retention_policy {
      enabled = true
      days    = 365 # Keep audit logs for 1 year for compliance
    }
  }
  
  log {
    category = "AzurePolicyEvaluationDetails"
    enabled  = true
    
    retention_policy {
      enabled = true
      days    = 90
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

# Private endpoint for enhanced security
resource "azurerm_private_endpoint" "key_vault" {
  count = var.enable_private_endpoint ? 1 : 0
  
  name                = "${var.naming_convention.key_vault}-pe"
  location            = var.location
  resource_group_name = var.resource_group_name
  subnet_id           = var.private_endpoint_subnet_id
  
  private_service_connection {
    name                           = "${var.naming_convention.key_vault}-psc"
    private_connection_resource_id = azurerm_key_vault.main.id
    subresource_names              = ["vault"]
    is_manual_connection           = false
  }
  
  tags = var.common_tags
}

# Key Vault certificate for SSL/TLS (if custom domain is used)
resource "azurerm_key_vault_certificate" "ssl" {
  count = var.ssl_certificate_data != null ? 1 : 0
  
  name         = "ssl-certificate"
  key_vault_id = azurerm_key_vault.main.id
  
  certificate {
    contents = var.ssl_certificate_data
    password = var.ssl_certificate_password
  }
  
  depends_on = [azurerm_role_assignment.current_user]
}
