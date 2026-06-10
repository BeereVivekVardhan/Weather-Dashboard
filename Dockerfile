# 1. Base image (Python installed)
FROM python:3.11-slim

# 2. Set working directory inside container
WORKDIR /app

# 3. Copy requirements file
COPY requirements.txt .

# 4. Install Python libraries
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy all project files
COPY . .

# 6. Tell Docker which port app uses
EXPOSE 5000

# 7. Start the Flask app
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]