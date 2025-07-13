# Azure Cache for Redis Module for AI Music Portal
# Premium tier with persistence, clustering, and security

resource "azurerm_redis_cache" "main" {
  name                = var.redis_name
  location            = var.location
  resource_group_name = var.resource_group_name
  capacity            = var.capacity
  family              = var.family
  sku_name            = var.sku_name
  enable_non_ssl_port = false
  minimum_tls_version = "1.2"
  
  # Redis configuration
  redis_configuration {
    enable_authentication           = true
    maxmemory_reserved             = var.maxmemory_reserved
    maxmemory_delta                = var.maxmemory_delta
    maxmemory_policy               = "allkeys-lru"
    notify_keyspace_events         = "Ex"
    rdb_backup_enabled             = var.backup_enabled
    rdb_backup_frequency           = var.backup_frequency
    rdb_backup_max_snapshot_count  = var.backup_max_snapshots
    rdb_storage_connection_string  = var.backup_storage_connection_string
    aof_backup_enabled             = var.aof_backup_enabled
    aof_storage_connection_string_0 = var.aof_storage_connection_string
  }

  # Patch schedule for maintenance
  patch_schedule {
    day_of_week    = "Sunday"
    start_hour_utc = 2
  }

  # Network security
  public_network_access_enabled = var.public_access_enabled
  
  tags = var.tags
}

# Firewall rules for Redis
resource "azurerm_redis_firewall_rule" "allowed_ips" {
  for_each = toset(var.allowed_ip_ranges)
  
  name                = "allowed-ip-${replace(each.value, "/[^a-zA-Z0-9]/", "-")}"
  redis_cache_name    = azurerm_redis_cache.main.name
  resource_group_name = var.resource_group_name
  start_ip            = split("-", each.value)[0]
  end_ip              = length(split("-", each.value)) > 1 ? split("-", each.value)[1] : split("-", each.value)[0]
}

# Private endpoint for Redis
resource "azurerm_private_endpoint" "redis" {
  count               = var.enable_private_endpoint ? 1 : 0
  name                = "${var.redis_name}-pe"
  location            = var.location
  resource_group_name = var.resource_group_name
  subnet_id           = var.private_endpoint_subnet_id

  private_service_connection {
    name                           = "${var.redis_name}-psc"
    private_connection_resource_id = azurerm_redis_cache.main.id
    subresource_names              = ["redisCache"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name                 = "default"
    private_dns_zone_ids = var.private_dns_zone_ids
  }

  tags = var.tags
}

# Managed identity for Redis access
resource "azurerm_user_assigned_identity" "redis" {
  name                = "${var.redis_name}-identity"
  location            = var.location
  resource_group_name = var.resource_group_name
  tags                = var.tags
}

# RBAC assignment for Redis access
resource "azurerm_role_assignment" "redis_contributor" {
  scope                = azurerm_redis_cache.main.id
  role_definition_name = "Redis Cache Contributor"
  principal_id         = azurerm_user_assigned_identity.redis.principal_id
}

# Diagnostic settings
resource "azurerm_monitor_diagnostic_setting" "redis" {
  name               = "${var.redis_name}-diagnostics"
  target_resource_id = azurerm_redis_cache.main.id
  log_analytics_workspace_id = var.log_analytics_workspace_id

  enabled_log {
    category = "ConnectedClientList"
  }

  metric {
    category = "AllMetrics"
    enabled  = true
  }
}

# Key Vault secret for Redis connection string
resource "azurerm_key_vault_secret" "redis_connection_string" {
  name         = "redis-connection-string"
  value        = azurerm_redis_cache.main.primary_connection_string
  key_vault_id = var.key_vault_id

  tags = var.tags
}

# Key Vault secret for Redis access key
resource "azurerm_key_vault_secret" "redis_access_key" {
  name         = "redis-access-key"
  value        = azurerm_redis_cache.main.primary_access_key
  key_vault_id = var.key_vault_id

  tags = var.tags
}
