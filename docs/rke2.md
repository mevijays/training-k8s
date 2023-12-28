# Rancher RKE2 kubernetes cluster (2 node)
## Introduction:    
RKE2 is the enterprise ready,stable and secure kubernetes distribution which is easy to install configure and manage. Most of the enterprise configurations comes out of the boxy from the installation like:
 - Nginx ingress controller
 - Metric-server
 - Canal CNI plugin
 - Core DNS
 - ETCD backup and restore snapshot script
## Prerequisites:
- Fresh 2 ubuntu 22.04 server VM
## Server/ Master node Setup
The server or master node vm.   
Install RKE2 binaries:
```bash
curl -sfL https://get.rke2.io | sudo sh -
sudo systemctl enable rke2-server.service
```
If you have extra ips or domains as API endpoints add them in config file ``/etc/rancher/rke2/config.yaml``  like this-
```bash
vim /etc/rancher/rke2/config.yaml

write-kubeconfig-mode: "0644"
tls-san:
  - "foo.local" # or any other ip external public ip in azure vm case
```
Now start RKE2 server
```bash
sudo systemctl start rke2-server.service
```

if you want to see the logs of process run this in seperate shell of server
```bash
sudo journalctl -u rke2-server -f
```
Now enable your kubernetes credentials for the user
```bash
mkdir ~/.kube
sudo cp /etc/rancher/rke2/rke2.yaml ~/.kube/config
sudo chown $(whoami):$(whoami) ~/.kube/config
```
A token that can be used to register other server or agent nodes will be created at ``/var/lib/rancher/rke2/server/node-token`` copy the token when registering your client/worker nodes.
```bash
sudo cat /var/lib/rancher/rke2/server/node-token
```

## Agent/worker node setup
Install and enable the worker node or agent binary
```bash
sudo bash
curl -sfL https://get.rke2.io | INSTALL_RKE2_TYPE="agent" sh -
systemctl enable rke2-agent.service
```
Now before we start the node we need to configure the token and master node api address. run bellow commands to create config folder and configure the master details.
```bash
mkdir -p /etc/rancher/rke2/
vim /etc/rancher/rke2/config.yaml
```
Content for config.yaml:
```bash
server: https://<server>:9345
token: <token from server node>
```
Replace the server from the real master server ip or hostname and replace the correct token.

Now join the agent 
```bash
systemctl start rke2-agent.service
```
# All these commands to run from master node.
### Local storage provisioner installation:
#### Dynamic storage provisioning
For the dynamic provisioning we need a storage class and rancher have the answer for this lab.

- Setup the provisioner
```bash
kubectl apply -f https://raw.githubusercontent.com/rancher/local-path-provisioner/v0.0.23/deploy/local-path-storage.yaml
``````### Cert manager installation:
```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```
You can patch this storageClass to act as default
```bash
kubectl patch storageclass local-path -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
```
Create a pvc and pod
```bash
kubectl create -f https://raw.githubusercontent.com/rancher/local-path-provisioner/master/examples/pvc/pvc.yaml
kubectl create -f https://raw.githubusercontent.com/rancher/local-path-provisioner/master/examples/pod/pod.yaml
```
### Cert manager installation:
```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

### ETCD backup restore
- Creating Snapshots   

Snapshots are enabled by default.

The snapshot directory defaults to ``/var/lib/rancher/rke2/server/db/snapshots.``   
In RKE2, snapshots are stored on each etcd node. If you have multiple etcd or etcd + control-plane nodes, you will have multiple copies of local etcd snapshots.

You can take a snapshot manually while RKE2 is running with the etcd-snapshot subcommand. For example: ``rke2 etcd-snapshot save --name pre-upgrade-snapshot.``

## Cluster Reset
RKE2 enables a feature to reset the cluster to one member cluster by passing ``--cluster-reset`` flag, when passing this flag to rke2 server it will reset the cluster with the same data dir in place, the data directory for etcd exists in ``/var/lib/rancher/rke2/server/db/etcd``, this flag can be passed in the events of quorum loss in the cluster.

To pass the reset flag, first you need to stop RKE2 service if its enabled via systemd:
```bash
systemctl stop rke2-server
rke2 server --cluster-reset
```
**Result:** A message in the logs say that RKE2 can be restarted without the flags. Start rke2 again and it should start rke2 as a 1 member cluster.

### Restoring a Snapshot to Existing Nodes
When RKE2 is restored from backup, the old data directory will be moved to /var/lib/rancher/rke2/server/db/etcd-old-%date%/. RKE2 will then attempt to restore the snapshot by creating a new data directory and start etcd with a new RKE2 cluster with one etcd member.

You must stop RKE2 service on all server nodes if it is enabled via systemd. Use the following command to do so:
```bash
systemctl stop rke2-server
```

Next, you will initiate the restore from snapshot on the first server node with the following commands:
```bash
rke2 server \
  --cluster-reset \
  --cluster-reset-restore-path=<PATH-TO-SNAPSHOT>
```
Once the restore process is complete, start the rke2-server service on the first server node as follows:
```bash
systemctl start rke2-server
```
Remove the rke2 db directory on the other server nodes as follows:
```bash
rm -rf /var/lib/rancher/rke2/server/db
```
Start the rke2-server service on other server nodes with the following command:
```bash
systemctl start rke2-server
```
**Result:** After a successful restore, a message in the logs says that etcd is running, and RKE2 can be restarted without the flags. Start RKE2 again, and it should run successfully and be restored from the specified snapshot.

When rke2 resets the cluster, it creates an empty file at ``/var/lib/rancher/rke2/server/db/reset-flag.`` This file is harmless to leave in place, but must be removed in order to perform subsequent resets or restores. This file is deleted when rke2 starts normally.

## Auto-Deploying Manifests
One of the amazing feature in RKE2 is, any file found in ``/var/lib/rancher/rke2/server/manifests`` will automatically be deployed to Kubernetes in a manner similar to kubectl apply.