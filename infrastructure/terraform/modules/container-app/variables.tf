# Container App Module Variables

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "location" {
  description = "Azure region"
  type        = string
}

variable "app_name" {
  description = "Application name"
  type        = string
}

variable "environment" {
  description = "Environment name"
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

variable "min_replicas" {
  description = "Minimum number of replicas"
  type        = number
  default     = 1
}

variable "max_replicas" {
  description = "Maximum number of replicas"
  type        = number
  default     = 5
}

variable "cpu_requests" {
  description = "CPU requests"
  type        = string
  default     = "0.5"
}

variable "memory_requests" {
  description = "Memory requests"
  type        = string
  default     = "1Gi"
}

variable "cpu_limits" {
  description = "CPU limits"
  type        = string
  default     = "2.0"
}

variable "memory_limits" {
  description = "Memory limits"
  type        = string
  default     = "4Gi"
}

variable "custom_domain" {
  description = "Custom domain for the container app"
  type        = string
  default     = null
}
