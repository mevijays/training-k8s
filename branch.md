
 ```mermaid
 %%{init: { 'logLevel': 'debug', 'theme': 'default' , 'themeVariables': {
              'tagLabelColor': '#ff0000',
              'tagLabelBackground': '#00ff00',
              'tagLabelBorder': '#0000ff',
              'tagLabelFontSize': '18px',
              'git2': '#ff0000',
              'git3': '#00FFFF',
              'git4': '#00FFFF',
              'git5': '#228B22',
              'commitLabelColor': '#000000',
              'commitLabelBackground': '#00ff00',
              'commitLabelFontSize': '14px'
       } } }%%
       gitGraph
        commit id: "Start"
        commit id: "Branch from main"
        branch develop
        branch hotfix
        checkout hotfix
        commit id:"fix-A"
        checkout develop
        commit id:"merge to develop" type: HIGHLIGHT
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
        checkout featureB
        commit id:"JIRA-C"
        checkout develop
        commit id:"feature checkout"
        branch featureA
        commit id:"JIRA-CRC"
        checkout featureA
        commit id:"JIRA-RCL"
        checkout featureB
        commit id:"JIRA-D" type: REVERSE
        checkout develop
        merge featureA
        checkout develop
        commit id:"create release"
        branch release
        checkout release
        commit id:"bugfix checkout"
        branch bugfix
        checkout bugfix
        commit id:"BUGFIX-A"
        checkout release
        merge bugfix
        checkout main
        commit id:"release-v1" tag:"release-v1" type: HIGHLIGHT
        checkout release
        merge main
        checkout develop
        merge release
        commit
        checkout main
        commit id:"releasev2" tag:"release-v2" type: REVERSE
 ```
