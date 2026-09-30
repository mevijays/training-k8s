#!/usr/bin/env bash
# k8s-node-prep.sh — prepare an Ubuntu 26.04 VM as a kubeadm node (master or worker)
# for a kube-proxy-free Cilium cluster. Idempotent: safe to re-run on a fresh node.
#
# Usage:
#   sudo ./k8s-node-prep.sh
#   sudo K8S_VERSION=1.36.5 NODE_HOSTNAME=k8s-master NODE_IP=172.16.1.10 \
#        HOSTS_ENTRIES="172.16.1.10 k8s-master,172.16.1.11 k8s-worker" ./k8s-node-prep.sh
#   (put variables AFTER sudo, or use sudo -E, otherwise sudo drops them)
#
# Environment overrides (all optional):
#   K8S_VERSION      1.36 | v1.36 | 1.36.5     default 1.36 (latest 1.36.x patch)
#   ROLE             all | master | worker     image pre-pull scope, default all
#   NODE_HOSTNAME    set the hostname
#   NODE_IP          pin kubelet --node-ip (VMs with multiple NICs)
#   HOSTS_ENTRIES    "IP name,IP name" appended to /etc/hosts (replaces same name)
#   PREPULL_CILIUM   1 = also pre-pull Cilium agent/operator/relay images (default 0)
#   CILIUM_VERSION   default 1.20.2
#   SKIP_IMAGE_PULL  1 = skip all image pulls
#   FORCE            1 = run even if node already joined a cluster
#   HTTP_PROXY / HTTPS_PROXY / NO_PROXY   passed to containerd when set

set -Eeuo pipefail

K8S_VERSION="${K8S_VERSION:-1.36}"
ROLE="${ROLE:-all}"
NODE_HOSTNAME="${NODE_HOSTNAME:-}"
NODE_IP="${NODE_IP:-}"
HOSTS_ENTRIES="${HOSTS_ENTRIES:-}"
PREPULL_CILIUM="${PREPULL_CILIUM:-0}"
CILIUM_VERSION="${CILIUM_VERSION:-1.20.2}"
SKIP_IMAGE_PULL="${SKIP_IMAGE_PULL:-0}"
FORCE="${FORCE:-0}"

LOG=/var/log/k8s-node-prep.log
CFG=/etc/containerd/config.toml
CRI_SOCK=unix:///run/containerd/containerd.sock
export DEBIAN_FRONTEND=noninteractive NEEDRESTART_MODE=a
APT=(apt-get -y -q -o DPkg::Lock::Timeout=600)

log()  { echo -e "\033[1;32m[+]\033[0m $*"; }
warn() { echo -e "\033[1;33m[!]\033[0m $*"; }
die()  { echo -e "\033[1;31m[x]\033[0m $*" >&2; exit 1; }
trap 'die "failed at line $LINENO: $BASH_COMMAND (log: $LOG)"' ERR

# ---------------------------------------------------------------- preflight
[[ $EUID -eq 0 ]] || die "run as root: sudo $0"
exec > >(tee -a "$LOG") 2>&1
log "k8s-node-prep started $(date -Is)"

case "$ROLE" in all|master|worker) ;; *) die "ROLE must be all|master|worker" ;; esac

v="${K8S_VERSION#v}"
[[ $v =~ ^([0-9]+)\.([0-9]+)(\.([0-9]+))?$ ]] || die "bad K8S_VERSION '$K8S_VERSION' (use 1.36 or 1.36.5)"
K8S_MINOR="v${BASH_REMATCH[1]}.${BASH_REMATCH[2]}"
K8S_PATCH=""
if [[ -n ${BASH_REMATCH[4]} ]]; then K8S_PATCH="${BASH_REMATCH[1]}.${BASH_REMATCH[2]}.${BASH_REMATCH[4]}"; fi

# shellcheck disable=SC1091
. /etc/os-release
[[ ${ID:-} == ubuntu ]] || die "Ubuntu required (found ${ID:-unknown})"
if [[ ${VERSION_ID:-} != "26.04" ]]; then warn "written for 26.04, found ${VERSION_ID:-?} — continuing"; fi

if [[ -f /etc/kubernetes/kubelet.conf && $FORCE != 1 ]]; then
  die "node already part of a cluster (/etc/kubernetes/kubelet.conf). Re-run with FORCE=1 or 'kubeadm reset' first"
fi

IFS=. read -r kmaj kmin _ <<<"$(uname -r)"
(( kmaj > 5 || (kmaj == 5 && kmin >= 10) )) || die "kernel $(uname -r) < 5.10 (Cilium minimum)"

cpus=$(nproc); mem=$(awk '/MemTotal/{print int($2/1024)}' /proc/meminfo)
if (( cpus < 2 )); then warn "$cpus CPU — kubeadm init needs 2 on the master"; fi
if (( mem < 1700 )); then warn "${mem}MB RAM — 2GB+ recommended"; fi

if command -v cloud-init >/dev/null 2>&1; then
  log "waiting for cloud-init to finish"
  cloud-init status --wait >/dev/null 2>&1 || true
fi

# ---------------------------------------------------------------- identity
if [[ -n $NODE_HOSTNAME ]]; then
  log "hostname -> $NODE_HOSTNAME"
  hostnamectl set-hostname "$NODE_HOSTNAME"
fi
case "$(hostname)" in ubuntu|localhost*) warn "generic hostname '$(hostname)' — set NODE_HOSTNAME to avoid clashes" ;; esac

if [[ -n $HOSTS_ENTRIES ]]; then
  IFS=',' read -ra entries <<<"$HOSTS_ENTRIES"
  for e in "${entries[@]}"; do
    e="$(xargs <<<"$e")"; [[ -z $e ]] && continue
    name="${e##* }"
    awk -v n="$name" '$NF != n' /etc/hosts > /etc/hosts.tmp && cat /etc/hosts.tmp > /etc/hosts && rm -f /etc/hosts.tmp
    echo "$e" >> /etc/hosts
    log "/etc/hosts: $e"
  done
fi

timedatectl set-ntp true >/dev/null 2>&1 || warn "could not enable NTP"

# ---------------------------------------------------------------- swap
log "disabling swap"
swapoff -a
sed -ri '/^[^#].*[[:space:]]swap[[:space:]]/ s/^/#/' /etc/fstab
while read -r unit; do
  [[ -n $unit ]] && systemctl mask "$unit" >/dev/null 2>&1 || true
done < <(systemctl list-units --type=swap --all --plain --no-legend 2>/dev/null | awk '{print $1}')
if [[ -e /usr/lib/systemd/system-generators/zram-generator ]]; then : > /etc/systemd/zram-generator.conf; fi
rm -f /swap.img /swapfile
[[ -z $(swapon --show --noheadings) ]] || die "swap still active: $(swapon --show)"

# ---------------------------------------------------------------- kernel
log "kernel modules + sysctl"
cat > /etc/modules-load.d/k8s.conf <<EOF
overlay
br_netfilter
EOF
modprobe overlay
modprobe br_netfilter

cat > /etc/sysctl.d/99-k8s.conf <<EOF
net.ipv4.ip_forward                 = 1
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
fs.inotify.max_user_instances       = 8192
fs.inotify.max_user_watches         = 524288
EOF
# systemd's default rp_filter=2 can drop Cilium traffic; override last
cat > /etc/sysctl.d/99-zzz-override_cilium.conf <<EOF
net.ipv4.conf.lxc*.rp_filter = 0
net.ipv4.conf.cilium_*.rp_filter = 0
net.ipv4.conf.all.rp_filter = 0
EOF
sysctl --system >/dev/null

# ---------------------------------------------------------------- base packages
log "installing base packages"
"${APT[@]}" update
"${APT[@]}" install ca-certificates curl gpg socat conntrack ethtool iptables jq

# ---------------------------------------------------------------- containerd
if dpkg -s containerd.io >/dev/null 2>&1; then
  log "containerd.io (Docker repo) already installed — reusing it"
else
  log "installing containerd"
  "${APT[@]}" install containerd
fi

mkdir -p /etc/containerd
if [[ -f $CFG && ! -f $CFG.orig ]]; then cp "$CFG" "$CFG.orig"; fi
containerd config default > "$CFG"
sed -ri 's/^([[:space:]]*)SystemdCgroup[[:space:]]*=[[:space:]]*false/\1SystemdCgroup = true/' "$CFG"
if ! grep -q 'SystemdCgroup = true' "$CFG"; then
  sed -ri "/\[plugins\.('io\.containerd\.cri\.v1\.runtime'|\"io\.containerd\.grpc\.v1\.cri\")\.containerd\.runtimes\.runc\.options\]/a\            SystemdCgroup = true" "$CFG"
fi
grep -q 'SystemdCgroup = true' "$CFG" || die "could not set SystemdCgroup in $CFG"

if [[ -n ${HTTP_PROXY:-}${HTTPS_PROXY:-} ]]; then
  log "configuring containerd proxy"
  mkdir -p /etc/systemd/system/containerd.service.d
  cat > /etc/systemd/system/containerd.service.d/http-proxy.conf <<EOF
[Service]
Environment="HTTP_PROXY=${HTTP_PROXY:-}" "HTTPS_PROXY=${HTTPS_PROXY:-}" "NO_PROXY=${NO_PROXY:-localhost,127.0.0.1,10.96.0.0/12,10.244.0.0/16}"
EOF
fi

cat > /etc/crictl.yaml <<EOF
runtime-endpoint: $CRI_SOCK
image-endpoint: $CRI_SOCK
timeout: 30
EOF

systemctl daemon-reload
systemctl enable --now containerd
systemctl restart containerd

# ---------------------------------------------------------------- kubeadm / kubelet / kubectl
log "adding Kubernetes $K8S_MINOR repo"
install -m 0755 -d /etc/apt/keyrings
curl -fsSL "https://pkgs.k8s.io/core:/stable:/${K8S_MINOR}/deb/Release.key" \
  | gpg --dearmor --yes -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/${K8S_MINOR}/deb/ /" \
  > /etc/apt/sources.list.d/kubernetes.list
"${APT[@]}" update

if [[ -n $K8S_PATCH ]]; then
  pkgver=$(apt-cache madison kubeadm | awk -v p="${K8S_PATCH}-" 'index($3,p)==1 {print $3; exit}')
  [[ -n $pkgver ]] || die "kubeadm $K8S_PATCH not found in $K8S_MINOR repo"
  log "installing kubelet/kubeadm/kubectl $pkgver"
  "${APT[@]}" install --allow-downgrades --allow-change-held-packages \
    "kubelet=$pkgver" "kubeadm=$pkgver" "kubectl=$pkgver"
else
  log "installing latest kubelet/kubeadm/kubectl from $K8S_MINOR"
  "${APT[@]}" install --allow-change-held-packages kubelet kubeadm kubectl
fi
apt-mark hold kubelet kubeadm kubectl >/dev/null

if [[ -n $NODE_IP ]]; then
  ip -4 -o addr show | grep -qwF "$NODE_IP" || die "NODE_IP $NODE_IP is not configured on this host"
  echo "KUBELET_EXTRA_ARGS=--node-ip=$NODE_IP" > /etc/default/kubelet
  log "kubelet --node-ip=$NODE_IP"
fi
systemctl enable kubelet >/dev/null 2>&1

KVER=$(kubeadm version -o short)

# match containerd sandbox image to kubeadm's pause version (avoids kubeadm warning)
PAUSE=$(kubeadm config images list --kubernetes-version "$KVER" 2>/dev/null | grep '/pause:')
sed -ri "s#^([[:space:]]*)(sandbox_image|sandbox)[[:space:]]*=.*#\1\2 = \"$PAUSE\"#" "$CFG"
systemctl restart containerd

# ---------------------------------------------------------------- firewall
if command -v ufw >/dev/null 2>&1 && ufw status | grep -q "Status: active"; then
  log "ufw active — opening Kubernetes + Cilium ports"
  for p in 6443/tcp 2379:2380/tcp 10250/tcp 10257/tcp 10259/tcp 30000:32767/tcp \
           4240/tcp 4244/tcp 4245/tcp 8472/udp 51871/udp; do
    ufw allow "$p" >/dev/null
  done
fi

# ---------------------------------------------------------------- images
pull() {
  local n
  for n in 1 2 3; do
    if crictl pull "$1" >/dev/null; then log "pulled $1"; return 0; fi
    warn "pull attempt $n failed: $1"; sleep 5
  done
  die "cannot pull $1"
}

if [[ $SKIP_IMAGE_PULL != 1 ]]; then
  if [[ $ROLE == worker ]]; then
    imgs=("$PAUSE")
  else
    mapfile -t imgs < <(kubeadm config images list --kubernetes-version "$KVER" | grep -v kube-proxy)
  fi
  if [[ $PREPULL_CILIUM == 1 ]]; then
    imgs+=("quay.io/cilium/cilium:v${CILIUM_VERSION}"
           "quay.io/cilium/operator-generic:v${CILIUM_VERSION}"
           "quay.io/cilium/hubble-relay:v${CILIUM_VERSION}")
  fi
  log "pre-pulling ${#imgs[@]} images"
  for i in "${imgs[@]}"; do pull "$i"; done
fi

# ---------------------------------------------------------------- summary
cat <<EOF

================================================================
 Node ready for kubeadm
----------------------------------------------------------------
 Hostname      : $(hostname)
 IPv4          : $(hostname -I)
 Kubernetes    : $KVER   (containerd $(containerd --version | awk '{print $3}'))
 machine-id    : $(cat /etc/machine-id)
 product_uuid  : $(cat /sys/class/dmi/id/product_uuid 2>/dev/null || echo n/a)
   ^ both must be UNIQUE per node (cloned VMs often share them)
 Log           : $LOG
----------------------------------------------------------------
 Master:
   kubeadm init --skip-phases=addon/kube-proxy \\
     --apiserver-advertise-address=<MASTER_IP> \\
     --pod-network-cidr=10.244.0.0/16
 Worker:
   kubeadm join <MASTER_IP>:6443 --token ... --discovery-token-ca-cert-hash ...
================================================================
EOF
