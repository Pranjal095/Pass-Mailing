import os, csv, smtplib
from string import Template
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# load environment
load_dotenv()
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT   = int(os.getenv("SMTP_PORT", 587))
USER        = os.getenv("EMAIL_USER")
PASS        = os.getenv("EMAIL_PASS")
FORM_LINK   = os.getenv("FORM_LINK")

# sanity‐check that nothing’s missing
if not all([SMTP_SERVER, SMTP_PORT, USER, PASS, FORM_LINK]):
    raise RuntimeError("Missing one of SMTP_SERVER/EMAIL_USER/EMAIL_PASS/FORM_LINK in .env")

# load HTML template
with open("pass.html", "r") as f:
    tpl = Template(f.read())

# connect SMTP
server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
server.starttls()
server.login(USER, PASS)

# send to each recipient
with open("recipients.csv") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        name  = row["name"]
        email = row["email"]

        # fill in placeholders
        html = tpl.substitute(NAME=name, FORM_LINK=FORM_LINK)

        msg = MIMEMultipart("alternative")
        # updated subject & from
        msg["Subject"] = "Your SPICMACAY 2025 Invitation – Complete Registration"
        msg["From"]    = f"SPICMACAY 2025 <{USER}>"
        msg["To"]      = email

        # plain‐text fallback
        text = f"""Dear {name},

Please complete your registration for SPICMACAY 2025 by visiting:
{FORM_LINK}

See you on campus!
"""
        msg.attach(MIMEText(text, "plain", "utf-8"))
        msg.attach(MIMEText(html, "html", "utf-8"))

        try:
            server.sendmail(USER, email, msg.as_string())
            print(f"✓ Sent to {email}")
        except Exception as e:
            print(f"✗ Failed for {email}: {e}")

server.quit()