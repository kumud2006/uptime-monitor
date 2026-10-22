resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

locals {
  suffix = random_string.suffix.result
  tags = {
    project    = "uptime-monitor"
    managed_by = "terraform"
    course     = "CCD"
  }
}

resource "azurerm_resource_group" "main" {
  name     = "rg-${var.project}"
  location = var.location
  tags     = local.tags
}

# ---------- Storage (function code package) ----------
resource "azurerm_storage_account" "main" {
  name                            = "st${var.project}${local.suffix}"
  resource_group_name             = azurerm_resource_group.main.name
  location                        = azurerm_resource_group.main.location
  account_tier                    = "Standard"
  account_replication_type        = "LRS"
  min_tls_version                 = "TLS1_2"
  allow_nested_items_to_be_public = false
  tags                            = local.tags
}

resource "azurerm_storage_container" "deploy" {
  name                  = "app-package"
  storage_account_id    = azurerm_storage_account.main.id
  container_access_type = "private"
}

# ---------- Monitoring ----------
resource "azurerm_log_analytics_workspace" "main" {
  name                = "log-${var.project}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = local.tags
}

resource "azurerm_application_insights" "main" {
  name                = "appi-${var.project}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  workspace_id        = azurerm_log_analytics_workspace.main.id
  application_type    = "web"
  tags                = local.tags
}

resource "azurerm_monitor_action_group" "email" {
  name                = "ag-${var.project}-email"
  resource_group_name = azurerm_resource_group.main.name
  short_name          = "uptimealert"

  email_receiver {
    name                    = "team"
    email_address           = var.alert_email
    use_common_alert_schema = true
  }
}

resource "azurerm_monitor_scheduled_query_rules_alert_v2" "func_errors" {
  name                 = "alert-${var.project}-func-exceptions"
  resource_group_name  = azurerm_resource_group.main.name
  location             = azurerm_resource_group.main.location
  description          = "Fires when the Function App logs any exception in 5 minutes"
  evaluation_frequency = "PT5M"
  window_duration      = "PT5M"
  scopes               = [azurerm_application_insights.main.id]
  severity             = 2

  criteria {
    query                   = <<-QUERY
      exceptions
      | where timestamp > ago(5m)
    QUERY
    time_aggregation_method = "Count"
    threshold               = 0
    operator                = "GreaterThan"
  }

  action {
    action_groups = [azurerm_monitor_action_group.email.id]
  }
}

# ---------- Database (Cosmos DB free tier) ----------
resource "azurerm_cosmosdb_account" "main" {
  name                = "cosmos-${var.project}-${local.suffix}"
  resource_group_name = azurerm_resource_group.main.name
  location            = var.cosmos_location
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"
  free_tier_enabled   = true
  tags                = local.tags

  consistency_policy {
    consistency_level = "Session"
  }

  geo_location {
    location          = var.cosmos_location
    failover_priority = 0
  }
}

resource "azurerm_cosmosdb_sql_database" "main" {
  name                = "uptime"
  resource_group_name = azurerm_resource_group.main.name
  account_name        = azurerm_cosmosdb_account.main.name
  throughput          = 400
}

resource "azurerm_cosmosdb_sql_container" "containers" {
  for_each = {
    targets   = "/id"
    checks    = "/target_id"
    incidents = "/target_id"
  }

  name                = each.key
  resource_group_name = azurerm_resource_group.main.name
  account_name        = azurerm_cosmosdb_account.main.name
  database_name       = azurerm_cosmosdb_sql_database.main.name
  partition_key_paths = [each.value]
}

# ---------- Function App (Flex Consumption) ----------
resource "azurerm_service_plan" "func" {
  name                = "asp-${var.project}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  os_type             = "Linux"
  sku_name            = "FC1"
  tags                = local.tags
}

resource "azurerm_function_app_flex_consumption" "main" {
  name                = "func-${var.project}-${local.suffix}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  service_plan_id     = azurerm_service_plan.func.id
  tags                = local.tags

  storage_container_type      = "blobContainer"
  storage_container_endpoint  = "${azurerm_storage_account.main.primary_blob_endpoint}${azurerm_storage_container.deploy.name}"
  storage_authentication_type = "StorageAccountConnectionString"
  storage_access_key          = azurerm_storage_account.main.primary_access_key

  runtime_name           = "python"
  runtime_version        = "3.11"
  maximum_instance_count = 40
  instance_memory_in_mb  = 512

  site_config {
    application_insights_connection_string = azurerm_application_insights.main.connection_string

    cors {
      allowed_origins = [
        "https://${azurerm_static_web_app.main.default_host_name}",
        "http://localhost:5173",
      ]
    }
  }

  app_settings = {
    AzureWebJobsStorage = azurerm_storage_account.main.primary_connection_string
    DB_CONNECTION       = azurerm_cosmosdb_account.main.primary_sql_connection_string
    DB_NAME             = azurerm_cosmosdb_sql_database.main.name
    ALERT_EMAIL         = var.alert_email
    SMTP_HOST           = "smtp.gmail.com"
    SMTP_PORT           = "587"
    SMTP_USER           = var.smtp_user
    SMTP_PASSWORD       = var.smtp_password
  }
}

# ---------- Dashboard hosting ----------
resource "azurerm_static_web_app" "main" {
  name                = "swa-${var.project}"
  resource_group_name = azurerm_resource_group.main.name
  location            = var.swa_location
  sku_tier            = "Free"
  sku_size            = "Free"
  tags                = local.tags
}