# NGINX ingress splits traffic by canary weight and exports per-service metrics
resource "helm_release" "ingress_nginx" {
  name             = "ingress-nginx"
  repository       = "https://kubernetes.github.io/ingress-nginx"
  chart            = "ingress-nginx"
  namespace        = "ingress-nginx"
  create_namespace = true

  set = [
    {
      # Health probe path required for the Azure load balancer
      name  = "controller.service.annotations.service\\.beta\\.kubernetes\\.io/azure-load-balancer-health-probe-request-path"
      value = "/healthz"
    },
  ]

  depends_on = [azurerm_kubernetes_cluster.aks]
}

# The controller and CRDs for Rollout and AnalysisTemplate
resource "helm_release" "argo_rollouts" {
  name             = "argo-rollouts"
  repository       = "https://argoproj.github.io/argo-helm"
  chart            = "argo-rollouts"
  namespace        = "argo-rollouts"
  create_namespace = true

  depends_on = [azurerm_kubernetes_cluster.aks]
}
