"""
OUTPOST AI - Database Models
============================
SQLAlchemy ORM models — compatible with both SQLite and MySQL.
"""
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()


# ---------------------------------------------------------------------------
# Users (both Client / freelancer and Job Provider roles)
# ---------------------------------------------------------------------------
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'client' | 'provider'
    company = db.Column(db.String(120))
    title = db.Column(db.String(120))
    avatar_color = db.Column(db.String(7), default="#000000")
    bio = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # relationships
    leads = db.relationship("Lead", backref="owner", lazy="dynamic",
                            foreign_keys="Lead.owner_id")
    jobs = db.relationship("Job", backref="employer", lazy="dynamic")

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)


# ---------------------------------------------------------------------------
# Leads (people found via Client Finder)
# ---------------------------------------------------------------------------
class Lead(db.Model):
    __tablename__ = "leads"

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    name = db.Column(db.String(150), nullable=False)
    title = db.Column(db.String(150))
    company = db.Column(db.String(150))
    company_size = db.Column(db.String(60))
    industry = db.Column(db.String(120))
    location = db.Column(db.String(150))
    website = db.Column(db.String(255))
    linkedin = db.Column(db.String(255))
    email = db.Column(db.String(150), index=True)
    phone = db.Column(db.String(40))

    tag = db.Column(db.String(40), default="Cold Lead")  # Hot/Warm/Cold/Follow Up/Client
    stage = db.Column(db.String(40), default="New")       # New/Contacted/Replied/Meeting Scheduled/Closed

    last_interaction = db.Column(db.String(255))
    last_interaction_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    emails = db.relationship("Email", backref="lead", lazy="dynamic")
    meetings = db.relationship("Meeting", backref="lead", lazy="dynamic")

    tags_history = db.relationship("LeadTag", backref="lead", lazy="dynamic")


class LeadTag(db.Model):
    __tablename__ = "lead_tags"
    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, db.ForeignKey("leads.id"), nullable=False)
    tag = db.Column(db.String(40), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ---------------------------------------------------------------------------
# Emails (sent, opens, replies, bounces, follow-ups)
# ---------------------------------------------------------------------------
class Email(db.Model):
    __tablename__ = "emails"

    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, db.ForeignKey("leads.id"), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    subject = db.Column(db.String(255))
    body = db.Column(db.Text)
    channel = db.Column(db.String(20), default="email")  # email | linkedin
    status = db.Column(db.String(20), default="sent")     # sent | opened | replied | bounced
    is_followup = db.Column(db.Boolean, default=False)
    followup_day = db.Column(db.Integer)  # 0 (original), 3, 7, 14
    is_positive = db.Column(db.Boolean, default=False)

    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    opened_at = db.Column(db.DateTime)
    replied_at = db.Column(db.DateTime)

    sender = db.relationship("User", foreign_keys=[sender_id])


# ---------------------------------------------------------------------------
# Meetings
# ---------------------------------------------------------------------------
class Meeting(db.Model):
    __tablename__ = "meetings"

    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, db.ForeignKey("leads.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    title = db.Column(db.String(200), default="Discovery Call")
    scheduled_at = db.Column(db.DateTime, nullable=False)
    duration_min = db.Column(db.Integer, default=30)
    booking_link = db.Column(db.String(255))
    google_event_id = db.Column(db.String(120))
    status = db.Column(db.String(20), default="scheduled")  # scheduled | completed | cancelled
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", foreign_keys=[user_id])


# ---------------------------------------------------------------------------
# Jobs (Job Provider side)
# ---------------------------------------------------------------------------
class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    employer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(120))   # e.g. Web Development
    budget = db.Column(db.String(60))
    duration = db.Column(db.String(60))    # e.g. "3 months"
    experience_level = db.Column(db.String(40))  # Entry / Intermediate / Expert
    description = db.Column(db.Text)
    skills_required = db.Column(db.Text)   # comma separated
    location_type = db.Column(db.String(40), default="Remote")  # Remote / Onsite / Hybrid
    status = db.Column(db.String(20), default="open")  # open / closed / draft

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    applications = db.relationship("JobApplication", backref="job", lazy="dynamic")


class JobApplication(db.Model):
    __tablename__ = "job_applications"

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    freelancer_name = db.Column(db.String(150), nullable=False)
    freelancer_email = db.Column(db.String(150))
    freelancer_title = db.Column(db.String(150))
    freelancer_skills = db.Column(db.Text)
    freelancer_rate = db.Column(db.String(60))
    proposal = db.Column(db.Text)
    rating = db.Column(db.Float, default=4.5)
    status = db.Column(db.String(20), default="pending")  # pending / shortlisted / hired / rejected
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)


# ---------------------------------------------------------------------------
# Analytics events (for the analytics dashboard)
# ---------------------------------------------------------------------------
class AnalyticsEvent(db.Model):
    __tablename__ = "analytics_events"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    event_type = db.Column(db.String(60), nullable=False)  # lead_added, email_sent, reply, meeting, closed
    value = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
