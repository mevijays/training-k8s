# yamls 

```
kubectl create deploy webapp --image=nginx:1.22
kubectl expose deploy webapp --port=8080 --target-port=80
kubectl create ingress webapp --class=nginx --rule="abc.lan/*=webappp:80"
```
