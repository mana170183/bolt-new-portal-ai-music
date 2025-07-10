# Ultra Cost-Optimized Development Environment Configuration

environment = "dev"
location = "uksouth"
location_short = "uks"
openai_location = "East US"

# Basic configuration for cost-optimized development
custom_domain = "dev.portal-ai-music.com"
resource_owner = "dev-team"
cost_center = "ai-music-dev"

# Ultra-minimal container configuration for maximum cost savings
container_app_min_replicas = 0  # Allow scale to zero for auto-shutdown
container_app_max_replicas = 2  # Reduced from 3
container_app_cpu_requests = "0.25"  # Reduced from 0.5
container_app_memory_requests = "512Mi"  # Reduced from 1Gi
container_app_cpu_limits = "0.5"  # Reduced from 1.0
container_app_memory_limits = "1Gi"  # Reduced from 2Gi

# Database configuration - Basic tier for development
sql_sku_name = "Basic"
sql_max_size_gb = 2
sql_zone_redundant = false
sql_backup_retention_days = 7
sql_geo_backup_enabled = false

# Storage configuration - LRS for cost savings
storage_account_tier = "Standard"
storage_replication_type = "LRS"  # Locally redundant storage
storage_access_tier = "Hot"

# Redis configuration - Basic tier for development (no SLA but huge cost savings)
redis_sku_name = "Basic"
redis_family = "C"
redis_capacity = 0  # C0 - smallest and cheapest

# Container Registry - Basic tier
container_registry_sku = "Basic"

# AI Services - Minimal capacity for development
openai_gpt4_capacity = 1      # Minimal capacity
openai_gpt35_capacity = 3     # Minimal capacity
openai_embedding_capacity = 1  # Minimal capacity
cognitive_services_sku = "F0"  # Free tier where possible

# Security - Disabled expensive features for dev
enable_private_endpoints = false
enable_advanced_threat_protection = false
enable_azure_defender = false
enable_disk_encryption = false

# Compliance - Minimal for development
data_retention_years = 1  # Reduced from 3
enable_audit_logging = false  # Disabled for cost savings
gdpr_compliance = false  # Not required for dev
soc2_compliance = false

# Performance - Minimal tier for dev
performance_tier = "basic"
enable_autoscaling = true
backup_retention_days = 7
geo_redundant_backup = false

# Feature flags - Disabled expensive features
enable_blue_green_deployment = false
enable_canary_deployment = false
enable_feature_flags = false

# Monitoring - Reduced retention and features
log_retention_days = 30  # Reduced from 90
metrics_retention_days = 7  # Reduced from 30
enable_detailed_monitoring = false

# Cost optimization flags
enable_auto_shutdown = true
shutdown_schedule = {
  weekday_shutdown_time = "18:00"
  weekday_startup_time = "08:00"
  weekend_shutdown = true
}

# Budget configuration
monthly_budget_limit = 300
budget_alert_thresholds = [50, 80, 100]

monitoring_email_receivers = [
  {
    name  = "dev-alerts"
    email = "dev-team@yourcompany.com"
  }
]

# Trusted IP ranges (example - replace with your actual IPs)
trusted_ip_ranges = [
  "203.0.113.0/24",  # Office network
  "198.51.100.0/24"  # VPN network
]

# Cost center tags for detailed tracking
additional_tags = {
  "CostOptimization" = "UltraDev"
  "AutoShutdown" = "Enabled"
  "BudgetLimit" = "300"
}
