import argparse
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import smtplib
import syslog

def import_secrets(filename):
    """
    Import a secrets file containing JSON in the following form:

    {
      "sender": "your_email_address@gmail.com",
      "sender_name": "Raspberry Pi",
      "recipient": "your_email_address@gmail.com",
      "smtp_username": "ABCDEFGHIJKLMNOPQRST",
      "smtp_password": "ABCD1eXw0/V/abcDEFg709fhJFKLAleabc",
      "host": "email-smtp.us-west-2.amazonaws.com",
      "port": 587
    }
    """

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
        syslog.syslog(str(e))
    else:
        msg = "Email sent to {}".format(recipient)
        print(msg)
        syslog.syslog(msg)

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-b", "--body", type=str, default="")
    argparser.add_argument(
        "-f", "--filepath", default="secrets", help="Path to secrets file"
    )
    argparser.add_argument("-s", "--subject", type=str, default="")
    args = argparser.parse_args()

    secrets = import_secrets(args.filepath)
    send_mail(body=args.body, subject=args.subject, **secrets)
