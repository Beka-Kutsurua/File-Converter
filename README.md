
# 🗂️ Flask File Converter Web Application

A web-based file converter built with Flask. It supports document and image format conversion, OCR-based text extraction, and English-to-Georgian transliteration — all through a clean, intuitive interface.

---

## 🚀 Features

- 📄 Convert DOCX ⇄ PDF, JPG ⇄ PNG, and more
- 🔠 Transliterate English text to the Georgian alphabet
- 🧠 Extract text from images using OCR (EasyOCR)
- 📁 Upload multiple files and receive a ZIP download
- 🕓 Track past conversions via database logging
- 🐳 Dockerized for easy deployment

---

## 🛠️ Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript, Jinja2
- **Libraries**: docx2pdf, pdf2docx, Pillow, EasyOCR, PyMuPDF
- **Database**: SQLite + SQLAlchemy
- **Containerization**: Docker

---

## 📁 Project Structure

```
project/
├── conversion/
│   ├── __init__.py
│   ├── routes.py
│   ├── models.py
│   ├── scan.py
│   ├── translate.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── conversion.html
│   │   └── scan.html
│   └── static/
│       ├── css/
│       ├── uploads/
│       └── converted/
├── instance/
│   └── db  (SQLite file)
├── run.py
└── Dockerfile
```

---

## ▶️ How to Run the Project

### 🔧 Option 1: Run Locally (Python)

#### 1. Clone the repository

```bash
git clone https://github.com/yourusername/flask-file-converter.git
cd flask-file-converter
```

#### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install dependencies

```bash
pip install -r requirements.txt
```

#### 4. Run the Flask app

```bash
python run.py
```

By default, the app runs at `http://127.0.0.1:5000/`

---

### 🐳 Option 2: Run with Docker

#### 1. Build the image

```bash
docker build -t flask-file-converter .
```

#### 2. Run the container

```bash
docker run -p 5000:5000 flask-file-converter
```

Access the app in your browser at `http://localhost:5000/`

---

## 🙌 Acknowledgments

- [EasyOCR](https://github.com/JaidedAI/EasyOCR)
- [docx2pdf](https://github.com/AlJohri/docx2pdf)
- [Flask](https://flask.palletsprojects.com/)
- [Pillow](https://python-pillow.org/)
