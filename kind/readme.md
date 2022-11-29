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
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.17.0/kind-linux-amd64
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

