# Question 10: Explicitly Project a ServiceAccount Token

## Objective

- Disable automatic credential mounting on ServiceAccount `stats-monitor-sa` in namespace `monitoring`.
- Explicitly project a short-lived token into Deployment `stats-monitor`.
- Name the projected volume `token`.
- Make the final token path `/var/run/secrets/kubernetes.io/serviceaccount/token` and mount it read-only.

## What this lab does and why

**What we are doing:** We are disabling automatic API credential injection and then explicitly mounting a short-lived, Pod-bound ServiceAccount token only where the application expects it. The projected volume allows kubelet to request and rotate the token rather than relying on a long-lived Secret.

**Why it matters:** Automatic token mounting gives API credentials to containers even when they do not need them. Explicit projection follows least privilege, makes credential use visible in the manifest, supports automatic rotation, and reduces the useful lifetime of a stolen token.

**Objective summary:** The ServiceAccount no longer supplies credentials automatically, while `stats-monitor` receives one deliberately projected, read-only, rotating token at the required path.

## Concept and theory

- **Workload identity:** A ServiceAccount gives a Pod an identity for Kubernetes API authentication. RBAC bindings determine what that identity may do; possessing a token does not automatically grant broad permissions.
- **Automatic mounting:** Kubernetes can automatically inject API credentials based on the Pod and ServiceAccount `automountServiceAccountToken` settings. A Pod-level value takes precedence over the ServiceAccount value. Disabling automount removes credentials from workloads that do not explicitly request them.
- **Token projection:** A `serviceAccountToken` projected volume uses the TokenRequest API to obtain a short-lived, Pod-bound JWT. Kubelet refreshes the token before expiry, and deletion of the Pod or ServiceAccount limits its continued usefulness.
- **Audience:** A token audience identifies the service intended to accept the token. Omitting it uses the API server's configured default; specifying an unrelated audience can make the Kubernetes API reject the token.
- **Volume path construction:** The source's `path` is relative to the volume mount directory. Mounting volume `token` at `/var/run/secrets/kubernetes.io/serviceaccount` with source path `token` creates the required final filename without using a long-lived Secret.

## Disable automatic mounting

```bash
kubectl patch serviceaccount stats-monitor-sa -n monitoring \
  --type=merge \
  -p '{"automountServiceAccountToken":false}'
```

Verify:

```bash
kubectl get serviceaccount stats-monitor-sa -n monitoring \
  -o jsonpath='{.automountServiceAccountToken}{"\n"}'
```

Expected: `false`.

## Edit the supplied Deployment manifest

Resolve the pasted path and inspect the existing names:

```bash
ls -l ~/stats-monitor/deployment.yaml /stats-monitor/deployment.yaml 2>/dev/null
kubectl get deployment stats-monitor -n monitoring -o yaml
```

Inside `spec.template.spec`, ensure:

```yaml
serviceAccountName: stats-monitor-sa
automountServiceAccountToken: false
```

Add this volume:

```yaml
volumes:
- name: token
  projected:
    sources:
    - serviceAccountToken:
        path: token
        expirationSeconds: 3600
```

The audience is intentionally omitted so Kubernetes uses the API server's configured default audience. Set an explicit audience only when the consuming service requires one.

For the application container, add:

```yaml
volumeMounts:
- name: token
  mountPath: /var/run/secrets/kubernetes.io/serviceaccount
  readOnly: true
```

The volume's `path: token` is relative to `mountPath`, producing exactly:

```text
/var/run/secrets/kubernetes.io/serviceaccount/token
```

Apply and wait:

```bash
kubectl apply -f ~/stats-monitor/deployment.yaml
kubectl rollout status deployment/stats-monitor -n monitoring
```

## Verify without printing the credential

```bash
POD=$(kubectl get pods -n monitoring \
  -l app=stats-monitor \
  -o jsonpath='{.items[0].metadata.name}')

kubectl exec -n monitoring "$POD" -- \
  sh -c 'test -s /var/run/secrets/kubernetes.io/serviceaccount/token && echo token-present'

kubectl exec -n monitoring "$POD" -- \
  sh -c 'mount | grep /var/run/secrets/kubernetes.io/serviceaccount || true'

kubectl get pod "$POD" -n monitoring -o yaml
```

Do not use `cat` on the token during verification; credentials can leak into terminal history or recordings.

## Source

- [Configure ServiceAccounts and projected tokens](https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/)

---

[← Previous: Question 9](09-tls-ingress.md) · [Index](README.md) · [Next: Question 11 →](11-worker-node-upgrade.md)
