![Kubernetes](k8slogo.png)
# Kubernetes cluster lab with ubuntu 20.04

### Step to follow on all nodes

```
sudo apt-get update
sudo apt-get upgrade
```
To turn off swap space, if it is enabled 
```
sudo sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab
sudo swapoff -a
```
You have 2 diffrent CRI options to use:   
- containerd
- cri-o   

Bellow are steps to install either of one.   
### To install containerd.
```
sudo apt install containerd -y
```
### To install CRIO
```
sudo apt update
sudo apt install -y apt-transport-https ca-certificates curl gnupg2 software-properties-common
export OS_VERSION=xUbuntu_20.04
export CRIO_VERSION=1.23
curl -fsSL https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/$OS_VERSION/Release.key | sudo gpg --dearmor -o /usr/share/keyrings/libcontainers-archive-keyring.gpg
curl -fsSL https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable:/cri-o:/$CRIO_VERSION/$OS_VERSION/Release.key | sudo gpg --dearmor -o /usr/share/keyrings/libcontainers-crio-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/libcontainers-archive-keyring.gpg] https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/$OS_VERSION/ /" | sudo tee /etc/apt/sources.list.d/devel:kubic:libcontainers:stable.list
echo "deb [signed-by=/usr/share/keyrings/libcontainers-crio-archive-keyring.gpg] https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable:/cri-o:/$CRIO_VERSION/$OS_VERSION/ /" | sudo tee /etc/apt/sources.list.d/devel:kubic:libcontainers:stable:cri-o:$CRIO_VERSION.list
sudo apt update
sudo apt install -y cri-o cri-o-runc
sudo systemctl daemon-reload
sudo systemctl enable crio
sudo systemctl start crio
```
### Enable kube adm repository
```
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add
```

```
sudo apt-add-repository "deb http://apt.kubernetes.io/ kubernetes-xenial main"
```
If we want to install specific version of k8s, use bellow command. Just replace the version from 1.23.5-00 to other.
```
sudo apt install kubelet=1.23.5-00 kubeadm=1.23.5-00 kubectl=1.23.5-00 -y
```
For latest version, to install, use bellow.
```
sudo apt install kubelet kubeadm kubectl -y
```

```
sudo modprobe overlay
sudo modprobe br_netfilter
```
```
sudo tee /etc/sysctl.d/kubernetes.conf<<EOF
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
EOF
```
```
sudo sysctl --system
```

## Step on master nodes

We can initialize master node with difrent options:   
- Standard install with defined pod-cidr
```
sudo kubeadm init --pod-network-cidr=10.244.0.0/16
```
- To install with specific CRI socket, in case cri-o.
```
sudo kubeadm init --pod-network-cidr=10.244.0.0/16 --cri-socket unix:///var/run/crio/crio.sock
```

To enable the kubectl admin context.
``` 
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

## Join worker node ( step on worker node )

- With specific CRI
``` 
sudo kubeadm join 192.168.122.220:6443 --token gefqt9.oj3kcgubehofxbz8  --discovery-token-ca-cert-hash sha256:a79789ade9c95182522f55b1ab17e93cd6eac9c7eaf8b7b67a6c125bbb5f50ce  --cri-socket unix:///var/run/crio/crio.sock
```
- With standard option.
``` 
sudo kubeadm join 192.168.122.220:6443 --token gefqt9.oj3kcgubehofxbz8  --discovery-token-ca-cert-hash sha256:a79789ade9c95182522f55b1ab17e93cd6eac9c7eaf8b7b67a6c125bbb5f50ce  
```

## Deploy a pod network plugin ( on master node )
- Flannel install
``` 
kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
```
- Weavnet install
```
kubectl apply -f https://github.com/weaveworks/weave/releases/download/v2.8.1/weave-daemonset-k8s.yaml
```
 
 ## Setup of metal LB (Optional)
Apply deployment manifests-
```
kubectl get configmap kube-proxy -n kube-system -o yaml | sed -e "s/strictARP: false/strictARP: true/" | kubectl apply -f - -n kube-system
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.9.6/manifests/namespace.yaml
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.9.6/manifests/metallb.yaml
kubectl create secret generic -n metallb-system memberlist --from-literal=secretkey="$(openssl rand -base64 128)"
```
Create yaml for ip pool 
```
vim ip-pool.yaml
```
Apply the ip pool for LB. Create and modify values based on your network.
```
apiVersion: v1
kind: ConfigMap
metadata:
  namespace: metallb-system
  name: config
data:
  config: |
    address-pools:
    - name: default
      protocol: layer2
      addresses:
      - 192.168.122.20-192.168.122.30
```
Apply
```
kubectl apply -f ip-pool.yaml
```
## Install/enable helm binary 
```
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
sudo bash get_helm.sh
```
## Setup ingres as nginx
 - Daemonset
 ``` 
 helm install ingress-nginx ingress-nginx --repo https://kubernetes.github.io/ingress-nginx --create-namespace=true \
    --set controller.kind=DaemonSet,controller.service.enabled=false \
    --set controller.hostNetwork=true,controller.publishService.enabled=false --namespace=ingress 
 ```
 - Deployment
 ```
 helm install ingress-nginx ingress-nginx --repo https://kubernetes.github.io/ingress-nginx --namespace=ingress --create-namespace=true 
 ```

## NFS dynamic provisioner setup ( Helm Chart )
```
helm install nfsclient nfs-subdir-external-provisioner --repo https://kubernetes-sigs.github.io/nfs-subdir-external-provisioner \
    --namespace=kube-system \
    --set storageClass.archiveOnDelete=false \
    --set nfs.server=172.10.10.144 \
    --set nfs.path=/nfs
```
   
 If you wish to set the storage class as default as well Then upgrade the chart
```
helm install nfsclient nfs-subdir-external-provisioner --repo https://kubernetes-sigs.github.io/nfs-subdir-external-provisioner \
    --namespace=kube-system \
    --set storageClass.archiveOnDelete=false \
    --set nfs.server=172.10.10.144 \
    --set nfs.path=/nfs  \
    --set storageClass.defaultClass=true
 ```
   
## Setup Cert-manager   

```
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.10.0/cert-manager.yaml
```
Now you need a cert provider or issuer. For selfsigned certificates use this.

Create a file named issuer.yaml

```
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-staging
spec:
  selfSigned: {}
```
Apply the changes

```
kubectl apply -f issuer.yaml
```

## Setup metrics-server  
```
kubectl apply -f https://raw.githubusercontent.com/sharmavijay86/sharmavijay86.github.io/master/blog/k8ssetup/components.yaml
```
## Setup the EFK (elastic search fluentbit & kibana) stack with helm chart

```
kubectl create ns logging
helm upgrade --install fluent-bit fluent-bit --repo=https://fluent.github.io/helm-charts
helm upgrade --install elasticsearch elasticsearch --set=replicas=3,minimumMasterNodes=1,resources.requests.cpu=100m,resources.requests.memory=1Gi,volumeClaimTemplate.resources.requets.storage=5Gi, --repo=https://helm.elastic.co -n logging

helm upgrade --install kibana kibana --set=resources.requests.cpu=100m,resources.requests.memory=500Mi,ingress.enabled=true,ingress.annotations."cert-manager\.io\/cluster-issuer"=letsencrypt-staging,ingress.hosts[0].host=kibana.k8s.mevijay.dev,ingress.hosts[0].paths[0].path=/,ingress.tls[0].secretName=kibana-tls,ingress.tls[0].hosts[0]=kibana.k8s.mevijay.dev --repo=https://helm.elastic.co -n logging
```

## Dynamic storage provisioning
For the dynamic provisioning we need a storage class and rancher have the answer for this lab.
### Setup the provisioner 
```
kubectl apply -f https://raw.githubusercontent.com/rancher/local-path-provisioner/v0.0.23/deploy/local-path-storage.yaml
```

You can patch this storageClass to act as default 

```
kubectl patch storageclass local-path -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
```
Create a pvc and pod
```
kubectl create -f https://raw.githubusercontent.com/rancher/local-path-provisioner/master/examples/pvc/pvc.yaml
kubectl create -f https://raw.githubusercontent.com/rancher/local-path-provisioner/master/examples/pod/pod.yaml
```

## Setup monitoring with prometheus and grafana

- Download the hlem chart values.yaml file for both grafana and prometheus.   
```
wget https://raw.githubusercontent.com/sharmavijay86/sharmavijay86.github.io/master/blog/k8ssetup/grafana-values.yaml
wget https://raw.githubusercontent.com/sharmavijay86/sharmavijay86.github.io/master/blog/k8ssetup/prometheus-values.yaml
```
- Updates values based on your case. mainly the ingress part and storage part.
- Run the helm commands to deploy it all.
```
helm install prometheus prometheus --repo=https://prometheus-community.github.io/helm-charts -n prometheus --create-namespace
helm install grafana grafana --repo=https://grafana.github.io/helm-charts  -f grafana-values.yaml -n prometheus
```

