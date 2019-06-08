import email.utils
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def import_secrets(filename):
    with open(filename, "r") as file_:
        secrets = json.load(file_)
    return secrets

def send_mail(secrets, subject, body):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = email.utils.formataddr(
        (secrets["sender_name"], secrets["sender"])
    )
    msg["To"] = secrets["recipient"]
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(secrets["host"], secrets["port"])
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(secrets["smtp_username"], secrets["smtp_password"])
        server.sendmail(secrets["sender"], secrets["recipient"], msg.as_string())
        server.close()
    except Exception as e:
        print(e)
    else:
        print("success")
