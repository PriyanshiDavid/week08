location             = "Australia East"
resource_group_name  = "koalatech-week08-rg"
acr_name             = "koalatechweek08acr30145"
storage_account_name = "koalatechweek08sa"
aks_cluster_name     = "koalatech-week08-aks"
aks_dns_prefix       = "koalatechweek08"
aks_node_count       = 3
environment          = "development"
tags = {
  Project   = "KoalaTech Course Platform"
  ManagedBy = "Terraform"
  Practical = "Week08"
}
