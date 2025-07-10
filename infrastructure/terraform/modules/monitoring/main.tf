# Azure Monitoring Module for AI Music Portal
# Application Insights, Log Analytics, Dashboards, and Alerts

# Log Analytics Workspace
resource "azurerm_log_analytics_workspace" "main" {
  name                = var.log_analytics_name
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = var.log_analytics_sku
  retention_in_days   = var.retention_days

  tags = var.tags
}

# Application Insights
resource "azurerm_application_insights" "main" {
  name                = var.application_insights_name
  location            = var.location
  resource_group_name = var.resource_group_name
  workspace_id        = azurerm_log_analytics_workspace.main.id
  application_type    = "web"
  retention_in_days   = var.retention_days
  sampling_percentage = var.sampling_percentage

  tags = var.tags
}

# Action Group for alerts
resource "azurerm_monitor_action_group" "main" {
  name                = var.action_group_name
  resource_group_name = var.resource_group_name
  short_name          = var.action_group_short_name

  # Email notifications
  dynamic "email_receiver" {
    for_each = var.email_receivers
    content {
      name          = email_receiver.value.name
      email_address = email_receiver.value.email
    }
  }

  # SMS notifications
  dynamic "sms_receiver" {
    for_each = var.sms_receivers
    content {
      name         = sms_receiver.value.name
      country_code = sms_receiver.value.country_code
      phone_number = sms_receiver.value.phone_number
    }
  }

  # Webhook notifications
  dynamic "webhook_receiver" {
    for_each = var.webhook_receivers
    content {
      name        = webhook_receiver.value.name
      service_uri = webhook_receiver.value.uri
    }
  }

  # Azure Function notifications
  dynamic "azure_function_receiver" {
    for_each = var.function_receivers
    content {
      name                     = azure_function_receiver.value.name
      function_app_resource_id = azure_function_receiver.value.function_app_id
      function_name            = azure_function_receiver.value.function_name
      http_trigger_url         = azure_function_receiver.value.trigger_url
    }
  }

  tags = var.tags
}

# Metric Alerts
resource "azurerm_monitor_metric_alert" "cpu_usage" {
  name                = "${var.application_insights_name}-cpu-usage"
  resource_group_name = var.resource_group_name
  scopes              = var.monitored_resource_ids
  description         = "Alert when CPU usage exceeds threshold"
  severity            = 2

  criteria {
    metric_namespace = "Microsoft.ContainerInstance/containerGroups"
    metric_name      = "CpuUsage"
    aggregation      = "Average"
    operator         = "GreaterThan"
    threshold        = var.cpu_threshold

    dimension {
      name     = "containerName"
      operator = "Include"
      values   = ["*"]
    }
  }

  action {
    action_group_id = azurerm_monitor_action_group.main.id
  }

  frequency   = "PT1M"
  window_size = "PT5M"

  tags = var.tags
}

resource "azurerm_monitor_metric_alert" "memory_usage" {
  name                = "${var.application_insights_name}-memory-usage"
  resource_group_name = var.resource_group_name
  scopes              = var.monitored_resource_ids
  description         = "Alert when memory usage exceeds threshold"
  severity            = 2

  criteria {
    metric_namespace = "Microsoft.ContainerInstance/containerGroups"
    metric_name      = "MemoryUsage"
    aggregation      = "Average"
    operator         = "GreaterThan"
    threshold        = var.memory_threshold

    dimension {
      name     = "containerName"
      operator = "Include"
      values   = ["*"]
    }
  }

  action {
    action_group_id = azurerm_monitor_action_group.main.id
  }

  frequency   = "PT1M"
  window_size = "PT5M"

  tags = var.tags
}

resource "azurerm_monitor_metric_alert" "response_time" {
  name                = "${var.application_insights_name}-response-time"
  resource_group_name = var.resource_group_name
  scopes              = [azurerm_application_insights.main.id]
  description         = "Alert when response time exceeds threshold"
  severity            = 1

  criteria {
    metric_namespace = "Microsoft.Insights/components"
    metric_name      = "requests/duration"
    aggregation      = "Average"
    operator         = "GreaterThan"
    threshold        = var.response_time_threshold
  }

  action {
    action_group_id = azurerm_monitor_action_group.main.id
  }

  frequency   = "PT1M"
  window_size = "PT5M"

  tags = var.tags
}

resource "azurerm_monitor_metric_alert" "error_rate" {
  name                = "${var.application_insights_name}-error-rate"
  resource_group_name = var.resource_group_name
  scopes              = [azurerm_application_insights.main.id]
  description         = "Alert when error rate exceeds threshold"
  severity            = 0

  criteria {
    metric_namespace = "Microsoft.Insights/components"
    metric_name      = "requests/failed"
    aggregation      = "Count"
    operator         = "GreaterThan"
    threshold        = var.error_rate_threshold
  }

  action {
    action_group_id = azurerm_monitor_action_group.main.id
  }

  frequency   = "PT1M"
  window_size = "PT5M"

  tags = var.tags
}

# Log Alerts
resource "azurerm_monitor_scheduled_query_rules_alert_v2" "security_alert" {
  name                = "${var.application_insights_name}-security-alert"
  resource_group_name = var.resource_group_name
  location            = var.location
  evaluation_frequency = "PT5M"
  window_duration     = "PT5M"
  scopes              = [azurerm_log_analytics_workspace.main.id]
  severity            = 0
  description         = "Alert on security events"

  criteria {
    query = <<-QUERY
      SecurityEvent
      | where EventID in (4625, 4648, 4719, 4765)
      | summarize count() by bin(TimeGenerated, 5m)
      | where count_ > 10
    QUERY

    time_aggregation_method = "Count"
    threshold               = 1
    operator                = "GreaterThan"

    failing_periods {
      minimum_failing_periods_to_trigger_alert = 1
      number_of_evaluation_periods             = 1
    }
  }

  action {
    action_groups = [azurerm_monitor_action_group.main.id]
  }

  tags = var.tags
}

resource "azurerm_monitor_scheduled_query_rules_alert_v2" "performance_alert" {
  name                = "${var.application_insights_name}-performance-alert"
  resource_group_name = var.resource_group_name
  location            = var.location
  evaluation_frequency = "PT5M"
  window_duration     = "PT15M"
  scopes              = [azurerm_application_insights.main.id]
  severity            = 2
  description         = "Alert on performance degradation"

  criteria {
    query = <<-QUERY
      requests
      | where timestamp > ago(15m)
      | summarize avg(duration) by bin(timestamp, 5m)
      | where avg_duration > ${var.response_time_threshold}
    QUERY

    time_aggregation_method = "Count"
    threshold               = 1
    operator                = "GreaterThan"

    failing_periods {
      minimum_failing_periods_to_trigger_alert = 2
      number_of_evaluation_periods             = 3
    }
  }

  action {
    action_groups = [azurerm_monitor_action_group.main.id]
  }

  tags = var.tags
}

# Dashboard
resource "azurerm_portal_dashboard" "main" {
  name                = "${var.application_insights_name}-dashboard"
  resource_group_name = var.resource_group_name
  location            = var.location
  tags                = var.tags

  dashboard_properties = templatefile("${path.module}/dashboard.json", {
    subscription_id          = var.subscription_id
    resource_group_name      = var.resource_group_name
    application_insights_name = azurerm_application_insights.main.name
    log_analytics_name       = azurerm_log_analytics_workspace.main.name
  })
}

# Data Collection Rules
resource "azurerm_monitor_data_collection_rule" "main" {
  name                = "${var.log_analytics_name}-dcr"
  resource_group_name = var.resource_group_name
  location            = var.location

  destinations {
    log_analytics {
      workspace_resource_id = azurerm_log_analytics_workspace.main.id
      name                  = "destination-log"
    }
  }

  data_flow {
    streams      = ["Microsoft-Event"]
    destinations = ["destination-log"]
  }

  data_sources {
    windows_event_log {
      streams = ["Microsoft-Event"]
      x_path_queries = [
        "Security!*[System[(EventID=4625 or EventID=4648 or EventID=4719 or EventID=4765)]]",
        "Application!*[System[(Level=1 or Level=2 or Level=3)]]",
        "System!*[System[(Level=1 or Level=2 or Level=3)]]"
      ]
      name = "eventLogsDataSource"
    }

    performance_counter {
      streams                       = ["Microsoft-Perf"]
      sampling_frequency_in_seconds = 60
      counter_specifiers = [
        "\\Processor(_Total)\\% Processor Time",
        "\\Memory\\Available Bytes",
        "\\Network Interface(*)\\Bytes Total/sec"
      ]
      name = "perfCounterDataSource"
    }

    iis_log {
      streams         = ["Microsoft-W3CIISLog"]
      log_directories = ["C:\\inetpub\\logs\\LogFiles\\W3SVC1"]
      name            = "iisLogsDataSource"
    }
  }

  tags = var.tags
}

# Workbook for custom analytics
resource "azurerm_application_insights_workbook" "main" {
  name                = "${var.application_insights_name}-workbook"
  resource_group_name = var.resource_group_name
  location            = var.location
  display_name        = "AI Music Portal Analytics"
  
  data_json = jsonencode({
    version = "Notebook/1.0"
    items = [
      {
        type = 1
        content = {
          json = "## AI Music Portal - Performance Analytics\n\nThis workbook provides comprehensive monitoring for the AI Music Portal application."
        }
      },
      {
        type = 3
        content = {
          version = "KqlItem/1.0"
          query = "requests | summarize count() by bin(timestamp, 1h) | render timechart"
          size = 0
          title = "Request Volume"
          timeContext = {
            durationMs = 3600000
          }
        }
      },
      {
        type = 3
        content = {
          version = "KqlItem/1.0"
          query = "requests | summarize avg(duration) by bin(timestamp, 1h) | render timechart"
          size = 0
          title = "Average Response Time"
          timeContext = {
            durationMs = 3600000
          }
        }
      }
    ]
  })

  tags = var.tags
}

# Store secrets in Key Vault
resource "azurerm_key_vault_secret" "application_insights_key" {
  name         = "application-insights-instrumentation-key"
  value        = azurerm_application_insights.main.instrumentation_key
  key_vault_id = var.key_vault_id
  tags         = var.tags
}

resource "azurerm_key_vault_secret" "application_insights_connection_string" {
  name         = "application-insights-connection-string"
  value        = azurerm_application_insights.main.connection_string
  key_vault_id = var.key_vault_id
  tags         = var.tags
}
