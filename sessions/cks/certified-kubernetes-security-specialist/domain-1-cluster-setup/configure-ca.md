<!-- NAV-TOP -->
# Configure Certificate Authority

[&larr; Configure etcd Binaries](./install-etcd.md) &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Workflow - Issuance of Signed Certificates &rarr;](./certificate-workflow.md)

---
<!-- /NAV-TOP -->

#### Step 1 - Creating a private key for Certificate Authority:
```sh
mkdir /root/certificates

cd /root/certificates
```

#### Step 2 -  Creating Private Key and CSR:
```sh
openssl genrsa -out ca.key 2048

openssl req -new -key ca.key -subj "/CN=KUBERNETES-CA" -out ca.csr
```
#### Step 3 - Self-Sign the CSR:
```sh
openssl x509 -req -in ca.csr -signkey ca.key -out ca.crt -days 1000
```
#### Step 4 - Remove the CSR
```sh
rm -f ca.csr
```
#### Step 5 - Check Contents of Certificate
```sh
openssl x509 -in ca.crt -text -noout
```


<!-- NAV-BOTTOM -->
---

[&larr; Configure etcd Binaries](./install-etcd.md) &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Workflow - Issuance of Signed Certificates &rarr;](./certificate-workflow.md)

[&#8962; All Domains](../README.md)
<!-- /NAV-BOTTOM -->
