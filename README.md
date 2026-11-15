<p align="center">
  <img src="static/img/nurseon-logo.png" alt="Nurseon logo" width="104">
</p>

<h1 align="center">Nurseon</h1>

<p align="center">
  <strong>A structured and personalized learning platform for nursing students.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Django-6.1.3-0C4B33?logo=django&logoColor=white" alt="Django 6.1.3">
  <img src="https://img.shields.io/badge/Python-3.14.5-3776AB?logo=python&logoColor=white" alt="Python 3.14.5">
  <img src="https://img.shields.io/badge/Database-PostgreSQL-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Status-Active%20Development-orange" alt="Active development">
</p>

<p align="center">
  <a href="#overview">Overview</a> ·
  <a href="#features">Features</a> ·
  <a href="#tech-stack">Tech Stack</a> ·
  <a href="#getting-started">Getting Started</a> ·
  <a href="#routes">Routes</a> ·
  <a href="#testing">Testing</a> ·
  <a href="#roadmap">Roadmap</a>
</p>

---

## Overview

Nurseon is an AI nursing review website that has been developed with the intention of making the process of nursing students getting ready for nursing board exams more efficiently. This platform offers a structured and personalized learning experience through many features including AI Nurse Tutor, nursing documents, quizzes, case studies, mock nursing board exams, nursing care plans, interactive anatomy lab, surgical skills, and tracking of progress. These features make it easy for nursing students to review the necessary concepts, practice their clinical decision making, and identify their weak areas. Implementing AI with interactive learning materials will make the process of preparation easier and more convenient for nursing students.

## Features

The following ten features define the complete product scope. Account, profile, and role-based administration foundations are present; the learning modules and result tracking are planned work.

### 1. AI Nurse Tutor — Planned

Let students ask nursing-related questions and receive AI-generated explanations and study guidance.

### 2. Nursing Documents — Planned

Provide a searchable library of nursing study materials and references, organized by topic and difficulty.

### 3. Interactive Quizzes — Planned

Offer topic-based multiple-choice quizzes with immediate answer feedback and recorded scores.

### 4. Case Studies — Planned

Present clinical nursing scenarios for applied reasoning, with scoring and feedback after submission.

### 5. Mock Board Examination — Planned

Simulate the NLE with timed, scored examinations, selectable difficulty, and a detailed score breakdown.

### 6. Nursing Care Plans — Planned

Allow students to create, save, edit, and review structured care plans as guided learning activities.

### 7. Interactive Anatomy Lab — Planned

Support anatomy review through interactive exploration of labeled body structures.

### 8. Surgical Skills Resources — Planned

Provide step-by-step educational guides for basic nursing-related clinical procedures.

### 9. Progress Tracking and Dashboard — Partially implemented

The role-based dashboard shell exists. Recording and displaying quiz, case-study, and mock-exam results over time is planned.

### 10. User Account Management — Implemented

- Register, sign in with a username or email, manage profile information, and sign out.
- Use Django session authentication, form validation, and CSRF protection.
- Provide role-based dashboard routing and administrator tools for user accounts.

## Tech Stack

| Layer | Technology |
| --- | --- |
| Backend | Django 6.1.3 |
| Runtime | Python 3.14.5 in the current development environment |
| Frontend | Django templates, HTML, Tailwind CSS, JavaScript |
| Database | PostgreSQL (Supabase), configured through `DATABASE_URL` |
| Configuration | `python-dotenv` |
| Testing | Django test framework |

## Getting Started

### Prerequisites

- Python 3.14.5, or another version compatible with the pinned Django release
- PostgreSQL (Supabase) database
- Git

### 1. Clone the repository

```bash
git clone https://github.com/josephrubiojimenez/Nurseon-Jimenez-Joseph-G02.git
cd Nurseon-Jimenez-Joseph-G02
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
```

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a private `.env` file in the project root. Do not commit it. The application reads these variables:

| Variable | Description |
| --- | --- |
| `SECRET_KEY` | Django secret key |
| `DEBUG` | Debug mode; defaults to `False` |
| `DATABASE_URL` | PostgreSQL connection URL |
| `ADMIN_EMAIL` | Email for the configured administrator account |
| `ADMIN_PASSWORD` | Password for the configured administrator account |
| `ADMIN_USERNAME` | Optional administrator username; defaults to `admin` |

Generate a Django secret key with:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Apply database migrations

```bash
python manage.py migrate
```

### 6. Run the development server

```bash
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/). The root page redirects to the dashboard. Registration is available at `/accounts/signup/`.

## Administrator Setup

The project synchronizes an administrator account from `ADMIN_EMAIL`, `ADMIN_PASSWORD`, and optionally `ADMIN_USERNAME`. You can also run:

```bash
python manage.py setup_admin
```

> **Warning:** The current automatic synchronization and setup command can delete other administrator-role accounts. Review `accounts/admin_setup.py` before using this with shared or production data, and keep a database backup.

## Routes

| URL | Access | Description |
| --- | --- | --- |
| `/` | Public redirect | Redirects to the dashboard |
| `/accounts/signup/` | Public | Student registration |
| `/accounts/login/` | Public | Sign in |
| `/accounts/logout/` | Authenticated | Sign out |
| `/accounts/profile/` | Authenticated | View and update profile |
| `/dashboard/` | Authenticated | Student dashboard; administrators are redirected |
| `/dashboard/admin-panel/` | Administrator | Manage user accounts |
| `/admin/` | Django staff | Django administration site |

## Testing

Run the Django test suite with:

```bash
python manage.py test
```

Use an isolated test database rather than a production database. Some existing tests may need updates to match the current routes and dashboard templates.

## Deployment Notes

- `ALLOWED_HOSTS` currently includes only `localhost` and `127.0.0.1`. Add explicit deployment hostnames in `nurseon/settings.py`; do not use a wildcard.
- Admin-role synchronization currently can remove other administrator accounts. Review this behavior before using it with shared or production data.
- Demoting an administrator currently does not revoke Django's `is_staff` and `is_superuser` flags.
- Keep `.env` and all credentials out of version control. Set `DEBUG` to `False` and use a unique `SECRET_KEY` in production.

## Project Structure

```text
.
├── accounts/       # Custom user, authentication, profiles, and admin tools
├── dashboard/      # Student and administrator dashboard views
├── nurseon/        # Django settings and project URL configuration
├── static/         # Logo and JavaScript assets
├── templates/      # Shared layouts and application pages
├── manage.py       # Django management entry point
└── requirements.txt
```

## Roadmap

- [x] User registration, authentication, and profile management
- [x] Role-based dashboard shell and administrator account tools
- [ ] AI Nurse Tutor
- [ ] Searchable Nursing Documents library
- [ ] Interactive topic quizzes with recorded scores
- [ ] Scored clinical Case Studies
- [ ] Timed Mock Board Examination with score breakdown
- [ ] Saveable and editable Nursing Care Plans
- [ ] Interactive Anatomy Lab
- [ ] Surgical Skills Resources
- [ ] Long-term learning progress and analytics

## License

No license file is currently included in this repository.
