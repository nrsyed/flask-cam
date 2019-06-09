import argparse
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import smtplib

def import_secrets(filename):
    with open(filename, "r") as file_:
        secrets = json.load(file_)
    return secrets

def send_mail(
    sender, sender_name, recipient, smtp_username, smtp_password, host, port,
    subject, body
):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = email.utils.formataddr(
        (sender_name, sender)
    )
    msg["To"] = recipient
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(host, port)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(smtp_username, smtp_password)
        server.sendmail(sender, recipient, msg.as_string())
        server.close()
    except Exception as e:
        print(e)
    else:
        print("Email sent successfully")

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-b", "--body", type=str, default="")
    argparser.add_argument("-s", "--subject", type=str, default="")

    args = argparser.parse_args()
    secrets = import_secrets("secrets")

    send_mail(body=args.body, subject=args.subject, **secrets)
