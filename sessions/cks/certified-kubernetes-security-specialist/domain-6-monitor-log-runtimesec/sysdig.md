<!-- NAV-TOP -->
# Introduction to Sysdig

[&larr; Falco Configuration File](./falco-config-file.md) &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Audit Logging &rarr;](./audit-log-detailed.md)

---
<!-- /NAV-TOP -->

### Documentation:

https://github.com/draios/sysdig/wiki/Sysdig-User-Guide

#### Install sysdig:
```sh
apt install sysdig
```
#### Commands Used:
```sh
sysdig
sysdig proc.name=nano
sysdig proc.name=cat or proc.name=nano
```
```sh
sysdig -l
sysdig proc.name=cat and container.name!=host
```
```sh
csysdig
```
#### Sysdig Chisels:
```sh
sysdig -cl
sysdig -c topprocs_cpu
sysdig -c spectrogram
sysdig -c spy_users
sysdig -c ps
```


<!-- NAV-BOTTOM -->
---

[&larr; Falco Configuration File](./falco-config-file.md) &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Audit Logging &rarr;](./audit-log-detailed.md)

[&#8962; All Domains](../README.md)
<!-- /NAV-BOTTOM -->
