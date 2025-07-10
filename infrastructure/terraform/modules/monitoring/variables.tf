variable "log_analytics_name" {
  description = "Name of the Log Analytics workspace"
  type        = string
}

variable "application_insights_name" {
  description = "Name of the Application Insights instance"
  type        = string
}

variable "action_group_name" {
  description = "Name of the action group"
  type        = string
}

variable "action_group_short_name" {
  description = "Short name of the action group (max 12 chars)"
  type        = string
  validation {
    condition     = length(var.action_group_short_name) <= 12
    error_message = "Action group short name must be 12 characters or less."
  }
}

variable "location" {
  description = "Azure region for resources"
  type        = string
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
}

variable "log_analytics_sku" {
  description = "SKU for Log Analytics workspace"
  type        = string
  default     = "PerGB2018"
  validation {
    condition     = contains(["Free", "Standalone", "PerNode", "PerGB2018"], var.log_analytics_sku)
    error_message = "Log Analytics SKU must be one of: Free, Standalone, PerNode, PerGB2018."
  }
}

variable "retention_days" {
  description = "Data retention in days"
  type        = number
  default     = 90
  validation {
    condition     = var.retention_days >= 30 && var.retention_days <= 730
    error_message = "Retention days must be between 30 and 730."
  }
}

variable "sampling_percentage" {
  description = "Application Insights sampling percentage"
  type        = number
  default     = 100
  validation {
    condition     = var.sampling_percentage >= 0 && var.sampling_percentage <= 100
    error_message = "Sampling percentage must be between 0 and 100."
  }
}

variable "monitored_resource_ids" {
  description = "List of resource IDs to monitor"
  type        = list(string)
  default     = []
}

variable "key_vault_id" {
  description = "Key Vault ID for storing secrets"
  type        = string
}

# Alert thresholds
variable "cpu_threshold" {
  description = "CPU usage threshold for alerts (percentage)"
  type        = number
  default     = 80
}

variable "memory_threshold" {
  description = "Memory usage threshold for alerts (percentage)"
  type        = number
  default     = 80
}

variable "response_time_threshold" {
  description = "Response time threshold for alerts (milliseconds)"
  type        = number
  default     = 5000
}

variable "error_rate_threshold" {
  description = "Error rate threshold for alerts (count)"
  type        = number
  default     = 10
}

# Notification receivers
variable "email_receivers" {
  description = "Email receivers for alerts"
  type = list(object({
    name  = string
    email = string
  }))
  default = []
}

variable "sms_receivers" {
  description = "SMS receivers for alerts"
  type = list(object({
    name         = string
    country_code = string
    phone_number = string
  }))
  default = []
}

variable "webhook_receivers" {
  description = "Webhook receivers for alerts"
  type = list(object({
    name = string
    uri  = string
  }))
  default = []
}

variable "function_receivers" {
  description = "Azure Function receivers for alerts"
  type = list(object({
    name            = string
    function_app_id = string
    function_name   = string
    trigger_url     = string
  }))
  default = []
}

# Monitoring configuration
variable "enable_application_insights" {
  description = "Enable Application Insights"
  type        = bool
  default     = true
}

variable "enable_log_analytics" {
  description = "Enable Log Analytics"
  type        = bool
  default     = true
}

variable "enable_alerts" {
  description = "Enable monitoring alerts"
  type        = bool
  default     = true
}

variable "enable_dashboard" {
  description = "Enable monitoring dashboard"
  type        = bool
  default     = true
}

variable "custom_metrics" {
  description = "Custom metrics to track"
  type = list(object({
    name        = string
    namespace   = string
    description = string
  }))
  default = []
}

variable "compliance_monitoring" {
  description = "Compliance monitoring configuration"
  type = object({
    enable_gdpr_monitoring    = bool
    enable_soc2_monitoring    = bool
    enable_audit_logging      = bool
    audit_retention_days      = number
  })
  default = {
    enable_gdpr_monitoring = true
    enable_soc2_monitoring = true
    enable_audit_logging   = true
    audit_retention_days   = 2555  # 7 years
  }
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
