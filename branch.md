
 ```mermaid
       gitGraph
        commit id: "Start"
        commit id: "Branch from main"
        branch develop
        branch hotfix
        checkout hotfix
        commit id:"fix-A"
        checkout develop
        commit id:"merge to develop" tag:"merge to develop"
        branch featureB
        checkout featureB
        commit id:"JIRA-A"
        checkout main
        checkout hotfix
        commit type:NORMAL id:"fix-B"
        checkout hotfix
        merge develop
        checkout develop
        checkout featureB
        commit id:"JIRA-B"
        checkout main
        merge hotfix
        commit
        checkout featureB
        commit id:"JIRA-C"
        checkout develop
        commit
        branch featureA
        commit id:"JIRA-CRC"
        checkout featureA
        commit id:"JIRA-RCL"
        checkout featureB
        commit id:"JIRA-D"
        checkout develop
        merge featureA
        checkout develop
        commit id:"create release"
        branch release
        checkout release
        commit
        branch bugfix
        checkout bugfix
        commit
        checkout release
        merge bugfix
        checkout main
        commit id:"release-v1" tag:"release-v1"
        checkout release
        merge main
        checkout develop
        merge release
        commit
        checkout main
        commit id:"releasev2" tag:"release-v2"
 ```
