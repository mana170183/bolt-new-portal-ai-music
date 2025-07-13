# Azure AD B2C Module for AI Music Portal
# Identity provider with MFA, custom branding, and compliance

terraform {
  required_providers {
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.15"
    }
  }
}

data "azuread_client_config" "current" {}

# Azure AD B2C Tenant
resource "azuread_application" "b2c_app" {
  display_name = var.application_name
  owners       = [data.azuread_client_config.current.object_id]

  # Application settings
  sign_in_audience = "AzureADandPersonalMicrosoftAccount"
  
  # API permissions
  required_resource_access {
    resource_app_id = "00000003-0000-0000-c000-000000000000" # Microsoft Graph

    resource_access {
      id   = "e1fe6dd8-ba31-4d61-89e7-88639da4683d" # User.Read
      type = "Scope"
    }

    resource_access {
      id   = "37f7f235-527c-4136-accd-4a02d197296e" # openid
      type = "Scope"
    }

    resource_access {
      id   = "14dad69e-099b-42c9-810b-d002981feec1" # profile
      type = "Scope"
    }

    resource_access {
      id   = "64a6cdd6-aab1-4aaf-94b8-3cc8405e90d0" # email
      type = "Scope"
    }
  }

  # Web configuration
  web {
    redirect_uris = var.redirect_uris
    
    implicit_grant {
      access_token_issuance_enabled = true
      id_token_issuance_enabled     = true
    }
  }

  # SPA configuration
  single_page_application {
    redirect_uris = var.spa_redirect_uris
  }

  # Optional claims
  optional_claims {
    access_token {
      name = "email"
    }
    access_token {
      name = "given_name"
    }
    access_token {
      name = "family_name"
    }
    id_token {
      name = "email"
    }
    id_token {
      name = "given_name"
    }
    id_token {
      name = "family_name"
    }
  }

  tags = var.tags
}

# Service Principal for the application
resource "azuread_service_principal" "b2c_app" {
  application_id               = azuread_application.b2c_app.application_id
  app_role_assignment_required = false
  owners                      = [data.azuread_client_config.current.object_id]

  tags = var.tags
}

# Application password/secret
resource "azuread_application_password" "b2c_app" {
  application_object_id = azuread_application.b2c_app.object_id
  display_name         = "B2C Application Secret"
  end_date_relative    = "8760h" # 1 year
}

# Custom attribute definitions for B2C
resource "azuread_application_extension_property" "user_preferences" {
  application_object_id = azuread_application.b2c_app.object_id
  display_name         = "UserPreferences"
  name                 = "UserPreferences"
  data_type            = "String"
}

resource "azuread_application_extension_property" "subscription_tier" {
  application_object_id = azuread_application.b2c_app.object_id
  display_name         = "SubscriptionTier"
  name                 = "SubscriptionTier"
  data_type            = "String"
}

resource "azuread_application_extension_property" "gdpr_consent" {
  application_object_id = azuread_application.b2c_app.object_id
  display_name         = "GDPRConsent"
  name                 = "GDPRConsent"
  data_type            = "Boolean"
}

# Groups for different user roles
resource "azuread_group" "premium_users" {
  display_name     = "${var.application_name}-premium-users"
  owners          = [data.azuread_client_config.current.object_id]
  security_enabled = true
  description     = "Premium subscription users"
}

resource "azuread_group" "basic_users" {
  display_name     = "${var.application_name}-basic-users"
  owners          = [data.azuread_client_config.current.object_id]
  security_enabled = true
  description     = "Basic subscription users"
}

resource "azuread_group" "administrators" {
  display_name     = "${var.application_name}-administrators"
  owners          = [data.azuread_client_config.current.object_id]
  security_enabled = true
  description     = "Application administrators"
}

# Conditional Access Policy for MFA
resource "azuread_conditional_access_policy" "mfa_policy" {
  display_name = "${var.application_name}-mfa-policy"
  state        = "enabled"

  conditions {
    client_app_types = ["all"]

    applications {
      included_applications = [azuread_application.b2c_app.application_id]
    }

    users {
      included_groups = [
        azuread_group.premium_users.object_id,
        azuread_group.basic_users.object_id
      ]
    }

    locations {
      included_locations = ["All"]
    }

    platforms {
      included_platforms = ["all"]
    }

    sign_in_risk_levels = ["high", "medium"]
    user_risk_levels   = ["high", "medium"]
  }

  grant_controls {
    operator          = "OR"
    built_in_controls = ["mfa"]
  }

  session_controls {
    application_enforced_restrictions_enabled = true
    cloud_app_security_policy                = "monitorOnly"
    sign_in_frequency                         = 24
    sign_in_frequency_period                  = "hours"
  }
}

# App role definitions
resource "azuread_application_app_role" "admin_role" {
  application_object_id = azuread_application.b2c_app.object_id
  allowed_member_types  = ["User"]
  description          = "Administrators can manage the application"
  display_name         = "Administrator"
  enabled              = true
  id                   = "00000000-0000-0000-0000-000000000001"
  value                = "Administrator"
}

resource "azuread_application_app_role" "premium_user_role" {
  application_object_id = azuread_application.b2c_app.object_id
  allowed_member_types  = ["User"]
  description          = "Premium users with full access"
  display_name         = "PremiumUser"
  enabled              = true
  id                   = "00000000-0000-0000-0000-000000000002"
  value                = "PremiumUser"
}

resource "azuread_application_app_role" "basic_user_role" {
  application_object_id = azuread_application.b2c_app.object_id
  allowed_member_types  = ["User"]
  description          = "Basic users with limited access"
  display_name         = "BasicUser"
  enabled              = true
  id                   = "00000000-0000-0000-0000-000000000003"
  value                = "BasicUser"
}

# Store secrets in Key Vault
resource "azurerm_key_vault_secret" "b2c_client_id" {
  name         = "b2c-client-id"
  value        = azuread_application.b2c_app.application_id
  key_vault_id = var.key_vault_id
  tags         = var.tags
}

resource "azurerm_key_vault_secret" "b2c_client_secret" {
  name         = "b2c-client-secret"
  value        = azuread_application_password.b2c_app.value
  key_vault_id = var.key_vault_id
  tags         = var.tags
}

# Named locations for conditional access
resource "azuread_named_location" "trusted_locations" {
  count        = length(var.trusted_ip_ranges) > 0 ? 1 : 0
  display_name = "${var.application_name}-trusted-locations"

  ip {
    ip_ranges = var.trusted_ip_ranges
    trusted   = true
  }
}

# Directory extension for custom claims
resource "azuread_directory_role_assignment" "directory_readers" {
  role_id             = "88d8e3e3-8f55-4a1e-953a-9b9898b8876b" # Directory Readers
  principal_object_id = azuread_service_principal.b2c_app.object_id
}
