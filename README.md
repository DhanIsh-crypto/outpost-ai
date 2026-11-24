# OUTPOST AI

**AI-Powered Freelancer Outreach Platform** — built with Python Flask + SQLAlchemy (MySQL-ready), black & white LinkedIn-inspired UI, dual-role login (Freelancer + Job Provider) with two distinct dashboards.

## Modules (Freelancer / Client dashboard)

1. **Client Finder** — LinkedIn-style search by title, company size, industry, location, keywords. Save leads with auto-duplicate detection.
2. **Lead Database** — searchable, taggable (Hot / Warm / Cold / Follow Up / Client), full last-interaction history.
3. **AI Personalization** — reads lead LinkedIn + website, drafts editable cold email + LinkedIn message.
4. **Email Automation** — send, track opens / replies / bounces, fire Day-3 / Day-7 / Day-14 follow-ups.
5. **Meeting Scheduler** — booking link, Google Calendar sync, auto-move lead to "Meeting Scheduled".
6. **Analytics** — leads, emails, reply rate, positive replies, meetings, clients closed, monthly conversion, funnel.

## Modules (Job Provider dashboard)

1. **Jobs** — post, manage, close.
2. **Find Talent** — browse vetted freelancers by skill, rate, rating.
3. **Applicants** — pending / shortlisted / hired / rejected workflow.
4. **Hiring Analytics** — funnel, hire rate, by category, monthly trend.

## Run locally

```bash
cd /home/z/my-project/outpost_ai
pip install -r requirements.txt
python3 app.py
```

Visit http://localhost:5000

## Database: SQLite (default) or MySQL

The app uses SQLAlchemy ORM and works with **either** SQLite or MySQL — to switch to MySQL, set the `DATABASE_URL` environment variable:

```bash
export DATABASE_URL="mysql+pymysql://username:password@localhost:3306/outpost_ai"
export SECRET_KEY="change-this-in-production"
python3 app.py
```

Then create the database in MySQL:

```sql
CREATE DATABASE outpost_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

On first run the app auto-creates all tables and seeds demo data.

## Demo accounts

| Role          | Email             | Password   |
| ------------- | ----------------- | ---------- |
| Freelancer    | alex@outpost.ai   | password   |
| Job Provider  | jordan@outpost.ai | password   |

## Tech stack

- **Backend**: Python 3.12, Flask 3, SQLAlchemy 2, Flask-Login
- **Database**: SQLite (default) / MySQL 8 via PyMySQL
- **Frontend**: Jinja2 templates, hand-rolled B&W CSS, vanilla JS for dark mode / modals / tabs / charts
- **Theme**: pure black & white, dark mode toggle, LinkedIn-inspired layout

## Project structure

```
outpost_ai/
├── app.py              # Flask app + all routes
├── config.py           # DB URL, secret key
├── models.py           # SQLAlchemy models (User, Lead, Email, Meeting, Job, ...)
├── seed.py             # Realistic demo data
├── requirements.txt
├── README.md
├── outpost_ai.db       # SQLite (auto-created)
├── static/
│   ├── css/style.css   # Black & white theme
│   └── js/app.js       # Dark mode, tabs, modals, charts
└── templates/
    ├── base.html
    ├── landing.html    # LinkedIn-style landing
    ├── login.html      # Role-picker login
    ├── register.html
    ├── error.html
    ├── client/         # Freelancer dashboard templates
    │   ├── _sidebar.html
    │   ├── dashboard.html
    │   ├── finder.html
    │   ├── leads.html
    │   ├── lead_detail.html
    │   ├── ai.html
    │   ├── email.html
    │   ├── meetings.html
    │   └── analytics.html
    └── provider/       # Job Provider dashboard templates
        ├── _sidebar.html
        ├── dashboard.html
        ├── jobs.html
        ├── post_job.html
        ├── job_detail.html
        ├── freelancers.html
        └── analytics.html
```
