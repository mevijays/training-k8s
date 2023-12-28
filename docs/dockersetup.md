## Docker setup on ubuntu 22

Step is simple with easy install

example i have a remote vm with ip 192.168.1.19

Lets ssh in to the vm. If you are using putty just login. bellow ssh command is only for mac or linux users.

```
ssh vijay@192.168.1.19
```
Now run the command to download docker install script.
```
curl -fsSL https://get.docker.com | sudo bash
```
If you dont have curl command , please get it install with. 
```
sudo apt install curl -y
```

Now lets add current user in docker group
```
sudo usermod -aG docker $(whoami)
```
**Note:** Please log out now from terminal and login back 
to validate just run the id command and you will see docker also as a group for the user

validate installation with this command

```bash
docker ps
```
and
```
id $(whoami)
uid=1000(vijay) gid=1000(vijay) groups=1000(vijay),4(adm),20(dialout),24(cdrom),25(floppy),27(sudo),29(audio),30(dip),44(video),46(plugdev),117(netdev),118(lxd),998(docker)
```
Done ! you have installed docker correctly!   
Now its time to run commands like docker ps to validate docker is working.

# Clean uninstall of docker-ce
Run bellow commands in the terminal

```bash
sudo apt-get purge -y docker-engine docker docker.io docker-ce docker-ce-cli docker-compose-plugin
sudo apt-get autoremove -y --purge docker-engine docker docker.io docker-ce docker-compose-plugin
sudo rm -rf /var/lib/docker /etc/docker
sudo rm /etc/apparmor.d/docker
sudo groupdel docker
sudo rm -rf /var/run/docker.sock
```

Thanks@
