<!-- NAV-TOP -->
# Configure etcd Binaries

&larr; _Start of domain_ &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Configure Certificate Authority &rarr;](./configure-ca.md)

---
<!-- /NAV-TOP -->

#### Step 1: Create the Base Binaries Directory

```sh
mkdir /root/binaries

cd /root/binaries
```
#### Step 2: Download and Copy the ETCD Binaries to Path
```sh
wget https://github.com/etcd-io/etcd/releases/download/v3.5.18/etcd-v3.5.18-linux-amd64.tar.gz

tar -xzvf etcd-v3.5.18-linux-amd64.tar.gz

cd /root/binaries/etcd-v3.5.18-linux-amd64/

cp etcd etcdctl /usr/local/bin/
```
#### Step 3: Start etcd
```sh
cd /tmp
etcd
```

#### Step 4: Verification - Store and Fetch Data from etcd
```sh
etcdctl put key1 "value1"
```
```sh
 etcdctl get key1
 ```


<!-- NAV-BOTTOM -->
---

&larr; _Start of domain_ &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Configure Certificate Authority &rarr;](./configure-ca.md)

[&#8962; All Domains](../README.md)
<!-- /NAV-BOTTOM -->
