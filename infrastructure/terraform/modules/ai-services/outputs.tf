output "cognitive_services_id" {
  description = "Cognitive Services account ID"
  value       = azurerm_cognitive_account.multi_service.id
}

output "cognitive_services_endpoint" {
  description = "Cognitive Services endpoint"
  value       = azurerm_cognitive_account.multi_service.endpoint
}

output "cognitive_services_key" {
  description = "Cognitive Services primary access key"
  value       = azurerm_cognitive_account.multi_service.primary_access_key
  sensitive   = true
}

output "openai_id" {
  description = "OpenAI service ID"
  value       = azurerm_cognitive_account.openai.id
}

output "openai_endpoint" {
  description = "OpenAI service endpoint"
  value       = azurerm_cognitive_account.openai.endpoint
}

output "openai_key" {
  description = "OpenAI service primary access key"
  value       = azurerm_cognitive_account.openai.primary_access_key
  sensitive   = true
}

output "speech_service_id" {
  description = "Speech service ID"
  value       = azurerm_cognitive_account.speech.id
}

output "speech_service_endpoint" {
  description = "Speech service endpoint"
  value       = azurerm_cognitive_account.speech.endpoint
}

output "speech_service_key" {
  description = "Speech service primary access key"
  value       = azurerm_cognitive_account.speech.primary_access_key
  sensitive   = true
}

output "ml_workspace_id" {
  description = "ML workspace ID"
  value       = azurerm_machine_learning_workspace.main.id
}

output "ml_workspace_name" {
  description = "ML workspace name"
  value       = azurerm_machine_learning_workspace.main.name
}

output "search_service_id" {
  description = "Search service ID"
  value       = azurerm_search_service.main.id
}

output "search_service_name" {
  description = "Search service name"
  value       = azurerm_search_service.main.name
}

output "search_service_url" {
  description = "Search service URL"
  value       = "https://${azurerm_search_service.main.name}.search.windows.net"
}

output "search_service_key" {
  description = "Search service primary key"
  value       = azurerm_search_service.main.primary_key
  sensitive   = true
}

output "openai_deployments" {
  description = "OpenAI model deployments"
  value = {
    gpt4 = {
      name = azurerm_cognitive_deployment.gpt4.name
      model = azurerm_cognitive_deployment.gpt4.model[0].name
      version = azurerm_cognitive_deployment.gpt4.model[0].version
    }
    gpt35_turbo = {
      name = azurerm_cognitive_deployment.gpt35_turbo.name
      model = azurerm_cognitive_deployment.gpt35_turbo.model[0].name
      version = azurerm_cognitive_deployment.gpt35_turbo.model[0].version
    }
    text_embedding = {
      name = azurerm_cognitive_deployment.text_embedding.name
      model = azurerm_cognitive_deployment.text_embedding.model[0].name
      version = azurerm_cognitive_deployment.text_embedding.model[0].version
    }
  }
}

output "estimated_monthly_cost_usd" {
  description = "Estimated monthly cost in USD"
  value = {
    cognitive_services = var.cognitive_services_sku == "S0" ? 243.62 : 50.0
    openai = {
      gpt4 = var.gpt4_capacity * 30.0 * 24 * 0.06  # $0.06 per 1K tokens
      gpt35_turbo = var.gpt35_capacity * 30.0 * 24 * 0.002  # $0.002 per 1K tokens
      embedding = var.embedding_capacity * 30.0 * 24 * 0.0001  # $0.0001 per 1K tokens
    }
    speech = var.speech_sku == "S0" ? 300.0 : 15.0
    search = var.search_sku == "standard" ? 250.0 : (var.search_sku == "basic" ? 36.0 : 0.0)
    ml_workspace = 0.0  # Pay per compute usage
    private_endpoints = var.enable_private_endpoint ? (3 * 7.30) : 0.0
    total = (var.cognitive_services_sku == "S0" ? 243.62 : 50.0) +
            (var.gpt4_capacity * 30.0 * 24 * 0.06) +
            (var.gpt35_capacity * 30.0 * 24 * 0.002) +
            (var.embedding_capacity * 30.0 * 24 * 0.0001) +
            (var.speech_sku == "S0" ? 300.0 : 15.0) +
            (var.search_sku == "standard" ? 250.0 : (var.search_sku == "basic" ? 36.0 : 0.0)) +
            (var.enable_private_endpoint ? (3 * 7.30) : 0.0)
  }
}
