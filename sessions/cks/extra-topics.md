# CKS Missing Topics: Lab Steps & Understanding

---

## 1. Pod-to-Pod Encryption with Cilium and Istio

### Why It Matters
By default, pod-to-pod traffic in Kubernetes is unencrypted (plaintext). In the CKS exam, you must secure this communication. Cilium and Istio offer different approaches: Cilium uses native kernel-level encryption (WireGuard/IPsec), while Istio uses application-level mTLS with sidecar proxies.

### Concepts

#### Cilium Encryption
- **WireGuard**: Lightweight kernel VPN (fast, < 1ms overhead)
- **IPsec**: Traditional encryption protocol
- **Transparent**: Cilium handles encryption automatically at the node level; applications don't know about it

#### Istio mTLS with PeerAuthentication
- **mTLS**: Mutual TLS between envoy sidecars
- **PeerAuthentication**: Istio admission policy to enforce STRICT mode (rejects non-mTLS traffic)
- **Sidecar Proxies**: Transparent proxy container injected into every pod

---

### Lab: Cilium Pod-to-Pod Encryption

#### Prerequisites
- AKS cluster with Cilium CNI (or any k8s cluster with Cilium)
- kubectl access
- Two test namespaces

#### Step 1: Install/Verify Cilium
```bash
# Check if Cilium is already installed
kubectl get daemonset -n kube-system cilium

# If not installed, install Cilium Helm chart with encryption enabled
helm repo add cilium https://helm.cilium.io
helm install cilium cilium/cilium --namespace kube-system \
  --set encryption.enabled=true \
  --set encryption.type=wireguard
```

#### Step 2: Create Test Namespaces & Pods
```bash
# Create two namespaces
kubectl create ns app-a
kubectl create ns app-b

# Deploy a simple web server in app-a
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: web-server
  namespace: app-a
  labels:
    app: web
spec:
  containers:
  - name: nginx
    image: nginx:alpine
    ports:
    - containerPort: 80
EOF

# Deploy a client pod in app-b
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: client
  namespace: app-b
  labels:
    app: client
spec:
  containers:
  - name: curl
    image: curlimages/curl:latest
    command: ["sleep", "3600"]
EOF

# Wait for pods to be running
kubectl get pods -n app-a -n app-b -w
```

#### Step 3: Verify Encryption is Active
```bash
# Check Cilium agent logs for encryption statistics
kubectl logs -n kube-system -l k8s-app=cilium --tail=50 | grep -i encrypt

# Check WireGuard status (if using WireGuard)
kubectl exec -it -n kube-system -l k8s-app=cilium -- cilium status
```

#### Step 4: Test Pod-to-Pod Communication
```bash
# From client pod, curl the web server
kubectl exec -it -n app-b client -- curl http://web-server.app-a.svc.cluster.local

# You should get the nginx welcome page
# Traffic flows through Cilium's encrypted tunnel transparently
```

#### Step 5: Capture & Verify Encryption
```bash
# On the node where traffic flows, capture packets
# (Traffic should be encrypted - you won't see plaintext HTTP headers)
tcpdump -i cilium_vxlan dst 172.x.x.x -A | head -20
# Notice: encrypted binary data, no HTTP plaintext

# Or use cilium command to see encrypted tunnel stats
kubectl exec -it -n kube-system <cilium-pod-name> -- cilium metrics list | grep encry
```

#### Step 6: Cilium NetworkPolicy (Optional - for added security)
```bash
# Create a NetworkPolicy allowing only app-b → app-a:80
cat <<EOF | kubectl apply -f -
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: allow-app-a-from-app-b
  namespace: app-a
spec:
  endpointSelector:
    matchLabels:
      app: web
  ingress:
  - fromEndpoints:
    - matchLabels:
        app: client
    toPorts:
    - ports:
      - port: "80"
        protocol: TCP
EOF

# Retest communication - should still work
```

**Key Takeaway**: Cilium encryption is transparent, automatic, and kernel-level. No application changes needed.

---

### Lab: Istio mTLS with PeerAuthentication (STRICT Mode)

#### Prerequisites
- AKS cluster with Istio installed
- Two test namespaces

#### Step 1: Install Istio
```bash
# Install Istio using istioctl or Helm
istioctl install --set profile=demo -y

# Or via Helm
helm repo add istio https://istio.release.io
helm install istio-base istio/base -n istio-system --create-namespace
helm install istiod istio/istiod -n istio-system
```

#### Step 2: Enable Sidecar Injection
```bash
# Label the namespaces for automatic sidecar injection
kubectl label namespace app-a istio-injection=enabled
kubectl label namespace app-b istio-injection=enabled

# Delete and recreate pods so sidecars are injected
kubectl delete pod web-server -n app-a
kubectl delete pod client -n app-b

# Recreate them (use same YAML as Cilium lab)
# Verify sidecars are injected
kubectl get pods -n app-a -o jsonpath='{.items[*].spec.containers[*].name}'
# Should see: nginx istio-proxy (two containers per pod)
```

#### Step 3: Set PeerAuthentication to STRICT
```bash
# Create a cluster-wide PeerAuthentication policy
cat <<EOF | kubectl apply -f -
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: strict-mtls
  namespace: istio-system
spec:
  mtls:
    mode: STRICT
EOF

# This enforces: all pod-to-pod traffic MUST be mTLS encrypted
# Plain HTTP requests will be rejected
```

#### Step 4: Test mTLS Communication
```bash
# From client pod, curl the web server through mTLS
kubectl exec -it -n app-b client -- curl http://web-server.app-a.svc.cluster.local

# Request succeeds because:
# - Client sidecar (Envoy) intercepts the request
# - Sidecar performs mTLS handshake with server sidecar
# - Server sidecar validates client certificate
# - Traffic is encrypted

# Check Envoy sidecar logs
kubectl logs -n app-b client -c istio-proxy | grep -i "tls\|mtls"
```

#### Step 5: Verify Plain HTTP is Rejected (STRICT Mode)
```bash
# Try to reach the server from outside the mesh (without sidecar)
# Create a pod WITHOUT sidecar injection

cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: external-client
  namespace: default
spec:
  containers:
  - name: curl
    image: curlimages/curl:latest
    command: ["sleep", "3600"]
EOF

# Try to curl from external pod
kubectl exec -it external-client -- curl -v http://web-server.app-a.svc.cluster.local

# Result: Connection refused or timeout
# Because STRICT mode rejects non-mTLS traffic
```

#### Step 6: Allow External Traffic (Optional)
```bash
# If you need external (non-mesh) traffic, use PERMISSIVE mode temporarily
# (Not for production - use for migration only)

cat <<EOF | kubectl apply -f -
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: mtls-permissive
  namespace: app-a
spec:
  mtls:
    mode: PERMISSIVE
EOF

# Now external traffic is allowed, but mTLS is still used when available
```

**Key Takeaway**: Istio STRICT mode enforces mTLS for all traffic. It's application-aware (sees HTTP/gRPC), but requires sidecar injection overhead.

---

### Cilium vs Istio: When to Use Each

| Aspect | Cilium | Istio |
|--------|--------|-------|
| **Encryption Level** | Kernel (transparent) | Application (sidecar proxies) |
| **Overhead** | Low (<1ms) | Higher (sidecar proxies) |
| **Setup Complexity** | Simple (install CNI) | Complex (sidecar injection, policies) |
| **Observability** | Basic (metrics) | Rich (traffic management, traces) |
| **CKS Exam Focus** | Pod-to-pod encryption | mTLS enforcement, PeerAuthentication |
| **Use Case** | Pure encryption at network layer | Full service mesh (traffic mgmt + encryption) |

**For CKS**: Know both concepts, but focus on:
- Cilium: How it transparently encrypts
- Istio: How PeerAuthentication STRICT mode enforces mTLS

---

## 2. KubeLinter

### Why It Matters
KubeLinter is an open-source tool that scans Kubernetes YAML manifests **before** they are deployed, catching security misconfigurations (e.g., running as root, missing resource limits, privileged containers). Unlike Kubesec (which focuses on scoring), KubeLinter provides actionable remediation.

### Concepts
- **Static Analysis**: Scans YAML files without running them
- **Built-in Rules**: ~50 security, efficiency, and best-practice checks
- **Custom Rules**: Write custom Rego policies (similar to Kyverno)
- **CI/CD Integration**: Run in pipelines to gate deployments
- **Output Formats**: JSON, SARIF (for GitHub security tab)

---

### Lab: Install & Scan with KubeLinter

#### Step 1: Install KubeLinter
```bash
# On macOS
brew install kubelinter

# On Linux
wget https://github.com/stackrox/kube-linter/releases/download/v0.6.4/kube-linter-linux
chmod +x kube-linter-linux
sudo mv kube-linter-linux /usr/local/bin/kube-linter

# Verify installation
kube-linter version
```

#### Step 2: Create Test YAML with Security Issues
```bash
cat <<EOF > vulnerable-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: vulnerable-app
  namespace: default
spec:
  containers:
  - name: app
    image: nginx:latest
    # Missing:
    # - runAsNonRoot: true
    # - readOnlyRootFilesystem: true
    # - resources limits/requests
    securityContext:
      privileged: true  # BAD! CKS violation
    volumeMounts:
    - name: host-fs
      mountPath: /host
  volumes:
  - name: host-fs
    hostPath:
      path: /  # BAD! Exposes entire host filesystem
EOF
```

#### Step 3: Run KubeLinter Scan
```bash
# Basic scan
kube-linter lint vulnerable-pod.yaml

# You should see warnings:
# - privileged container
# - missing resource limits
# - runs as root
# - host filesystem mount

# Output shows: [ERROR] violation type, severity, and remediation
```

#### Step 4: Review KubeLinter Rules
```bash
# List all built-in checks
kube-linter checks list

# Show details for a specific check
kube-linter checks describe privilege-escalation-container

# Search for a check by name
kube-linter checks list | grep -i "resources"
```

#### Step 5: Create a Fixed YAML
```bash
cat <<EOF > secure-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-app
  namespace: default
spec:
  containers:
  - name: app
    image: nginx:1.23  # Pinned version (not latest)
    securityContext:
      runAsNonRoot: true
      runAsUser: 101  # nginx user
      readOnlyRootFilesystem: true
      allowPrivilegeEscalation: false
      capabilities:
        drop:
        - ALL
    resources:
      requests:
        memory: "64Mi"
        cpu: "100m"
      limits:
        memory: "128Mi"
        cpu: "200m"
    volumeMounts:
    - name: cache
      mountPath: /var/cache/nginx
    - name: run
      mountPath: /var/run
  volumes:
  - name: cache
    emptyDir: {}
  - name: run
    emptyDir: {}
EOF
```

#### Step 6: Scan the Secure YAML
```bash
kube-linter lint secure-pod.yaml

# Result: No errors or minimal warnings (PASSED)
```

#### Step 7: Generate JSON Report
```bash
# Useful for CI/CD pipelines
kube-linter lint vulnerable-pod.yaml --format json > report.json

# View report
cat report.json | jq '.Reports[0].Checks[] | {name, severity, remediation}'
```

#### Step 8: GitHub Actions Integration (Optional)
```bash
cat <<EOF > .github/workflows/kube-lint.yml
name: KubeLinter Check

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Install KubeLinter
      run: |
        wget https://github.com/stackrox/kube-linter/releases/download/v0.6.4/kube-linter-linux
        chmod +x kube-linter-linux
        sudo mv kube-linter-linux /usr/local/bin/kube-linter
    
    - name: Lint Kubernetes manifests
      run: kube-linter lint k8s/*.yaml
EOF
```

**Key Takeaway**: KubeLinter catches security violations early in the pipeline. It's simpler than Kyverno/Gatekeeper but doesn't enforce at admission time.

---

## 3. Multi-Tenancy Isolation

### Why It Matters
In shared Kubernetes clusters, tenants (teams, customers, projects) must be isolated to prevent one tenant's workload from affecting another's. CKS requires knowledge of namespace isolation, quotas, limits, and node affinity.

### Concepts

#### Layer 1: Namespace-Level Isolation
- Each tenant gets its own namespace
- RBAC prevents cross-namespace access
- NetworkPolicy controls traffic between namespaces

#### Layer 2: Resource Quotas & Limits
- **ResourceQuota**: Limits total CPU/memory per namespace
- **LimitRange**: Sets min/max CPU/memory per container
- Prevents one tenant from consuming all cluster resources

#### Layer 3: Node-Level Isolation
- **Taints**: Mark nodes as unavailable for certain pods
- **NodeSelectors/Affinity**: Force pods to run on specific nodes
- Separates tenant workloads onto dedicated nodes

#### Layer 4: Network Isolation
- **NetworkPolicy**: Restrict traffic between pods in different namespaces
- Default deny, then allow specific flows

---

### Lab: Multi-Tenancy Isolation Setup

#### Step 1: Create Tenant Namespaces
```bash
# Create namespaces for tenant-a and tenant-b
kubectl create namespace tenant-a
kubectl create namespace tenant-b
```

#### Step 2: Set ResourceQuota per Tenant
```bash
# Tenant-A: Limited to 2 CPU, 2Gi memory
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ResourceQuota
metadata:
  name: quota-tenant-a
  namespace: tenant-a
spec:
  hard:
    requests.cpu: "2"
    requests.memory: "2Gi"
    limits.cpu: "4"
    limits.memory: "4Gi"
    pods: "10"
EOF

# Tenant-B: Limited to 1 CPU, 1Gi memory
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ResourceQuota
metadata:
  name: quota-tenant-b
  namespace: tenant-b
spec:
  hard:
    requests.cpu: "1"
    requests.memory: "1Gi"
    limits.cpu: "2"
    limits.memory: "2Gi"
    pods: "5"
EOF

# Verify quotas
kubectl describe quota -n tenant-a
kubectl describe quota -n tenant-b
```

#### Step 3: Set LimitRange per Tenant
```bash
# Set min/max container resources for tenant-a
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: LimitRange
metadata:
  name: limits-tenant-a
  namespace: tenant-a
spec:
  limits:
  - max:
      cpu: "500m"
      memory: "512Mi"
    min:
      cpu: "50m"
      memory: "64Mi"
    type: Container
  - max:
      cpu: "1"
      memory: "1Gi"
    min:
      cpu: "100m"
      memory: "128Mi"
    type: Pod
EOF

# Verify limits
kubectl describe limitrange -n tenant-a
```

#### Step 4: Deploy Pods to Tenant Namespaces
```bash
# Deploy pod in tenant-a with resource requests/limits
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: app-a-pod
  namespace: tenant-a
spec:
  containers:
  - name: app
    image: nginx:latest
    resources:
      requests:
        cpu: "100m"
        memory: "128Mi"
      limits:
        cpu: "200m"
        memory: "256Mi"
EOF

# Deploy pod in tenant-b
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: app-b-pod
  namespace: tenant-b
spec:
  containers:
  - name: app
    image: nginx:latest
    resources:
      requests:
        cpu: "100m"
        memory: "128Mi"
      limits:
        cpu: "200m"
        memory: "256Mi"
EOF

# Verify pods are running
kubectl get pods -n tenant-a -n tenant-b
```

#### Step 5: Test Quota Enforcement
```bash
# Try to deploy a pod that exceeds ResourceQuota in tenant-a
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: oversized-pod
  namespace: tenant-a
spec:
  containers:
  - name: app
    image: nginx:latest
    resources:
      requests:
        cpu: "2.5"  # Exceeds quota (max 2)
        memory: "512Mi"
      limits:
        cpu: "5"
        memory: "1Gi"
EOF

# Result: Error - exceeds ResourceQuota
# This enforces multi-tenancy isolation at resource level
```

#### Step 6: Set Up Node-Level Isolation (Optional but Recommended)
```bash
# Taint nodes for tenant-a only
kubectl taint nodes <node-name> tenant=a:NoSchedule

# Taint different nodes for tenant-b
kubectl taint nodes <other-node-name> tenant=b:NoSchedule

# Now deploy pods with node affinity
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: tenant-a-exclusive-pod
  namespace: tenant-a
spec:
  tolerations:
  - key: tenant
    operator: Equal
    value: "a"
    effect: NoSchedule
  nodeSelector:
    tenant: a
  containers:
  - name: app
    image: nginx:latest
EOF

# This pod will ONLY run on nodes tainted with tenant=a
# Tenant-B pods cannot run on these nodes
```

#### Step 7: NetworkPolicy - Namespace Isolation
```bash
# Deny all ingress traffic in tenant-a by default
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-ingress
  namespace: tenant-a
spec:
  podSelector: {}
  policyTypes:
  - Ingress
EOF

# Allow traffic only from within tenant-a
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-within-tenant
  namespace: tenant-a
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: tenant-a
    ports:
    - protocol: TCP
      port: 80
EOF

# Label tenant-a namespace so the policy matches it
kubectl label namespace tenant-a name=tenant-a

# Verify network isolation: try to curl from tenant-b pod to tenant-a pod
# Result: Connection refused (NetworkPolicy blocks it)
```

#### Step 8: RBAC for Tenant Isolation
```bash
# Create role for tenant-a users (limited to tenant-a namespace)
cat <<EOF | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: tenant-a-admin
  namespace: tenant-a
rules:
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["get", "list", "create", "delete"]
EOF

# Bind the role to a user/service account
cat <<EOF | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: tenant-a-admin-binding
  namespace: tenant-a
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: tenant-a-admin
subjects:
- kind: User
  name: tenant-a-user@example.com
  apiGroup: rbac.authorization.k8s.io
EOF

# Tenant-A user can only access tenant-a namespace
# They cannot see pods in tenant-b
```

**Multi-Tenancy Checklist**:
- ✅ Separate namespaces per tenant
- ✅ ResourceQuota limits total resources
- ✅ LimitRange enforces per-container limits
- ✅ Node taints separate tenant workloads
- ✅ NetworkPolicy blocks cross-tenant traffic
- ✅ RBAC restricts user access to tenant namespace

---

## 4. ImagePolicyWebhook

### Why It Matters
ImagePolicyWebhook is the **built-in Kubernetes admission plugin** that controls which container images are allowed in the cluster. It enforces a whitelist of trusted registries (e.g., only allow images from `company-registry.com`, reject Docker Hub images).

Unlike Kyverno/Gatekeeper (which are separate controllers), ImagePolicyWebhook is a native admission plugin configured in the API server itself.

### Concepts

#### Admission Controller Flow
1. User submits a Pod/Deployment
2. API server calls the webhook server
3. Webhook server evaluates the image against policy
4. Webhook returns `allow: true/false`
5. Pod is created (or rejected)

#### Configuration Components
- **Admission config file**: Tells API server which webhook to call
- **Kubeconfig file**: Credentials/endpoint for webhook server
- **Policy file**: Rules on which images are allowed
- **defaultAllow**: If webhook is unreachable, allow or deny?

---

### Lab: Set Up ImagePolicyWebhook

#### Step 1: Create a Simple Webhook Server
```bash
# Create a webhook that allows only specific registries
mkdir -p ~/image-policy-webhook
cd ~/image-policy-webhook

cat <<EOF > webhook.py
#!/usr/bin/env python3
import json
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

class ImagePolicyHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        
        # Parse the admission request
        admission_review = json.loads(body)
        request = admission_review['request']
        
        # Extract the image from the pod spec
        pod_spec = request['object']['spec']
        images = []
        for container in pod_spec.get('containers', []):
            images.append(container['image'])
        
        # Policy: Only allow images from these registries
        ALLOWED_REGISTRIES = [
            'docker.io',
            'gcr.io',
            'my-company-registry.com',
            'nginx',  # Docker Hub implicit
            'alpine'
        ]
        
        allowed = True
        reason = ""
        
        for image in images:
            # Extract registry from image (before the first /)
            registry = image.split('/')[0] if '/' in image else 'docker.io'
            
            # Check if registry is in whitelist
            if registry not in ALLOWED_REGISTRIES:
                allowed = False
                reason = f"Image '{image}' uses disallowed registry '{registry}'"
                break
        
        # Build response
        admission_response = {
            "apiVersion": "admission.k8s.io/v1",
            "kind": "AdmissionReview",
            "response": {
                "uid": request['uid'],
                "allowed": allowed,
                "status": {
                    "message": reason if reason else "Image registry allowed"
                }
            }
        }
        
        # Send response
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(admission_response).encode())

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8443), ImagePolicyHandler)
    print("Starting webhook server on port 8443...")
    server.serve_forever()
EOF

chmod +x webhook.py
```

#### Step 2: Create Webhook TLS Certificates
```bash
# Create self-signed cert for the webhook
openssl req -x509 -newkey rsa:2048 -keyout webhook.key -out webhook.crt \
  -days 365 -nodes -subj "/CN=image-policy-webhook.default.svc"

# Create a Kubernetes secret with the certs
kubectl create secret tls image-policy-webhook-certs \
  --cert=webhook.crt --key=webhook.key
```

#### Step 3: Deploy Webhook as a Pod
```bash
# Create a Deployment for the webhook
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: webhook-script
  namespace: default
data:
  webhook.py: |
$(cat webhook.py | sed 's/^/    /')
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: image-policy-webhook
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: image-policy-webhook
  template:
    metadata:
      labels:
        app: image-policy-webhook
    spec:
      containers:
      - name: webhook
        image: python:3.9-slim
        ports:
        - containerPort: 8443
        volumeMounts:
        - name: webhook-script
          mountPath: /webhook
        - name: webhook-certs
          mountPath: /etc/webhook/certs
          readOnly: true
        command: ["python3", "/webhook/webhook.py"]
      volumes:
      - name: webhook-script
        configMap:
          name: webhook-script
      - name: webhook-certs
        secret:
          secretName: image-policy-webhook-certs
---
apiVersion: v1
kind: Service
metadata:
  name: image-policy-webhook
  namespace: default
spec:
  ports:
  - port: 443
    targetPort: 8443
  selector:
    app: image-policy-webhook
EOF

# Verify the webhook is running
kubectl get pods -l app=image-policy-webhook
```

#### Step 4: Configure ImagePolicyWebhook on API Server
```bash
# Create admission config that calls the webhook
cat <<EOF > /etc/kubernetes/policies/image-policy.yaml
apiVersion: apiserver.config.k8s.io/v1
kind: AdmissionConfiguration
plugins:
- name: ImagePolicyWebhook
  configuration:
    imagePolicy:
      kubeConfigFile: /etc/kubernetes/policies/webhook-config.kubeconfig
      allowTTL: 50
      denyTTL: 50
      retryBackoff: 5
      defaultAllow: false
EOF

# Create kubeconfig for the webhook
cat <<EOF > /etc/kubernetes/policies/webhook-config.kubeconfig
apiVersion: v1
kind: Config
clusters:
- cluster:
    certificate-authority: /etc/kubernetes/policies/webhook.crt
    server: https://image-policy-webhook.default.svc.cluster.local
  name: image-policy-webhook
contexts:
- context:
    cluster: image-policy-webhook
    user: api-server
  name: image-policy-webhook-context
current-context: image-policy-webhook-context
users:
- name: api-server
  user:
    client-certificate: /etc/kubernetes/pki/apiserver.crt
    client-key: /etc/kubernetes/pki/apiserver.key
EOF
```

#### Step 5: Restart API Server (if self-managed cluster)
```bash
# Edit the API server pod manifest
# For AKS/managed clusters, contact your cloud provider to enable the plugin

# For kubeadm clusters:
sudo nano /etc/kubernetes/manifests/kube-apiserver.yaml

# Add these arguments:
# - --admission-control-config-file=/etc/kubernetes/policies/image-policy.yaml
# - --enable-admission-plugins=...,ImagePolicyWebhook

# API server will auto-restart due to kubelet watching the manifest
```

#### Step 6: Test Policy Enforcement
```bash
# Try to create a pod with an ALLOWED image
kubectl run test-nginx --image=nginx:latest

# Result: Pod created successfully (image from docker.io, which is allowed)

# Try to create a pod with a DISALLOWED image
kubectl run test-bad --image=ubuntu:latest

# Result: Error - webhook rejected the image
# Message: "Image 'ubuntu:latest' uses disallowed registry 'docker.io' (or custom logic)"
```

#### Step 7: View Policy Rejections
```bash
# Check API server logs to see webhook decisions
kubectl logs -n kube-system kube-apiserver-$(hostname) | grep -i "imagepolicy"

# Or check the webhook deployment logs
kubectl logs -l app=image-policy-webhook
```

#### Step 8: Update Policy (Add More Registries)
```bash
# Edit the ConfigMap to update the webhook script
# Example: Add 'quay.io' to ALLOWED_REGISTRIES

kubectl edit configmap webhook-script

# In the editor, update the list:
# ALLOWED_REGISTRIES = [
#     'docker.io',
#     'gcr.io',
#     'quay.io',  # NEW
#     'my-company-registry.com'
# ]

# Save and exit. The webhook pod will pick up the change
# (You may need to restart the webhook pod)
kubectl rollout restart deployment image-policy-webhook
```

---

### ImagePolicyWebhook vs Kyverno/Gatekeeper

| Aspect | ImagePolicyWebhook | Kyverno | Gatekeeper |
|--------|-------------------|---------|-----------|
| **Type** | Native admission plugin | Kubernetes controller | Policy enforcement engine |
| **Setup** | API server config | Install controller | Install controller |
| **Policy Language** | Custom (webhook logic) | Kyverno DSL (YAML) | Rego (CEL) |
| **Complexity** | Simple (for image rules) | Medium | Complex (Rego) |
| **Performance** | Direct (no extra pods) | Minimal overhead | Minimal overhead |
| **CKS Exam** | MUST know | Nice to know | Nice to know |

**For CKS Exam**: ImagePolicyWebhook is the core requirement. You need to know:
1. Admission config file syntax
2. Kubeconfig file for webhook endpoint
3. How defaultAllow works
4. How to configure on the API server

---

## Quick Reference: Exam-Focused Commands

### Cilium
```bash
helm install cilium cilium/cilium --set encryption.enabled=true --set encryption.type=wireguard
kubectl exec -n kube-system <cilium-pod> -- cilium status
```

### Istio
```bash
istioctl install --set profile=demo
kubectl label namespace <ns> istio-injection=enabled
kubectl apply -f - <<EOF
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: strict-mtls
spec:
  mtls:
    mode: STRICT
EOF
```

### KubeLinter
```bash
kube-linter lint <manifest.yaml>
kube-linter lint <manifest.yaml> --format json
```

### Multi-Tenancy
```bash
kubectl create namespace <tenant>
kubectl apply -f - <<EOF
apiVersion: v1
kind: ResourceQuota
metadata:
  name: quota-<tenant>
  namespace: <tenant>
spec:
  hard:
    requests.cpu: "2"
    requests.memory: "2Gi"
EOF
```

### ImagePolicyWebhook
```bash
# Key config file locations:
# - /etc/kubernetes/policies/image-policy.yaml (admission config)
# - /etc/kubernetes/policies/webhook-config.kubeconfig (webhook credentials)
# - kubeconfig defaultAllow: false (deny if webhook unreachable)
```

---

## Summary: What CKS Expects You to Know

1. **Cilium**: Transparent kernel-level encryption, WireGuard/IPsec
2. **Istio**: mTLS via PeerAuthentication STRICT mode, sidecar proxies
3. **KubeLinter**: Static analysis of YAML before deployment, caught security issues
4. **Multi-Tenancy**: Namespace + ResourceQuota + LimitRange + Node affinity + NetworkPolicy + RBAC
5. **ImagePolicyWebhook**: Built-in admission plugin for image registry whitelisting

All four are components of the **"Secure Kubernetes Supply Chain"** and **"Runtime Security"** domains in CKS.
