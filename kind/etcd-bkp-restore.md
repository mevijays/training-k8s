# ETCD back and restore process

### Backup process   
- Bellow script can perform a snapshot on host machine running kind container
```
#!/bin/bash
if [[ ! -d "ETCD" ]]
then
    mkdir ETCD
fi
NAME=$(kind get clusters)-control-plane
certfile="/etc/kubernetes/pki/etcd/server.crt"
cafile="/etc/kubernetes/pki/etcd/ca.crt"
keyfile="/etc/kubernetes/pki/etcd/server.key"
if [[ ! -f "ETCD/$certfile" ]]
then
docker cp $NAME:$certfile  ETCD/
fi
if [[ ! -f "ETCD/$cafile" ]]
then
docker cp $NAME:$cafile  ETCD/
fi
if [[ ! -f "ETCD/$keyfile" ]]
then
docker cp $NAME:$keyfile  ETCD/
fi
if [[ ! -f "/usr/bin/etcdctl" ]]
then    
        wget https://github.com/etcd-io/etcd/releases/download/v3.5.6/etcd-v3.5.6-linux-amd64.tar.gz
        tar -xvf etcd-v3.5.6-linux-amd64.tar.gz
        mv etcd-v3.5.6-linux-amd64/etcdctl /usr/local/bin/
fi      

ETCDCTL_API=3 etcdctl --endpoints https://127.0.0.1:2379 snapshot save kind.backup --cacert="ETCD/ca.crt" --cert="ETCD/server.crt" --key="ETCD/server.key"
```
### Restore process
- Copy the binary and snpshot file inside the container
```
docker cp /usr/local/bin/etcdctl kind-control-plane:/
docker cp kind.backup kind-control-plane:/
```
- Login inside kind container
```
docker exec -it kind-control-plane bash
```
- Perform restore steps as bellow
```
mv /etc/kubernetes/manifests/etcd.yaml /
rm -rf /var/lib/etcd
ETCDCTL_API=3 /etcdctl --data-dir=/var/lib/etcd snapshot restore /kind.backup
mv /etcd.yaml /etc/kubernetes/manifests/etcd.yaml
```

