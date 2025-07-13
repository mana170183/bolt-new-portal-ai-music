# Key Vault Module Variables

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "location" {
  description = "Azure region"
  type        = string
}

variable "naming_convention" {
  description = "Naming convention map"
  type        = map(string)
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
}

variable "tenant_id" {
  description = "Azure AD tenant ID"
  type        = string
}

variable "object_id" {
  description = "Object ID of the current user/service principal"
  type        = string
}

variable "container_app_principal_id" {
  description = "Principal ID of the container app managed identity"
  type        = string
  default     = null
}

variable "allowed_ip_ranges" {
  description = "List of allowed IP ranges for Key Vault access"
  type        = list(string)
  default     = []
}

variable "allowed_subnet_ids" {
  description = "List of allowed subnet IDs for Key Vault access"
  type        = list(string)
  default     = []
}

variable "log_analytics_workspace_id" {
  description = "Log Analytics workspace ID for diagnostics"
  type        = string
  default     = null
}

variable "enable_private_endpoint" {
  description = "Enable private endpoint for Key Vault"
  type        = bool
  default     = false
}

variable "private_endpoint_subnet_id" {
  description = "Subnet ID for private endpoint"
  type        = string
  default     = null
}

# Secret values (will be provided by other modules or CI/CD)
variable "database_connection_string" {
  description = "Database connection string"
  type        = string
  default     = null
  sensitive   = true
}

variable "redis_connection_string" {
  description = "Redis connection string"
  type        = string
  default     = null
  sensitive   = true
}

variable "storage_connection_string" {
  description = "Storage connection string"
  type        = string
  default     = null
  sensitive   = true
}

variable "openai_api_key" {
  description = "OpenAI API key"
  type        = string
  default     = null
  sensitive   = true
}

variable "cognitive_services_key" {
  description = "Cognitive Services API key"
  type        = string
  default     = null
  sensitive   = true
}

variable "app_insights_connection_string" {
  description = "Application Insights connection string"
  type        = string
  default     = null
  sensitive   = true
}

variable "ssl_certificate_data" {
  description = "SSL certificate data for custom domain"
  type        = string
  default     = null
  sensitive   = true
}

variable "ssl_certificate_password" {
  description = "SSL certificate password"
  type        = string
  default     = null
  sensitive   = true
}
