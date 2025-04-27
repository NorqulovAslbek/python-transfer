# PROJECT

Ushbu loyiha plastik kartalar o‘rtasida pul o‘tkazmalarni amalga oshirish uchun yozilgan.

## ⚙️ O‘rnatish.

1. Loyihani yuklab oling :

```bash
  py -m venv venv   # Windows uchun virtual muhit yaratish.
```

```bash
  source venv/bin/activate # linux va macos uchun virtual muhitni aktivatsiya qilish.
```

2.Kutubxonalarni o'rnating:

```bash
  pip install -r requirements.txt 
```

3. ##### `.env` faylni yarating:

```.env
SECRET_KEY=***
DEBUG=True
DATABASE_URL=...
```
4.Migratsiya qiling:
```bash
  py manage.py migrate
```
## 🚀 Xizmatlarni ishga tushirish.
* Django serverni ishga tushuring.
```bash
   py manage.py runserver
```
* Celery va Celery beat va Redis hammasini sozlamari bitta Docker-compose fileda yozib qo'yilgan Docker fileni ishga tushurishirishimizni o'zi yetadi:
``` dockerfile
docker compose up --build
```
## 📡 API endpointlar.
Barcha so‘rovlar faqat **POST** usulida yuboriladi va yagona endpoint orqali amalga oshiriladi:  
**URL:** `http://127.0.0.1:8000/`

| JSON-RPC Method Nomi     | Tavsif                                                           |
|--------------------------|------------------------------------------------------------------|
| `transfer_create`        | Pul o‘tkazishni boshlash                                         |
| `confirm_transfer`       | OTP orqali tasdiqlash                                            |
| `transfer_state`         | Transfer holatini olish                                          |
| `transfer_cancel`        | Transferni bekor qilish                                          |
| `transfer_filter`        | Transferlar tarixini filterlash                                  |
| `card.info`              | Karta haqida ma’lumot olish faqat (30 sekund keshlanadi malumot) |

## 🧠 Qo‘shimcha
* Keshlash: Karta ma’lumotlari 30 soniyaga cache qilinadi.
* Loglash: Har bir request va response logga yoziladi.
* Celery: Davriy ishlar uchun ishlatiladi.







