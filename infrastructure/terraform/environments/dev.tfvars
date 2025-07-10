# Development Environment Configuration for Portal AI Music

environment = "dev"
location = "uksouth"
location_short = "uks"
openai_location = "East US"

# Basic configuration for development
custom_domain = "dev.portal-ai-music.com"
resource_owner = "dev-team"
cost_center = "ai-music-dev"

# Minimal configuration for development
container_app_min_replicas = 1
container_app_max_replicas = 3
container_app_cpu_requests = "0.25"
container_app_memory_requests = "512Mi"
container_app_cpu_limits = "1.0"
container_app_memory_limits = "2Gi"

# AI Services - reduced capacity for dev
openai_gpt4_capacity = 2
openai_gpt35_capacity = 5
openai_embedding_capacity = 2

# Security - basic settings for dev
enable_private_endpoints = false
enable_advanced_threat_protection = false
enable_azure_defender = false

# Compliance - basic for development
data_retention_years = 3
enable_audit_logging = true
gdpr_compliance = true
soc2_compliance = false

# Performance - basic tier for dev
performance_tier = "basic"
enable_autoscaling = true
backup_retention_days = 7
geo_redundant_backup = false

# Feature flags
enable_blue_green_deployment = false
enable_canary_deployment = false
enable_feature_flags = true

# Monitoring
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
