# Container App Module Outputs

output "container_app_fqdn" {
  description = "FQDN of the container app"
  value       = azurerm_container_app.main.latest_revision_fqdn
}

output "container_app_environment_id" {
  description = "ID of the container app environment"
  value       = azurerm_container_app_environment.main.id
}

output "container_app_id" {
  description = "ID of the container app"
  value       = azurerm_container_app.main.id
}

output "container_app_name" {
  description = "Name of the container app"
  value       = azurerm_container_app.main.name
}

output "managed_identity_principal_id" {
  description = "Principal ID of the managed identity"
  value       = azurerm_user_assigned_identity.container_app.principal_id
}

output "managed_identity_client_id" {
  description = "Client ID of the managed identity"
  value       = azurerm_user_assigned_identity.container_app.client_id
}

output "managed_identity_id" {
  description = "ID of the managed identity"
  value       = azurerm_user_assigned_identity.container_app.id
}

output "log_analytics_workspace_id" {
  description = "ID of the Log Analytics workspace"
  value       = azurerm_log_analytics_workspace.container_app.id
}
