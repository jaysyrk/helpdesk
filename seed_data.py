"""
seed_data.py — Populate HelpDesk Pro with a full year of realistic business data.
Run once: python seed_data.py
"""
import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

# Bootstrap the app
from app import create_app, db
from app.models import User, Ticket, Comment, Asset

app = create_app()

# ── Helpers ──────────────────────────────────────────────────────────────────

def rand_date(start: datetime, end: datetime) -> datetime:
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))


def business_date(start: datetime, end: datetime) -> datetime:
    """Random datetime skewed toward business hours Mon-Fri."""
    for _ in range(20):
        dt = rand_date(start, end)
        if dt.weekday() < 5 and 7 <= dt.hour <= 18:
            return dt
    return rand_date(start, end)


# ── Seed data definitions ────────────────────────────────────────────────────

DEPARTMENTS = ['IT', 'Finance', 'HR', 'Marketing', 'Operations', 'Sales', 'Legal', 'Engineering']

STAFF = [
    ('jsmith',    'John Smith',    'Finance'),
    ('amartinez', 'Ana Martinez',  'HR'),
    ('bwilliams', 'Bob Williams',  'Marketing'),
    ('cjohnson',  'Carol Johnson', 'Operations'),
    ('dlee',      'David Lee',     'Sales'),
    ('efoster',   'Emma Foster',   'Legal'),
    ('fgarcia',   'Frank Garcia',  'Engineering'),
    ('gthompson', 'Grace Thompson','Finance'),
    ('hpatel',    'Hina Patel',    'HR'),
    ('iwang',     'Ivan Wang',     'Marketing'),
    ('jkelly',    'James Kelly',   'Operations'),
    ('kchen',     'Karen Chen',    'Engineering'),
]

ADMINS = [
    ('sysadmin',  'sysadmin@helpdesk.local',  'IT'),
    ('helpdesk1', 'helpdesk1@helpdesk.local', 'IT'),
]

TICKET_TEMPLATES = [
    # (title_template, description_template, category, priority_weights)
    ("Laptop won't turn on",
     "My laptop is completely unresponsive. Pressing the power button does nothing. "
     "The charging light was on last night but now nothing. I have a deadline today.",
     "Hardware", [5, 30, 40, 25]),

    ("Outlook keeps crashing on startup",
     "Every time I open Outlook it crashes within 30 seconds with an error message "
     "about a corrupted PST file. Tried restarting, same issue.",
     "Software", [20, 50, 25, 5]),

    ("Cannot connect to VPN from home",
     "Getting 'Authentication failed' when trying to connect to the company VPN. "
     "This started after the weekend — I haven't changed anything on my end.",
     "Network", [10, 35, 40, 15]),

    ("Need access to shared drive Q:",
     "I've joined the Finance team and still don't have access to the Q: drive. "
     "My manager {manager} has already approved this.",
     "Account / Access", [40, 45, 10, 5]),

    ("Printer on 3rd floor not working",
     "The HP LaserJet on the 3rd floor is showing 'Paper Jam' but there is no paper "
     "visible inside. Multiple people are affected.",
     "Hardware", [15, 45, 30, 10]),

    ("Suspicious phishing email received",
     "I received an email claiming to be from IT asking for my login credentials. "
     "I did NOT click any links. Forwarding the email for investigation.",
     "Security", [5, 15, 35, 45]),

    ("Software license expired — Adobe CC",
     "Adobe Creative Cloud is showing a 'License expired' popup and won't open. "
     "I need it for the client presentation tomorrow.",
     "Software", [10, 30, 40, 20]),

    ("Slow WiFi in conference room B",
     "WiFi speeds in Conference Room B are extremely slow (tested at 1 Mbps). "
     "Other rooms seem fine. We have a video call in 2 hours.",
     "Network", [20, 45, 25, 10]),

    ("New employee laptop setup request",
     "We have a new hire starting Monday: {name}. Please set up a laptop with "
     "standard software package, email account, and VPN access.",
     "Software", [30, 50, 15, 5]),

    ("Password reset — locked out of account",
     "I've been locked out of my Windows account after too many failed attempts. "
     "I'm on-site and need access urgently.",
     "Account / Access", [5, 20, 50, 25]),

    ("Ransomware alert on workstation",
     "Windows Defender flagged a ransomware attempt on my machine. I immediately "
     "disconnected from the network. Please advise on next steps.",
     "Security", [2, 5, 18, 75]),

    ("Monitor flickering / display issues",
     "My second monitor has been flickering on and off all morning. Tried reseating "
     "the cable and rebooting — still flickering.",
     "Hardware", [25, 50, 20, 5]),

    ("Request for new software — Figma",
     "Our design team would like Figma Professional licences for 4 users. "
     "Budget approval ref: BUD-2024-0441.",
     "Software", [50, 40, 8, 2]),

    ("Network switch down — Floor 2",
     "Multiple users on Floor 2 have lost network connectivity simultaneously. "
     "Likely a switch issue.",
     "Network", [2, 8, 30, 60]),

    ("Two-factor auth not working",
     "The authenticator app on my phone was reset and I can no longer generate "
     "2FA codes for my work account. Need to re-enroll.",
     "Account / Access", [15, 45, 30, 10]),

    ("Excel crashing when opening large files",
     "Excel crashes every time I open our quarterly report file (approx 80MB). "
     "Other Excel files work fine.",
     "Software", [25, 50, 20, 5]),

    ("Keyboard/mouse not responding after Windows update",
     "After last night's Windows update my USB keyboard and mouse stopped working. "
     "Tried a different USB port, same issue.",
     "Hardware", [10, 35, 40, 15]),

    ("Request admin rights on local machine",
     "I need temporary local admin rights to install approved software for the "
     "project deliverable due Friday. Manager approval attached.",
     "Account / Access", [30, 50, 15, 5]),

    ("Website internal portal returning 500 error",
     "The internal HR portal at hr.company.local is returning a 500 Internal Server "
     "Error for all users since approximately 9 AM.",
     "Software", [5, 15, 40, 40]),

    ("Backup failure alert — File server",
     "The automated backup job for FS01 failed overnight with error code 0x8007045D. "
     "This is the third consecutive failure.",
     "Hardware", [3, 12, 45, 40]),
]

COMMENTS_POOL = [
    "Looking into this now, will update you shortly.",
    "Can you provide your asset tag number so I can look up your machine?",
    "I've remotely connected to your workstation — investigating the issue.",
    "This has been escalated to the senior engineer.",
    "Issue confirmed. A fix is being deployed — please restart your machine.",
    "Can you try clearing your browser cache and attempting again?",
    "I've reset your credentials. Please check your email for the temporary password.",
    "The issue was caused by a misconfigured Group Policy. Fixed now.",
    "Replaced the network cable — please confirm if this resolves the problem.",
    "Updated the driver to the latest version. Please test and confirm.",
    "This appears to be a known issue with the latest Windows update. Workaround applied.",
    "Licence has been re-activated. Adobe CC should now open normally.",
    "VPN profile updated — please reconnect using the new configuration.",
    "Thanks for the update, I'll follow up tomorrow if the issue persists.",
    "Switch rebooted successfully. All Floor 2 users should have connectivity restored.",
    "Phishing email quarantined and reported to the security team for analysis.",
    "New employee account created. Laptop will be ready by 9 AM Monday.",
    "Shared drive permissions updated. Please sign out and sign back in.",
    "Backup job re-scheduled and completed successfully at 3 AM.",
    "Confirmed resolved on my end — closing this ticket. Thank you!",
]

ASSET_TEMPLATES = [
    ("Laptop",    "Dell",    ["Latitude 5530", "Latitude 7430", "XPS 15"]),
    ("Laptop",    "Apple",   ["MacBook Pro 14\"", "MacBook Air M2"]),
    ("Laptop",    "Lenovo",  ["ThinkPad X1 Carbon", "ThinkPad T14"]),
    ("Desktop",   "Dell",    ["OptiPlex 7090", "OptiPlex 5090"]),
    ("Desktop",   "HP",      ["EliteDesk 800 G9", "ProDesk 600 G6"]),
    ("Server",    "Dell",    ["PowerEdge R740", "PowerEdge R640"]),
    ("Server",    "HP",      ["ProLiant DL380 Gen10", "ProLiant DL360 Gen10"]),
    ("Network",   "Cisco",   ["Catalyst 9300", "Meraki MX68", "Meraki MS225"]),
    ("Network",   "Ubiquiti",["UniFi AP Pro", "EdgeSwitch 24"]),
    ("Peripheral","Logitech",["MX Keys Keyboard", "MX Master 3 Mouse", "Webcam C920"]),
    ("Peripheral","Dell",    ["27\" 4K Monitor U2723D", "24\" Monitor P2422H"]),
    ("Peripheral","HP",      ["LaserJet Pro M404dn", "Color LaserJet M455dn"]),
]

LOCATIONS = [
    "Floor 1 - Open Plan", "Floor 2 - Open Plan", "Floor 3 - Open Plan",
    "Floor 1 - IT Room", "Server Room A", "Server Room B",
    "Conference Room A", "Conference Room B", "Reception",
    "Executive Suite", "Finance Pod", "Marketing Pod",
]

ASSET_STATUSES = ['Active', 'Active', 'Active', 'Active', 'Inactive', 'In Repair', 'Retired']


# ── Main seeder ──────────────────────────────────────────────────────────────

def seed():
    START = datetime(2025, 1, 1, 8, 0, 0)
    END   = datetime(2025, 12, 31, 18, 0, 0)

    print("Clearing existing data (except admin)...")
    Comment.query.delete()
    Ticket.query.delete()
    Asset.query.delete()
    User.query.filter(User.username != 'admin').delete()
    db.session.commit()

    # ── Users ────────────────────────────────────────────────────────────────
    print("Creating users...")
    admin_users = []
    for uname, email, dept in ADMINS:
        u = User(
            username=uname,
            email=email,
            password_hash=generate_password_hash('helpdesk123'),
            role='admin',
            department=dept,
        )
        db.session.add(u)
        admin_users.append(u)

    regular_users = []
    for uname, fullname, dept in STAFF:
        email = f"{uname}@company.local"
        u = User(
            username=uname,
            email=email,
            password_hash=generate_password_hash('password123'),
            role='user',
            department=dept,
        )
        db.session.add(u)
        regular_users.append(u)

    db.session.flush()
    all_users = regular_users + admin_users
    print(f"  Created {len(all_users)} users")

    # ── Assets ───────────────────────────────────────────────────────────────
    print("Creating assets...")
    asset_count = 0
    for asset_type, manufacturer, models in ASSET_TEMPLATES:
        count = random.randint(4, 12)
        for i in range(count):
            tag = f"{asset_type[:2].upper()}-{random.randint(1000,9999)}"
            purchase = rand_date(datetime(2020, 1, 1), datetime(2024, 6, 1)).date()
            warranty = (purchase + timedelta(days=random.choice([365, 730, 1095]))).replace()
            status = random.choices(
                ['Active', 'Inactive', 'In Repair', 'Retired'],
                weights=[70, 10, 10, 10]
            )[0]
            asset = Asset(
                asset_tag=f"{tag}-{asset_count:04d}",
                name=f"{manufacturer} {random.choice(models)}",
                asset_type=asset_type,
                manufacturer=manufacturer,
                model=random.choice(models),
                serial_number=f"SN{random.randint(10000000, 99999999)}",
                status=status,
                location=random.choice(LOCATIONS),
                assigned_to_id=random.choice(all_users).id if random.random() > 0.3 else None,
                purchase_date=purchase,
                warranty_expiry=warranty,
            )
            db.session.add(asset)
            asset_count += 1
    db.session.flush()
    print(f"  Created {asset_count} assets")

    # ── Tickets ──────────────────────────────────────────────────────────────
    print("Creating tickets...")
    ticket_count = 0
    comment_count = 0

    # Roughly 300 tickets spread over the year, weighted toward busier months
    month_weights = [8, 7, 9, 10, 11, 10, 7, 7, 10, 11, 10, 8]  # Jan–Dec

    total_tickets = 320
    tickets_per_month = []
    for w in month_weights:
        tickets_per_month.append(round(total_tickets * w / sum(month_weights)))

    for month_idx, n_tickets in enumerate(tickets_per_month):
        month = month_idx + 1
        m_start = datetime(2025, month, 1, 7, 0)
        # Last day of month
        if month == 12:
            m_end = datetime(2025, 12, 31, 18, 0)
        else:
            m_end = datetime(2025, month + 1, 1, 7, 0) - timedelta(seconds=1)

        for _ in range(n_tickets):
            template = random.choice(TICKET_TEMPLATES)
            title, desc, category, pw = template

            # Fill template placeholders
            names = [s[1].split()[0] for s in STAFF]
            title = title.replace('{name}', random.choice(names))
            title = title.replace('{manager}', random.choice(names))
            desc  = desc.replace('{name}', random.choice(names))
            desc  = desc.replace('{manager}', random.choice(names))

            priority = random.choices(['Low','Medium','High','Critical'], weights=pw)[0]
            submitter = random.choice(regular_users)
            created_at = business_date(m_start, m_end)

            # Resolve most tickets
            resolve_chance = {'Low': 0.90, 'Medium': 0.85, 'High': 0.80, 'Critical': 0.75}
            resolved = random.random() < resolve_chance[priority]

            if resolved:
                sla_hours = {'Critical': 4, 'High': 24, 'Medium': 48, 'Low': 72}[priority]
                # Mix of within-SLA and breached
                if random.random() < 0.80:
                    resolve_hours = random.uniform(0.5, sla_hours * 0.9)
                else:
                    resolve_hours = random.uniform(sla_hours * 1.1, sla_hours * 3)
                resolved_at = created_at + timedelta(hours=resolve_hours)
                if resolved_at > END:
                    resolved_at = END
                status = random.choice(['Resolved', 'Closed'])
                updated_at = resolved_at
            else:
                # Still open / in progress
                open_statuses = ['Open', 'In Progress']
                status = random.choices(open_statuses, weights=[60, 40])[0]
                resolved_at = None
                updated_at = created_at + timedelta(hours=random.uniform(1, 200))
                if updated_at > END:
                    updated_at = END

            assignee = random.choice(admin_users) if random.random() > 0.25 else None

            ticket = Ticket(
                title=title,
                description=desc,
                category=category,
                priority=priority,
                status=status,
                submitter_id=submitter.id,
                assignee_id=assignee.id if assignee else None,
                created_at=created_at,
                updated_at=updated_at,
                resolved_at=resolved_at,
            )
            db.session.add(ticket)
            db.session.flush()

            # Add 1-4 comments per ticket
            n_comments = random.choices([0, 1, 2, 3, 4], weights=[10, 30, 35, 15, 10])[0]
            comment_time = created_at + timedelta(minutes=random.randint(10, 60))
            for _ in range(n_comments):
                if comment_time >= (resolved_at or END):
                    break
                author = random.choice([submitter] + admin_users)
                c = Comment(
                    body=random.choice(COMMENTS_POOL),
                    ticket_id=ticket.id,
                    author_id=author.id,
                    created_at=comment_time,
                )
                db.session.add(c)
                comment_time += timedelta(hours=random.uniform(0.5, 12))
                comment_count += 1

            ticket_count += 1

    db.session.commit()
    print(f"  Created {ticket_count} tickets with {comment_count} comments")
    print("\nDone! Summary:")
    print(f"  Users:    {User.query.count()}")
    print(f"  Tickets:  {Ticket.query.count()}")
    print(f"  Comments: {Comment.query.count()}")
    print(f"  Assets:   {Asset.query.count()}")
    print("\nExtra login credentials:")
    print("  sysadmin  / helpdesk123  (admin)")
    print("  helpdesk1 / helpdesk123  (admin)")
    print("  jsmith    / password123  (user)")


if __name__ == '__main__':
    with app.app_context():
        seed()
