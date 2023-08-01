# Installation of ansible on control machine

```
sudo apt-get update 
sudo apt-get install software-properties-common 
sudo apt-add-repository ppa:ansible/ansible
sudo apt-get update 
sudo apt-get install ansible
```
## To enable password less authentication

- on ubuntu01

  ```
  ssh-keygen
  ```
  do enter on all prompts

  collect remote machine user id and ip address and run the command in ubuntu 01

  ```
  ssh-copy-id ubuntu02@<ip>
  ```
  give password if it is asking..

  Then to test password less auth run the command from ubuntu 01

  ```
  ssh ubuntu02@<ip>
  ```

# Configuration of remote machine

```
sudo visudo
```
Add sudo user in no-passwd   
find out the %sudo line and add prefix NOPASSWD:  before last ALL option in the same line   
```bash
%sudo ALL(ALL:ALL)  NOPASSWD:ALL
```
close the editor and save the content by pressing . ctrl+x followed by y and Enter

To validate if sudo is working fine without password run this.

```bash
sudo bash

```

If you see the locale specific error please run this

```bash
export LC_ALL=en_US.UTF8

```
# Inventory file

```
[web]
192.168.46.129  ansible_user=ubuntu02
```

Adhoc command to validate ansible connectivity

```
ansible -i inventory web -m ping
```


## Ansible playbook 

Sample playbook.yaml
```yaml
name: creating a file on remote machine
hosts: web
tasks:
  - name: create file
    copy:
      content: 'Hello from ansiblelab'
      dest: /home/ubuntu02/lab.txt
  - name: install git
    apt:
       name: apache2
       state: present
```


Run the playbook
```
ansible-playbook -i inventory web playbook.yaml

```







