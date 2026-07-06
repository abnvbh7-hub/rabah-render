import smtplib
import os
import dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

dotenv.load_dotenv()

def send_email(to_email: str, subject: str, body: str):
    sender_email = "dev.rabahpapyrus@gmail.com"
    app_password = os.getenv("GMAIL_KEY")

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "html"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

# send_email("proxysyrup@gmail.com","test","test")