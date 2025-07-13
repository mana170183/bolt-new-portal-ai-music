# Variables for Portal AI Music Azure Infrastructure

# Environment Configuration
variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "uksouth"
}

variable "location_short" {
  description = "Short form of location for naming"
  type        = string
  default     = "uks"
}

variable "openai_location" {
  description = "Azure region for OpenAI services (limited availability)"
  type        = string
  default     = "East US"
  validation {
    condition     = contains(["East US", "West Europe", "South Central US"], var.openai_location)
    error_message = "OpenAI location must be one of the supported regions."
  }
}

# Tagging Configuration
variable "resource_owner" {
  description = "Owner of the resources"
  type        = string
  default     = "portal-ai-team"
}

variable "cost_center" {
  description = "Cost center for billing"
  type        = string
  default     = "ai-music-platform"
}

# Network Configuration
variable "custom_domain" {
  description = "Custom domain for the application"
  type        = string
  default     = "portal-ai-music.com"
}

variable "trusted_ip_ranges" {
  description = "Trusted IP ranges for conditional access"
  type        = list(string)
  default     = []
}

# Monitoring Configuration
variable "monitoring_email_receivers" {
  description = "Email addresses for monitoring alerts"
  type = list(object({
    name  = string
    email = string
  }))
  default = []
}

# Container App Configuration
variable "container_app_min_replicas" {
  description = "Minimum number of container app replicas"
  type        = number
  default     = 2
  validation {
    condition     = var.container_app_min_replicas >= 1 && var.container_app_min_replicas <= 100
    error_message = "Min replicas must be between 1 and 100."
  }
}

variable "container_app_max_replicas" {
  description = "Maximum number of container app replicas"
  type        = number
  default     = 30
  validation {
    condition     = var.container_app_max_replicas >= 1 && var.container_app_max_replicas <= 300
    error_message = "Max replicas must be between 1 and 300."
  }
}

variable "container_app_cpu_requests" {
  description = "CPU requests for container app"
  type        = string
  default     = "0.5"
  validation {
    condition     = can(regex("^[0-9]+(\\.[0-9]+)?$", var.container_app_cpu_requests))
    error_message = "CPU requests must be a valid number."
  }
}

variable "container_app_memory_requests" {
  description = "Memory requests for container app"
  type        = string
  default     = "1Gi"
  validation {
    condition     = can(regex("^[0-9]+(\\.[0-9]+)?(Gi|Mi)$", var.container_app_memory_requests))
    error_message = "Memory requests must be in format like '1Gi' or '512Mi'."
  }
}

variable "container_app_cpu_limits" {
  description = "CPU limits for container app"
  type        = string
  default     = "2.0"
  validation {
    condition     = can(regex("^[0-9]+(\\.[0-9]+)?$", var.container_app_cpu_limits))
    error_message = "CPU limits must be a valid number."
  }
}

variable "container_app_memory_limits" {
  description = "Memory limits for container app"
  type        = string
  default     = "4Gi"
  validation {
    condition     = can(regex("^[0-9]+(\\.[0-9]+)?(Gi|Mi)$", var.container_app_memory_limits))
    error_message = "Memory limits must be in format like '4Gi' or '2048Mi'."
  }
}

# AI Services Configuration
variable "openai_gpt4_capacity" {
  description = "Capacity for GPT-4 deployment"
  type        = number
  default     = 10
  validation {
    condition     = var.openai_gpt4_capacity >= 1 && var.openai_gpt4_capacity <= 120
    error_message = "GPT-4 capacity must be between 1 and 120."
  }
}

variable "openai_gpt35_capacity" {
  description = "Capacity for GPT-3.5 deployment"
  type        = number
  default     = 20
  validation {
    condition     = var.openai_gpt35_capacity >= 1 && var.openai_gpt35_capacity <= 120
    error_message = "GPT-3.5 capacity must be between 1 and 120."
  }
}

variable "openai_embedding_capacity" {
  description = "Capacity for text embedding deployment"
  type        = number
  default     = 10
  validation {
    condition     = var.openai_embedding_capacity >= 1 && var.openai_embedding_capacity <= 120
    error_message = "Embedding capacity must be between 1 and 120."
  }
}

# Security Configuration
variable "enable_private_endpoints" {
  description = "Enable private endpoints for all services"
  type        = bool
  default     = true
}

variable "enable_advanced_threat_protection" {
  description = "Enable advanced threat protection"
  type        = bool
  default     = true
}

variable "enable_azure_defender" {
  description = "Enable Azure Defender for all services"
  type        = bool
  default     = true
}

# Compliance Configuration
variable "data_retention_years" {
  description = "Data retention period in years for compliance"
  type        = number
  default     = 7
  validation {
    condition     = var.data_retention_years >= 3 && var.data_retention_years <= 10
    error_message = "Data retention must be between 3 and 10 years."
  }
}

variable "enable_audit_logging" {
  description = "Enable comprehensive audit logging"
  type        = bool
  default     = true
}

variable "gdpr_compliance" {
  description = "Enable GDPR compliance features"
  type        = bool
  default     = true
}

variable "soc2_compliance" {
  description = "Enable SOC 2 compliance features"
  type        = bool
  default     = true
}

# Backup Configuration
variable "backup_retention_days" {
  description = "Backup retention in days"
  type        = number
  default     = 90
  validation {
    condition     = var.backup_retention_days >= 7 && var.backup_retention_days <= 2555
    error_message = "Backup retention must be between 7 and 2555 days."
  }
}

variable "geo_redundant_backup" {
  description = "Enable geo-redundant backup"
  type        = bool
  default     = true
}

# Performance Configuration
variable "enable_autoscaling" {
  description = "Enable autoscaling for compute resources"
  type        = bool
  default     = true
}

variable "performance_tier" {
  description = "Performance tier (basic, standard, premium)"
  type        = string
  default     = "premium"
  validation {
    condition     = contains(["basic", "standard", "premium"], var.performance_tier)
    error_message = "Performance tier must be basic, standard, or premium."
  }
}

# Feature Flags
variable "enable_blue_green_deployment" {
  description = "Enable blue-green deployment strategy"
  type        = bool
  default     = true
}

variable "enable_canary_deployment" {
  description = "Enable canary deployment strategy"
  type        = bool
  default     = false
}

variable "enable_feature_flags" {
  description = "Enable feature flag management"
  type        = bool
  default     = true
}

# Storage Configuration
variable "storage_account_tier" {
  description = "Storage account tier"
  type        = string
  default     = "Standard"
}

variable "storage_replication_type" {
  description = "Storage replication type"
  type        = string
  default     = "ZRS" # Zone-redundant storage
}

# Redis Configuration
variable "redis_sku_name" {
  description = "Redis SKU name"
  type        = string
  default     = "Premium"
}

variable "redis_family" {
  description = "Redis family"
  type        = string
  default     = "P"
}

variable "redis_capacity" {
  description = "Redis capacity"
  type        = number
  default     = 1
}

# AI Services Configuration
variable "openai_sku" {
  description = "OpenAI service SKU"
  type        = string
  default     = "S0"
}

variable "cognitive_services_sku" {
  description = "Cognitive Services SKU"
  type        = string
  default     = "S0"
}

# Azure AD B2C Configuration
variable "enable_ad_b2c" {
  description = "Enable Azure AD B2C deployment"
  type        = bool
  default     = false
}

variable "b2c_domain_name" {
  description = "Azure AD B2C domain name"
  type        = string
  default     = "portalaimusic"
}

# Application Configuration
variable "app_settings" {
  description = "Application settings for Container App"
  type        = map(string)
  default = {
    NODE_ENV = "production"
    PORT     = "3000"
  }
}

# Security Configuration
variable "allowed_ip_ranges" {
  description = "Allowed IP ranges for firewall rules"
  type        = list(string)
  default     = ["0.0.0.0/0"] # Should be restricted in production
}

# Monitoring Configuration
variable "enable_application_insights" {
  description = "Enable Application Insights"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "Log retention days"
  type        = number
  default     = 90
}

# Backup Configuration
variable "backup_retention_days" {
  description = "Backup retention days"
  type        = number
  default     = 30
}

# Scaling Configuration
variable "autoscale_enabled" {
  description = "Enable autoscaling"
  type        = bool
  default     = true
}

variable "max_concurrent_users" {
  description = "Maximum concurrent users for scaling calculations"
  type        = number
  default     = 100
}

# Development Configuration
variable "enable_debug_mode" {
  description = "Enable debug mode for development environments"
  type        = bool
  default     = false
}

# Cost Optimization Variables
variable "sql_sku_name" {
  description = "SQL Database SKU name"
  type        = string
  default     = "GP_Gen5_2"
  validation {
    condition     = contains(["Basic", "S0", "S1", "S2", "GP_Gen5_2", "GP_Gen5_4", "BC_Gen5_2"], var.sql_sku_name)
    error_message = "SQL SKU must be a valid Azure SQL Database SKU."
  }
}

variable "sql_max_size_gb" {
  description = "Maximum size of SQL Database in GB"
  type        = number
  default     = 32
}

variable "sql_zone_redundant" {
  description = "Enable zone redundancy for SQL Database"
  type        = bool
  default     = true
}

variable "sql_geo_backup_enabled" {
  description = "Enable geo-redundant backup for SQL Database"
  type        = bool
  default     = true
}

variable "container_registry_sku" {
  description = "Container Registry SKU"
  type        = string
  default     = "Standard"
  validation {
    condition     = contains(["Basic", "Standard", "Premium"], var.container_registry_sku)
    error_message = "Container Registry SKU must be Basic, Standard, or Premium."
  }
}

variable "enable_auto_shutdown" {
  description = "Enable auto-shutdown for development environments"
  type        = bool
  default     = false
}

variable "shutdown_schedule" {
  description = "Auto-shutdown schedule configuration"
  type = object({
    weekday_shutdown_time = string
    weekday_startup_time  = string
    weekend_shutdown      = bool
  })
  default = {
    weekday_shutdown_time = "18:00"
    weekday_startup_time  = "08:00"
    weekend_shutdown      = false
  }
}

variable "monthly_budget_limit" {
  description = "Monthly budget limit in USD"
  type        = number
  default     = 1000
}

variable "budget_alert_thresholds" {
  description = "Budget alert thresholds as percentages"
  type        = list(number)
  default     = [50, 80, 100]
}

variable "log_retention_days" {
  description = "Log Analytics retention in days"
  type        = number
  default     = 90
}

variable "metrics_retention_days" {
  description = "Metrics retention in days"  
  type        = number
  default     = 30
}

variable "enable_detailed_monitoring" {
  description = "Enable detailed monitoring (additional cost)"
  type        = bool
  default     = true
}

variable "additional_tags" {
  description = "Additional tags for cost tracking"
  type        = map(string)
  default     = {}
}
