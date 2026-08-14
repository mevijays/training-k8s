# Question 7: Configure and Extend Kubernetes Audit Logging

## Objective

Configure kube-apiserver to:

- use `/etc/kubernetes/logpolicy/audit-policy.yaml`;
- write `/var/log/kubernetes/audit-logs.txt`;
- retain at most two rotated logs for ten days;
- retain existing `None` rules;
- log namespace operations at `RequestResponse`;
- log deployment request bodies in namespace `webapps` at `Request`;
- log ConfigMaps and Secrets at `Metadata`;
- log everything else at `Metadata`.

## What this lab does and why

**What we are doing:** We are enabling the API server's file audit backend, defining retention limits, and extending the supplied policy with different detail levels for different resources. High-value operations receive request or response bodies, while broad cluster activity receives metadata-only records.

**Why it matters:** Kubernetes audit logs establish who performed an API action, when it happened, what resource was affected, and—in selected cases—what data was submitted or returned. Rule ordering and selective detail are important because excessive logging can expose sensitive data and consume storage, while insufficient logging makes investigation impossible.

**Objective summary:** Produce persistent, rotated audit records that preserve the supplied exclusions, capture detailed high-risk activity, and retain metadata for all remaining requests.

## Concept and theory

- **Audit event lifecycle:** kube-apiserver can record an API request at stages including `RequestReceived`, `ResponseStarted`, `ResponseComplete`, and `Panic`. Long-running requests such as watches have different stage behavior from ordinary requests.
- **Audit levels:** `None` records nothing, `Metadata` records identity and request metadata, `Request` adds the request body, and `RequestResponse` adds both request and response bodies. Higher levels provide more evidence but increase storage use and the chance of recording sensitive data.
- **First-match policy:** Audit policy rules are evaluated from top to bottom and the first matching rule determines the level. Specific exclusions and high-detail rules must appear before a broad catch-all rule.
- **Backend and persistence:** The policy decides what to record; the log backend decides where to persist it. Because kube-apiserver runs in a container, both the policy path and log destination need hostPath mounts to survive container recreation.
- **Rotation controls:** `maxage` limits the age of rotated logs and `maxbackup` limits their count. Rotation limits disk growth, but audit logs still require monitoring because the active file can grow until its size threshold is reached.

## Rule-order principle

Audit rules are evaluated top to bottom and the first match wins. Existing rules describing what not to log must remain before the new positive rules.

## Extend the policy

Back up and edit:

```bash
sudo mkdir -p /root/cks-backup
sudo cp -a /etc/kubernetes/logpolicy/audit-policy.yaml /root/cks-backup/
sudo vi /etc/kubernetes/logpolicy/audit-policy.yaml
```

Preserve the supplied `None` rules at the top, then append the following rules in this order:

```yaml
apiVersion: audit.k8s.io/v1
kind: Policy
omitStages:
- RequestReceived
rules:
# Keep all supplied `level: None` rules here first.

- level: RequestResponse
  resources:
  - group: ""
    resources: ["namespaces"]

- level: Request
  namespaces: ["webapps"]
  resources:
  - group: "apps"
    resources: ["deployments"]

- level: Metadata
  resources:
  - group: ""
    resources: ["configmaps", "secrets"]

- level: Metadata
```

`Request` includes the request body but not the response body. Use `RequestResponse` only where both are required.

## Configure the static API-server Pod

```bash
sudo mkdir -p /var/log/kubernetes
sudo cp -a /etc/kubernetes/manifests/kube-apiserver.yaml /root/cks-backup/q7-kube-apiserver.yaml
sudo vi /etc/kubernetes/manifests/kube-apiserver.yaml
```

Add these command flags:

```yaml
- --audit-policy-file=/etc/kubernetes/logpolicy/audit-policy.yaml
- --audit-log-path=/var/log/kubernetes/audit-logs.txt
- --audit-log-maxbackup=2
- --audit-log-maxage=10
```

Add container mounts:

```yaml
volumeMounts:
- name: audit-policy
  mountPath: /etc/kubernetes/logpolicy
  readOnly: true
- name: audit-log
  mountPath: /var/log/kubernetes
  readOnly: false
```

Add Pod volumes:

```yaml
volumes:
- name: audit-policy
  hostPath:
    path: /etc/kubernetes/logpolicy
    type: Directory
- name: audit-log
  hostPath:
    path: /var/log/kubernetes
    type: DirectoryOrCreate
```

## Generate and inspect audit events

```bash
export KUBECONFIG=/etc/kubernetes/admin.conf
until kubectl get --raw=/readyz >/dev/null 2>&1; do sleep 2; done

kubectl get namespaces
kubectl get secrets -A >/dev/null
kubectl -n webapps get deployments >/dev/null

sudo tail -n 20 /var/log/kubernetes/audit-logs.txt
```

Read operations do not have a request body. To verify the deployment request body rule, perform a safe patch on a lab Deployment or use a server-side dry-run and inspect the generated audit event:

```bash
kubectl -n webapps patch deployment <lab-deployment> \
  --type=merge -p '{"spec":{"template":{"metadata":{"annotations":{"audit-lab":"true"}}}}}'

sudo grep '"resource":"deployments"' /var/log/kubernetes/audit-logs.txt | tail -1
```

## Source

- [Kubernetes auditing](https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/)

---

[← Previous: Question 6](06-deployment-security-context.md) · [Index](README.md) · [Next: Question 8 →](08-network-policies.md)
