## Setup NFS server for k8s storage LAB
- On the NFS server, update all packages.
```
sudo apt update
```
- Install the nfs-kernel-server package on the server.
```
 sudo apt install nfs-kernel-server
```
- Verify the status of the NFS server using the systemctl utility. It should display a status of active.
```
sudo systemctl status nfs-kernel-server.service
```
### Firewall setup ( if ufw enabled )
NFS has an inherent security risk because it allows external servers to access some of its directories and files. Configure the ufw firewall to enforce strict NFS access based on the IP address of the client. NFS allows access through port 2049. Verified users require access to this port to use NFS.

- On the server, verify the current ufw settings and verify whether a rule exists for NFS yet.
```
sudo ufw status

    Status: active

    To                         Action      From
    --                         ------      ----
    OpenSSH                    ALLOW       Anywhere
    Apache Full                ALLOW       Anywhere
    OpenSSH (v6)               ALLOW       Anywhere (v6)
    Apache Full (v6)           ALLOW       Anywhere (v6)
```
- Add a rule to allow port 2049 to accept traffic from the client’s IP address. Replace client_ip_addr with the address of the client Linode.
```
     sudo ufw allow from client_ip_addr to any port nfs
```
- Run ufw status again and confirm the rule has been added.
```
sudo ufw status
Status: active

To                         Action      From
--                         ------      ----
OpenSSH                    ALLOW       Anywhere
Apache Full                ALLOW       Anywhere
2049                       ALLOW       client_ip_addr
OpenSSH (v6)               ALLOW       Anywhere (v6)
Apache Full (v6)           ALLOW       Anywhere (v6)
```

- Create a directory on the NFS server to contain the shared files. It is best to create a separate export directory for each project to better control user access. Because the directory is created using sudo, the root user account owns this directory.
```
     sudo mkdir -p /nfs/share/project1
```
- For security reasons, NFS translates any root credentials from a client to nobody:nogroup. This restricts the ability of remote root users to invoke root privileges on the server. To grant client root users access to the export directory, change the directory ownership to nobody:nogroup.
```
     sudo chown nobody:nogroup /nfs/share/project1
```
- Adjust the file permissions for the directory. The following command grants NFS clients full read, write and execute privileges to the directory files.
```
     sudo chmod 777 /nfs/share/project1
```

- To add the new export directory to NFS, execute the following commands on the server.  
Edit the /etc/exports file.
```
     vi /etc/exports
```
- Add the following line and save the file. Replace client_ip_addr with the actual IP address or subnet of the client.

File: /etc/exports
```
    /nfs/share/project1  client_ip_addr(rw,sync,no_subtree_check)
```        

- Apply the configuration changes using the exportfs command.
```
 sudo exportfs -a
```
- View all the active exports and verify the /nfs/share/project1 directory has export status.
```
 sudo exportfs -v

/nfs/share/project1
client_ip_addr(rw,wdelay,root_squash,no_subtree_check,sec=sys,rw,secure,root_squash,no_all_squash)
```
- Restart the NFS utility using systemctl.
```
 sudo systemctl restart nfs-kernel-server
```
Done!
