# Question 2: Forbid Anonymous Access and Enable Node/RBAC Authorization

## Objective

Configure kube-apiserver with:

```text
--anonymous-auth=false
--authorization-mode=Node,RBAC
--enable-admission-plugins=NodeRestriction
```

Then remove the `system:anonymous` ClusterRoleBinding named in the scenario.

## What this lab does and why

**What we are doing:** We are configuring three complementary API-server protections. Authentication rejects anonymous callers, the Node and RBAC authorizers decide what authenticated identities may do, and `NodeRestriction` limits the Kubernetes objects a kubelet identity can modify. We also remove an obsolete binding that grants permissions to `system:anonymous`.

**Why it matters:** Authentication alone does not restrict an authenticated user, and authorization alone cannot safely distinguish callers when anonymous access is permitted. NodeRestriction adds a second boundary around node credentials so a compromised kubelet cannot freely modify other Nodes or unrelated Pods.

**Objective summary:** The resulting API server accepts identified callers, authorizes them through Node/RBAC rules, constrains kubelet writes, and contains no scenario-specific anonymous binding.

## Concept and theory

- **Authentication and authorization are separate:** A valid certificate or token proves who the caller is but does not grant permission by itself. The authorizer chain evaluates the authenticated username and groups against the requested API action.
- **Node authorizer identity:** A kubelet is normally authenticated as `system:node:<nodeName>` and belongs to `system:nodes`. The Node authorizer understands the relationship between that node, the Pods scheduled to it, and the Secrets or volumes those Pods require.
- **NodeRestriction admission:** The Node authorizer governs reads and writes broadly, while `NodeRestriction` adds admission-time restrictions to Node and Pod modifications. Together they reduce the effect of stolen kubelet credentials.
- **RBAC objects:** A Role or ClusterRole describes allowed API operations. A RoleBinding or ClusterRoleBinding attaches those permissions to users, groups, or ServiceAccounts. RBAC permissions are additive; Kubernetes has no general RBAC deny rule.
- **Anonymous bindings:** Disabling anonymous authentication blocks new anonymous requests, but removing an unnecessary binding is still important defense in depth. It prevents accidental exposure if anonymous access is later re-enabled or configured differently.

## Inspect

```bash
sudo grep -E -- \
  '--anonymous-auth|--authorization-mode|--enable-admission-plugins|--disable-admission-plugins' \
  /etc/kubernetes/manifests/kube-apiserver.yaml

KUBECONFIG=/etc/kubernetes/admin.conf \
  kubectl get clusterrolebinding system:anonymous -o yaml
```

## Configure kube-apiserver

```bash
sudo mkdir -p /root/cks-backup
sudo cp -a /etc/kubernetes/manifests/kube-apiserver.yaml /root/cks-backup/q2-kube-apiserver.yaml
sudo vi /etc/kubernetes/manifests/kube-apiserver.yaml
```

Set these command entries:

```yaml
- --anonymous-auth=false
- --authorization-mode=Node,RBAC
- --enable-admission-plugins=NodeRestriction
```

If `--enable-admission-plugins` already exists, add `NodeRestriction` to its comma-separated value instead of adding a duplicate flag. If `--disable-admission-plugins` contains `NodeRestriction`, remove it from that list.

Wait for recovery:

```bash
export KUBECONFIG=/etc/kubernetes/admin.conf
until kubectl get --raw=/readyz >/dev/null 2>&1; do sleep 2; done
kubectl get nodes
```

## Remove the binding

Confirm the exact target before deleting it:

```bash
kubectl get clusterrolebinding system:anonymous -o yaml
kubectl delete clusterrolebinding system:anonymous
```

Do not delete the built-in `system:public-info-viewer` binding unless the question names it.

## Verify

```bash
sudo grep -E -- \
  '--anonymous-auth|--authorization-mode|--enable-admission-plugins' \
  /etc/kubernetes/manifests/kube-apiserver.yaml

kubectl get clusterrolebinding system:anonymous
# Expected: NotFound

curl -k -o /dev/null -w '%{http_code}\n' https://127.0.0.1:6443/api
# Expected: 401

kubectl auth can-i delete nodes --as=system:node:worker-1
# Expected: no
```

## Why NodeRestriction matters

The Node authorizer controls what kubelets may access. The `NodeRestriction` admission plugin additionally limits which Node and Pod objects a kubelet identity may modify.

## Source

- [Admission controllers and NodeRestriction](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/#noderestriction)

---

[← Previous: Question 1](01-api-server-and-etcd-hardening.md) · [Index](README.md) · [Next: Question 3 →](03-image-policy-webhook.md)
