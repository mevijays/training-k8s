<!-- NAV-TOP -->
# Audit Logging

[&larr; Introduction to Sysdig](./sysdig.md) &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Reference - Falco Installation from Packages &rarr;](./falco-install.md)

---
<!-- /NAV-TOP -->

#### Step 1 Create a directory for storing audit logs and audit policy:
```sh
cd /etc/kubernetes/
mkdir audit
```
#### Step 2 - Mount the directory as HostPath Volumes in kube-apiserver:
```sh
  - hostPath:
      path: /etc/kubernetes/audit
      type: DirectoryOrCreate
    name: auditing

    - mountPath: /etc/kubernetes/audit
      name: auditing
```
#### Step 3 - Add Auditing Related Configuration in kube-apiserver:
```sh
- --audit-policy-file=/etc/kubernetes/audit/audit-policy.yaml
- --audit-log-path=/etc/kubernetes/audit/audit.log
```

#### Our Final Audit Policy:
```sh
apiVersion: audit.k8s.io/v1
kind: Policy
omitStages:
  - "RequestReceived"

rules:

  - level: None
    resources:
    - group: ""
      resources: ["secrets"]
    namespaces: ["kube-system"]

  - level: None
    users: ["system:kube-controller-manager"]
    resources:
    - group: ""
      resources: ["secrets"]

  - level: RequestResponse
    resources:
    - group: ""
      resources: ["secrets"]
```


<!-- NAV-BOTTOM -->
---

[&larr; Introduction to Sysdig](./sysdig.md) &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Reference - Falco Installation from Packages &rarr;](./falco-install.md)

[&#8962; All Domains](../README.md)
<!-- /NAV-BOTTOM -->
