# ADK Enterprise Deployment on GKE & Eventarc Specification Template

> Fill in this template when deploying production-grade, containerized ADK 2 agents
> to Google Kubernetes Engine (GKE) Autopilot with Eventarc reactive triggers.

---

## 1. Workload Architecture & Cluster Topology

### What is the hosting infrastructure?

- [ ] **GKE Autopilot** (Recommended: managed node provisioning, security baselines, automatic scaling)
- [ ] **GKE Standard** (Custom node pools, specialized hardware/GPU requirements)
- [ ] **Cloud Run & GKE Hybrid** (Stateless coordinator on Cloud Run, heavy worker agents on GKE)

### Workload Identity Federation Binding:

```bash
# Bind Kubernetes Service Account (KSA) to Google Service Account (GSA)
gcloud iam service-accounts add-iam-policy-binding \
    adk-agent-gsa@$PROJECT_ID.iam.gserviceaccount.com \
    --role roles/iam.workloadIdentityUser \
    --member "serviceAccount:$PROJECT_ID.svc.id.goog[adk-agents/adk-agent-ksa]"
```

- [ ] GKE Workload Identity enabled on cluster
- [ ] Dedicated Kubernetes Namespace created (`adk-agents`)
- [ ] No static service account keys mounted or baked into container images

---

## 2. Containerization & Runtime Manifests

### Docker Multi-Stage Packaging:

- [ ] Multi-stage build (distroless or minimal Python slim base image)
- [ ] Non-root execution (`USER 1001:1001`)
- [ ] Pre-installed runtime dependencies (`uv` or `pip` cache mounted during build)
- [ ] Application entrypoint hosts ADK Runner with FastAPI/Uvicorn

### Kubernetes Deployment Manifest Checklist:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: adk-agent-deployment
  namespace: adk-agents
spec:
  replicas: 2
  template:
    spec:
      serviceAccountName: adk-agent-ksa
      containers:
      - name: adk-agent
        image: gcr.io/PROJECT_ID/adk-agent:v1.0
        resources:
          requests:
            cpu: "1"
            memory: "2Gi"
          limits:
            cpu: "2"
            memory: "4Gi"
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8080
          initialDelaySeconds: 15
          periodSeconds: 20
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 10
```

- [ ] Dedicated liveness probe verifying HTTP responsiveness
- [ ] Dedicated readiness probe verifying Vertex AI API reachability & model connectivity
- [ ] Explicit resource requests and limits configured

---

## 3. Stateful Streaming & Ingress Routing

### How are client connections managed?

- [ ] **Server-Sent Events (SSE)** over HTTPS
- [ ] **WebSockets** for bidirectional conversational streaming
- [ ] **REST Polling** against asynchronous session journals

### GKE Gateway API & Session Stickiness:

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: adk-agent-route
  namespace: adk-agents
spec:
  parentRefs:
  - name: external-gateway
  rules:
  - backendRefs:
    - name: adk-agent-service
      port: 8080
    sessionPersistence:
      sessionName: ADK_SESSION_AFFINITY
      type: Cookie
```

- [ ] GKE Gateway API configured with session persistence (Cookie-based session affinity)
- [ ] Cloud Armor security policy attached to Gateway (rate limiting, DDoS protection)
- [ ] TLS certificate managed automatically via Google Certificate Manager

---

## 4. Horizontal Autoscaling & Resource Scaling

### HorizontalPodAutoscaler (HPA) Policy:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: adk-agent-hpa
  namespace: adk-agents
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: adk-agent-deployment
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 65
  - type: Pods
    pods:
      metric:
        name: concurrent_agent_sessions
      target:
        type: AverageValue
        averageValue: 15
```

- [ ] Minimum 2 replicas configured to guarantee high availability during rollouts
- [ ] Scaling metric configured (CPU utilization + custom concurrent session metric)
- [ ] Graceful termination (`terminationGracePeriodSeconds: 60`) allowing ongoing agent turns to finalize before container shutdown

---

## 5. Event-Driven Reactive Triggers via Eventarc

### What event sources trigger asynchronous agent execution?

- [ ] **Cloud Storage**: Object creation (e.g. document uploaded, media uploaded)
- [ ] **Cloud Pub/Sub**: Message arriving on event bus
- [ ] **Cloud Audit Logs**: IAM modifications, infrastructure changes
- [ ] **Custom Application Events**: Microservice webhooks

### Eventarc Trigger Configuration:

```bash
# Trigger agent on document upload to Cloud Storage
gcloud eventarc triggers create doc-processing-agent-trigger \
    --location=us-central1 \
    --destination-run-service=adk-fulfillment-agent \
    --destination-run-region=us-central1 \
    --event-filters="type=google.cloud.storage.object.v1.finalized" \
    --event-filters="bucket=incoming-creator-uploads" \
    --service-account=eventarc-agent-trigger-sa@$PROJECT_ID.iam.gserviceaccount.com
```

- [ ] Eventarc trigger configured with exact CloudEvent filter criteria
- [ ] Target endpoint parses CloudEvent payload and initiates detached ADK workflow run
- [ ] Event-driven runner commits completion status back to database journal
