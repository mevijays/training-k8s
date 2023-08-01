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
