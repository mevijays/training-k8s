# Falco
Network Policies, Pod Security Admission, RBAC and image scanning all try to prevent problems. None of them tell you what is actually happening inside a running container. Falco does detection. It watches every system call on the node in real time and raises an alert when behaviour matches a rule.

## Typical things it catches:

A shell started inside a production container (someone ran kubectl exec, or an attacker got in)
Reads of /etc/shadow, /dev/mem or service-account tokens
Writes to /etc or /usr/bin in a container that should never change
Unexpected outbound connections, privilege escalation, and package managers run at runtime

## How it works:

``kernel syscalls → modern eBPF probe → Falco rule engine (+ K8s metadata) → outputs (stdout, file, HTTP → Falcosidekick → UI / Loki / Slack / SIEM)``

Falco runs as a DaemonSet (one pod per node), because it has to read each node's kernel events.

**The YAML files you need**
File	Purpose
- /etc/falco/falco.yaml	Main config: where alerts go (stdout, file, HTTP), JSON output, minimum priority, which rule files to load
- /etc/falco/falco_rules.yaml	Default rules. Don't edit it, it's replaced on upgrade
- /etc/falco/falco_rules.local.yaml or /etc/falco/rules.d/*.yaml	Your own rules and overrides. In the exam, this is where you edit
- falco-values.yaml (Helm)	The Kubernetes version of the above: driver, JSON output, Falcosidekick, UI, custom rules

A rule has five parts :

rule – the name
desc – what it detects
condition – a filter on system-call fields, built from macros such as spawned_process, open_read and container
output – the alert text, using fields like %proc.cmdline and %k8s.pod.name
priority – from EMERGENCY down to DEBUG

### Method A – Package install on a node (how the CKS exam is set up)
```shell
# 1. Add the repo and install
curl -fsSL https://falco.org/repo/falcosecurity-packages.asc | sudo gpg --dearmor -o /usr/share/keyrings/falco-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/falco-archive-keyring.gpg] https://download.falco.org/packages/deb stable main" \
  | sudo tee /etc/apt/sources.list.d/falcosecurity.list
sudo apt-get update && sudo apt-get install -y falco     # choose "modern eBPF" when prompted

# 2. Check it is running
systemctl status falco-modern-bpf
journalctl -u falco-modern-bpf -f                         # live alerts

# 3. Add your rules
sudo cp falco_rules.local.yaml /etc/falco/falco_rules.local.yaml
sudo falco --dry-run                                      # check that the rules load without errors
sudo systemctl restart falco-modern-bpf

# 4. Send alerts to a file (a common exam task) – edit /etc/falco/falco.yaml:
#    file_output:
#      enabled: true
#      keep_alive: false
#      filename: /var/log/falco-alerts.log
sudo systemctl restart falco-modern-bpf
```

### Method B – Helm on Kubernetes, with a UI (for real clusters and the demo)
```bash
helm repo add falcosecurity https://falcosecurity.github.io/charts && helm repo update
helm install falco falcosecurity/falco -n falco --create-namespace -f falco-values.yaml
kubectl -n falco get pods -o wide        # expect one falco pod per node, plus the sidekick and UI pods
```


falco-values.yaml sets up four things:

The modern eBPF driver, so no kernel module has to be built
JSON output
Falcosidekick with its web UI. The chart points Falco's HTTP output at Falcosidekick automatically.
Your custom rules, under the customRules: key
Triggering and viewing the alerts
```bash
kubectl apply -f falco-test-pod.yaml
kubectl exec -it falco-test -- bash                       # triggers the shell rule
kubectl exec falco-test -- head -c 10 /dev/mem            # triggers the /dev/mem rule (CRITICAL)
```
There are three ways to see what Falco caught:

### Pod logs (quickest):
``kubectl -n falco logs -l app.kubernetes.io/name=falco -c falco -f | grep -E "Shell|/dev/mem"``
### Falcosidekick UI (dashboard):
``kubectl -n falco port-forward svc/falco-falcosidekick-ui 2802:2802``, then open http://localhost:2802. The default login is admin / admin, so change it in a real setup. It shows the event timeline, counts by priority and rule, and the full JSON of each event.
### Your observability stack. Falcosidekick forwards to more than 50 destinations:
- Grafana + Loki: uncomment the loki: block in the values file, then query {priority="Critical"} in Grafana.
- Prometheus: set falcosidekick.serviceMonitor.enabled: true to scrape its /metrics endpoint. You can then graph event counts by rule and alert on critical events in Alertmanager.
- Slack, Teams or a SIEM (Elasticsearch, Splunk): add their block under config:. Use minimumpriority to cut the noise.
