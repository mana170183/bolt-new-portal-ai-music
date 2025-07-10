# Variables for SQL Database Module

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "location" {
  description = "Azure location"
  type        = string
}

variable "naming_convention" {
  description = "Naming convention object"
  type = object({
    sql_server = string
  })
}

variable "common_tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default     = {}
}

variable "key_vault_id" {
  description = "Key Vault ID for storing secrets"
  type        = string
}

variable "log_analytics_workspace_id" {
  description = "Log Analytics workspace ID for diagnostics"
  type        = string
}

variable "enable_private_endpoint" {
  description = "Enable private endpoint for SQL Database"
  type        = bool
  default     = false
}

variable "private_endpoint_subnet_id" {
  description = "Subnet ID for private endpoint"
  type        = string
  default     = null
}

variable "allowed_subnet_ids" {
  description = "List of subnet IDs allowed to access the database"
  type        = list(string)
  default     = []
}
