variable "cognitive_services_name" {
  description = "Name of the Cognitive Services account"
  type        = string
}

variable "openai_name" {
  description = "Name of the OpenAI service"
  type        = string
}

variable "speech_service_name" {
  description = "Name of the Speech service"
  type        = string
}

variable "ml_workspace_name" {
  description = "Name of the ML workspace"
  type        = string
}

variable "search_service_name" {
  description = "Name of the Search service"
  type        = string
}

variable "location" {
  description = "Azure region for resources"
  type        = string
}

variable "openai_location" {
  description = "Azure region for OpenAI (limited availability)"
  type        = string
  default     = "East US"
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "cognitive_services_sku" {
  description = "SKU for Cognitive Services"
  type        = string
  default     = "S0"
}

variable "speech_sku" {
  description = "SKU for Speech service"
  type        = string
  default     = "S0"
}

variable "search_sku" {
  description = "SKU for Search service"
  type        = string
  default     = "standard"
  validation {
    condition     = contains(["free", "basic", "standard", "standard2", "standard3", "storage_optimized_l1", "storage_optimized_l2"], var.search_sku)
    error_message = "Search SKU must be one of: free, basic, standard, standard2, standard3, storage_optimized_l1, storage_optimized_l2."
  }
}

variable "search_replica_count" {
  description = "Number of replicas for Search service"
  type        = number
  default     = 1
}

variable "search_partition_count" {
  description = "Number of partitions for Search service"
  type        = number
  default     = 1
}

variable "gpt4_capacity" {
  description = "Capacity for GPT-4 deployment"
  type        = number
  default     = 10
}

variable "gpt35_capacity" {
  description = "Capacity for GPT-3.5 deployment"
  type        = number
  default     = 20
}

variable "embedding_capacity" {
  description = "Capacity for text embedding deployment"
  type        = number
  default     = 10
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
  description = "Enable private endpoints"
  type        = bool
  default     = true
}

variable "private_endpoint_subnet_id" {
  description = "Subnet ID for private endpoints"
  type        = string
  default     = ""
}

variable "private_dns_zone_ids" {
  description = "Private DNS zone IDs"
  type        = list(string)
  default     = []
}

variable "key_vault_id" {
  description = "Key Vault ID for storing secrets"
  type        = string
}

variable "storage_account_id" {
  description = "Storage account ID for ML workspace"
  type        = string
}

variable "container_registry_id" {
  description = "Container registry ID for ML workspace"
  type        = string
}

variable "application_insights_id" {
  description = "Application Insights ID for ML workspace"
  type        = string
}

variable "log_analytics_workspace_id" {
  description = "Log Analytics workspace ID"
  type        = string
}

variable "search_service_id" {
  description = "Search service ID for QnA"
  type        = string
  default     = ""
}

variable "cmk_key_id" {
  description = "Customer-managed key ID for encryption"
  type        = string
  default     = ""
}

variable "user_assigned_identity_id" {
  description = "User-assigned identity ID for encryption"
  type        = string
  default     = ""
}

variable "application_principal_id" {
  description = "Application principal ID for RBAC"
  type        = string
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
