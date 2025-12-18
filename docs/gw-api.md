# New kubernetes gateway api based ingress.

1. Install CRDs

```bash
kubectl kustomize "https://github.com/nginx/nginx-gateway-fabric/config/crd/gateway-api/standard?ref=v2.2.2" \
  | kubectl apply -f -
customresourcedefinition.apiextensions.k8s.io/gatewayclasses.gateway.networking.k8s.io created
customresourcedefinition.apiextensions.k8s.io/gateways.gateway.networking.k8s.io created
customresourcedefinition.apiextensions.k8s.io/grpcroutes.gateway.networking.k8s.io created
customresourcedefinition.apiextensions.k8s.io/httproutes.gateway.networking.k8s.io created
customresourcedefinition.apiextensions.k8s.io/referencegrants.gateway.networking.k8s.io created

```
2. Install NGF ( nginx gateway fabric controller)
```bash
$ kubectl apply --server-side -f https://raw.githubusercontent.com/nginx/nginx-gateway-fabric/v2.2.2/deploy/crds.yaml
customresourcedefinition.apiextensions.k8s.io/clientsettingspolicies.gateway.nginx.org serverside-applied
customresourcedefinition.apiextensions.k8s.io/nginxgateways.gateway.nginx.org serverside-applied
customresourcedefinition.apiextensions.k8s.io/nginxproxies.gateway.nginx.org serverside-applied
customresourcedefinition.apiextensions.k8s.io/observabilitypolicies.gateway.nginx.org serverside-applied
customresourcedefinition.apiextensions.k8s.io/snippetsfilters.gateway.nginx.org serverside-applied
customresourcedefinition.apiextensions.k8s.io/upstreamsettingspolicies.gateway.nginx.org serverside-applied

$ apply -f https://raw.githubusercontent.com/nginx/nginx-gateway-fabric/v2.2.2/deploy/default/deploy.yaml
namespace/nginx-gateway created
serviceaccount/nginx-gateway created
serviceaccount/nginx-gateway-cert-generator created
role.rbac.authorization.k8s.io/nginx-gateway-cert-generator created
clusterrole.rbac.authorization.k8s.io/nginx-gateway created
rolebinding.rbac.authorization.k8s.io/nginx-gateway-cert-generator created
clusterrolebinding.rbac.authorization.k8s.io/nginx-gateway created
service/nginx-gateway created
deployment.apps/nginx-gateway created
job.batch/nginx-gateway-cert-generator created
gatewayclass.gateway.networking.k8s.io/nginx created
nginxgateway.gateway.nginx.org/nginx-gateway-config created
nginxproxy.gateway.nginx.org/nginx-gateway-proxy-config created
```
3. Verify the controller pod is running.
```bash
 kubectl get pods -n nginx-gateway
NAME                             READY   STATUS    RESTARTS   AGE
nginx-gateway-7ff794846b-wfhcl   1/1     Running   0          54s
```
4. Deploy a sample app (2 services)
This is a simple “coffee/tea” demo (feel free to replace with your own app/services):

```bash
cat <<'EOF' > cafe.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: coffee
spec:
  replicas: 1
  selector:
    matchLabels:
      app: coffee
  template:
    metadata:
      labels:
        app: coffee
    spec:
      containers:
      - name: coffee
        image: nginxdemos/nginx-hello:plain-text
        ports:
        - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: coffee
spec:
  selector:
    app: coffee
  ports:
  - name: http
    port: 80
    targetPort: 8080
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tea
spec:
  replicas: 1
  selector:
    matchLabels:
      app: tea
  template:
    metadata:
      labels:
        app: tea
    spec:
      containers:
      - name: tea
        image: nginxdemos/nginx-hello:plain-text
        ports:
        - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: tea
spec:
  selector:
    app: tea
  ports:
  - name: http
    port: 80
    targetPort: 8080
EOF

kubectl apply -f cafe.yaml
```
5. Create a Gateway

```bash
cat <<'EOF' > gateway.yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: cafe-gw
spec:
  gatewayClassName: nginx
  listeners:
  - name: http
    port: 80
    protocol: HTTP
EOF

kubectl apply -f gateway.yaml
```
6. Check it
```bash
kubectl get gateway cafe-gw
kubectl get svc
kubectl get deploy
```
7. Create HTTPRoutes now
```bash
cat <<'EOF' > routes.yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: coffee-route
spec:
  parentRefs:
  - name: cafe-gw
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: /coffee
    backendRefs:
    - name: coffee
      port: 80
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: tea-route
spec:
  parentRefs:
  - name: cafe-gw
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: /tea
    backendRefs:
    - name: tea
      port: 80
EOF

kubectl apply -f routes.yaml
```
