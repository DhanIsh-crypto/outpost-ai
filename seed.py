"""
OUTPOST AI - Database seed
===========================
Populates realistic demo data: 2 users (client + provider),
leads, emails, meetings, jobs, applications, analytics events.
"""
from datetime import datetime, timedelta
import random

from models import (db, User, Lead, LeadTag, Email, Meeting, Job, JobApplication,
                    AnalyticsEvent)


def run_seed(db, app):
    with app.app_context():
        # Never erase an existing database. Demo data is inserted only into an
        # empty database, making this command safe to run during restarts.
        db.create_all()
        if User.query.first():
            print("[INFO] Existing users found; demo seeding skipped.")
            return False

        # --- Users --------------------------------------------------------
        client = User(
            name="Alex Morgan", email="alex@outpost.ai", role="client",
            title="Freelance Growth Specialist", company="Independent",
            bio="Helping SaaS & services companies 10x their outreach pipeline.",
        )
        client.set_password("password")
        provider = User(
            name="Jordan Reyes", email="jordan@outpost.ai", role="provider",
            title="Talent Acquisition Lead", company="Nimbus Labs",
            bio="Hiring freelancers for product, design and engineering work.",
        )
        provider.set_password("password")
        db.session.add_all([client, provider])
        db.session.flush()

        # --- Leads (for the client) --------------------------------------
        leads_data = [
            ("Sarah Mitchell", "VP Marketing", "Lumen Health", "51-200", "Healthcare",
             "Austin, TX", "lumenhealth.io", "linkedin.com/in/sarahmitchell",
             "sarah@lumenhealth.io", "Hot Lead", "Replied",
             "Replied positively — wants a call", datetime.utcnow() - timedelta(days=2)),
            ("David Chen", "Founder & CEO", "Apex Studios", "11-50", "Design Services",
             "San Francisco, CA", "apexstudios.co", "linkedin.com/in/davidchen",
             "david@apexstudios.co", "Warm Lead", "Contacted",
             "Cold email sent", datetime.utcnow() - timedelta(days=5)),
            ("Priya Sharma", "Head of Growth", "Brightline SaaS", "201-500", "SaaS",
             "Bangalore, India", "brightline.io", "linkedin.com/in/priyasharma",
             "priya@brightline.io", "Client", "Closed",
             "Closed! Signed retainer", datetime.utcnow() - timedelta(days=45)),
            ("Marcus Johnson", "CTO", "Forge Robotics", "11-50", "Robotics",
             "Boston, MA", "forgerobotics.ai", "linkedin.com/in/marcusj",
             "marcus@forgerobotics.ai", "Follow Up Needed", "Contacted",
             "Day 7 follow-up sent", datetime.utcnow() - timedelta(days=12)),
            ("Elena Rossi", "Marketing Director", "Bella Foods", "201-500", "Food & Beverage",
             "Milan, Italy", "bellafoods.it", "linkedin.com/in/elenarossi",
             "elena@bellafoods.it", "Hot Lead", "Meeting Scheduled",
             "Meeting booked for Thursday", datetime.utcnow() - timedelta(days=3)),
            ("James Park", "Product Lead", "Quanta Labs", "51-200", "AI / ML",
             "Seattle, WA", "quantalabs.com", "linkedin.com/in/jamespark",
             "james@quantalabs.com", "Cold Lead", "New",
             "Added via Client Finder", datetime.utcnow() - timedelta(hours=6)),
            ("Aisha Khan", "Operations Head", "Skyline Logistics", "500-1000", "Logistics",
             "Dubai, UAE", "skylinelogistics.ae", "linkedin.com/in/aishakhan",
             "aisha@skylinelogistics.ae", "Warm Lead", "Contacted",
             "Day 3 follow-up sent", datetime.utcnow() - timedelta(days=8)),
            ("Tom Whitfield", "CEO", "GreenLeaf Retail", "11-50", "Retail",
             "London, UK", "greenleaf.co.uk", "linkedin.com/in/tomwhitfield",
             "tom@greenleaf.co.uk", "Cold Lead", "New",
             "Added via Client Finder", datetime.utcnow() - timedelta(days=1)),
            ("Nina Alvarez", "Brand Manager", "Sol Media", "51-200", "Media",
             "Madrid, Spain", "solmedia.es", "linkedin.com/in/ninaalvarez",
             "nina@solmedia.es", "Cold Lead", "Contacted",
             "Email bounced", datetime.utcnow() - timedelta(days=15)),
            ("Raj Patel", "Co-Founder", "DevForge", "11-50", "Software Dev",
             "Toronto, Canada", "devforge.io", "linkedin.com/in/rajpatel",
             "raj@devforge.io", "Warm Lead", "Replied",
             "Asked for proposal", datetime.utcnow() - timedelta(days=4)),
            ("Olivia Brown", "CMO", "Pulse Fitness", "201-500", "Health & Wellness",
             "Los Angeles, CA", "pulsefit.com", "linkedin.com/in/oliviabrown",
             "olivia@pulsefit.com", "Cold Lead", "New",
             "Added via Client Finder", datetime.utcnow() - timedelta(days=20)),
            ("Kenji Tanaka", "VP Engineering", "Nimbus Cloud", "500-1000", "Cloud Infra",
             "Tokyo, Japan", "nimbuscloud.jp", "linkedin.com/in/kenjitanaka",
             "kenji@nimbuscloud.jp", "Hot Lead", "Meeting Scheduled",
             "Demo scheduled", datetime.utcnow() - timedelta(days=7)),
        ]
        leads = []
        for d in leads_data:
            lead = Lead(
                owner_id=client.id, name=d[0], title=d[1], company=d[2],
                company_size=d[3], industry=d[4], location=d[5], website=d[6],
                linkedin=d[7], email=d[8], tag=d[9], stage=d[10],
                last_interaction=d[11], last_interaction_at=d[12],
                created_at=d[12],
            )
            db.session.add(lead)
            leads.append(lead)
        db.session.flush()

        for lead in leads:
            db.session.add(LeadTag(lead_id=lead.id, tag=lead.tag))

        # --- Emails -------------------------------------------------------
        email_templates = [
            (leads[0], "Idea for Lumen Health's outreach — 38% lift in meetings",
             "Hi Sarah,\n\nI had a look at lumenhealth.io and the patient-first approach you've taken is genuinely impressive...",
             "email", "replied", True, False, 0, datetime.utcnow() - timedelta(days=4)),
            (leads[0], "Re: Idea for Lumen Health's outreach",
             "Following up — happy to share a couple of ideas...",
             "email", "opened", False, True, 3, datetime.utcnow() - timedelta(days=1)),
            (leads[1], "Helping Apex Studios scale outreach",
             "Hi David,\n\nCame across Apex Studios and the visual identity work your studio ships...",
             "email", "sent", False, False, 0, datetime.utcnow() - timedelta(days=5)),
            (leads[2], "Quick idea for Brightline SaaS",
             "Hi Priya,\n\nThe workflow automation in your product is ahead of most players I've seen...",
             "email", "replied", True, False, 0, datetime.utcnow() - timedelta(days=50)),
            (leads[3], "Forge Robotics — outreach idea",
             "Hi Marcus,\n\nThe precision engineering behind your robots is remarkable...",
             "email", "opened", False, False, 0, datetime.utcnow() - timedelta(days=14)),
            (leads[3], "Re: Forge Robotics — outreach idea",
             "Following up on my earlier note...",
             "email", "sent", False, True, 7, datetime.utcnow() - timedelta(days=7)),
            (leads[4], "Bella Foods — outreach collaboration",
             "Hi Elena,\n\nYour brand storytelling around quality sourcing stands out...",
             "email", "replied", True, False, 0, datetime.utcnow() - timedelta(days=6)),
            (leads[6], "Skyline Logistics — quick idea",
             "Hi Aisha,\n\nYour real-time tracking layer solves a hard problem elegantly...",
             "email", "opened", False, False, 0, datetime.utcnow() - timedelta(days=11)),
            (leads[6], "Re: Skyline Logistics — quick idea",
             "Floating this back up...",
             "email", "sent", False, True, 3, datetime.utcnow() - timedelta(days=8)),
            (leads[8], "Sol Media — outreach proposal",
             "Hi Nina,\n\nYour editorial standards clearly set you apart...",
             "email", "bounced", False, False, 0, datetime.utcnow() - timedelta(days=15)),
            (leads[9], "DevForge — outreach idea",
             "Hi Raj,\n\nThe engineering culture at your company is exactly what great teams need...",
             "email", "replied", False, False, 0, datetime.utcnow() - timedelta(days=5)),
            (leads[11], "Nimbus Cloud — outreach collaboration",
             "Hi Kenji,\n\nYour uptime story is the kind of proof buyers actually trust...",
             "email", "replied", True, False, 0, datetime.utcnow() - timedelta(days=9)),
        ]
        for tpl in email_templates:
            lead, subj, body, ch, st, pos, fu, day, sent = tpl
            e = Email(
                lead_id=lead.id, sender_id=client.id, subject=subj, body=body,
                channel=ch, status=st, is_positive=pos, is_followup=fu,
                followup_day=day, sent_at=sent,
                opened_at=sent + timedelta(hours=2) if st in ("opened", "replied") else None,
                replied_at=sent + timedelta(hours=6) if st == "replied" else None,
            )
            db.session.add(e)

        # --- Meetings -----------------------------------------------------
        meetings_data = [
            (leads[0], datetime.utcnow() + timedelta(days=1, hours=2), "scheduled", "Discovery call"),
            (leads[4], datetime.utcnow() + timedelta(days=2), "scheduled", "Brand strategy call"),
            (leads[11], datetime.utcnow() + timedelta(days=3, hours=4), "scheduled", "Demo + scoping"),
            (leads[2], datetime.utcnow() - timedelta(days=30), "completed", "Closed as client"),
            (leads[9], datetime.utcnow() + timedelta(days=4), "scheduled", "Proposal walkthrough"),
        ]
        for lead, when, status, title in meetings_data:
            m = Meeting(
                lead_id=lead.id, user_id=client.id, title=title, scheduled_at=when,
                duration_min=30, booking_link=f"https://calendly.com/alexmorgan/30min?lead={lead.id}",
                google_event_id=f"outpost_{lead.id}_{int(when.timestamp())}",
                status=status,
            )
            db.session.add(m)

        # --- Analytics events --------------------------------------------
        for _ in range(12):
            db.session.add(AnalyticsEvent(user_id=client.id, event_type="lead_added",
                                          created_at=datetime.utcnow() - timedelta(days=random.randint(0, 60))))
        for _ in range(8):
            db.session.add(AnalyticsEvent(user_id=client.id, event_type="email_sent",
                                          created_at=datetime.utcnow() - timedelta(days=random.randint(0, 60))))
        for _ in range(4):
            db.session.add(AnalyticsEvent(user_id=client.id, event_type="reply",
                                          created_at=datetime.utcnow() - timedelta(days=random.randint(0, 60))))
        for _ in range(3):
            db.session.add(AnalyticsEvent(user_id=client.id, event_type="positive_reply",
                                          created_at=datetime.utcnow() - timedelta(days=random.randint(0, 60))))
        for _ in range(5):
            db.session.add(AnalyticsEvent(user_id=client.id, event_type="meeting",
                                          created_at=datetime.utcnow() - timedelta(days=random.randint(0, 60))))
        for _ in range(1):
            db.session.add(AnalyticsEvent(user_id=client.id, event_type="closed",
                                          created_at=datetime.utcnow() - timedelta(days=30)))

        # --- Jobs (provider side) ---------------------------------------
        jobs_data = [
            ("Senior React Engineer", "Web Development", "$8,000", "3 months", "Expert",
             "Build a customer-facing dashboard with React, TypeScript and Chart.js. Must integrate with our REST API.",
             "React, TypeScript, REST API", "Remote"),
            ("Brand Identity Designer", "Design", "$3,500", "1 month", "Intermediate",
             "Design complete brand identity: logo, color system, typography, brand guidelines PDF.",
             "Figma, Illustrator, Branding", "Remote"),
            ("Technical Content Writer", "Writing", "$50/hr", "Ongoing", "Intermediate",
             "Write long-form technical blog posts on cloud infrastructure topics. 2 posts/week.",
             "Technical Writing, SEO, Markdown", "Remote"),
            ("Flutter Mobile App Dev", "Mobile Development", "$12,000", "4 months", "Expert",
             "Build cross-platform mobile app for our logistics platform. iOS + Android.",
             "Flutter, Dart, Firebase", "Remote"),
            ("ML Pipeline Engineer", "Data & AI", "$15,000", "6 weeks", "Expert",
             "Set up MLOps pipeline for our recommendation model. TensorFlow + Kubernetes.",
             "Python, TensorFlow, Kubernetes, GCP", "Remote"),
        ]
        jobs = []
        for d in jobs_data:
            job = Job(
                employer_id=provider.id, title=d[0], category=d[1], budget=d[2],
                duration=d[3], experience_level=d[4], description=d[5],
                skills_required=d[6], location_type=d[7], status="open",
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 40)),
            )
            db.session.add(job)
            jobs.append(job)
        db.session.flush()

        # --- Job Applications -------------------------------------------
        applicants_data = [
            ("Maya Roberts", "maya@email.com", "Full-Stack Developer", "React, TypeScript", "$75/hr", 4.9,
             "I've built 3 dashboards similar to what you're describing, including one for a SaaS company that scaled to 50k users."),
            ("Lucas Meyer", "lucas@email.com", "UI/UX Designer", "Figma, Webflow", "$60/hr", 4.8,
             "Brand identity is my specialty — I've shipped 12 brand systems in the last year."),
            ("Hannah Kim", "hannah@email.com", "Data Scientist", "Python, TensorFlow", "$95/hr", 4.9,
             "I've built MLOps pipelines at two prior companies. Happy to share case studies."),
            ("Aaron Wright", "aaron@email.com", "DevOps Engineer", "AWS, K8s", "$85/hr", 4.8,
             "Kubernetes is my home turf. I can set this up end-to-end in 3 weeks."),
            ("Diego Fernandez", "diego@email.com", "Mobile Developer", "Flutter, Swift", "$70/hr", 4.7,
             "I've shipped 6 Flutter apps to production. Logistics is a domain I know well."),
            ("Fatima Al-Sayed", "fatima@email.com", "Content Writer", "Copywriting", "$45/hr", 4.7,
             "I write for two top-10 cloud infra blogs. Samples on request."),
            ("Sophie Laurent", "sophie@email.com", "Brand Strategist", "Brand, SEO", "$80/hr", 5.0,
             "I've led brand strategy for 4 YC companies. Would love to work with Nimbus Labs."),
            ("Noah Bennett", "noah@email.com", "Video Editor", "Premiere", "$55/hr", 4.6,
             "I've edited 200+ brand videos. Fast turnaround, story-first approach."),
        ]
        statuses = ["pending", "shortlisted", "pending", "shortlisted", "hired", "pending", "rejected", "pending"]
        for i, job in enumerate(jobs):
            # 2-3 applicants per job
            n_applicants = random.randint(2, 3)
            chosen = random.sample(applicants_data, n_applicants)
            chosen_statuses = random.sample(statuses, n_applicants) if n_applicants <= len(statuses) else statuses[:n_applicants]
            for a_data, a_status in zip(chosen, chosen_statuses):
                app_row = JobApplication(
                    job_id=job.id,
                    freelancer_name=a_data[0], freelancer_email=a_data[1],
                    freelancer_title=a_data[2], freelancer_skills=a_data[3],
                    freelancer_rate=a_data[4], rating=a_data[5], proposal=a_data[6],
                    status=a_status,
                    applied_at=datetime.utcnow() - timedelta(days=random.randint(0, 20)),
                )
                db.session.add(app_row)

        db.session.commit()
        print(f"[SEED] Created {User.query.count()} users, {Lead.query.count()} leads, "
              f"{Email.query.count()} emails, {Meeting.query.count()} meetings, "
              f"{Job.query.count()} jobs, {JobApplication.query.count()} applications.")
        return True
