# Terminal Commands to Build and Run

## Build the Docker Image

```
bash
docker build -t attendance-staff-portal .
```

## Run the Container with .env file on Port 80

```
bash
docker run -d -p 80:5000 --env-file .env --name attendance-staff attendance-staff-portal
```

---

## Useful Commands

```
bash
# Check if container is running
docker ps

# View logs
docker logs attendance-staff

# Stop the container
docker stop attendance-staff

# Start the container again
docker start attendance-staff

# Remove the container
docker rm attendance-staff
```

---

## Access the Site

- Staff Portal: http://185.252.235.2
- Casual Worker: http://185.252.235.2/casual
- Admin Dashboard: http://185.252.235.2/admin-login
