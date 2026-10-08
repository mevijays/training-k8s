[**Domain Home**](./Readme.md).  


## gvisor ( runsc with containerd ).   
   

- Reference URLs:  
1) [https://gvisor.dev/docs/user_guide/install/](https://gvisor.dev/docs/user_guide/install/)
2) [https://docs.cilium.io/en/stable/gettingstarted/k8s-install-default/#install-the-cilium-cli](https://docs.cilium.io/en/stable/gettingstarted/k8s-install-default/#install-the-cilium-cli)
3) [https://v1-34.docs.kubernetes.io/docs/setup/production-environment/tools/kubeadm/create-cluster-kubeadm/](https://v1-34.docs.kubernetes.io/docs/setup/production-environment/tools/kubeadm/create-cluster-kubeadm/)
4) [https://v1-34.docs.kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/](https://v1-34.docs.kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/)
5) [https://gvisor.dev/docs/user_guide/containerd/quick_start/](https://gvisor.dev/docs/user_guide/containerd/quick_start/)

### Gvisor installation steps
- Setup the host
```bash
sudo apt-get update && \
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg
```
You should have curl available to setup package repo

```bash
curl -fsSL https://gvisor.dev/archive.key | sudo gpg --dearmor -o /usr/share/keyrings/gvisor-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/gvisor-archive-keyring.gpg] https://storage.googleapis.com/gvisor/releases release main" | sudo tee /etc/apt/sources.list.d/gvisor.list > /dev/null
```

- install package
Now the runsc package can be installed:
```bash
sudo apt-get update && sudo apt-get install -y runsc
```
### containerd setup for kubeadm
```bash
swapoff -a
```
#### Step 1: Setup containerd
```sh
cat <<EOF | sudo tee /etc/modules-load.d/containerd.conf
overlay
br_netfilter
EOF
```
```sh
modprobe overlay
modprobe br_netfilter
```
```sh
cat <<EOF | sudo tee /etc/sysctl.d/99-kubernetes-cri.conf
net.bridge.bridge-nf-call-iptables  = 1
net.ipv4.ip_forward                 = 1
net.bridge.bridge-nf-call-ip6tables = 1
EOF
```
```sh
sysctl --system
```
```sh
apt-get install -y containerd
mkdir -p /etc/containerd
```
```sh
cat <<EOF | sudo tee /etc/containerd/config.toml
version = 2
[plugins."io.containerd.runtime.v1.linux"]
  shim_debug = true
[plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc]
  runtime_type = "io.containerd.runc.v2"
[plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runsc]
  runtime_type = "io.containerd.runsc.v1"
EOF
```

#### Step 2: Kernel Parameter Configuration
```sh
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
EOF
```
```sh
sudo sysctl --system
```

#### Step 3: Configuring Repo and Installation
```sh
sudo apt-get update
# apt-transport-https may be a dummy package; if so, you can skip that package
sudo apt-get install -y apt-transport-https ca-certificates curl gpg
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.34/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
# This overwrites any existing configuration in /etc/apt/sources.list.d/kubernetes.list # you can change your desired k8s version you want.
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.34/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
```

Update the apt package index, install kubelet, kubeadm and kubectl, and pin their version:
```sh
sudo apt-get update
 apt-get install -y kubelet=1.34.11-1.1 kubeadm=1.34.11-1.1 kubectl=1.34.11-1.1 cri-tools=1.34.0-1.1
sudo apt-mark hold kubelet kubeadm kubectl
systemctl enable --now kubelet
```

#### Step 4: setup cluster
```sh
kubeadm init --pod-network-cidr=192.168.0.0/16 
```

### Installation of cilium CNI plugin

#### Step 1: Latest version of clilium CLI installation.
```sh
CILIUM_CLI_VERSION=$(curl -s https://raw.githubusercontent.com/cilium/cilium-cli/main/stable.txt)
CLI_ARCH=amd64
if [ "$(uname -m)" = "aarch64" ]; then CLI_ARCH=arm64; fi
curl -L --fail --remote-name-all https://github.com/cilium/cilium-cli/releases/download/${CILIUM_CLI_VERSION}/cilium-linux-${CLI_ARCH}.tar.gz{,.sha256sum}
sha256sum --check cilium-linux-${CLI_ARCH}.tar.gz.sha256sum
sudo tar xzvfC cilium-linux-${CLI_ARCH}.tar.gz /usr/local/bin
rm cilium-linux-${CLI_ARCH}.tar.gz{,.sha256sum}
```
#### Step 2: Installing cilium CNI on to k8s cluster
``Note`` Run following command from the node where your k8s context are available.

```sh
cilium install 1.20.2
```

- Validate the installation
```sh
kubectl get po -A
# and
$ cilium status --wait
   /¯¯\
/¯¯\__/¯¯\    Cilium:         OK
\__/¯¯\__/    Operator:       OK
/¯¯\__/¯¯\    Hubble:         disabled
\__/¯¯\__/    ClusterMesh:    disabled
   \__/

DaemonSet         cilium             Desired: 2, Ready: 2/2, Available: 2/2
Deployment        cilium-operator    Desired: 2, Ready: 2/2, Available: 2/2
Containers:       cilium-operator    Running: 2
                  cilium             Running: 2
Image versions    cilium             quay.io/cilium/cilium:v1.9.5: 2
                  cilium-operator    quay.io/cilium/operator-generic:v1.9.5: 2
```

## Verify the gvisor runtimeclass and a pod creation.

#### Explore gVisor:
```sh
kubectl get runtimeclass
```
```sh
nano runtimeclass.yaml
```
```sh
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: gvisor2
handler: runsc
```
```sh
kubectl apply -f runtimeclass.yaml
```
```sh
nano gvisor-pod.yaml
```
```sh
apiVersion: v1
kind: Pod
metadata:
  name: nginx
spec:
  runtimeClassName: gvisor2
  containers:
  - image: nginx
    name: nginx
```
```sh
kubectl apply -f gvisor-pod.yaml
```

#### Create one more pod for seeing the difference in dmesg and uname output:
```sh
kubectl run nginx-default --image=nginx
```

#### Verify output (dmesg and uname -r)

From host machine: Run `dmesg` and 'uname -r'

```sh
kubectl exec -it nginx -- bash
dmesg
uname -r
logout
```

```sh
kubectl exec -it nginx-default -- bash
dmesg
uname -r
logout
```
