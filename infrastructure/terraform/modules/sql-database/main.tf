# SQL Database Module for Portal AI Music

# Generate a random password for SQL admin
resource "random_password" "sql_password" {
  length  = 32
  special = true
}

# Azure SQL Server
resource "azurerm_mssql_server" "main" {
  name                         = var.naming_convention.sql_server
  resource_group_name          = var.resource_group_name
  location                    = var.location
  version                     = "12.0"
  administrator_login         = var.admin_username
  administrator_login_password = random_password.sql_password.result
  
  # Security configuration
  minimum_tls_version = "1.2"
  
  # Azure AD authentication
  azuread_administrator {
    login_username = var.azuread_admin_login
    object_id      = var.azuread_admin_object_id
  }
  
  # Identity for managed identity authentication
  identity {
    type = "SystemAssigned"
  }
  
  tags = var.common_tags
}

# Store SQL password in Key Vault
resource "azurerm_key_vault_secret" "sql_password" {
  name         = "sql-admin-password"
  value        = random_password.sql_password.result
  key_vault_id = var.key_vault_id
}

# Azure SQL Database
resource "azurerm_mssql_database" "main" {
  name         = "${var.naming_convention.sql_server}-db"
  server_id    = azurerm_mssql_server.main.id
  collation    = "SQL_Latin1_General_CP1_CI_AS"
  license_type = "LicenseIncluded"
  max_size_gb  = var.max_size_gb
  sku_name     = var.sku_name
  
  # Backup and recovery
  short_term_retention_policy {
    retention_days = var.backup_retention_days
  }
  
  long_term_retention_policy {
    weekly_retention  = "P4W"   # 4 weeks
    monthly_retention = "P12M"  # 12 months
    yearly_retention  = "P5Y"   # 5 years
    week_of_year      = 1
  }
  
  # Threat detection
  threat_detection_policy {
    state           = "Enabled"
    email_addresses = var.security_alert_email_addresses
  }
  
  tags = var.common_tags
}

# Geo-backup configuration
resource "azurerm_mssql_database_extended_auditing_policy" "main" {
  database_id = azurerm_mssql_database.main.id
  
  storage_endpoint                        = var.audit_storage_endpoint
  storage_account_access_key             = var.audit_storage_account_key
  storage_account_access_key_is_secondary = false
  retention_in_days                      = 90
}

# SQL Server firewall rules
resource "azurerm_mssql_firewall_rule" "azure_services" {
  name             = "AllowAzureServices"
  server_id        = azurerm_mssql_server.main.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

# Firewall rules for allowed IP ranges
resource "azurerm_mssql_firewall_rule" "allowed_ips" {
  count = length(var.allowed_ip_ranges)
  
  name             = "AllowedIP-${count.index}"
  server_id        = azurerm_mssql_server.main.id
  start_ip_address = split("/", var.allowed_ip_ranges[count.index])[0]
  end_ip_address   = split("/", var.allowed_ip_ranges[count.index])[0]
}

# Private endpoint for enhanced security
resource "azurerm_private_endpoint" "sql" {
  count = var.enable_private_endpoint ? 1 : 0
  
  name                = "${var.naming_convention.sql_server}-pe"
  location            = var.location
  resource_group_name = var.resource_group_name
  subnet_id           = var.private_endpoint_subnet_id
  
  private_service_connection {
    name                           = "${var.naming_convention.sql_server}-psc"
    private_connection_resource_id = azurerm_mssql_server.main.id
    subresource_names              = ["sqlServer"]
    is_manual_connection           = false
  }
  
  tags = var.common_tags
}

# Diagnostic settings
resource "azurerm_monitor_diagnostic_setting" "sql_server" {
  name                       = "${var.naming_convention.sql_server}-diagnostics"
  target_resource_id         = azurerm_mssql_server.main.id
  log_analytics_workspace_id = var.log_analytics_workspace_id
  
  log {
    category = "DevOpsOperationsAudit"
    enabled  = true
    
    retention_policy {
      enabled = true
      days    = 90
    }
  }
  
  log {
    category = "SQLSecurityAuditEvents"
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

resource "azurerm_monitor_diagnostic_setting" "sql_database" {
  name                       = "${var.naming_convention.sql_server}-db-diagnostics"
  target_resource_id         = azurerm_mssql_database.main.id
  log_analytics_workspace_id = var.log_analytics_workspace_id
  
  log {
    category = "SQLInsights"
    enabled  = true
    
    retention_policy {
      enabled = true
      days    = 30
    }
  }
  
  log {
    category = "AutomaticTuning"
    enabled  = true
    
    retention_policy {
      enabled = true
      days    = 30
    }
  }
  
  log {
    category = "QueryStoreRuntimeStatistics"
    enabled  = true
    
    retention_policy {
      enabled = true
      days    = 30
    }
  }
  
  log {
    category = "QueryStoreWaitStatistics"
    enabled  = true
    
    retention_policy {
      enabled = true
      days    = 30
    }
  }
  
  log {
    category = "Errors"
    enabled  = true
    
    retention_policy {
      enabled = true
      days    = 90
    }
  }
  
  log {
    category = "DatabaseWaitStatistics"
    enabled  = true
    
    retention_policy {
      enabled = true
      days    = 30
    }
  }
  
  log {
    category = "Timeouts"
    enabled  = true
    
    retention_policy {
      enabled = true
      days    = 30
    }
  }
  
  log {
    category = "Blocks"
    enabled  = true
    
    retention_policy {
      enabled = true
      days    = 30
    }
  }
  
  log {
    category = "Deadlocks"
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

# Elastic pool (optional for cost optimization)
resource "azurerm_mssql_elasticpool" "main" {
  count = var.enable_elastic_pool ? 1 : 0
  
  name                = "${var.naming_convention.sql_server}-pool"
  resource_group_name = var.resource_group_name
  location            = var.location
  server_name         = azurerm_mssql_server.main.name
  license_type        = "LicenseIncluded"
  max_size_gb         = var.elastic_pool_max_size_gb
  
  sku {
    name     = var.elastic_pool_sku_name
    tier     = var.elastic_pool_sku_tier
    capacity = var.elastic_pool_capacity
  }
  
  per_database_settings {
    min_capacity = var.elastic_pool_min_capacity
    max_capacity = var.elastic_pool_max_capacity
  }
  
  tags = var.common_tags
}
