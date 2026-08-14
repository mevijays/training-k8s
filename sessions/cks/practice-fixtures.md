# Practice Fixtures for a Normal Kubernetes Cluster

This file supplies safe starting states for the labs that normally assume an exam cluster already contains resources. Apply only the section you are practicing. Use a disposable cluster and review every manifest first.

## Questions 1, 2, 3, 7, 11, and 14: host-level prerequisites

These tasks need node access and cannot be faithfully reproduced on a managed control plane.

- Questions 1, 2, 3, and 7 require a kubeadm control plane whose static manifests live in `/etc/kubernetes/manifests`.
- Question 11 requires at least one worker node and package repositories containing both versions.
- Question 14 requires a host actually running Docker Engine. Modern Kubernetes normally uses containerd, so use an older/disposable Docker-backed VM for that exercise.
- Back up static manifests outside `/etc/kubernetes/manifests` before creating an insecure state.

For Question 1, an isolated failure state consists of:

```yaml
# kube-apiserver command entries
- --anonymous-auth=true
- --authorization-mode=AlwaysAllow
```

```yaml
# etcd command entry
- --client-cert-auth=false
```

Restore the secure values immediately by following Question 1. Do not use this failure simulation on any machine reachable by untrusted users.

For Question 3, `defaultAllow: false` can be tested with an unreachable HTTPS webhook, but a full success/deny exercise requires a backend that accepts `imagepolicy.k8s.io/v1alpha1` `ImageReview` objects. The exam-provided scanner supplies that behavior.

For Question 7, a minimal starting policy is:

```yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
- level: None
  users: ["system:kube-proxy"]
  verbs: ["watch"]
  resources:
  - group: ""
    resources: ["endpoints", "services"]
```

Save it as `/etc/kubernetes/logpolicy/audit-policy.yaml`, then extend it using the lab.

## Question 4: vulnerable Deployment and Dockerfile

Use this Deployment in a disposable namespace:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: subtle-bee
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: subtle-bee
  template:
    metadata:
      labels:
        app: subtle-bee
    spec:
      containers:
      - name: web
        image: nginx:1.27
        securityContext:
          privileged: true
```

Example Dockerfile:

```dockerfile
FROM nginx:1.27
USER root
```

The practice fixes are `privileged: false` and a suitable non-root user. Real exam files can contain different one-field violations; diagnose before editing.

## Question 5: harmless fake `/dev/mem` reader

This fixture mounts a normal `emptyDir` file at `/dev/mem`. It exercises process discovery without exposing system memory.

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ollama
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ollama-memory-reader
  namespace: ollama
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ollama
  template:
    metadata:
      labels:
        app: ollama
    spec:
      initContainers:
      - name: create-fake-memory
        image: busybox:1.36
        command: ["sh", "-c", "printf safe > /seed/mem"]
        volumeMounts:
        - name: fake-memory
          mountPath: /seed
      containers:
      - name: ollama
        image: busybox:1.36
        command:
        - sh
        - -c
        - while true; do dd if=/dev/mem of=/dev/null bs=1 count=1 2>/dev/null; sleep 5; done
        volumeMounts:
        - name: fake-memory
          mountPath: /dev/mem
          subPath: mem
      volumes:
      - name: fake-memory
        emptyDir: {}
```

Apply it, discover it with the Question 5 workflow, and scale its Deployment to zero.

## Question 6: `lamp-deployment`

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: lamp
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: lamp-deployment
  namespace: lamp
spec:
  replicas: 1
  selector:
    matchLabels:
      app: lamp
  template:
    metadata:
      labels:
        app: lamp
    spec:
      containers:
      - name: lamp
        image: busybox:1.36
        command: ["sh", "-c", "id; sleep 3600"]
```

Save it as `lamp-deployment.yaml`, apply it, and then add the three requested security settings.

## Question 8: namespaces and test applications

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: prod
  labels:
    env: prod
---
apiVersion: v1
kind: Namespace
metadata:
  name: data
  labels:
    env: data
---
apiVersion: v1
kind: Pod
metadata:
  name: client
  namespace: prod
  labels:
    app: client
spec:
  containers:
  - name: client
    image: busybox:1.36
    command: ["sleep", "3600"]
---
apiVersion: v1
kind: Pod
metadata:
  name: web
  namespace: data
  labels:
    app: web
spec:
  containers:
  - name: web
    image: nginx:1.27
---
apiVersion: v1
kind: Service
metadata:
  name: web
  namespace: data
spec:
  selector:
    app: web
  ports:
  - port: 80
```

This requires a CNI that implements NetworkPolicy. After applying the policies:

```bash
kubectl exec -n prod client -- wget -qO- --timeout=3 http://web.data.svc
```

The request should succeed. A client from an unlabeled namespace should fail.

## Question 9: web Service and TLS material

This fixture assumes ingress-nginx is already installed.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
  namespace: prod
spec:
  replicas: 1
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: web
        image: nginx:1.27
---
apiVersion: v1
kind: Service
metadata:
  name: web
  namespace: prod
spec:
  selector:
    app: web
  ports:
  - name: http
    port: 80
    targetPort: 80
```

Generate a disposable certificate and Secret:

```bash
openssl req -x509 -nodes -newkey rsa:2048 -days 7 \
  -subj '/CN=web.k8s.local' \
  -addext 'subjectAltName=DNS:web.k8s.local' \
  -keyout web.k8s.local.key \
  -out web.k8s.local.crt

kubectl create secret tls web-cert -n prod \
  --cert=web.k8s.local.crt \
  --key=web.k8s.local.key
```

## Question 10: ServiceAccount and Deployment

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: monitoring
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: stats-monitor-sa
  namespace: monitoring
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: stats-monitor
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: stats-monitor
  template:
    metadata:
      labels:
        app: stats-monitor
    spec:
      serviceAccountName: stats-monitor-sa
      containers:
      - name: monitor
        image: busybox:1.36
        command: ["sleep", "3600"]
```

Apply it and then perform the explicit token-projection lab.

## Question 12: three Alpine images

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: alpine
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: alpine
  namespace: alpine
spec:
  replicas: 1
  selector:
    matchLabels:
      app: alpine
  template:
    metadata:
      labels:
        app: alpine
    spec:
      containers:
      - name: alpine-317
        image: alpine:3.17
        command: ["sleep", "3600"]
      - name: alpine-318
        image: alpine:3.18
        command: ["sleep", "3600"]
      - name: alpine-319
        image: alpine:3.19
        command: ["sleep", "3600"]
```

Public tags receive rebuilt patch images, so they may no longer contain historical package version `3.1.4-r5`. The fixture still practices discovery, SBOM generation, and container removal. To reproduce the exact version, load the pinned digest or image archive supplied by the course lab.

## Question 13: Restricted Pod Security failure

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: confidential
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: latest
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-unprivileged
  namespace: confidential
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx-unprivileged
  template:
    metadata:
      labels:
        app: nginx-unprivileged
    spec:
      containers:
      - name: nginx
        image: nginxinc/nginx-unprivileged:1.27-alpine
        ports:
        - containerPort: 8080
```

The Deployment can be created, but Pod admission should report the missing Restricted fields. Add the fields from Question 13 and verify the Pod starts.

## Question 15: Istio workloads

After Istio is installed, create the namespace without an injection label and deploy two services from the Istio samples, or use two simple HTTP Deployments. Confirm each Pod initially has one container, then perform the injection and `PeerAuthentication` steps.

```bash
kubectl create namespace mtls
kubectl apply -n mtls -f samples/httpbin/httpbin.yaml
kubectl apply -n mtls -f samples/curl/curl.yaml
kubectl get pods -n mtls \
  -o custom-columns=NAME:.metadata.name,CONTAINERS:.spec.containers[*].name
```

Run these paths from the root of an Istio release that contains `samples/`.

## Question 16: Deployment waiting for a TLS Secret

Generate the certificate files:

```bash
mkdir -p /home/candidate/clever-cactus
openssl req -x509 -nodes -newkey rsa:2048 -days 7 \
  -subj '/CN=web.k8s.local' \
  -addext 'subjectAltName=DNS:web.k8s.local' \
  -keyout /home/candidate/clever-cactus/web.k8s.local.key \
  -out /home/candidate/clever-cactus/web.k8s.local.crt
```

Create the starting workload:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: clever-cactus
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: clever-cactus
  namespace: clever-cactus
spec:
  replicas: 1
  selector:
    matchLabels:
      app: clever-cactus
  template:
    metadata:
      labels:
        app: clever-cactus
    spec:
      containers:
      - name: app
        image: busybox:1.36
        command: ["sleep", "3600"]
        volumeMounts:
        - name: tls
          mountPath: /tls
          readOnly: true
      volumes:
      - name: tls
        secret:
          secretName: clever-cactus
```

The Pod remains in `CreateContainerConfigError` until Question 16 creates the Secret.

## Fixture cleanup

Delete only the resources you created for practice:

```bash
kubectl delete namespace ollama lamp prod data monitoring alpine confidential mtls clever-cactus
```

Review the namespace list before running cleanup, especially on a non-disposable cluster.

---

[← Previous: Lab conventions](00-lab-conventions.md) · [Index](README.md) · [Next: Question 1 →](01-api-server-and-etcd-hardening.md)
