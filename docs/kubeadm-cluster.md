# Kubernetes cluster lab with ubuntu 22.04

### Step to follow on all nodes

To turn off swap space, if it is enabled 
```
sudo sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab
sudo swapoff -a
```
### To install CRIO
- Install required packages
```bash
sudo apt update
sudo apt install -y apt-transport-https ca-certificates curl gnupg2 software-properties-common
```
- Enable The repo
```
export OS_VERSION=xUbuntu_22.04
export CRIO_VERSION=1.24
curl -fsSL https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/$OS_VERSION/Release.key | sudo gpg --dearmor -o /usr/share/keyrings/libcontainers-archive-keyring.gpg
curl -fsSL https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable:/cri-o:/$CRIO_VERSION/$OS_VERSION/Release.key | sudo gpg --dearmor -o /usr/share/keyrings/libcontainers-crio-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/libcontainers-archive-keyring.gpg] https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/$OS_VERSION/ /" | sudo tee /etc/apt/sources.list.d/devel:kubic:libcontainers:stable.list
echo "deb [signed-by=/usr/share/keyrings/libcontainers-crio-archive-keyring.gpg] https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable:/cri-o:/$CRIO_VERSION/$OS_VERSION/ /" | sudo tee /etc/apt/sources.list.d/devel:kubic:libcontainers:stable:cri-o:$CRIO_VERSION.list
```
- Install packages
```
sudo apt update
sudo apt install -y cri-o cri-o-runc
sudo systemctl daemon-reload
sudo systemctl enable crio
sudo systemctl start crio
```
### Enable kube adm repository
Change the version from v1.27 to something else if you want to install any other version
```bash
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.27/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.27/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt update
```
To install kubernetes binaries run bellow
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
- Pull the required container images on node
```
sudo kubeadm config images pull
```
We can initialize master node with difrent options:   
- To install with specific CRI socket, in case cri-o.
```
sudo kubeadm init --pod-network-cidr=10.244.0.0/16 --service-cidr=10.20.0.0/12 --cri-socket unix:///var/run/crio/crio.sock
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
sudo kubeadm join 192.168.142.130:6443 --token gefqt9.oj3kcgubehofxbz8  --discovery-token-ca-cert-hash sha256:a79789ade9c95182522f55b1ab17e93cd6eac9c7eaf8b7b67a6c125bbb5f50ce  --cri-socket unix:///var/run/crio/crio.sock
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
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.13.12/config/manifests/metallb-native.yaml
```
Create yaml for ip pool 
```
vim ip-pool.yaml
```
Apply the ip pool for LB. Create and modify values based on your network.
```yaml
---
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: first-pool
  namespace: metallb-system
spec:
  addresses:
  - 192.168.142.100-192.168.142.125

---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: l2advert
  namespace: metallb-system

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
## Dynamic storage provisioning
For the dynamic provisioning we need a storage class and rancher have the answer for this lab.
### Setup the localpath provisioner 
```
kubectl apply -f https://raw.githubusercontent.com/rancher/local-path-provisioner/v0.0.23/deploy/local-path-storage.yaml
```

You can patch this storageClass to act as default 

```
kubectl patch storageclass local-path -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
```
Verify Create a pvc and pod
```
kubectl create -f https://raw.githubusercontent.com/rancher/local-path-provisioner/master/examples/pvc/pvc.yaml
kubectl create -f https://raw.githubusercontent.com/rancher/local-path-provisioner/master/examples/pod/pod.yaml
```
### NFS dynamic provisioner setup ( Helm Chart )
```
helm install nfsclient nfs-subdir-external-provisioner --repo https://kubernetes-sigs.github.io/nfs-subdir-external-provisioner \
    --namespace=kube-system \
    --set storageClass.archiveOnDelete=false \
    --set nfs.server=<NFS_SERVER_IP> \
    --set nfs.path=/nfs
```
   
 If you wish to set the storage class as default as well Then upgrade the chart
```
helm install nfsclient nfs-subdir-external-provisioner --repo https://kubernetes-sigs.github.io/nfs-subdir-external-provisioner \
    --namespace kube-system \
    --set storageClass.archiveOnDelete=false \
    --set nfs.server=<NFS_SERVER_IP> \
    --set nfs.path=/nfs  \
    --set storageClass.defaultClass=true
 ```
   
## Setup Cert-manager   

```
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```
- Create a selfsigned issuer
```bash
kubectl apply -f https://raw.githubusercontent.com/mevijays/training-k8s/main/kubernetes/yamls/SS-clusterIssuer.yaml
```
- How to use with ingress?
```
kubectl create ingress webcm --rule="abc.com/*=webcm:8080,tls=abc-tls" --annotation="cert-manager.io/cluster-issuer: selfsigned-issuer"
```

## Setup metrics-server  
```
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/download/v0.6.1/components.yaml
```

## Setup the EFK Stack (Elasticsearch, Fluent Bit, Kibana)

### Prerequisites
Ensure network connectivity between services:
```bash
kubectl get pods -n logging
kubectl get svc -n logging
```

### 1. Install Elasticsearch
```bash
helm upgrade --install elasticsearch elasticsearch \
  --set replicas=1 \
  --set minimumMasterNodes=1 \
  --set resources.requests.cpu=100m \
  --set resources.requests.memory=1Gi \
  --set volumeClaimTemplate.resources.requests.storage=5Gi \
  --set elasticsearch.password='redhat123' \
  --repo https://helm.elastic.co \
  -n logging \
  --create-namespace
```

### 2. Install Logstash
Create `logstash.yaml`:
```yaml
persistence:
  enabled: true

logstashConfig:
  logstash.yml: |
    http.host: 0.0.0.0

logstashPipeline:
  logstash.conf: |
    input {
      beats {
        port => 5044
      }
    }
    output {
      elasticsearch {
        hosts => ["https://elasticsearch-master:9200"]
        manage_template => false
        ssl_certificate_verification => false
        index => "%{[@metadata][beat]}-%{+YYYY.MM.dd}"
        user => "elastic"
        password => "redhat123"
      }
    }

service:
  type: ClusterIP
  ports:
    - name: beats
      port: 5044
      protocol: TCP
      targetPort: 5044
    - name: http
      port: 8080
      protocol: TCP
      targetPort: 8080
```

Install Logstash:
```bash
helm upgrade --install logstash logstash \
  --set replicas=1 \
  --set resources.requests.cpu=100m \
  --set resources.requests.memory=1Gi \
  --repo https://helm.elastic.co \
  -f logstash.yaml \
  -n logging
```

### 3. Install Kibana
```bash
helm upgrade --install kibana kibana \
  --set resources.requests.cpu=100m \
  --set resources.requests.memory=500Mi \
  --repo https://helm.elastic.co \
  -n logging
```

### 4. Install Filebeat
Create `filebeat.yaml`:
```yaml
daemonset:
  filebeatConfig:
    filebeat.yml: |
      filebeat.inputs:
        - type: container
          paths:
            - /var/log/containers/*.log
          processors:
            - add_kubernetes_metadata:
                host: ${NODE_NAME}
                matchers:
                  - logs_path:
                      logs_path: "/var/log/containers/"

      output.logstash:
        hosts: ["logstash-logstash:5044"]
```

Install Filebeat:
```bash
helm upgrade --install filebeat filebeat \
  --set resources.requests.cpu=100m \
  --set resources.requests.memory=500Mi \
  --repo https://helm.elastic.co \
  -f filebeat.yaml \
  -n logging
```

### 5. Expose Kibana
Create `svc-kibana.yaml`:
```yaml
apiVersion: v1
kind: Service
metadata:
  labels:
    app: kibana
    release: kibana
  name: kibana-kibana-public
  namespace: logging
spec:
  ports:
    - name: http
      port: 5601
      protocol: TCP
      targetPort: 5601
  selector:
    app: kibana
    release: kibana
  type: LoadBalancer
```

Apply and access:
```bash
kubectl apply -f svc-kibana.yaml -n logging
kubectl get svc -n logging
```

Access Kibana at `http://<LOADBALANCER-IP>:5601` with:
- Username: `elastic`
- Password: Extract using:
```bash
kubectl get secrets --namespace=logging elasticsearch-master-credentials -o jsonpath='{.data.password}' | base64 -d
```

### Verification
```bash
# Check Elasticsearch
curl https://elasticsearch-master:9200

# Check Logstash
kubectl logs -n logging -l release=logstash

# Check Kibana
kubectl get pods -n logging -l release=kibana

# Check Filebeat
kubectl get pods -n logging -l release=filebeat
```
kubectl create ns logging
helm upgrade --install fd oci://registry-1.docker.io/bitnamicharts/fluent-bit -n logging
helm upgrade --install elasticsearch elasticsearch --set=replicas=1,minimumMasterNodes=1,resources.requests.cpu=100m,resources.requests.memory=1Gi,volumeClaimTemplate.resources.requests.storage=5Gi, --repo=https://helm.elastic.co -n logging

helm upgrade --install kibana kibana --set=resources.requests.cpu=100m,resources.requests.memory=500Mi,ingress.enabled=true,ingress.annotations."cert-manager\.io\/cluster-issuer"=letsencrypt-staging,ingress.hosts[0].host=kibana.k8s.mevijay.dev,ingress.hosts[0].paths[0].path=/,ingress.tls[0].secretName=kibana-tls,ingress.tls[0].hosts[0]=kibana.k8s.mevijay.dev --repo=https://helm.elastic.co -n logging
```

## Setup monitoring with prometheus and grafana

- Clone kubeprometheus repo
```
git clone https://github.com/prometheus-operator/kube-prometheus.git
```
- Deploy it!
```bash
cd kube-prometheus
# Create the namespace and CRDs, and then wait for them to be availble before creating the remaining resources
kubectl create -f manifests/setup

# Wait until the "servicemonitors" CRD is created. The message "No resources found" means success in this context.
until kubectl get servicemonitors --all-namespaces ; do date; sleep 1; echo ""; done

kubectl create -f manifests/
```
- Create ingress to access grafana!
```
kubectl create ingress grafana-ui --rule=grafana.k8s.mevijay.dev/*=grafana:3000,tls=grafana-tls -n monitoring --class=nginx --annotation="cert-manager.io/cluster-issuer=le-issuer"
```
Now access with user id and password as ``admin/admin``
- To delete it !
```
kubectl delete --ignore-not-found=true -f manifests/ -f manifests/setup
```
# Upgrading kubeadm cluster !

### Upgrade control plane node
- change the version repository from 27 to 28
```
sudo sed -i 's/27/28/g' /etc/apt/sources.list.d/kubernetes.list
sudo apt update
```
- Install packages
```
sudo apt install  kubeadm kubelet kubectl -y
```
- check the upgrade plan
```
sudo kubeadm upgrade plan
```
- Apply upgrade to target version and wait till success msgs
```
sudo kubeadm upgrade apply v1.28.6
```

### Upgrade worker nodes
***Note:*** kubectl commands will be run from master
- Drain the worker node
```bash
# replace <node-to-drain> with the name of your node you are draining
kubectl drain ubuntu02-vitual-machine --ignore-daemonsets --delete-emptydir-data  --force
```
- change the version repository from 27 to 28
```
sudo sed -i 's/27/28/g' /etc/apt/sources.list.d/kubernetes.list
sudo apt update
```

- Installation of kubeadm and kubectl 
```
sudo apt install kubelet kubeadm -y
```
- upgrade!
```
sudo kubeadm upgrade node
```
- Restart kubelet 
```
sudo systemctl daemon-reload
sudo systemctl restart kubelet
```
- uncordon node
```
kubectl uncordon ubuntu02-vitual-machine 
```

