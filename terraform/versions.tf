terraform {
  required_version = ">= 1.7.0"

  # Remote state so the GitHub Actions pipeline and local runs share one state.
  # The storage details are passed in with -backend-config at terraform init.
  backend "azurerm" {}

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

provider "azurerm" {
  features {}
}