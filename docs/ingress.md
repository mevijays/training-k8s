# Create ingress
### Creating nginx ingress rule for hostname abc.com and service webcm on port 8080 without ssl.

```
kubectl create ingress webcm --class=nginx --rule="abc.com/*=webcm:8080"
```
#### Creating nginx ingress rule for hostname abc.com and service webcm on port 8080. using selfsigned certificate.   
- generate certificate
```
openssl req -subj '/CN=abc.com/O=abc ltd/C=IN' -new -newkey rsa:2048 -sha256 -days 365 -nodes -x509 -keyout cert.key -out cert.pem
```  
- create secret
```
kubectl create secret tls abc-tls --cert=cert.pem --key=cert.key
```
- create ingress with secret
```
kubectl create ingress webcm --class=nginx --rule="abc.com/*=webcm:8080,tls=abc-tls"
```
### Creating nginx ingress rule for hostname abc.com and service webcm on port 8080. using letsencrypt TLS cluster issuer.
```
kubectl create ingress webcm --class=nginx --rule="abc.com/*=webcm:8080,tls=abc-tls" --annotation="cert-manager.io/cluster-issuer=le-issuer
```

### Creating ingress with selfsigned tls and rewrite path
```
kubectl create ingress webcm --class=nginx --rule=ckatcswebcm.lab/hello*=webcm:80,tls=test-tls --annotation="nginx.ingress.kubernetes.io/rewrite-target=/"
```
