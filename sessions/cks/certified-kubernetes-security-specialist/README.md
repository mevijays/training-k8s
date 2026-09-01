# Certified Kubernetes Security Specialist (CKS)

Hands-on notes and lab walkthroughs for the CKS exam, organised by the six exam
domains. Each domain folder has its own index; every document inside links back
to that index and on to the next topic.

## Domains

| Domain | Documents | Folder | Link |
| :--- | :---: | :--- | :--- |
| Domain 1 - Cluster Setup | 27 | `domain-1-cluster-setup` | [Read](./domain-1-cluster-setup/Readme.md) |
| Domain 2 - Cluster Hardening | 14 | `domain-2-cluster-hardening` | [Read](./domain-2-cluster-hardening/Readme.md) |
| Domain 3 - Minimize Microservice Vulnerabilities | 30 | `domain-3-minimize-microservice-vulnerability` | [Read](./domain-3-minimize-microservice-vulnerability/Readme.md) |
| Domain 4 - System Hardening | 8 | `domain-4-system-hardening` | [Read](./domain-4-system-hardening/Readme.md) |
| Domain 5 - Supply Chain Security | 8 | `domain-5-supply-chain-security` | [Read](./domain-5-supply-chain-security/Readme.md) |
| Domain 6 - Monitoring, Logging and Runtime Security | 10 | `domain-6-monitor-log-runtimesec` | [Read](./domain-6-monitor-log-runtimesec/Readme.md) |

## How to use these notes

- Start at any domain index and use the **next / previous** links at the top and
  bottom of each document to work through it in order.
- The **Domain Home** link in every document brings you back to that domain's index,
  and **All Domains** brings you back here.
- Commands are written for a Linux control-plane node running as `root` unless a
  document says otherwise.
- Environment-specific values are shown as placeholders such as `<IP-ADDRESS>` —
  substitute the value from your own cluster before running a command.
