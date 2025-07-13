# Terraform Backend Configuration for Production Environment

resource_group_name  = "rg-terraform-state"
storage_account_name = "replace-with-your-storage-account"
container_name       = "tfstate"
key                  = "prod/portal-ai-music.tfstate"
