podTemplate(label: 'mypod', serviceAccount: 'jenkins-ci', containers: [ 
    containerTemplate(
      name: 'k8s-helm', 
      image: 'sharmavijay86/k8s-helm:v1', 
      command: 'cat', 
      resourceRequestCpu: '100m',
      resourceLimitCpu: '300m',
      resourceRequestMemory: '300Mi',
      resourceLimitMemory: '500Mi',
      ttyEnabled: true
    )
  ],

  volumes: [
    hostPathVolume(mountPath: '/var/run/docker.sock', hostPath: '/var/run/docker.sock'),
    hostPathVolume(mountPath: '/usr/local/bin/helm', hostPath: '/usr/local/bin/helm')
  ]
  ) {
    node('mypod') {
        stage('Get latest version of code') {
          git branch: 'main', credentialsId: 'github', url: 'https://github.com/mevijays/training-k8s'
        }
        stage('Deploy application') {
              container('k8s-helm') {  
                  sh 'ls'
                  sh 'pwd'
                  sh 'kubectl apply -f DevOps/yamls -n app'
               }
            
        }
  
        stage('Check running containers') {
            container('k8s-helm') { 
                sh 'kubectl get pods -n app'  
            }
            container('k8s-helm') { 
                sh 'helm ls'
            }
        }         
    }
}
