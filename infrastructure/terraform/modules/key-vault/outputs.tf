# Key Vault Module Outputs

output "key_vault_name" {
  description = "Name of the Key Vault"
  value       = azurerm_key_vault.main.name
}

output "key_vault_id" {
  description = "ID of the Key Vault"
  value       = azurerm_key_vault.main.id
}

output "key_vault_uri" {
  description = "URI of the Key Vault"
  value       = azurerm_key_vault.main.vault_uri
}

output "key_vault_key_id" {
  description = "ID of the Key Vault key"
  value       = azurerm_key_vault_key.main.id
}

output "key_vault_secrets" {
  description = "Map of Key Vault secret names and IDs"
  value = {
    database_url                          = azurerm_key_vault_secret.database_url.id
    redis_connection_string               = azurerm_key_vault_secret.redis_connection_string.id
    storage_connection_string             = azurerm_key_vault_secret.storage_connection_string.id
    openai_api_key                       = azurerm_key_vault_secret.openai_api_key.id
    cognitive_services_key               = azurerm_key_vault_secret.cognitive_services_key.id
    application_insights_connection_string = azurerm_key_vault_secret.application_insights_connection_string.id
  }
}
