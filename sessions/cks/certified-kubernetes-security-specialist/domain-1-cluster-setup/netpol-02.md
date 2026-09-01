<!-- NAV-TOP -->
# Network Policies - Except, Port and Protocol

[&larr; Practical - Network Policies](./netpol-practical.md) &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Reference - systemd Unit Files for etcd &rarr;](./systemd.md)

---
<!-- /NAV-TOP -->

### Example 1 - Except Field

```sh
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: except
spec:
  podSelector: 
    matchLabels:
      role: database
  ingress:
  - from:
    - ipBlock:
        cidr: 172.17.0.0/16
        except: 
        - 172.17.1.0/24
  policyTypes:
  - Ingress
```
```sh
kubectl create -f except.yaml
```


### Example 2 - Port and Protocol
```sh
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: multi-port-egress
  namespace: default
spec:
  podSelector:
    matchLabels:
      role: db
  policyTypes:
    - Egress
  egress:
    - to:
        - ipBlock:
            cidr: 10.0.0.0/24
      ports:
        - protocol: TCP
          port: 32000
          endPort: 32768
```
```sh
kubectl create -f port-proto.yaml
```


<!-- NAV-BOTTOM -->
---

[&larr; Practical - Network Policies](./netpol-practical.md) &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Reference - systemd Unit Files for etcd &rarr;](./systemd.md)

[&#8962; All Domains](../README.md)
<!-- /NAV-BOTTOM -->
