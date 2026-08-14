# Question 9: TLS Ingress and HTTP-to-HTTPS Redirect

## Objective

Create an Ingress named `web` in namespace `prod` that:

- matches host `web.k8s.local`;
- routes every path to Service `web`;
- terminates TLS using Secret `web-cert`;
- redirects HTTP to HTTPS.

## What this lab does and why

**What we are doing:** We are defining host- and path-based routing from an Ingress controller to the existing Service. The controller presents the certificate stored in `web-cert`, terminates the TLS connection, and redirects plaintext HTTP clients to the encrypted HTTPS endpoint.

**Why it matters:** Ingress centralizes external web routing, but traffic remains exposed if HTTP is accepted without redirection or if TLS is misconfigured. Host matching prevents the route from unintentionally serving unrelated domains, and TLS protects credentials and application data while they cross the network.

**Objective summary:** Requests for `web.k8s.local` are encrypted, plaintext clients are redirected, and every path is delivered to the existing `web` Service.

## Concept and theory

- **Ingress API and controller:** An Ingress is desired routing configuration stored in Kubernetes. An Ingress controller watches those objects and configures an actual proxy or load balancer. Without a controller and matching IngressClass, creating the object alone does not route traffic.
- **Routing chain:** The client connects to the Ingress controller, which matches the HTTP host and path, then forwards the request to the selected Service port. The Service selects backend Pods and distributes traffic to their endpoints.
- **TLS termination:** The controller presents the certificate from the namespaced TLS Secret and decrypts the client connection. Traffic from the controller to the Service is separate and may be plaintext or encrypted depending on controller and backend configuration.
- **Host and certificate matching:** The requested hostname must match the Ingress rule and should appear in the certificate's SANs. TLS SNI helps the controller select a certificate, while the HTTP `Host` header selects the route.
- **Redirect behavior:** Kubernetes' Ingress specification defines TLS and routing but does not universally define HTTP-to-HTTPS redirection. Redirect annotations are interpreted by a specific controller, which is why the installed controller must be identified first.

## Inspect prerequisites

```bash
kubectl get service web -n prod -o yaml
kubectl get secret web-cert -n prod -o jsonpath='{.type}{"\n"}'
kubectl get ingressclass
```

The Secret type should be `kubernetes.io/tls`. Record the Service port:

```bash
kubectl get service web -n prod \
  -o jsonpath='{range .spec.ports[*]}{.name}{" "}{.port}{"\n"}{end}'
```

## Create the Ingress

Use the actual Service port in place of `<service-port>`. For ingress-nginx:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web
  namespace: prod
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - web.k8s.local
    secretName: web-cert
  rules:
  - host: web.k8s.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web
            port:
              number: <service-port>
```

If the Service exposes a named port, use this instead:

```yaml
port:
  name: http
```

Apply:

```bash
kubectl apply -f web-ingress.yaml
kubectl describe ingress web -n prod
```

Redirect annotations are controller-specific. The annotations above target ingress-nginx; use the installed controller's equivalent if the IngressClass is not nginx.

## Test

The pasted question's test command uses `web.ks.local`, which conflicts with the requested `web.k8s.local`. Configure and test the requested hostname.

```bash
INGRESS_IP=$(kubectl get ingress web -n prod -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

curl -I --resolve web.k8s.local:80:"$INGRESS_IP" \
  http://web.k8s.local/
```

Expected: a `301` or `308` redirect to HTTPS.

```bash
curl -kL --resolve web.k8s.local:80:"$INGRESS_IP" \
  --resolve web.k8s.local:443:"$INGRESS_IP" \
  http://web.k8s.local/
```

If local DNS already resolves the host:

```bash
curl -kL http://web.k8s.local/
```

## Source

- [Kubernetes Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/)

---

[← Previous: Question 8](08-network-policies.md) · [Index](README.md) · [Next: Question 10 →](10-projected-service-account-token.md)
