variable "redis_name" {
  description = "Name of the Redis cache"
  type        = string
}

variable "location" {
  description = "Azure region for resources"
  type        = string
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "capacity" {
  description = "Redis cache capacity"
  type        = number
  default     = 1
  validation {
    condition     = var.capacity >= 0 && var.capacity <= 120
    error_message = "Capacity must be between 0 and 120."
  }
}

variable "family" {
  description = "Redis cache family"
  type        = string
  default     = "P"
  validation {
    condition     = contains(["C", "P"], var.family)
    error_message = "Family must be either C (Basic/Standard) or P (Premium)."
  }
}

variable "sku_name" {
  description = "Redis cache SKU"
  type        = string
  default     = "Premium"
  validation {
    condition     = contains(["Basic", "Standard", "Premium"], var.sku_name)
    error_message = "SKU must be Basic, Standard, or Premium."
  }
}

variable "maxmemory_reserved" {
  description = "Maxmemory reserved setting"
  type        = number
  default     = 200
}

variable "maxmemory_delta" {
  description = "Maxmemory delta setting"
  type        = number
  default     = 200
}

variable "backup_enabled" {
  description = "Enable RDB backup"
  type        = bool
  default     = true
}

variable "backup_frequency" {
  description = "Backup frequency in minutes"
  type        = number
  default     = 60
  validation {
    condition     = contains([15, 30, 60, 360, 720, 1440], var.backup_frequency)
    error_message = "Backup frequency must be 15, 30, 60, 360, 720, or 1440 minutes."
  }
}

variable "backup_max_snapshots" {
  description = "Maximum number of backup snapshots"
  type        = number
  default     = 1
}

variable "backup_storage_connection_string" {
  description = "Storage connection string for backups"
  type        = string
  default     = ""
}

variable "aof_backup_enabled" {
  description = "Enable AOF backup"
  type        = bool
  default     = false
}

variable "aof_storage_connection_string" {
  description = "Storage connection string for AOF backups"
  type        = string
  default     = ""
}

variable "public_access_enabled" {
  description = "Enable public network access"
  type        = bool
  default     = false
}

variable "allowed_ip_ranges" {
  description = "List of allowed IP ranges"
  type        = list(string)
  default     = []
}

variable "enable_private_endpoint" {
  description = "Enable private endpoint"
  type        = bool
  default     = true
}

variable "private_endpoint_subnet_id" {
  description = "Subnet ID for private endpoint"
  type        = string
  default     = ""
}

variable "private_dns_zone_ids" {
  description = "Private DNS zone IDs"
  type        = list(string)
  default     = []
}

variable "log_analytics_workspace_id" {
  description = "Log Analytics workspace ID"
  type        = string
}

variable "key_vault_id" {
  description = "Key Vault ID for storing secrets"
  type        = string
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
