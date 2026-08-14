# Question 15: Inject Istio Sidecars and Require Strict mTLS

## Objective

- Ensure every Pod in namespace `mtls` has an `istio-proxy` sidecar.
- Require mutual TLS for all workloads in the namespace.

## What this lab does and why

**What we are doing:** We are enrolling the namespace's workloads into the Istio data plane and applying a namespace-wide `PeerAuthentication` policy in `STRICT` mode. Existing Pods are recreated because injection occurs only when a Pod is created.

**Why it matters:** The sidecar proxies establish workload identities and encrypt service-to-service connections. Strict mTLS requires both ends to authenticate with mesh certificates and rejects plaintext connections that could bypass workload identity or expose application traffic.

**Objective summary:** Every workload Pod is represented in the mesh by an `istio-proxy`, and all inbound workload communication in `mtls` requires authenticated mutual TLS.

## Concept and theory

- **Service-mesh data plane:** In Istio sidecar mode, an Envoy proxy named `istio-proxy` runs beside the application container and intercepts workload traffic. The application usually does not need to implement mesh certificate handling itself.
- **Injection timing:** Automatic injection is performed by a mutating admission webhook when a Pod is created. Labeling a namespace changes future admission behavior but does not modify already running Pods, so controller-managed Pods must be recreated.
- **Workload identity and mTLS:** Istio issues short-lived workload certificates and uses them to authenticate both sides of a connection. Mutual TLS provides encryption, peer identity, and integrity rather than encryption alone.
- **PeerAuthentication scope:** A `PeerAuthentication` resource controls the mTLS mode accepted for inbound traffic. A policy named `default` with no selector applies to all workloads in its namespace. `STRICT` rejects plaintext; `PERMISSIVE` accepts both plaintext and mTLS.
- **Two required conditions:** Injecting sidecars makes workloads mesh-capable, while `PeerAuthentication` enforces the inbound mode. Completing only one half either leaves workloads outside the data plane or leaves plaintext connections accepted.

## Inspect Istio and workloads

```bash
istioctl version
kubectl get namespace mtls --show-labels
kubectl get pods -n mtls \
  -o custom-columns=NAME:.metadata.name,CONTAINERS:.spec.containers[*].name
kubectl get deploy,statefulset,daemonset -n mtls
kubectl get peerauthentication -n mtls
```

Check whether the installation uses revision-based injection:

```bash
kubectl get namespace istio-system --show-labels
kubectl get pods -n istio-system -l app=istiod --show-labels
```

## Enable injection

For a non-revisioned/default Istio installation:

```bash
kubectl label namespace mtls istio-injection=enabled --overwrite
```

For a revisioned control plane, use its actual revision instead:

```bash
kubectl label namespace mtls istio.io/rev=<revision> --overwrite
```

Do not keep conflicting labels. Istio documents that `istio-injection` takes precedence when both labels exist.

Namespace labels affect only newly created Pods. Restart controller-managed workloads:

```bash
for resource in $(kubectl get deployment,statefulset,daemonset -n mtls -o name); do
  kubectl rollout restart "$resource" -n mtls
done
```

Wait for each controller:

```bash
for resource in $(kubectl get deployment,statefulset,daemonset -n mtls -o name); do
  kubectl rollout status "$resource" -n mtls --timeout=180s
done
```

If standalone Pods exist, locate their source manifests or owning automation before deleting them. A deleted unmanaged Pod will not return automatically.

## Require strict mTLS

Create `mtls-strict.yaml`:

```yaml
apiVersion: security.istio.io/v1
kind: PeerAuthentication
metadata:
  name: default
  namespace: mtls
spec:
  mtls:
    mode: STRICT
```

Apply:

```bash
kubectl apply -f mtls-strict.yaml
```

If the installed Istio release does not serve `security.istio.io/v1`, inspect `kubectl api-resources | grep -i peerauthentication` and use the served version, commonly `v1beta1` on older releases.

## Verify

```bash
kubectl get pods -n mtls \
  -o custom-columns=NAME:.metadata.name,READY:.status.containerStatuses[*].ready,CONTAINERS:.spec.containers[*].name

kubectl get peerauthentication default -n mtls -o yaml
istioctl analyze -n mtls
```

Every application Pod should list `istio-proxy`. Check proxy synchronization:

```bash
istioctl proxy-status
```

When client and server workloads exist, test normal mesh-to-mesh traffic and confirm it succeeds. A plaintext client outside the mesh should fail against a strict-mTLS workload unless another gateway or policy terminates and originates mTLS.

## Cleanup for a disposable lab only

```bash
kubectl delete peerauthentication default -n mtls
kubectl label namespace mtls istio-injection-
kubectl label namespace mtls istio.io/rev-
```

## Sources

- [Istio sidecar injection](https://istio.io/latest/docs/setup/additional-setup/sidecar-injection/)
- [Istio PeerAuthentication](https://istio.io/latest/docs/reference/config/security/peer_authentication/)

---

[← Previous: Question 14](14-secure-docker-daemon.md) · [Index](README.md) · [Next: Question 16 →](16-create-tls-secret.md)
