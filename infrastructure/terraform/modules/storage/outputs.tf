output "storage_account_id" {
  description = "Storage account resource ID"
  value       = azurerm_storage_account.main.id
}

output "storage_account_name" {
  description = "Storage account name"
  value       = azurerm_storage_account.main.name
}

output "primary_blob_endpoint" {
  description = "Primary blob service endpoint"
  value       = azurerm_storage_account.main.primary_blob_endpoint
}

output "primary_connection_string" {
  description = "Primary connection string"
  value       = azurerm_storage_account.main.primary_connection_string
  sensitive   = true
}

output "primary_access_key" {
  description = "Primary access key"
  value       = azurerm_storage_account.main.primary_access_key
  sensitive   = true
}

output "identity_principal_id" {
  description = "Storage managed identity principal ID"
  value       = azurerm_user_assigned_identity.storage.principal_id
}

output "identity_client_id" {
  description = "Storage managed identity client ID"
  value       = azurerm_user_assigned_identity.storage.client_id
}

output "containers" {
  description = "Created storage containers"
  value = {
    audio_files  = azurerm_storage_container.audio_files.name
    user_uploads = azurerm_storage_container.user_uploads.name
    models      = azurerm_storage_container.models.name
    backups     = azurerm_storage_container.backups.name
  }
}

output "private_endpoint_id" {
  description = "Private endpoint resource ID"
  value       = var.enable_private_endpoint ? azurerm_private_endpoint.storage[0].id : null
}

output "estimated_monthly_cost_usd" {
  description = "Estimated monthly cost in USD"
  value = {
    storage_account = 150.0  # Premium ZRS with advanced features
    private_endpoint = var.enable_private_endpoint ? 7.30 : 0.0
    defender = 15.0
    total = var.enable_private_endpoint ? 172.30 : 165.0
  }
}
