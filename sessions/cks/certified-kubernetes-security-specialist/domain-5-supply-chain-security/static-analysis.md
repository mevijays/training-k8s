<!-- NAV-TOP -->
# Static Analysis

[&larr; Scanning K8s Clusters for Security Best Practices](./kube-bench.md) &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Dockerfile - Security Best Practices &rarr;](./dockerfile-best-practice.md)

---
<!-- /NAV-TOP -->

### Documentation:

https://github.com/bridgecrewio/checkov

#### Install the Tool:
```sh
apt install python3-pip
pip3 install checkov
```
#### Our Demo Manifest File:
```sh
nano pod-priv.yaml
```
```sh
apiVersion: v1
kind: Pod
metadata:
  name: privileged
spec:
  containers:
  - image: nginx
    name: demo-pod
    securityContext:
      privileged: true

```
#### Perform a static analysis:
```sh
checkov -f pod-priv.yaml
```


<!-- NAV-BOTTOM -->
---

[&larr; Scanning K8s Clusters for Security Best Practices](./kube-bench.md) &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Dockerfile - Security Best Practices &rarr;](./dockerfile-best-practice.md)

[&#8962; All Domains](../README.md)
<!-- /NAV-BOTTOM -->
