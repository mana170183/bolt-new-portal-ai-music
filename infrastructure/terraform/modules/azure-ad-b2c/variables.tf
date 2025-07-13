variable "application_name" {
  description = "Name of the B2C application"
  type        = string
}

variable "redirect_uris" {
  description = "Redirect URIs for the application"
  type        = list(string)
  default     = []
}

variable "spa_redirect_uris" {
  description = "SPA redirect URIs for the application"
  type        = list(string)
  default     = []
}

variable "trusted_ip_ranges" {
  description = "Trusted IP ranges for conditional access"
  type        = list(string)
  default     = []
}

variable "key_vault_id" {
  description = "Key Vault ID for storing secrets"
  type        = string
}

variable "enable_mfa" {
  description = "Enable multi-factor authentication"
  type        = bool
  default     = true
}

variable "enable_conditional_access" {
  description = "Enable conditional access policies"
  type        = bool
  default     = true
}

variable "session_timeout_hours" {
  description = "Session timeout in hours"
  type        = number
  default     = 24
  validation {
    condition     = var.session_timeout_hours >= 1 && var.session_timeout_hours <= 720
    error_message = "Session timeout must be between 1 and 720 hours."
  }
}

variable "password_complexity" {
  description = "Password complexity requirements"
  type = object({
    min_length          = number
    require_uppercase   = bool
    require_lowercase   = bool
    require_numbers     = bool
    require_symbols     = bool
  })
  default = {
    min_length        = 12
    require_uppercase = true
    require_lowercase = true
    require_numbers   = true
    require_symbols   = true
  }
}

variable "custom_domain" {
  description = "Custom domain for B2C tenant"
  type        = string
  default     = ""
}

variable "branding_config" {
  description = "Branding configuration for B2C"
  type = object({
    background_color     = string
    banner_logo_url     = string
    square_logo_url     = string
    company_name        = string
    privacy_policy_url  = string
    terms_of_use_url    = string
  })
  default = {
    background_color    = "#ffffff"
    banner_logo_url    = ""
    square_logo_url    = ""
    company_name       = "AI Music Portal"
    privacy_policy_url = ""
    terms_of_use_url   = ""
  }
}

variable "gdpr_compliance" {
  description = "GDPR compliance settings"
  type = object({
    enable_consent_tracking = bool
    data_retention_days     = number
    enable_data_export      = bool
    enable_data_deletion    = bool
  })
  default = {
    enable_consent_tracking = true
    data_retention_days     = 2555  # 7 years
    enable_data_export      = true
    enable_data_deletion    = true
  }
}

variable "sso_providers" {
  description = "External SSO providers to enable"
  type = object({
    enable_google    = bool
    enable_facebook  = bool
    enable_microsoft = bool
    enable_apple     = bool
  })
  default = {
    enable_google    = true
    enable_facebook  = false
    enable_microsoft = true
    enable_apple     = false
  }
}

variable "progressive_profiling" {
  description = "Progressive profiling configuration"
  type = object({
    enable_progressive_profiling = bool
    required_attributes         = list(string)
    optional_attributes         = list(string)
  })
  default = {
    enable_progressive_profiling = true
    required_attributes         = ["email", "displayName"]
    optional_attributes         = ["givenName", "surname", "country"]
  }
}

variable "api_connector_config" {
  description = "API connector configuration for custom logic"
  type = object({
    enable_api_connectors = bool
    webhook_endpoints     = list(string)
    authentication_type   = string
  })
  default = {
    enable_api_connectors = false
    webhook_endpoints     = []
    authentication_type   = "basic"
  }
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
