<!-- NAV-TOP -->
# Static Token Authentication

[&larr; Transport Security for API Server](./apiserver-https.md) &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Downsides - Static Token Authentication &rarr;](./downside-token-auth.md)

---
<!-- /NAV-TOP -->

#### Format of Static Token File:
```sh
token,user,uid,"group1,group2,group3"
```
#### Create a token file with required data:
```sh
nano /root/token.csv
```
```sh
Dem0Passw0rd#,bob,01,admins
```
#### Pass the token auth flag:
  ```sh
nano /etc/systemd/system/kube-apiserver.service
```
```sh
--token-auth-file /root/token.csv
```
```sh
systemctl daemon-reload
systemctl restart kube-apiserver
```
#### Verification:
```sh
curl -k --header "Authorization: Bearer Dem0Passw0rd#" https://localhost:6443

kubectl get secret --server=https://localhost:6443 --token Dem0Passw0rd# --insecure-skip-tls-verify
```
#### Testing:
```sh
kubectl create secret generic my-secret --server=https://localhost:6443 --token Dem0Passw0rd# --insecure-skip-tls-verify
kubectl delete secret my-secret --server=https://localhost:6443 --token Dem0Passw0rd# --insecure-skip-tls-verify
```


<!-- NAV-BOTTOM -->
---

[&larr; Transport Security for API Server](./apiserver-https.md) &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Downsides - Static Token Authentication &rarr;](./downside-token-auth.md)

[&#8962; All Domains](../README.md)
<!-- /NAV-BOTTOM -->
