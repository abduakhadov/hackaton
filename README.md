# Royal Barber — Barbershop Booking System

Django **MVT** (Model-View-Template) arxitekturasida qurilgan to'liq Full-Stack loyiha.
**DRF yo'q** — faqat klassik Django Forms, ModelForms va CBV (Class-Based Views).
Frontend: Tailwind CSS (CDN orqali).

## Loyiha strukturasi

```
barber_booking/
├── config/                 # Sozlamalar, root urls.py, wsgi/asgi
├── apps/
│   ├── users/               # CustomUser (telefon orqali login), Register/Login/Profile
│   ├── services/             # Category, Service — xizmatlar katalogi
│   ├── barbers/               # BarberProfile — ustalar, ish vaqti, xizmatlari
│   ├── bookings/               # Appointment — bron qilish, band vaqtni tekshirish
│   └── main/                    # Bosh sahifa, Biz haqimizda, Bog'lanish
├── templates/               # Barcha HTML shablonlar (base.html + har bir app uchun)
├── static/                  # Statik fayllar (ixtiyoriy, Tailwind CDN orqali ishlatiladi)
├── media/                    # Yuklangan rasmlar (avatar, xizmat rasmlari)
├── manage.py
└── requirements.txt
```

## O'rnatish

```bash
# 1) Virtual muhit yaratish
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2) Kutubxonalarni o'rnatish
pip install -r requirements.txt

# 3) Migratsiyalarni bajarish
python manage.py migrate

# 4) (Ixtiyoriy) Demo ma'lumotlar bilan to'ldirish
python manage.py seed_demo

# 5) Superuser yaratish (agar seed_demo ishlatilmasa)
python manage.py createsuperuser

# 6) Serverni ishga tushirish
python manage.py runserver
```

Saytga kirish: http://127.0.0.1:8000/
Admin panel: http://127.0.0.1:8000/admin/

## Demo login ma'lumotlari (seed_demo dan keyin)

| Rol      | Telefon           | Parol         |
|----------|--------------------|---------------|
| Admin    | +998900000000      | admin12345    |
| Usta     | +998911111111      | barber12345   |
| Mijoz    | +998922222222      | client12345   |

## Asosiy biznes-mantiq

`apps/bookings/models.py` dagi `Appointment.clean()` metodi:
- Xizmat davomiyligidan kelib chiqib `end_time` avtomatik hisoblanadi.
- Tanlangan vaqt ustaning ish vaqti oralig'ida ekanligi tekshiriladi.
- **Bitta usta bir vaqtning o'zida ikkita mijozni qabul qila olmasligi** — vaqt oralig'ining ustma-ust tushishi tekshiriladi (`pending`/`confirmed` holatidagi bronlar bilan solishtiriladi).

Bu tekshiruvlar `save()` chaqirilganda `full_clean()` orqali avtomatik ishga tushadi, shuningdek `BookingForm` orqali ham himoyalangan.

## Rollar (CustomUser.role)

- `client` — oddiy mijoz, bron qiladi
- `barber` — usta, `BarberProfile` orqali profilga ega, o'z jadvalini ko'radi (`/bookings/schedule/`)
- `admin` — xizmatlarni qo'shish/tahrirlash huquqiga ega (`is_staff=True` yoki `role=admin`)

## Muhim eslatmalar

- `AUTH_USER_MODEL = 'users.CustomUser'` — login **telefon raqami** orqali amalga oshiriladi (email/username emas).
- Rasm yuklash uchun `Pillow` kerak (`requirements.txt` da bor).
- Production uchun `DEBUG = False` qiling, `SECRET_KEY` ni maxfiy saqlang va PostgreSQL kabi haqiqiy DB ishlatishni tavsiya qilamiz.
