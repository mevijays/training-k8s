#!/bin/sh
set -o errexit
# check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi
# setup docker if not installed 
if [[ ! -f "/usr/bin/docker" ]]
then
        curl -fsSL https://get.docker.com -o get-docker.sh
        /bin/bash get-docker.sh
fi
# setup kind binary
if [[ ! -f "/usr/local/bin/kind" ]]
then
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.17.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
fi

# setup kubectl
if [[ ! -f "/usr/local/bin/kubectl" ]]
then
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv ./kubectl /usr/local/bin/
fi
# create registry container unless it already exists
reg_name='kind-registry'
reg_port='5001'
host_ip='192.168.1.2'
if [ "$(docker inspect -f '{{.State.Running}}' "${reg_name}" 2>/dev/null || true)" != 'true' ]; then
  docker volume create regvol
  docker run \
    -d --restart=always -v "regvol:/var/lib/registry" -p "127.0.0.1:${reg_port}:5000" --name "${reg_name}" \
    registry:2
  docker run -d -p 8080:80 --restart=always -e REGISTRY_TITLE='My LAB' -e NGINX_PROXY_PASS_URL=http://"${reg_name}":5000  --name "${reg_name}"-ui joxit/docker-registry-ui:latest
fi

# create a cluster with the local registry enabled in containerd
cat <<EOF | kind create cluster --config=-
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
    - containerPort: 2379
      hostPort: 2379
      listenAddress: "127.0.0.1"
      protocol: TCP
    kubeadmConfigPatches:
    - |
      kind: InitConfiguration
      nodeRegistration:
        kubeletExtraArgs:
          node-labels: "ingress-ready=true"
networking:
  kubeProxyMode: "ipvs"
  apiServerAddress: "${host_ip}"
  apiServerPort: 6443
containerdConfigPatches:
- |-
  [plugins."io.containerd.grpc.v1.cri".registry.mirrors."localhost:${reg_port}"]
    endpoint = ["http://${reg_name}:5000"]
EOF

# connect the registry to the cluster network if not already connected
if [ "$(docker inspect -f='{{json .NetworkSettings.Networks.kind}}' "${reg_name}")" = 'null' ]; then
  docker network connect "kind" "${reg_name}"
  docker network connect "kind" "${reg_name}"-ui
fi

# Document the local registry
# https://github.com/kubernetes/enhancements/tree/master/keps/sig-cluster-lifecycle/generic/1755-communicating-a-local-registry
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: local-registry-hosting
  namespace: kube-public
data:
  localRegistryHosting.v1: |
    host: "localhost:${reg_port}"
    help: "https://kind.sigs.k8s.io/docs/user/local-registry/"
EOF

kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
kubectl apply -f https://raw.githubusercontent.com/sharmavijay86/sharmavijay86.github.io/master/blog/k8ssetup/components.yaml
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.10.0/cert-manager.yaml
