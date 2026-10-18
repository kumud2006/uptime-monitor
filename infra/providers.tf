terraform {
  required_version = ">= 1.6"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }

  backend "azurerm" {
    resource_group_name  = "rg-tfstate"
    storage_account_name = "tfstateuptime4821"
    container_name       = "tfstate"
    key                  = "uptime-monitor.tfstate"
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}