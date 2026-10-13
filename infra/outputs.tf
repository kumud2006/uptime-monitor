output "resource_group" {
  value = azurerm_resource_group.main.name
}

output "function_app_name" {
  value = azurerm_function_app_flex_consumption.main.name
}

output "function_app_url" {
  value = "https://${azurerm_function_app_flex_consumption.main.default_hostname}"
}

output "static_web_app_name" {
  value = azurerm_static_web_app.main.name
}

output "static_web_app_url" {
  value = "https://${azurerm_static_web_app.main.default_host_name}"
}

output "static_web_app_token" {
  value     = azurerm_static_web_app.main.api_key
  sensitive = true
}

output "cosmos_connection_string" {
  value     = azurerm_cosmosdb_account.main.primary_sql_connection_string
  sensitive = true
}

output "action_group_id" {
  value = azurerm_monitor_action_group.email.id
}