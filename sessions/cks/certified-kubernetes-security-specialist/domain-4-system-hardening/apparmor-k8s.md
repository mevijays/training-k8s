<!-- NAV-TOP -->
# AppArmor and Kubernetes

[&larr; Practical - AppArmor](./apparmor.md) &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Configuring containerd and runc &rarr;](./oci.md)

---
<!-- /NAV-TOP -->

#### Create a Sample Profile:
```sh
apparmor_parser -q <<EOF
#include <tunables/global>

profile k8s-apparmor-example-deny-write flags=(attach_disconnected) {
  #include <abstractions/base>

  file,

  # Deny all file writes.
  deny /** w,
}
EOF
```
#### Verify the status of the profile:
```sh
aa-status
```

#### Sample YAML File based on Host PID:
```sh
cd /root
```
```sh
nano hello-armor.yaml
```
```sh
apiVersion: v1
kind: Pod
metadata:
  name: hello-apparmor
spec:
  securityContext:
    appArmorProfile:
      type: Localhost
      localhostProfile: k8s-apparmor-example-deny-write
  containers:
  - name: hello
    image: busybox
    command: [ "sh", "-c", "echo 'Hello AppArmor!' && sleep 1h" ]
```
```sh
kubectl apply -f hello-armor.yaml
```

#### Verification Stage:
```sh
kubectl exec -it hello-apparmor -- sh
touch /tmp/file.txt
```


<!-- NAV-BOTTOM -->
---

[&larr; Practical - AppArmor](./apparmor.md) &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Configuring containerd and runc &rarr;](./oci.md)

[&#8962; All Domains](../README.md)
<!-- /NAV-BOTTOM -->
