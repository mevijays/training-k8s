## Understanding Falco Security Rules

Falco uses a YAML-based rule format where each rule defines conditions that, when matched, trigger alerts. Here's the complete structure:

### Basic Rule Structure

```yaml
- rule: RULE_NAME
  desc: Description of what this rule detects
  condition: CONDITION_EXPRESSION
  output: ALERT_MESSAGE [PRIORITY]
  priority: CRITICAL|WARNING|INFO|LOW
  tags: tag1,tag2,tag3
```

### Rule Components Explained

**1. `rule`**: Unique name for the rule (no spaces)

**2. `desc`**: Human-readable description of what's being detected

**3. `condition`**: The core logic - uses FALCO rules language with field=value comparisons, logical operators, and function calls

**4. `output`**: Alert message format when triggered (supports variables like `$(USER)`, `$(PROG)`, `$(CMDLINE)`)

**5. `priority`**: Severity level (CRITICAL > WARNING > INFO > LOW)

**6. `tags`**: Categorization tags for filtering/grouping alerts

## Common Falco Fields Used in Rules

### Process-Related Fields
```
$(USER)          # User running the process
$(CMDLINE)       # Full command line
$(CMDLINE_NOARGS)# Command without arguments
$(PROG)          # Executable path
$(PPID)          # Parent PID
$(PID)           # Process ID
$(TYPE)          # Process type (process, socket, file, etc.)
```

### Network Fields
```
$(SRC_PORT)      # Source port
$(DEST_PORT)     # Destination port
$(PROTOCOL)      # TCP/UDP
$(ICMP_TYPE)     # ICMP type number
```

### File-Related Fields
```
$(FILE)          # Full file path
$(FD)            # File descriptor number
```

### Container Fields
```
$(CONTAINER_ID)  # Container ID
$(K8S_POD)       # Kubernetes pod name
$(K8S_NS)        # Kubernetes namespace
$(K8S_NODE)      # Node name
```

## Example Rules by Category

### 1. Sensitive File Access

```yaml
- rule: SUID_FILE_EXECUTION
  desc: Process executing a SUID/SGID binary
  condition: (type in (exec,open) and ((suid=1) or (sgid=1)))
  output: "Sensitive file access detected by user $(USER) on $(FILE): $(CMDLINE)\n[FALL-THROUGH]"
  priority: WARNING
  tags: file,security,suid
```

### 2. Privileged Container Detection

```yaml
- rule: PRIVILEGED_CONTAINER
  desc: Pod running in privileged mode
  condition: (container=1 and is_privileged=1)
  output: "Privileged container detected on $(K8S_NODE) for pod $(K8S_POD)\n[container]"
  priority: CRITICAL
  tags: container,privileged,kubernetes
```

### 3. Suspicious Network Connections

```yaml
- rule: SUSPICIOUS_OUTBOUND_CONNECTION
  desc: Process connecting to suspicious port
  condition: (fd=1 and dest_port in (4444,5555,6666,31337))
  output: "Suspicious outbound connection from $(USER) on $(CMDLINE) to port $(DEST_PORT)\n[network]"
  priority: WARNING
  tags: network,suspicious
```

### 4. Container Escape Attempt

```yaml
- rule: CONTAINER_ESCAPE_ATTEMPT
  desc: Process attempting to escape container
  condition: (open=/dev/.ptmx and container=1)
  output: "Container escape attempt detected from $(K8S_POD) on $(K8S_NODE)\n[container]"
  priority: CRITICAL
  tags: container,escape,kubernetes
```

### 5. Unauthorized Root Login

```yaml
- rule: UNAUTHORIZED_ROOT_LOGIN
  desc: Root login by non-root user via SSH
  condition: (open=/dev/pts/* and user=root and (user not in $(ALLOWED_USERS)) and cmdline contains sshd)
  output: "Unauthorized root login attempt from $(USER) via SSH\n[shell]"
  priority: CRITICAL
  tags: authentication,root,kubernetes
```

### 6. Database Access Anomalies

```yaml
- rule: SUSPICIOUS_DATABASE_ACCESS
  desc: Process accessing database ports from unexpected location
  condition: (fd=1 and dest_port in (3306,5432,27017) and container=1)
  output: "Database access from container $(CONTAINER_ID) to port $(DEST_PORT): $(CMDLINE)\n[database]"
  priority: WARNING
  tags: database,kubernetes
```

### 7. Java-Specific Security Rules (for your use case)

```yaml
- rule: JAVA_EXECUTION_AS_ROOT
  desc: Java application running as root user
  condition: (type=process and user=root and prog=~^/usr/bin/java)
  output: "Java application detected running as root by $(USER) on $(CMDLINE)\n[container]\n[shell]"
  priority: WARNING
  tags: java,java-app,kubernetes,root

- rule: JAVA_UNKNOWN_IMAGE
  desc: Java pod using unknown/unpinned image tag
  condition: (container=1 and k8s_pod_labels_image not in $(ALLOWED_IMAGES) and container_image_tag="latest")
  output: "Java application using unpinned image tag 'latest': $(K8S_POD) with image $(CONTAINER_IMAGE)\n[container]"
  priority: WARNING
  tags: java,image-security,kubernetes

- rule: JAVA_NETWORK_EXPOSURE
  desc: Java process listening on all interfaces
  condition: (type=process and user=root and cmdline contains java and fd=3 and l4_protocol=tcp and l4_src_port=8080)
  output: "Java application $(CMDLINE) exposed on all interfaces port $(SRC_PORT)\n[shell]\n[network]"
  priority: INFO
  tags: java,network,kubernetes
```

## Advanced Rule Features

### Using Functions

```yaml
- rule: COMMAND_NOT_IN_PATH
  desc: Executable not in PATH or standard locations
  condition: (type=exec and path not in (/usr/bin,/bin,/sbin,/usr/sbin))
  output: "Command executed from unusual location: $(PROG)\n[shell]\n[container]"
  priority: WARNING
  tags: shell,command,kubernetes
```

### Logical Operators

```yaml
- rule: COMPLEX_SECURITY_RULE
  desc: Multiple conditions combined
  condition: (type=exec and user=root and (prog=/usr/bin/sudo or prog=/bin/bash) and container=1)
  output: "Root command execution in container by $(USER): $(CMDLINE)\n[shell]\n[container]"
  priority: WARNING
  tags: kubernetes,root,command
```

### Time-Based Rules (using FALCO functions)

```yaml
- rule: AFTER_HOURS_ACCESS
  desc: Sensitive access outside business hours
  condition: (type=open and path=/etc/shadow and hour>23 or hour<6)
  output: "Sensitive file access at unusual time $(TIME): $(CMDLINE)\n[shell]\n[file]"
  priority: WARNING
  tags: file,audit,kubernetes
```

## Custom Variables in Rules

You can define variables to make rules more flexible:

```yaml
# Define allowed users
- rule: ALLOWED_USERS_LIST
  desc: Define list of authorized users for whitelisting
  condition: user in (admin,developer,monitoring)
  output: "User $(USER) is in the allowed list\n[shell]\n[container]"
  priority: INFO
  tags: variable,allowed-users

# Use the variable in other rules
- rule: UNAUTHORIZED_USER_ACCESS
  desc: Access by non-authorized users
  condition: user not in ($(ALLOWED_USERS)) and (type=exec or type=open)
  output: "Unauthorized access attempt by $(USER): $(CMDLINE)\n[shell]\n[file]"
  priority: WARNING
  tags: security,kubernetes,authorization
```

## Best Practices for Writing Falco Rules

1. **Start with built-in rules**: Sysdig provides hundreds of pre-built rules
2. **Be specific**: Use precise field matching to reduce false positives
3. **Use tags consistently**: Makes filtering and reporting easier
4. **Set appropriate priorities**: Don't overwhelm with CRITICAL alerts
5. **Test in debug mode**: Use `falco -r your_rules.yaml -n` before production
6. **Document the business context**: Why does this rule matter?
7. **Use output variables wisely**: Include actionable information
8. **Consider performance**: Complex rules may impact detection speed

## Testing Your Rules

```bash
# Test a single rule file
falco -r /path/to/your/rules.yaml -n

# Test with specific conditions
echo "exec /bin/bash" | nc localhost 15067

# Run in foreground for immediate feedback
falco -r your_rules.yaml
```

## Common Pitfalls to Avoid

- **Overly broad rules**: Generate too many false positives
- **Missing priority**: Defaults to INFO, which may get ignored
- **No output format**: Make sure output is actionable
- **Ignoring tags**: Can't filter/alert based on categories
- **Not testing**: Rules should be validated before deployment
