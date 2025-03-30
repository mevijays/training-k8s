from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
import requests
import json
import logging
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a real secret key in production

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# HTML Templates as strings

# Login page
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>DockerHub Login</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 500px;
            margin: 50px auto;
            padding: 20px;
            background-color: white;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        h1 {
            text-align: center;
            color: #333;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        button {
            background-color: #0066cc;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            width: 100%;
        }
        button:hover {
            background-color: #0052a3;
        }
        .error {
            color: red;
            margin-bottom: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>DockerHub Login</h1>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        <form method="post">
            <div class="form-group">
                <label for="username">Username:</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="token">Access Token:</label>
                <input type="password" id="token" name="token" required>
            </div>
            <button type="submit">Login</button>
        </form>
    </div>
</body>
</html>
'''

# Dashboard template
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>DockerHub Repositories</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f7f9fc;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 25px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        }
        h1 {
            color: #2a5885;
            margin-bottom: 25px;
            font-weight: 600;
            border-bottom: 2px solid #eaeef2;
            padding-bottom: 15px;
        }
        .repo-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .repo-table th {
            background-color: #f0f5fa;
            color: #2a5885;
            text-align: left;
            padding: 12px 15px;
            font-weight: 600;
            border-bottom: 2px solid #dce3eb;
        }
        .repo-table td {
            padding: 12px 15px;
            border-bottom: 1px solid #eaeef2;
            vertical-align: top;
        }
        .repo-row {
            background-color: #f9fbfd;
        }
        .repo-row:hover {
            background-color: #f0f5fa;
        }
        .repo-name {
            font-weight: 600;
            color: #2a5885;
        }
        .tag-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 8px;
        }
        .tag-table td {
            padding: 8px 10px;
            border: none;
            border-bottom: 1px solid #eaeef2;
        }
        .tag-row:hover {
            background-color: #edf2f7;
        }
        .tag-name {
            font-family: 'Courier New', monospace;
            color: #4a6785;
        }
        .checkbox-container {
            width: 30px;
        }
        .logout {
            float: right;
            background-color: #5a6a85;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 4px;
            cursor: pointer;
            text-decoration: none;
            font-size: 14px;
            transition: background-color 0.2s;
        }
        .logout:hover {
            background-color: #4a5a75;
        }
        .loading {
            text-align: center;
            padding: 40px;
            font-style: italic;
            color: #5a6a85;
        }
        .actions {
            display: flex;
            gap: 10px;
            margin: 20px 0;
        }
        .button {
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s;
        }
        .button-blue {
            background-color: #2a5885;
            color: white;
        }
        .button-blue:hover {
            background-color: #1d4067;
        }
        .button-red {
            background-color: #e05454;
            color: white;
        }
        .button-red:hover {
            background-color: #c83c3c;
        }
        .hidden {
            display: none;
        }
        .empty-message {
            text-align: center;
            padding: 30px;
            color: #5a6a85;
            font-style: italic;
        }
        .checkbox {
            width: 16px;
            height: 16px;
            cursor: pointer;
        }
        .tag-count {
            font-size: 12px;
            color: #666;
            background: #edf2f7;
            border-radius: 10px;
            padding: 2px 8px;
            margin-left: 8px;
        }
        .loading-spinner {
            border: 4px solid rgba(0, 0, 0, 0.1);
            width: 36px;
            height: 36px;
            border-radius: 50%;
            border-left-color: #2a5885;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .search-container {
            margin-bottom: 20px;
            display: flex;
            max-width: 500px;
        }
        .search-input {
            flex-grow: 1;
            padding: 10px 15px;
            border: 1px solid #dce3eb;
            border-radius: 4px 0 0 4px;
            font-size: 14px;
        }
        .search-button {
            background-color: #2a5885;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 0 4px 4px 0;
            cursor: pointer;
        }
        .meta-info {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }
        .meta-item {
            display: inline-block;
            margin-right: 15px;
            background: #f5f7fa;
            padding: 3px 8px;
            border-radius: 3px;
        }
        .pull-info {
            display: flex;
            align-items: center;
            background: #f0f5fa;
            padding: 6px 10px;
            border-radius: 4px;
            margin-top: 8px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            border: 1px dashed #dce3eb;
        }
        .copy-button {
            background: #2a5885;
            color: white;
            border: none;
            border-radius: 3px;
            padding: 3px 8px;
            font-size: 11px;
            cursor: pointer;
            margin-left: 8px;
        }
        .copy-button:hover {
            background: #1d4067;
        }
        .copied-message {
            color: #4CAF50;
            margin-left: 5px;
            font-size: 11px;
            opacity: 0;
            transition: opacity 0.3s;
        }
        .show-copied {
            opacity: 1;
        }
        .no-results {
            text-align: center;
            padding: 20px;
            font-style: italic;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <a href="/logout" class="logout">Logout</a>
        <h1>DockerHub Repositories</h1>
        
        <div class="search-container">
            <input type="text" id="searchInput" class="search-input" placeholder="Search repositories or tags..." />
            <button class="search-button" onclick="searchRepositories()">
                Search
            </button>
        </div>
        
        <div class="actions">
            <button id="selectAllBtn" class="button button-blue">Select All</button>
            <button id="deselectAllBtn" class="button button-blue">Deselect All</button>
            <button id="deleteSelectedBtn" class="button button-red">Delete Selected</button>
        </div>
        
        <div id="loading" class="loading">
            <div class="loading-spinner"></div>
            <p>Loading your repositories...</p>
        </div>
        
        <div id="repoContainer" class="hidden">
            <table class="repo-table" id="repoTable">
                <thead>
                    <tr>
                        <th width="30"></th>
                        <th>Repository</th>
                        <th>Tags</th>
                    </tr>
                </thead>
                <tbody id="repoList">
                    <!-- Repositories will be populated here -->
                </tbody>
            </table>
            <div id="emptyMessage" class="empty-message hidden">
                No repositories found in your DockerHub account.
            </div>
            <div id="noSearchResults" class="no-results hidden">
                No repositories match your search criteria.
            </div>
        </div>
    </div>

    <script>
        let allRepositories = []; // Store all repositories for filtering
        
        document.addEventListener('DOMContentLoaded', function() {
            fetchRepositories();
            
            document.getElementById('selectAllBtn').addEventListener('click', function() {
                document.querySelectorAll('input[type="checkbox"]:not([disabled])').forEach(checkbox => {
                    checkbox.checked = true;
                });
            });
            
            document.getElementById('deselectAllBtn').addEventListener('click', function() {
                document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
                    checkbox.checked = false;
                });
            });
            
            document.getElementById('deleteSelectedBtn').addEventListener('click', function() {
                const selected = [];
                
                document.querySelectorAll('input[type="checkbox"]:checked').forEach(checkbox => {
                    if (checkbox.dataset.type === 'repo') {
                        selected.push({
                            type: 'repo',
                            name: checkbox.dataset.repo
                        });
                    } else if (checkbox.dataset.type === 'tag') {
                        selected.push({
                            type: 'tag',
                            repo: checkbox.dataset.repo,
                            tag: checkbox.dataset.tag
                        });
                    }
                });
                
                if (selected.length === 0) {
                    alert('Please select at least one item to delete');
                    return;
                }
                
                if (confirm('Are you sure you want to delete the selected items? This action cannot be undone.')) {
                    deleteSelected(selected);
                }
            });
            
            // Add event listener for search input
            document.getElementById('searchInput').addEventListener('keyup', function(event) {
                if (event.key === 'Enter') {
                    searchRepositories();
                }
            });
        });
        
        function fetchRepositories() {
            document.getElementById('loading').classList.remove('hidden');
            document.getElementById('repoContainer').classList.add('hidden');
            
            fetch('/api/repositories')
                .then(response => response.json())
                .then(data => {
                    allRepositories = data; // Store for search functionality
                    renderRepositories(data);
                    document.getElementById('loading').classList.add('hidden');
                    document.getElementById('repoContainer').classList.remove('hidden');
                })
                .catch(error => {
                    console.error('Error fetching repositories:', error);
                    document.getElementById('loading').innerHTML = 
                        '<p>Error loading repositories. Please try again.</p>' +
                        '<button onclick="fetchRepositories()" class="button button-blue">Retry</button>';
                });
        }
        
        function searchRepositories() {
            const searchTerm = document.getElementById('searchInput').value.toLowerCase().trim();
            
            if (!searchTerm) {
                renderRepositories(allRepositories);
                return;
            }
            
            const filteredRepos = allRepositories.filter(repo => {
                // Check if repo name matches
                if (repo.name.toLowerCase().includes(searchTerm)) {
                    return true;
                }
                
                // Check if any tag matches
                if (repo.tags && repo.tags.some(tag => tag.name.toLowerCase().includes(searchTerm))) {
                    return true;
                }
                
                return false;
            });
            
            renderRepositories(filteredRepos, searchTerm);
        }
        
        function formatDate(dateString) {
            if (!dateString) return 'Unknown';
            
            const date = new Date(dateString);
            const now = new Date();
            const diffTime = Math.abs(now - date);
            const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
            
            if (diffDays === 0) {
                return 'Today';
            } else if (diffDays === 1) {
                return 'Yesterday';
            } else if (diffDays < 30) {
                return diffDays + ' days ago';
            } else {
                return date.toLocaleDateString();
            }
        }
        
        function formatPulls(count) {
            if (!count && count !== 0) return 'Unknown';
            
            if (count >= 1000000) {
                return (count / 1000000).toFixed(1) + 'M';
            } else if (count >= 1000) {
                return (count / 1000).toFixed(1) + 'K';
            }
            return count.toString();
        }
        
        function copyToClipboard(text, buttonId) {
            navigator.clipboard.writeText(text).then(
                function() {
                    // Show copied message
                    const button = document.getElementById(buttonId);
                    const message = button.nextElementSibling;
                    message.classList.add('show-copied');
                    
                    // Hide after 2 seconds
                    setTimeout(() => {
                        message.classList.remove('show-copied');
                    }, 2000);
                },
                function(err) {
                    console.error('Could not copy text: ', err);
                }
            );
        }
        
        function renderRepositories(repositories, searchTerm = '') {
            const repoListElement = document.getElementById('repoList');
            const repoTable = document.getElementById('repoTable');
            const emptyMessage = document.getElementById('emptyMessage');
            const noSearchResults = document.getElementById('noSearchResults');
            
            repoListElement.innerHTML = '';
            
            if (repositories.length === 0) {
                repoTable.classList.add('hidden');
                
                if (searchTerm) {
                    emptyMessage.classList.add('hidden');
                    noSearchResults.classList.remove('hidden');
                } else {
                    emptyMessage.classList.remove('hidden');
                    noSearchResults.classList.add('hidden');
                }
                return;
            }
            
            repoTable.classList.remove('hidden');
            emptyMessage.classList.add('hidden');
            noSearchResults.classList.add('hidden');
            
            let counter = 0;
            
            repositories.forEach(repo => {
                // Create repository row
                const repoRow = document.createElement('tr');
                repoRow.className = 'repo-row';
                
                // Checkbox cell
                const checkboxCell = document.createElement('td');
                checkboxCell.className = 'checkbox-container';
                
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.className = 'checkbox';
                checkbox.dataset.type = 'repo';
                checkbox.dataset.repo = repo.name;
                
                checkboxCell.appendChild(checkbox);
                
                // Repository name cell
                const nameCell = document.createElement('td');
                const repoName = document.createElement('div');
                repoName.className = 'repo-name';
                repoName.textContent = repo.name;
                
                const tagCount = document.createElement('span');
                tagCount.className = 'tag-count';
                tagCount.textContent = repo.tags ? repo.tags.length + ' tags' : '0 tags';
                
                repoName.appendChild(tagCount);
                nameCell.appendChild(repoName);
                
                // Add metadata info
                const metaInfo = document.createElement('div');
                metaInfo.className = 'meta-info';
                
                const lastUpdated = document.createElement('span');
                lastUpdated.className = 'meta-item';
                lastUpdated.innerHTML = '<strong>Updated:</strong> ' + formatDate(repo.last_updated);
                metaInfo.appendChild(lastUpdated);
                
                const pullCount = document.createElement('span');
                pullCount.className = 'meta-item';
                pullCount.innerHTML = '<strong>Pulls:</strong> ' + formatPulls(repo.pull_count);
                metaInfo.appendChild(pullCount);
                
                nameCell.appendChild(metaInfo);
                
                // Add pull command with copy button
                const pullInfo = document.createElement('div');
                pullInfo.className = 'pull-info';
                
                const pullCmd = document.createElement('code');
                const pullCommand = 'docker pull ' + repo.name;
                pullCmd.textContent = pullCommand;
                pullInfo.appendChild(pullCmd);
                
                const copyBtnId = 'copy-btn-' + counter++;
                
                const copyBtn = document.createElement('button');
                copyBtn.className = 'copy-button';
                copyBtn.textContent = 'Copy';
                copyBtn.id = copyBtnId;
                copyBtn.onclick = function() { copyToClipboard(pullCommand, copyBtnId); };
                pullInfo.appendChild(copyBtn);
                
                const copiedMsg = document.createElement('span');
                copiedMsg.className = 'copied-message';
                copiedMsg.textContent = 'Copied!';
                pullInfo.appendChild(copiedMsg);
                
                nameCell.appendChild(pullInfo);
                
                // Tags cell
                const tagsCell = document.createElement('td');
                
                if (repo.tags && repo.tags.length > 0) {
                    const tagTable = document.createElement('table');
                    tagTable.className = 'tag-table';
                    
                    // Filter tags if there's a search term
                    let tagsToRender = repo.tags;
                    if (searchTerm) {
                        tagsToRender = repo.tags.filter(tag => 
                            tag.name.toLowerCase().includes(searchTerm.toLowerCase())
                        );
                    }
                    
                    tagsToRender.forEach(tag => {
                        const tagRow = document.createElement('tr');
                        tagRow.className = 'tag-row';
                        
                        // Tag checkbox cell
                        const tagCheckCell = document.createElement('td');
                        tagCheckCell.className = 'checkbox-container';
                        
                        const tagCheckbox = document.createElement('input');
                        tagCheckbox.type = 'checkbox';
                        tagCheckbox.className = 'checkbox';
                        tagCheckbox.dataset.type = 'tag';
                        tagCheckbox.dataset.repo = repo.name;
                        tagCheckbox.dataset.tag = tag.name;
                        
                        tagCheckCell.appendChild(tagCheckbox);
                        
                        // Tag name cell
                        const tagNameCell = document.createElement('td');
                        
                        const tagNameDiv = document.createElement('div');
                        tagNameDiv.className = 'tag-name';
                        tagNameDiv.textContent = tag.name;
                        
                        tagNameCell.appendChild(tagNameDiv);
                        
                        // Add pull command for specific tag
                        const tagPullInfo = document.createElement('div');
                        tagPullInfo.className = 'pull-info';
                        
                        const tagPullCmd = document.createElement('code');
                        const tagPullCommand = 'docker pull ' + repo.name + ':' + tag.name;
                        tagPullCmd.textContent = tagPullCommand;
                        tagPullInfo.appendChild(tagPullCmd);
                        
                        const tagCopyBtnId = 'copy-tag-btn-' + counter++;
                        
                        const tagCopyBtn = document.createElement('button');
                        tagCopyBtn.className = 'copy-button';
                        tagCopyBtn.textContent = 'Copy';
                        tagCopyBtn.id = tagCopyBtnId;
                        tagCopyBtn.onclick = function() { copyToClipboard(tagPullCommand, tagCopyBtnId); };
                        tagPullInfo.appendChild(tagCopyBtn);
                        
                        const tagCopiedMsg = document.createElement('span');
                        tagCopiedMsg.className = 'copied-message';
                        tagCopiedMsg.textContent = 'Copied!';
                        tagPullInfo.appendChild(tagCopiedMsg);
                        
                        tagNameCell.appendChild(tagPullInfo);
                        
                        // Add tag metadata if available
                        if (tag.last_updated) {
                            const tagMeta = document.createElement('div');
                            tagMeta.className = 'meta-info';
                            tagMeta.innerHTML = '<span class="meta-item"><strong>Updated:</strong> ' + 
                                formatDate(tag.last_updated) + '</span>';
                            tagNameCell.appendChild(tagMeta);
                        }
                        
                        tagRow.appendChild(tagCheckCell);
                        tagRow.appendChild(tagNameCell);
                        
                        tagTable.appendChild(tagRow);
                    });
                    
                    if (tagsToRender.length > 0) {
                        tagsCell.appendChild(tagTable);
                    } else {
                        const noMatchingTags = document.createElement('div');
                        noMatchingTags.textContent = 'No matching tags found';
                        noMatchingTags.style.fontStyle = 'italic';
                        noMatchingTags.style.color = '#999';
                        tagsCell.appendChild(noMatchingTags);
                    }
                } else {
                    const noTags = document.createElement('div');
                    noTags.textContent = 'No tags available';
                    noTags.style.fontStyle = 'italic';
                    noTags.style.color = '#999';
                    tagsCell.appendChild(noTags);
                }
                
                // Add cells to row
                repoRow.appendChild(checkboxCell);
                repoRow.appendChild(nameCell);
                repoRow.appendChild(tagsCell);
                
                // Add row to table
                repoListElement.appendChild(repoRow);
            });
        }
        
        function deleteSelected(selected) {
            // Show loading state on button
            const deleteBtn = document.getElementById('deleteSelectedBtn');
            const originalText = deleteBtn.textContent;
            deleteBtn.textContent = 'Deleting...';
            deleteBtn.disabled = true;
            
            fetch('/api/delete', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ items: selected })
            })
            .then(response => response.json())
            .then(data => {
                deleteBtn.textContent = originalText;
                deleteBtn.disabled = false;
                
                if (data.success) {
                    alert('Selected items have been deleted successfully');
                    fetchRepositories();
                } else {
                    alert('Error: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error deleting items:', error);
                alert('An error occurred while deleting items');
                deleteBtn.textContent = originalText;
                deleteBtn.disabled = false;
            });
        }
    </script>
</body>
</html>
'''

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session or 'token' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        token = request.form.get('token')
        
        # Verify credentials with DockerHub
        try:
            auth_url = "https://hub.docker.com/v2/users/login"
            headers = {"Content-Type": "application/json"}
            data = {"username": username, "password": token}
            
            response = requests.post(auth_url, headers=headers, json=data)
            
            if response.status_code == 200:
                # Store credentials in session
                session['username'] = username
                session['token'] = token
                session['jwt_token'] = response.json().get('token')
                return redirect(url_for('dashboard'))
            else:
                error = "Invalid credentials. Please try again."
                logger.error(f"Login failed: {response.status_code} - {response.text}")
        except Exception as e:
            error = "An error occurred during authentication."
            logger.error(f"Login exception: {str(e)}")
    
    return render_template_string(LOGIN_TEMPLATE, error=error)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template_string(DASHBOARD_TEMPLATE)

@app.route('/api/repositories')
@login_required
def get_repositories():
    try:
        username = session['username']
        jwt_token = session['jwt_token']
        
        # Get repositories
        repos_url = f"https://hub.docker.com/v2/repositories/{username}/"
        headers = {"Authorization": f"JWT {jwt_token}"}
        
        repos_response = requests.get(repos_url, headers=headers)
        
        if repos_response.status_code != 200:
            logger.error(f"Failed to fetch repositories: {repos_response.status_code} - {repos_response.text}")
            return jsonify({"error": "Failed to fetch repositories"}), 500
        
        repositories = repos_response.json().get('results', [])
        result = []
        
        for repo in repositories:
            repo_name = repo['name']
            namespace = repo['namespace']
            full_name = f"{namespace}/{repo_name}"
            
            # Extract repository metadata
            pull_count = repo.get('pull_count', 0)
            last_updated = repo.get('last_updated')
            
            # Get tags for each repository
            tags_url = f"https://hub.docker.com/v2/repositories/{namespace}/{repo_name}/tags"
            tags_response = requests.get(tags_url, headers=headers)
            
            if tags_response.status_code == 200:
                tags_data = tags_response.json().get('results', [])
                tags = []
                
                for tag_data in tags_data:
                    tag = {
                        'name': tag_data['name'],
                        'last_updated': tag_data.get('last_updated')
                    }
                    tags.append(tag)
                
                repo_info = {
                    'name': full_name,
                    'tags': tags,
                    'pull_count': pull_count,
                    'last_updated': last_updated
                }
                result.append(repo_info)
            else:
                logger.error(f"Failed to fetch tags for {repo_name}: {tags_response.status_code} - {tags_response.text}")
                repo_info = {
                    'name': full_name,
                    'tags': [],
                    'pull_count': pull_count,
                    'last_updated': last_updated
                }
                result.append(repo_info)
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error fetching repositories: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/delete', methods=['POST'])
@login_required
def delete_items():
    try:
        username = session['username']
        jwt_token = session['jwt_token']
        items = request.json.get('items', [])
        
        if not items:
            return jsonify({"success": False, "message": "No items specified for deletion"}), 400
        
        headers = {"Authorization": f"JWT {jwt_token}"}
        results = []
        
        for item in items:
            try:
                if item['type'] == 'repo':
                    # Delete repository
                    repo_name = item['name']
                    delete_url = f"https://hub.docker.com/v2/repositories/{repo_name}/"
                    response = requests.delete(delete_url, headers=headers)
                    
                    if response.status_code in [200, 202, 204]:
                        results.append({"item": repo_name, "success": True})
                    else:
                        results.append({
                            "item": repo_name, 
                            "success": False, 
                            "status": response.status_code,
                            "message": response.text
                        })
                
                elif item['type'] == 'tag':
                    # Delete tag
                    repo = item['repo']
                    tag = item['tag']
                    delete_url = f"https://hub.docker.com/v2/repositories/{repo}/tags/{tag}/"
                    response = requests.delete(delete_url, headers=headers)
                    
                    if response.status_code in [200, 202, 204]:
                        results.append({"item": f"{repo}:{tag}", "success": True})
                    else:
                        results.append({
                            "item": f"{repo}:{tag}", 
                            "success": False, 
                            "status": response.status_code,
                            "message": response.text
                        })
            
            except Exception as e:
                logger.error(f"Error deleting item {item}: {str(e)}")
                results.append({"item": str(item), "success": False, "message": str(e)})
        
        # Check if all deletions were successful
        all_success = all(result.get('success', False) for result in results)
        
        if all_success:
            return jsonify({"success": True, "results": results})
        else:
            return jsonify({
                "success": False, 
                "message": "Some items failed to delete", 
                "results": results
            })
    
    except Exception as e:
        logger.error(f"Error in delete operation: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
