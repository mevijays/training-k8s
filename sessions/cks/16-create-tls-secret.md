# Question 16: Create a TLS Secret

## Objective

Create Secret `clever-cactus` in namespace `clever-cactus` from:

- certificate: `/home/candidate/clever-cactus/web.k8s.local.crt`;
- private key: `/home/candidate/clever-cactus/web.k8s.local.key`.

The existing Deployment already references this Secret.

## What this lab does and why

**What we are doing:** We are validating that the supplied PEM certificate and private key form a matching pair, then storing them in a Kubernetes Secret of type `kubernetes.io/tls`. Kubernetes assigns the conventional `tls.crt` and `tls.key` data keys expected by TLS-aware workloads.

**Why it matters:** A mismatched or malformed key pair prevents the application from starting or serving TLS. Creating the correct typed Secret lets the existing Deployment consume the files without embedding private-key material in a Pod specification or container image.

**Objective summary:** Produce the exact namespaced TLS Secret expected by the Deployment, confirm its type and keys, and verify the application becomes healthy without revealing the private key.

## Concept and theory

- **TLS key pair:** The certificate contains a public key and signed identity information, while the private key proves control of that identity during the TLS handshake. Their derived public keys must match or the server cannot use them together.
- **PEM encoding:** `kubectl create secret tls` expects a PEM-encoded certificate and corresponding unencrypted private key file. PEM uses recognizable header and footer lines around base64-encoded cryptographic data.
- **Typed Secret:** A Secret of type `kubernetes.io/tls` conventionally contains `tls.crt` and `tls.key`. The type communicates intent and lets tooling validate or discover the expected keys.
- **Namespace boundary:** Secrets are namespaced. A Pod can directly reference only a Secret in its own namespace, so both the Secret name and namespace must match the existing Deployment.
- **Storage caution:** Secret values are base64-encoded in the API object, not inherently encrypted by base64. Access should be restricted with RBAC, private keys should not be printed during verification, and production clusters should enable encryption at rest for Kubernetes Secrets.

## Inspect and validate the input

```bash
ls -l \
  /home/candidate/clever-cactus/web.k8s.local.crt \
  /home/candidate/clever-cactus/web.k8s.local.key

openssl x509 \
  -in /home/candidate/clever-cactus/web.k8s.local.crt \
  -noout -subject -issuer -dates

openssl pkey \
  -in /home/candidate/clever-cactus/web.k8s.local.key \
  -noout -check
```

Compare the public keys without printing private-key material:

```bash
openssl x509 \
  -in /home/candidate/clever-cactus/web.k8s.local.crt \
  -pubkey -noout \
  | openssl pkey -pubin -outform DER \
  | sha256sum

openssl pkey \
  -in /home/candidate/clever-cactus/web.k8s.local.key \
  -pubout -outform DER \
  | sha256sum
```

The hashes must match.

## Create the Secret

```bash
kubectl create secret tls clever-cactus \
  --namespace clever-cactus \
  --cert=/home/candidate/clever-cactus/web.k8s.local.crt \
  --key=/home/candidate/clever-cactus/web.k8s.local.key
```

For an idempotent practice command that updates an existing Secret:

```bash
kubectl create secret tls clever-cactus \
  --namespace clever-cactus \
  --cert=/home/candidate/clever-cactus/web.k8s.local.crt \
  --key=/home/candidate/clever-cactus/web.k8s.local.key \
  --dry-run=client -o yaml \
  | kubectl apply -f -
```

## Verify without revealing the Secret

```bash
kubectl get secret clever-cactus -n clever-cactus \
  -o jsonpath='{.type}{"\n"}'

kubectl get secret clever-cactus -n clever-cactus \
  -o jsonpath='{range $k,$v := .data}{$k}{"\n"}{end}'

kubectl rollout status deployment/clever-cactus -n clever-cactus
kubectl get pods -n clever-cactus
```

Expected:

```text
kubernetes.io/tls
tls.crt
tls.key
```

Do not print or decode `tls.key` during verification.

## Cleanup for a disposable lab only

```bash
kubectl delete secret clever-cactus -n clever-cactus
```

## Source

- [`kubectl create secret tls`](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_create/kubectl_create_secret_tls/)

---

[← Previous: Question 15](15-istio-strict-mtls.md) · [Index](README.md) · [Next: CKS lab index →](README.md)
