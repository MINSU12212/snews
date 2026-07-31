import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv()


def send_news_email(html_content, subject='🎵 토큰 - 음향기기 뉴스'):
    sender_email = os.getenv('GMAIL_USER')
    sender_password = os.getenv('GMAIL_PASSWORD')
    recipients = [
        os.getenv('EMAIL_RECIPIENT_1'),
        os.getenv('EMAIL_RECIPIENT_2'),
    ]
    recipients = [r for r in recipients if r]

    if not sender_email or not sender_password:
        print("❌ GMAIL_USER / GMAIL_PASSWORD가 .env에 설정되어 있지 않습니다.")
        return False

    if not recipients:
        print("❌ 수신자가 설정되어 있지 않습니다.")
        return False

    message = MIMEMultipart('alternative')
    message['Subject'] = subject
    message['From'] = sender_email
    message['To'] = ', '.join(recipients)
    message.attach(MIMEText(html_content, 'html', 'utf-8'))

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipients, message.as_string())
        server.quit()
        print(f"✅ 이메일 발송 완료: {', '.join(recipients)}")
        return True
    except Exception as e:
        print(f"❌ 이메일 발송 실패: {e}")
        return False
