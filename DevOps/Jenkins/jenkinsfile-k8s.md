## deploying Jenkins

Values file.

```yaml
controller:
  adminUser: "admin"
  adminPassword: "password"
  installPlugins:
    - kubernetes:4029.v5712230ccb_f8
    - workflow-aggregator:596.v8c21c963d92d
    - git:5.1.0
    - configuration-as-code:1670.v564dc8b_982d0
  additionalPlugins: []
  ingress:
    enabled: true
    apiVersion: 'networking.k8s.io/v1'
    annotations:
     cert-manager.io/cluster-issuer: le-issuer
    ingressClassName: nginx
    hostName: jenkins.k8s.mevijay.dev
    tls:
     - secretName: jenkins-tls
       hosts:
         - jenkins.k8s.mevijay.dev
agent:
  additionalContainers:
    - sideContainerName: dind
      image: docker
      tag: dind
      command: dockerd-entrypoint.sh
      args: ""
      privileged: true
      resources:
        requests:
          cpu: 500m
          memory: 1Gi
        limits:
          cpu: 1
          memory: 2Gi
additionalAgents:
  maven:
    podName: maven
    customJenkinsLabels: maven
    # An example of overriding the jnlp container
    # sideContainerName: jnlp
    image: jenkins/jnlp-agent-maven
    tag: latest
persistence:
  storageClass: ""
  size: "8Gi"

```

Deploy

```bash
helm repo add jenkins https://charts.jenkins.io 
helm install jenkins jenkins/jenkins --namespace public --create-namespace -f jenkins-values.yaml --version 4.11.1
```
Create a serviceAccount and provide privileges
```bash
kubectl create sa jenkins-ci -n public
kubectl create clusterrolebinding jenkins-ci --clusterrole=cluster-admin --serviceaccount=public:jenkins-ci -n public
```
