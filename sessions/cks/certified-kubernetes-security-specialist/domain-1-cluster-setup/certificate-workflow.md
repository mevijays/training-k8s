<!-- NAV-TOP -->
# Workflow - Issuance of Signed Certificates

[&larr; Configure Certificate Authority](./configure-ca.md) &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [etcd - Transport Security with HTTPS &rarr;](./etcd-https.md)

---
<!-- /NAV-TOP -->

#### Step 1 - Generate Client CSR and Client Key:
```sh
cd /root/certificates
```
```sh
openssl genrsa -out client.key 2048

openssl req -new -key client.key -subj "/CN=devuser" -out client.csr
```
#### Step 2 - Sign the Client CSR with Certificate Authority
```sh
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -out client.crt -days 1000
```
#### Step 3 - Verify Client Certificate
```sh
openssl x509 -in client.crt -text -noout

openssl verify -CAfile ca.crt client.crt
```

#### Step 4 - Delete the Client Certificate and Key
```sh
rm -f client.crt client.key client.csr
```


<!-- NAV-BOTTOM -->
---

[&larr; Configure Certificate Authority](./configure-ca.md) &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [etcd - Transport Security with HTTPS &rarr;](./etcd-https.md)

[&#8962; All Domains](../README.md)
<!-- /NAV-BOTTOM -->
