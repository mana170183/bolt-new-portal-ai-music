output "log_analytics_workspace_id" {
  description = "Log Analytics workspace ID"
  value       = azurerm_log_analytics_workspace.main.id
}

output "log_analytics_workspace_name" {
  description = "Log Analytics workspace name"
  value       = azurerm_log_analytics_workspace.main.name
}

output "application_insights_id" {
  description = "Application Insights ID"
  value       = azurerm_application_insights.main.id
}

output "application_insights_name" {
  description = "Application Insights name"
  value       = azurerm_application_insights.main.name
}

output "application_insights_instrumentation_key" {
  description = "Application Insights instrumentation key"
  value       = azurerm_application_insights.main.instrumentation_key
  sensitive   = true
}

output "application_insights_connection_string" {
  description = "Application Insights connection string"
  value       = azurerm_application_insights.main.connection_string
  sensitive   = true
}

output "action_group_id" {
  description = "Action group ID"
  value       = azurerm_monitor_action_group.main.id
}

output "dashboard_id" {
  description = "Dashboard ID"
  value       = azurerm_portal_dashboard.main.id
}

output "workbook_id" {
  description = "Workbook ID"
  value       = azurerm_application_insights_workbook.main.id
}

output "data_collection_rule_id" {
  description = "Data collection rule ID"
  value       = azurerm_monitor_data_collection_rule.main.id
}

output "metric_alerts" {
  description = "Created metric alerts"
  value = {
    cpu_usage     = azurerm_monitor_metric_alert.cpu_usage.id
    memory_usage  = azurerm_monitor_metric_alert.memory_usage.id
    response_time = azurerm_monitor_metric_alert.response_time.id
    error_rate    = azurerm_monitor_metric_alert.error_rate.id
  }
}

output "log_alerts" {
  description = "Created log alerts"
  value = {
    security_alert    = azurerm_monitor_scheduled_query_rules_alert_v2.security_alert.id
    performance_alert = azurerm_monitor_scheduled_query_rules_alert_v2.performance_alert.id
  }
}

output "monitoring_endpoints" {
  description = "Monitoring endpoints and URLs"
  value = {
    log_analytics_portal_url = "https://portal.azure.com/#@${var.subscription_id}/resource${azurerm_log_analytics_workspace.main.id}/overview"
    application_insights_portal_url = "https://portal.azure.com/#@${var.subscription_id}/resource${azurerm_application_insights.main.id}/overview"
    dashboard_url = "https://portal.azure.com/#@${var.subscription_id}/dashboard/arm${azurerm_portal_dashboard.main.id}"
    workbook_url = "https://portal.azure.com/#@${var.subscription_id}/resource${azurerm_application_insights_workbook.main.id}/overview"
  }
}

output "compliance_monitoring" {
  description = "Compliance monitoring configuration"
  value = {
    gdpr_monitoring_enabled = var.compliance_monitoring.enable_gdpr_monitoring
    soc2_monitoring_enabled = var.compliance_monitoring.enable_soc2_monitoring
    audit_logging_enabled = var.compliance_monitoring.enable_audit_logging
    audit_retention_days = var.compliance_monitoring.audit_retention_days
  }
}

output "estimated_monthly_cost_usd" {
  description = "Estimated monthly cost in USD"
  value = {
    log_analytics = {
      workspace = 0.0  # Pay per GB ingested
      data_ingestion = 50.0  # Estimated 10GB/month at $2.30/GB
      data_retention = var.retention_days > 31 ? ((var.retention_days - 31) * 0.10 * 10) : 0.0  # $0.10/GB/month after 31 days
    }
    application_insights = {
      base_cost = 0.0  # First 5GB free per month
      data_volume = 20.0  # Estimated additional data at $2.30/GB
    }
    alerts = {
      metric_alerts = 4 * 0.10  # $0.10 per metric alert per month
      log_alerts = 2 * 1.50     # $1.50 per log alert per month
    }
    dashboard = 0.0  # Included
    action_group = 0.0  # Free
    total = 50.0 + (var.retention_days > 31 ? ((var.retention_days - 31) * 0.10 * 10) : 0.0) + 20.0 + 3.40
  }
}
