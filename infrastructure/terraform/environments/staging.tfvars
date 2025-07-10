# Staging Environment Configuration for Portal AI Music

environment = "staging"
location = "uksouth"
location_short = "uks"
openai_location = "East US"

# Staging configuration - production-like but scaled down
custom_domain = "staging.portal-ai-music.com"
resource_owner = "staging-team"
cost_center = "ai-music-staging"

# Moderate configuration for staging
container_app_min_replicas = 2
container_app_max_replicas = 10
container_app_cpu_requests = "0.5"
container_app_memory_requests = "1Gi"
container_app_cpu_limits = "2.0"
container_app_memory_limits = "4Gi"

# AI Services - moderate capacity for staging
openai_gpt4_capacity = 5
openai_gpt35_capacity = 10
openai_embedding_capacity = 5

# Security - production-like for staging
enable_private_endpoints = true
enable_advanced_threat_protection = true
enable_azure_defender = false  # Optional for staging

# Compliance - full compliance for staging testing
data_retention_years = 7
enable_audit_logging = true
gdpr_compliance = true
soc2_compliance = true

# Performance - standard tier for staging
performance_tier = "standard"
enable_autoscaling = true
backup_retention_days = 30
geo_redundant_backup = true

# Feature flags
enable_blue_green_deployment = true
enable_canary_deployment = true
enable_feature_flags = true

# Monitoring
monitoring_email_receivers = [
  {
    name  = "staging-alerts"
    email = "staging-team@yourcompany.com"
  },
  {
    name  = "qa-team"
    email = "qa-team@yourcompany.com"
  }
]

# Trusted IP ranges (example - replace with your actual IPs)
trusted_ip_ranges = [
  "203.0.113.0/24",  # Office network
  "198.51.100.0/24", # VPN network
  "192.0.2.0/24"     # QA network
]
