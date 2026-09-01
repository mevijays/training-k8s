<!-- NAV-TOP -->
# Falco Rule for /dev/mem

[&larr; Writing Custom Falco Rules and Macros](./writing-falco-rules.md) &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Falco Configuration File &rarr;](./falco-config-file.md)

---
<!-- /NAV-TOP -->

### Verify /dev/mem access
```sh
kubectl run nginx-pod --image=nginx
kubectl exec -it nginx-pod -- bash
ls -l /dev

kubectl run privileged-pod --image=nginx --privileged
kubectl exec -it privileged-pod -- bash
ls -l /dev
```
### Rule to Alert /dev/mem access from Container

```sh
- rule: Detect /dev/mem Access from Containers
  desc: Detect processes inside containers attempting to access /dev/mem
  condition: >
    (open_read or open_write) and
    fd.name=/dev/mem and container.id != host
  output: >
    "Container: %container.id and %container.name attempted to access /dev/mem"
  priority: CRITICAL
```

### Testing
```sh
kubectl exec -it privileged-pod -- bash

cat /dev/mem
```


### Find the Pod from Container ID
```sh
 kubectl get pods -A -o json > pods.json

 nano pods.json
```
 Search using `CTRL+W` and add container ID


<!-- NAV-BOTTOM -->
---

[&larr; Writing Custom Falco Rules and Macros](./writing-falco-rules.md) &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Falco Configuration File &rarr;](./falco-config-file.md)

[&#8962; All Domains](../README.md)
<!-- /NAV-BOTTOM -->
