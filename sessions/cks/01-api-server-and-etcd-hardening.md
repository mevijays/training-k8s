# Question 1: Secure kube-apiserver and etcd

## Objective

Remediate these findings:

- anonymous API authentication is enabled;
- authorization uses `AlwaysAllow`;
- etcd does not require trusted client certificates;
- use authentication or authorization webhooks only when a functioning backend is supplied.

## What this lab does and why

**What we are doing:** We are hardening the two most sensitive control-plane endpoints. The API server will stop treating unauthenticated requests as anonymous users and will make authorization decisions through the Node and RBAC authorizers. etcd will accept client connections only when they present a certificate signed by the trusted CA.

**Why it matters:** `AlwaysAllow` effectively removes API authorization, while anonymous authentication can give unauthenticated callers access to any permissions accidentally granted to anonymous identities. An etcd endpoint that does not verify client certificates may expose the cluster's complete stored state, including Secrets.

**Objective summary:** After this lab, unauthenticated API requests are rejected, API actions require an explicit authorization decision, and etcd clients must prove their identity with a trusted certificate.

## Concept and theory

- **API request security pipeline:** A Kubernetes API request passes through authentication, authorization, and then admission control. Authentication establishes the caller's identity; authorization decides whether that identity may perform the requested verb on the resource. Admission controllers evaluate create or update requests after those two checks.
- **Anonymous authentication:** When enabled, a request that supplies no accepted credential can become user `system:anonymous` in group `system:unauthenticated`. Disabling it makes the API server reject such requests instead of allowing them to continue to authorization.
- **Authorization modes:** `AlwaysAllow` approves every authenticated or anonymous request and therefore provides no real authorization boundary. `Node` gives kubelets narrowly defined access associated with their Nodes and Pods, while `RBAC` evaluates permissions declared through Roles and bindings.
- **etcd trust boundary:** etcd is Kubernetes' source of truth. API objects, cluster configuration, and Kubernetes Secrets are stored there. Server-side TLS encrypts the connection, while `--client-cert-auth=true` additionally requires the client to authenticate with a certificate signed by `--trusted-ca-file`.
- **Static Pod behavior:** In kubeadm clusters, kube-apiserver and stacked etcd run as static Pods. Kubelet watches their manifest files directly, so saving a manifest change causes the component to restart without a Deployment or API-server operation.

## Inspect

Run on the control-plane node:

```bash
sudo grep -E -- '--anonymous-auth|--authorization-mode|webhook' \
  /etc/kubernetes/manifests/kube-apiserver.yaml

sudo grep -E -- '--client-cert-auth|--trusted-ca-file|--cert-file|--key-file' \
  /etc/kubernetes/manifests/etcd.yaml
```

An isolated failure simulation can set `--anonymous-auth=true`, `--authorization-mode=AlwaysAllow`, and `--client-cert-auth=false`. Never do this on a shared cluster.

## Remediate kube-apiserver

Back up the manifest outside the static manifest directory:

```bash
sudo mkdir -p /root/cks-backup
sudo cp -a /etc/kubernetes/manifests/kube-apiserver.yaml /root/cks-backup/
sudo vi /etc/kubernetes/manifests/kube-apiserver.yaml
```

In `spec.containers[0].command`, remove `AlwaysAllow` and configure:

```yaml
- --anonymous-auth=false
- --authorization-mode=Node,RBAC
```

Kubelet will restart the API server automatically.

## Remediate etcd

```bash
sudo cp -a /etc/kubernetes/manifests/etcd.yaml /root/cks-backup/
sudo vi /etc/kubernetes/manifests/etcd.yaml
```

Ensure `spec.containers[0].command` includes:

```yaml
- --client-cert-auth=true
- --trusted-ca-file=/etc/kubernetes/pki/etcd/ca.crt
- --cert-file=/etc/kubernetes/pki/etcd/server.crt
- --key-file=/etc/kubernetes/pki/etcd/server.key
```

## Verify

```bash
kubectl get --raw='/readyz?verbose'

curl -k -o /dev/null -w '%{http_code}\n' https://127.0.0.1:6443/api
# Expected: 401

kubectl auth can-i create pods -n default --as alice
# Expected: no

sudo env ETCDCTL_API=3 etcdctl \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt \
  --key=/etc/kubernetes/pki/etcd/healthcheck-client.key \
  endpoint health
```

This request should fail because it has no client certificate:

```bash
curl --cacert /etc/kubernetes/pki/etcd/ca.crt \
  https://127.0.0.1:2379/health
```

## Webhook interpretation

Authentication and authorization webhooks are separate. Do not add `Webhook` without a provided backend and kubeconfig. When both backends exist, typical flags are:

```yaml
- --authentication-token-webhook-config-file=/etc/kubernetes/authn-webhook.yaml
- --authorization-mode=Node,RBAC,Webhook
- --authorization-webhook-config-file=/etc/kubernetes/authz-webhook.yaml
```

## Sources

- [kube-apiserver flags](https://kubernetes.io/docs/reference/command-line-tools-reference/kube-apiserver/)
- [Kubernetes authorization](https://kubernetes.io/docs/reference/access-authn-authz/authorization/)
- [etcd transport security](https://etcd.io/docs/v3.6/op-guide/security/)

---

[← Previous: Practice fixtures](practice-fixtures.md) · [Index](README.md) · [Next: Question 2 →](02-api-server-node-rbac-noderestriction.md)
