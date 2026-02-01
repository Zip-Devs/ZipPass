# 🔐 ZipPass

**ZipPass** is a lightweight local password utility designed for privacy, simplicity, and offline usage.  
A pet-project created for learning and practical use.

**ZipPass** — лёгкая локальная утилита для работы с паролями.  
Pet-проект, созданный для обучения и практики.

---

## 🚀 Features | Возможности

### English
- Password generation
- Local password storage (offline)
- Search by:
  - website
  - login / username
  - email
- Import and export:
  - CSV → ZipPass
  - ZipPass → CSV
- Simple and intuitive interface
- Minimal dependencies
- Works without Python (Windows `.exe`)

### Русский
- Генерация паролей
- Локальное хранение данных (офлайн)
- Поиск по:
  - сайтам
  - логинам / именам пользователей
  - почте
- Импорт и экспорт:
  - CSV → ZipPass
  - ZipPass → CSV
- Простой и понятный интерфейс
- Минимум зависимостей
- Работает без установленного Python (Windows `.exe`)

---

## 🛠 Technologies | Технологии
- Python 3
- tkinter / CLI (depending on implementation)
- PyInstaller (for `.exe` build)

---

## 📦 Installation & Run | Установка и запуск

### Windows (Recommended)
1. Open **Releases**
2. Download `ZipPass.exe`
3. Run the application

> ⚠️ Windows may show a warning about an unknown application.  
> This is normal for open-source utilities without a digital signature.

---

### From source (Python)

```bash
git clone https://github.com/Zip-Devs/ZipPass.git
cd ZipPass
python app.py
