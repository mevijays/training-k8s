
 ```mermaid
       gitGraph
        commit id: "Start"
        commit id: "Branch from main"
        branch develop
        branch hotfix
        checkout hotfix
        commit id:"fix-A"
        checkout develop
        commit id:"ash" tag:"merge to develop"
        branch featureB
        checkout featureB
        commit id:"JIRA-A"
        checkout main
        checkout hotfix
        commit type:NORMAL id:"fix-B"
        checkout hotfix
        merge develop
        checkout develop
        commit type:REVERSE
        checkout featureB
        commit id:"JIRA-B"
        checkout main
        merge hotfix
        commit
        checkout featureB
        commit
        checkout develop
        commit
        branch featureA
        commit
        checkout featureA
        commit
        checkout featureB
        commit
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
