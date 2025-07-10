# Portal AI Music - Terraform Infrastructure

Enterprise-grade, cost-optimized Azure infrastructure for Portal AI Music.

## Quick Start

```bash
# Deploy ultra cost-optimized environment ($185-278/month)
cd infrastructure/terraform
terraform init
terraform apply -var-file=environments/dev-optimized.tfvars
```

## Environment Options

| Environment | Cost/Month | Use Case |
|-------------|------------|----------|
| dev-optimized | $185-278 | Individual development |
| dev | $400-600 | Team development |
| staging | $800-1200 | Pre-production |
| prod | $2000-5000 | Production |

## Key Features

- **Cost Optimized**: 50-70% savings with dev-optimized configuration
- **Auto-Shutdown**: Container Apps scale to zero when inactive
- **Enterprise Security**: Key Vault, private endpoints, RBAC
- **Scalable**: Easy progression from dev to production
- **Monitored**: Built-in cost alerts and performance monitoring

## Architecture

- Container Apps (serverless backend)
- Azure SQL Database (configurable tiers)
- Redis Cache (cost-optimized)
- Storage Account (music files)
- Cognitive Services (AI/ML)
- Key Vault (secrets)
- Monitoring (Application Insights)

See [Cost Optimization Guide](../../docs/DEV-COST-OPTIMIZATION.md) for detailed analysis.
