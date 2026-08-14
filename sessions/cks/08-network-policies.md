# Question 8: Namespace-Based NetworkPolicies

## Objective

Create only these policies:

1. `deny-policy` in `prod`, selecting every Pod and allowing no ingress.
2. `allow-from-prod` in `data`, selecting every Pod and permitting ingress only from the namespace carrying the production label.

Do not modify namespaces or Pods.

## What this lab does and why

**What we are doing:** We are isolating all Pods in `prod` from incoming connections and isolating all Pods in `data` so their only permitted ingress source is the namespace labeled as production. The policy selects namespaces by label rather than by a hard-coded namespace name.

**Why it matters:** Kubernetes networking is normally open between Pods unless a network policy isolates them. Default-deny behavior reduces lateral movement, while a narrowly scoped allow rule documents and enforces the one trusted communication path required by the application.

**Objective summary:** `prod` receives no ingress traffic, and `data` receives ingress only from Pods whose namespace matches the verified production label.

## Concept and theory

- **Default networking model:** Without effective NetworkPolicies, Kubernetes expects Pods to communicate freely across nodes and namespaces. A NetworkPolicy changes this behavior only for the Pods and traffic directions it selects.
- **Ingress isolation:** A Pod becomes isolated for ingress when at least one ingress NetworkPolicy selects it. Once isolated, a connection is allowed when at least one applicable policy permits that source. Policies are additive; one policy does not override another.
- **Empty selectors:** `podSelector: {}` selects every Pod in the policy's own namespace. An ingress policy with no `ingress` rules selects those Pods but permits no incoming sources, which produces default-deny ingress behavior.
- **Namespace selectors:** `namespaceSelector` matches namespace labels, not namespace names. Label-based selection is flexible, but it also means RBAC over namespace-label changes is part of the security boundary.
- **Enforcement location:** The Kubernetes API stores NetworkPolicy objects, while the CNI plugin enforces them in the data plane. A cluster can accept a valid policy even when its installed CNI does not implement enforcement.

## Inspect the real namespace labels

The pasted text rendered the labels as `env.prod` and `env.data`; this most likely represents `env=prod` and `env=data`. Confirm before writing the selector:

```bash
kubectl get namespace prod data --show-labels
kubectl get namespace prod -o jsonpath='{.metadata.labels}{"\n"}'
```

Assuming the label is `env=prod`, create `deny-policy.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-policy
  namespace: prod
spec:
  podSelector: {}
  policyTypes:
  - Ingress
```

Create `allow-from-prod.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-prod
  namespace: data
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          env: prod
```

Apply only the policies:

```bash
kubectl apply -f deny-policy.yaml
kubectl apply -f allow-from-prod.yaml
```

## Important YAML distinction

This permits sources matching both selectors in the same item:

```yaml
- namespaceSelector: {}
  podSelector: {}
```

This permits either source and is an OR operation:

```yaml
- namespaceSelector: {}
- podSelector: {}
```

The question requires only `namespaceSelector`.

## Verify without creating or changing Pods

```bash
kubectl get networkpolicy -n prod deny-policy -o yaml
kubectl get networkpolicy -n data allow-from-prod -o yaml
kubectl describe networkpolicy deny-policy -n prod
kubectl describe networkpolicy allow-from-prod -n data
```

Use existing Pods, if suitable ones already exist, to test traffic from `prod` and from another namespace. Do not create probe Pods in the exam scenario.

NetworkPolicy has an effect only when the installed CNI implements it. The Kubernetes API can accept the objects even when the network plugin does not enforce them.

## Cleanup for a disposable lab only

```bash
kubectl delete networkpolicy deny-policy -n prod
kubectl delete networkpolicy allow-from-prod -n data
```

## Source

- [Kubernetes NetworkPolicy](https://kubernetes.io/docs/concepts/services-networking/network-policies/)

---

[← Previous: Question 7](07-audit-logging.md) · [Index](README.md) · [Next: Question 9 →](09-tls-ingress.md)
