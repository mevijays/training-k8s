# Flux cd
## Installation with azure devops repo
```bash
echo <azureRepoPAT> | flux bootstrap git --token-auth=true --url=<azurerepourl>   --branch=main  --path=clusters/my-cluster 
```
