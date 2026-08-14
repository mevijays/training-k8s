# CKS Practical Lab Guide

This directory converts the 16 supplied CKS-style scenarios into reproducible labs for a normal Kubernetes cluster. The goal is to understand, perform, and verify each security control rather than memorize commands.

## Recommended environment

- A disposable Linux cluster created with `kubeadm`
- Shell and `sudo` access to the control-plane and worker nodes
- `kubectl` configured with cluster-admin credentials
- `crictl` for modern containerd/CRI-O clusters
- Docker only for questions that explicitly assume Docker Engine
- A CNI that enforces `NetworkPolicy`, such as Calico or Cilium
- ingress-nginx for the Ingress lab
- Istio for the mTLS lab

Read [00-lab-conventions.md](00-lab-conventions.md) before changing control-plane manifests.
Use [practice-fixtures.md](practice-fixtures.md) to create safe starting resources for scenarios that normally rely on a prebuilt exam cluster.

## Labs

1. [Secure kube-apiserver and etcd](01-api-server-and-etcd-hardening.md)
2. [API server authorization and NodeRestriction](02-api-server-node-rbac-noderestriction.md)
3. [ImagePolicyWebhook admission controller](03-image-policy-webhook.md)
4. [Deployment and Dockerfile hardening](04-manifest-and-dockerfile-hardening.md)
5. [Find a container accessing `/dev/mem`](05-detect-devmem-access.md)
6. [Apply container security contexts](06-deployment-security-context.md)
7. [Configure Kubernetes audit logging](07-audit-logging.md)
8. [Create namespace-based NetworkPolicies](08-network-policies.md)
9. [Create a TLS Ingress with HTTPS redirect](09-tls-ingress.md)
10. [Project a ServiceAccount token explicitly](10-projected-service-account-token.md)
11. [Upgrade a kubeadm worker node](11-worker-node-upgrade.md)
12. [Find a vulnerable package and generate an SPDX SBOM](12-sbom-and-image-removal.md)
13. [Meet the Restricted Pod Security Standard](13-restricted-pod-security.md)
14. [Secure the Docker daemon](14-secure-docker-daemon.md)
15. [Enable Istio sidecars and strict mTLS](15-istio-strict-mtls.md)
16. [Create a Kubernetes TLS Secret](16-create-tls-secret.md)

## Important scope notes

- The supplied scenarios omit the contents of several manifests. Those labs include a diagnostic workflow and a representative vulnerable example. Inspect the real file before choosing the exact edit.
- Commands containing placeholder values such as `<version>` or `<service-port>` must be replaced using cluster data.
- Static Pod changes can temporarily take the API server down. Keep a root shell open on the control-plane node and keep backups outside `/etc/kubernetes/manifests`.
- These are practice scenarios. Do not deliberately weaken a shared or production cluster to reproduce a failure.

---

[← Previous: Question 16](16-create-tls-secret.md) · [Index](README.md) · [Next: Lab conventions →](00-lab-conventions.md)
