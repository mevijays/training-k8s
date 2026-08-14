# Question 13: Make a Deployment Comply with Restricted Pod Security

## Objective

Modify `/home/candidate/nginx-unprivileged.yaml` so the Deployment in namespace `confidential` passes the namespace's Restricted Pod Security policy and its Pods run.

## What this lab does and why

**What we are doing:** We are diagnosing the fields rejected by Pod Security Admission and updating the Pod template with a non-root identity, a runtime-default seccomp profile, disabled privilege escalation, and dropped Linux capabilities. Every regular and init container must satisfy the applicable Restricted controls.

**Why it matters:** The Restricted standard provides a consistent baseline against common container escape and privilege-escalation techniques. A controller object can exist even while its Pods repeatedly fail admission, so both policy compliance and successful Pod startup must be verified.

**Objective summary:** Correct every reported violation with the smallest application-compatible changes and confirm the Deployment produces running, non-root Pods under Restricted enforcement.

## Concept and theory

- **Standards vs. admission:** Pod Security Standards define the `Privileged`, `Baseline`, and `Restricted` policy profiles. Pod Security Admission is the built-in mechanism that applies those standards to namespaces using `enforce`, `audit`, and `warn` labels.
- **Restricted profile:** Restricted builds on Baseline and requires common hardening controls such as non-root execution, disabled privilege escalation, an allowed seccomp profile, and dropping Linux capabilities. It also restricts host namespaces, host paths, host ports, and certain volume or kernel settings.
- **Enforcement behavior:** A Deployment can be stored even when its Pod template produces warnings, but the ReplicaSet's Pod creations can be denied. This often appears as a Deployment with zero ready replicas and admission failures in namespace events.
- **Seccomp and capabilities:** `RuntimeDefault` applies the container runtime's syscall filter. Dropping `ALL` removes the default Linux capability set; an application should add back only a specifically justified capability if the namespace policy permits it.
- **Every container matters:** Pod Security evaluates regular containers, init containers, and relevant ephemeral containers. Hardening only the first application container can leave the Pod noncompliant.

## Diagnose every admission failure

```bash
kubectl get namespace confidential --show-labels
kubectl get deployment -n confidential
kubectl get replicaset,pods -n confidential
kubectl get events -n confidential --sort-by=.lastTimestamp | tail -30
kubectl apply --dry-run=server -f /home/candidate/nginx-unprivileged.yaml
```

The server-side dry-run error usually lists every violating field. Correct all of them, not only the first.

## Restricted-compatible template

Merge the following into `spec.template.spec` without deleting existing labels, probes, ports, volumes, or commands:

```yaml
spec:
  template:
    spec:
      securityContext:
        runAsNonRoot: true
        seccompProfile:
          type: RuntimeDefault
      containers:
      - name: <existing-container-name>
        securityContext:
          allowPrivilegeEscalation: false
          capabilities:
            drop:
            - ALL
```

Apply the same container-level settings to every regular container and init container.

If the image does not declare a non-root user, add an image-compatible UID:

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 101
  seccompProfile:
    type: RuntimeDefault
```

Do not guess a UID for an unknown image. Check its documented user or inspect it first. `nginxinc/nginx-unprivileged` commonly uses a non-root account and listens on an unprivileged port, but the exact tag may differ.

Also remove or correct prohibited settings if present:

```yaml
hostNetwork: false
hostPID: false
hostIPC: false
```

```yaml
securityContext:
  privileged: false
  allowPrivilegeEscalation: false
  capabilities:
    drop: ["ALL"]
```

Restricted policy also limits `hostPath`, host ports, unsafe sysctls, SELinux options, AppArmor overrides, and volume types. Use the server error and the current standard rather than adding unrelated changes.

## Apply and verify

```bash
kubectl apply --dry-run=server -f /home/candidate/nginx-unprivileged.yaml
kubectl apply -f /home/candidate/nginx-unprivileged.yaml
kubectl rollout status deployment/<deployment-name> -n confidential
kubectl get pods -n confidential
```

Inspect the effective settings:

```bash
kubectl get deployment <deployment-name> -n confidential -o yaml
POD=$(kubectl get pods -n confidential -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n confidential "$POD" -- id
```

Expected: the dry-run succeeds, the rollout completes, and the process UID is non-zero.

## Sources

- [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [Pod Security Admission](https://kubernetes.io/docs/concepts/security/pod-security-admission/)

---

[← Previous: Question 12](12-sbom-and-image-removal.md) · [Index](README.md) · [Next: Question 14 →](14-secure-docker-daemon.md)
