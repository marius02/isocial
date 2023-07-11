import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_welcome_email(email: str, token: str):
    sender_email = "latentvariable.z@gmail.com"
    receiver_email = email

    message = MIMEMultipart("alternative")
    message["Subject"] = "Welcome to iSocial!"
    message["From"] = sender_email
    message["To"] = receiver_email

    # address = "http://159.203.54.13:8787/auth/verify"

    html = f"""\
    <html>
    <body>
        <p>Hi,<br>
            Welcome to iSocial
            Click <a href="http://143.198.40.50/auth/verify2/{token}">Here</a> to verify
    </p>
    </body>
    </html>
    """

    part2 = MIMEText(html, 'html')

    message.attach(part2)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, "nuxpqnxljidxwfyr")
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )


def send_forgot_email(email: str, token: str):
    sender_email = "latentvariable.z@gmail.com"
    receiver_email = email

    message = MIMEMultipart("alternative")
    message["Subject"] = "Welcome to iSocial!"
    message["From"] = sender_email
    message["To"] = receiver_email

    address = "http://159.203.54.13:8787/auth/verify"

    html = f"""\
    <html>
    <body>
        <p>Hi,<br>
            iSocial forgot password 
            Click <a href="http://143.198.40.50/auth/verify2/{token}">Here</a> to reset your password 
    </p>
    </body>
    </html>
    """

    part2 = MIMEText(html, 'html')

    message.attach(part2)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, "nuxpqnxljidxwfyr")
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )
