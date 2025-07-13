# Terraform Backend Configuration for Staging Environment

resource_group_name  = "rg-terraform-state"
storage_account_name = "replace-with-your-storage-account"
container_name       = "tfstate"
key                  = "staging/portal-ai-music.tfstate"
