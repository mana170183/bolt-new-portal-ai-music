output "application_id" {
  description = "Application (client) ID"
  value       = azuread_application.b2c_app.application_id
}

output "application_object_id" {
  description = "Application object ID"
  value       = azuread_application.b2c_app.object_id
}

output "client_secret" {
  description = "Application client secret"
  value       = azuread_application_password.b2c_app.value
  sensitive   = true
}

output "service_principal_id" {
  description = "Service principal ID"
  value       = azuread_service_principal.b2c_app.object_id
}

output "groups" {
  description = "Created security groups"
  value = {
    premium_users   = azuread_group.premium_users.object_id
    basic_users     = azuread_group.basic_users.object_id
    administrators  = azuread_group.administrators.object_id
  }
}

output "app_roles" {
  description = "Application roles"
  value = {
    administrator = azuread_application_app_role.admin_role.id
    premium_user  = azuread_application_app_role.premium_user_role.id
    basic_user    = azuread_application_app_role.basic_user_role.id
  }
}

output "conditional_access_policy_id" {
  description = "Conditional access policy ID"
  value       = azuread_conditional_access_policy.mfa_policy.id
}

output "extension_properties" {
  description = "Custom extension properties"
  value = {
    user_preferences = azuread_application_extension_property.user_preferences.name
    subscription_tier = azuread_application_extension_property.subscription_tier.name
    gdpr_consent = azuread_application_extension_property.gdpr_consent.name
  }
}

output "named_location_id" {
  description = "Named location ID for trusted IPs"
  value       = length(var.trusted_ip_ranges) > 0 ? azuread_named_location.trusted_locations[0].id : null
}

output "b2c_configuration" {
  description = "B2C configuration for application"
  value = {
    tenant_name = data.azuread_client_config.current.tenant_id
    client_id   = azuread_application.b2c_app.application_id
    redirect_uris = var.redirect_uris
    spa_redirect_uris = var.spa_redirect_uris
    authority = "https://login.microsoftonline.com/${data.azuread_client_config.current.tenant_id}/v2.0"
    known_authorities = ["https://login.microsoftonline.com/${data.azuread_client_config.current.tenant_id}"]
  }
}

output "compliance_features" {
  description = "Enabled compliance features"
  value = {
    mfa_enabled = var.enable_mfa
    conditional_access_enabled = var.enable_conditional_access
    gdpr_consent_tracking = var.gdpr_compliance.enable_consent_tracking
    data_retention_days = var.gdpr_compliance.data_retention_days
    progressive_profiling = var.progressive_profiling.enable_progressive_profiling
  }
}

output "estimated_monthly_cost_usd" {
  description = "Estimated monthly cost in USD"
  value = {
    azure_ad_b2c = {
      mau_pricing = 50.0  # First 50K MAU free, then $0.0055 per MAU
      premium_features = var.enable_conditional_access ? 3.0 : 0.0  # Premium P1 features
      api_connectors = var.api_connector_config.enable_api_connectors ? 10.0 : 0.0
    }
    conditional_access = var.enable_conditional_access ? 6.0 : 0.0  # Per user per month
    total = 50.0 + (var.enable_conditional_access ? 9.0 : 0.0) + (var.api_connector_config.enable_api_connectors ? 10.0 : 0.0)
  }
}
