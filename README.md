#  AI Medical Coder

> **Automated Medical Coding System** for extracting **ICD-10, CPT, and HCPCS** codes from clinical documents (SOAP notes, Operative/Diagnostic reports, etc.), ensuring **HIPAA compliance**, **OCR processing**, and **AI-assisted inference** using GPT-5.

---

##  Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Folder Structure](#folder-structure)
- [Database Schema](#database-schema)
- [Backend APIs](#backend-apis)
- [HIPAA Workflow Integration](#hipaa-workflow-integration)
- [Testing the Workflow](#testing-the-workflow)
- [Deployment (Internal Server)](#deployment-internal-server)
- [Commands Reference](#commands-reference)
- [Future Enhancements](#future-enhancements)

---

##  Overview

The **AI Medical Coder** automates the medical coding process through a secure pipeline:

1. **Upload medical document** → stored in backend/medicalcoder
2. **HIPAA compliance** → PHI redaction (using `hippa_pipeline.py`)
3. **OCR processing** → text extraction via internal OCR service (`ocr-direct`)
4. **Code generation** → GPT-5 inference for ICD-10, CPT, HCPCS codes
5. **Database logging** → all documents, outputs, and metadata persisted
6. **Results returned** via REST API in structured JSON schema

---

##  System Architecture
OCR Server (8122) ←→ HIPAA Pipeline ←→ AI Code Generator (GPT-5)
PostgreSQL DB / SQLite (dev)


---

## ⚙️ Features

✅ HIPAA compliant PHI redaction  
✅ OCR text extraction (image / PDF)  
✅ AI medical code generation (ICD-10, CPT, HCPCS)  
✅ Modular prompt engineering  
✅ Code filtering & billing validation  
✅ Detailed logging & error tracking  
✅ REST API endpoints for integration  
✅ Secure internal deployment support  

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|-------------|
| Backend | Django 5 + DRF |
| AI Inference | GPT-5 (API) |
| OCR | Internal service @ `http://10.0.0.84:8122/ocr-direct` |
| Database | PostgreSQL (dev/test uses SQLite) |
| Authentication | JWT |
| Deployment | Gunicorn + Nginx (on Linux internal server) |
| Infrastructure | Docker (optional), Paramiko (for remote SFTP integration) |

---

## 📁 Folder Structure

backend/
│
├── medicalcoder/
│ ├── code_generation.py # Main AI workflow controller
│ ├── hippa_pipeline.py # PHI redaction module
│ ├── models.py # DB models
│ ├── serializers.py # DRF serializers
│ ├── views.py # API views
│ ├── urls.py # Endpoint routing
│ ├── tests/ # Unit & integration tests
│ └── utils/ # Helper functions / prompt templates
│
├── manage.py
└── requirements.txt

## To run the full pipeline on your development server:
# 1. Activate virtual environment
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run migrations
python manage.py makemigrations
python manage.py migrate

# 4. Create superuser
python manage.py createsuperuser

# 5. Run development server
python manage.py runserver 0.0.0.0:8000






