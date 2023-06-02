# Working with kind cluster
## KIND kubernetes cluster lab setup.
**Kind** is a very good option for those who are just starting with kubernetes and dont have suffecient enough resources available. KIND i.e. ***kubernetes in docker*** is a binary file using which and docker you can create multiple node k8s cluster, all in docker container.

 **Steps**
 - Docker installation.
 - Kind setup.
 - Kind config file.
 - Setup kind cluster
 ### **Docker Installation**
- Docker setup steps based on your linux flavor can be find in here. 

1. Steps for Ubuntu [Click here](https://docs.docker.com/engine/install/ubuntu/)
1. Steps for Fedora [Click here](https://docs.docker.com/engine/install/fedora/)
1. Steps for RHEL/CentOS [Click here](https://docs.docker.com/engine/install/rhel/)

- One script install is also possible here-
[ Script install ](../dockersetup.md)

### **Kind Setup**

Download and setup kind binary.
```
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.19.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
```
Validate the version.

```
$ kind version

 kind v0.11.1 go1.16.4 linux/amd64
```
### **Kind config file**
Preapre a file with required configuration. Bellow config is a sample which usage extra port mapping for ingress controller.

File content

```
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
    extraPortMappings:
    - containerPort: 80
      hostPort: 80
      listenAddress: "0.0.0.0"
      protocol: TCP
    - containerPort: 443
      hostPort: 443
      listenAddress: "0.0.0.0"
      protocol: TCP
    kubeadmConfigPatches:
    - |
      kind: InitConfiguration
      nodeRegistration:
        kubeletExtraArgs:
          node-labels: "ingress-ready=true"
networking:
  kubeProxyMode: "ipvs"
```
File can be found [here](kind-config.yaml)

### **Setup Kind cluster**

You can now setup kind cluster by using bellow command.

```
kind create cluster --name kind --config kind-config.yaml
```

check the cluster status

```
kind get clusters

docker ps
```
To manage the cluster you need kubectl command. Get it setup with this process defined-
```
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
```
Now check kind status with kubectl command.
```
kubectl get node
```
## Setup metric
```
kubectl apply -f https://raw.githubusercontent.com/sharmavijay86/sharmavijay86.github.io/master/blog/k8ssetup/components.yaml
```
## Setup Ingress

1. Install nginx ingress

```
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
```
Above is patched version for mainly kind. Please note we have already exposed port 80 and 443 in config yaml file so 80 would be listening on kind host node at 127.0.0.1:80 and 127.0.0.1:443

2. Setup sample foo bar ingres.

```
kubectl apply -f https://kind.sigs.k8s.io/examples/ingress/usage.yaml
```
3. check it .

```
curl localhost/foo
curl localhost/bar
```
Above is working means we have setup corectly our kind cluster along with nginx ingress controller.

## how to expose API for remote access
You see we have exposed nodeport to host machine NIC interface, that is why you can access ingresson kind host ip address. If you wish to access this k8s server from remote machine, then you need api server also to expose on hostport. 

This just need a configuration line to put in networking section.

```
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
    extraPortMappings:
    - containerPort: 80
      hostPort: 80
      listenAddress: "0.0.0.0"
      protocol: TCP
    - containerPort: 443
      hostPort: 443
      listenAddress: "0.0.0.0"
      protocol: TCP
    kubeadmConfigPatches:
    - |
      kind: InitConfiguration
      nodeRegistration:
        kubeletExtraArgs:
          node-labels: "ingress-ready=true"
networking:
  kubeProxyMode: "ipvs"
  apiServerAddress: "192.168.56.101"
  apiServerPort: 6443

```

- Check the services nginx ingress.

```
kubectl create deploy webapp --image=nginx:1.22
kubectl expose deploy webapp --port=8080 --target-port=80
kubectl create ingress webapp --class=nginx --rule="abc.lan/*=webappp:80"
```
Now make an entry in hosts file for abc.lan and check in browser.

### Ingress with config map in nginx:1.22

```
apiVersion: v1
data:
  index.html: |
    <h1>Hello from testing CM mount</h1>
kind: ConfigMap
metadata:
  creationTimestamp: null
  name: foo
---
apiVersion: apps/v1
kind: Deployment
metadata:
  creationTimestamp: null
  labels:
    app: webcm
  name: webcm
spec:
  replicas: 3
  selector:
    matchLabels:
      app: webcm
  strategy: {}
  template:
    metadata:
      creationTimestamp: null
      labels:
        app: webcm
    spec:
      containers:
      - image: nginx:alpine
        name: nginx
        volumeMounts:
          - name: foo
            mountPath: "/usr/share/nginx/html/"
      volumes:
      - name: foo
        configMap:
           name: foo
---
apiVersion: v1
kind: Service
metadata:
  creationTimestamp: null
  labels:
    app: webcm
  name: webcm
spec:
  ports:
  - port: 80
    protocol: TCP
    targetPort: 80
  selector:
    app: webcm
status:
  loadBalancer: {}
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  creationTimestamp: null
  name: webcm
spec:
  ingressClassName: nginx
  rules:
  - host: ckatcswebcm.lab
    http:
      paths:
      - backend:
          service:
            name: webcm
            port:
              number: 80
        path: /
        pathType: Prefix
status:
  loadBalancer: {}
```
### ETCD backup and restore
[ETCD Backup and restore process](etcd-bkp-restore.md)

### Setup Helm binary
```
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
sudo bash get_helm.sh
```

### Prometheus

```
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add stable https://charts.helm.sh/stable
helm install prometheus prometheus-community/kube-prometheus-stack
kubectl port-forward deployment/prometheus-grafana 3000
```

### Setup Credentials

username: admin   
password: prom-operator

### Cert manager setup

```
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.12.1/cert-manager.yaml
```

### Issuer    
```
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: selfsigned-cluster-issuer
spec:
  selfSigned: {}
```
