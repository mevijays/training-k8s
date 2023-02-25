# jenkins pipeline related content
The service account we are using in this Jenkinsfile is seperate serviceaccount which we can create in same project or namespace where the jenkins master is running and build agent will come up. Build agent uses this SA ondemand hence we can configure rolebindings based on what task we want the build agentt o able to perform.
Values file.

```python
#jenkins-valus.yaml
controller:
  #  serviceType: LoadBalancer
  adminPassword: ''
  #additionalPlugins:
  #- git:4.11.5
  ingress:
    enabled: true
    paths: []
    apiVersion: "networking.k8s.io/v1"
    labels: {}
    annotations: 
       kubernetes.io/ingress.class: nginx
       kubernetes.io/tls-acme: "true"
       cert-manager.io/cluster-issuer: letsencrypt-staging
    hostName: jenkins.k8s.mevijay.dev
    tls:
      - secretName: jenkins-tls
        hosts:
          - jenkins.k8s.mevijay.dev
additionalAgents:
  maven:
    podName: maven
    customJenkinsLabels: maven
    # An example of overriding the jnlp container
    # sideContainerName: jnlp
    image: jenkins/jnlp-agent-maven
    tag: latest
  python:
    podName: python
    customJenkinsLabels: python
    sideContainerName: python
    image: python
    tag: "3"
    command: "/bin/sh -c"
    args: "cat"
    TTYEnabled: true

```

Deploy

```python
helm repo add jenkins https://charts.jenkins.io 
helm install jenkins jenkins/jenkins --namespace public --create-namespace -f jenkins-values.yaml
```
