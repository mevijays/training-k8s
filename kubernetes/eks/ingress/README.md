# Ingress in AWS EKS
## Deploy nginx ingress controller
```bash
kubectl apply -f https://raw.githubusercontent.com/mevijays/training-k8s/refs/heads/main/kubernetes/eks/ingress/nginx-ingress-controller.yaml
```

## Deploy ingress
```bash
kubectl create ingress webcm --class=nginx --rule="abc.com/*=webcm:8080,tls=abc-tls"
```