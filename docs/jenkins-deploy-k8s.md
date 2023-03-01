# Jenkins in k8s
The deployment usually gives problem with kubeamd k8s hence use this with rancher kubernetes.

## Deploy Jenkins
create a jenkins-values.yaml file

```
controller:
  adminPassword: "redhat123"
  #additionalPlugins:
  #- git:4.11.5
  ingress:
    enabled: true
    apiVersion: "networking.k8s.io/v1"
    annotations:
       kubernetes.io/ingress.class: nginx
       cert-manager.io/cluster-issuer: letsencrypt-staging
    hostName: jenkins.mylab.lan
    tls:
      - secretName: jenkins-tls
        hosts:
          - jenkins.mylab.lan
```

Apply changes

```
# add helm repo 
helm repo add jenkins https://charts.jenkins.io
# create namespace
kubectl create ns devops
# install
helm install jenkins -f jenkins-values.yaml  jenkins/jenkins -n devops
# upgrade
helm upgrade jenkins -f jenkins-values.yaml  jenkins/jenkins -n devops
```
