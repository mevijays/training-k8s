# Question 3: Configure ImagePolicyWebhook

## Objective

Complete `/etc/kubernetes/bouncer` so that kube-apiserver:

- enables `ImagePolicyWebhook`;
- loads the provided `AdmissionConfiguration`;
- denies image admission when the backend fails;
- calls `https://smooth-yak.local/review`;
- rejects the workload in `/vulnerable.yaml`.

## What this lab does and why

**What we are doing:** We are inserting an image-policy check into the API request path. Before a Pod is admitted, kube-apiserver sends its container images to the external scanner and uses the scanner's response to allow or deny the workload. The configuration is fail-closed, so a scanner outage results in denial rather than bypass.

**Why it matters:** Kubernetes normally accepts an image reference without deciding whether the image is vulnerable or approved. An admission policy prevents known-bad images from entering the cluster, and fail-closed behavior prevents attackers or outages from silently disabling that protection.

**Objective summary:** After configuration, every new workload image is reviewed by the supplied HTTPS backend and vulnerable images, including the test resource, are denied.

## Concept and theory

- **Admission control position:** Admission runs after a request is authenticated and authorized but before the object is persisted. Validating admission can accept or reject an object but cannot rewrite it. Read operations such as `get`, `list`, and `watch` bypass admission.
- **ImagePolicyWebhook:** This built-in validating plugin extracts images from Pod containers, init containers, and ephemeral containers, then sends an `ImageReview` to an external service. A controller workload such as a Deployment is effectively checked when its controller creates Pods.
- **Two-layer configuration:** `--enable-admission-plugins` activates the plugin. `--admission-control-config-file` points to an `AdmissionConfiguration`, which in turn points to the image-policy settings and backend kubeconfig. Every referenced host path must also be visible inside the API-server container.
- **Fail-open vs. fail-closed:** `defaultAllow: true` admits an image when the scanner cannot answer, preserving availability but weakening enforcement. `defaultAllow: false` denies on backend failure, preserving the security boundary at the cost of blocking new workload admission during an outage.
- **Webhook TLS:** The API server must authenticate the HTTPS endpoint using a trusted CA. If mutual TLS is configured, it also presents its client certificate and key. DNS name, server certificate SANs, CA trust, and file mounts must all agree.

## Discover the supplied files

```bash
sudo find /etc/kubernetes/bouncer -maxdepth 2 -type f -print
sudo grep -RniE 'AdmissionConfiguration|ImagePolicyWebhook|defaultAllow|server:' \
  /etc/kubernetes/bouncer
```

Do not invent certificate paths. Reuse the CA, client certificate, and client key supplied in that directory.

## Admission configuration

The file referenced by kube-apiserver should contain the equivalent of:

```yaml
apiVersion: apiserver.config.k8s.io/v1
kind: AdmissionConfiguration
plugins:
- name: ImagePolicyWebhook
  path: image-policy.yaml
```

If `path` is relative, it is resolved relative to the admission configuration file. The referenced `image-policy.yaml` should contain:

```yaml
imagePolicy:
  kubeConfigFile: /etc/kubernetes/bouncer/backend-kubeconfig.yaml
  allowTTL: 50
  denyTTL: 50
  retryBackoff: 500
  defaultAllow: false
```

`defaultAllow: false` creates fail-closed behavior.

## Backend kubeconfig

Complete the existing kubeconfig, preserving its supplied certificate settings:

```yaml
apiVersion: v1
kind: Config
clusters:
- name: image-review
  cluster:
    certificate-authority: /etc/kubernetes/bouncer/ca.crt
    server: https://smooth-yak.local/review
users:
- name: apiserver
  user:
    client-certificate: /etc/kubernetes/bouncer/client.crt
    client-key: /etc/kubernetes/bouncer/client.key
contexts:
- name: image-review
  context:
    cluster: image-review
    user: apiserver
current-context: image-review
```

Use the filenames actually supplied by the lab.

## Configure kube-apiserver

Back up the manifest outside its watched directory, then edit it:

```bash
sudo mkdir -p /root/cks-backup
sudo cp -a /etc/kubernetes/manifests/kube-apiserver.yaml /root/cks-backup/q3-kube-apiserver.yaml
sudo vi /etc/kubernetes/manifests/kube-apiserver.yaml
```

Add or merge these command flags:

```yaml
- --enable-admission-plugins=ImagePolicyWebhook
- --admission-control-config-file=/etc/kubernetes/bouncer/admission-config.yaml
- --runtime-config=imagepolicy.k8s.io/v1alpha1=true
```

If `--enable-admission-plugins` already exists, append `ImagePolicyWebhook` to the existing list.

Mount the host directory into the API-server container:

```yaml
volumeMounts:
- name: bouncer
  mountPath: /etc/kubernetes/bouncer
  readOnly: true
```

```yaml
volumes:
- name: bouncer
  hostPath:
    path: /etc/kubernetes/bouncer
    type: Directory
```

## Test

```bash
export KUBECONFIG=/etc/kubernetes/admin.conf
until kubectl get --raw=/readyz >/dev/null 2>&1; do sleep 2; done

kubectl apply -f /vulnerable.yaml
```

Expected: the API server rejects the resource with an image-policy denial. A timeout or connection error combined with rejection also proves fail-closed behavior, but verify DNS, certificates, and the endpoint if the intended scanner should be reachable.

Troubleshoot with:

```bash
sudo crictl ps --name kube-apiserver
sudo crictl logs "$(sudo crictl ps --name kube-apiserver -q | head -1)" | tail -100
getent hosts smooth-yak.local
```

## Source

- [ImagePolicyWebhook admission controller](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/#imagepolicywebhook)

---

[← Previous: Question 2](02-api-server-node-rbac-noderestriction.md) · [Index](README.md) · [Next: Question 4 →](04-manifest-and-dockerfile-hardening.md)
