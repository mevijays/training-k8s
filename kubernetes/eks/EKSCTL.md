# eksctl install 
```bash
ARCH=amd64
PLATFORM=$(uname -s)_$ARCH
curl -sLO "https://github.com/eksctl-io/eksctl/releases/latest/download/eksctl_$PLATFORM.tar.gz"
tar -xzf eksctl_$PLATFORM.tar.gz -C /tmp && rm eksctl_$PLATFORM.tar.gz
sudo mv /tmp/eksctl /usr/local/bin
```
# Instantiate EKS cluster
Install EKS using bellow.   
```bash
export EKS_CLUSTER_NAME=eks-cluster
curl -fsSL https://raw.githubusercontent.com/mevijays/training-k8s/refs/heads/main/kubernetes/eks/eksclusterconfig.yaml | envsubst | eksctl create cluster -f -
```

# Install kubectl
```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
```
# Clean-up EKS
 You can delete cluster by this.
```bash
eksctl delete cluster $EKS_CLUSTER_NAME --wait
```
 
