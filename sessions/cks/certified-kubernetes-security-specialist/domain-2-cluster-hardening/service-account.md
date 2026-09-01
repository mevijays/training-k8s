<!-- NAV-TOP -->
# Overview of Service Accounts

[&larr; Practical - ClusterRole and ClusterRoleBinding](./clusterrole.md) &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Service Accounts - Points to Note &rarr;](./sa-pointers.md)

---
<!-- /NAV-TOP -->

#### List service account in all namespaces
```sh
kubectl get serviceaccount --all-namespaces
```

#### Create a Test App Pod
```sh
kubectl run app-pod --image=nginx 
kubectl get pods
```
#### Verify Namespace associated with Pod
```sh
kubectl describe pod app-pod
```
#### Verify Mounted Token in Pod
```sh
kubectl exec -it app-pod -- bash

cd /var/run/secrets/kubernetes.io/serviceaccount/

ls

cat token
```
#### Connect to Kubernetes Cluster using Token
```sh
token=$(cat token)
echo $token

kubectl cluster-info (from outside of Pod)

curl -k -H "Authorization: Bearer $token" https://control-plane-url-here/api/v1
```


<!-- NAV-BOTTOM -->
---

[&larr; Practical - ClusterRole and ClusterRoleBinding](./clusterrole.md) &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Service Accounts - Points to Note &rarr;](./sa-pointers.md)

[&#8962; All Domains](../README.md)
<!-- /NAV-BOTTOM -->
