# Container Registry Module Variables

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

variable "sku" {
  description = "SKU for the container registry"
  type        = string
  default     = "Premium"
  
  validation {
    condition     = contains(["Basic", "Standard", "Premium"], var.sku)
    error_message = "SKU must be Basic, Standard, or Premium."
  }
}

variable "admin_enabled" {
  description = "Enable admin user for the container registry"
  type        = bool
  default     = false
}

variable "enable_geo_replication" {
  description = "Enable geo-replication for Premium tier"
  type        = bool
  default     = true
}

variable "geo_replication_locations" {
  description = "List of Azure regions for geo-replication"
  type        = list(string)
  default     = ["westeurope", "eastus"]
}

variable "webhook_service_uri" {
  description = "Service URI for vulnerability scanning webhook"
  type        = string
  default     = "https://example.com/webhook"
}

variable "container_app_identity_id" {
  description = "Resource ID of the container app managed identity"
  type        = string
  default     = null
}

variable "log_analytics_workspace_id" {
  description = "Log Analytics workspace ID for diagnostics"
  type        = string
  default     = null
}

variable "enable_private_endpoint" {
  description = "Enable private endpoint for ACR"
  type        = bool
  default     = false
}

variable "private_endpoint_subnet_id" {
  description = "Subnet ID for private endpoint"
  type        = string
  default     = null
}

variable "github_token" {
  description = "GitHub token for ACR tasks"
  type        = string
  default     = null
  sensitive   = true
}
