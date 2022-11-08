# Hostpath storage lab
- Create hostpath dir in worker node   
SSH in to worker node, run these commands
```
sudo mkdir /srv/app-data
sudo chmod 777 /srv/app-data
```
- Download all yaml files one by one 
```
wget https://raw.githubusercontent.com/mevijays/training-k8s/main/TCS/CKA/yamls/hostpath/pv-volume.yaml
wget https://raw.githubusercontent.com/mevijays/training-k8s/main/TCS/CKA/yamls/hostpath/pv-claim.yaml
wget https://raw.githubusercontent.com/mevijays/training-k8s/main/TCS/CKA/yamls/hostpath/deployment.yaml
```
- Create a PV
```
kubectl apply -f pv-volume.yaml
```
- Create a PVC
```
kubectl apply -f pv-claim.yaml
```
- Create deployment and use pvc mount
```
kubectl apply -f deployment.yaml
```
