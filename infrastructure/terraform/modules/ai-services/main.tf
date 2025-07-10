# Azure AI Services Module for AI Music Portal
# OpenAI, Cognitive Services, Machine Learning, and Custom Neural Voice

data "azurerm_client_config" "current" {}

# Cognitive Services Multi-Service Account
resource "azurerm_cognitive_account" "multi_service" {
  name                = var.cognitive_services_name
  location            = var.location
  resource_group_name = var.resource_group_name
  kind                = "CognitiveServices"
  sku_name            = var.cognitive_services_sku

  # Network access control
  public_network_access_enabled = var.public_access_enabled
  custom_question_answering_search_service_id = var.search_service_id

  # Identity
  identity {
    type = "SystemAssigned"
  }

  tags = var.tags
}

# Azure OpenAI Service
resource "azurerm_cognitive_account" "openai" {
  name                = var.openai_name
  location            = var.openai_location
  resource_group_name = var.resource_group_name
  kind                = "OpenAI"
  sku_name            = "S0"

  # Network access control
  public_network_access_enabled = var.public_access_enabled

  # Identity
  identity {
    type = "SystemAssigned"
  }

  tags = var.tags
}

# OpenAI Deployments
resource "azurerm_cognitive_deployment" "gpt4" {
  name                 = "gpt-4"
  cognitive_account_id = azurerm_cognitive_account.openai.id

  model {
    format  = "OpenAI"
    name    = "gpt-4"
    version = "0613"
  }

  scale {
    type     = "Standard"
    capacity = var.gpt4_capacity
  }
}

resource "azurerm_cognitive_deployment" "gpt35_turbo" {
  name                 = "gpt-35-turbo"
  cognitive_account_id = azurerm_cognitive_account.openai.id

  model {
    format  = "OpenAI"
    name    = "gpt-35-turbo"
    version = "0613"
  }

  scale {
    type     = "Standard"
    capacity = var.gpt35_capacity
  }
}

resource "azurerm_cognitive_deployment" "text_embedding" {
  name                 = "text-embedding-ada-002"
  cognitive_account_id = azurerm_cognitive_account.openai.id

  model {
    format  = "OpenAI"
    name    = "text-embedding-ada-002"
    version = "2"
  }

  scale {
    type     = "Standard"
    capacity = var.embedding_capacity
  }
}

# Speech Service for Neural Voice
resource "azurerm_cognitive_account" "speech" {
  name                = var.speech_service_name
  location            = var.location
  resource_group_name = var.resource_group_name
  kind                = "SpeechServices"
  sku_name            = var.speech_sku

  # Network access control
  public_network_access_enabled = var.public_access_enabled

  # Identity
  identity {
    type = "SystemAssigned"
  }

  tags = var.tags
}

# Machine Learning Workspace
resource "azurerm_machine_learning_workspace" "main" {
  name                = var.ml_workspace_name
  location            = var.location
  resource_group_name = var.resource_group_name
  application_insights_id = var.application_insights_id
  key_vault_id           = var.key_vault_id
  storage_account_id     = var.storage_account_id
  container_registry_id  = var.container_registry_id

  # Network security
  public_network_access_enabled = var.public_access_enabled
  
  # Identity
  identity {
    type = "SystemAssigned"
  }

  # Encryption
  encryption {
    key_vault_key_id   = var.cmk_key_id
    key_id             = var.cmk_key_id
    user_assigned_identity_id = var.user_assigned_identity_id
  }

  tags = var.tags
}

# Search Service for AI capabilities
resource "azurerm_search_service" "main" {
  name                = var.search_service_name
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = var.search_sku
  replica_count       = var.search_replica_count
  partition_count     = var.search_partition_count

  # Network security
  public_network_access_enabled = var.public_access_enabled
  allowed_ips                   = var.allowed_ip_ranges

  # Identity
  identity {
    type = "SystemAssigned"
  }

  tags = var.tags
}

# Private endpoints
resource "azurerm_private_endpoint" "cognitive_services" {
  count               = var.enable_private_endpoint ? 1 : 0
  name                = "${var.cognitive_services_name}-pe"
  location            = var.location
  resource_group_name = var.resource_group_name
  subnet_id           = var.private_endpoint_subnet_id

  private_service_connection {
    name                           = "${var.cognitive_services_name}-psc"
    private_connection_resource_id = azurerm_cognitive_account.multi_service.id
    subresource_names              = ["account"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name                 = "default"
    private_dns_zone_ids = var.private_dns_zone_ids
  }

  tags = var.tags
}

resource "azurerm_private_endpoint" "openai" {
  count               = var.enable_private_endpoint ? 1 : 0
  name                = "${var.openai_name}-pe"
  location            = var.location
  resource_group_name = var.resource_group_name
  subnet_id           = var.private_endpoint_subnet_id

  private_service_connection {
    name                           = "${var.openai_name}-psc"
    private_connection_resource_id = azurerm_cognitive_account.openai.id
    subresource_names              = ["account"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name                 = "default"
    private_dns_zone_ids = var.private_dns_zone_ids
  }

  tags = var.tags
}

resource "azurerm_private_endpoint" "ml_workspace" {
  count               = var.enable_private_endpoint ? 1 : 0
  name                = "${var.ml_workspace_name}-pe"
  location            = var.location
  resource_group_name = var.resource_group_name
  subnet_id           = var.private_endpoint_subnet_id

  private_service_connection {
    name                           = "${var.ml_workspace_name}-psc"
    private_connection_resource_id = azurerm_machine_learning_workspace.main.id
    subresource_names              = ["amlworkspace"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name                 = "default"
    private_dns_zone_ids = var.private_dns_zone_ids
  }

  tags = var.tags
}

# Key Vault secrets for API keys
resource "azurerm_key_vault_secret" "cognitive_services_key" {
  name         = "cognitive-services-key"
  value        = azurerm_cognitive_account.multi_service.primary_access_key
  key_vault_id = var.key_vault_id
  tags         = var.tags
}

resource "azurerm_key_vault_secret" "openai_key" {
  name         = "openai-key"
  value        = azurerm_cognitive_account.openai.primary_access_key
  key_vault_id = var.key_vault_id
  tags         = var.tags
}

resource "azurerm_key_vault_secret" "speech_key" {
  name         = "speech-key"
  value        = azurerm_cognitive_account.speech.primary_access_key
  key_vault_id = var.key_vault_id
  tags         = var.tags
}

resource "azurerm_key_vault_secret" "search_key" {
  name         = "search-key"
  value        = azurerm_search_service.main.primary_key
  key_vault_id = var.key_vault_id
  tags         = var.tags
}

# Diagnostic settings
resource "azurerm_monitor_diagnostic_setting" "cognitive_services" {
  name               = "${var.cognitive_services_name}-diagnostics"
  target_resource_id = azurerm_cognitive_account.multi_service.id
  log_analytics_workspace_id = var.log_analytics_workspace_id

  enabled_log {
    category = "Audit"
  }

  enabled_log {
    category = "RequestResponse"
  }

  metric {
    category = "AllMetrics"
    enabled  = true
  }
}

resource "azurerm_monitor_diagnostic_setting" "openai" {
  name               = "${var.openai_name}-diagnostics"
  target_resource_id = azurerm_cognitive_account.openai.id
  log_analytics_workspace_id = var.log_analytics_workspace_id

  enabled_log {
    category = "Audit"
  }

  enabled_log {
    category = "RequestResponse"
  }

  metric {
    category = "AllMetrics"
    enabled  = true
  }
}

# RBAC assignments
resource "azurerm_role_assignment" "cognitive_services_user" {
  scope                = azurerm_cognitive_account.multi_service.id
  role_definition_name = "Cognitive Services User"
  principal_id         = var.application_principal_id
}

resource "azurerm_role_assignment" "openai_user" {
  scope                = azurerm_cognitive_account.openai.id
  role_definition_name = "Cognitive Services OpenAI User"
  principal_id         = var.application_principal_id
}
