<!-- NAV-TOP -->
# Downsides - Static Token Authentication

[&larr; Static Token Authentication](./token-authentication.md) &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Implementing X509 Client Authentication &rarr;](./certificate-auth-k8s.md)

---
<!-- /NAV-TOP -->

#### Step 1 Remove Token for BOB user

From the below file, remove the line associated with the Bob user
```sh
nano /root/token.csv
```

#### Step 2 - Authenticate with BOB token to API Server

```sh
curl -k --header "Authorization: Bearer Dem0Passw0rd#" https://localhost:6443

kubectl get secret --server=https://localhost:6443 --token Dem0Passw0rd# --insecure-skip-tls-verify
```
#### Step 3 - Remove the Static Token File Authentication

```sh
nano /etc/systemd/system/kube-apiserver.service
```

Remove the --token-auth option

```sh
systemctl daemon-reload
systemctl restart kube-apiserver
```


<!-- NAV-BOTTOM -->
---

[&larr; Static Token Authentication](./token-authentication.md) &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Implementing X509 Client Authentication &rarr;](./certificate-auth-k8s.md)

[&#8962; All Domains](../README.md)
<!-- /NAV-BOTTOM -->
