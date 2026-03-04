# Docker Deployment Commands

## Build the Docker Image

```
bash
docker build -t attendance-staff-portal .
```

## Run the Container

### Option 1: Map port 5000 to 5000
```
bash
docker run -d -p 5000:5000 --name attendance-staff attendance-staff-portal
```

### Option 2: Map port 5000 to 80 (As Requested)
```
bash
docker run -d -p 80:5000 --name attendance-staff attendance-staff-portal
```

## With Environment Variables (Production)

```
bash
docker run -d \
  -p 80:5000 \
  -e DATABASE_URL="postgresql://postgres:ra6oj7UjKpnW5n@db.sfwhsgrphfrsckzqquxp.supabase.co:5432/postgres" \
  -e SECRET_KEY="production_secret_key_change_this" \
  --name attendance-staff \
  attendance-staff-portal
```

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

# Rebuild the image
docker build -t attendance-staff-portal .

# Run interactively (for debugging)
docker run -it -p 80:5000 attendance-staff-portal /bin/bash
```

---

## Access the Site

- **If using port 80:** http://185.252.235.2
- **If using port 5000:** http://185.252.235.2:5000

---

## Note

The Dockerfile uses `python app.py` to run the application. This works because app.py already has:
```
python
app.run(debug=debug_mode, host='0.0.0.0', port=port)
```

The `host='0.0.0.0'` ensures the app accepts connections from outside the container.
