<!-- NAV-TOP -->
# Service Account Security

[&larr; Service Accounts - Points to Note](./sa-pointers.md) &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Setup Environment for Upgrading Clusters &rarr;](./kubeadm-automate.md)

---
<!-- /NAV-TOP -->

### Documentation Referred:

https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/

#### Authenticating with Token:
```sh
kubectl run pod-1 --image=nginx
kubectl exec -it pod-1 -- bash
```
```sh
cat /var/run/secrets/kubernetes.io/serviceaccount/token
TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
echo $TOKEN
curl -k -H "Authorization: Bearer $TOKEN" "https://kubernetes/api/v1"

curl -k -H "Authorization: Bearer $TOKEN" "https://kubernetes/api/v1/namespaces"
```

### Approach 1 - Opt out AutoMounting at Service Account level (Reference):
```sh
kubectl edit sa default
```
Add following snippet:

`automountServiceAccountToken: false`


#### Verification
```sh
kubectl run pod-2 --image=nginx

kubectl exec -it pod-2 -- bash

cat /var/run/secrets/kubernetes.io/serviceaccount/token
```

### Approach 2 Opt out AutoMounting at Pod level

```sh
nano pod-3.yaml
```
```sh
apiVersion: v1
kind: Pod
metadata:
  name: demo-pod
spec:
  automountServiceAccountToken: false
  containers:
  - image: nginx
    name: demo-pod
```
```sh
kubectl apply -f pod-3.yaml
```

#### Verification Stage:

```sh
kubectl exec -it demo-pod -- bash

cat /var/run/secrets/kubernetes.io/serviceaccount/token
```
#### Delete the resources created
```sh
kubectl delete pods --all
```


<!-- NAV-BOTTOM -->
---

[&larr; Service Accounts - Points to Note](./sa-pointers.md) &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Setup Environment for Upgrading Clusters &rarr;](./kubeadm-automate.md)

[&#8962; All Domains](../README.md)
<!-- /NAV-BOTTOM -->
