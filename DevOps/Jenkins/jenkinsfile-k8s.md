pipeline {
    agent {
        label 'linux-node'
    }
    stages {
        stage('Hello') {
            steps {
     withKubeConfig([credentialsId: 'kube', serverUrl: 'https://192.168.1.130:6443']) {
      sh 'kubectl get po'
    }

    }
            }
        }
}
