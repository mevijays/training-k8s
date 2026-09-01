<!-- NAV-TOP -->
# Falco Configuration File

[&larr; Falco Rule for /dev/mem](./falco-mem-rule.md) &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Introduction to Sysdig &rarr;](./sysdig.md)

---
<!-- /NAV-TOP -->

### Documentation Referred:

https://github.com/falcosecurity/falco/blob/0.40.0/falco.yaml

### Commands Used for Testing
```sh
cd /etc/falco
cp falco.yaml falco.yaml.bak
```
```sh
nano falco.yaml
```
`CTRL+W` to search for `syslog_output` and replace true to false

```sh
syslog_output:
  enabled: false
```

```sh
systemctl restart falco
```

### Start Falco manually

```sh
systemctl stop falco

falco

cat /etc/shadow
```

### Revert the Changes
```sh
rm -f falco.yaml

mv falco.yaml.bak falco.yaml

systemctl restart falco

cat /etc/shadow
```


<!-- NAV-BOTTOM -->
---

[&larr; Falco Rule for /dev/mem](./falco-mem-rule.md) &nbsp;&nbsp;|&nbsp;&nbsp; [**Domain Home**](./Readme.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Introduction to Sysdig &rarr;](./sysdig.md)

[&#8962; All Domains](../README.md)
<!-- /NAV-BOTTOM -->
