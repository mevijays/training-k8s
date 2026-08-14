# Question 11: Upgrade Worker `compute-0`

## Objective

Upgrade the worker's kubeadm, kubelet, and kubectl packages to the control-plane node's Kubernetes version without editing application manifests.

Kubernetes supports one-minor-version-at-a-time upgrades. Use the exact target reported by the control plane.

## What this lab does and why

**What we are doing:** We are aligning the worker's kubeadm, kubelet, and kubectl versions with the control plane through the supported node-upgrade workflow. The node is inspected, its local kubelet configuration is upgraded, workloads are safely evacuated when required, and scheduling is restored after verification.

**Why it matters:** Unsupported version skew can cause API incompatibilities, missing security fixes, and unpredictable node behavior. Upgrading one node at a time and using drain/uncordon controls reduces workload disruption and provides a clear recovery boundary.

**Objective summary:** `compute-0` returns to `Ready` and schedulable state with the target Kubernetes version, without editing or deleting application definitions.

## Concept and theory

- **Component roles:** `kubeadm` manages cluster bootstrap and node configuration, `kubelet` runs and reports node workloads, and `kubectl` is the API client. Upgrading a worker requires compatible versions of these packages but does not run `kubeadm upgrade apply`, which is for the primary control plane.
- **Version skew:** Kubernetes supports only defined version differences between control-plane and node components. Minor versions must be upgraded sequentially rather than skipped, and the target package version should be derived from the already upgraded control plane.
- **Cordon and drain:** Cordon marks a Node unschedulable but leaves existing Pods running. Drain also evicts eligible Pods so controllers can replace them elsewhere; DaemonSet Pods are ignored because their controller is node-scoped.
- **Desired state remains intact:** Eviction does not edit Deployments, StatefulSets, or other workload definitions. Those controllers continue to express the same desired state and create replacements where scheduling permits.
- **Completion criteria:** Package installation alone is insufficient. The kubelet service must restart, the Node must report the target version and `Ready`, it must be uncordoned, and cluster workloads must remain healthy.

## Discover versions and workloads

From the control-plane node:

```bash
kubectl get nodes -o custom-columns=NAME:.metadata.name,KUBELET:.status.nodeInfo.kubeletVersion
kubectl get pods -A --field-selector spec.nodeName=compute-0 -o wide
```

Record the control-plane kubelet version:

```bash
CONTROL_NODE=$(kubectl get nodes -l node-role.kubernetes.io/control-plane \
  -o jsonpath='{.items[0].metadata.name}')
TARGET=$(kubectl get node "$CONTROL_NODE" \
  -o jsonpath='{.status.nodeInfo.kubeletVersion}' | sed 's/^v//')
echo "$TARGET"
```

## Interpret "do not modify running workloads"

Do not edit, delete, or scale application resources. For a minor kubelet upgrade, upstream guidance requires draining the worker. Drain performs controlled eviction, so controllers may recreate Pods elsewhere. Do not add `--delete-emptydir-data` or `--force` casually.

If the worker contains unmanaged Pods or local data and the task literally prohibits eviction, stop and reconcile that conflict rather than destroying workloads.

## Upgrade kubeadm on the worker

```bash
ssh compute-0
```

For Debian/Ubuntu, discover the exact package version string:

```bash
TARGET=<control-plane-version-without-leading-v>
apt-cache madison kubeadm | grep "$TARGET"
```

Set the returned package version, which can have a repository suffix:

```bash
PKG_VERSION=<exact-package-version>
sudo apt-mark unhold kubeadm
sudo apt-get update
sudo apt-get install -y kubeadm="$PKG_VERSION"
sudo apt-mark hold kubeadm
kubeadm version
```

For RPM-based systems:

```bash
sudo dnf --showduplicates list kubeadm
sudo dnf install -y kubeadm-<target-package-version> --disableexcludes=kubernetes
```

Update the node-local kubelet configuration:

```bash
sudo kubeadm upgrade node
exit
```

## Drain, upgrade kubelet, and return the node

From the control plane:

```bash
kubectl drain compute-0 --ignore-daemonsets
ssh compute-0
```

Debian/Ubuntu:

```bash
TARGET=<control-plane-version-without-leading-v>
apt-cache madison kubelet | grep "$TARGET"
PKG_VERSION=<exact-package-version>
sudo apt-mark unhold kubelet kubectl
sudo apt-get install -y kubelet="$PKG_VERSION" kubectl="$PKG_VERSION"
sudo apt-mark hold kubelet kubectl
sudo systemctl daemon-reload
sudo systemctl restart kubelet
sudo systemctl is-active kubelet
exit
```

RPM-based:

```bash
sudo dnf install -y \
  kubelet-<target-package-version> \
  kubectl-<target-package-version> \
  --disableexcludes=kubernetes
sudo systemctl daemon-reload
sudo systemctl restart kubelet
```

From the control plane:

```bash
kubectl uncordon compute-0
kubectl get node compute-0
kubectl get pods -A -o wide
```

Expected: `compute-0` is `Ready`, schedulable, and reports the same Kubernetes version as the control-plane node.

## Sources

- [Upgrading kubeadm clusters](https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-upgrade/)
- [Upgrading Linux worker nodes](https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/upgrading-linux-nodes/)

---

[← Previous: Question 10](10-projected-service-account-token.md) · [Index](README.md) · [Next: Question 12 →](12-sbom-and-image-removal.md)
