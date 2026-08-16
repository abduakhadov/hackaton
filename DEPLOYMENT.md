# Royal Barber — Serverga Yuklash (Deployment) Yo'riqnomasi

Ushbu yo'riqnoma orqali loyihani istalgan Linux VPS (Ubuntu 22.04 / 24.04), DigitalOcean, Hetzner, AWS yoki Cloud serverlarga 2 xil usulda tez va xavfsiz joylashtirishingiz mumkin.

---

## 🚀 1-usul: Docker & Docker-Compose orqali (Tavsiya etiladi)

Eng oson va tezkor usul. Barcha xizmatlar (Django, PostgreSQL, Nginx) konteynerlarda avtomatik sozlanadi.

### 1. Serverda Docker-ni o'rnatish (Ubuntu):
```bash
sudo apt update
sudo apt install -y docker.io docker-compose git
sudo systemctl enable --now docker
```

### 2. Loyihani serverga yuklab olish:
```bash
git clone <LOYIHA_GIT_URL>
cd barber_booking
```

### 3. `.env` faylini yaratish va sozlash:
```bash
cp .env.example .env
nano .env
```
`.env` faylida quyidagi qiymatlarni o'zgartiring:
- `SECRET_KEY`: Tasodifiy uzundan-uzun mahfiy kalit.
- `DEBUG`: `False` qiling.
- `ALLOWED_HOSTS`: Serveringiz IP manzili yoki domeningiz (masalan: `mybarber.uz,123.45.67.89`).

### 4. Konteynerlarni ishga tushirish:
```bash
docker-compose up -d --build
```

Barchasi tayyor! Loyihangiz server IP manzili orqali `http://SERVER_IP` da ishlaydi.

---

## 🛠 2-usul: Standart Linux VPS (Systemd + Gunicorn + Nginx)

Agar Docker ishlatmasdan to'g'ridan-to'g'ri Linux OS da ishlatmoqchi bo'lsangiz:

### 1. Kerakli paketlarni o'rnatish:
```bash
sudo apt update
sudo apt install -y python3-pip python3-venv nginx git
```

### 2. Virtual muhit va bog'liqliklarni o'rnatish:
```bash
cd /var/www
sudo git clone <LOYIHA_GIT_URL> royal_barber
cd royal_barber/barber_booking

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Statik fayllarni yig'ish va migratsiya:
```bash
cp .env.example .env
# .env faylini tahrirlang: nano .env

python manage.py migrate
python manage.py collectstatic --noinput
python manage.py seed_demo
```

### 4. Gunicorn uchun Systemd xizmatini yaratish:
Fayl ochamiz: `/etc/systemd/system/royal_barber.service`
```ini
[Unit]
Description=Royal Barber Gunicorn Daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/royal_barber/barber_booking
ExecStart=/var/www/royal_barber/barber_booking/venv/bin/gunicorn --workers 3 --bind unix:/var/www/royal_barber/barber_booking/royal_barber.sock config.wsgi:application

[Install]
WantedBy=multi-user.target
```

Xizmatni ishga tushirish:
```bash
sudo systemctl daemon-reload
sudo systemctl start royal_barber
sudo systemctl enable royal_barber
```

### 5. Nginx-ni sozlash:
Fayl ochamiz: `/etc/nginx/sites-available/royal_barber`
```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_SERVER_IP;

    location /static/ {
        alias /var/www/royal_barber/barber_booking/staticfiles/;
    }

    location /media/ {
        alias /var/www/royal_barber/barber_booking/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/royal_barber/barber_booking/royal_barber.sock;
    }
}
```

Nginx xizmatini yoqish va qayta yuklash:
```bash
sudo ln -s /etc/nginx/sites-available/royal_barber /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔒 Free SSL (HTTPS) Sertifikatini o'rnatish (Certbot)

Agar domeningiz bo'lsa, bepul HTTPS sertifikatini 1 daqiqada yoqishingiz mumkin:
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

## 🔐 Standart Admin Parollari (Seed Data):
- **Superadmin:** Tel: `+998900000000` | Parol: `admin12345`
- **Demo Usta:** Tel: `+998911111111` | Parol: `barber12345`
- **Demo Mijoz:** Tel: `+998922222222` | Parol: `client12345`
