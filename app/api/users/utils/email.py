from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from fastapi.exceptions import HTTPException
from dotenv import load_dotenv
import os

load_dotenv()

OWN_EMAIL = os.getenv('OWN_EMAIL')
OWN_EMAIL_PASSWORD = os.getenv('OWN_EMAIL_PASSWORD')


def send_welcome_email(email, token):
    try:
        html = f"""<html>
                    <body>
                        <p>Hi,<br>
                            Welcome to iSocial! Click the following link to verify your email address:
                            <a href="http://23.100.16.133:8000/auth/email-verification/?token={token}">Verify Email</a> 
                        </p>
                    </body>
                    </html>
                    """
        msg = MIMEText(html, "html")
        msg['Subject'] = "Welcome to iSocial!"
        msg['From'] = OWN_EMAIL
        msg['To'] = email

        port = 465

        # Connect to the email server
        server = SMTP_SSL("mail.privateemail.com", port)
        server.login(OWN_EMAIL, OWN_EMAIL_PASSWORD)

        # Send the email
        server.send_message(msg)
        server.quit()
        return {"message": "Email sent successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=e)


# def send_forgot_email(email: str, token: str):
#     sender_email = "latentvariable.z@gmail.com"
#     receiver_email = email

#     message = MIMEMultipart("alternative")
#     message["Subject"] = "Welcome to iSocial!"
#     message["From"] = sender_email
#     message["To"] = receiver_email

#     address = "http://159.203.54.13:8787/auth/verify"

#     html = f"""\
#     <html>
#     <body>
#         <p>Hi,<br>
#             iSocial forgot password
#             Click <a href="http://143.198.40.50/auth/verify2/{token}">Here</a> to reset your password
#     </p>
#     </body>
#     </html>
#     """

#     part2 = MIMEText(html, 'html')

#     message.attach(part2)

#     context = ssl.create_default_context()
#     with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
#         server.login(sender_email, "nuxpqnxljidxwfyr")
#         server.sendmail(
#             sender_email, receiver_email, message.as_string()
#         )
