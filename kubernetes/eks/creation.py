import subprocess

# List of regions
regions = ['us-west-1', 'us-east-1']

# List of usernames
usernames = ['user1', 'user2', 'user3', 'user4', 'user5', 'user6']

# EKS cluster configuration options
eksctl_options = {
    'nodegroup-name': 'default',
    'node-type': 't3.medium',
    'nodes': 1,
    'nodes-min': 1,
    'nodes-max': 3,
    'managed': True
}

def create_cluster(region, username, options):
    cluster_name = f"{username}-eks"
    command = [
        'eksctl', 'create', 'cluster',
        '--name', cluster_name,
        '--region', region,
        '--nodegroup-name', options['nodegroup-name'],
        '--node-type', options['node-type'],
        '--nodes', str(options['nodes']),
        '--nodes-min', str(options['nodes-min']),
        '--nodes-max', str(options['nodes-max']),
        '--managed' if options['managed'] else '--no-managed'
    ]
    
    try:
        subprocess.run(command, check=True)
        print(f"Cluster {cluster_name} created successfully in region {region}.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to create cluster {cluster_name} in region {region}. Error: {e}")

def main():
    for i, username in enumerate(usernames):
        region = regions[i % len(regions)]
        create_cluster(region, username, eksctl_options)

if __name__ == "__main__":
    main()