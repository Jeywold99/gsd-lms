"""
Container entrypoint: migrate, seed the courses, optionally create the first
admin from env vars, then hand off to gunicorn.
"""
import os
import subprocess
import sys


def run(*args, check=True):
    print("+", " ".join(args), flush=True)
    return subprocess.run([sys.executable, "manage.py", *args], check=check)


def main():
    run("migrate", "--noinput")
    run("seed_courses")
    if os.environ.get("DJANGO_SUPERUSER_USERNAME"):
        # Requires DJANGO_SUPERUSER_PASSWORD (and optionally _EMAIL) in env.
        # Exits non-zero if the user already exists, which is fine.
        run("createsuperuser", "--noinput", check=False)

    workers = os.environ.get("GUNICORN_WORKERS", "2")
    threads = os.environ.get("GUNICORN_THREADS", "3")
    os.execvp(
        "gunicorn",
        [
            "gunicorn",
            "config.wsgi:application",
            "--bind", "0.0.0.0:8000",
            "--workers", workers,
            "--threads", threads,
            "--timeout", "90",
            "--access-logfile", "-",
        ],
    )


if __name__ == "__main__":
    main()
