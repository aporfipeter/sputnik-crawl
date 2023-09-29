import os
from email.message import EmailMessage
import ssl
import smtplib


class EmailService:
    def __init__(self):
        self.sender = "aporfi.py@gmail.com"
        self.server = "smtp.gmail.com"
        self.port = 465
        self.password = os.environ.get("GMAIL_APP_PASSWORD")
        self.recipients = self.read_recipients()

    def read_recipients(self):
        with open("recipients.txt") as recipients:
            lines = [line.rstrip('\n') for line in recipients]
            return lines

    def send_email(self, subject, body):
        em = EmailMessage()
        em['From'] = self.sender
        em['To'] = self.read_recipients()
        em['subject'] = subject
        em.set_content(body)

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(self.server, self.port, context=context) as smtp:
            smtp.login(self.sender, self.password)
            smtp.sendmail(self.sender, self.recipients, em.as_string())

