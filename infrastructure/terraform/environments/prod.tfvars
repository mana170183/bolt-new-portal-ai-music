# Production Environment Configuration for Portal AI Music

environment = "prod"
location = "uksouth"
location_short = "uks"
openai_location = "East US"

# Production configuration
custom_domain = "portal-ai-music.com"
resource_owner = "production-team"
cost_center = "ai-music-prod"

# Production-scale configuration
container_app_min_replicas = 3
container_app_max_replicas = 30
container_app_cpu_requests = "1.0"
container_app_memory_requests = "2Gi"
container_app_cpu_limits = "4.0"
container_app_memory_limits = "8Gi"

# AI Services - full capacity for production
openai_gpt4_capacity = 10
openai_gpt35_capacity = 20
openai_embedding_capacity = 10

# Security - maximum security for production
enable_private_endpoints = true
enable_advanced_threat_protection = true
enable_azure_defender = true

# Compliance - full compliance for production
data_retention_years = 7
enable_audit_logging = true
gdpr_compliance = true
soc2_compliance = true

# Performance - premium tier for production
performance_tier = "premium"
enable_autoscaling = true
backup_retention_days = 90
geo_redundant_backup = true

# Feature flags
enable_blue_green_deployment = true
enable_canary_deployment = false  # Use blue-green for production
enable_feature_flags = true

# Monitoring - comprehensive for production
monitoring_email_receivers = [
  {
    name  = "production-alerts"
    email = "production-team@yourcompany.com"
  },
  {
    name  = "ops-team"
    email = "ops-team@yourcompany.com"
  },
  {
    name  = "security-team"
    email = "security-team@yourcompany.com"
  },
  {
    name  = "management"
    email = "management@yourcompany.com"
  }
]

# Trusted IP ranges (example - replace with your actual IPs)
# Production should have stricter IP restrictions
trusted_ip_ranges = [
  "203.0.113.0/24",  # Office network
  "198.51.100.0/24"  # Admin VPN network
]
