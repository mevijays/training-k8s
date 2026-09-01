# Domain 1 - Cluster Setup

Securing the cluster control plane: etcd, TLS everywhere, API server flags, authentication, authorization, encryption at rest, auditing, kubelet security, ingress TLS and network policies.

[&#8962; Back to All Domains](../README.md)

---

## Documents

| # | Topic | Link |
| :--- | :--- | :--- |
| 1 | Configure etcd Binaries | [Read](./install-etcd.md) |
| 2 | Configure Certificate Authority | [Read](./configure-ca.md) |
| 3 | Workflow - Issuance of Signed Certificates | [Read](./certificate-workflow.md) |
| 4 | etcd - Transport Security with HTTPS | [Read](./etcd-https.md) |
| 5 | Practical - Mutual TLS Authentication | [Read](./mutual-tls.md) |
| 6 | Integrating systemd with etcd | [Read](./etcd-systemd.md) |
| 7 | Configuring API Server | [Read](./configure-apiserver.md) |
| 8 | Transport Security for API Server | [Read](./apiserver-https.md) |
| 9 | Static Token Authentication | [Read](./token-authentication.md) |
| 10 | Downsides - Static Token Authentication | [Read](./downside-token-auth.md) |
| 11 | Implementing X509 Client Authentication | [Read](./certificate-auth-k8s.md) |
| 12 | Authorization | [Read](./authorization.md) |
| 13 | Encryption Providers | [Read](./encryption-provider.md) |
| 14 | Implementing Auditing | [Read](./audit-logs.md) |
| 15 | Setting up a kubeadm Cluster | [Read](./kubeadm-install.md) |
| 16 | Revising Taints and Tolerations | [Read](./taint-toleration.md) |
| 17 | Kubelet Security | [Read](./kubelet-security.md) |
| 18 | Verifying Platform Binaries | [Read](./verify-binaries.md) |
| 19 | Practical - Ingress with TLS | [Read](./ingress-security.md) |
| 20 | Ingress Annotation - SSL Redirect | [Read](./ingress-ssl-annotation.md) |
| 21 | Structure of a Network Policy | [Read](./netpol-structure.md) |
| 22 | Practical - Network Policies | [Read](./netpol-practical.md) |
| 23 | Network Policies - Except, Port and Protocol | [Read](./netpol-02.md) |

## Additional References

Supporting notes and alternate walkthroughs that live in this domain.

| # | Topic | Link |
| :--- | :--- | :--- |
| 24 | Reference - systemd Unit Files for etcd | [Read](./systemd.md) |
| 25 | Reference - kubeadm Installation Steps | [Read](./kubeadm.md) |
| 26 | Reference - Ingress Resource Rules | [Read](./ingress.md) |
| 27 | Reference - Ingress Controller and Name-Based Routing | [Read](./ingress-controller.md) |

---

Every document above links to the previous and next topic, so you can read this domain straight through starting with [Configure etcd Binaries](./install-etcd.md).
