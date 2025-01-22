from flask import Flask, render_template_string, request, redirect, url_for, flash, session, render_template
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from functools import wraps
import os
import yaml

# Add environment variables for auth
USERNAME = os.getenv('K8S_MGR_USERNAME', 'admin')
PASSWORD = os.getenv('K8S_MGR_PASSWORD', 'admin123')

# Add URL prefix to app
app = Flask(__name__)
app.config['APPLICATION_ROOT'] = '/k8smgr'
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key')

# Login template
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>K8s Manager Login</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h3 class="text-center">Kubernetes Cluster Manager</h3>
                    </div>
                    <div class="card-body">
                        {% if error %}
                        <div class="alert alert-danger">{{ error }}</div>
                        {% endif %}
                        <form method="POST" action="{{ url_for('login') }}">
                            <div class="mb-3">
                                <label>Username</label>
                                <input type="text" name="username" class="form-control" required>
                            </div>
                            <div class="mb-3">
                                <label>Password</label>
                                <input type="password" name="password" class="form-control" required>
                            </div>
                            <button type="submit" class="btn btn-primary w-100">Login</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Update login route to store username
@app.route('/k8smgr/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] == USERNAME and request.form['password'] == PASSWORD:
            session['logged_in'] = True
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        error = 'Invalid credentials'
    return render_template_string(LOGIN_TEMPLATE, error=error)

# Logout route
@app.route('/k8smgr/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# Add flash message support to Flask app
app.secret_key = 'your-secret-key'  # Required for flash messages

# Update HTML_TEMPLATE to add logout button and welcome message
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Kubernetes Cluster Manager</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</head>
<body>
    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2>Kubernetes Cluster Manager</h2>
            <div>
                <span class="me-3">Welcome, {{ session.username }}!</span>
                <a href="{{ url_for('logout') }}" class="btn btn-outline-danger">Logout</a>
            </div>
        </div>
        
        <!-- Flash Messages -->
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <form method="POST" action="{{ url_for('index') }}" class="mb-4">
            <div class="row">
                <div class="col-md-4">
                    <select name="kubeconfig" class="form-select" onchange="this.form.submit()">
                        <option value="">Select Cluster</option>
                        {% for config in kubeconfigs %}
                            <option value="{{ config }}" {% if config == selected_config %}selected{% endif %}>
                                {{ cluster_mapping[config] }}
                            </option>
                        {% endfor %}
                    </select>
                </div>
                
                {% if namespaces %}
                <div class="col-md-4">
                    <select name="namespace" class="form-select" onchange="this.form.submit()">
                        <option value="">Select Namespace</option>
                        {% for ns in namespaces %}
                            <option value="{{ ns }}" {% if selected_namespace == ns %}selected{% endif %}>
                                {{ ns }}
                            </option>
                        {% endfor %}
                    </select>
                </div>
                {% endif %}
            </div>
        </form>

        {% if deployments %}
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>Deployment Name</th>
                    <th>Replicas</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for deploy in deployments %}
                <tr>
                    <td>{{ deploy.name }}</td>
                    <td>{{ deploy.replicas }}</td>
                    <td>
                        <button type="button" class="btn btn-primary btn-sm" data-bs-toggle="modal" 
                                data-bs-target="#scaleModal{{ loop.index }}">
                            Scale
                        </button>
                        <button type="button" class="btn btn-info btn-sm" data-bs-toggle="modal" 
                                data-bs-target="#detailsModal{{ loop.index }}">
                            Details
                        </button>
                    </td>
                </tr>

                <!-- Scale Modal -->
                <div class="modal fade" id="scaleModal{{ loop.index }}" tabindex="-1">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">Scale Deployment: {{ deploy.name }}</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <form action="{{ url_for('scale') }}" method="POST">
                                <div class="modal-body">
                                    <input type="hidden" name="deployment" value="{{ deploy.name }}">
                                    <input type="hidden" name="namespace" value="{{ selected_namespace }}">
                                    <input type="hidden" name="kubeconfig" value="{{ selected_config }}">
                                    <input type="number" name="replicas" class="form-control" 
                                           value="{{ deploy.replicas }}" min="0">
                                </div>
                                <div class="modal-footer">
                                    <button type="submit" class="btn btn-primary">Scale</button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>

                <!-- Details Modal -->
                <div class="modal fade" id="detailsModal{{ loop.index }}" tabindex="-1">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">Deployment Details: {{ deploy.name }}</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <h6>Pods:</h6>
                                <form action="{{ url_for('delete_pods') }}" method="POST" class="mb-3">
                                    <input type="hidden" name="deployment" value="{{ deploy.name }}">
                                    <input type="hidden" name="namespace" value="{{ selected_namespace }}">
                                    <input type="hidden" name="kubeconfig" value="{{ selected_config }}">
                                    <div class="mb-3">
                                        {% for pod in deploy.pods %}
                                        <div class="form-check">
                                            <input class="form-check-input" type="checkbox" name="selected_pods" value="{{ pod }}" id="pod_{{ loop.index }}">
                                            <label class="form-check-label" for="pod_{{ loop.index }}">
                                                {{ pod }}
                                            </label>
                                        </div>
                                        {% endfor %}
                                    </div>
                                    <button type="submit" class="btn btn-danger" {% if not deploy.pods %}disabled{% endif %}>
                                        Delete Selected Pods
                                    </button>
                                </form>
                                <h6 class="mt-3">Images:</h6>
                                <ul>
                                {% for image in deploy.images %}
                                    <li>{{ image }}</li>
                                {% endfor %}
                                </ul>

                                <h6 class="mt-3">Service Account:</h6>
                                <p>{{ deploy.service_account }}</p>

                                <h6 class="mt-3">Image Pull Secrets:</h6>
                                {% if deploy.image_pull_secrets %}
                                <ul>
                                {% for secret in deploy.image_pull_secrets %}
                                    <li>{{ secret }}</li>
                                {% endfor %}
                                </ul>
                                {% else %}
                                <p>No image pull secrets configured</p>
                                {% endif %}

                                <h6 class="mt-3">Volumes:</h6>
                                {% if deploy.volumes %}
                                <ul>
                                {% for volume in deploy.volumes %}
                                    <li>
                                        {{ volume.name }} ({{ volume.type }})
                                        {% if volume.claim_name %}
                                            - PVC: {{ volume.claim_name }}
                                        {% elif volume.config_name %}
                                            - ConfigMap: {{ volume.config_name }}
                                        {% elif volume.secret_name %}
                                            - Secret: {{ volume.secret_name }}
                                        {% endif %}
                                    </li>
                                {% endfor %}
                                </ul>
                                {% else %}
                                <p>No volumes configured</p>
                                {% endif %}

                                <h6 class="mt-3">Volume Mounts:</h6>
                                {% if deploy.mounts %}
                                {% for container in deploy.mounts %}
                                <div class="mb-2">
                                    <strong>Container: {{ container.container }}</strong>
                                    <ul>
                                    {% for mount in container.mounts %}
                                        <li>
                                            {{ mount.name }} → {{ mount.path }}
                                            {% if mount.readonly %} (readonly){% endif %}
                                        </li>
                                    {% endfor %}
                                    </ul>
                                </div>
                                {% endfor %}
                                {% else %}
                                <p>No volume mounts configured</p>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </tbody>
        </table>
        {% endif %}
    </div>
</body>
</html>
'''

def get_kubeconfigs():
    kubeconfig_dir = "kubeconfigs"
    if os.path.exists(kubeconfig_dir):
        return [f for f in os.listdir(kubeconfig_dir) if f.endswith(('.yaml', '.yml'))]
    return []

def get_k8s_client(kubeconfig):
    """Helper to get k8s client with proper config"""
    try:
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kubeconfigs', kubeconfig)
        # Load config directly without clearing
        config.load_kube_config(config_path)
        # Initialize API clients
        apps_v1 = client.AppsV1Api()
        core_v1 = client.CoreV1Api()
        return apps_v1, core_v1
    except Exception as e:
        print(f"Error initializing k8s client: {e}")
        return None, None

def get_cluster_names():
    """Get mapping of kubeconfig files to their cluster names"""
    cluster_mapping = {}
    kubeconfig_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kubeconfigs')
    
    for filename in os.listdir(kubeconfig_dir):
        if filename.endswith('.yaml') or filename.endswith('.yml'):
            try:
                config_path = os.path.join(kubeconfig_dir, filename)
                with open(config_path) as f:
                    kube_config = yaml.safe_load(f)
                    # Get cluster name from config
                    if 'clusters' in kube_config and len(kube_config['clusters']) > 0:
                        cluster_name = kube_config['clusters'][0]['name']
                        cluster_mapping[filename] = cluster_name
            except Exception as e:
                print(f"Error reading {filename}: {e}")
                cluster_mapping[filename] = filename  # Fallback to filename
    
    return cluster_mapping

@app.route('/', methods=['GET', 'POST'])
@app.route('/k8smgr/', methods=['GET', 'POST'])
@login_required
def index():
    """Main route - should only GET data, no modifications"""
    # Get kubeconfig files and their cluster names
    cluster_mapping = get_cluster_names()
    kubeconfigs = list(cluster_mapping.keys())
    selected_config = request.form.get('kubeconfig', '')
    selected_namespace = request.form.get('namespace', '')
    namespaces = []
    deployments = []

    if selected_config:
        apps_v1, core_v1 = get_k8s_client(selected_config)
        
        # Only GET operations, no modifications
        if apps_v1 and core_v1:
            # Get namespaces
            ns_list = core_v1.list_namespace()
            namespaces = [ns.metadata.name for ns in ns_list.items]

            if selected_namespace:
                # Only GET deployments, no modifications
                deployments = get_deployments(apps_v1, core_v1, selected_namespace)

    return render_template_string(
        HTML_TEMPLATE,
        kubeconfigs=kubeconfigs,
        cluster_mapping=cluster_mapping,
        selected_config=selected_config,
        namespaces=namespaces,
        selected_namespace=selected_namespace,
        deployments=deployments
    )

def load_kubernetes_config(kubeconfig):
    """Helper function to load kubeconfig safely"""
    try:
        # Updated path to 'kubeconfigs' instead of 'kubeconfig'
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kubeconfigs', kubeconfig)
        
        # Debug logging
        print(f"Attempting to load kubeconfig from: {config_path}")
        
        if not os.path.exists(config_path):
            print(f"Available files in directory: {os.listdir(os.path.dirname(config_path))}")
            raise FileNotFoundError(f"Kubeconfig file not found: {config_path}")
            
        config.load_kube_config(config_path)
        return True
    except Exception as e:
        raise Exception(f"Failed to load kubeconfig: {str(e)}")

@app.route('/k8smgr/delete_pods', methods=['POST'])
@login_required
def delete_pods():
    try:
        kubeconfig = request.form.get('kubeconfig')
        if not kubeconfig:
            flash('No kubeconfig selected', 'danger')
            return redirect(url_for('index'))

        # Load kubernetes config
        load_kubernetes_config(kubeconfig)
        
        namespace = request.form.get('namespace')
        selected_pods = request.form.getlist('selected_pods')
        
        if not selected_pods:
            flash('No pods selected for deletion', 'warning')
            return redirect(url_for('index'))

        core_v1 = client.CoreV1Api()
        
        for pod_name in selected_pods:
            core_v1.delete_namespaced_pod(
                name=pod_name,
                namespace=namespace,
                body=client.V1DeleteOptions(
                    grace_period_seconds=0,
                    propagation_policy='Background'
                )
            )
        
        flash(f'Successfully deleted {len(selected_pods)} pod(s)', 'success')
    except Exception as e:
        flash(f'Error in pod deletion: {str(e)}', 'danger')
    return redirect(url_for('index'))

# Update the scale route to include success/error messages
@app.route('/k8smgr/scale', methods=['POST'])
@login_required
def scale():
    """Only route that should modify replicas"""
    try:
        kubeconfig = request.form.get('kubeconfig')
        namespace = request.form.get('namespace')
        deployment = request.form.get('deployment')
        replicas = int(request.form.get('replicas', 1))

        apps_v1, _ = get_k8s_client(kubeconfig)
        
        # Use deployment patch instead of scale subresource
        apps_v1.patch_namespaced_deployment(
            name=deployment,
            namespace=namespace,
            body={
                'spec': {
                    'replicas': replicas
                }
            }
        )
        
        flash(f'Successfully scaled deployment {deployment} to {replicas} replicas', 'success')
    except Exception as e:
        flash(f'Error scaling deployment: {str(e)}', 'danger')
    
    return redirect(url_for('index'))

def get_deployments(apps_v1, core_v1, namespace):
    deployments = []
    try:
        deploy_list = apps_v1.list_namespaced_deployment(namespace)
        for d in deploy_list.items:
            # Get existing deployment info
            pod_spec = d.spec.template.spec
            
            # Get ServiceAccount info
            service_account = pod_spec.service_account_name if pod_spec.service_account_name else "default"
            
            # Get Image Pull Secrets
            image_pull_secrets = []
            if pod_spec.image_pull_secrets:
                image_pull_secrets = [secret.name for secret in pod_spec.image_pull_secrets]
            
            # Get pods and their volumes
            label_selector = ','.join([f"{k}={v}" for k, v in d.spec.selector.match_labels.items()])
            pods = core_v1.list_namespaced_pod(namespace, label_selector=label_selector)
            
            # Get volume information from pod template
            volumes = []
            if d.spec.template.spec.volumes:
                for vol in d.spec.template.spec.volumes:
                    volume_info = {'name': vol.name}
                    if vol.persistent_volume_claim:
                        volume_info['type'] = 'PVC'
                        volume_info['claim_name'] = vol.persistent_volume_claim.claim_name
                    elif vol.config_map:
                        volume_info['type'] = 'ConfigMap'
                        volume_info['config_name'] = vol.config_map.name
                    elif vol.secret:
                        volume_info['type'] = 'Secret'
                        volume_info['secret_name'] = vol.secret.secret_name
                    volumes.append(volume_info)

            # Get volume mounts for each container
            container_mounts = []
            for container in d.spec.template.spec.containers:
                if container.volume_mounts:
                    container_mounts.append({
                        'container': container.name,
                        'mounts': [{
                            'name': mount.name,
                            'path': mount.mount_path,
                            'readonly': mount.read_only if hasattr(mount, 'read_only') else False
                        } for mount in container.volume_mounts]
                    })

            deployments.append({
                'name': d.metadata.name,
                'replicas': f"{d.status.replicas or 0}/{d.status.available_replicas or 0}",
                'pods': [p.metadata.name for p in pods.items],
                'images': [c.image for c in d.spec.template.spec.containers],
                'volumes': volumes,
                'mounts': container_mounts,
                'service_account': service_account,
                'image_pull_secrets': image_pull_secrets
            })
    except Exception as e:
        print(f"Error getting deployments: {e}")
    return deployments

if __name__ == '__main__':
    app.config['APPLICATION_ROOT'] = '/k8smgr'
    app.config['PREFERRED_URL_SCHEME'] = 'http'
    app.run(debug=True)
