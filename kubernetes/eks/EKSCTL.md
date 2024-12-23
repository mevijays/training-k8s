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
eksctl create cluster -n <clustername> -r us-east-1 -t t3.medium -N 1 -m 1 -M 3 --with-oidc --nodegroup-name default --vpc-cidr 192.168.0.0/16 

# enable addon ebs
eksctl create addon --name aws-ebs-csi-driver -c my-cluster -r us-east-1 
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
eksctl delete cluster $EKS_CLUSTER_NAME --region us-east-1
```