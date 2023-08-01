# Installation of ansible

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
