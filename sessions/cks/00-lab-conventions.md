# Lab Conventions and Safety

## Establish the cluster context

```bash
kubectl config current-context
kubectl cluster-info
kubectl get nodes -o wide
```

For kubeadm control-plane work, use the original administrator kubeconfig when required:

```bash
export KUBECONFIG=/etc/kubernetes/admin.conf
```

## Back up static Pod manifests safely

Kubelet scans `/etc/kubernetes/manifests`. Do not place `.bak`, `.old`, or other backup files there because kubelet can interpret them as additional manifests.

```bash
sudo mkdir -p /root/cks-backup
sudo cp -a /etc/kubernetes/manifests/kube-apiserver.yaml /root/cks-backup/
sudo cp -a /etc/kubernetes/manifests/etcd.yaml /root/cks-backup/
```

After editing a static Pod manifest, kubelet automatically recreates the component. Watch recovery with:

```bash
sudo crictl ps | grep -E 'kube-apiserver|etcd'
sudo journalctl -u kubelet --since '5 minutes ago'
kubectl get --raw='/readyz?verbose'
```

On an old Docker-based cluster, use `sudo docker ps` instead of `crictl`.

## Prefer declarative edits

When a question provides a manifest, edit that file and apply it:

```bash
kubectl apply -f /path/to/manifest.yaml
```

Use `kubectl patch` for a fast targeted change only when the question does not require the supplied file to be corrected.

## Verify every change

Use both configuration and behavioral checks:

```bash
kubectl get RESOURCE NAME -n NAMESPACE -o yaml
kubectl describe RESOURCE NAME -n NAMESPACE
kubectl get events -n NAMESPACE --sort-by=.lastTimestamp
```

## Cleanup

Lab-specific cleanup is included where the lab creates resources. Do not delete pre-existing resources unless the scenario explicitly asks for deletion.

---

[← Previous: CKS lab index](README.md) · [Index](README.md) · [Next: Practice fixtures →](practice-fixtures.md)
