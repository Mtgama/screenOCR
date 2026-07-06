<div align="center">

# Persian OCR

**Professional Persian text recognition desktop application**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
![Version](https://img.shields.io/badge/Version-2.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![PyQt6](https://img.shields.io/badge/PyQt6-6.6%2B-green?logo=qt)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-lightgrey)
[![GitHub stars](https://img.shields.io/github/stars/Mtgama/screenOCR?style=social)](https://github.com/Mtgama/screenOCR/stargazers)

---

**[English](#english)** · **[فارسی](#persian)**

---

</div>

<a name="english"></a>

## English

### About

Persian OCR is a modern desktop application for extracting text from Persian (Farsi) images and PDFs. Built with **PyQt6** following **MVC architecture** and **HCI principles**, it provides a professional, fast, and fully offline OCR experience.

### Features

| Feature | Description |
|---------|-------------|
| Persian OCR | Extract text from Persian images and PDFs using Tesseract 5 |
| Modern UI | Dark purple theme, responsive layout, RTL support |
| Drag & Drop | Drop files directly onto the window |
| Screenshot OCR | Capture full screen or select a region for OCR |
| Batch Processing | Process entire folders of images at once |
| PDF Support | Multi-page PDF with per-page navigation and progress |
| Export | Save as `.txt`, `.docx`, or searchable `.pdf` |
| Image Enhancement | Upscale, denoise, deskew, binarize before OCR |
| Auto Layout Detection | Automatically selects optimal PSM mode |
| Persian Normalization | Fixes common OCR errors (ي→ی, ك→ک, ...) |
| Keyboard Shortcuts | `Ctrl+O` open · `Ctrl+S` save · `Ctrl+C` copy · `F5` run |
| Bilingual UI | Switch between English and Persian |
| Fully Offline | No internet required, all processing is local |

### Screenshots

<p align="center">
  <img src="https://github.com/Mtgama/screenOCR/blob/main/assets/image.png?raw=true" alt="Persian OCR App" width="700" />
</p>

### Installation

#### System-wide install (recommended)

```bash
git clone https://github.com/Mtgama/screenOCR.git
cd screenOCR
chmod +x install_user.sh
./install_user.sh
```

Then run from anywhere:

```bash
screenocr
```

The app will also appear in your application menu as **Persian OCR**.

#### Run from source

```bash
git clone https://github.com/Mtgama/screenOCR.git
cd screenOCR
pip install -r requirements.txt
python main.py
```

#### Uninstall

```bash
./uninstall_user.sh
```

### Dependencies

| Package | Purpose |
|---------|---------|
| PyQt6 | GUI framework |
| pytesseract | Tesseract OCR wrapper |
| Pillow | Image processing |
| PyMuPDF | PDF rendering |
| opencv-python-headless | Image enhancement |
| python-docx | Word export |
| pyautogui | Screenshot capture |

### Project Structure

```
screenOCR/
├── main.py                # Entry point
├── app.py                 # QApplication setup
├── core/                  # Business logic (Model)
│   ├── ocr_engine.py      # OCR execution & Tesseract config
│   ├── image_processor.py # Preprocessing, PSM detection
│   ├── pdf_handler.py     # PDF operations
│   └── export_manager.py  # Export to txt/docx/pdf
├── ui/                    # User interface (View)
│   ├── main_window.py     # Main window & drag-and-drop
│   ├── theme.py           # QSS stylesheet & colors
│   ├── screenshot.py      # PyQt6 region selector
│   ├── workers.py         # QThread for background OCR
│   └── panels/            # UI components
│       ├── actions_panel.py    # File/screenshot/OCR buttons
│       ├── preview_panel.py    # Document preview
│       ├── result_panel.py     # OCR result display
│       ├── settings_panel.py   # OCR settings
│       └── log_panel.py        # Activity log
├── utils/                 # Utilities
│   └── i18n.py            # Translation system (EN/FA)
├── assets/                # Icons & resources
├── Tesseract/             # OCR engine & language models
├── settings.py            # Settings persistence
├── tessdata_manager.py    # Model management
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Package configuration
├── install_user.sh        # System installer
└── uninstall_user.sh      # Uninstaller
```

### Architecture

The application follows **MVC (Model-View-Controller)** pattern:

- **Model** (`core/`) — Pure business logic, no UI dependencies. Handles OCR, image processing, PDF operations, and export.
- **View** (`ui/`) — PyQt6 widgets with QSS theming. Each panel is an independent, reusable component.
- **Controller** (`app.py` + `main_window.py`) — Mediates between UI and core logic using Qt signals/slots.

Key design principles:
- **Separation of concerns** — Each module has a single responsibility
- **Signal/Slot** — Loose coupling between components via Qt signals
- **QThread workers** — OCR runs in background threads, UI stays responsive
- **Theme system** — Centralized QSS stylesheet in `ui/theme.py`

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open file |
| `Ctrl+S` | Save output |
| `Ctrl+C` | Copy result |
| `F5` | Run OCR |
| `Escape` | Cancel screenshot selection |

### License

MIT

---

<a name="persian"></a>

## فارسی

### درباره برنامه

برنامه OCR فارسی یک اپلیکیشن دسکتاپ مدرن برای استخراج متن از تصاویر و PDF فارسی است. این برنامه با **PyQt6** و بر اساس معماری **MVC** و اصول **HCI** طراحی شده و تجربه OCR حرفه‌ای، سریع و کاملاً آفلاین را ارائه می‌دهد.

### امکانات

| امکان | توضیح |
|-------|-------|
| OCR فارسی | استخراج متن از تصاویر و PDF فارسی با Tesseract 5 |
| رابط کاربری مدرن | تم بنفش تیره، layout واکنش‌گرا، پشتیبانی RTL |
| Drag & Drop | رها کردن فایل مستقیماً روی پنجره |
| اسکرین‌شات OCR | ثبت کل صفحه یا انتخاب ناحیه برای OCR |
| پردازش دسته‌ای | پردازش کل پوشه تصاویر در یک مرحله |
| پشتیبانی PDF | PDF چند صفحه‌ای با ناوبری و پیشرفت صفحه‌به‌صفحه |
| خروجی | ذخیره در فرمت‌های `.txt` ،`.docx` یا `.pdf` قابل جستجو |
| بهبود تصویر | افزایش وضوح، کاهش نویز، اصلاح شیب، باینری‌سازی |
| تشخیص خودکار چیدمان | انتخاب خودکار بهترین حالت PSM |
| نرمال‌سازی متن فارسی | اصلاح خطاهای رایج OCR (ي→ی، ك→ک، ...) |
| میانبرهای کلیدی | `Ctrl+O` باز کردن · `Ctrl+S` ذخیره · `Ctrl+C` کپی · `F5` اجرا |
| رابط دوزبانه | تغییر بین فارسی و انگلیسی |
| کاملاً آفلاین | بدون نیاز به اینترنت، تمام پردازش‌ها محلی |

### اسکرین‌شات

<p align="center">
  <img src="https://github.com/Mtgama/screenOCR/blob/main/assets/image.png?raw=true" alt="Persian OCR App" width="700" />
</p>

### نصب

#### نصب سراسری (پیشنهادی)

```bash
git clone https://github.com/Mtgama/screenOCR.git
cd screenOCR
chmod +x install_user.sh
./install_user.sh
```

سپس از هر جایی اجرا کنید:

```bash
screenocr
```

برنامه در منوی برنامه‌های سیستم با نام **Persian OCR** نیز نمایش داده می‌شود.

#### اجرا از سورس

```bash
git clone https://github.com/Mtgama/screenOCR.git
cd screenOCR
pip install -r requirements.txt
python main.py
```

#### حذف

```bash
./uninstall_user.sh
```

### وابستگی‌ها

| پکیج | کاربرد |
|------|--------|
| PyQt6 | فریم‌ورک رابط کاربری |
| pytesseract | رابط Tesseract OCR |
| Pillow | پردازش تصویر |
| PyMuPDF | رندر PDF |
| opencv-python-headless | بهبود تصویر |
| python-docx | خروجی Word |
| pyautogui | ثبت اسکرین‌شات |

### ساختار دایرکتوری

```
screenOCR/
├── main.py                # نقطه ورود
├── app.py                 # راه‌اندازی QApplication
├── core/                  # منطق تجاری (Model)
│   ├── ocr_engine.py      # اجرای OCR و پیکربندی Tesseract
│   ├── image_processor.py # پیش‌پردازش، تشخیص PSM
│   ├── pdf_handler.py     # عملیات PDF
│   └── export_manager.py  # خروجی txt/docx/pdf
├── ui/                    # رابط کاربری (View)
│   ├── main_window.py     # پنجره اصلی و drag-and-drop
│   ├── theme.py           # استایل‌شیت QSS و رنگ‌ها
│   ├── screenshot.py      # انتخابگر ناحیه PyQt6
│   ├── workers.py         # QThread برای OCR پس‌زمینه
│   └── panels/            # کامپوننت‌های UI
│       ├── actions_panel.py    # دکمه‌های فایل/اسکرین‌شات/OCR
│       ├── preview_panel.py    # پیش‌نمایش سند
│       ├── result_panel.py     # نمایش نتیجه OCR
│       ├── settings_panel.py   # تنظیمات OCR
│       └── log_panel.py        # گزارش فعالیت
├── utils/                 # ابزارها
│   └── i18n.py            # سیستم ترجمه (EN/FA)
├── assets/                # آیکون‌ها و منابع
├── Tesseract/             # موتور OCR و مدل‌های زبانی
├── settings.py            # ذخیره تنظیمات
├── tessdata_manager.py    # مدیریت مدل‌ها
├── requirements.txt       # وابستگی‌های پایتون
├── pyproject.toml         # پیکربندی پکیج
├── install_user.sh        # اسکریپت نصب
└── uninstall_user.sh      # اسکریپت حذف
```

### معماری

برنامه بر اساس الگوی **MVC (Model-View-Controller)** طراحی شده:

- **Model** (`core/`) — منطق تجاری خالص، بدون وابستگی به UI. شامل OCR، پردازش تصویر، عملیات PDF و خروجی.
- **View** (`ui/`) — ویجت‌های PyQt6 با تم QSS. هر پنل یک کامپوننت مستقل و قابل استفاده مجدد.
- **Controller** (`app.py` + `main_window.py`) — اتصال UI به منطق اصلی از طریق signal/slot.

اصول طراحی کلیدی:
- **جداسازی مسئولیت** — هر ماژول یک وظیفه دارد
- **Signal/Slot** — اتصال شل بین کامپوننت‌ها از طریق سیگنال‌های Qt
- **QThread workers** — OCR در thread پس‌زمینه اجرا می‌شود، UI پاسخگو می‌ماند
- **سیستم تم** — استایل‌شیت QSS متمرکز در `ui/theme.py`

### میانبرهای کلیدی

| میانبر | عمل |
|--------|------|
| `Ctrl+O` | باز کردن فایل |
| `Ctrl+S` | ذخیره خروجی |
| `Ctrl+C` | کپی نتیجه |
| `F5` | اجرای OCR |
| `Escape` | لغو انتخاب ناحیه اسکرین‌شات |

### مجوز

MIT

---

<div align="center">

**Built with ❤️ by [Mehrdad Hasanzade & Mahshid jalili](https://github.com/Mtgama)**

</div>
