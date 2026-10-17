# End-to-End Guide: NVIDIA A100 80GB GPU Node Preparation & GPU Operator on Kubernetes (Ubuntu 26.04)

This guide covers the complete workflow for provisioning 3 Ubuntu 26.04 worker nodes equipped with NVIDIA A100 80GB PCIe/SXM4 GPUs, configuring host-level drivers and runtime toolkit, deploying the NVIDIA GPU Operator on Kubernetes, and verifying execution using a sample GPU workload.

---

## Architecture Overview

* **OS:** Ubuntu 26.04 LTS (x86_64)
* **Compute:** 3x Worker Nodes with NVIDIA A100 80GB
* **Container Runtime:** `containerd` (v1.7+ / v2.x)
* **GPU Stack:** NVIDIA Data Center Drivers (Branch 550+ / 560+), NVIDIA Container Toolkit, NVIDIA GPU Operator (Helm)

> **Important Architectural Note:**  
> When deploying the **NVIDIA GPU Operator**, you have two approaches:
> 1. **Operator-managed Drivers (Default):** Nodes run vanilla Ubuntu without drivers; the Operator containerizes driver compilation and installation.
> 2. **Pre-installed Host Drivers (Recommended for high-performance clusters & A100 NVLink/Fabric Manager):** You install the proprietary driver and container toolkit on the host first, and tell the GPU Operator `driver.enabled=false`. This guide implements this robust, production-proven path.

---

## Phase 1: Host-Level Setup (Run on All 3 Worker Nodes)

Perform these steps sequentially across all three worker nodes (`node-1`, `node-2`, `node-3`).

### 1.1. Prerequisites & Kernel Headers

```bash
# Update repositories and upgrade system packages
sudo apt-get update && sudo apt-get upgrade -y

# Install build dependencies and kernel headers matching running kernel
sudo apt-get install -y \
    build-essential \
    linux-headers-$(uname -r) \
    dkms \
    pkg-config \
    pciutils \
    curl \
    gpg

# Verify A100 GPU hardware is detected on the PCIe bus
lspci | grep -i nvidia
```

### 1.2. Install NVIDIA Data Center Driver

For A100 80GB enterprise GPUs, use the official NVIDIA Data Center APT repository:

```bash
# Download and install NVIDIA repository keyring
curl -fsSL https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.1-1_all.deb -o cuda-keyring.deb
sudo dpkg -i cuda-keyring.deb
sudo apt-get update

# Install NVIDIA Data Center Driver (Production Branch) & Fabric Manager (if SXM4/NVLink)
sudo apt-get install -y nvidia-driver-550-server nvidia-utils-550-server

# If using A100 SXM4 (NVLink/NVSwitch), install and enable Fabric Manager:
sudo apt-get install -y nvidia-fabricmanager-550
sudo systemctl enable --now nvidia-fabricmanager

# Reboot the host to load kernel modules
sudo reboot
```

### 1.3. Validate Driver on Host

Once the node comes back online:

```bash
# Check device communication, VRAM capacity (81920 MiB), and driver version
nvidia-smi
```

---

## Phase 2: Install & Configure NVIDIA Container Toolkit (All 3 Nodes)

The container runtime (`containerd`) must be configured with NVIDIA's runtime hook to pass GPU devices into container namespaces.

### 2.1. Install Toolkit Packages

```bash
# Set up NVIDIA Container Toolkit repository
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
```

### 2.2. Configure `containerd` Runtime

```bash
# Configure the NVIDIA runtime in containerd's config.toml automatically
sudo nvidia-ctk runtime configure --runtime=containerd

# Set nvidia-container-runtime as the default runtime (Optional but recommended for GPU nodes)
sudo nvidia-ctk runtime configure --runtime=containerd --set-as-default

# Restart containerd to load changes
sudo systemctl restart containerd
sudo systemctl status containerd
```

---

## Phase 3: Node Labeling & Tainting (Control Plane)

Switch to your Kubernetes control plane machine or workstation with `kubectl` admin access.

### 3.1. Label Worker Nodes

Tag the worker nodes so workloads and operator components target them:

```bash
kubectl label nodes <node-1-name> <node-2-name> <node-3-name> accelerator=nvidia-a100-80gb
kubectl label nodes <node-1-name> <node-2-name> <node-3-name> nvidia.com/gpu.present=true
```

### 3.2. Apply Taints (Optional but Recommended)

Taints prevent generic non-GPU pods from wasting memory or CPU capacity on your A100 nodes:

```bash
kubectl taint nodes <node-1-name> <node-2-name> <node-3-name> nvidia.com/gpu=present:NoSchedule
```

---

## Phase 4: Deploy NVIDIA GPU Operator via Helm

The GPU Operator manages the Device Plugin, DCGM monitoring, node feature discovery (NFD), and Validator daemonsets.

### 4.1. Add Helm Repository

```bash
helm repo add nvidia https://helm.ngc.nvidia.com/nvidia
helm repo update
```

### 4.2. Install Operator with Existing Host Driver Configuration

Because we installed the drivers and toolkit at the host level in Phases 1 & 2, disable `driver.enabled` and `toolkit.enabled` so the operator operates in passthrough mode:

```bash
helm install gpu-operator nvidia/gpu-operator \
  --namespace gpu-operator \
  --create-namespace \
  --set driver.enabled=false \
  --set toolkit.enabled=false \
  --set devicePlugin.enabled=true \
  --set dcgmExporter.enabled=true \
  --set gfd.enabled=true \
  --set operator.defaultRuntime=containerd \
  --set daemonsets.tolerations[0].key="nvidia.com/gpu" \
  --set daemonsets.tolerations[0].operator="Exists" \
  --set daemonsets.tolerations[0].effect="NoSchedule"
```

### 4.3. Monitor DaemonSet Deployment

Wait for all pods in the `gpu-operator` namespace to report `Running`:

```bash
kubectl get pods -n gpu-operator -w
```

### 4.4. Verify Allocatable GPUs on Nodes

Check that the Kubernetes API server exposes the 80GB A100 resources:

```bash
kubectl get nodes "-o=custom-columns=NAME:.metadata.name,GPU_CAPACITY:.status.capacity.nvidia\.com/gpu,GPU_ALLOCATABLE:.status.allocatable.nvidia\.com/gpu"
```

*Expected output per node:*
```text
NAME       GPU_CAPACITY   GPU_ALLOCATABLE
node-1     1              1
node-2     1              1
node-3     1              1
```

---

## Phase 5: Verification Test with `nvidia-smi` Pod

Deploy a test pod requesting `nvidia.com/gpu: 1` to verify containerized CUDA access and memory reporting.

### 5.1. Apply Test Pod Manifest

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: a100-gpu-verification
  namespace: default
spec:
  restartPolicy: Never
  tolerations:
    - key: "nvidia.com/gpu"
      operator: "Exists"
      effect: "NoSchedule"
  containers:
    - name: cuda-test
      image: nvcr.io/nvidia/cuda:12.4.1-base-ubuntu22.04
      command: ["nvidia-smi"]
      resources:
        limits:
          nvidia.com/gpu: 1
EOF
```

### 5.2. Review Logs

Inspect the execution logs once the pod transitions to `Completed`:

```bash
kubectl logs a100-gpu-verification
```

*Expected standard output:*
```text
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 550.54.15              Driver Version: 550.54.15      CUDA Version: 12.4     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA A100-PCIE-80GB          On  |   00000000:00:04.0 Off |                    0 |
| N/A   32C    P0             41W / 250W  |       0MiB / 81920MiB  |      0%      Default |
|                                         |                        |             Disabled |
+-----------------------------------------+------------------------+----------------------+
```

### 5.3. Clean Up

```bash
kubectl delete pod a100-gpu-verification
```
