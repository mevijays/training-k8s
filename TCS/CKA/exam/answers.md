# Questions Answers 
### Q1.
Create a deployment name as webcm from image nginx:alpine and expose it to service named webcm internally on port 80. Now create an ingress with hostname ckatcswebcm.lab when you access url ckatcswebcm.lab/hello, the deployment root should be accessible.
- **Answer** :   
```
kubectl create deploy webcm --image=nginx:alpine
kubectl expose deploy webcm --port=80 --target-port=80
kubectl create ingress webcm --class=nginx --rule=ckatcswebcm.lab/hello*=webcm:80 --annotation="nginx.ingress.kubernetes.io/rewrite-target=/"
```
### Q2. 
A kubernetes node is in not ready condition, troubleshoot it.
- **Answer** :
Check the node 
```
kubectl get node
```
SSH in to worker node and start enable kubelet
```
systemctl enable kubelet && systemctl start kubelet
```
exit and check again
```
kubectl get node
```

### Q3.
From the pod label name =overloaded-cpu, find the pods running high cpu workloads and write the name of the po consuming most cpu to the file in /opt
- **Answer** :
```
kubectl top po -l name=overloaded-cpu --sort-by='cpu'
```
### Q4.
Monitor the logs of a pod foo and: 1- extract the log lines containing error 'file not found'.   2- write them to /opt/file

- **Answer**

```
kubectl logs apppod | grep 'file not found' >> /opt/file
```
### Q5.
Create a persistent volume with name app-data and access mode readonlymany. the type of volume is hostpath and its location is /srv/app-data

- **Answer** :

```
apiVersion: v1
kind: PersistentVolume
metadata:
  name: example-pv
spec:
  capacity:
    storage: 2Gi
  volumeMode: Filesystem
  accessModes:
  - ReadOnlyMany
  persistentVolumeReclaimPolicy: Delete
  storageClassName: local-storage
  hostPath:
    path: /srv/app-data
```

### Q6.
Schedule a pod as follows - name: kucc8, app containers: 2. container name/image is consul:consul and  nginx:nginx.

- **Answer** :

```
apiVersion: v1
kind: Pod
metadata:
  creationTimestamp: null
  labels:
    run: kucc8
  name: kucc8
spec:
  containers:
  - image: nginx
    name: nginx
  - image: consul
    name: consul
    resources: {}
  dnsPolicy: ClusterFirst
  restartPolicy: Always
status: {}
```
### Q7.
Check to see how many nodes are ready ( not include node tainted to noschedule) and write the number to /opt/file2
- **Answer** :

```
kubectl get node
kubectl describe node <node name>
```
check the taints by above command and take note of count.


### Q8.
Schedule a pod as follow:  name nginx-ku8, image= nginx   node selector = disk=ssd

- **Answer** :

```
apiVersion: v1
kind: Pod
metadata:
  name: nginx-ku8
  labels:
    env: test
spec:
  containers:
  - name: nginx
    image: nginx
    imagePullPolicy: IfNotPresent
  nodeSelector:
    disk: ssd
```

### Q9.
Scalea deployment  mywebapp to 3 pods.
- **Answer** :

```
kubectl get deploy
kubectl scale deploy mywebapp --replicas=3
```

### Q10.
Set the node name ek8s-node0 as unavailable and rescedule all the pods running on it.

- **Answer**

```
kubectl drain node ek8s-node0 --ignore-daemonsets=true 
```
### Q11. 
backup the ETCD database and restore

First create snapshot of etcd instance running on https://127.0.0.1:2379, saving the snapshot to var/lib/backup/etcd-snapshot.db
Note: in exam the etcdctl bin will be available in client machine and certificates details will be given already in question itself.
- **Answer** :
IN LAB
Download the etcdctl binary archive
```
 wget https://github.com/etcd-io/etcd/releases/download/v3.4.22/etcd-v3.4.22-linux-amd64.tar.gz
```
extract it.
```
tar xvf etcd-v3.4.22-linux-amd64.tar.gz
```
change dir 
```
cd etcd-v3.4.22-linux-amd64
```
Now get the details of etcd pod and describe it for certificates path.
```
 kubectl describe $(kubectl get po -l component=etcd -n kube-system -o name) -n kube-system
```
take a note of the cert paths and endpoint, lets perform backup 

```
 ETCDCTL_API=3; sudo ./etcdctl --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/server.crt --key=/etc/kubernetes/pki/etcd/server.key snapshot save  /var/lib/backup/etcd-snapshot.db
```
Second part of the question is to restore the older etcd database  snapshot from file /var/lib/backup/etcd-snapshot-previous.db

Lets stop the etcd 
```
sudo bash 
systemctl stop etcd   # this command to run when etcd installed as service # in exam step
mv /etc/kubernetes/manifests/etcd.yaml /root/    # this command in case etcd running as static pod
```
Restore backup 
```
mv /var/lib/etcd /var/lib/etcd-old
ETCDCTL_API=3; sudo ./etcdctl --data-dir=/var/lib/etcd snapshot restore /var/lib/backup/etcd-snapshot-previous.db
systemctl start etcd # in exam 
mv /root/etcd.yaml /etc/kubernetes/manifests/   # in lab
```
### Q12.
***Master upgrade***
Upgrade the control plane to newer version

- SSH in to master node  # This qestion asked in exam
```
sudo bash
apt-mark unhold kubeadm kubelet
apt install kubeadm=1.25.3-00 kubelet=1.25.3-00 -y
apt-mark hold kubeadm kubelet
kubeadm upgrade apply v1.25.3
systemctl daemon-reload
systemctl restart kubelet
```
***Worker upgrade***
- Drain the node -step from kubectl
```
kubectl drain <node-name> --ignore-daemonsets  --delete-emptydir-data
```
- SSH in to worker node  ## for a lab purpose only. we do this one by one on all the nodes

```
apt-mark unhold kubeadm kubelet
apt install kubeadm=1.25.3-00 kubelet=1.25.3-00 -y
kubeadm upgrade node
apt-mark hold kubeadm kubelet
systemctl daemon-reload
systemctl restart kubelet
```

- Uncordon node -step from kubectl
```
kubectl uncordon <node-name>
```

### Q12.
You have been asked to create a new ClusterRole for a deployment pipeline and bind it to a specific ServiceAccount scoped to a specific
namespace.
Task -
Create a new ClusterRole named deployment-clusterrole, which only allows to create the following resource types:
 Deployment
 Stateful Set
 DaemonSet
Create a new ServiceAccount named cicd-token in the existing namespace app-team1.
Bind the new ClusterRole deployment-clusterrole to the new ServiceAccount cicd-token, limited to the namespace app-team1.

### Q13.
Create a new NetworkPolicy named allow-port-from-namespace in the existing namespace fubar.
Ensure that the new NetworkPolicy allows Pods in namespace internal to connect to port 9000 of Pods in namespace fubar.
Further ensure that the new NetworkPolicy:
 does not allow access to Pods, which don't listen on port 9000
 does not allow access from Pods, which are not in namespace internal
 
### Q14.
Reconfigure the existing deployment front-end and add a port specification named http exposing port 80/tcp of the existing container nginx.
Create a new service named front-end-svc exposing the container port http.
Configure the new service to also expose the individual Pods via a NodePort on the nodes on which they are scheduled.

### Q15.
Check to see how many nodes are ready (not including nodes tainted NoSchedule) and write the number to /opt/KUSC00402/kusc00402.txt.
### Q16.
Add a sidecar container named sidecar, using the busybox image, to the existing Pod big-corp-app. The new sidecar container has to run the
following command:

Use a Volume, mounted at /var/log, to make the log file big-corp-app.log available to the sidecar container.

### Q17.

Create a new PersistentVolumeClaim:
✑ Name: pv-volume
✑ Class: csi-hostpath-sc
✑ Capacity: 10Mi
Create a new Pod which mounts the PersistentVolumeClaim as a volume:
✑ Name: web-server
✑ Image: nginx
✑ Mount path: /usr/share/nginx/html
Configure the new Pod to have ReadWriteOnce access on the volume.
Finally, using kubectl edit or kubectl patch expand the PersistentVolumeClaim to a capacity of 70Mi and record that change.
