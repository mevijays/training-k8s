<!-- NAV-TOP -->
# Practical - ClusterRole and ClusterRoleBinding

[&larr; Practical - Role and RoleBinding](./role-rolebinding.md) &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Overview of Service Accounts &rarr;](./service-account.md)

---
<!-- /NAV-TOP -->

#### Create ClusterRole
```sh
kubectl create clusterrole pod-reader --verb=get,list,watch --resource=pods

kubectl describe clusterrole pod-reader
```
#### Create ClusterRoleBinding
```sh
kubectl create clusterrolebinding test-clusterrole --clusterrole=pod-reader --user=system:serviceaccount:default:test-sa

kubectl describe clusterrolebinding test-clusterrole
```
#### Test the Setup

Replace the URL in below command to your K8s URL. If using macOS or Linux, use `$TOKEN` instead of `%TOKEN%`

```sh
curl -k https://38140ecd-e8d7-4fff-be52-24629c40cdac.k8s.ondigitalocean.com/api/v1/namespaces/default/pods --header "Authorization: Bearer %TOKEN%"
```

```sh
curl -k https://38140ecd-e8d7-4fff-be52-24629c40cdac.k8s.ondigitalocean.com/api/v1/namespaces/kube-system/pods --header "Authorization: Bearer %TOKEN%"
```


<!-- NAV-BOTTOM -->
---

[&larr; Practical - Role and RoleBinding](./role-rolebinding.md) &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Overview of Service Accounts &rarr;](./service-account.md)

[&#8962; All Domains](../README.md)
<!-- /NAV-BOTTOM -->
