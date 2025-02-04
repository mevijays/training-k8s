### Istio lab setup and exam practice.
- install docker
- install kind
```bash
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.25.0/kind-linux-amd64 -k
chmod +x kind 
sudo mv kind /usr/local/bin/
kind create cluster -n kind
```
When you done with lab just delete the cluster
```bash
kind delete cluster -n kind
```
Install kubectl 
```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
```
get the nodes and ips 
```bash
kubectl get node -o wide
```
install metallb
```bash
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.14.8/config/manifests/metallb-native.yaml
```
metallb ip range config 
```yaml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: kind
  namespace: metallb-system
spec:
  addresses:
  - 172.18.0.200-172.18.0.250

---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: kind
  namespace: metallb-system
spec:
  ipAddressPools:
  - kind  
```
Apply it 
```bash
kubectl apply -f lb-config.yaml
```
Download the istio release (https://github.com/istio/istio/releases)
```bash
wget https://github.com/istio/istio/releases/download/1.18.2/istio-1.18.2-linux-amd64.tar.gz
tar xvf istio-1.18.2-linux-amd64.tar.gz
mv istio-1.18.2 istio
mv istio/bin/istioctl /usr/local/bin/
```
### Exam question-1

Write istio operator manifest for :- 
- default profile
- enable egressgateway as name system-egress
- disabledefault ingress gateway
- configure the pilot to use 200m cpu and 161 of memory (https://istio.io/latest/docs/reference/config/istio.operator.v1alpha1/)

```yaml
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
spec:
  profile: default
  components:
    egressGateways:
    - name: system-egress
      enabled: true
    ingressGateways:
    - name: istio-ingressgateway
      enabled: false 
    pilot:
      k8s:
        resources:
          requests:
            cpu: "200m"
            memory: "161Mi"
```
Installing istio on kind
```bash
istioctl install -f istio-install.yaml 
press y+Enter for default profile
```
### Exam question2
1. destination rule for two subsets with custom label (https://istio.io/latest/docs/reference/config/networking/destination-rule/)
2. Use bookinfo sample ``destination-rule-reviews.yaml`` & ``virtual-service-details-v2.yaml``

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: customers-dr
spec:
  host: customers-demo.customer.svc.cluster.local # Replace with the actual service name
  subsets:
  - name: demo
    labels:
      env: demo
  - name: stage
    labels:
      env: stage
```
2- virtual service creation to distribute traffic between 2 workloads dr and stage (https://istio.io/latest/docs/reference/config/networking/virtual-service/)
```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: customers-vs
spec:
  hosts:
  - customers.customer.svc.cluster.local
  http:
  - route:
    - destination:
        host: customers.customer.svc.cluster.local 
        subset: demo
      weight: 15
    - destination:
        host: customers.customer.svc.cluster.local
        subset: stage
      weight: 85
```

### Exam question3

gateway creationfor virtual service using ingressgateway  (https://istio.io/latest/docs/tasks/traffic-management/ingress/ingress-control/)
first deploy a default profile istio with ingressgateway as outof the box. - metallb is required as given above.
Deploy a workloads - open the httpbin.yaml and change the desired name for deployment if you want.  ``Use HTTPbin for this yaml and file is httpbin-gateway.yaml``
```bash
kubectl create ns mondo-ns
kubectl apply -f istio/samples/httpbin/httpbin.yaml -n mondons
```
```yaml
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: mondo-gateway
  namespace: mondo-ns
spec:
  selector:
    istio: ingressgateway  # Selects the default Istio ingress gateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - mondo.example.com

---
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: mondo-vs
  namespace: mondo-ns
spec:
  hosts:
  - mondo.example.com
  gateways:
  - mondo-gateway 
  http:
  - route:
    - destination:
        host: mondo.mondo-ns.svc.cluster.local  # Replace with the actual service name for your mondo workloads
```
### Exam question4

ensure the namespace automatically inject sidecar proxy istio envoy
```bash
kubectl label namespace default istio-injection=enabled
kubectl get ns --show-labels
```
### Exam question5
Create a gateway resource of istio named oscorp-gateway in ns oscorp-prod as:
1. All virtual services from the `oscorp-prod` namespace should be able to bind to the gateway. Only virtual services with the hostname `oscorp.example.com` from the `oscorp-dev` namespace should be able to bind to the gateway.

2. Use the gateway selector `istio: ingressgateway`.

3. Port is set to `80` and protocol to `HTTP`. ``for this file creation in exam use httpbin httpbin-gateway.yaml, remove destination rule and iterate Gateway``

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: oscorp-gateway
  namespace: oscorp-prod
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "*"
---
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: oscorp-gateway
  namespace: oscorp-dev
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - oscorp.example.com
```
```yaml
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: oscorp-gateway
  namespace: oscorp-prod
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - oscorp.example.com
    tls:
      httpsRedirect: true
```
### Exam question6
Add an external service http://httpbin.org that you will be consuming through the APIs, to Istio's internal service mesh registry. The external service is accessible on host httpban.org using the HTTP protocol and port 80.

Additionally, inject a 5-second delay for all requests to httpbin.org.

Create all required resources in the httpbin namespace.
```yaml
# httpbin-gateway.yaml
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: httpbin-gateway
  namespace: httpbin
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - httpbin.org

---
# httpbin-virtual-service.yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: httpbin
  namespace: httpbin
spec:
  hosts:
  - httpbin.org
  http:
  - route:
    - destination:
        host: httpbin.org 
        port:
          number: 80
  fault:
    delay:
      fixedDelay: 5s
      percentage:
        value: 100

---
# httpbin-service-entry.yaml
apiVersion: networking.istio.io/v1alpha3
kind: ServiceEntry
metadata:
  name: httpbin-ext
  namespace: httpbin
spec:
  hosts:
  - httpbin.org
  ports:
  - number: 80
    name: http
    protocol: HTTP
  resolution: DNS
  location: MESH_EXTERNAL
```

### Exam Qeustion7
Two Deployments are running in the cyberdyne namespace:

- workload-v1

- workload-v2

Configure traffic routing through the public-gateway defined in the cyberdyne namespace using the host cyberdyne.example.com in the following manner

1. Incoming traffic through the public-gateway matching the URI prefix /api/headers is rewritten to /headers and routed to subset v2.

2. All other traffic through the public-gateway is routed to the vi subset.

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: cyberdyne-vs
  namespace: cyberdyne
spec:
  hosts:
  - cyberdyne.example.com
  gateways:
  - public-gateway
  http:
  - match:
    - uri:
        prefix: /api/headers
    rewrite:
      uri: /headers 
    route:
    - destination:
        host: workload-v2.cyberdyne.svc.cluster.local  # Assuming workload-v2 is the service name for v2
        subset: v2
  - route:
    - destination:
        host: workload-v1.cyberdyne.svc.cluster.local  # Assuming workload-v1 is the service name for v1
        subset: v1
``` 

### Exam Question8

Create a namespace-wide Sidecar resource called default in the salera-prog namespace

Configure the Sidecar resource so that it enables egress to workloads in namespaces istio-system, salera-dev and salera-prod.
```yaml
apiVersion: networking.istio.io/v1alpha3
kind: Sidecar
metadata:
  name: default
  namespace: salera-prog
spec:
  egress:
  - hosts:
    - "istio-system/*"
    - "salera-dev/*"
    - "salera-prod/*"
```

### Exam question 9
Create and configure Istio resources required to route all traffic destined for http://wikipedia.org through the default istio egress gateway running in the sstio-system namespace

Make sure you use the following:

- Use istio egressgateway as the egress gateway selector

- Use ServiceEntry host wikipedia.org and HTTP protocol

- Gateway resource has to be named wikipedia-egress

Use fully-qualified host names when referring to host names

All resources have to be created in the namespace called egress.

```yaml
# wikipedia-egress-gateway.yaml
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: wikipedia-egress
  namespace: egress
spec:
  selector:
    istio: egressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - wikipedia.org

---
# wikipedia-service-entry.yaml
apiVersion: networking.istio.io/v1alpha3
kind: ServiceEntry
metadata:
  name: wikipedia-ext
  namespace: egress
spec:
  hosts:
  - wikipedia.org
  ports:
  - number: 80
    name: http
    protocol: HTTP
  resolution: DNS
  location: MESH_EXTERNAL

---
# wikipedia-virtual-service.yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: wikipedia-vs
  namespace: egress
spec:
  hosts:
  - wikipedia.org
  http:
  - route:
    - destination:
        host: wikipedia.org
        port:
          number: 80

```

### Exam Question 10
**Referance** (https://istio.io/latest/docs/reference/config/networking/virtual-service/)
In the namespace duck-tales, create a Virtual Service named controller-vs to route traffic for the host controller.duck-tales.svc.cluster.local.

Route the requests to the same destination (backed by the workload named controller), and set the timeout to 2 seconds.

Use fully-qualified domain names when referencing any workloads or services

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: controller-vs
  namespace: duck-tales
spec:
  hosts:
  - controller.duck-tales.svc.cluster.local
  http:
  - route:
    - destination:
        host: controller.duck-tales.svc.cluster.local 
  timeout: 2s
```

### Exam Question11
 (https://istio.io/latest/docs/reference/config/networking/virtual-service/)
In the namespace ecorp-prod, create a Virtual Service to route all traffic for the host robot.ecorp-prod.svc.cluster.local to subset vi

In addition, configure the route with 5 retry attempts, and a per-try timeout of 1 second.

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: robot-vs
  namespace: ecorp-prod
spec:
  hosts:
  - robot.ecorp-prod.svc.cluster.local
  http:
  - route:
    - destination:
        host: robot.ecorp-prod.svc.cluster.local
        subset: v1
    retries:
      attempts: 5
      perTryTimeout: 1s
```
### Exam question 12 
(https://istio.io/latest/docs/reference/config/networking/destination-rule/)
Configure a circuit breaker and outlier detection in a destination rule co-destination for the host backend.cb.svc.cluster.local in the namespace called co.

Use the following configuration:

 connection pool size (HTTP1): 50

 maximum number of concurrent HTTP2 request: 100 maximum number of requests per connection: 5

number of consecutive 5xx errors: 5

host scanning interval: 3 minutes

ejection time: 8 minutes
```yaml

apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: co-destination
  namespace: co
spec:
  host: backend.cb.svc.cluster.local
  trafficPolicy:
    connectionPool:
      http:
        http1MaxPendingRequests: 50  # HTTP1 connection pool size
        maxRequestsPerConnection: 5   # Maximum requests per connection
      tcp: 
        maxConnections: 100         # Maximum concurrent HTTP2 requests (TCP connections)
    outlierDetection:
      consecutiveErrors: 5          # Number of consecutive 5xx errors
      interval: 3m                  # Host scanning interval
      baseEjectionTime: 8m          # Ejection time
```

### Exam question 13 
 (https://istio.io/latest/docs/reference/config/security/peer_authentication/)
Create a resource called default in the namespace policy-1 that configures strict mTLS for workloads with the label version: vi set

```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: policy-1
spec:
  selector:
    matchLabels:
      version: v1
  mtls:
    mode: STRICT
```

### Exam question 14 
(https://istio.io/latest/docs/reference/config/security/authorization-policy/)
A pair of apps, sleep and helloworld, are running in namespace xyz

Make an HTTP GET call to the helloworld endpoint from the sleep pod:

kubectl exec -n xyz deploy/sleepcurl -s helloworld:5000/hello

"allow-nothing" policy in place for the namespace, causing the above call to return the error message RBAC: access denied.

Here is your checklist:

An Your task is to author an authorization policy named "helloworld-policy" that allows sleep (and only sleep) to call helloworld, for HTTP GET operations.

- The authorization policy should be named "helloworld-policy". • The authorization policy should apply only to helloworld workloads.

Requests should be allowed only if the call is from sleep workloads. The

only operations allowed should HTTP GET methods.

You can verify that your authorization policy works correctly by repeating the above call to helloworld endpoint.

```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: helloworld-policy
  namespace: xyz
spec:
  selector:
    matchLabels:
      app: helloworld  # Apply this policy to the helloworld workload
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/xyz/sa/sleep"]  # Allow requests from the sleep workload
    to:
    - operation:
        methods: ["GET"]  # Allow only GET requests
```

### Exam question15 
(https://istio.io/latest/docs/reference/config/security/authorization-policy/)

Create an authorization policy named allow get in the namespace policy-3 that allows all GET requests sent to the /get path from the workloads in the default namespace to all workloads running in the policy-3 namespace.
```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: allow-get
  namespace: policy-3
spec:
  selector:
    matchLabels:
      app: "*" # Apply this policy to all workloads in the policy-3 namespace
  rules:
  - from:
    - source:
        namespaces: ["default"] # Allow requests from the default namespace
    to:
    - operation:
        paths: ["/get"] # Allow requests to the /get path
        methods: ["GET"] # Allow only GET requests
```

### EXAM Question16  
(https://istio.io/latest/docs/reference/config/networking/sidecar/)
Update and deploy the provided Sidecar below so that it applies to all workloads in the discovery namespace that have the label version: vi ser
```yaml
apiVersion: networking.istio.io/v1alpha3 # Corrected API version
kind: Sidecar
metadata:
  name: scoped-to-namespace
  namespace: discovery
spec:
  workloadSelector:  # Add workloadSelector to target specific workloads
    labels:
      version: v1
  egress:
  - hosts:
    - "istio-system/*"
```

### Exam question17
The workload httpbin is running in namespace troubleshoot-1, along with a client named sleep.

Calling the service from the sleep client with:
```bash
kubectl exec -n troubleshoot-1 deploy/sleep - curl --head httpbin:8000/headers
```
Results in the following error:

`curl: (56) Recv failure: Connection reset by peer command terminated with exit code 56`

Resolve this issue. Make the call succeed. Do not modify any security polites that are already in place.

Possible causes:
Port is not correct in service and deployment 
```
check : kubectl exec -n troubleshoot-1 deploy/sleep - curl --head httpbin:8000/headers
kubectl get svc -n troubleshoot-1 httpbin
kubectl get deploy -n troubleshoot-1 httpbin -o yaml
Check DNS: kubectl exec -n troubleshoot-1 deploy/sleep - nslookup httpbin
Restart pod:
check if istio sidecar is injected : kubectl get pod -n troubleshoot-1 -l app=httpbin -o yaml | grep istio-proxy
```

### Exam question18
Which mechanism is used in Istio to enable request-level authentication?

``Select One:``

- Istio doesn't support request-level authentication

- JSON Web Tokens langle JWTs rangle

- MTLS

- SDS

**Answer is:** JSON web token

### Exam Question19

When installing multiple Istio control plane versions on the same Kubernetes cluster, which of the following statements are true?

``Select One:``

Each Istio version must be installed to a distinct namespace.

- A'revision' must be set when installing Istio, creating a designation for that version.

- Istio does not support running multiple versions on the same Kubernetes cluster.

- The Istio version is automatically inferred and used to differentiate each version.   
  
**Answer:** A 'revision' must be set when installing Istio, creating a designation for that version.

### Exam question20
What is the to field in AuthorizationPolicy used for?

``Select One:``

- To specify the operation of the request

- To specify the target workload of the request

- To specify the destination service of the request

- To specify the target and conditions of the request

**Answer:**  To specify the target and conditions of the request.

### Exam Question:21
Setting the PERMISSIVE mode in PeerAuthentication resource allows sidecars to accept both mTLS and non-mTLS traffic.

``Select One:``

True

False

**Answer:** True

### Exam question:22
What are Istio's WorkloadGroup and workloadEntry resources used for?

``Select One:``

- The resources create corresponding Deployments (WorkloadGroup) and Pods (WorkloadEntry) for VM workloads

- The resources tell Istio how to configure the mesh for VM workloads

- The resources trigger the bootstrap process for the VM workloads

- The resources generate ConfigMap and Secret resources that can be copied to the VMs to connect back to the mesh

**Answer:** The resources tell Istio how to configure the mesh for VM workloads.
