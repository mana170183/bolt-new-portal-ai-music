output "redis_id" {
  description = "Redis cache resource ID"
  value       = azurerm_redis_cache.main.id
}

output "redis_name" {
  description = "Redis cache name"
  value       = azurerm_redis_cache.main.name
}

output "redis_hostname" {
  description = "Redis cache hostname"
  value       = azurerm_redis_cache.main.hostname
}

output "redis_port" {
  description = "Redis cache port"
  value       = azurerm_redis_cache.main.port
}

output "redis_ssl_port" {
  description = "Redis cache SSL port"
  value       = azurerm_redis_cache.main.ssl_port
}

output "primary_connection_string" {
  description = "Primary connection string"
  value       = azurerm_redis_cache.main.primary_connection_string
  sensitive   = true
}

output "primary_access_key" {
  description = "Primary access key"
  value       = azurerm_redis_cache.main.primary_access_key
  sensitive   = true
}

output "secondary_access_key" {
  description = "Secondary access key"
  value       = azurerm_redis_cache.main.secondary_access_key
  sensitive   = true
}

output "identity_principal_id" {
  description = "Redis managed identity principal ID"
  value       = azurerm_user_assigned_identity.redis.principal_id
}

output "identity_client_id" {
  description = "Redis managed identity client ID"
  value       = azurerm_user_assigned_identity.redis.client_id
}

output "private_endpoint_id" {
  description = "Private endpoint resource ID"
  value       = var.enable_private_endpoint ? azurerm_private_endpoint.redis[0].id : null
}

output "estimated_monthly_cost_usd" {
  description = "Estimated monthly cost in USD"
  value = {
    redis_cache = var.sku_name == "Premium" ? (var.capacity == 1 ? 481.32 : var.capacity * 481.32) : (var.capacity * 73.00)
    private_endpoint = var.enable_private_endpoint ? 7.30 : 0.0
    backup_storage = var.backup_enabled ? 10.0 : 0.0
    total = (var.sku_name == "Premium" ? (var.capacity == 1 ? 481.32 : var.capacity * 481.32) : (var.capacity * 73.00)) + 
            (var.enable_private_endpoint ? 7.30 : 0.0) + 
            (var.backup_enabled ? 10.0 : 0.0)
  }
}
