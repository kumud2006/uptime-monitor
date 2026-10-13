variable "subscription_id" {
  type        = string
  description = "Azure subscription ID"
}

variable "alert_email" {
  type        = string
  description = "Email that receives Azure Monitor alerts"
}

variable "project" {
  type    = string
  default = "uptimemon"
}

variable "location" {
  type    = string
  default = "centralindia"
}

# Static Web Apps (free) only exists in a few regions
variable "swa_location" {
  type    = string
  default = "eastasia"
}

variable "cosmos_location" {
  type    = string
  default = "koreacentral"
}