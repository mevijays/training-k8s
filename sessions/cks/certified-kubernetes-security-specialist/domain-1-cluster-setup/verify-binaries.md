<!-- NAV-TOP -->
# Verifying Platform Binaries

[&larr; Kubelet Security](./kubelet-security.md) &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Practical - Ingress with TLS &rarr;](./ingress-security.md)

---
<!-- /NAV-TOP -->

  #### Kubernetes GitHub Repository:

  https://github.com/kubernetes/kubernetes/releases

  #### Step 1 - Download Binaries:
  ```sh
 wget https://dl.k8s.io/v1.33.0-alpha.1/kubernetes-client-darwin-arm64.tar.gz
  ```

  #### Step 2 - Verify the Message Digest:
  ```sh
  sha512sum kubernetes-server-linux-amd64.tar.gz
  ```


<!-- NAV-BOTTOM -->
---

[&larr; Kubelet Security](./kubelet-security.md) &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Practical - Ingress with TLS &rarr;](./ingress-security.md)

[&#8962; All Domains](../README.md)
<!-- /NAV-BOTTOM -->
