# MariaDB Setup — Docker (Cyberlab)

Host: **Desktop PC (simulated branch office)**  
OS: **Ubuntu 24.04 LTS**  
Container Engine: **Docker** (from Ubuntu repo)

---

### 1) Download MariaDB Image

I used the official MariaDB 10.11 image from Docker Hub:

```bash
docker pull mariadb:10.11
```
Check that the image downloaded:
```bash
docker images | grep mariadb
```

### 2) Run MariaDB Container
I deployed MariaDB with a test inventory database.
```bash
docker run -d \
  --name cyberlab-mariadb \
  -e MARIADB_ROOT_PASSWORD=admin123 \
  -e MARIADB_DATABASE=inventory \
  -p 3306:3306 \
  mariadb:10.11
```
### 3) Verify Container is Running
```bash
docker ps                               # confirm container is running
docker logs -f cyberlab-mariadb         # check startup logs
```

### 4) Test Database Connection
Install the MariaDB client and connect:
```bash
sudo apt install -y mariadb-client
mysql -h 127.0.0.1 -P 3306 -u root -p
```
*Password: admin123 (lab-only, intentionally weak for testing)*

### 5) Useful Commands
```bash
docker exec -it cyberlab-mariadb bash   # shell into container
docker stop cyberlab-mariadb            # stop container
docker start cyberlab-mariadb           # start container
docker restart cyberlab-mariadb         # restart container
docker rm -f cyberlab-mariadb           # remove container (data persists if mapped to host volume)
docker logs --tail 50 cyberlab-mariadb  # show last 50 log lines

```

✅ MariaDB is now running as a container on the Desktop PC