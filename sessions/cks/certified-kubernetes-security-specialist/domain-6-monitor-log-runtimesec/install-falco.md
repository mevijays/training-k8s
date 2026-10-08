<!-- NAV-TOP -->
# Installing Falco

&larr; _Start of domain_ &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Falco - Practical &rarr;](./falco-practical.md)

---
<!-- /NAV-TOP -->

### Falco Documentation:

https://falco.org/docs/getting-started/installation/

#### Installation Steps:
```sh
curl -fsSL https://falco.org/repo/falcosecurity-packages.asc | \
  sudo gpg --dearmor -o /usr/share/keyrings/falco-archive-keyring.gpg

echo "deb [signed-by=/usr/share/keyrings/falco-archive-keyring.gpg] \
  https://download.falco.org/packages/deb stable main" | \
  sudo tee /etc/apt/sources.list.d/falcosecurity.list

sudo apt update
sudo apt install -y falco
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
