FROM python:3.11-slim

WORKDIR /app

# Install gunicorn for production
RUN pip install --no-cache-dir gunicorn

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose the port that Render will use
EXPOSE 5000

# Use gunicorn for production - more reliable than flask dev server
# Bind to 0.0.0.0 and use the PORT environment variable
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
