<!-- NAV-TOP -->
# Installing Falco

&larr; _Start of domain_ &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Falco - Practical &rarr;](./falco-practical.md)

---
<!-- /NAV-TOP -->

### Falco Documentation:

https://falco.org/docs/getting-started/installation/

#### Installation Steps:
```sh
curl -s https://falco.org/repo/falcosecurity-3672BA8F.asc | apt-key add -
echo "deb https://dl.bintray.com/falcosecurity/deb stable main" | tee -a /etc/apt/sources.list.d/falcosecurity.list
apt-get -y install linux-headers-$(uname -r)
apt-get update && apt-get install -y falco
```
#### Start falco:
```sh
falco
```
#### Sample Rules tested:
```sh
kubectl run nginx --image=nginx
kubectl exec -it nginx -- bash
```
```sh
mkdir /bin/tmp-dir
cat /etc/shadow
```


<!-- NAV-BOTTOM -->
---

&larr; _Start of domain_ &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Falco - Practical &rarr;](./falco-practical.md)

[&#8962; All Domains](../README.md)
<!-- /NAV-BOTTOM -->
