# Question 5: Identify a Pod Accessing `/dev/mem`

## Objective

Use Docker Engine process information to identify the offending container and Pod, follow its owner chain to the Deployment, and scale that Deployment to zero.

## What this lab does and why

**What we are doing:** We are starting with host-level evidence—a process reading `/dev/mem`—and tracing it back through the Docker container, Kubernetes Pod, ReplicaSet, and owning Deployment. Once attribution is confirmed, we contain the activity by scaling only that Deployment to zero.

**Why it matters:** `/dev/mem` represents access to physical memory and can expose credentials, kernel data, or other sensitive information. Acting only on a process or Pod is temporary because a controller recreates it; acting on the verified owning Deployment stops the controller from bringing the workload back.

**Objective summary:** Reliably identify the responsible workload from runtime evidence and contain it at the controller level without disrupting unrelated applications.

## Concept and theory

- **Linux device files:** `/dev/mem` is a character device that exposes physical memory where the kernel permits it. Normal containers should not need it. Access commonly indicates an overly privileged container, a passed-through device, or a dangerous host mount.
- **Container processes are host processes:** Containers isolate processes with namespaces and cgroups, but the Linux kernel still schedules host PIDs. Runtime tools and `/proc/<pid>/cgroup` let an administrator map suspicious host activity back to a container.
- **Runtime metadata mapping:** Docker containers created for Kubernetes Pods carry labels containing the Pod name, namespace, and container name. These labels bridge host-level runtime evidence with Kubernetes API objects.
- **Controller ownership chain:** A Pod created by a Deployment is owned by a ReplicaSet, and that ReplicaSet is owned by the Deployment. Deleting only the Pod triggers reconciliation and creates a replacement; scaling the verified Deployment to zero changes the desired state and stops recreation.
- **Containment before remediation:** Scaling to zero is a reversible containment action. It stops the behavior while preserving the workload definition for later forensic review and correction.

## Investigation workflow

Run on the node hosting the suspect containers:

```bash
sudo docker ps --no-trunc

for cid in $(sudo docker ps -q); do
  if sudo docker top "$cid" -eo pid,args | grep -q '/dev/mem'; then
    echo "suspect container: $cid"
    sudo docker top "$cid" -eo pid,user,args
  fi
done
```

If the command line does not contain the path, find a host process with the file open:

```bash
sudo lsof /dev/mem
sudo fuser -v /dev/mem
```

For a returned host PID, obtain its Docker container ID:

```bash
sudo cat /proc/<PID>/cgroup
```

Map the container to Kubernetes metadata. Kubernetes-created Docker containers carry labels:

```bash
sudo docker inspect <CONTAINER_ID> --format \
  'pod={{ index .Config.Labels "io.kubernetes.pod.name" }} namespace={{ index .Config.Labels "io.kubernetes.pod.namespace" }} container={{ index .Config.Labels "io.kubernetes.container.name" }}'
```

## Follow the owner chain

```bash
POD=<suspect-pod>
NS=<suspect-namespace>

kubectl get pod "$POD" -n "$NS" -o wide
kubectl get pod "$POD" -n "$NS" \
  -o jsonpath='{.metadata.ownerReferences[0].kind}{" "}{.metadata.ownerReferences[0].name}{"\n"}'
```

If the owner is a ReplicaSet:

```bash
RS=$(kubectl get pod "$POD" -n "$NS" -o jsonpath='{.metadata.ownerReferences[0].name}')
kubectl get rs "$RS" -n "$NS" \
  -o jsonpath='{.metadata.ownerReferences[0].kind}{" "}{.metadata.ownerReferences[0].name}{"\n"}'

DEPLOY=$(kubectl get rs "$RS" -n "$NS" -o jsonpath='{.metadata.ownerReferences[0].name}')
```

Confirm before changing replicas:

```bash
kubectl get deployment "$DEPLOY" -n "$NS"
kubectl scale deployment "$DEPLOY" -n "$NS" --replicas=0
```

## Verify

```bash
kubectl get deployment "$DEPLOY" -n "$NS"
kubectl get pods -n "$NS" -o wide
sudo lsof /dev/mem
```

The Deployment should show `0/0`, its Pods should terminate, and no workload process should hold `/dev/mem`.

## Safe simulation

On a disposable Docker-backed lab, simulate the command pattern without exposing real system memory. Mount a normal file at the container path `/dev/mem` and run a loop that reads it. The investigation still exercises `docker top`, Docker labels, owner traversal, and scaling, but no host memory is exposed.

Modern Kubernetes removed the built-in dockershim. On containerd clusters, replace Docker inspection with `crictl ps`, `crictl inspect`, and the host PID information exposed by the CRI runtime.

---

[← Previous: Question 4](04-manifest-and-dockerfile-hardening.md) · [Index](README.md) · [Next: Question 6 →](06-deployment-security-context.md)
