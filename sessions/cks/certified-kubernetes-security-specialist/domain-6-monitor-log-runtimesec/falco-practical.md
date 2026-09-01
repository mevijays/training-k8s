<!-- NAV-TOP -->
# Falco - Practical

[&larr; Installing Falco](./install-falco.md) &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Writing Custom Falco Rules and Macros &rarr;](./writing-falco-rules.md)

---
<!-- /NAV-TOP -->

### Monitor Falco Logs (Terminal Tab 1)
```sh
systemctl status falco 

journalctl -u falco-modern-bpf.service -f
```
### Testing
```sh
cat /etc/shadow

kubectl run nginx-pod --image=nginx

kubectl exec -it nginx-pod -- bash
```


<!-- NAV-BOTTOM -->
---

[&larr; Installing Falco](./install-falco.md) &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Writing Custom Falco Rules and Macros &rarr;](./writing-falco-rules.md)

[&#8962; All Domains](../README.md)
<!-- /NAV-BOTTOM -->
