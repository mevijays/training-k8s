
 ```mermaid
       gitGraph
        commit id: "Start"
        commit id: "Branch from main"
        branch develop
        branch hotfix
        checkout hotfix
        commit
        checkout develop
        commit
        commit id:"ash" tag:"merge to develop"
        branch featureB
        checkout featureB
        commit tag:"test"
        checkout main
        checkout hotfix
        commit type:NORMAL id:"test2"
        checkout hotfix
        merge develop
        checkout develop
        commit type:REVERSE
        commit id:"vijay"
        checkout featureB
        commit
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
        commit id:"merge to main"
        checkout develop
        merge main
        commit
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
