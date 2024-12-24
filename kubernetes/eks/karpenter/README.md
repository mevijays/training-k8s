Imagine your school needs more classrooms because there are too many students!

EKS is like the land where the school is built.
Karpenter is like a smart builder who knows when to build more classrooms and when to take some down.
Nodes are like the classrooms in the school.
When there are more students (like more apps needing to run), Karpenter sees that and builds a new classroom (a new node). If a classroom is empty for a long time, Karpenter can take it down to save space and money.
## Prerequisites cloudformation deployment
```bash
export TEMPOUT="$(mktemp)"
curl -fsSL https://raw.githubusercontent.com/aws/karpenter-provider-aws/v1.1.0/website/content/en/preview/getting-started/getting-started-with-karpenter/cloudformation.yaml  > "${TEMPOUT}" \
&& aws cloudformation deploy \
  --stack-name "Karpenter-trainereks" \
  --template-file "${TEMPOUT}" \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1 \
  --parameter-overrides "ClusterName=trainereks"
```
# Install EKS cluster
- Create the eksctl file 
```yaml
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig
metadata:
  name: "trainereks"    # change
  region: "us-east-1"   # change
  version: "1.30"
  tags:
    karpenter.sh/discovery: "trainereks"   # change
iam:
  withOIDC: true
  podIdentityAssociations:
  - namespace: "kube-system"
    serviceAccountName: karpenter
    roleName: trainereks-karpenter
    permissionPolicyARNs:
      - arn:aws:iam::<customerID>:policy/KarpenterControllerPolicy-trainereks      # change customerid

iamIdentityMappings:
- arn: "arn:aws:iam::<customerID>:role/KarpenterNodeRole-trainereks"              # change customer id
  username: system:node:{{EC2PrivateDNSName}}
  groups:
    - system:bootstrappers
    - system:nodes
vpc:
  cidr: 192.168.0.0/16
addons:
  - name: eks-pod-identity-agent
    version: latest
managedNodeGroups:
  - name: default
    desiredCapacity: 1
    minSize: 1
    maxSize: 3
    instanceType: t3.medium
    amiFamily: AmazonLinux2

```
- Deploy now
```bash
eksctl create cluster -f eksclusterconfig.yaml
```


## Link the role
```bash
aws iam create-service-linked-role --aws-service-name spot.amazonaws.com || true
# If the role has already been successfully created, you will see:
# An error occurred (InvalidInput) when calling the CreateServiceLinkedRole operation: Service role name AWSServiceRoleForEC2Spot has been taken in this account, please try a different suffix.

```

## installation
```Bash
export KARPENTER_VERSION="1.1.0"
export KARPENTER_NAMESPACE="kube-system"
export CLUSTER_NAME="trainereks"
export AWS_DEFAULT_REGION="us-east-1"
export AWS_ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
export TEMPOUT="$(mktemp)"
export K8S_VERSION="1.30"
export AMD_AMI_ID="$(aws ssm get-parameter --name /aws/service/eks/optimized-ami/${K8S_VERSION}/amazon-linux-2/recommended/image_id --query Parameter.Value --output text)"

# Logout of helm registry to perform an unauthenticated pull against the public ECR
helm registry logout public.ecr.aws

helm upgrade --install karpenter oci://public.ecr.aws/karpenter/karpenter --version "${KARPENTER_VERSION}" --namespace "${KARPENTER_NAMESPACE}" --create-namespace \
  --set "settings.clusterName=${CLUSTER_NAME}" \
  --set "settings.interruptionQueue=${CLUSTER_NAME}" \
  --set controller.resources.requests.cpu=1 \
  --set controller.resources.requests.memory=1Gi \
  --set controller.resources.limits.cpu=1 \
  --set controller.resources.limits.memory=1Gi \
  --wait
```
``Nodepool`` is like a blueprint for the classroom. It tells Karpenter:

What kind of classroom to build: Big or small? With desks or with tables?
Where to build it: On the ground floor or on the first floor?
Special rules for the classroom: Maybe only students with certain badges can use this classroom.
EC2NodeClass is like a detailed instruction manual for the classroom. It tells Karpenter things like:

What color to paint the walls: Should it be blue, green, or yellow?
What kind of chairs to use: Should they be soft chairs or hard chairs?
Where to put the lights: Should they be on the ceiling or on the walls?
Karpenter uses the Nodepool and EC2NodeClass to build the perfect classroom for the students. This way, everyone has a place to learn and the school doesn't waste space or money!

### Uses:

Nodepool: Helps Karpenter decide what kind of nodes to create and where to put them.
EC2NodeClass: Gives Karpenter very specific instructions on how to build the nodes.
This makes sure that the "classrooms" (nodes) are just right for the "students" (apps) and that the "school" (EKS) runs smoothly!


### 1. Nodepool YAML Example

```YAML
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: default
spec:
  template:
    spec:
      requirements:
        - key: kubernetes.io/arch
          operator: In
          values: ["amd64"]
        - key: kubernetes.io/os
          operator: In
          values: ["linux"]
        - key: karpenter.sh/capacity-type
          operator: In
          values: ["on-demand"]
        - key: karpenter.k8s.aws/instance-category
          operator: In
          values: ["t"]
        - key: karpenter.k8s.aws/instance-generation
          operator: In
          values: ["3"]
        - key: karpenter.k8s.aws/instance-size
          operator: In
          values: ["medium"]
      nodeClassRef:
        group: karpenter.k8s.aws
        kind: EC2NodeClass
        name: default
      expireAfter: 720h # 30 * 24h = 720h
  limits:
    cpu: 1000
  disruption:
    consolidationPolicy: WhenEmptyOrUnderutilized
    consolidateAfter: 1m
```

### Explanation:

``apiVersion:`` This tells Kubernetes what version of the NodePool definition we're using.

``kind:`` This specifies that we're creating a NodePool object.

``metadata.name:`` This is a unique name for our NodePool.

``spec.template.metadata.labels:`` These labels will be added to any nodes created by this NodePool.

``spec.template.spec.nodeClassRef.name:`` This links the NodePool to an EC2NodeClass named "my-nodeclass".

``spec.template.spec.requirements:`` These are rules for the nodes:

Only use instances from the "c" and "m" families (like c5.large, m5.xlarge).  
Only create nodes in the "us-west-2a" and "us-west-2b" zones.  
``spec.template.spec.taints:`` This adds a "taint" to the nodes. Taints are like special marks that can prevent certain applications from running on the node unless they have a matching "tolerance".  

### 2. EC2NodeClass YAML Example

```YAML
apiVersion: karpenter.k8s.aws/v1
kind: EC2NodeClass
metadata:
  name: default
spec:
  amiFamily: AL2 # Amazon Linux 2
  role: "KarpenterNodeRole-trainereks" # replace with your cluster name
  subnetSelectorTerms:
    - tags:
        karpenter.sh/discovery: "trainereks" # replace with your cluster name
  securityGroupSelectorTerms:
    - tags:
        karpenter.sh/discovery: "trainereks" # replace with your cluster name
  amiSelectorTerms:
    - id: "${AMD_AMI_ID}"
```
## Get the AMI id using :
```bash
aws ssm get-parameter --name /aws/service/eks/optimized-ami/1.30/amazon-linux-2/recommended/image_id --query Parameter.Value --output text
```
### Explanation:

``apiVersion:`` This tells Kubernetes what version of the EC2NodeClass definition we're using.   
``kind:`` This specifies that we're creating an EC2NodeClass object.   
``metadata.name:`` This is a unique name for our EC2NodeClass (must match the one in the NodePool).   
``spec.amiFamily: ``This tells Karpenter to use the Amazon Linux 2 operating system for the nodes.   
``spec.subnetSelectorTerms:`` This tells Karpenter to place the nodes in subnets with the tag karpenter.sh/discovery: my-cluster.   
``spec.securityGroupSelectorTerms:`` This tells Karpenter to apply security groups with the tag karpenter.sh/discovery: my-cluster to the nodes.   


## Testing the autoscalling 

```bash
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: inflate
spec:
  replicas: 0
  selector:
    matchLabels:
      app: inflate
  template:
    metadata:
      labels:
        app: inflate
    spec:
      terminationGracePeriodSeconds: 0
      securityContext:
        runAsUser: 1000
        runAsGroup: 3000
        fsGroup: 2000
      containers:
      - name: inflate
        image: public.ecr.aws/eks-distro/kubernetes/pause:3.7
        resources:
          requests:
            cpu: 1
        securityContext:
          allowPrivilegeEscalation: false
EOF

kubectl scale deployment inflate --replicas 5
kubectl logs -f -n "${KARPENTER_NAMESPACE}" -l app.kubernetes.io/name=karpenter -c controller

```
