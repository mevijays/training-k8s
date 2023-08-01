# Docker install with Ansible

```yaml
---

- hosts: all
  become: true
  tasks:
  - name: Update apt cache
    apt: update_cache=yes
  - name: Install packages
    apt: name={{ item }} state=present
    with_items:
      - apt-transport-https
      - ca-certificates
      - curl
      - software-properties-common
  - name: Add GPG key
    apt_key: url=https://download.docker.com/linux/ubuntu/gpg state=present
  - name: Add Docker apt repository
    apt_repository: repo='deb [arch=amd64] https://download.docker.com/linux/ubuntu {{ ansible_distribution_release }} stable'
  - name: Install Docker
    apt: name=docker-ce state=present
  - name: Add user to Docker group
    user: name={{ ansible_user_id }} groups=docker append=yes
  - name: Enable and start Docker service
    service: name=docker state=started enabled=yes
```
