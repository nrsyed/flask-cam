from argparse import ArgumentParser
from json import load as js_load
from typing import AnyStr, Any, NoReturn
from smtplib import SMTP
from syslog import syslog

from email.utils import formataddr
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def import_secrets(filename: AnyStr) -> Any:
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
        secrets = js_load(file_)
    return secrets


def send_mail(
        sender: AnyStr,
        sender_name: AnyStr,
        recipient: AnyStr,
        smtp_username: AnyStr,
        smtp_password: AnyStr,
        host: AnyStr,
        port: int,
        subject: AnyStr,
        body: AnyStr,
        verbose=False
) -> NoReturn:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = formataddr( (sender_name, sender) )
    msg["To"] = recipient
    msg.attach(MIMEText(body, "plain"))

    try:
        server = SMTP(host, port)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(smtp_username, smtp_password)
        server.sendmail(sender, recipient, msg.as_string())
        server.close()
    except Exception as e:
        syslog(str(e))
        if verbose:
            print(e)
    else:
        msg = "Email sent to {}".format(recipient)
        syslog(msg)
        if verbose:
            print(msg)


if __name__ == "__main__":
    argument_parser = ArgumentParser()

    argument_parser.add_argument("-b", "--body", type=str, default="")
    argument_parser.add_argument("-f", "--filepath", default="secrets", help="Path to secrets file")
    argument_parser.add_argument("-s", "--subject", type=str, default="")
    argument_parser.add_argument("-v", "--verbose", action="store_true")

    args = argument_parser.parse_args()

    body = args.body
    subject = args.subject
    verbose = args.verbose

    secrets = import_secrets(args.filepath)
    send_mail(body=body, subject=subject, verbose=verbose, **secrets)
