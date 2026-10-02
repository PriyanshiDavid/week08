# Week 08 – Continuous Deployment with GitHub Actions and Kubernetes

> **10.3HD feature:** metrics-driven canary releases with automated rollback for `course-service`. See [section 13](#13-progressive-delivery-with-automated-rollback-103hd).


In Week 07, we implemented a Continuous Integration (CI) pipeline using GitHub Actions. The pipeline automatically tested the backend services, built Docker images, and pushed the successfully built images to Azure Container Registry (ACR).

In Week 08, we extended this workflow to implement Continuous Delivery: automatic deployment to **staging**, followed by automated smoke tests, with production promoted manually.

In Task 9.3C, this is extended further to full **Continuous Deployment (CD)**: once the staging smoke test passes, the same tested image is automatically promoted to **production** as well — no manual step is required.

The same Docker images that are tested in staging are deployed to production. The application is **not rebuilt** during production deployment.

---

## 1. Continuous Deployment Workflow

The pipeline consists of four GitHub Actions workflows:

![](./workflow.png)

All four workflows run automatically, chained via `workflow_run`:

```
push to main
  -> 01 - CI (test, build, push images)
  -> 02 - Deploy to Staging
  -> 03 - Test Staging (smoke test)
  -> 04 - Deploy to Production   (NEW: auto-triggered on staging test success)
```

`04-deploy-production.yml` still accepts a manual `workflow_dispatch` with an `image_tag` input as a fallback, so a specific previously-tested SHA can be re-deployed on demand. But the default path is fully automatic: merging a pull request into `main` is enough to carry a change all the way to production.

---

# 2. Prepare the Infrastructure

Create the Terraform infrastructure files using the same approach demonstrated in **Week 06**.

The infrastructure should provide the Azure resources required by the application, including the Kubernetes infrastructure, Azure Container Registry, and Azure Storage configuration used by the application.

### Important AKS Change

When creating the Kubernetes infrastructure, update the AKS node count to:

```hcl
node_count = 3
```

Three nodes are required for this practical because both the staging and production environments run persistent PostgreSQL database workloads.

After running Terraform, verify that the AKS cluster contains three nodes:

```bash
kubectl get nodes
```

---

# 4. Fork the Repository

Fork the provided Week 08 repository into your own GitHub account.

Clone your fork:

```bash
git clone <YOUR-FORK-URL>
```

Move into the project:

```bash
cd week08
```

Ensure that your remote points to your fork:

```bash
git remote -v
```

---

# 5. Create Azure Service Principal

GitHub Actions requires permission to interact with Azure.

Create a Service Principal following the same process introduced previously.

The Service Principal must have sufficient permissions to:

* authenticate with Azure;
* push Docker images to Azure Container Registry;
* access the AKS cluster;
* deploy Kubernetes workloads.

Store the Service Principal credentials as a GitHub Repository Secret named:

```text
AZURE_CREDENTIALS
```

The value must use the following structure:

```json
{
  "clientId": "YOUR_CLIENT_ID",
  "clientSecret": "YOUR_CLIENT_SECRET",
  "subscriptionId": "YOUR_SUBSCRIPTION_ID",
  "tenantId": "YOUR_TENANT_ID"
}
```

Do not commit these credentials to the repository.

---

# 6. Configure GitHub Repository Variables

Go to:

```text
GitHub Repository
→ Settings
→ Secrets and variables
→ Actions
→ Variables
```

Create the following **Repository Variables**.

### ACR_NAME

The name of your Azure Container Registry.

---

### ACR_LOGIN_SERVER

The complete ACR login server.

---

### AKS_RESOURCE_GROUP

The Resource Group containing your AKS cluster.

---

### AKS_CLUSTER_NAME

The name of your AKS cluster.

---

# 7. Repository Secret

Under:

```text
Settings
→ Secrets and variables
→ Actions
→ Secrets
```

create:

```text
AZURE_CREDENTIALS
```

This contains the Service Principal authentication JSON.

---

# 8. Create the Staging GitHub Environment

Go to:

```text
GitHub Repository
→ Settings
→ Environments
→ New environment
```

Create:

```text
staging
```

Add the following **Environment Secrets**:

```text
POSTGRES_USER = postgres
POSTGRES_PASSWORD = postgres
JWT_SECRET_KEY = koalatech-local-development-secret
DEFAULT_ADMIN_USERNAME = admin
DEFAULT_ADMIN_EMAIL = admin@koalatech.edu.au
DEFAULT_ADMIN_PASSWORD = AdminPassword123!
AZURE_STORAGE_CONNECTION_STRING = <YOUR_STORAGE_ACCOUNT_CONNECTION_STRING>
```
---

# 9. Create the Production GitHub Environment

Create another environment:

```text
production
```

Add the same Environment Secret names:

```text
POSTGRES_USER = postgres
POSTGRES_PASSWORD = postgres
JWT_SECRET_KEY = koalatech-local-development-secret
DEFAULT_ADMIN_USERNAME = admin
DEFAULT_ADMIN_EMAIL = admin@koalatech.edu.au
DEFAULT_ADMIN_PASSWORD = AdminPassword123!
AZURE_STORAGE_CONNECTION_STRING = <YOUR_STORAGE_ACCOUNT_CONNECTION_STRING>
```

Staging and production therefore have independent environment configuration.

---

# 10. GitHub Configuration Summary

The final GitHub configuration should be:

| Type                          | Name                              |
| ----------------------------- | --------------------------------- |
| Repository Secret             | `AZURE_CREDENTIALS`               |
| Repository Variable           | `ACR_NAME`                        |
| Repository Variable           | `ACR_LOGIN_SERVER`                |
| Repository Variable           | `AKS_RESOURCE_GROUP`              |
| Repository Variable           | `AKS_CLUSTER_NAME`                |
| Staging Environment Secret    | `POSTGRES_USER`                   |
| Staging Environment Secret    | `POSTGRES_PASSWORD`               |
| Staging Environment Secret    | `JWT_SECRET_KEY`                  |
| Staging Environment Secret    | `DEFAULT_ADMIN_USERNAME`          |
| Staging Environment Secret    | `DEFAULT_ADMIN_EMAIL`             |
| Staging Environment Secret    | `DEFAULT_ADMIN_PASSWORD`          |
| Staging Environment Secret    | `AZURE_STORAGE_CONNECTION_STRING` |
| Production Environment Secret | `POSTGRES_USER`                   |
| Production Environment Secret | `POSTGRES_PASSWORD`               |
| Production Environment Secret | `JWT_SECRET_KEY`                  |
| Production Environment Secret | `DEFAULT_ADMIN_USERNAME`          |
| Production Environment Secret | `DEFAULT_ADMIN_EMAIL`             |
| Production Environment Secret | `DEFAULT_ADMIN_PASSWORD`          |
| Production Environment Secret | `AZURE_STORAGE_CONNECTION_STRING` |

---

# 11. GitHub Actions Workflows

The repository contains four workflow files:

```text
.github/
└── workflows/
    ├── 01-ci.yml
    ├── 02-deploy-staging.yml
    ├── 03-staging-test.yml
    └── 04-deploy-production.yml
```

---

# 12. Run and Verify the Staging Application

Verify that the following workflows complete successfully:

01 - CI
02 - Deploy to Staging
03 - Staging Test
04 - Deploy to Production

Once the deployment is complete, verify the Kubernetes resources in the staging namespace and access the staging application using the frontend external IP.

Confirm that the application is working correctly before proceeding to production.

13. Deploy to Production

Production deployment is automatic. As soon as **03 - Staging Test** completes successfully, GitHub Actions triggers **04 - Deploy to Production** via a `workflow_run` event and deploys the exact same image SHA that was just tested in staging — no manual action is required.

To trigger the whole chain end-to-end, push a change to `main` (typically by merging a pull request):

```bash
git push origin main
```

Then watch the run in:

```text
GitHub Repository
→ Actions
```

All four workflows should run in sequence and complete successfully.

### Manual override (optional)

If you need to re-deploy a specific previously-tested commit to production without going through staging again, you can still trigger **04 - Deploy to Production** manually:

```text
GitHub Repository
→ Actions
→ 04 - Deploy to Production
→ Run workflow
```

Provide the image SHA as `image_tag`. This SHA must belong to a version that already passed the staging pipeline — production must use the same image version that was tested in staging. Do not rebuild the Docker images for production.

14. Verify the Production Application

After the production deployment completes:

- Verify the Kubernetes resources in the production namespace.
- Find the external IP of the production frontend service.
- Access the production application.
- Confirm that the application is working correctly.
- Verify that production is running the same image SHA that was tested in staging.


# 13. Progressive Delivery with Automated Rollback (10.3HD)

`course-service` is released as an **Argo Rollouts canary** on AKS. Traffic moves to a new version in steps (10%, 30%, 60%, 100%). At every step Prometheus is queried for the canary pods' HTTP 5xx ratio and p95 latency. If a threshold is breached three readings in a row, the rollout aborts automatically, traffic returns to the stable version, the GitHub Actions run fails, and a Discord alert is posted. No human is involved.

The other services still use the standard rolling update.

## How it works

```
merge to main
  -> 01 CI: Terraform (AKS, ACR, ingress-nginx, Argo Rollouts), tests, build and push images
  -> 02 deploy to staging -> 03 staging test
  -> 04 deploy to production: course-service becomes a canary
        10% -> analysis -> 30% -> analysis -> 60% -> analysis -> 100% (promoted)
                    \-> analysis fails -> abort, back to stable, Discord alert, job fails
  -> 05 monitoring: Prometheus, Grafana, PodMonitor, dashboards
```

| Piece | File |
| --- | --- |
| App metrics (`/metrics`), fault injection, `/courses/ping` | `course-service/app/main.py` |
| Rollout, stable and canary Services, Ingress | `kubernetes/progressive/course-service-rollout.yaml` |
| Analysis queries and thresholds | `kubernetes/progressive/analysis-template.yaml` |
| PodMonitor (keeps the `rollouts-pod-template-hash` label) | `kubernetes/progressive/podmonitor.yaml` |
| ingress-nginx and Argo Rollouts via Terraform's Helm provider | `terraform/progressive_delivery.tf` |
| Canary wait and Discord alert | `.github/workflows/04-deploy-production.yml` |
| Faulty-release demo (production canary or staging baseline) | `.github/workflows/06-demo-faulty-release.yml` |
| Grafana dashboard "Canary Release Analysis" | `kubernetes/monitoring/canary-dashboard.json` |
| Load generator | `k6/load.js` |

### The analysis gate

Both metrics run every 20 seconds after a 30-second initial delay, filtered to the canary's `rollouts_pod_template_hash`, so canary pods are separated from stable pods even though they run the same image.

| Metric | Query (simplified) | Fails when |
| --- | --- | --- |
| `error-ratio` | `5xx request rate / all request rate` | above 0.05 |
| `p95-latency` | `histogram_quantile(0.95, request duration buckets)` | above 0.5 s |

`failureLimit: 2` means the third bad reading fails the run, so one noisy sample cannot abort a healthy release. The initial delay stops empty early readings counting as passes (the query falls back to `vector(0)` when no data exists).

## Setup

1. Complete sections 1 to 12 first (fork, service principal, variables, secrets, environments).
2. Create a Discord webhook (channel settings, Integrations, Webhooks) and add its URL as the repository secret `DISCORD_WEBHOOK_URL`.
3. Merge to `main`. The CI Terraform job creates the cluster and installs ingress-nginx and Argo Rollouts, then the workflows build and deploy everything.
4. Install the tools for the demo: `k6`, and the Argo Rollouts kubectl plugin ([releases](https://github.com/argoproj/argo-rollouts/releases)).

> The pipeline's service principal only has **Contributor**, so it cannot create role assignments. Images are pulled with an `acr-pull` image pull secret created by the staging and production workflows from the ACR admin credentials, instead of an `AcrPull` role assignment.

## Run the demo

Find the ingress address and start steady load (about 75 requests per second):

```bash
az aks get-credentials -g <resource-group> -n <cluster> --overwrite-existing
INGRESS_IP=$(kubectl get svc ingress-nginx-controller -n ingress-nginx -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
k6 run -e BASE_URL=http://$INGRESS_IP --duration 15m k6/load.js
```

Always run load during a release. With no traffic the analysis has nothing to judge.

Watch the rollout and the dashboard in two more terminals:

```bash
kubectl argo rollouts get rollout course-service -n production --watch
kubectl -n monitoring port-forward svc/kube-prometheus-stack-grafana 3000:80   # http://localhost:3000
```

**Healthy release.** Merge any change to `main`. The canary steps through 10%, 30%, 60% and 100% and is promoted. The first deploy on a new cluster has no previous version, so it goes straight to 100%; canaries show from the second release.

**Faulty release (canary).** Run the manual workflow `06 - Demo Faulty Release` with `target = production`. It builds `course-service` with `FAULT_RATE=0.5` (HTTP 500 on half of `/courses` requests) and releases it. The analysis fails, the rollout shows `Degraded: RolloutAborted`, the job fails and Discord receives the image, failing metric and value.

**Baseline (rolling update).** Run the same workflow with `target = staging`. The plain Deployment accepts the faulty image because its readiness probe passes, the job succeeds, and about half of requests fail until you undo it:

```bash
kubectl rollout undo deployment/course-service -n staging
```

## Measured results

| Scenario | Result |
| --- | --- |
| Healthy canary | 45,232 requests during the release, all HTTP 200, zero failures |
| Faulty canary (production) | Aborted after 59 s of exposure; 234 failed requests, about 2.6% of traffic (first run: 75 s, 2.7%) |
| Same faulty image, rolling update (staging) | Job reported success; 49.9% of requests failed, live until a manual rollback |

## Clean up

The cluster costs Azure credits while it runs. When finished, run the `99 - Infrastructure Teardown` workflow.

## Known limitations

- Only `course-service` uses canaries.
- ACR admin credentials are less secure than a managed identity; they are used because the lab service principal cannot create role assignments.
- The frontend reaches `course-service` through the in-cluster Service, so frontend traffic is not split. The canary split applies to traffic through the ingress.
