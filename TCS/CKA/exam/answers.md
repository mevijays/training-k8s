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
