<!-- NAV-TOP -->
# Service Accounts - Points to Note

[&larr; Overview of Service Accounts](./service-account.md) &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Service Account Security &rarr;](./sa-security.md)

---
<!-- /NAV-TOP -->

#### Verify Default Service Account In Namespace
```sh
kubectl get serviceaccount
kubectl get sa
kubectl get sa -n kube-system
```
#### Create New Namespace
```sh
kubectl create namespace demo-test
```
#### Verify if Default Service Account Gets Created in Namespace
```sh
kubectl get sa -n demo-test
```
#### Create New Pod in Newly Created Namespace
```sh
kubectl run nginx-pod -n demo-test --image=nginx
kubectl get pods -n demo-test
kubectl describe pod nginx-pod -n demo-test
```
#### Verify if Mounted Token is Available inside Pod
```sh
kubectl exec -it nginx-pod -n demo-test -- bash
cd /var/run/secrets/kubernetes.io/serviceaccount/
ls
cat token
```


<!-- NAV-BOTTOM -->
---

[&larr; Overview of Service Accounts](./service-account.md) &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Service Account Security &rarr;](./sa-security.md)

[&#8962; All Domains](../README.md)
<!-- /NAV-BOTTOM -->
