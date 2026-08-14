# Question 4: Harden a Deployment Manifest and Dockerfile

## Objective

Inspect the supplied Kubernetes Deployment and Dockerfile, identify one prominent security or best-practice problem in each file, and make the smallest correct change that removes each issue.

## What this lab does and why

**What we are doing:** We are reviewing security at two layers. The Deployment controls the privileges and isolation applied when a container runs, while the Dockerfile controls how the image is built, what it contains, and which user starts by default.

**Why it matters:** A secure runtime manifest cannot fully compensate for an unsafe image, and a well-built image can still become dangerous when Kubernetes grants it excessive privileges. Reviewing both files catches risks such as privileged execution, root users, unpinned images, embedded secrets, and unnecessary capabilities.

**Objective summary:** Make one evidence-based correction in each supplied file, validate both results, and avoid unrelated changes that could break the application.

## Concept and theory

- **Build-time and runtime security:** A Dockerfile defines image layers, installed software, copied files, and the default process identity. A Deployment defines how Kubernetes runs that image, including privileges, capabilities, volumes, networking, and security context. Both layers contribute to the final attack surface.
- **Least privilege:** Containers should receive only the permissions necessary for their function. Settings such as `privileged: true`, added capabilities, host namespaces, or root execution expand what a compromised process can reach.
- **Image identity:** A mutable tag such as `latest` can point to different content over time. A version tag improves repeatability, while a digest identifies exact immutable image content. Pinning does not prove an image is safe, but it makes the deployed artifact auditable.
- **Dockerfile users:** The last effective `USER` instruction determines the image's default UID or username. Kubernetes can override it with `runAsUser`, but building the image to run non-root provides a safer default outside Kubernetes as well.
- **Minimal correction principle:** Security hardening must preserve application behavior. When a task asks for one field, first prove which field is the prominent violation and change only that field rather than applying a generic hardening template blindly.

## Important limitation

The question does not include the contents of the two files, so there is no responsible way to name the exact two bad fields in advance. Inspect them and change only the prominent issue in each file.

## Inspect the files

```bash
cd /home/candidate/subtle-bee
nl -ba deployment.yaml
nl -ba Dockerfile

kubectl apply --dry-run=server -f deployment.yaml
```

Look for high-impact issues before style issues.

### Deployment checklist

```bash
grep -nE \
  'privileged:|allowPrivilegeEscalation:|runAsUser:|runAsNonRoot:|hostNetwork:|hostPID:|hostIPC:|hostPath:|capabilities:|seccompProfile:|image:' \
  deployment.yaml
```

Common one-field remediations include:

```yaml
securityContext:
  privileged: false
```

or:

```yaml
securityContext:
  allowPrivilegeEscalation: false
```

or replacing an unpinned image:

```yaml
image: example/app@sha256:<trusted-digest>
```

Do not blindly add every possible field when the question asks for one correction. Identify the explicit outlier.

### Dockerfile checklist

```bash
grep -nE '^(FROM|USER|ADD|COPY|RUN|EXPOSE)' Dockerfile
```

Common prominent issues:

- no `USER`, or `USER root`;
- `FROM image:latest` instead of a pinned release or digest;
- `ADD` of a remote URL when `COPY` is sufficient;
- secrets embedded in `ENV`, `ARG`, or `RUN`;
- unnecessary package installation or broad permissions such as `chmod 777`.

A representative non-root correction is:

```dockerfile
RUN addgroup --system app && adduser --system --ingroup app app
USER app
```

The exact account-creation syntax depends on the base image.

## Reproducible practice example

Create a disposable example outside the provided exam path with this bad Deployment fragment:

```yaml
containers:
- name: app
  image: nginx:1.27
  securityContext:
    privileged: true
```

Change only `privileged: true` to `privileged: false`, then validate:

```bash
kubectl apply --dry-run=server -f deployment.yaml
kubectl diff -f deployment.yaml
kubectl apply -f deployment.yaml
```

For a Dockerfile containing `USER root`, create a dedicated user and finish with `USER app`. Build and inspect:

```bash
docker build -t subtle-bee:test .
docker image inspect subtle-bee:test --format '{{.Config.User}}'
```

Expected: a non-root user name or numeric UID.

## Verify the deployed result

```bash
kubectl get deployment -A
kubectl get deployment <name> -n <namespace> -o yaml
kubectl get pods -n <namespace>
```

## Sources

- [Kubernetes security contexts](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/)
- [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)

---

[← Previous: Question 3](03-image-policy-webhook.md) · [Index](README.md) · [Next: Question 5 →](05-detect-devmem-access.md)
