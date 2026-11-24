"""
OUTPOST AI - Main Flask Application
====================================
Black & white, LinkedIn-inspired freelancer outreach platform.

Run:
    cd /home/z/my-project/outpost_ai
    python3 app.py

Then visit: http://localhost:5000

Demo accounts (after seeding):
    Client (freelancer):    alex@outpost.ai   / password
    Job Provider:           jordan@outpost.ai / password
"""
import os
import random
from datetime import datetime, timedelta
from functools import wraps

from flask import (Flask, render_template, request, redirect, url_for,
                   flash, jsonify, g, abort)
from flask_login import (LoginManager, login_user, logout_user,
                         login_required, current_user)

from config import Config
from models import db, User, Lead, LeadTag, Email, Meeting, Job, JobApplication, AnalyticsEvent

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Please sign in to continue."

TAGS = ["Hot Lead", "Warm Lead", "Cold Lead", "Follow Up Needed", "Client"]
STAGES = ["New", "Contacted", "Replied", "Meeting Scheduled", "Closed"]


@login_manager.user_loader
def load_user(uid):
    return db.session.get(User, int(uid))


# ---------------------------------------------------------------------------
# Template helpers / context
# ---------------------------------------------------------------------------
@app.context_processor
def inject_globals():
    return dict(APP_NAME=Config.APP_NAME, APP_TAGLINE=Config.APP_TAGLINE, TAGS=TAGS, STAGES=STAGES)


def role_required(role):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*a, **kw):
            if not current_user.is_authenticated:
                return redirect(url_for("login"))
            if current_user.role != role:
                abort(403)
            return fn(*a, **kw)
        return wrapper
    return decorator


# ---------------------------------------------------------------------------
# Public routes
# ---------------------------------------------------------------------------
@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter(db.func.lower(User.email) == email).first()
        if user and user.check_password(password):
            login_user(user, remember=True)
            if user.role == "client":
                return redirect(url_for("client_dashboard"))
            return redirect(url_for("provider_dashboard"))
        flash("Invalid email or password.", "error")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "client")
        company = request.form.get("company", "").strip()
        title = request.form.get("title", "").strip()
        if User.query.filter(db.func.lower(User.email) == email).first():
            flash("An account with this email already exists.", "error")
            return redirect(url_for("register"))
        user = User(name=name, email=email, role=role, company=company, title=title)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=True)
        flash(f"Welcome to {Config.APP_NAME}, {name}!", "success")
        return redirect(url_for("client_dashboard") if role == "client" else url_for("provider_dashboard"))
    return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("landing"))


# ---------------------------------------------------------------------------
# CLIENT (Freelancer) DASHBOARD
# ---------------------------------------------------------------------------
@app.route("/client/dashboard")
@login_required
@role_required("client")
def client_dashboard():
    stats = {
        "total_leads": current_user.leads.count(),
        "hot_leads": current_user.leads.filter(Lead.tag == "Hot Lead").count(),
        "emails_sent": Email.query.filter_by(sender_id=current_user.id).count(),
        "replies": Email.query.filter_by(sender_id=current_user.id, status="replied").count(),
        "meetings": Meeting.query.filter_by(user_id=current_user.id).count(),
        "clients": current_user.leads.filter(Lead.tag == "Client").count(),
    }
    recent_leads = current_user.leads.order_by(Lead.created_at.desc()).limit(6).all()
    upcoming = Meeting.query.filter(
        Meeting.user_id == current_user.id,
        Meeting.scheduled_at >= datetime.utcnow(),
        Meeting.status == "scheduled",
    ).order_by(Meeting.scheduled_at.asc()).limit(5).all()
    return render_template("client/dashboard.html", stats=stats,
                           recent_leads=recent_leads, upcoming=upcoming)


# ---- Client Finder ---------------------------------------------------------
@app.route("/client/finder", methods=["GET", "POST"])
@login_required
@role_required("client")
def client_finder():
    results = []
    if request.method == "POST":
        results = _simulate_linkedin_search(request.form)
    return render_template("client/finder.html", results=results)


def _simulate_linkedin_search(form):
    """Simulated LinkedIn-like search with realistic results."""
    title = (form.get("title") or "").strip()
    industry = (form.get("industry") or "").strip()
    location = (form.get("location") or "").strip()
    company_size = form.get("company_size", "")
    keywords = (form.get("keywords") or "").strip()

    pool = [
        ("Sarah Mitchell", "VP Marketing", "Lumen Health", "51-200", "Healthcare", "Austin, TX",
         "lumenhealth.io", "linkedin.com/in/sarahmitchell", "sarah@lumenhealth.io"),
        ("David Chen", "Founder & CEO", "Apex Studios", "11-50", "Design Services", "San Francisco, CA",
         "apexstudios.co", "linkedin.com/in/davidchen", "david@apexstudios.co"),
        ("Priya Sharma", "Head of Growth", "Brightline SaaS", "201-500", "SaaS", "Bangalore, India",
         "brightline.io", "linkedin.com/in/priyasharma", "priya@brightline.io"),
        ("Marcus Johnson", "CTO", "Forge Robotics", "11-50", "Robotics", "Boston, MA",
         "forgerobotics.ai", "linkedin.com/in/marcusj", "marcus@forgerobotics.ai"),
        ("Elena Rossi", "Marketing Director", "Bella Foods", "201-500", "Food & Beverage", "Milan, Italy",
         "bellafoods.it", "linkedin.com/in/elenarossi", "elena@bellafoods.it"),
        ("James Park", "Product Lead", "Quanta Labs", "51-200", "AI / ML", "Seattle, WA",
         "quantalabs.com", "linkedin.com/in/jamespark", "james@quantalabs.com"),
        ("Aisha Khan", "Operations Head", "Skyline Logistics", "500-1000", "Logistics", "Dubai, UAE",
         "skylinelogistics.ae", "linkedin.com/in/aishakhan", "aisha@skylinelogistics.ae"),
        ("Tom Whitfield", "CEO", "GreenLeaf Retail", "11-50", "Retail", "London, UK",
         "greenleaf.co.uk", "linkedin.com/in/tomwhitfield", "tom@greenleaf.co.uk"),
        ("Nina Alvarez", "Brand Manager", "Sol Media", "51-200", "Media", "Madrid, Spain",
         "solmedia.es", "linkedin.com/in/ninaalvarez", "nina@solmedia.es"),
        ("Raj Patel", "Co-Founder", "DevForge", "11-50", "Software Dev", "Toronto, Canada",
         "devforge.io", "linkedin.com/in/rajpatel", "raj@devforge.io"),
        ("Olivia Brown", "CMO", "Pulse Fitness", "201-500", "Health & Wellness", "Los Angeles, CA",
         "pulsefit.com", "linkedin.com/in/oliviabrown", "olivia@pulsefit.com"),
        ("Kenji Tanaka", "VP Engineering", "Nimbus Cloud", "500-1000", "Cloud Infra", "Tokyo, Japan",
         "nimbuscloud.jp", "linkedin.com/in/kenjitanaka", "kenji@nimbuscloud.jp"),
    ]
    out = []
    for p in pool:
        if title and title.lower() not in p[1].lower():
            continue
        if industry and industry.lower() not in p[4].lower():
            continue
        if location and location.lower() not in p[5].lower():
            continue
        if company_size and company_size != p[3]:
            continue
        if keywords and keywords.lower() not in (p[1] + " " + p[2] + " " + p[4]).lower():
            continue
        out.append({
            "name": p[0], "title": p[1], "company": p[2], "company_size": p[3],
            "industry": p[4], "location": p[5], "website": p[6],
            "linkedin": p[7], "email": p[8],
        })
    return out


@app.route("/client/finder/save", methods=["POST"])
@login_required
@role_required("client")
def save_lead():
    # Duplicate detection: same email OR same linkedin under this owner
    email = request.form.get("email", "").strip().lower()
    linkedin = request.form.get("linkedin", "").strip()
    existing = current_user.leads.filter(
        db.or_(
            db.func.lower(Lead.email) == email if email else db.false(),
            Lead.linkedin == linkedin if linkedin else db.false(),
        )
    ).first()
    if existing:
        flash(f"Duplicate lead detected: {existing.name} is already in your database.", "warning")
        return redirect(url_for("client_leads"))

    lead = Lead(
        owner_id=current_user.id,
        name=request.form.get("name"),
        title=request.form.get("title"),
        company=request.form.get("company"),
        company_size=request.form.get("company_size"),
        industry=request.form.get("industry"),
        location=request.form.get("location"),
        website=request.form.get("website"),
        linkedin=linkedin,
        email=email,
        tag="Cold Lead",
        stage="New",
        last_interaction="Added via Client Finder",
        last_interaction_at=datetime.utcnow(),
    )
    db.session.add(lead)
    db.session.flush()  # Assign the new lead's ID before creating its tag record.
    db.session.add(LeadTag(lead_id=lead.id, tag="Cold Lead"))
    db.session.add(AnalyticsEvent(user_id=current_user.id, event_type="lead_added"))
    db.session.commit()
    flash(f"Saved lead: {lead.name} from {lead.company}.", "success")
    return redirect(url_for("client_leads"))


# ---- Lead Database ---------------------------------------------------------
@app.route("/client/leads")
@login_required
@role_required("client")
def client_leads():
    q = request.args.get("q", "").strip()
    tag = request.args.get("tag", "")
    stage = request.args.get("stage", "")
    sort = request.args.get("sort", "newest")

    query = current_user.leads
    if q:
        like = f"%{q}%"
        query = query.filter(db.or_(Lead.name.ilike(like), Lead.company.ilike(like),
                                    Lead.email.ilike(like), Lead.title.ilike(like)))
    if tag:
        query = query.filter(Lead.tag == tag)
    if stage:
        query = query.filter(Lead.stage == stage)
    if sort == "oldest":
        query = query.order_by(Lead.created_at.asc())
    elif sort == "company":
        query = query.order_by(Lead.company.asc())
    else:
        query = query.order_by(Lead.created_at.desc())

    leads = query.all()
    counts = {t: current_user.leads.filter(Lead.tag == t).count() for t in TAGS}
    return render_template("client/leads.html", leads=leads, q=q, tag=tag, stage=stage,
                           sort=sort, counts=counts)


@app.route("/client/leads/<int:lid>/tag", methods=["POST"])
@login_required
@role_required("client")
def update_lead_tag(lid):
    lead = current_user.leads.filter_by(id=lid).first_or_404()
    new_tag = request.form.get("tag")
    if new_tag in TAGS:
        lead.tag = new_tag
        lead.last_interaction = f"Tag changed to {new_tag}"
        lead.last_interaction_at = datetime.utcnow()
        db.session.add(LeadTag(lead_id=lead.id, tag=new_tag))
        db.session.commit()
        flash(f"Tag updated to {new_tag}.", "success")
    return redirect(url_for("client_leads"))


@app.route("/client/leads/<int:lid>/delete", methods=["POST"])
@login_required
@role_required("client")
def delete_lead(lid):
    lead = current_user.leads.filter_by(id=lid).first_or_404()
    db.session.delete(lead)
    db.session.commit()
    flash("Lead deleted.", "info")
    return redirect(url_for("client_leads"))


@app.route("/client/leads/<int:lid>")
@login_required
@role_required("client")
def lead_detail(lid):
    lead = current_user.leads.filter_by(id=lid).first_or_404()
    emails = lead.emails.order_by(Email.sent_at.desc()).all()
    meetings = lead.meetings.order_by(Meeting.scheduled_at.desc()).all()
    return render_template("client/lead_detail.html", lead=lead, emails=emails, meetings=meetings)


# ---- AI Personalization ----------------------------------------------------
@app.route("/client/ai", methods=["GET", "POST"])
@login_required
@role_required("client")
def ai_personalize():
    leads_list = current_user.leads.order_by(Lead.created_at.desc()).all()
    generated = None
    selected_lead = None
    if request.method == "POST":
        lid = request.form.get("lead_id", type=int)
        tone = request.form.get("tone", "professional")
        selected_lead = current_user.leads.filter_by(id=lid).first_or_404()
        generated = _generate_personalized_message(selected_lead, tone)
    return render_template("client/ai.html", leads=leads_list, generated=generated,
                           selected_lead=selected_lead)


def _generate_personalized_message(lead, tone):
    """Rule-based 'AI' personalization that reads lead profile + website context."""
    business = lead.industry or "your industry"
    company = lead.company or "your company"
    first = (lead.name or "there").split()[0]
    website_note = f"I had a look at {lead.website} and" if lead.website else "I"
    specific = {
        "Healthcare": "the patient-first approach you've taken is genuinely impressive",
        "SaaS": "the workflow automation in your product is ahead of most players I've seen",
        "Design Services": "the visual identity work your studio ships is consistently sharp",
        "Robotics": "the precision engineering behind your robots is remarkable",
        "Food & Beverage": "your brand storytelling around quality sourcing stands out",
        "AI / ML": "the model evaluation rigor your team shows is rare",
        "Logistics": "your real-time tracking layer solves a hard problem elegantly",
        "Retail": "your in-store experience design is thoughtful",
        "Media": "your editorial standards clearly set you apart",
        "Software Dev": "the engineering culture at your company is exactly what great teams need",
        "Health & Wellness": "your community-led growth model is working brilliantly",
        "Cloud Infra": "your uptime story is the kind of proof buyers actually trust",
    }.get(business, "your recent work shows real momentum")

    if tone == "friendly":
        opener = f"Hey {first} — hope your week's off to a great start."
        close = "Cheers,\nAlex"
    elif tone == "direct":
        opener = f"Hi {first},"
        close = "Best,\nAlex Morgan"
    else:
        opener = f"Dear {first},"
        close = "Kind regards,\nAlex Morgan"

    email_body = f"""{opener}

{website_note} wanted to share a quick thought. {specific} — and that's exactly the kind of work I help {business} companies scale.

I'm a freelance {current_user.title or 'growth specialist'} and over the last 3 years I've helped 14 {business.lower()} companies like {company} improve their outreach-to-meeting conversion by an average of 38%.

For {company}, I'd start with a 2-week sprint:
  1. Audit your current outreach flow
  2. Ship 3 personalized sequences
  3. Track opens, replies and meetings booked

Worth a 20-minute call this week? I can send a Calendly link if it's easier.

{close}"""

    linkedin_body = f"""Hi {first} — came across {company} while researching standout {business} companies and {website_note.lower()} thought your recent work was worth connecting over.

I freelance with {business} companies on outreach + pipeline. If you're open to it, I'd love to share a couple of ideas specific to {company} — no pitch, just useful.

Open to a quick chat this week?

- Alex"""

    subject = f"Idea for {company}'s outreach — 38% lift in meetings"
    return {"email_subject": subject, "email_body": email_body,
            "linkedin_body": linkedin_body, "lead": lead}


@app.route("/client/ai/send", methods=["POST"])
@login_required
@role_required("client")
def ai_send():
    lid = request.form.get("lead_id", type=int)
    lead = current_user.leads.filter_by(id=lid).first_or_404()
    channel = request.form.get("channel", "email")
    subject = request.form.get("subject", "")
    body = request.form.get("body", "")

    email = Email(
        lead_id=lead.id, sender_id=current_user.id, subject=subject, body=body,
        channel=channel, status="sent", is_followup=False, followup_day=0,
    )
    db.session.add(email)
    lead.stage = "Contacted"
    lead.last_interaction = f"Sent {channel} via AI Personalization"
    lead.last_interaction_at = datetime.utcnow()
    db.session.add(AnalyticsEvent(user_id=current_user.id, event_type="email_sent"))
    db.session.commit()
    flash(f"{channel.title()} sent to {lead.name}. Tracking enabled.", "success")
    return redirect(url_for("client_email_automation"))


# ---- Email Automation ------------------------------------------------------
@app.route("/client/email")
@login_required
@role_required("client")
def client_email_automation():
    emails = Email.query.filter_by(sender_id=current_user.id).order_by(Email.sent_at.desc()).all()
    stats = {
        "sent": Email.query.filter_by(sender_id=current_user.id).count(),
        "opened": Email.query.filter_by(sender_id=current_user.id, status="opened").count(),
        "replied": Email.query.filter_by(sender_id=current_user.id, status="replied").count(),
        "bounced": Email.query.filter_by(sender_id=current_user.id, status="bounced").count(),
        "followups": Email.query.filter_by(sender_id=current_user.id, is_followup=True).count(),
    }
    return render_template("client/email.html", emails=emails, stats=stats)


@app.route("/client/email/<int:eid>/track", methods=["POST"])
@login_required
@role_required("client")
def track_email(eid):
    """Manually mark an email as opened / replied / bounced — for demo tracking."""
    email = Email.query.filter_by(id=eid, sender_id=current_user.id).first_or_404()
    new_status = request.form.get("status")
    is_positive = request.form.get("is_positive") == "on"
    if new_status in ("opened", "replied", "bounced"):
        email.status = new_status
        if new_status == "opened":
            email.opened_at = datetime.utcnow()
        elif new_status == "replied":
            email.replied_at = datetime.utcnow()
            email.is_positive = is_positive
            lead = email.lead
            lead.stage = "Replied"
            lead.last_interaction = "Replied to email"
            lead.last_interaction_at = datetime.utcnow()
            if is_positive:
                lead.tag = "Hot Lead"
                db.session.add(LeadTag(lead_id=lead.id, tag="Hot Lead"))
                db.session.add(AnalyticsEvent(user_id=current_user.id, event_type="positive_reply"))
            db.session.add(AnalyticsEvent(user_id=current_user.id, event_type="reply"))
        db.session.commit()
        flash(f"Email marked as {new_status}.", "success")
    return redirect(url_for("client_email_automation"))


@app.route("/client/email/<int:eid>/followup", methods=["POST"])
@login_required
@role_required("client")
def send_followup(eid):
    email = Email.query.filter_by(id=eid, sender_id=current_user.id).first_or_404()
    day = request.form.get("day", type=int)
    if day not in (3, 7, 14):
        abort(400)
    followup = Email(
        lead_id=email.lead_id, sender_id=current_user.id,
        subject=f"Re: {email.subject}",
        body=f"Hi {{first_name}},\n\nJust floating this back to the top of your inbox. Happy to share a couple of ideas specific to your outreach — even if now isn't the right time.\n\nBest,\nAlex",
        channel=email.channel, status="sent", is_followup=True, followup_day=day,
    )
    db.session.add(followup)
    lead = email.lead
    lead.last_interaction = f"Follow-up sent (Day {day})"
    lead.last_interaction_at = datetime.utcnow()
    db.session.commit()
    flash(f"Day-{day} follow-up sent to {lead.name}.", "success")
    return redirect(url_for("client_email_automation"))


# ---- Meeting Scheduler -----------------------------------------------------
@app.route("/client/meetings")
@login_required
@role_required("client")
def client_meetings():
    meetings = Meeting.query.filter_by(user_id=current_user.id).order_by(Meeting.scheduled_at.desc()).all()
    return render_template("client/meetings.html", meetings=meetings)


@app.route("/client/meetings/book", methods=["POST"])
@login_required
@role_required("client")
def book_meeting():
    lid = request.form.get("lead_id", type=int)
    lead = current_user.leads.filter_by(id=lid).first_or_404()
    when_str = request.form.get("scheduled_at")
    when = datetime.strptime(when_str, "%Y-%m-%dT%H:%M") if when_str else datetime.utcnow() + timedelta(days=2)
    meeting = Meeting(
        lead_id=lead.id, user_id=current_user.id, title="Discovery Call",
        scheduled_at=when, duration_min=30,
        booking_link=f"https://calendly.com/alexmorgan/30min?lead={lead.id}",
        google_event_id=f"outpost_{lead.id}_{int(when.timestamp())}",
        status="scheduled",
    )
    db.session.add(meeting)
    lead.stage = "Meeting Scheduled"
    lead.last_interaction = "Meeting scheduled"
    lead.last_interaction_at = datetime.utcnow()
    db.session.add(AnalyticsEvent(user_id=current_user.id, event_type="meeting"))
    db.session.commit()
    flash(f"Meeting scheduled with {lead.name}. Google Calendar event created.", "success")
    return redirect(url_for("client_meetings"))


@app.route("/client/meetings/<int:mid>/close", methods=["POST"])
@login_required
@role_required("client")
def close_meeting(mid):
    meeting = Meeting.query.filter_by(id=mid, user_id=current_user.id).first_or_404()
    meeting.status = "completed"
    lead = meeting.lead
    lead.tag = "Client"
    lead.stage = "Closed"
    lead.last_interaction = "Closed as Client"
    lead.last_interaction_at = datetime.utcnow()
    db.session.add(LeadTag(lead_id=lead.id, tag="Client"))
    db.session.add(AnalyticsEvent(user_id=current_user.id, event_type="closed"))
    db.session.commit()
    flash(f"{lead.name} moved to Client. Win!", "success")
    return redirect(url_for("client_meetings"))


# ---- Analytics -------------------------------------------------------------
@app.route("/client/analytics")
@login_required
@role_required("client")
def client_analytics():
    uid = current_user.id
    leads_total = current_user.leads.count()
    emails_sent = Email.query.filter_by(sender_id=uid).count()
    opens = Email.query.filter_by(sender_id=uid, status="opened").count()
    replies = Email.query.filter_by(sender_id=uid, status="replied").count()
    positives = Email.query.filter_by(sender_id=uid, status="replied", is_positive=True).count()
    meetings = Meeting.query.filter_by(user_id=uid).count()
    clients = current_user.leads.filter(Lead.tag == "Client").count()

    reply_rate = round((replies / emails_sent * 100), 1) if emails_sent else 0
    positive_rate = round((positives / replies * 100), 1) if replies else 0
    close_rate = round((clients / leads_total * 100), 1) if leads_total else 0

    # Monthly conversion (last 6 months)
    months = []
    for i in range(5, -1, -1):
        m_start = (datetime.utcnow().replace(day=1) - timedelta(days=30 * i)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        m_end = (m_start + timedelta(days=32)).replace(day=1)
        m_leads = current_user.leads.filter(Lead.created_at >= m_start, Lead.created_at < m_end).count()
        m_clients = current_user.leads.filter(Lead.created_at >= m_start, Lead.created_at < m_end, Lead.tag == "Client").count()
        conv = round((m_clients / m_leads * 100), 1) if m_leads else 0
        months.append({"label": m_start.strftime("%b"), "leads": m_leads, "clients": m_clients, "conv": conv})

    funnel = [
        {"stage": "Leads", "value": leads_total},
        {"stage": "Contacted", "value": Email.query.filter_by(sender_id=uid).distinct(Email.lead_id).count()},
        {"stage": "Replied", "value": replies},
        {"stage": "Meetings", "value": meetings},
        {"stage": "Clients", "value": clients},
    ]

    stats = {
        "leads_total": leads_total, "emails_sent": emails_sent, "opens": opens,
        "replies": replies, "positives": positives, "meetings": meetings,
        "clients": clients, "reply_rate": reply_rate, "positive_rate": positive_rate,
        "close_rate": close_rate,
    }
    return render_template("client/analytics.html", stats=stats, months=months, funnel=funnel)


# ---------------------------------------------------------------------------
# JOB PROVIDER DASHBOARD
# ---------------------------------------------------------------------------
@app.route("/provider/dashboard")
@login_required
@role_required("provider")
def provider_dashboard():
    stats = {
        "open_jobs": current_user.jobs.filter(Job.status == "open").count(),
        "total_applicants": JobApplication.query.join(Job).filter(Job.employer_id == current_user.id).count(),
        "shortlisted": JobApplication.query.join(Job).filter(Job.employer_id == current_user.id, JobApplication.status == "shortlisted").count(),
        "hired": JobApplication.query.join(Job).filter(Job.employer_id == current_user.id, JobApplication.status == "hired").count(),
    }
    recent_jobs = current_user.jobs.order_by(Job.created_at.desc()).limit(5).all()
    recent_apps = (JobApplication.query.join(Job)
                   .filter(Job.employer_id == current_user.id)
                   .order_by(JobApplication.applied_at.desc()).limit(6).all())
    return render_template("provider/dashboard.html", stats=stats,
                           recent_jobs=recent_jobs, recent_apps=recent_apps)


@app.route("/provider/jobs")
@login_required
@role_required("provider")
def provider_jobs():
    jobs = current_user.jobs.order_by(Job.created_at.desc()).all()
    return render_template("provider/jobs.html", jobs=jobs)


@app.route("/provider/jobs/new", methods=["GET", "POST"])
@login_required
@role_required("provider")
def post_job():
    if request.method == "POST":
        job = Job(
            employer_id=current_user.id,
            title=request.form.get("title"),
            category=request.form.get("category"),
            budget=request.form.get("budget"),
            duration=request.form.get("duration"),
            experience_level=request.form.get("experience_level"),
            description=request.form.get("description"),
            skills_required=request.form.get("skills_required"),
            location_type=request.form.get("location_type", "Remote"),
            status="open",
        )
        db.session.add(job)
        db.session.commit()
        flash(f"Job posted: {job.title}", "success")
        return redirect(url_for("provider_jobs"))
    return render_template("provider/post_job.html")


@app.route("/provider/jobs/<int:jid>/close", methods=["POST"])
@login_required
@role_required("provider")
def close_job(jid):
    job = current_user.jobs.filter_by(id=jid).first_or_404()
    job.status = "closed"
    db.session.commit()
    flash("Job closed.", "info")
    return redirect(url_for("provider_jobs"))


@app.route("/provider/jobs/<int:jid>")
@login_required
@role_required("provider")
def job_detail(jid):
    job = current_user.jobs.filter_by(id=jid).first_or_404()
    applications = job.applications.order_by(JobApplication.applied_at.desc()).all()
    return render_template("provider/job_detail.html", job=job, applications=applications)


@app.route("/provider/applications/<int:aid>/status", methods=["POST"])
@login_required
@role_required("provider")
def update_application(aid):
    app_row = (JobApplication.query.join(Job)
               .filter(JobApplication.id == aid, Job.employer_id == current_user.id).first_or_404())
    new_status = request.form.get("status")
    if new_status in ("pending", "shortlisted", "hired", "rejected"):
        app_row.status = new_status
        db.session.commit()
        flash(f"Applicant marked as {new_status}.", "success")
    return redirect(url_for("job_detail", jid=app_row.job_id))


@app.route("/provider/freelancers")
@login_required
@role_required("provider")
def find_freelancers():
    freelancers = _freelancer_pool()
    q = request.args.get("q", "").strip().lower()
    cat = request.args.get("category", "").strip()
    if q:
        freelancers = [f for f in freelancers if q in (f["name"] + f["title"] + f["skills"]).lower()]
    if cat:
        freelancers = [f for f in freelancers if cat.lower() in f["category"].lower()]
    return render_template("provider/freelancers.html", freelancers=freelancers, q=q, cat=cat)


def _freelancer_pool():
    return [
        {"id": 1, "name": "Maya Roberts", "title": "Full-Stack Developer", "category": "Web Development",
         "skills": "React, Node.js, PostgreSQL", "rate": "$75/hr", "rating": 4.9, "projects": 47,
         "location": "Remote, USA"},
        {"id": 2, "name": "Lucas Meyer", "title": "UI/UX Designer", "category": "Design",
         "skills": "Figma, Webflow, Branding", "rate": "$60/hr", "rating": 4.8, "projects": 32,
         "location": "Berlin, Germany"},
        {"id": 3, "name": "Sophie Laurent", "title": "Brand Strategist", "category": "Marketing",
         "skills": "Brand, Content, SEO", "rate": "$80/hr", "rating": 5.0, "projects": 28,
         "location": "Paris, France"},
        {"id": 4, "name": "Diego Fernandez", "title": "Mobile Developer", "category": "Mobile Development",
         "skills": "Flutter, Swift, Kotlin", "rate": "$70/hr", "rating": 4.7, "projects": 41,
         "location": "Mexico City, Mexico"},
        {"id": 5, "name": "Hannah Kim", "title": "Data Scientist", "category": "Data & AI",
         "skills": "Python, ML, TensorFlow", "rate": "$95/hr", "rating": 4.9, "projects": 22,
         "location": "Seoul, South Korea"},
        {"id": 6, "name": "Aaron Wright", "title": "DevOps Engineer", "category": "DevOps & Cloud",
         "skills": "AWS, Docker, Kubernetes", "rate": "$85/hr", "rating": 4.8, "projects": 35,
         "location": "Remote, Canada"},
        {"id": 7, "name": "Fatima Al-Sayed", "title": "Content Writer", "category": "Writing",
         "skills": "Copywriting, Blogs, Tech", "rate": "$45/hr", "rating": 4.7, "projects": 58,
         "location": "Cairo, Egypt"},
        {"id": 8, "name": "Noah Bennett", "title": "Video Editor", "category": "Video & Animation",
         "skills": "Premiere, After Effects", "rate": "$55/hr", "rating": 4.6, "projects": 39,
         "location": "Remote, UK"},
    ]


@app.route("/provider/analytics")
@login_required
@role_required("provider")
def provider_analytics():
    uid = current_user.id
    jobs_total = current_user.jobs.count()
    open_jobs = current_user.jobs.filter(Job.status == "open").count()
    total_apps = JobApplication.query.join(Job).filter(Job.employer_id == uid).count()
    shortlisted = JobApplication.query.join(Job).filter(Job.employer_id == uid, JobApplication.status == "shortlisted").count()
    hired = JobApplication.query.join(Job).filter(Job.employer_id == uid, JobApplication.status == "hired").count()
    hire_rate = round((hired / total_apps * 100), 1) if total_apps else 0

    by_category = {}
    for j in current_user.jobs.all():
        c = j.category or "Other"
        by_category[c] = by_category.get(c, 0) + j.applications.count()

    months = []
    for i in range(5, -1, -1):
        m_start = (datetime.utcnow().replace(day=1) - timedelta(days=30 * i)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        m_end = (m_start + timedelta(days=32)).replace(day=1)
        m_jobs = current_user.jobs.filter(Job.created_at >= m_start, Job.created_at < m_end).count()
        m_apps = JobApplication.query.join(Job).filter(Job.employer_id == uid, JobApplication.applied_at >= m_start, JobApplication.applied_at < m_end).count()
        months.append({"label": m_start.strftime("%b"), "jobs": m_jobs, "apps": m_apps})

    stats = {"jobs_total": jobs_total, "open_jobs": open_jobs, "total_apps": total_apps,
             "shortlisted": shortlisted, "hired": hired, "hire_rate": hire_rate}
    return render_template("provider/analytics.html", stats=stats, months=months,
                           by_category=by_category)


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------
@app.errorhandler(403)
def forbidden(e):
    return render_template("error.html", code=403,
                           message="You don't have access to this page."), 403


@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404,
                           message="The page you're looking for doesn't exist."), 404


# ---------------------------------------------------------------------------
# CLI: init + seed
# ---------------------------------------------------------------------------
@app.cli.command("init-db")
def init_db():
    # Safe to run repeatedly: creates missing tables without deleting records.
    db.create_all()
    print("[OK] Missing database tables created; existing records preserved.")


@app.cli.command("seed")
def seed():
    from seed import run_seed
    inserted = run_seed(db, app)
    if inserted:
        print("[OK] Database seeded with demo data.")
    else:
        print("[OK] Existing database preserved; no demo rows inserted.")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # Auto-seed if empty
        if User.query.count() == 0:
            from seed import run_seed
            run_seed(db, app)
            print("[OK] Auto-seeded demo data.")
    app.run(host="0.0.0.0", port=5000, debug=True)
