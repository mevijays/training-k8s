# Hostpath storage lab
- Create hostpath dir in worker node   
SSH in to worker node, run these commands
```
sudo mkdir /srv/app-data
sudo chmod 777 /srv/app-data
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
