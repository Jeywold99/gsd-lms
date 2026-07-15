# GSD HQ LMS

Self-hosted, invite-only learning platform for Get Sh*t Done HQ's paid courses.
Django + SQLite, containerized for a Raspberry Pi 4B behind a Cloudflare Tunnel,
managed through OpenMediaVault Compose. **No payments in the app** — access is
granted by admins (directly or via one-time invite codes) after payment happens
elsewhere.

## What's inside

- **5 courses seeded** — *The 5-Day AI Strategist Masterclass* is live with its
  five real lessons and branded PDF worksheets; *Personal Branding in 2026*,
  *AI and Automation*, *Conversion*, and *Sales Psychology* exist as
  draft/"coming soon" records ready to be filled in later.
- **Gating rule** — Lesson N+1 unlocks when the student's worksheet for
  Lesson N is uploaded **and approved by an admin** (and the lesson's optional
  drip `release_date`, if set, has passed).
- **Per-course enrollment** — students see *only* the courses they're enrolled
  in. Everything else 404s.
- **Roles** — Student (regular account) and Admin (`is_staff`; use a superuser
  for full access). Admin work happens in the Django admin (`/admin/`).
- **Auth** — login, logout, password reset, hashed passwords, and optional
  per-account TOTP 2FA (authenticator app) at */account/security/*.
- **Private files** — worksheets and student submissions live on the mounted
  volume and are served only through permission-checked views; media is never
  exposed publicly.

## Run it locally (development)

```bash
python -m venv .venv
.venv/Scripts/activate            # Windows  (source .venv/bin/activate on Linux/Mac)
pip install -r requirements.txt
set DEBUG=true                    # export DEBUG=true on Linux/Mac
python manage.py migrate
python manage.py seed_courses
python manage.py createsuperuser
python manage.py runserver
```

App: http://127.0.0.1:8000 · Admin: http://127.0.0.1:8000/admin/

## Deploy on the Raspberry Pi (OMV Compose)

1. Copy this folder to the Pi (everything except `.venv/`, `data/`, `.env`).
2. `cp .env.example .env` and fill it in — at minimum `SECRET_KEY`,
   `ALLOWED_HOSTS`, and `CSRF_TRUSTED_ORIGINS` (your tunnel hostname). Set the
   `DJANGO_SUPERUSER_*` vars to auto-create the first admin on first boot
   (remove them afterwards).
3. In `docker-compose.yml`, change the volume's left side to a folder on the
   external drive, e.g. `/srv/dev-disk-by-uuid-XXXX/gsd-lms-data:/data`.
   That folder will hold the SQLite DB **and all uploaded worksheets** — back
   it up.
4. In OMV: **Services → Compose → Files → Add**, paste/point at this compose
   file, then **Up**. The image builds on the Pi itself (arm64-native,
   `python:3.13-slim` base).
5. Point the existing Cloudflare Tunnel at `http://localhost:8087`
   (or the host's LAN IP). HTTPS terminates at Cloudflare; the app already
   trusts `X-Forwarded-Proto`.

On every start the container runs migrations and `seed_courses`
(idempotent — it never overwrites video URLs, release dates, or worksheets an
admin has changed), then serves via gunicorn + WhiteNoise.

## Environment variables

| Var | Required | What it does |
| --- | --- | --- |
| `SECRET_KEY` | **yes** | Django secret. Generate: `python -c "import secrets; print(secrets.token_urlsafe(64))"` |
| `ALLOWED_HOSTS` | **yes** | Comma-separated hostnames, e.g. `learn.getshtdonehq.com` |
| `CSRF_TRUSTED_ORIGINS` | **yes** | Comma-separated origins **with scheme**, e.g. `https://learn.getshtdonehq.com` |
| `DEBUG` | no | `true`/`false` (default `false`). Never `true` in production. |
| `TIME_ZONE` | no | Default `Asia/Manila` |
| `DATA_DIR` | no | Where DB + media live. `/data` in Docker; `./data` locally. |
| `DJANGO_SUPERUSER_USERNAME/EMAIL/PASSWORD` | no | Auto-create first admin on boot |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, `DEFAULT_FROM_EMAIL` | no | SMTP for password-reset emails. Without `EMAIL_HOST`, reset emails print to the container log. |
| `GUNICORN_WORKERS` / `GUNICORN_THREADS` | no | Defaults 2 / 3 — right-sized for the Pi 4B |
| `SUBMISSION_MAX_MB` | no | Upload size cap for worksheets (default 20) |

## Day-to-day admin (all at `/admin/`)

**Add a student — option A (invite code, recommended):**
*Invite codes → Add*, tick the course(s) the student paid for, save. Send them
the code (or the link `https://<host>/invite/?code=GSD-XXXX-XXXX`). They create
their own account and are enrolled automatically. Codes are one-time and can
carry an expiry date.

**Add a student — option B (manual):**
*Users → Add*, set username/password, then add their courses in the
*Enrollments* section on the same page. Leave "staff status" off for students.

**Review worksheets:**
*Submissions* lists every upload with filters by course and status. Open one to
download the file, write feedback, and set status — or select several and use
the *Approve*/*Reject* actions. Approval instantly unlocks the student's next
lesson; rejection lets them resubmit and shows your feedback.

**Add / edit lessons and video URLs:**
*Courses → (course) → Lessons* inline, or the *Lessons* list. Each lesson has:
`order`, title, written content (HTML), **video_url** (paste a YouTube/Vimeo
watch or embed URL — Bunny embed URLs work too), a worksheet PDF, an optional
`prerequisite` (normally the previous lesson — that's the gate), and an
optional `release_date` for drip scheduling.

**Launch a new course later (e.g. Personal Branding in 2026):**
The draft course already exists. Add its lessons (set each lesson's
prerequisite to the previous one), attach worksheets, then flip the course
*status* to **Live**. Nothing else to build.

## Project layout

```
config/            Django settings/urls/wsgi (env-driven)
core/              models, views, forms, admin, seed_courses command
templates/         branded student pages + auth pages
static/            GSD brand CSS + logo
seed/worksheets/   the 5 generated worksheet PDFs (attached on seed)
seed/generate_worksheets.py   regenerates those PDFs (dev-only, needs fpdf2)
start.py           container entrypoint (migrate → seed → gunicorn)
```

> The instructor materials (textbook / teaching mastery sheets) are **not**
> part of the app and are excluded from the Docker image via `.dockerignore`.
> Keep them out of `seed/` and `static/` — nothing in the app links to them.
