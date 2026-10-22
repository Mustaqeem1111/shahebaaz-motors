import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

from config import (
    BREVO_SMTP_SERVER,
    BREVO_SMTP_PORT,
    BREVO_SMTP_LOGIN,
    BREVO_SMTP_PASSWORD,
    ADMIN_EMAIL,
    APP_NAME
)


# =========================================================
# SHAHEBAZ MOTORS - EMAIL SERVICE
# email_service.py
# Uses Brevo SMTP to send emails
# =========================================================

logger = logging.getLogger(__name__)


def send_email(to_email, subject, html_content):
    """
    Send email using Brevo SMTP.

    Args:
        to_email (str): Recipient email
        subject (str): Email subject
        html_content (str): HTML body

    Returns:
        (bool, str): (success, message)
    """

    if not BREVO_SMTP_LOGIN or not BREVO_SMTP_PASSWORD:
        logger.error("Email credentials not configured")
        return False, "Email service not configured"

    if not ADMIN_EMAIL:
        logger.error("Admin email not configured")
        return False, "Admin email not configured"

    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{APP_NAME} <{ADMIN_EMAIL}>"
        message["To"] = to_email

        # Attach HTML
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)

        # Create secure connection
        context = ssl.create_default_context()

        # Connect to Brevo SMTP
        with smtplib.SMTP(BREVO_SMTP_SERVER, BREVO_SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(BREVO_SMTP_LOGIN, BREVO_SMTP_PASSWORD)
            server.sendmail(ADMIN_EMAIL, to_email, message.as_string())

        logger.info(f"Email sent to {to_email}")
        return True, "Email sent successfully"

    except smtplib.SMTPAuthenticationError as error:
        logger.error(f"SMTP Authentication failed: {error}")
        return False, "Email authentication failed"

    except smtplib.SMTPException as error:
        logger.error(f"SMTP error: {error}")
        return False, f"SMTP error: {str(error)}"

    except Exception as error:
        logger.error(f"Email sending failed: {error}")
        return False, str(error)


def send_password_reset_email(to_email, reset_link):
    """
    Send password reset email.

    Args:
        to_email (str): Recipient email
        reset_link (str): Reset URL

    Returns:
        (bool, str): (success, message)
    """

    subject = f"Password Reset - {APP_NAME}"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, Helvetica, sans-serif;
                background: #f4f5f7;
                padding: 30px;
                margin: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background: white;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 5px 20px rgba(0,0,0,0.08);
            }}
            .header {{
                background: #111315;
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
                letter-spacing: 1px;
            }}
            .header p {{
                margin: 8px 0 0;
                color: #d9a441;
                font-size: 12px;
                letter-spacing: 2px;
            }}
            .content {{
                padding: 40px 30px;
                color: #17191c;
            }}
            .content h2 {{
                margin-top: 0;
                font-size: 22px;
            }}
            .content p {{
                color: #666d75;
                line-height: 1.7;
                font-size: 14px;
            }}
            .button-wrap {{
                text-align: center;
                margin: 30px 0;
            }}
            .button {{
                display: inline-block;
                background: #d9a441;
                color: #111315 !important;
                padding: 15px 40px;
                text-decoration: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }}
            .link-box {{
                background: #f8f9fa;
                border: 1px solid #e5e7ea;
                border-radius: 8px;
                padding: 15px;
                margin: 20px 0;
                word-break: break-all;
                font-size: 12px;
                color: #666d75;
            }}
            .warning {{
                background: #fff8e7;
                border-left: 4px solid #f3c969;
                padding: 15px;
                margin: 20px 0;
                font-size: 13px;
                color: #666d75;
            }}
            .footer {{
                background: #f8f9fa;
                padding: 20px 30px;
                text-align: center;
                font-size: 12px;
                color: #949aa1;
                border-top: 1px solid #e5e7ea;
            }}
        </style>
    </head>
    <body>
        <div class="container">

            <div class="header">
                <h1>SHAHEBAZ MOTORS</h1>
                <p>ADMIN PANEL</p>
            </div>

            <div class="content">
                <h2>Password Reset Request</h2>

                <p>Hello Admin,</p>

                <p>
                    We received a request to reset your admin password.
                    Click the button below to create a new password.
                </p>

                <div class="button-wrap">
                    <a href="{reset_link}" class="button">
                        Reset Password
                    </a>
                </div>

                <p>Or copy this link in your browser:</p>

                <div class="link-box">
                    {reset_link}
                </div>

                <div class="warning">
                    <strong>⚠️ Important:</strong>
                    This link will expire in 15 minutes.
                    If you didn't request this, please ignore this email.
                </div>
            </div>

            <div class="footer">
                © 2026 Shahebaz Motors<br>
                This is an automated email. Please do not reply.
            </div>

        </div>
    </body>
    </html>
    """

    return send_email(to_email, subject, html_content)