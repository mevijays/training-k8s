<!-- NAV-TOP -->
# Overview of Projected Volumes

[&larr; Practical - Upgrade Worker Node](./upgrade-kubeadm-worker.md) &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Mounting Service Accounts using Projected Volumes &rarr;](./sa-projectedvolume.md)

---
<!-- /NAV-TOP -->

### Documentation Referred:

https://kubernetes.io/docs/concepts/storage/projected-volumes/

### Create Secret and ConfigMap

```sh
kubectl create secret generic firstsecret --from-literal=dbpassword=mypassword123

kubectl create configmap my-config --from-literal=config-key="This is a config value"
```

### Create Pod with Projected Volume
```sh
apiVersion: v1
kind: Pod
metadata:
  name: volume-test
spec:
  containers:
  - name: container-test
    image: busybox:1.37
    command: ["sleep", "3600"]
    volumeMounts:
    - name: all-in-one
      mountPath: "/projected-volume"
      readOnly: true   
  volumes:
  - name: all-in-one
    projected:
      sources:
      - secret:
          name: firstsecret 
          items:
            - key: dbpassword
              path: my-username
      - configMap:
          name: my-config
          items:
            - key: config-key
              path: my-config
```
```sh
kubectl delete -f projected-volume.yaml
```

```sh
kubectl exec -it volume-test -- sh

cd /projected-volume


<!-- NAV-BOTTOM -->
---

[&larr; Practical - Upgrade Worker Node](./upgrade-kubeadm-worker.md) &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Mounting Service Accounts using Projected Volumes &rarr;](./sa-projectedvolume.md)

[&#8962; All Domains](../README.md)
<!-- /NAV-BOTTOM -->
