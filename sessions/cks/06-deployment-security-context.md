# Question 6: Harden `lamp-deployment`

## Objective

Modify the Deployment in namespace `lamp` so every application container:

- runs with UID `20000`;
- has a read-only root filesystem;
- cannot gain additional privileges.

## What this lab does and why

**What we are doing:** We are applying a Pod-level non-root UID and container-level filesystem and privilege-escalation restrictions. The Pod-level UID supplies a consistent identity to every container, while `readOnlyRootFilesystem` and `allowPrivilegeEscalation` control properties that belong to individual containers.

**Why it matters:** Running as a high-numbered non-root UID reduces the impact of a container compromise. A read-only root filesystem makes it harder to replace binaries or establish persistence, and disabling privilege escalation prevents child processes from gaining more rights through mechanisms such as setuid binaries.

**Objective summary:** Every application container runs as UID `20000`, cannot write to its image filesystem, and cannot acquire privileges beyond those of its parent process.

## Concept and theory

- **Pod vs. container security context:** Pod-level settings provide defaults for all containers, while container-level settings apply to one container and override overlapping Pod values. Some fields, including `readOnlyRootFilesystem` and `allowPrivilegeEscalation`, exist only at container level.
- **Numeric runtime identity:** `runAsUser: 20000` tells the runtime to start the process with that numeric UID. The image does not need a matching username in `/etc/passwd` for the kernel to enforce the UID, although some applications expect a named account or writable home directory.
- **Read-only root filesystem:** This makes the image's root filesystem non-writable. It does not make explicitly mounted volumes read-only. Applications that legitimately write temporary or state data should receive narrowly scoped writable volumes such as `emptyDir` or a PVC.
- **Privilege escalation:** `allowPrivilegeEscalation: false` sets the Linux `no_new_privs` behavior for the container process. It prevents mechanisms such as setuid or file capabilities from giving a child process more privileges than its parent.
- **Rollout behavior:** Changing `spec.template` creates a new Deployment revision. The Deployment controller replaces old Pods with new ones, so verification must inspect both the template and the newly running processes.

## Locate and inspect the supplied file

The pasted question rendered the path ambiguously. Check likely paths:

```bash
ls -l ~/finer-sunbeam/lamp-deployment.yaml /finer-sunbeam/lamp-deployment.yaml 2>/dev/null
kubectl get deployment lamp-deployment -n lamp -o yaml
```

Set the actual path:

```bash
MANIFEST=~/finer-sunbeam/lamp-deployment.yaml
```

## Edit the Pod template

At Pod level, set the UID so it applies to all containers:

```yaml
spec:
  template:
    spec:
      securityContext:
        runAsUser: 20000
```

For each entry under `spec.template.spec.containers`, configure:

```yaml
      containers:
      - name: <existing-name>
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
```

Apply the supplied manifest:

```bash
kubectl apply -f "$MANIFEST"
kubectl rollout status deployment/lamp-deployment -n lamp
```

If the image writes to `/tmp`, a cache, or another application directory, mount an `emptyDir` at only that writable location rather than disabling the read-only root filesystem:

```yaml
volumeMounts:
- name: tmp
  mountPath: /tmp
volumes:
- name: tmp
  emptyDir: {}
```

## Verify configuration

```bash
kubectl get deployment lamp-deployment -n lamp \
  -o jsonpath='{.spec.template.spec.securityContext.runAsUser}{"\n"}'

kubectl get deployment lamp-deployment -n lamp \
  -o jsonpath='{range .spec.template.spec.containers[*]}{.name}{" uid="}{.securityContext.runAsUser}{" ro="}{.securityContext.readOnlyRootFilesystem}{" no-priv-esc="}{.securityContext.allowPrivilegeEscalation}{"\n"}{end}'
```

An empty container-level UID is acceptable when Pod-level `runAsUser: 20000` is present.

Verify the runtime identity:

```bash
SELECTOR=$(kubectl get deployment lamp-deployment -n lamp \
  -o jsonpath='{range $k,$v := .spec.selector.matchLabels}{$k}={$v}{","}{end}' \
  | sed 's/,$//')
POD=$(kubectl get pod -n lamp -l "$SELECTOR" -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n lamp "$POD" -- id
kubectl exec -n lamp "$POD" -- sh -c 'touch /should-fail'
```

Expected: `uid=20000`; writing to `/` fails.

## Source

- [Configure a security context](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/)

---

[← Previous: Question 5](05-detect-devmem-access.md) · [Index](README.md) · [Next: Question 7 →](07-audit-logging.md)
