# Ingress in AWS EKS
## Deploy nginx ingress controller
```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.12.0-beta.0/deploy/static/provider/aws/deploy.yaml
```

## Deploy ingress
```bash
kubectl create ingress webcm --class=nginx --rule="abc.com/*=webcm:8080,tls=abc-tls"
```