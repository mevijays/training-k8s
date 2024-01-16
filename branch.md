
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
# helm release  provider for gke

```yaml
provider "helm" {
  kubernetes {
    config_path = "~/.kube/config"
  }

  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    args = ["gcloud", "auth", "application-default", "print-access-token"]
    env = {
      GOOGLE_APPLICATION_CREDENTIALS = "/path/to/service-account-key.json"
    }
  }
}

```
# dynamic dns provisioning 

To integrate GKE with Cloud DNS for automatic provisioning of DNS records when creating an ingress, you can use the ExternalDNS controller. ExternalDNS is a Kubernetes controller that monitors ingress resources and creates DNS records in Cloud DNS accordingly.

Here are the steps to set up ExternalDNS with GKE and Cloud DNS:

1. Install and configure the `gcloud` command-line tool if you haven't already.

2. Install ExternalDNS using Helm. Run the following commands:

```shell
$ helm repo add bitnami https://charts.bitnami.com/bitnami
$ helm install external-dns bitnami/external-dns \
  --set provider=google \
  --set google.project=<YOUR_PROJECT_ID> \
  --set google.serviceAccountSecret=<YOUR_SERVICE_ACCOUNT_SECRET_NAME> \
  --set domainFilters[0]=<YOUR_DOMAIN>
```

Replace `<YOUR_PROJECT_ID>` with your Google Cloud project ID, `<YOUR_SERVICE_ACCOUNT_SECRET_NAME>` with the name of the Kubernetes secret containing the service account key for ExternalDNS, and `<YOUR_DOMAIN>` with the domain you want to manage.

3. Create a service account for ExternalDNS with the necessary permissions. Run the following command:

```shell
$ gcloud iam service-accounts create external-dns \
  --display-name "ExternalDNS Service Account"
```

4. Generate a key for the service account and create a Kubernetes secret. Run the following commands:

```shell
$ gcloud iam service-accounts keys create key.json \
  --iam-account=external-dns@<YOUR_PROJECT_ID>.iam.gserviceaccount.com

$ kubectl create secret generic external-dns \
  --from-file=key.json
```

Replace `<YOUR_PROJECT_ID>` with your Google Cloud project ID.

5. Grant the necessary permissions to the service account. Run the following command:

```shell
$ gcloud projects add-iam-policy-binding <YOUR_PROJECT_ID> \
  --member=serviceAccount:external-dns@<YOUR_PROJECT_ID>.iam.gserviceaccount.com \
  --role=roles/dns.admin
```

Replace `<YOUR_PROJECT_ID>` with your Google Cloud project ID.

6. Update your ingress resources with the desired hostname. For example:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-ingress
spec:
  rules:
    - host: example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: my-service
                port:
                  number: 80
```

7. Apply the updated ingress resource. Run the following command:

```shell
$ kubectl apply -f ingress.yaml
```

ExternalDNS will monitor the ingress resources and automatically create DNS records in Cloud DNS for the specified hostname.

Note: Make sure you have the necessary permissions to manage DNS records in Cloud DNS.
