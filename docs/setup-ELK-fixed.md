# Setup ELK Stack (Elasticsearch, Logstash, Kibana, Filebeat) on Kubernetes

## Prerequisites
- Kubernetes cluster (kubeadm, EKS, GKE, KIND, etc.)
- Helm installed
- Network connectivity between pods

## Elastic Search Installation
```bash
helm upgrade --install elasticsearch elasticsearch \
  --set replicas=1 \
  --set minimumMasterNodes=1 \
  --set resources.requests.cpu=100m \
  --set resources.requests.memory=1Gi \
  --set volumeClaimTemplate.resources.requests.storage=5Gi \
  --set elasticsearch.password='ELASTIC_PASSWORD' \
  --repo https://helm.elastic.co \
  -n logging \
  --create-namespace
```

**Note**: Replace `ELASTIC_PASSWORD` with your desired password.

## Logstash Installation
Create `logstash.yaml`:
```yaml
persistence:
  enabled: true

logstashConfig:
  logstash.yml: |
    http.host: 0.0.0.0

logstashPipeline:
  logstash.conf: |
    input {
      beats {
        port => 5044
      }
    }
    output {
      elasticsearch {
        hosts => ["https://elasticsearch-master:9200"]
        manage_template => false
        ssl_certificate_verification => false
        index => "%{[@metadata][beat]}-%{+YYYY.MM.dd}"
        document_type => "%{[@metadata][type]}"
        user => "elastic"
        password => "ELASTIC_PASSWORD"
      }
    }

service:
  type: ClusterIP
  ports:
    - name: beats
      port: 5044
      protocol: TCP
      targetPort: 5044
    - name: http
      port: 8080
      protocol: TCP
      targetPort: 8080
```

Install Logstash:
```bash
helm upgrade --install logstash logstash \
  --set replicas=1 \
  --set resources.requests.cpu=100m \
  --set resources.requests.memory=1Gi \
  --repo https://helm.elastic.co \
  -f logstash.yaml \
  -n logging
```

## Kibana Installation
```bash
helm upgrade --install kibana kibana \
  --set resources.requests.cpu=100m \
  --set resources.requests.memory=500Mi \
  --repo https://helm.elastic.co \
  -n logging
```

## Filebeat Installation
Create `filebeat.yaml`:
```yaml
daemonset:
  filebeatConfig:
    filebeat.yml: |
      filebeat.inputs:
        - type: container
          paths:
            - /var/log/containers/*.log
          processors:
            - add_kubernetes_metadata:
                host: ${NODE_NAME}
                matchers:
                  - logs_path:
                      logs_path: "/var/log/containers/"

      output.logstash:
        hosts: ["logstash-logstash:5044"]
```

Install Filebeat:
```bash
helm upgrade --install filebeat filebeat \
  --set resources.requests.cpu=100m \
  --set resources.requests.memory=500Mi \
  --repo https://helm.elastic.co \
  -f filebeat.yaml \
  -n logging
```

## Expose Kibana
Create `svc-kibana.yaml`:
```yaml
apiVersion: v1
kind: Service
metadata:
  labels:
    app: kibana
    release: kibana
  name: kibana-kibana-public
  namespace: logging
spec:
  ports:
    - name: http
      port: 5601
      protocol: TCP
      targetPort: 5601
  selector:
    app: kibana
    release: kibana
  type: LoadBalancer
```

Apply and access:
```bash
kubectl apply -f svc-kibana.yaml -n logging
kubectl get svc -n logging
```

Access Kibana at `http://<LOADBALANCER-IP>:5601` with:
- Username: `elastic`
- Password: Extract using:
```bash
kubectl get secrets --namespace=logging elasticsearch-master-credentials -o jsonpath='{.data.password}' | base64 -d
```

## Verification
```bash
# Check all components
kubectl get pods -n logging
kubectl get svc -n logging

# Check Elasticsearch
curl https://elasticsearch-master:9200

# Check Filebeat logs
kubectl logs -n logging -l release=filebeat

# Check Logstash logs
kubectl logs -n logging -l release=logstash
```

## Security Best Practices
1. Use strong passwords for Elasticsearch
2. Enable SSL/TLS for inter-service communication
3. Configure proper RBAC for Elasticsearch users
4. Use Kubernetes Secrets for sensitive data
5. Enable audit logging
