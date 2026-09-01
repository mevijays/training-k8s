<!-- NAV-TOP -->
# Reference - Ingress Resource Rules

[&larr; Reference - kubeadm Installation Steps](./kubeadm.md) &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Reference - Ingress Controller and Name-Based Routing &rarr;](./ingress-controller.md)

---
<!-- /NAV-TOP -->

#### Documentation Referred:

https://kubernetes.io/docs/concepts/services-networking/ingress/#name-based-virtual-hosting

### Ingress Resource - Rule 1
```sh
kubectl create ingress --help

kubectl first  ingress first-ingress --rule="example.internal/*=example-service:80"

kubectl describe ingress first-ingress
```
### Ingress Resource - Rule 2
```sh
kubectl create ingress second-ingress --rule="example.internal/*=example-service:80" --rule="demo.internal/*=demo-service:80"
```

### Generating Manifest File for Ingress Resource

```sh
kubectl create ingress second-ingress --rule="example.internal/*=example-service:80" --rule="demo.internal/*=demo-service:80" --dry-run=client -o yaml
```


<!-- NAV-BOTTOM -->
---

[&larr; Reference - kubeadm Installation Steps](./kubeadm.md) &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Reference - Ingress Controller and Name-Based Routing &rarr;](./ingress-controller.md)

[&#8962; All Domains](../README.md)
<!-- /NAV-BOTTOM -->
