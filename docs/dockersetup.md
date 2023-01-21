## Docker setup on ubuntu 20

Step is simple with easy install

example i have a remote vm with ip 192.168.1.19

Lets ssh in to the vm. If you are using putty just login. bellow ssh command is only for mac or linux users.

```
ssh vijay@192.168.1.19
```
Now run the command to download docker install script.
```
curl -fsSL https://get.docker.com -o get-docker.sh
```
If you dont have curl command , please get it install with. 
```
sudo apt install curl -y
```
Lets install docker with script 
```
sudo bash get-docker.sh
```
Now lets add current user in docker group
```
sudo usermod -aG docker vijay
```
**Note:** Please log out now from terminal and login back 
to validate just run the id command and you will see docker also as a group for the user

validate installation with this command

```bash
docker ps
```
and
```
id vijay
uid=1000(vijay) gid=1000(vijay) groups=1000(vijay),4(adm),20(dialout),24(cdrom),25(floppy),27(sudo),29(audio),30(dip),44(video),46(plugdev),117(netdev),118(lxd),998(docker)
```
Done ! you have installed docker correctly!   
Now its time to run commands like docker ps to validate docker is working.
