# jenkins pipeline related content
The service account we are using in this Jenkinsfile is seperate serviceaccount which we can create in same project or namespace where the jenkins master is running and build agent will come up. Build agent uses this SA ondemand hence we can configure rolebindings based on what task we want the build agentt o able to perform.
