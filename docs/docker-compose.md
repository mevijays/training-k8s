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

### Health Checks
Add health checks to ensure containers are running properly:

```yaml
services:
  wordpress:
    image: wordpress:latest
    ports:
      - 80:80
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 40s
```

### Service Dependencies
Use `depends_on` to define service startup order:

```yaml
services:
  db:
    image: mariadb:10.6.4-focal
    volumes:
      - db_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  wordpress:
    image: wordpress:latest
    depends_on:
      db:
        condition: service_healthy
    environment:
      - WORDPRESS_DB_HOST=db
      - WORDPRESS_DB_USER=wordpress
      - WORDPRESS_DB_PASSWORD=wordpress
      - WORDPRESS_DB_NAME=wordpress
```

### Environment Files
Use `.env` files to manage environment variables securely:

1. Create `.env` file in the same directory as `docker-compose.yml`:
```
MYSQL_ROOT_PASSWORD=your_secure_password
WORDPRESS_DB_PASSWORD=your_db_password
```

2. Reference in docker-compose.yml:
```yaml
services:
  wordpress:
    environment:
      - WORDPRESS_DB_PASSWORD=${WORDPRESS_DB_PASSWORD}
```

### Docker Compose Version
- `docker-compose` (standalone CLI tool) - v1.x
- `docker compose` (built-in Docker CLI plugin) - v2.x

**Recommendation**: Use `docker compose` (v2.x) as it's the future direction from Docker.
 - Example Mysql with Adminer
```
version: '3.7'
services:
  mysql_db_container:
    image: mysql:latest
    command: --default-authentication-plugin=mysql_native_password
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
    ports:
      - 3306:3306
    volumes:
      - mysql_db_data_container:/var/lib/mysql
  adminer_container:
    image: adminer:latest
    environment:
      ADMINER_DEFAULT_SERVER: mysql_db_container
    ports:
      - 8080:8080

volumes:
  mysql_db_data_container:
```
