# Docker compose install  
- Intallation of docker-compose can be done via binary download. Follow these commands-
```
wget https://github.com/docker/compose/releases/download/v2.13.0/docker-compose-linux-x86_64

sudo mv docker-compose-linux-x86_64 /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```
- You can validate the installation by running bellow command
```
docker-compose version
```


- Sample docker-compose yaml file-
```
services:
  db:
    # We use a mariadb image which supports both amd64 & arm64 architecture
    image: mariadb:10.6.4-focal
    # If you really want to use MySQL, uncomment the following line
    #image: mysql:8.0.27
    command: '--default-authentication-plugin=mysql_native_password'
    volumes:
      - db_data:/var/lib/mysql
    restart: always
    environment:
      - MYSQL_ROOT_PASSWORD=somewordpress
      - MYSQL_DATABASE=wordpress
      - MYSQL_USER=wordpress
      - MYSQL_PASSWORD=wordpress
    expose:
      - 3306
      - 33060
  wordpress:
    image: wordpress:latest
    ports:
      - 80:80
    restart: always
    environment:
      - WORDPRESS_DB_HOST=db
      - WORDPRESS_DB_USER=wordpress
      - WORDPRESS_DB_PASSWORD=wordpress
      - WORDPRESS_DB_NAME=wordpress
volumes:
  db_data:
```

- To run the stack -
```
docker-compose up -d 
```
- to start , stop  & restart the stack-
```
```
docker-compose stop

docker-compose start

docker-compose restart
```

- To remove the stack 
```
docker-compose down
```

- To prune the volumes
```
docker volume prune
```
 
