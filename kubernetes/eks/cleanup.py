import subprocess

def get_clusters(region):
    try:
        result = subprocess.run(
            ['eksctl', 'get', 'cluster', '--region', region],
            capture_output=True,
            text=True,
            check=True
        )
        clusters = result.stdout.splitlines()
        return [cluster.split()[0] for cluster in clusters[1:]]  # Skip header line
    except subprocess.CalledProcessError as e:
        print(f"Error getting clusters in region {region}: {e}")
        return []

def delete_cluster(cluster_name, region):
    try:
        subprocess.run(
            ['eksctl', 'delete', 'cluster', '--name', cluster_name, '--region', region],
            check=True
        )
        print(f"Deleted cluster {cluster_name} in region {region}")
    except subprocess.CalledProcessError as e:
        print(f"Error deleting cluster {cluster_name} in region {region}: {e}")

def main(regions):
    for region in regions:
        clusters = get_clusters(region)
        for cluster in clusters:
            delete_cluster(cluster, region)

if __name__ == "__main__":
    regions = ['us-west-1', 'us-west-2']  # Add your regions here
    main(regions)