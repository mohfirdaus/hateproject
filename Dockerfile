# Gunakan image resmi Python
FROM python:3.10

# Atur direktori kerja di container
WORKDIR /app

# Salin requirements.txt dan install dependencies Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Salin sisa kode proyek
COPY . /app/

# Install dependencies untuk Selenium
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    xvfb \
    libxi6 \
    libgconf-2-4 \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install

# Install ChromeDriver
RUN wget -q https://chromedriver.storage.googleapis.com/$(curl -s https://chromedriver.storage.googleapis.com/LATEST_RELEASE)/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip \
    && mv chromedriver /usr/local/bin/ \
    && rm chromedriver_linux64.zip

# Jalankan perintah manage.py collectstatic (untuk mengumpulkan static files)
RUN python manage.py collectstatic --noinput

# Expose port 8000 untuk Django
EXPOSE 9876

# Tentukan perintah untuk menjalankan aplikasi Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:9876"]
