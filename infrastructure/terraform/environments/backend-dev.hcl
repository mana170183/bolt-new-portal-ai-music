# Terraform Backend Configuration for Development Environment

resource_group_name  = "rg-terraform-state"
storage_account_name = "replace-with-your-storage-account"
container_name       = "tfstate"
key                  = "dev/portal-ai-music.tfstate"
