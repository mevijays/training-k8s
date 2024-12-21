# Install ALB ingress controller
## configuration
Want to setup lab ??
Here is eksctl yaml file
```yaml
accessConfig:
  authenticationMode: API_AND_CONFIG_MAP
addons:
  - name: aws-ebs-csi-driver
    version: latest
  - name: eks-pod-identity-agent
    version: latest
apiVersion: eksctl.io/v1alpha5
availabilityZones:
- us-east-1f
- us-east-1d
cloudWatch:
  clusterLogging: {}
iam:
  vpcResourceControllerPolicy: true
  withOIDC: true
kind: ClusterConfig
kubernetesNetworkConfig:
  ipFamily: IPv4
managedNodeGroups:
- amiFamily: AmazonLinux2
  desiredCapacity: 1
  disableIMDSv1: true
  disablePodIMDS: false
  iam:
    withAddonPolicies:
      albIngress: false
      appMesh: false
      appMeshPreview: false
      autoScaler: false
      awsLoadBalancerController: false
      certManager: false
      cloudWatch: false
      ebs: false
      efs: false
      externalDNS: false
      fsx: false
      imageBuilder: false
      xRay: false
  instanceSelector: {}
  instanceType: t3.medium
  labels:
    alpha.eksctl.io/cluster-name: trainereks
    alpha.eksctl.io/nodegroup-name: default
  maxSize: 3
  minSize: 1
  name: default
  privateNetworking: false
  releaseVersion: ""
  securityGroups:
    withLocal: null
    withShared: null
  ssh:
    allow: false
    publicKeyPath: ""
  tags:
    alpha.eksctl.io/nodegroup-name: default
    alpha.eksctl.io/nodegroup-type: managed
  volumeIOPS: 3000
  volumeSize: 80
  volumeThroughput: 125
  volumeType: gp3
metadata:
  name: trainereks
  region: us-east-1
  version: "1.30"
privateCluster:
  enabled: false
  skipEndpointCreation: false
vpc:
  autoAllocateIPv6: false
  cidr: 192.168.0.0/16
  clusterEndpoints:
    privateAccess: false
    publicAccess: true
  manageSharedNodeSecurityGroupRules: true
  nat:
    gateway: Single

```
- Download the iam polcy required.
```bash
curl -o iam-policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.2.1/docs/install/iam_policy.json
```
- Create the policy.
```bash
aws iam create-policy \
    --policy-name AWSLoadBalancerControllerIAMPolicy \
    --policy-document file://iam-policy.json
```
- Create the serviceaccount
```bash
eksctl create iamserviceaccount \
--cluster=<clustername> \
--namespace=kube-system \
--name=aws-load-balancer-controller \
--attach-policy-arn=arn:aws:iam::<accountID>:policy/AWSLoadBalancerControllerIAMPolicy \
--override-existing-serviceaccounts \
--region <region> \
--approve
```
- Deploy Cert manager required for alb ingress controller
```bash
kubectl apply \
    --validate=false \
    -f https://github.com/jetstack/cert-manager/releases/download/v1.13.5/cert-manager.yaml
```
- Download the file of installation.
```bash
curl -Lo v2_11_0_full.yaml https://github.com/kubernetes-sigs/aws-load-balancer-controller/releases/download/v2.11.0/v2_11_0_full.yaml
```
- Remove sa
```bash
sed -i.bak -e '690,698d' ./v2_11_0_full.yaml
```
- Provide your cluster name. change mycluster to your cluster name
```bash
sed -i.bak -e 's|your-cluster-name|mycluster|' ./v2_11_0_full.yaml
```
- Deploy it 
```bash
kubectl apply -f v2_11_0_full.yaml
```
- Create the ingress class
```yaml
apiVersion: networking.k8s.io/v1
kind: IngressClass
metadata:
  name: alb
spec:
  controller: ingress.k8s.aws/alb
```
- Apply it .

```bash
kubectl apply -f ingressClass.yaml
```
- Deploy the sample echo server application

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/refs/heads/release-2.11/docs/examples/echoservice/echoserver-namespace.yaml &&\
kubectl apply -f https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/refs/heads/release-2.11/docs/examples/echoservice/echoserver-deployment.yaml &&\
kubectl apply -f https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/refs/heads/release-2.11/docs/examples/echoservice/echoserver-service.yaml && \
kubectl apply -f https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/refs/heads/release-2.11/docs/examples/echoservice/echoserver-ingress.yaml
```
Now get the ingress host dns name and access

```bash
kubectl get ing -n echoserver
```